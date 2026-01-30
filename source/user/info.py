from fastapi import APIRouter
from fastapi.responses import JSONResponse

from scripts import lpsql, parser
from data import config as cfg


router = APIRouter()
db = lpsql.DataBase(cfg.PATHS.DATA + "lypay_database.db", lpsql.Tables.MAIN)


@router.get("/get")
async def get(ID: int = None):
    if ID is None:
        return parser.form_error_bad_parsing()

    try:
        result = db.search("users", "ID", ID)
        if result is None:
            raise lpsql.exceptions.IDNotFound()
        return JSONResponse(
            result,
            status_code=200
        )
    except lpsql.exceptions.IDNotFound as e:
        return parser.form_error(e, "ID not found", 404)
    except Exception as e:
        return parser.form_error(e)


@router.get("/get_all")
async def all_ids():
    try:
        return JSONResponse(
            {"ids": db.searchall("users", "ID")},
            status_code=200
        )
    except Exception as e:
        return parser.form_error(e)
