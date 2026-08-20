from fastapi import APIRouter, Depends as D
from fastapi.responses import JSONResponse

from jwt import decode as jwt_decode

from database import Cheque
from scripts import parser, j2
from scripts.token_validator import token_validate_factory as TVF
from scripts.idgen import IDGenerator
from scripts.unix import unix
from data import config as cfg
import database as db


router = APIRouter()
idgen = IDGenerator()


@router.get("/get")
async def get_cheque(
        chequeID: str = None,
        _ = D(TVF(*cfg.TOKENIZER.PUBLIC_LIST))
):
    if chequeID is None:
        return parser.form_error_bad_parsing()

    try:
        async with db.session_link() as session:
            search_result = await session.get(db.Cheque, chequeID)
            if search_result is None:
                raise db.exceptions.NotFound

        return JSONResponse(
            search_result,
            status_code=200
        )
    except db.exceptions.NotFound as e:
        return parser.form_error(e, "ID not found", 404)
    except Exception as e:
        return parser.form_error(e)


@router.get("/all")
async def get_all_cheques(
        storeID:       str = None,
        active_filter: int = None,  # active_filter : bool
        _ = D(TVF(*cfg.TOKENIZER.ADMIN_LIST))
):
    if storeID is None:
        return parser.form_error_bad_parsing()

    inactive_filter = not bool(active_filter)
    try:
        async with db.session_link() as session:
            if await session.get(db.Store, storeID) is None:
                raise db.exceptions.NotFound

            search_result = (await session.scalars(
                db.select(db.Cheque.chequeID).where(
                    db.Cheque.storeID == storeID,
                    db.or_(inactive_filter, db.Cheque.active.is_(True))
                )
            )).all()

        return JSONResponse(
            {"result": search_result},
            status_code=200
        )
    except db.exceptions.NotFound as e:
        return parser.form_error(e, "ID not found", 404)
    except Exception as e:
        return parser.form_error(e)


@router.get("/add")
async def create_cheque(
        storeID:  str = None,
        customer: int = None,
        items:    str = None,
        _ = D(TVF(*cfg.TOKENIZER.ADMIN_LIST))
):
    if storeID is None or customer is None or items is None:
        return parser.form_error_bad_parsing()

    try:
        async with db.session_link() as session:
            if await session.geet(db.Store, storeID) is None:
                raise db.exceptions.NotFound

            parsed_items = jwt_decode(items, cfg.JWT_KEY, ["HS256"])
            unix_timestamp = unix()

            cheque_sum = 0
            for item, multiplier in parsed_items.items():
                cheque_sum += (await session.scalar(
                    db.select(db.Item.price).where(db.Item.itemID == item).with_for_update(read=True)
                )) * multiplier
            if cheque_sum <= 0:
                raise db.exceptions.ValueLoE0

            async with session.begin():
                user = await session.get(db.User, customer, with_for_update=True)
                store = await session.get(db.Store, storeID, with_for_update=True)

                user.balance -= cheque_sum
                store.balance += cheque_sum
                session.add(db.HistoryEntry(
                    ID_in=f"s{storeID}",
                    ID_out=f"u{customer}",
                    value=cheque_sum,
                    unix=unix_timestamp
                ))
                user.last_seen = unix_timestamp

                chequeID = await idgen.chequeID(storeID, session)
                session.add(db.Cheque(
                    chequeID=chequeID,
                    storeID=storeID,
                    unix=unix_timestamp,
                    customer=customer,
                    items=parsed_items,
                    active=True
                ))
        return JSONResponse(
            {'generated': chequeID},
            status_code=201
        )
    except db.exceptions.NotFound as e:
        return parser.form_error(e, "ID not found", 404)
    except db.exceptions.ValueLoE0 as e:
        return parser.form_error(e, "subzero input", 409)
    except db.exceptions.NotEnoughBalance as e:
        return parser.form_error(e, "not enough balance", 409)
    except Exception as e:
        return parser.form_error(e)


@router.get("/de")
async def cancel_cheque(
        chequeID: str = None,
        _ = D(TVF(*cfg.TOKENIZER.ADMIN_LIST))
):
    if chequeID is None:
        return parser.form_error_bad_parsing()

    try:
        async with db.session_link() as session:
            async with session.begin():
                cheque = await session.get(db.Cheque, chequeID, with_for_update=True)
                if cheque is None:
                    raise db.exceptions.NotFound

                amount = 0
                for itemID, multiplier in cheque.items.items():
                    item = await session.get(db.Item, itemID)
                    if item is None:
                        continue  # raise db.exceptions.NotFound ?
                    amount += item.price * multiplier

                store = await session.get(db.Store, cheque.storeID, with_for_update=True)
                user = await session.get(db.User, cheque.customer, with_for_update=True)

                store.balance -= amount
                user.balance += amount
                session.add(db.HistoryEntry(
                    ID_out=f"s{cheque.storeID}",
                    ID_in=f"u{cheque.customer}",
                    value=amount,
                    unix=unix()
                ))
                cheque.active = False

        return JSONResponse(
            {'ok': True},
            status_code=200
        )
    except db.exceptions.NotFound as e:
        return parser.form_error(e, "ID not found", 404)
    except Exception as e:
        return parser.form_error(e)
