from fastapi import APIRouter, UploadFile
from fastapi.responses import JSONResponse, FileResponse

from os.path import getmtime, exists
from os import remove

from scripts import lpsql, parser, memory
from data import config as cfg


router = APIRouter()
db = lpsql.DataBase(cfg.PATHS.DATA + "lypay_database.db", lpsql.Tables.MAIN)


@router.get("/get")
async def get_avatar(ID: int = None, unix: float = None):
    if ID is None:
        return parser.form_error_bad_parsing()

    try:
        path = cfg.PATHS.STORES_AVATARS + f"{ID}.jpg"
        if db.search("stores", "ID", ID) is not None:
            has_icon = db.search("stores", "ID", ID)["logo"]
        else:
            raise lpsql.exceptions.IDNotFound()

        if not bool(has_icon):
            return JSONResponse(
                {"result": "no icon"},
                status_code=200
            )

        if not exists(path):
            return parser.form_error(FileNotFoundError(), "avatar not found", 404)
        if unix is not None and unix >= getmtime(path):
            return JSONResponse(
                {"result": "avatar didn't change"},
                status_code=200
            )

        return FileResponse(
            path,
            media_type='image/jpg',
            status_code=200
        )
    except lpsql.exceptions.IDNotFound as e:
        return parser.form_error(e, "ID not found", 404)
    except Exception as e:
        return parser.form_error(e)


@router.post("/set")
async def set_avatar(avatar: UploadFile, ID: int = None):
    if ID is None:
        return parser.form_error_bad_parsing()

    try:
        if db.search("stores", "ID", ID) is not None:
            has_icon = db.search("stores", "ID", ID)["logo"]
        else:
            raise lpsql.exceptions.IDNotFound()

        if not bool(has_icon):
            db.update("stores", "ID", ID, "logo", True)

            await memory.save_iterative(avatar, cfg.PATHS.STORES_AVATARS + f"{ID}.jpg")
            return JSONResponse(
                {"ok": True},
                status_code=200
            )
    except lpsql.exceptions.IDNotFound as e:
        return parser.form_error(e, "ID not found", 404)
    except Exception as e:
        return parser.form_error(e)


@router.get("/remove")
async def remove_avatar(ID: int = None):
    if ID is None:
        return parser.form_error_bad_parsing()

    try:
        if db.search("stores", "ID", ID) is None:
            raise lpsql.exceptions.IDNotFound()

        path = cfg.PATHS.STORES_AVATARS + f"{ID}.jpg"
        if exists(path):
            remove(path)

        db.update("stores", "ID", ID, "logo", False)
        return JSONResponse(
            {"ok": True},
            status_code=200
        )
    except lpsql.exceptions.IDNotFound as e:
        return parser.form_error(e, "ID not found", 404)
    except Exception as e:
        return parser.form_error(e)
