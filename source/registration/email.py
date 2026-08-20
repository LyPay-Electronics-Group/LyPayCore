from fastapi import APIRouter, Depends as D
from fastapi.responses import JSONResponse

from jwt import decode as jwt_decode

from scripts import parser, mailer
from scripts.token_validator import token_validate_factory as TVF
from scripts.unix import unix
from scripts.idgen import IDGenerator
from data.config import VERSION, BUILD, NAME, JWT_KEY, EMAIL, TOKENIZER
import database as db


router = APIRouter()
idgen = IDGenerator()


@router.get("/send")
async def send(
        email: str = None,
        route: str = None,
        code:  str = None,
        keys:  str = None,
        _ = D(TVF(*TOKENIZER.ADMIN_LIST))
):
    if any(t is None for t in (email, route)) or route not in ('main', 'guest', 'shopkeeper'):
        return parser.form_error_bad_parsing()

    email = email.lower()

    try:
        async with db.session_link() as session:
            async with session.begin():
                if route == 'main':
                    if code is None:
                        code = idgen.generate_code_default(EMAIL.ACCESS_CODE_LENGTH)
                    if keys is None:
                        keys = {
                            "VERSION": VERSION,
                            "BUILD": BUILD,
                            "NAME": f' ({NAME})' if NAME != '' else ''
                        }
                    else:
                        keys = jwt_decode(keys, JWT_KEY, ["HS256"])
                    keys["CODE"] = code

                    await mailer.send_async(path=EMAIL.PATHS.MAIN, recipient=email,
                                            subject=EMAIL.SUBJECTS.MAIN, keys=keys,
                                            files=None)     # [EMAIL.PATHS.USER_MANUAL]

                    entry_to_delete = (await session.execute(
                        db.select(db.AccessCodesMain).where(db.AccessCodesMain.email == email).with_for_update()
                    )).scalar_one_or_none()
                    if entry_to_delete is not None:
                        session.delete(entry_to_delete)

                    session.add(
                        db.AccessCodesMain(
                            email=email,
                            code=code,
                        )
                    )

                elif route == 'guest':
                    if code is None:
                        code = idgen.generate_code_default(EMAIL.ACCESS_CODE_LENGTH)
                    if keys is None:
                        keys = {
                            "VERSION": VERSION,
                            "BUILD": BUILD,
                            "NAME": f' ({NAME})' if NAME != '' else '',
                            "UX": unix()
                        }
                    else:
                        keys = jwt_decode(keys, JWT_KEY, ["HS256"])
                    keys["CODE"] = code

                    await mailer.send_async(path=EMAIL.PATHS.GUEST, recipient=email,
                                            subject=EMAIL.SUBJECTS.GUEST, keys=keys,
                                            files=None)     # [EMAIL.PATHS.USER_MANUAL]

                    entry_to_delete = (await session.execute(
                        db.select(db.AccessCodesGuest).where(db.AccessCodesGuest.email == email).with_for_update()
                    )).scalar_one_or_none()
                    if entry_to_delete is not None:
                        session.delete(entry_to_delete)

                    session.add(
                        db.AccessCodesGuest(
                            email=email,
                            code=code,
                        )
                    )

                else:  # shopkeeper
                    if code is None:
                        code = idgen.generate_code_default(EMAIL.ACCESS_CODE_LENGTH)
                    if keys is None:
                        keys = {
                            "VERSION": VERSION,
                            "BUILD": BUILD,
                            "NAME": f' ({NAME})' if NAME != '' else ''
                        }
                    else:
                        keys = jwt_decode(keys, JWT_KEY, ["HS256"])
                    keys["CODE"] = code

                    await mailer.send_async(path=EMAIL.PATHS.STORE, recipient=email,
                                            subject=EMAIL.SUBJECTS.SHOPKEEPER, keys=keys,
                                            files=None)     # [EMAIL.PATHS.STORE_MANUAL]

                    session.add(
                        db.StoreFormLink(
                            email=email,
                            code=code,
                        )
                    )

        return JSONResponse(
            {'ok': True},
            status_code=200
        )
    except Exception as e:
        return parser.form_error(e)


@router.get("/corp_record")
async def check_corporation_record(
        email: str = None,
        _ = D(TVF(*TOKENIZER.ADMIN_LIST))
):
    if email is None:
        return parser.form_error_bad_parsing()

    try:
        async with db.session_link() as session:
            result = await session.get(db.CorporationEntry, email.lower())
            if result is None:
                raise db.exceptions.NotFound

        result = result.to_dict()
        result["group"] = result.pop("category")

        return JSONResponse(
            result,
            status_code=200
        )
    except db.exceptions.NotFound as e:
        return parser.form_error(e, "email not found", 404)
    except Exception as e:
        return parser.form_error(e)
