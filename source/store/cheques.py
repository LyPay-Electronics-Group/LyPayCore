from fastapi import APIRouter
from fastapi.responses import JSONResponse

from asyncio import sleep

from scripts import lpsql, parser, idgen
from data import config as cfg


router = APIRouter()
db = lpsql.DataBase(cfg.PATHS.DATA + "lypay_database.db", lpsql.Tables.MAIN)


@router.get("/get")
async def get_cheque(chequeID: str = None):
    if chequeID is None:
        return parser.form_error_bad_parsing()

    try:
        search_result = db.search("cheques", "chequeID", chequeID)
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
async def get_all_cheques(storeID: str = None, active_filter: bool = None):
    if storeID is None:
        return parser.form_error_bad_parsing()

    active_filter = bool(active_filter)
    try:
        search_result = list()
        for item in db.search("cheques", "storeID", storeID, True):
            if active_filter and item['active']:
                search_result.append(item)

        if len(search_result) == 0:
            raise lpsql.exceptions.IDNotFound

        return JSONResponse(
            {"result": search_result},
            status_code=200
        )
    except lpsql.exceptions.IDNotFound as e:
        return parser.form_error(e, "ID not found", 404)
    except Exception as e:
        return parser.form_error(e)
