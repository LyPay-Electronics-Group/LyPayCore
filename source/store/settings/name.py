from fastapi import APIRouter, Depends as D
from fastapi.responses import JSONResponse

from scripts import lpsql, parser, censor
from scripts.token_validator import token_validate_factory as TVF
from data import config as cfg


router = APIRouter()
db = lpsql.DataBase(cfg.PATHS.DATA + "lypay_database.db", lpsql.Tables.MAIN)


@router.get("/get")
async def get_name(
        ID: str = None,
        _ = D(TVF(*cfg.TOKENIZER.ADMIN_LIST))
):
    if ID is None:
        return parser.form_error_bad_parsing()

    try:
        store = db.search("stores", "ID", ID)
        if store is None:
            raise lpsql.exceptions.IDNotFound()

        return JSONResponse(
            {"result": store["name"]},
            status_code=200
        )
    except lpsql.exceptions.IDNotFound as e:
        return parser.form_error(e, "ID not found", 404)
    except Exception as e:
        return parser.form_error(e)


@router.get("/upd")
async def update_name(
        ID:  str = None,
        new: str = None,
        _ = D(TVF(*cfg.TOKENIZER.ADMIN_LIST))
):
    if ID is None or new is None:
        return parser.form_error_bad_parsing()

    try:
        store = db.search("stores", "ID", ID)
        if store is None:
            raise lpsql.exceptions.IDNotFound()

        if not censor.check_store_name(new):
            return parser.form_error(AttributeError(), "bad censor flag: store name", 406)

        db.update("stores", "ID", ID, "name", new)
        return JSONResponse(
            {"ok": True},
            status_code=200
        )
    except lpsql.exceptions.IDNotFound as e:
        return parser.form_error(e, "ID not found", 404)
    except Exception as e:
        return parser.form_error(e)
