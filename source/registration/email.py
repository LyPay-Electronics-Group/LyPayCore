from fastapi import APIRouter
from fastapi.responses import JSONResponse

from jwt import decode as jwt_decode

from scripts import parser, lpsql, mailer
from scripts.unix import unix
from scripts.idgen import IDGenerator
from data.config import PATHS, VERSION, BUILD, NAME, JWT_KEY, EMAIL


router = APIRouter()
db = lpsql.DataBase(PATHS.DATA + "lypay_database.db", lpsql.Tables.MAIN)
idgen = IDGenerator(db)


@router.get("/send")
async def send(email: str = None, route: str = None, code: str = None, keys: str = None):
    if any(t is None for t in (email, route, code)) or route not in ('main', 'guest', 'store'):
        return parser.form_error_bad_parsing()

    try:
        if route == 'main':
            if keys is None:
                keys = {
                    "VERSION": VERSION,
                    "BUILD": BUILD,
                    "NAME": f' ({NAME})' if NAME != '' else ''
                }
            else:
                keys = jwt_decode(keys, JWT_KEY, algorithm="HS256")
            keys["CODE"] = code
            await mailer.send_async(path=EMAIL.PATHS.MAIN, recipient=email,
                                    subject=EMAIL.SUBJECTS.MAIN, keys=keys,
                                    files=[EMAIL.PATHS.USER_MANUAL])

        elif route == 'guest':
            if keys is None:
                keys = {
                    "VERSION": VERSION,
                    "BUILD": BUILD,
                    "NAME": f' ({NAME})' if NAME != '' else '',
                    "UX": unix()
                }
            else:
                keys = jwt_decode(keys, JWT_KEY, algorithm="HS256")
            keys["CODE"] = code
            await mailer.send_async(path=EMAIL.PATHS.GUEST, recipient=email,
                                    subject=EMAIL.SUBJECTS.GUEST, keys=keys,
                                    files=[EMAIL.PATHS.USER_MANUAL])
        else:  # shopkeeper
            link = idgen.generate_code(16)
            if keys is None:
                keys = {
                    "VERSION": VERSION,
                    "BUILD": BUILD,
                    "NAME": f' ({NAME})' if NAME != '' else ''
                }
            else:
                keys = jwt_decode(keys, JWT_KEY, algorithm="HS256")
            keys["CODE"] = link
            await mailer.send_async(path=EMAIL.PATHS.STORE, recipient=email,
                                    subject=EMAIL.SUBJECTS.SHOPKEEPER, keys=keys,
                                    files=[EMAIL.PATHS.STORE_MANUAL])
            db.insert(
                "store_form_link",
                [
                    link,
                    email
                ]
            )
        return JSONResponse(
            {'ok': True},
            status_code=200
        )
    except Exception as e:
        return parser.form_error(e)


@router.get("/corp_record")
async def check_corporation_record(email: str = None):
    if email is None:
        return parser.form_error_bad_parsing()

    try:
        result = db.search("corporation", "email", email)
        if result is None:
            raise lpsql.exceptions.EmailNotFound
        return JSONResponse(
            result,
            status_code=200
        )
    except lpsql.exceptions.EmailNotFound as e:
        return parser.form_error(e, "email not found", 404)
    except Exception as e:
        return parser.form_error(e)
