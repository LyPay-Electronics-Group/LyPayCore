from fastapi import APIRouter
from fastapi.responses import JSONResponse

from scripts import parser, lpsql
from data import config as cfg


router = APIRouter()
db = lpsql.DataBase(cfg.PATHS.DATA + "lypay_database.db", lpsql.Tables.MAIN)


@router.get("/test3")
async def test3(ID: int = None):
    if ID is None:
        return parser.form_error_bad_parsing()

    try:
        search = db.search("mst_test3", "ID", ID)

        if search is None:
            db.insert("mst_test3", [ID, 1])
        else:
            db.update("mst_test3", "ID", ID, "value", search["value"] + 1)

        return JSONResponse(
            {"ok": True},
            status_code=200
        )
    except Exception as e:
        return parser.form_error(e)


@router.get("/test3_end")
async def test3_end(ID: int = None):
    if ID is None:
        return parser.form_error_bad_parsing()

    try:
        search = db.search("mst_test3", "ID", ID)

        if search is None:
            search = 0
        else:
            search = search["value"]

        return JSONResponse(
            {"value": search},
            status_code=200
        )
    except Exception as e:
        return parser.form_error(e)
