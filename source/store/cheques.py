from fastapi import APIRouter
from fastapi.responses import JSONResponse

from jwt import decode as jwt_decode

from dotenv import load_dotenv
from os import getenv

from scripts import lpsql, parser
from scripts.idgen import IDGenerator
from scripts.unix import unix
from data import config as cfg


router = APIRouter()
db = lpsql.DataBase(cfg.PATHS.DATA + "lypay_database.db", lpsql.Tables.MAIN)
idgen = IDGenerator(db)

load_dotenv()


@router.get("/get")
async def get_cheque(chequeID: str = None):
    if chequeID is None:
        return parser.form_error_bad_parsing()

    try:
        search_result = db.search("cheques", "chequeID", chequeID)
        if search_result is None:
            raise lpsql.exceptions.IDNotFound

        return JSONResponse(
            search_result,
            status_code=200
        )
    except lpsql.exceptions.IDNotFound as e:
        return parser.form_error(e, "ID not found", 404)
    except Exception as e:
        return parser.form_error(e)


@router.get("/all")
async def get_all_cheques(storeID: str = None, active_filter: bool = None):
    if storeID is None:
        return parser.form_error_bad_parsing()

    active_filter = bool(active_filter)
    try:
        search_result = list()
        for item in db.search("cheques", "storeID", storeID, True):
            if active_filter and item['active']:
                search_result.append(item)

        if len(search_result) == 0:
            raise lpsql.exceptions.IDNotFound

        return JSONResponse(
            {"result": search_result},
            status_code=200
        )
    except lpsql.exceptions.IDNotFound as e:
        return parser.form_error(e, "ID not found", 404)
    except Exception as e:
        return parser.form_error(e)


@router.get("/add")
async def create_cheque(storeID: str = None, customer: int = None, values: str = None):
    if storeID is None or customer is None or values is None:
        return parser.form_error_bad_parsing()

    try:
        if storeID not in db.searchall("stores", "ID"):
            raise lpsql.exceptions.IDNotFound

        parsed_values = jwt_decode(values, getenv("LYPAY_JWT"), algorithm="HS256")
        chequeID = await idgen.chequeID(storeID)

        db.insert("cheques", [
            chequeID,
            storeID,
            unix(),
            customer,
            parsed_values,
            True  # active flag
        ])
        return JSONResponse(
            {'generated': chequeID},
            status_code=201
        )
    except lpsql.exceptions.IDNotFound as e:
        return parser.form_error(e, "ID not found", 404)
    except Exception as e:
        return parser.form_error(e)


@router.get("/de")
async def deactivate_cheque(chequeID: str = None):
    if chequeID is None:
        return parser.form_error_bad_parsing()

    try:
        db.update("cheques", "chequeID", chequeID, "active", False)

        return JSONResponse(
            {'ok': True},
            status_code=200
        )
    except lpsql.exceptions.EntryNotFound as e:
        return parser.form_error(e, "ID not found", 404)
    except Exception as e:
        return parser.form_error(e)
