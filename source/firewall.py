from fastapi import APIRouter
from fastapi.responses import JSONResponse

from scripts import lpsql, parser
from data.config import PATHS


router = APIRouter()
db = lpsql.DataBase(PATHS.DATA + "lypay_firewall.db", lpsql.Tables.FIREWALL)


@router.get("/{route}")
async def info(route: str, ID: str | None = None):
    if ID is None or route.lower() not in ('main', 'stores', 'admins'):
        return JSONResponse(
            {"error": "ValueError"},
            status_code=400
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
        return JSONResponse(
            {"error": parser.get_full_name(e)},
            status_code=500
        )
