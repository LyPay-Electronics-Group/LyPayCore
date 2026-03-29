from fastapi import APIRouter
from fastapi.responses import JSONResponse

from scripts import lpsql, parser, censor
from data import config as cfg


router = APIRouter()
db = lpsql.DataBase(cfg.PATHS.DATA + "lypay_database.db", lpsql.Tables.MAIN)


@router.get("/get")
async def get_description(ID: str = None):
    if ID is None:
        return parser.form_error_bad_parsing()

    try:
        store = db.search("stores", "ID", ID)
        if store is None:
            raise lpsql.exceptions.IDNotFound()

        return JSONResponse(
            {"result": store["description"]},
            status_code=200
        )
    except lpsql.exceptions.IDNotFound as e:
        return parser.form_error(e, "ID not found", 404)
    except Exception as e:
        return parser.form_error(e)


@router.get("/upd")
async def update_description(ID: str = None, new: str = None):
    if ID is None:
        return parser.form_error_bad_parsing()
    if new is None:
        new = ""

    try:
        store = db.search("stores", "ID", ID)
        if store is None:
            raise lpsql.exceptions.IDNotFound()

        if not censor.check_store_description(new):
            return parser.form_error(AttributeError(), "bad censor flag: desc", 406)

        db.update("stores", "ID", ID, "description", new)
        return JSONResponse(
            {"ok": True},
            status_code=200
        )
    except lpsql.exceptions.IDNotFound as e:
        return parser.form_error(e, "ID not found", 404)
    except Exception as e:
        return parser.form_error(e)
