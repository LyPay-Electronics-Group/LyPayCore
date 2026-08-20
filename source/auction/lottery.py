from fastapi import APIRouter, Depends as D
from fastapi.responses import JSONResponse

from scripts import parser
from scripts.unix import unix
from scripts.token_validator import token_validate_factory as TVF
from data import config as cfg
import database as db


router = APIRouter()


@router.get("/lottery")
async def lottery(
        ID: str = None,
        _ = D(TVF(*cfg.TOKENIZER.ADMIN_LIST))
):
    if ID is None:
        return parser.form_error_bad_parsing()
    if not await parser.get_setting("auction"):
        return parser.form_error_flag_blocked()

    try:
        async with db.session_link() as session:
            if await session.get(db.LotteryTicket, ID) is not None:
                raise PermissionError

            async with session.begin():
                store = await session.get(db.Store, ID, with_for_update=True)
                if store is None:
                    raise db.exceptions.NotFound
                if store.balance < 1000:
                    raise db.exceptions.NotEnoughBalance

                auction_lottery_route = await session.get(db.Store, "auction_lottery_route", with_for_update=True)
                store.balance -= 1000
                auction_lottery_route.balance += 1000

                session.add(db.LotteryTicket(
                    ID=ID,
                    unix=unix()
                ))
        return JSONResponse(
            {"ok": True},
            status_code=200
        )
    except PermissionError as e:
        return parser.form_error(e, "ticket has already been purchased", 403)
    except db.exceptions.NotEnoughBalance as e:
        return parser.form_error(e, "not enough balance", 409)
    except db.exceptions.NotFound as e:
        return parser.form_error(e, "ID not found", 404)
    except Exception as e:
        return parser.form_error(e)
