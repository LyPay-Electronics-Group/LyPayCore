from fastapi import APIRouter
from fastapi.responses import JSONResponse

from asyncio import sleep

from scripts import lpsql, parser, idgen
from data import config as cfg


router = APIRouter()
db = lpsql.DataBase(cfg.PATHS.DATA + "lypay_database.db", lpsql.Tables.MAIN)


@router.get("/get")
async def get_basic_info(storeID: str = None):
    if storeID is None:
        return parser.form_error_bad_parsing()

    try:
        search_result = db.search("stores", "ID", storeID)
        if search_result is None:
            raise lpsql.exceptions.IDNotFound

        return JSONResponse(
            search_result,
            status_code=200
        )
    except lpsql.exceptions.IDNotFound as e:
        return parser.form_error(e, "ID not found", 404)
    except Exception as e:
        return parser.form_error(e)


@router.get("/all")
async def get_all_stores_ids():
    try:
        return JSONResponse(
            {"result": db.searchall("stores", "ID")},
            status_code=200
        )
    except Exception as e:
        return parser.form_error(e)
