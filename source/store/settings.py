from fastapi import APIRouter
from fastapi.responses import JSONResponse, FileResponse
from os.path import getmtime

from scripts import lpsql, parser
from data import config as cfg


router = APIRouter()
db = lpsql.DataBase(cfg.PATHS.DATA + "lypay_database.db", lpsql.Tables.MAIN)


@router.get("/avatar/get")
async def get_avatar(ID: int = None, unix: float = None):
    if ID is None or unix is None:
        return parser.form_error_bad_parsing()

    try:
        has_icon = db.search("stores", "ID", ID)["logo"]
        if has_icon is None:
            return JSONResponse(
                {"result": "no icon"},
                status_code=200
            )

        path = cfg.PATHS.STORES_AVATARS + f"{ID}.jpg"
        if unix <= getmtime(path):
            return JSONResponse(
                {"result": "avatar didn't change"},
                status_code=200
            )

        return FileResponse(
            path,
            status_code=200
        )
    except lpsql.exceptions.IDNotFound as e:
        return parser.form_error(e, "ID not found", 404)
    except Exception as e:
        return parser.form_error(e)
