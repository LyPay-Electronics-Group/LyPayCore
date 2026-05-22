from fastapi import APIRouter, Depends as D
from fastapi.responses import JSONResponse

from scripts import lpsql, parser
from scripts.token_validator import token_validate_factory as TVF
from data import config as cfg


router = APIRouter()
db = lpsql.DataBase(cfg.PATHS.MAIN_DB, lpsql.Tables.MAIN)


@router.get("/lottery")
async def lottery(
        ID: str = None,
        _ = D(TVF(*cfg.TOKENIZER.ADMIN_LIST))
):
    if ID is None:
        return parser.form_error_bad_parsing()
    if not await parser.get_setting("auction"):
        return parser.form_error_flag_blocked()

    try:
        db.transfer(ID, "auction_lottery_route", 1000)
        return JSONResponse(
            {"ok": True},
            status_code=200
        )
    except lpsql.exceptions.NotEnoughBalance as e:
        return parser.form_error(e, "not enough balance", 409)
    except lpsql.exceptions.IDNotFound as e:
        return parser.form_error(e, "ID not found", 404)
    except Exception as e:
        return parser.form_error(e)
