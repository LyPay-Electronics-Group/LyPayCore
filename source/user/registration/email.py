from fastapi import APIRouter
from fastapi.responses import JSONResponse

from scripts import parser, lpsql, mailer
from scripts.unix import unix
from data.config import PATHS, VERSION, BUILD, NAME


router = APIRouter()
db = lpsql.DataBase(PATHS.DATA + "lypay_database.db", lpsql.Tables.MAIN)


@router.get("/send")
async def send(email: str = None, route: str = None, code: str = None):
    if any(t is None for t in (email, route, code)) or route not in ('main', 'guest'):
        return parser.form_error_bad_parsing()

    try:
        if route == 'main':
            await mailer.send_async(path=PATHS.EMAIL + "main.html", participant=email,
                                    subject="Регистрация в LyPay", keys={
                    "VERSION": VERSION,
                    "BUILD": BUILD,
                    "NAME": f' ({NAME})' if NAME != '' else '',
                    "CODE": code
                })
        else:
            await mailer.send_async(path=PATHS.EMAIL + "guest.html", participant=email,
                                    subject="Регистрация в LyPay: Гостевой доступ", keys={
                    "VERSION": VERSION,
                    "BUILD": BUILD,
                    "NAME": f' ({NAME})' if NAME != '' else '',
                    "CODE": code,
                    "UX": unix()
                })
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
