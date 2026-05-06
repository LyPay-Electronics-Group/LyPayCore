from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from scripts import lpsql, parser
from scripts.token_validator import token_validate_factory
from data import config as cfg


router = APIRouter()
db = lpsql.DataBase(cfg.PATHS.DATA + "lypay_database.db", lpsql.Tables.MAIN)


@router.get("/get")
async def get_basic_info(
        ID:    int = None,
        email: str = None,
        login: str = None,
        _ = Depends(token_validate_factory('default'))
):
    if ID is None and email is None and login is None:
        return parser.form_error_bad_parsing()

    try:
        if ID is not None:
            result = db.search("users", "ID", ID)
        elif email is not None:
            result = db.search("users", "email", email)
        else:
            result = db.search("users", "login", login)

        if result is None:
            raise lpsql.exceptions.IDNotFound()

        result["group"] = result.pop("class")
        return JSONResponse(
            result,
            status_code=200
        )
    except lpsql.exceptions.IDNotFound as e:
        return parser.form_error(e, "ID not found", 404)
    except Exception as e:
        return parser.form_error(e)


@router.get("/all")
async def get_all_users_ids(
        _ = Depends(token_validate_factory('default'))
):
    try:
        return JSONResponse(
            {"ids": db.searchall("users", "ID")},
            status_code=200
        )
    except Exception as e:
        return parser.form_error(e)


@router.get("/code")
async def check_code(
        code: str = None,
        _ = Depends(token_validate_factory('default'))
):
    if code is None:
        return parser.form_error_bad_parsing()

    try:
        search_result = db.search("access_codes_main", "code", code)
        if search_result is None:
            raise lpsql.exceptions.EmailNotFound

        return JSONResponse(
            {"email": search_result["email"]},
            status_code=200
        )
    except lpsql.exceptions.EmailNotFound as e:
        return parser.form_error(e, "email not found", 404)
    except Exception as e:
        return parser.form_error(e)
