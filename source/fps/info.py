from fastapi import APIRouter, Depends as D
from fastapi.responses import JSONResponse

from scripts import lpsql, parser
from scripts.token_validator import token_validate_factory as TVF
from data import config as cfg


router = APIRouter()
db = lpsql.DataBase(cfg.PATHS.DATA + "lypay_database.db", lpsql.Tables.MAIN)


@router.get("/status")
async def status(
        ID: str = None,
        _ = D(TVF(*cfg.TOKENIZER.PUBLIC_LIST))
):
    if ID is None:
        return parser.form_error_bad_parsing()

    try:
        search_result = db.search("fps", "ID", ID)
        if search_result is None:
            raise lpsql.exceptions.IDNotFound

        if search_result.pop("author_type") == 'u':
            search_result["author"] = int(search_result["author"])

        return JSONResponse(
            search_result,
            status_code=200
        )
    except lpsql.exceptions.IDNotFound as e:
        return parser.form_error(e, "ID not found", 404)
    except Exception as e:
        return parser.form_error(e)

