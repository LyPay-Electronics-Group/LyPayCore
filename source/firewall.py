from fastapi import APIRouter, Depends as D
from fastapi.responses import JSONResponse

from scripts import parser
from scripts.j2 import fromfile_async as j2_fromfile_async
from scripts.token_validator import token_validate_factory as TVF
from data.config import PATHS, TOKENIZER
import database as db


router = APIRouter()


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
    elif route.lower() not in ('main', 'stores', 'admins', 'high'):
        return parser.form_error(NameError(), "invalid route", 404)

    try:
        async with db.session_link() as session:
            search_result = (await session.execute(
                db.select(db.FirewallHighEntry).where(db.FirewallHighEntry.ID == ID),
            )).all()
            if len(search_result) == 0:
                raise db.exceptions.NotFound

        return JSONResponse(
            {'result': list(map(tuple, search_result))},
            status_code=200
        )
    except db.exceptions.NotFound as e:
        return parser.form_error(e, "ID not found", 404)
    except Exception as e:
        return parser.form_error(e)
