from fastapi import APIRouter, Depends as D
from fastapi.responses import JSONResponse

from scripts import parser
from scripts.unix import unix
from scripts.token_validator import token_validate_factory as TVF
from data import config as cfg
import database as db


router = APIRouter()


@router.get("/transfer")
async def transfer(
        ID_out: int = None,
        ID_in: str = None,
        amount: int = None,
        mode: str = None,
        _ = D(TVF(*cfg.TOKENIZER.ADMIN_LIST))
):
    if ID_out is None or ID_in is None or amount is None or mode is None or mode not in ('t', 'b'):
        return parser.form_error_bad_parsing()
    if not await parser.get_setting("user_can_transfer"):
        return parser.form_error_flag_blocked()

    try:
        if amount <= 0:
            raise db.exceptions.ValueLoE0

        async with db.session_link() as session:
            async with session.begin():
                out_ = await session.get(db.User, ID_out)
                if out_ is None:
                    raise db.exceptions.NotFound
                if out_.balance < amount:
                    raise db.exceptions.NotEnoughBalance


                if mode == 't':
                    in_ = await session.get(db.User, int(ID_in))
                else:  # mode == 'b'
                    in_ = await session.get(db.Store, ID_in)
                if in_ is None:
                    raise db.exceptions.NotFound

                out_.balance -= amount
                in_.balance += amount

                unix_timestamp = unix()
                out_.last_online = unix_timestamp
                session.add(db.HistoryEntry(
                    ID_out=f"u{ID_out}",
                    ID_in=f"{'s' if mode == 't' else 'u'}{ID_in}",
                    value=amount,
                    unix=unix_timestamp
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


@router.get("/transfer_list")
async def transfer_list(
        ID_out: int = None,
        ID_in: int = None,
        _ = D(TVF(*cfg.TOKENIZER.ADMIN_LIST))
):
    if not ((ID_out is None) ^ (ID_in is None)):
        return parser.form_error_bad_parsing()

    try:
        async with db.session_link() as session:
            if ID_out is not None:
                if await session.get(db.User, ID_out) is None:
                    raise db.exceptions.NotFound
                return JSONResponse(
                    {
                        'result': list(map(tuple, (await session.execute(
                            db.select(
                                db.HistoryEntry.ID_in,
                                db.HistoryEntry.value,
                                db.HistoryEntry.unix
                            ).where(
                                db.HistoryEntry.ID_out == f"u{ID_out}",
                                db.HistoryEntry.ID_in.startswith('u')
                            ).with_for_update(read=True)
                        )).all()))
                    },
                    status_code=200
                )
            else:
                if await session.get(db.User, ID_in) is None:
                    raise db.exceptions.NotFound
                return JSONResponse(
                    {
                        'result': list(map(tuple, (await session.execute(
                            db.select(
                                db.HistoryEntry.ID_out,
                                db.HistoryEntry.value,
                                db.HistoryEntry.unix
                            ).where(
                                db.HistoryEntry.ID_in == f"u{ID_in}",
                                db.HistoryEntry.ID_out.startswith('u')
                            ).with_for_update(read=True)
                        )).all()))
                    },
                    status_code=200
                )
    except db.exceptions.NotFound as e:
        return parser.form_error(e, "ID not found", 404)
    except Exception as e:
        return parser.form_error(e)


@router.get("/deposit_list")
async def deposit_list(
        ID: int = None,
        _ = D(TVF(*cfg.TOKENIZER.ADMIN_LIST))
):
    if ID is None:
        return parser.form_error_bad_parsing()

    try:
        async with db.session_link() as session:
            if await session.get(db.User, ID) is None:
                raise db.exceptions.NotFound
            return JSONResponse(
                {
                    'result': list(map(tuple, (await session.execute(
                        db.select(
                            db.HistoryEntry.value,
                            db.HistoryEntry.unix
                        ).where(
                            db.HistoryEntry.ID_in == f"u{ID}",
                            db.HistoryEntry.ID_out.startswith('d')
                        ).with_for_update(read=True)
                    )).all()))
                },
                status_code=200
            )
    except db.exceptions.NotFound as e:
        return parser.form_error(e, "ID not found", 404)
    except Exception as e:
        return parser.form_error(e)


@router.get("/cheque_list")
async def cheque_list(
        ID: int = None,
        _ = D(TVF(*cfg.TOKENIZER.ADMIN_LIST))
):
    if ID is None:
        return parser.form_error_bad_parsing()

    try:
        async with db.session_link() as session:
            if await session.get(db.User, ID) is None:
                raise db.exceptions.NotFound
            return JSONResponse(
                {
                    'result': list(map(tuple, (await session.execute(
                        db.select(
                            db.Cheque.storeID,
                            db.Cheque.items,
                            db.Cheque.unix
                        ).where(
                            db.Cheque.customer == ID
                        ).with_for_update(read=True)
                    )).all()))
                },
                status_code=200
            )
    except db.exceptions.NotFound as e:
        return parser.form_error(e, "ID not found", 404)
    except Exception as e:
        return parser.form_error(e)
