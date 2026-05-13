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

default_description = """
FPS-<=>, созданный {author}.
"""[1:-1]

@router.get("/new")
async def new(
        amount: int = None,
        author: str = None,
        description: str = None,
        _ = D(TVF(*cfg.TOKENIZER.PUBLIC_LIST))
):
    if amount is None or author is None:
        return parser.form_error_bad_parsing()

    if len(author) != 3:
        try:
            author = int(author)
            author_search = db.search("users", "ID", author)
        except ValueError:
            return parser.form_error_bad_parsing()
    else:
        author_search = db.search("stores", "ID", author)

    if author_search is None:
        return parser.form_error(lpsql.exceptions.IDNotFound(), "ID not found", 404)

    if description is None:
        description = default_description.format(author=author)
    try:
        ID = await idgen.fpsID()
        db.insert("fps", [
            ID,                                   # ID
            str(author),                          # author
            'u' if type(author) is int else 's',  # author_type
            description,                          # description
            amount,                               # amount
            None,                                 # payed
            None,                                 # cheque
            unix(),                               # unix_creation
            None                                  # unix_payment
        ])

        return JSONResponse(
            {'ID': ID},
            status_code=201
        )
    except Exception as e:
        return parser.form_error(e)


@router.get("/cancel")
async def cancel(
        ID: str = None,
        _ = D(TVF(*cfg.TOKENIZER.PUBLIC_LIST))
):
    if ID is None:
        return parser.form_error_bad_parsing()

    try:
        search_result = db.search("fps", "ID", ID)
        if search_result is None:
            raise lpsql.exceptions.IDNotFound

        if search_result["payed"] is None:
            db.manual(f"DELETE FROM fps WHERE ID like \"{ID}\"")
            return JSONResponse(
                {'ok': True},
                status_code=200
            )

        return parser.form_error(PermissionError(), "FPS is payed", 403)
    except lpsql.exceptions.IDNotFound as e:
        return parser.form_error(e, "ID not found", 404)
    except Exception as e:
        return parser.form_error(e)
