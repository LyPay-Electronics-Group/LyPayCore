from fastapi import APIRouter, Depends as D
from fastapi.responses import JSONResponse

from scripts import parser
from scripts.token_validator import token_validate_factory as TVF
from scripts.unix import unix
from data import config as cfg
import database as db


router = APIRouter()


@router.get("/list")
async def access_list(
        storeID: str = None,
        _ = D(TVF(*cfg.TOKENIZER.ADMIN_LIST))
):
    if storeID is None:
        return parser.form_error_bad_parsing()

    try:
        async with db.session_link() as session:
            search_result = (await session.scalars(
                db.select(db.Shopkeeper.userID).where(db.Shopkeeper.storeID == storeID)
            )).all()

            if len(search_result) == 0:
                raise db.exceptions.NotFound

        return JSONResponse(
            {"result": search_result},
            status_code=200
        )
    except db.exceptions.NotFound as e:
        return parser.form_error(e, "ID not found", 404)
    except Exception as e:
        return parser.form_error(e)


@router.get("/add")
async def access_add(
        storeID: str = None,
        userID:  int = None,
        _ = D(TVF(*cfg.TOKENIZER.ADMIN_LIST))
):
    if storeID is None or userID is None:
        return parser.form_error_bad_parsing()

    try:
        async with db.session_link() as session:
            if await session.get(db.Store, storeID) is None or await session.get(db.User, userID) is None:
                raise db.exceptions.NotFound
            if (await session.scalars(
                db.select(db.Shopkeeper).where(db.Shopkeeper.userID == userID)
            )).one_or_none() is not None:
                raise PermissionError

            async with session.begin():
                session.add(db.Shopkeeper(
                    userID=userID,
                    storeID=storeID
                ))
                session.add(db.FirewallStoresEntry(
                    ID=userID,
                    unix=unix(),
                    access=True,
                    comment="added via access router"
                ))
        return JSONResponse(
            {"ok": True},
            status_code=201
        )
    except PermissionError as e:
        return parser.form_error(e, "user is already a shopkeeper", 403)
    except db.exceptions.NotFound as e:
        return parser.form_error(e, "ID not found", 404)
    except Exception as e:
        return parser.form_error(e)


@router.get("/rem")
async def remove_access(
        storeID: str = None,
        userID:  int = None,
        _ = D(TVF(*cfg.TOKENIZER.ADMIN_LIST))
):
    if storeID is None or userID is None:
        return parser.form_error_bad_parsing()

    try:
        async with db.session_link() as session:
            if await session.get(db.Store, storeID) is None or await session.get(db.User, userID) is None:
                raise db.exceptions.NotFound

            async with session.begin():
                shopkeeper = (await session.scalars(
                    db.select(db.Shopkeeper).where(db.Shopkeeper.userID == userID).with_for_update()
                )).one_or_none()
                firewall_entry = await session.get(db.FirewallStoresEntry, userID, with_for_update=True)
                session.delete(shopkeeper)
                session.delete(firewall_entry)
        return JSONResponse(
            {"ok": True},
            status_code=200
        )
    except db.exceptions.NotFound as e:
        return parser.form_error(e, "ID not found", 404)
    except Exception as e:
        return parser.form_error(e)
