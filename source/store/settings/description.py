from fastapi import APIRouter, Depends as D
from fastapi.responses import JSONResponse

from scripts import parser, censor
from scripts.token_validator import token_validate_factory as TVF
from data import config as cfg
import database as db


router = APIRouter()


@router.get("/get")
async def get_description(
        ID: str = None,
        _ = D(TVF(*cfg.TOKENIZER.ADMIN_LIST))
):
    if ID is None:
        return parser.form_error_bad_parsing()

    try:
        async with db.session_link() as session:
            store = await session.get(db.Store, ID)
            if store is None:
                raise db.exceptions.NotFound

        return JSONResponse(
            {"result": store.description},
            status_code=200
        )
    except db.exceptions.NotFound as e:
        return parser.form_error(e, "ID not found", 404)
    except Exception as e:
        return parser.form_error(e)


@router.get("/upd")
async def update_description(
        ID:  str = None,
        new: str = None,
        _ = D(TVF(*cfg.TOKENIZER.ADMIN_LIST))
):
    if ID is None:
        return parser.form_error_bad_parsing()
    if new is None:
        new = ""
    if not censor.check_store_description(new):
        return parser.form_error(AttributeError(), "bad censor flag: desc", 406)

    try:
        async with db.session_link() as session:
            async with session.begin():
                store = await session.get(db.Store, ID, with_for_update=True)
                if store is None:
                    raise db.exceptions.NotFound
                store.description = new

        return JSONResponse(
            {"ok": True},
            status_code=200
        )
    except db.exceptions.NotFound as e:
        return parser.form_error(e, "ID not found", 404)
    except Exception as e:
        return parser.form_error(e)
