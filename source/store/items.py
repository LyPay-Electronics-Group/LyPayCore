from fastapi import APIRouter
from fastapi.responses import JSONResponse

from scripts import lpsql, parser, censor
from scripts.idgen import IDGenerator
from data import config as cfg


router = APIRouter()
db = lpsql.DataBase(cfg.PATHS.DATA + "lypay_database.db", lpsql.Tables.MAIN)
idgen = IDGenerator(db)


@router.get("/get")
async def get_item(itemID: str = None):
    if itemID is None:
        return parser.form_error_bad_parsing()

    try:
        search_result = db.search("items", "itemID", itemID)
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
async def get_all_items(storeID: str = None, active_filter: bool = None):
    if storeID is None:
        return parser.form_error_bad_parsing()

    active_filter = bool(active_filter)
    try:
        search_result = list()
        for item in db.search("items", "storeID", storeID, True):
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
async def create_item(storeID: str = None, name: str = None, price: int = None):
    if storeID is None or name is None or price is None:
        return parser.form_error_bad_parsing()

    if not censor.check_store_item_name(name):
        return parser.form_error(AttributeError(), "bad censor flag: store item name", 406)
    if price < 0:
        return parser.form_error(AttributeError(), "bad censor flag: store item price", 406)

    try:
        if storeID not in db.searchall("stores", "ID"):
            raise lpsql.exceptions.IDNotFound

        itemID = await idgen.itemID(storeID)

        db.insert("items", [
            itemID,
            storeID,
            name,
            price,
            True    # active flag
        ])
        return JSONResponse(
            {'generated': itemID},
            status_code=201
        )
    except lpsql.exceptions.IDNotFound as e:
        return parser.form_error(e, "ID not found", 404)
    except Exception as e:
        return parser.form_error(e)


@router.get("/rem")
async def remove_item(itemID: str = None):
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


@router.get("/edit")
async def edit_item(itemID: str = None, name: str = None, price: int = None):
    if itemID is None or (name is None and price is None):
        return parser.form_error_bad_parsing()

    if name is not None and not censor.check_store_item_name(name):
        return parser.form_error(AttributeError(), "bad censor flag: store item name", 406)
    if price is not None and price < 0:
        return parser.form_error(AttributeError(), "bad censor flag: store item price", 406)

    try:
        item = db.search("items", "itemID", itemID)
        if name is not None:
            item["name"] = name
        if price is not None:
            item["price"] = price

        db.update("items", "itemID", itemID, "active", False)

        storeID = item["storeID"]
        itemID = await idgen.itemID(storeID)
        db.insert("items", [
            itemID,
            storeID,
            item["name"],
            item["price"],
            True    # active flag
        ])

        return JSONResponse(
            {'updated': itemID},
            status_code=200
        )
    except lpsql.exceptions.EntryNotFound as e:
        return parser.form_error(e, "ID not found", 404)
    except Exception as e:
        return parser.form_error(e)
