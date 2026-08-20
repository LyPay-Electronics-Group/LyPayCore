from fastapi import APIRouter, Depends as D
from fastapi.responses import JSONResponse

from scripts import parser, censor
from scripts.token_validator import token_validate_factory as TVF
from scripts.idgen import IDGenerator
from scripts.unix import unix
from data import config as cfg
import database as db


router = APIRouter()
idgen = IDGenerator()

default_description = """
FPS-линк, созданный {author}
"""[1:-1]

@router.get("/new")
async def new(
        amount: int = None,
        author: str = None,
        author_type: str = None,
        description: str = None,
        _ = D(TVF(*cfg.TOKENIZER.PUBLIC_LIST))
):
    if amount is None or author is None or author_type is None or author_type not in ('u', 's'):
        return parser.form_error_bad_parsing()
    if amount < 0:
        return parser.form_error(db.exceptions.ValueLoE0(), "subzero input", 409)

    if description is None:
        description = default_description.format(author=author)
    elif not censor.censor(description):
        return parser.form_error(AttributeError(), "bad censor flag: FPS desc", 406)

    try:
        async with db.session_link() as session:
            if author_type == 'u':
                try:
                    author = int(author)
                    author_search = await session.get(db.User, author)
                except ValueError:
                    return parser.form_error_bad_parsing()
            else:
                author_search = await session.get(db.Store, author)

            if author_search is None:
                return parser.form_error(db.exceptions.NotFound(), "ID not found", 404)

            ID = await idgen.fpsID(session)
            async with session.begin():
                session.add(db.FPS(
                    ID=ID,
                    author=str(author),
                    author_type=author_type,
                    description=description,
                    amount=amount,
                    payed=None,
                    cheque=None,
                    unix_creation=unix(),
                    unix_payment=None
                ))

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
        async with db.session_link() as session:
            fps = await session.get(db.FPS, ID, with_for_update=True)
            if fps is None:
                raise db.exceptions.NotFound
            if fps.payed is not None:
                raise PermissionError

            async with session.begin():
                session.delete(fps)

        return JSONResponse(
            {'ok': True},
            status_code=200
        )
    except PermissionError as e:
        return parser.form_error(e, "FPS is payed", 403)
    except db.exceptions.NotFound as e:
        return parser.form_error(e, "ID not found", 404)
    except Exception as e:
        return parser.form_error(e)
