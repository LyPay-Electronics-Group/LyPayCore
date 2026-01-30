from fastapi import APIRouter
from fastapi.responses import JSONResponse

from scripts import lpsql, parser
from data import config as cfg


router = APIRouter()
db = lpsql.DataBase(cfg.PATHS.DATA + "lypay_database.db", lpsql.Tables.MAIN)


@router.get("/balance")
async def balance(ID: int = None):
    if ID is None:
        return parser.form_error_bad_parsing()

    try:
        return JSONResponse(
            {'balance': db.balance_view(ID)},
            status_code=200
        )
    except lpsql.exceptions.IDNotFound as e:
        return parser.form_error(e, "ID not found", 404)
    except Exception as e:
        return parser.form_error(e)


@router.get("/deposit")
async def deposit(ID: int = None, value: int = None, agent_id: int = None):
    if ID is None or value is None:
        return parser.form_error_bad_parsing()

    try:
        db.deposit(ID, value, agent_id)
        return JSONResponse(
            {"ok": True},
            status_code=200
        )
    except lpsql.exceptions.IDNotFound as e:
        return parser.form_error(e, "ID not found", 404)
    except Exception as e:
        return parser.form_error(e)


@router.get("/transfer")
async def transfer(ID_out: int = None, ID_in: str = None, amount: int = None, mode: str = None):
    if ID_out is None or ID_in is None or amount is None or mode is None or mode not in ('t', 'b'):
        return parser.form_error_bad_parsing()

    try:
        db.transfer(ID_out, ID_in if mode == 'b' else int(ID_in), amount)
        return JSONResponse(
            {"ok": True},
            status_code=200
        )
    except lpsql.exceptions.SubzeroInput as e:
        return parser.form_error(e, "subzero input", 409)
    except lpsql.exceptions.NotEnoughBalance as e:
        return parser.form_error(e, "not enough balance", 409)
    except lpsql.exceptions.IDNotFound as e:
        return parser.form_error(e, "ID not found", 404)
    except Exception as e:
        return parser.form_error(e)
