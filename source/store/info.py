from fastapi import APIRouter
from fastapi.responses import JSONResponse

from scripts import lpsql, parser
from data import config as cfg


router = APIRouter()
db = lpsql.DataBase(cfg.PATHS.DATA + "lypay_database.db", lpsql.Tables.MAIN)


@router.get("/get")
async def get_basic_info(ID: str = None):
    if ID is None:
        return parser.form_error_bad_parsing()

    try:
        search_result = db.search("stores", "ID", ID)
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


@router.get("/all/stores")
async def get_all_stores_ids():
    try:
        return JSONResponse(
            {"ids": db.searchall("stores", "ID")},
            status_code=200
        )
    except Exception as e:
        return parser.form_error(e)


@router.get("/all/shopkeepers")
async def get_all_shopkeepers():
    try:
        return JSONResponse(
            {"ids": db.searchall("shopkeepers", "userID")},
            status_code=200
        )
    except Exception as e:
        return parser.form_error(e)


@router.get("/link")
async def check_link(link: str = None):
    if link is None:
        return parser.form_error_bad_parsing()

    try:
        search_result = db.search("store_form_link", "link", link)
        if search_result is None:
            raise lpsql.exceptions.IDNotFound

        return JSONResponse(
            {"email": search_result["email"]},
            status_code=200
        )
    except lpsql.exceptions.IDNotFound as e:
        return parser.form_error(e, "link not found", 404)
    except Exception as e:
        return parser.form_error(e)
