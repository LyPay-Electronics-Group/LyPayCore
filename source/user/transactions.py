from fastapi import APIRouter, Depends as D
from fastapi.responses import JSONResponse

from scripts import lpsql, parser
from scripts.unix import unix
from scripts.token_validator import token_validate_factory as TVF
from data import config as cfg


router = APIRouter()
db = lpsql.DataBase(cfg.PATHS.MAIN_DB, lpsql.Tables.MAIN)


@router.get("/transfer")
async def transfer(
        ID_out: int = None,
        ID_in: str = None,
        amount: int = None,
        mode: str = None,
        _ = D(TVF(*cfg.TOKENIZER.ADMIN_LIST))
):
    if ID_out is None or ID_in is None or amount is None or mode is None or mode not in ('t', 'b'):
        return parser.form_error_bad_parsing()
    if not await parser.get_setting("user_can_transfer"):
        return parser.form_error_flag_blocked()

    try:
        db.transfer(ID_out, ID_in if mode == 'b' else int(ID_in), amount)
        db.update("users", "ID", ID_out, "last_online", unix())
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


@router.get("/transfer_list")
async def transfer_list(
        ID_out: int = None,
        ID_in: int = None,
        _ = D(TVF(*cfg.TOKENIZER.ADMIN_LIST))
):
    if not ((ID_out is None) ^ (ID_in is None)):
        return parser.form_error_bad_parsing()

    try:
        if ID_out is not None:
            if db.search("users", "ID", ID_out) is None:
                raise lpsql.exceptions.IDNotFound()
            return JSONResponse(
                {'result':
                     db.manual(f"SELECT id_in, value, unix FROM history WHERE id_out LIKE \"u{ID_out}\" AND id_in LIKE \"u%\"")
                },
                status_code=200
            )
        else:
            if db.search("users", "ID", ID_in) is None:
                raise lpsql.exceptions.IDNotFound()
            return JSONResponse(
                {'result':
                     db.manual(f"SELECT id_out, value, unix FROM history WHERE id_in LIKE \"u{ID_out}\" AND id_out LIKE \"u%\"")
                },
                status_code=200
            )
    except lpsql.exceptions.IDNotFound as e:
        return parser.form_error(e, "ID not found", 404)
    except Exception as e:
        return parser.form_error(e)


@router.get("/deposit_list")
async def deposit_list(
        ID: int = None,
        _ = D(TVF(*cfg.TOKENIZER.ADMIN_LIST))
):
    if ID is None:
        return parser.form_error_bad_parsing()

    try:
        if db.search("users", "ID", ID) is None:
            raise lpsql.exceptions.IDNotFound()
        return JSONResponse(
            {'result':
                 db.manual(f"SELECT value, unix FROM history WHERE id_in LIKE \"u{ID}\" AND id_out LIKE \"d%\"")
            },
            status_code=200
        )
    except lpsql.exceptions.IDNotFound as e:
        return parser.form_error(e, "ID not found", 404)
    except Exception as e:
        return parser.form_error(e)
