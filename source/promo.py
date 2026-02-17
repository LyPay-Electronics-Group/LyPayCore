from fastapi import APIRouter
from fastapi.responses import JSONResponse

from scripts import lpsql, parser
from data.config import PATHS


router = APIRouter()
db = lpsql.DataBase(PATHS.DATA + "lypay_database.db", lpsql.Tables.MAIN)


@router.get("/all")
async def get_all():
    try:
        return JSONResponse(
            {'all': db.get_table("promo")},
            status_code=200
        )
    except Exception as e:
        return parser.form_error(e)


@router.get("/get")
async def get(ID: str = None):
    if ID is None:
        return parser.form_error_bad_parsing()

    try:
        ID = ID.lower()
        record = db.search("promo", "ID", ID)
        if record is None:
            raise lpsql.exceptions.IDNotFound
        return JSONResponse(
            record,
            status_code=200
        )
    except lpsql.exceptions.IDNotFound as e:
        return parser.form_error(e, "ID not found", 404)
    except Exception as e:
        return parser.form_error(e)


@router.get("/add")
async def add(ID: str = None, value: str = None, author: str = None):
    if ID is None or value is None or author is None:
        return parser.form_error_bad_parsing()

    try:
        record = db.search("promo", "ID", ID.lower())
        if record is not None:
            return JSONResponse(
                {"error": "ID already exists", "message": "ID already exists"},
                status_code=409
            )

        db.manual(f"INSERT INTO promo (ID, value, author, active) VALUES ('{ID}', {int(value)}, '{author}', 1)")
        return JSONResponse(
            {'ok': True},
            status_code=200
        )
    except Exception as e:
        return parser.form_error(e)


@router.get("/edit")
async def edit(ID: str = None, value: str = None, author: str = None, active: str = None):
    if ID is None or not any((value, author, active)):
        return parser.form_error_bad_parsing()

    try:
        ID = ID.lower()
        if value is not None:
            db.update("promo", "ID", ID, "value", int(value))
        if author is not None:
            db.update("promo", "ID", ID, "author", author)
        if active is not None:
            active = active.lower()
            active = True if active == "true" else active
            active = False if active == "false" else active
            active = active if type(active) is bool else int(active)
            db.update("promo", "ID", ID, "active", bool(active))
        return JSONResponse(
            {'ok': True},
            status_code=200
        )
    except Exception as e:
        return parser.form_error(e)
