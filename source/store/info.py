from fastapi import APIRouter, Depends as D
from fastapi.responses import JSONResponse

from scripts import parser
from scripts.token_validator import token_validate_factory as TVF
from data import config as cfg
import database as db


router = APIRouter()


@router.get("/get/base")
async def get_basic_info(
        ID: str = None,
        _ = D(TVF(*cfg.TOKENIZER.ADMIN_LIST))
):
    if ID is None:
        return parser.form_error_bad_parsing()

    try:
        async with db.session_link() as session:
            search_result = await session.get(db.Store, ID)
            if search_result is None:
                raise db.exceptions.NotFound

        return JSONResponse(
            search_result.as_dict(),
            status_code=200
        )
    except db.exceptions.NotFound as e:
        return parser.form_error(e, "ID not found", 404)
    except Exception as e:
        return parser.form_error(e)


@router.get("/get/shopkeeper")
async def get_by_shopkeeper(
        ID: int = None,
        _ = D(TVF(*cfg.TOKENIZER.ADMIN_LIST))
):
    if ID is None:
        return parser.form_error_bad_parsing()

    try:
        async with db.session_link() as session:
            search_result = (await session.scalars(
                db.select(db.Shopkeeper).where(db.Shopkeeper.userID == ID)
            )).one_or_none()
            if search_result is None:
                raise db.exceptions.NotFound

        return JSONResponse(
            search_result.as_dict(),
            status_code=200
        )
    except db.exceptions.NotFound as e:
        return parser.form_error(e, "ID not found", 404)
    except Exception as e:
        return parser.form_error(e)


@router.get("/all/stores")
async def get_all_stores_ids(
        _ = D(TVF(*cfg.TOKENIZER.ADMIN_LIST))
):
    try:
        async with db.session_link() as session:
            list_ = (await session.scalars(
                db.select(db.Store.ID)
            )).all()
        try:
            list_.remove("auction_transfer_route")
        except:
            pass
        try:
            list_.remove("auction_lottery_route")
        except:
            pass

        return JSONResponse(
            {"ids": list_},
            status_code=200
        )
    except Exception as e:
        return parser.form_error(e)


@router.get("/all/shopkeepers")
async def get_all_shopkeepers(
        _ = D(TVF(*cfg.TOKENIZER.ADMIN_LIST))
):
    try:
        async with db.session_link() as session:
            return JSONResponse(
                {
                    "ids": (await session.scalars(
                        db.select(db.Shopkeeper.userID)
                    )).all()
                },
                status_code=200
            )
    except Exception as e:
        return parser.form_error(e)


@router.get("/link")
async def check_link(
        link: str = None,
        _ = D(TVF(*cfg.TOKENIZER.ADMIN_LIST))
):
    if link is None:
        return parser.form_error_bad_parsing()

    try:
        async with db.session_link() as session:
            search_result = await session.get(db.StoreFormLink, link)
            if search_result is None:
                raise db.exceptions.NotFound

        return JSONResponse(
            {"email": search_result.email},
            status_code=200
        )
    except db.exceptions.NotFound as e:
        return parser.form_error(e, "link email not found", 404)
    except Exception as e:
        return parser.form_error(e)
