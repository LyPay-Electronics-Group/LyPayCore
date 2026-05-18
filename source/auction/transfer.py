from fastapi import APIRouter, Depends as D
from fastapi.responses import JSONResponse

from scripts import lpsql, parser
from scripts.token_validator import token_validate_factory as TVF
from data import config as cfg


router = APIRouter()
db = lpsql.DataBase(cfg.PATHS.MAIN_DB, lpsql.Tables.MAIN)


@router.get("/transfer")
async def check_agent_status(
        ID_in:  str = None,
        ID_out: str = None,
        amount: int = None,
        _ = D(TVF(*cfg.TOKENIZER.ADMIN_LIST))
):
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
