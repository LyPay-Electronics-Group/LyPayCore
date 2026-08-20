from fastapi import APIRouter, UploadFile, Depends as D
from fastapi.responses import JSONResponse, FileResponse

from os.path import getmtime, exists
from os import remove

from scripts import parser, memory
from scripts.token_validator import token_validate_factory as TVF
from data import config as cfg
import database as db


router = APIRouter()


@router.get("/get")
async def get_avatar(
        ID:   int = None,
        unix: float = None,
        _ = D(TVF(*cfg.TOKENIZER.ADMIN_LIST))
):
    if ID is None:
        return parser.form_error_bad_parsing()

    try:
        path = cfg.PATHS.USERS_AVATARS + f"{ID}.jpg"
        async with db.session_link() as session:
            has_icon = await session.scalar(
                db.select(db.User.avatar).where(db.User.ID == ID)
            )
            if has_icon is None:
                raise db.exceptions.NotFound

        if not has_icon:
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
    except db.exceptions.NotFound as e:
        return parser.form_error(e, "ID not found", 404)
    except Exception as e:
        return parser.form_error(e)


@router.post("/upd")
async def update_avatar(
        avatar: UploadFile,
        ID:     int = None,
        _ = D(TVF(*cfg.TOKENIZER.ADMIN_LIST))
):
    if ID is None:
        return parser.form_error_bad_parsing()

    try:
        async with db.session_link() as session:
            async with session.begin():
                user = await session.get(db.User, ID)
                if user is None:
                    raise db.exceptions.NotFound
                user.avatar = True

        await memory.save_iterative(avatar, cfg.PATHS.USERS_AVATARS + f"{ID}.jpg")
        return JSONResponse(
            {"ok": True},
            status_code=200
        )
    except db.exceptions.NotFound as e:
        return parser.form_error(e, "ID not found", 404)
    except Exception as e:
        return parser.form_error(e)


@router.get("/remove")
async def remove_avatar(
        ID: int = None,
        _ = D(TVF(*cfg.TOKENIZER.ADMIN_LIST))
):
    if ID is None:
        return parser.form_error_bad_parsing()

    try:
        async with db.session_link() as session:
            async with session.begin():
                user = await session.get(db.User, ID)
                if user is None:
                    raise db.exceptions.NotFound
                user.avatar = False

        path = cfg.PATHS.USERS_AVATARS + f"{ID}.jpg"
        if exists(path):
            remove(path)
        return JSONResponse(
            {"ok": True},
            status_code=200
        )
    except db.exceptions.NotFound as e:
        return parser.form_error(e, "ID not found", 404)
    except Exception as e:
        return parser.form_error(e)
