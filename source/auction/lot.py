from fastapi import APIRouter, Depends as D
from fastapi.responses import JSONResponse

from scripts import parser
from scripts.token_validator import token_validate_factory as TVF
from scripts.idgen import IDGenerator
from data import config as cfg
import database as db


router = APIRouter()
idgen = IDGenerator()


@router.get("/add")
async def create_new_lot(
        name:      str = None,
        price:     int = None,
        auctionID: int = None,
        lotID:     int = None,
        _ = D(TVF(*cfg.TOKENIZER.ADMIN_LIST))
):
    if name is None or price is None or auctionID is None:
        return parser.form_error_bad_parsing()
    if price < 0:
        return parser.form_error(db.exceptions.ValueLoE0(), "subzero input", 409)

    try:
        async with db.session_link() as session:
            async with session.begin():
                if lotID is None:
                    lotID = await idgen.lotID(session)
                else:
                    item = await session.get(db.Lot, lotID, with_for_update=True)
                    if item is not None:
                        session.delete(item)

                session.add(
                    db.Lot(
                        lotID=lotID,
                        name=name,
                        price=price,
                        auctionID=auctionID
                    )
                )
        return JSONResponse(
            {"indexed": lotID},
            status_code=200
        )
    except Exception as e:
        return parser.form_error(e)


@router.get("/confirm")
async def confirm_lot(
        lotID: int = None,
        _ = D(TVF(*cfg.TOKENIZER.ADMIN_LIST))
):
    if lotID is None:
        return parser.form_error_bad_parsing()

    try:
        async with db.session_link() as session:
            async with session.begin():
                lot = await session.get(db.Lot, lotID)
                if lot is None:
                    raise db.exceptions.NotFound

                store = (await session.execute(
                    db.select(db.Store).where(db.Store.auctionID == lot.auctionID).with_for_update()
                )).scalar_one_or_none()
                if store.balance < lot.price:
                    raise db.exceptions.NotEnoughBalance

                auction_transfer_route = await session.get(db.Store, "auction_transfer_route", with_for_update=True)

                store.balance -= lot.price
                auction_transfer_route.balance += lot.price
                lot.confirmed = True

        return JSONResponse(
            {"ok": True},
            status_code=200
        )
    except db.exceptions.NotFound as e:
        return parser.form_error(e, "ID not found", 404)
    except db.exceptions.NotEnoughBalance as e:
        return parser.form_error(e, "not enough balance", 409)
    except Exception as e:
        return parser.form_error(e)


@router.get("/list")
async def lot_list(
        storeID: str = None,
        _ = D(TVF(*cfg.TOKENIZER.ADMIN_LIST))
):
    if storeID is None:
        return parser.form_error_bad_parsing()

    try:
        async with db.session_link() as session:
            store = await session.get(db.Store, storeID)
            if store is None:
                raise db.exceptions.NotFound

            lots = (await session.execute(
                db.select(db.Lot).where(
                    db.Lot.auctionID == store.auctionID,
                    db.Lot.confirmed.is_(True)
                )
            )).all()

        return JSONResponse(
            {"result": lots},
            status_code=200
        )
    except db.exceptions.NotFound as e:
        return parser.form_error(e, "ID not found", 404)
    except Exception as e:
        return parser.form_error(e)
