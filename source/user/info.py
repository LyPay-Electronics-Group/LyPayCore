from fastapi import APIRouter, Depends as D
from fastapi.responses import JSONResponse

from scripts import parser
from scripts.token_validator import token_validate_factory as TVF
from data import config as cfg
import database as db


router = APIRouter()


@router.get("/get")
async def get_basic_info(
        ID:    int = None,
        email: str = None,
        login: str = None,
        _ = D(TVF(*cfg.TOKENIZER.ADMIN_LIST))
):
    if ID is None and email is None and login is None:
        return parser.form_error_bad_parsing()

    comment = None
    try:
        async with db.session_link() as session:
            if ID is not None:
                result = await session.get(db.User, ID)
                if result is None:
                    comment = "ID not found"
                    raise db.exceptions.NotFound
            elif email is not None:
                result = (await session.scalars(
                    db.select(db.User).where(db.User.email == email)
                )).one_or_none()
                if result is None:
                    comment = "email not found"
                    raise db.exceptions.NotFound
            else:
                result = (await session.scalars(
                    db.select(db.User).where(db.User.login == login)
                )).one_or_none()
                if result is None:
                    comment = "login not found"
                    raise db.exceptions.NotFound

        result = result.as_dict()
        result["group"] = result.pop("category")
        return JSONResponse(
            result,
            status_code=200
        )
    except db.exceptions.NotFound as e:
        return parser.form_error(e, comment, 404)
    except Exception as e:
        return parser.form_error(e)


@router.get("/all")
async def get_all_users_ids(
        _ = D(TVF(*cfg.TOKENIZER.ADMIN_LIST))
):
    try:
        async with db.session_link() as session:
            return JSONResponse(
                {
                    "ids": (await session.scalars(
                        db.select(db.User.ID)
                    )).all()
                },
                status_code=200
            )
    except Exception as e:
        return parser.form_error(e)


@router.get("/code")
async def check_code(
        code: str = None,
        route: str = "main",
        _ = D(TVF(*cfg.TOKENIZER.ADMIN_LIST))
):
    if code is None or route not in ('main', 'guest'):
        return parser.form_error_bad_parsing()

    try:
        async with db.session_link() as session:
            search_result = await session.scalar(
                db.text(f"SELECT email FROM access_codes_{route} WHERE code = '{code}'")
            )
            if search_result is None:
                raise db.exceptions.NotFound

        return JSONResponse(
            {"email": search_result},
            status_code=200
        )
    except db.exceptions.NotFound as e:
        return parser.form_error(e, "email not found", 404)
    except Exception as e:
        return parser.form_error(e)
