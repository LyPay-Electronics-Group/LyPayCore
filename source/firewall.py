from fastapi import APIRouter, Depends as D
from fastapi.responses import JSONResponse

from scripts import lpsql, parser
from scripts.j2 import fromfile_async as j2_fromfile_async
from scripts.token_validator import token_validate_factory as TVF
from data.config import PATHS, TOKENIZER


router = APIRouter()
db = lpsql.DataBase(PATHS.DATA + "lypay_firewall.db", lpsql.Tables.FIREWALL)


@router.get("/setting")
async def get_setting(
        key: str,
        _ = D(TVF(*TOKENIZER.ADMIN_LIST))
):
    if key is None:
        return parser.form_error_bad_parsing()
    key = key.lower()
    data = await j2_fromfile_async(PATHS.LAUNCH_SETTINGS)
    if key not in data.keys():
        return parser.form_error(NameError(), "invalid route", 404)

    try:
        return JSONResponse(
            {'result': data[key]},
            status_code=200
        )
    except Exception as e:
        return parser.form_error(e)


@router.get("/{route}")
async def info(
        route: str,
        ID:    int = None,
        _ = D(TVF(*TOKENIZER.ADMIN_LIST))
):
    if ID is None:
        return parser.form_error_bad_parsing()
    elif route.lower() not in lpsql.Tables.FIREWALL:
        return parser.form_error(NameError(), "invalid route", 404)

    try:
        search_result = db.search(route, "ID", ID, True)
        if len(search_result) == 0:
            raise lpsql.exceptions.IDNotFound

        return JSONResponse(
            {'result': search_result},
            status_code=200
        )
    except lpsql.exceptions.IDNotFound as e:
        return parser.form_error(e, "ID not found", 404)
    except Exception as e:
        return parser.form_error(e)
