from fastapi import APIRouter, Depends as D
from fastapi.responses import JSONResponse

from scripts import parser
from scripts.token_validator import token_validate_factory as TVF
from data.config import TOKENIZER
import database as db


router = APIRouter()


@router.get("/all")
async def get_all(
        _ = D(TVF(*TOKENIZER.ADMIN_LIST))
):
    try:
        async with db.session_link() as session:
            return JSONResponse(
                {
                    'all': [dict(t) for t in (await session.execute(
                        db.select(db.Promo).where(db.Promo.active.is_(True))
                    )).mappings().all()]
                },
                status_code=200
            )
    except Exception as e:
        return parser.form_error(e)


@router.get("/get")
async def get(
        ID: str = None,
        _ = D(TVF(*TOKENIZER.ADMIN_LIST))
):
    if ID is None:
        return parser.form_error_bad_parsing()

    ID = ID.lower()
    try:
        async with db.session_link() as session:
            record = await session.get(db.Promo, ID)
            if record is None:
                raise db.exceptions.NotFound

        return JSONResponse(
            record.as_dict(),
            status_code=200
        )
    except db.exceptions.NotFound as e:
        return parser.form_error(e, "ID not found", 404)
    except Exception as e:
        return parser.form_error(e)


@router.get("/add")
async def add(
        ID:     str = None,
        value:  str = None,
        author: str = None,
        _ = D(TVF(*TOKENIZER.ADMIN_LIST))
):
    if ID is None or value is None or author is None:
        return parser.form_error_bad_parsing()

    ID = ID.lower()
    try:
        async with db.session_link() as session:
            async with session.begin():
                if (await session.get(db.Promo, ID)) is not None:
                    return JSONResponse(
                        {"error": "ID already exists", "message": "ID already exists"},
                        status_code=409
                    )
                session.add(db.Promo(
                    ID=ID,
                    value=int(value),
                    author=author,
                    active=True
                ))

        return JSONResponse(
            {'ok': True},
            status_code=200
        )
    except Exception as e:
        return parser.form_error(e)


@router.get("/edit")
async def edit(
        ID:     str = None,
        value:  str = None,
        author: str = None,
        active: str = None,
        _ = D(TVF(*TOKENIZER.ADMIN_LIST))
):
    if ID is None or not any((value, author, active)):
        return parser.form_error_bad_parsing()

    ID = ID.lower()
    try:
        async with db.session_link() as session:
            async with session.begin():
                promo = await session.get(db.Promo, ID, with_for_update=True)
                if value is not None:
                    promo.value = int(value)
                if author is not None:
                    promo.author = author
                if active is not None:
                    active = active.lower()
                    active = True if active == "true" else active
                    active = False if active == "false" else active
                    active = active if type(active) is bool else int(active)
                    promo.active = bool(active)

        return JSONResponse(
            {'ok': True},
            status_code=200
        )
    except ValueError:
        return parser.form_error_bad_parsing()
    except Exception as e:
        return parser.form_error(e)
