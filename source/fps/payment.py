from fastapi import APIRouter, Depends as D
from fastapi.responses import JSONResponse

from scripts import parser
from scripts.token_validator import token_validate_factory as TVF
from scripts.idgen import IDGenerator
from scripts.unix import unix
from data import config as cfg
import database as db


router = APIRouter()
idgen = IDGenerator()


@router.get("/pay")
async def pay(
        fpsID:  str = None,
        userID: int = None,
        _ = D(TVF(*cfg.TOKENIZER.ADMIN_LIST))
):
    if fpsID is None or userID is None:
        return parser.form_error_bad_parsing()

    try:
        async with db.session_link() as session:
            async with session.begin():
                fps = await session.get(db.FPS, fpsID, with_for_update=True)
                if fps is None:
                    raise db.exceptions.NotFound

                if fps.author_type == "u":
                    author = await session.get(db.User, int(fps.author), with_for_update=True)
                else:
                    author = await session.get(db.Store, fps.author, with_for_update=True)
                user = await session.get(db.User, userID, with_for_update=True)

                if user is None or author is None:
                    raise db.exceptions.NotFound

                current_unix = unix()
                user.balance -= fps.amount
                author.balance += fps.amount
                session.add(db.HistoryEntry(
                    ID_out=f"u{user.ID}",
                    ID_in=f"{fps.author_type}{author.ID}",
                    value=fps.amount,
                    unix=current_unix
                ))

                if fps.author_type == "s":
                    itemID = await idgen.itemID(fps.author, session)
                    session.add(db.Item(
                        itemID=itemID,
                        storeID=fps.author,
                        name=f"FPS#{fpsID}",
                        price=fps.amount,
                        active=False
                    ))

                    chequeID = await idgen.chequeID(fps.author, session)
                    session.add(db.Cheque(
                        chequeID=itemID,
                        storeID=fps.author,
                        unix=current_unix,
                        customer=userID,
                        items={itemID: 1},
                        active=True
                    ))
                else:
                    chequeID = None

                fps.payed = userID
                fps.unix_payment = current_unix
                fps.cheque = chequeID

        return JSONResponse(
            {"chequeID": chequeID},
            status_code=200
        )
    except db.exceptions.NotFound as e:
        return parser.form_error(e, "ID not found", 404)
    except db.exceptions.NotEnoughBalance as e:
        return parser.form_error(e, "not enough balance", 409)
    except Exception as e:
        return parser.form_error(e)
