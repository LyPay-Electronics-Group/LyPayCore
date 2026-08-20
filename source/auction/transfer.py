from fastapi import APIRouter, Depends as D
from fastapi.responses import JSONResponse

from scripts import parser
from scripts.token_validator import token_validate_factory as TVF
from scripts.unix import unix
from data import config as cfg
import database as db


router = APIRouter()


@router.get("/transfer")
async def check_agent_status(
        ID_in:  str = None,
        ID_out: str = None,
        amount: int = None,
        _ = D(TVF(*cfg.TOKENIZER.ADMIN_LIST))
):
    if ID_in is None or ID_out is None or amount is None:
        return parser.form_error_bad_parsing()
    if not await parser.get_setting("auction"):
        return parser.form_error_flag_blocked()

    try:
        if amount <= 0:
            raise db.exceptions.ValueLoE0

        async with db.session_link() as session:
            async with session.begin():
                store_out = await session.get(db.Store, ID_out, with_for_update=True)
                store_in = await session.get(db.Store, ID_in, with_for_update=True)

                if store_out is None or store_in is None:
                    raise db.exceptions.NotFound
                if store_out.balance < amount:
                    raise db.exceptions.NotEnoughBalance

                store_out.balance -= amount
                store_in.balance += amount

                session.add(db.HistoryEntry(
                    ID_in=f"s{ID_in}",
                    ID_out=f"s{ID_out}",
                    value=amount,
                    unix=unix()
                ))

        return JSONResponse(
            {"ok": True},
            status_code=200
        )
    except db.exceptions.ValueLoE0 as e:
        return parser.form_error(e, "subzero input", 409)
    except db.exceptions.NotEnoughBalance as e:
        return parser.form_error(e, "not enough balance", 409)
    except db.exceptions.NotFound as e:
        return parser.form_error(e, "ID not found", 404)
    except Exception as e:
        return parser.form_error(e)
