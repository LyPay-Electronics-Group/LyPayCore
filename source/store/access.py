from fastapi import APIRouter
from fastapi.responses import JSONResponse

from scripts import lpsql, parser
from scripts.unix import unix
from data import config as cfg


router = APIRouter()
db = lpsql.DataBase(cfg.PATHS.DATA + "lypay_database.db", lpsql.Tables.MAIN)
firewall3 = lpsql.DataBase(cfg.PATHS.DATA + "lypay_firewall.db", lpsql.Tables.FIREWALL)


@router.get("/list")
async def access_list(storeID: str = None):
    if storeID is None:
        return parser.form_error_bad_parsing()

    try:
        search_result = db.search("shopkeepers", "storeID", storeID, True)
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


@router.get("/add")
async def access_add(storeID: str = None, userID: int = None):
    if storeID is None or userID is None:
        return parser.form_error_bad_parsing()

    try:
        if db.search("stores", "ID", storeID) is None:
            raise lpsql.exceptions.IDNotFound
        if db.search("users", "ID", userID) is None:
            raise lpsql.exceptions.IDNotFound

        db.insert(
            "shopkeepers",
            [userID, storeID]
        )
        firewall3.insert(
            "stores",
            [
                userID,  # ID
                unix(),  # unix
                True,    # access
                "added by access router"  # comment
            ]
        )
        return JSONResponse(
            {"ok": True},
            status_code=201
        )
    except lpsql.exceptions.IDNotFound as e:
        return parser.form_error(e, "ID not found", 404)
    except Exception as e:
        return parser.form_error(e)
