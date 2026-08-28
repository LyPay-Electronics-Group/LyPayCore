from fastapi import APIRouter, Depends as D
from fastapi.responses import JSONResponse

from scripts import parser
from scripts.token_validator import token_validate_factory as TVF
from data import config as cfg
import database as db


router = APIRouter()


@router.get("/status")
async def status(
        ID: str = None,
        _ = D(TVF(*cfg.TOKENIZER.PUBLIC_LIST))
):
    if ID is None:
        return parser.form_error_bad_parsing()

    try:
        async with db.session_link() as session:
            fps = await session.get(db.FPS, ID)
            if fps is None:
                raise db.exceptions.NotFound

        fps = fps.as_dict()
        if fps.pop("author_type") == 'u':
            fps["author"] = int(fps["author"])

        return JSONResponse(
            fps,
            status_code=200
        )
    except db.exceptions.NotFound as e:
        return parser.form_error(e, "ID not found", 404)
    except Exception as e:
        return parser.form_error(e)

