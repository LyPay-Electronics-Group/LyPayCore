from fastapi import APIRouter
from fastapi.responses import JSONResponse

from scripts import lpsql, parser
from data import config as cfg


router = APIRouter()
db = lpsql.DataBase(cfg.PATHS.DATA + "lypay_database.db", lpsql.Tables.MAIN)


@router.get("/transfer")
async def check_agent_status(ID_in: str = None, ID_out: str = None, amount: int = None):
    if ID_in is None or ID_out is None or amount is None:
        return parser.form_error_bad_parsing()

    try:
        db.transfer(ID_out, ID_in, amount)
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
