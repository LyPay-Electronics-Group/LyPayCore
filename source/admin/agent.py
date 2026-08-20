from fastapi import APIRouter, Depends as D
from fastapi.responses import JSONResponse

from scripts import parser
from scripts.unix import unix
from scripts.token_validator import token_validate_factory as TVF
from data import config as cfg
import database as db


router = APIRouter()


@router.get("/check")
async def check_agent_status(
        userID: int = None,
        _ = D(TVF(*cfg.TOKENIZER.ADMIN_LIST))
):
    if userID is None:
        return parser.form_error_bad_parsing()

    try:
        async with db.session_link() as session:
            user = await session.get(db.User, userID)
            if user is None:
                raise db.exceptions.NotFound

            firewall_entry = (await session.execute(
                db.select(db.FirewallAdminsEntry).where(db.FirewallAdminsEntry.ID == userID)
            )).scalar_one_or_none()

        return JSONResponse(
            {'result': firewall_entry is not None},
            status_code=200
        )
    except db.exceptions.NotFound as e:
        return parser.form_error(e, "ID not found", 404)
    except Exception as e:
        return parser.form_error(e)


@router.get("/deposit")
async def do_agent_deposit(
        userID:  int = None,
        amount:  int = None,
        agentID: int = None,
        _ = D(TVF(*cfg.TOKENIZER.ADMIN_LIST))
):
    if userID is None or amount is None or agentID is None:
        return parser.form_error_bad_parsing()
    if not await parser.get_setting("user_can_deposit"):
        return parser.form_error_flag_blocked()

    try:
        # if amount <= 0:
            # raise db.ValueLoE0

        async with db.session_link() as session:
            async with session.begin():
                user = await session.get(db.User, userID, with_for_update=True)
                if user is None:
                    raise db.exceptions.NotFound

                user.balance += amount

                history_entry = db.HistoryEntry(
                    ID_out=f"d{agentID}",
                    ID_in=f"u{userID}",
                    value=amount,
                    unix=unix()
                )
                session.add(history_entry)
        return JSONResponse(
            {'ok': True},
            status_code=200
        )
    except db.exceptions.NotFound as e:
        return parser.form_error(e, "ID not found", 404)
    # except db.exceptions.ValueLoE0 as e:
        # return parser.form_error(e, "subzero input", 409)
    except Exception as e:
        return parser.form_error(e)


@router.get("/deposit_auc")
async def do_auction_deposit(
        auctionID: int = None,
        amount:    int = None,
        agentID:   int = None,
        _ = D(TVF(*cfg.TOKENIZER.ADMIN_LIST))
):
    if auctionID is None or amount is None or agentID is None:
        return parser.form_error_bad_parsing()
    if not await parser.get_setting("auction"):
        return parser.form_error_flag_blocked()

    try:
        # if amount <= 0:
            # raise db.ValueLoE0

        async with db.session_link() as session:
            async with session.begin():
                store = (await session.execute(
                    db.select(db.Store).where(db.Store.auctionID == auctionID).with_for_update()
                )).scalar_one_or_none()
                if store is None:
                    raise db.exceptions.NotFound

                store.balance += amount

                history_entry = db.HistoryEntry(
                    ID_out=f"d{agentID}",
                    ID_in=f"s{store.ID}",
                    value=amount,
                    unix=unix()
                )
                session.add(history_entry)

        return JSONResponse(
            {'ok': True},
            status_code=200
        )
    except db.exceptions.NotFound as e:
        return parser.form_error(e, "ID not found", 404)
    # except db.exceptions.ValueLoE0 as e:
        # return parser.form_error(e, "subzero input", 409)
    except Exception as e:
        return parser.form_error(e)
