from fastapi import APIRouter
from fastapi.responses import JSONResponse, FileResponse

from os.path import exists, getmtime

from scripts import lpsql, memory, parser
from data import config as cfg


router = APIRouter()
db = lpsql.DataBase(cfg.PATHS.DATA + "lypay_database.db", lpsql.Tables.MAIN)


@router.get("/info")
async def info(ID: str | None = None):
    if ID is None:
        return JSONResponse(
            {"error": "ValueError"},
            status_code=400
        )
    try:
        result = db.search("users", "ID", int(ID))
        if result is not None:
            return JSONResponse(
                result,
                status_code=200
            )
        return JSONResponse(
            {"error": "NotFound"},
            status_code=404
        )
    except Exception as e:
        return JSONResponse(
            {"error": parser.get_full_name(e)},
            status_code=500
        )


@router.get("/balance")
async def balance(ID: str | None = None):
    if ID is None:
        return JSONResponse(
            {"error": "ValueError"},
            status_code=400
        )
    try:
        result = db.search("users", "ID", int(ID))
        if result is not None:
            return JSONResponse(
                {'balance': result["balance"]},
                status_code=200
            )
        return JSONResponse(
            {"error": "NotFound"},
            status_code=404
        )
    except Exception as e:
        return JSONResponse(
            {"error": parser.get_full_name(e)},
            status_code=500
        )


@router.get("/qr/check")
async def qr_check(ID: str | None = None, unix: str | None = None):
    if ID is None or unix is None:
        return JSONResponse(
            {"error": "ValueError"},
            status_code=400
        )

    try:
        path = cfg.PATHS.QR + f"{ID}.png"
        exist = exists(path)
        return JSONResponse(
            {'exists': exist, 'actual': exist and getmtime(path) <= float(unix)},
            status_code=200
        )
    except Exception as e:
        return JSONResponse(
            {"error": parser.get_full_name(e)},
            status_code=500
        )


@router.get("/qr/get")
async def qr_get(ID: str | None = None):
    if ID is None:
        return JSONResponse(
            {"error": "ValueError"},
            status_code=400
        )
    try:
        path = cfg.PATHS.QR + f"{ID}.png"
        if exists(path):
            return FileResponse(
                path,
                status_code=200
            )
        memory.qr(int(ID))
        return FileResponse(
            path,
            status_code=201
        )
    except Exception as e:
        return JSONResponse(
            {"error": parser.get_full_name(e)},
            status_code=500
        )
