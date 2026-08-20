from fastapi import APIRouter, Depends as D
from fastapi.responses import JSONResponse

from scripts import parser, censor
from scripts.token_validator import token_validate_factory as TVF
from scripts.idgen import IDGenerator
from data import config as cfg
import database as db


router = APIRouter()
idgen = IDGenerator()


@router.get("/get")
async def get_item(
        itemID: str = None,
        _ = D(TVF(*cfg.TOKENIZER.ADMIN_LIST))
):
    if itemID is None:
        return parser.form_error_bad_parsing()

    try:
        async with db.session_link() as session:
            search_result = await session.get(db.Item, itemID)
            if search_result is None:
                raise db.exceptions.NotFound

        return JSONResponse(
            search_result.as_dict(),
            status_code=200
        )
    except db.exceptions.NotFound as e:
        return parser.form_error(e, "ID not found", 404)
    except Exception as e:
        return parser.form_error(e)


@router.get("/all")
async def get_all_items(
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
                db.select(db.Item.itemID).where(
                    db.Item.storeID == storeID,
                    db.or_(inactive_filter, db.Item.active.is_(True))
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
async def create_item(
        storeID: str = None,
        name:    str = None,
        price:   int = None,
        _ = D(TVF(*cfg.TOKENIZER.ADMIN_LIST))
):
    if storeID is None or name is None or price is None:
        return parser.form_error_bad_parsing()

    if not censor.check_store_item_name(name):
        return parser.form_error(AttributeError(), "bad censor flag: store item name", 406)
    if price < 0:
        return parser.form_error(AttributeError(), "bad censor flag: store item price", 406)

    try:
        async with db.session_link() as session:
            async with session.begin():
                if await session.get(db.Store, storeID) is None:
                    raise db.exceptions.NotFound

                itemID = await idgen.itemID(storeID, session)
                session.add(db.Item(
                    itemID=itemID,
                    storeID=storeID,
                    name=name,
                    price=price,
                    active=True
                ))

        return JSONResponse(
            {'generated': itemID},
            status_code=201
        )
    except db.exceptions.NotFound as e:
        return parser.form_error(e, "ID not found", 404)
    except Exception as e:
        return parser.form_error(e)


@router.get("/rem")
async def remove_item(
        itemID: str = None,
        _ = D(TVF(*cfg.TOKENIZER.ADMIN_LIST))
):
    if itemID is None:
        return parser.form_error_bad_parsing()

    try:
        async with db.session_link() as session:
            async with session.begin():
                item = await session.get(db.Item, itemID, with_for_update=True)
                if item is None:
                    raise db.exceptions.NotFound
                item.active = False

        return JSONResponse(
            {'ok': True},
            status_code=200
        )
    except db.exceptions.NotFound as e:
        return parser.form_error(e, "ID not found", 404)
    except Exception as e:
        return parser.form_error(e)


@router.get("/edit")
async def edit_item(
        itemID: str = None,
        name: str = None,
        price: int = None,
        _ = D(TVF(*cfg.TOKENIZER.ADMIN_LIST))
):
    if itemID is None or (name is None and price is None):
        return parser.form_error_bad_parsing()

    if name is not None and not censor.check_store_item_name(name):
        return parser.form_error(AttributeError(), "bad censor flag: store item name", 406)
    if price is not None and price <= 0:
        return parser.form_error(AttributeError(), "bad censor flag: store item price", 406)

    try:
        async with db.session_link() as session:
            async with session.begin():
                item = await session.get(db.Item, itemID, with_for_update=True)
                if item is None:
                    raise db.exceptions.NotFound
                if name is None:
                    name = item.name
                if price is None:
                    price = item.price
                item.active = False

                itemID = await idgen.itemID(item.storeID, session)
                session.add(db.Item(
                    itemID=itemID,
                    storeID=item.storeID,
                    name=name,
                    price=price,
                    active=True
                ))

        return JSONResponse(
            {'updated': itemID},
            status_code=200
        )
    except db.exceptions.NotFound as e:
        return parser.form_error(e, "ID not found", 404)
    except Exception as e:
        return parser.form_error(e)
