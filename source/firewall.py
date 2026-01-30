from fastapi import APIRouter
from fastapi.responses import JSONResponse

from scripts import lpsql, parser
from data.config import PATHS


router = APIRouter()
db = lpsql.DataBase(PATHS.DATA + "lypay_firewall.db", lpsql.Tables.FIREWALL)


@router.get("/{route}")
async def info(route: str, ID: str = None):
    if ID is None:
        return parser.form_error_bad_parsing()

    elif route.lower() not in ('main', 'stores', 'admins'):
        return JSONResponse(
            {"error": "NameError", "message": "invalid route"},
            status_code=404
        )
    try:
        search_result = db.search(route, "ID", int(ID))
        return JSONResponse(
            {
                'found': search_result is not None,
                'entry': search_result
            },
            status_code=200
        )
    except Exception as e:
        return parser.form_error(e)
