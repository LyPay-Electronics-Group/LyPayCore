from fastapi import APIRouter, Depends as D
from fastapi.responses import JSONResponse

from scripts import lpsql, parser
from scripts.token_validator import token_validate_factory as TVF
from scripts.idgen import IDGenerator
from scripts.unix import unix
from data import config as cfg


router = APIRouter()
db = lpsql.DataBase(cfg.PATHS.DATA + "lypay_database.db", lpsql.Tables.MAIN)
idgen = IDGenerator(db)


@router.get("/pay")
async def pay(
        fpsID:  str = None,
        userID: int = None,
        _ = D(TVF(*cfg.TOKENIZER.ADMIN_LIST))
):
    if fpsID is None or userID is None:
        return parser.form_error_bad_parsing()

    try:
        fps = db.search("fps", "ID", fpsID)
        if fps is None:
            raise lpsql.exceptions.IDNotFound

        db.transfer(userID, fps["author"], fps["amount"])

        current_unix = unix()
        if type(fps["author"]) is str:
            itemID = await idgen.itemID(fps["author"])
            db.insert("items", [
                itemID,
                fps["author"],
                f"автоматическая оплата FPS#{fpsID}",
                fps["amount"],
                False  # active flag
            ])

            chequeID = await idgen.chequeID(fps["author"])
            db.insert("cheques", [
                chequeID,
                fps["author"],
                current_unix,
                userID,
                f'{{"{itemID}":1}}',
                True  # active flag
            ])
        else:
            chequeID = None

        db.update("fps", "ID", fpsID, "payed", userID)
        db.update("fps", "ID", fpsID, "unix_payment", current_unix)
        db.update("fps", "ID", fpsID, "cheque", chequeID)

        return JSONResponse(
            {"chequeID": chequeID},
            status_code=200
        )
    except lpsql.exceptions.IDNotFound as e:
        return parser.form_error(e, "ID not found", 404)
    except Exception as e:
        return parser.form_error(e)
