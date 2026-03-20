from fastapi import APIRouter
from fastapi.responses import JSONResponse

from scripts import lpsql, parser
from data import config as cfg


router = APIRouter()
db = lpsql.DataBase(cfg.PATHS.DATA + "lypay_database.db", lpsql.Tables.MAIN)
firewall4 = lpsql.DataBase(cfg.PATHS.DATA + "lypay_firewall.db", lpsql.Tables.FIREWALL)


@router.get("/check")
async def check_agent_status(userID: int = None):
    if userID is None:
        return parser.form_error_bad_parsing()

    try:
        result = firewall4.search("admins", "ID", userID)
        if result is None:
            raise lpsql.exceptions.IDNotFound

        return JSONResponse(
            {'result': result},
            status_code=200
        )
    except lpsql.exceptions.IDNotFound as e:
        return parser.form_error(e, "ID not found", 404)
    except Exception as e:
        return parser.form_error(e)


@router.get("/deposit")
async def do_agent_deposit(userID: int = None, amount: int = None, agentID: int = None):
    if userID is None or amount is None or agentID is None:
        return parser.form_error_bad_parsing()

    try:
        db.deposit(userID, amount, agentID)

        return JSONResponse(
            {'ok': True},
            status_code=200
        )
    except lpsql.exceptions.IDNotFound as e:
        return parser.form_error(e, "ID not found", 404)
    except Exception as e:
        return parser.form_error(e)
