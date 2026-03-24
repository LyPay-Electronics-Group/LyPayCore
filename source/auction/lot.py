from fastapi import APIRouter
from fastapi.responses import JSONResponse

from scripts import lpsql, parser
from scripts.idgen import IDGenerator
from data import config as cfg


router = APIRouter()
db = lpsql.DataBase(cfg.PATHS.DATA + "lypay_database.db", lpsql.Tables.MAIN)
idgen = IDGenerator(db)


@router.get("/add")
async def create_new_lot(name: str = None, price: int = None, auctionID: int = None):
    if name is None or price is None or auctionID is None:
        return parser.form_error_bad_parsing()
    if price < 0:
        return parser.form_error(lpsql.exceptions.SubzeroInput(), "subzero input", 409)

    try:
        lotID = await idgen.lotID()
        db.insert("auction", [
            lotID,       # lotID
            name,        # name
            price,       # price
            auctionID,   # auctionID
            0            # confirmed
        ])
        return JSONResponse(
            {"generated": lotID},
            status_code=200
        )
    except Exception as e:
        return parser.form_error(e)


@router.get("/confirm")
async def confirm_lot(lotID: int = None):
    if lotID is None:
        return parser.form_error_bad_parsing()

    try:
        lot_record = db.search("auction", "lotID", lotID)
        if lot_record is None:
            raise lpsql.exceptions.IDNotFound
        storeID = db.search("stores", "auctionID", lot_record["auctionID"])["ID"]

        db.transfer(storeID, "auction_transfer_route", lot_record["price"])
        # TODO: НУЖНА ПРОВЕРКА НА ЕДИНИЧНОСТЬ, чтобы исключить редактирование неверной записи (.update берёт первое совпадение)
        db.update("auction", "lotID", lotID, "confirmed", 1)

        return JSONResponse(
            {"ok": True},
            status_code=200
        )
    except lpsql.exceptions.IDNotFound as e:
        return parser.form_error(e, "ID not found", 404)
    except lpsql.exceptions.NotEnoughBalance as e:
        return parser.form_error(e, "not enough balance", 409)
    except Exception as e:
        return parser.form_error(e)
