from fastapi import APIRouter
from fastapi.responses import JSONResponse

from scripts import lpsql, parser
from data import config as cfg


router = APIRouter()
db = lpsql.DataBase(cfg.PATHS.DATA + "lypay_database.db", lpsql.Tables.MAIN)


@router.get("/add")
async def create_item(storeID: str = None, name: str = None, price: int = None):
    if storeID is None or name is None or price is None:
        return parser.form_error_bad_parsing()

    try:
        if storeID not in db.searchall("stores", "ID"):
            raise lpsql.exceptions.IDNotFound

        itemID = f"{storeID}_{parser.generate_code(6)}"
        while itemID in db.searchall("items", "itemID"):
            itemID = f"{storeID}_{parser.generate_code(6)}"

        db.insert("items", [
            itemID,
            storeID,
            name,
            price,
            True    # active flag
        ])
        return JSONResponse(
            {'ok': True},
            status_code=201
        )
    except lpsql.exceptions.IDNotFound as e:
        return parser.form_error(e, "ID not found", 404)
    except Exception as e:
        return parser.form_error(e)


@router.get("/del")
async def delete_item(itemID: str = None):
    if itemID is None:
        return parser.form_error_bad_parsing()

    try:
        db.update("items", "itemID", itemID, "active", False)

        return JSONResponse(
            {'ok': True},
            status_code=200
        )
    except lpsql.exceptions.EntryNotFound as e:
        return parser.form_error(e, "ID not found", 404)
    except Exception as e:
        return parser.form_error(e)
