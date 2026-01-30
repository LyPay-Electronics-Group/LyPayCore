from fastapi import APIRouter
from fastapi.responses import JSONResponse, FileResponse

from os.path import exists, getmtime

from scripts import lpsql, memory, parser
from data import config as cfg


router = APIRouter()
db = lpsql.DataBase(cfg.PATHS.DATA + "lypay_database.db", lpsql.Tables.MAIN)


@router.get("/check")
async def check(ID: str = None, unix: str = None):
    if ID is None or unix is None:
        return parser.form_error_bad_parsing()

    try:
        path = cfg.PATHS.QR + f"{ID}.png"
        exist = exists(path)
        return JSONResponse(
            {'exists': exist, 'actual': exist and getmtime(path) <= float(unix)},
            status_code=200
        )
    except Exception as e:
        return parser.form_error(e)


@router.get("/get")
async def get(ID: str = None):
    if ID is None:
        return parser.form_error_bad_parsing()

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
        return parser.form_error(e)
