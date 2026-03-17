from fastapi import APIRouter
from fastapi.responses import JSONResponse

from os.path import exists
from dotenv import load_dotenv

from scripts import parser, memory, lpsql, censor
from scripts.idgen import IDGenerator
from scripts.unix import unix
from data.config import PATHS


router = APIRouter()
db = lpsql.DataBase(PATHS.DATA + "lypay_database.db", lpsql.Tables.MAIN)
idgen = IDGenerator(db)
firewall4 = lpsql.DataBase(PATHS.DATA + "lypay_firewall.db", lpsql.Tables.FIREWALL)
load_dotenv()


@router.get("/user")
async def new_user(name: str = None, login: str = None, password: str = None, group: str = None, email: str = None, tag: str = None, owner_flag: str = None):
    if any(t is None for t in (name, login, password, group, email, owner_flag)) \
            or owner_flag not in ('tg_owner', 'tg_guest',
                                  'web_owner', 'web_guest',
                                  'integration'):
        return parser.form_error_bad_parsing()
    if not censor.check_user_name(name):
        return parser.form_error(AttributeError(), "bad censor flag: user name", 406)
    if not censor.check_login(login):
        return parser.form_error(AttributeError(), "bad censor flag: login", 406)

    try:
        ID = await idgen.userID()

        db.insert(
            "users",
            [
                ID,         # ID
                name,       # name
                login,      # login
                password,   # password
                group,      # class
                email,      # email
                tag,        # tag
                0,          # balance
                owner_flag, # owner :  '[tg/web]_owner' | '[tg/web]_guest' | 'integration'
                unix()      # last_online
            ]
        )
        if not exists(PATHS.QR + f"{ID}.png"):
            memory.qr(ID)
        return JSONResponse(
            {'ID': ID},
            status_code=201
        )
    except Exception as e:
        return parser.form_error(e)


@router.get("/store")
async def new_store(name: str = None, storeID: str = None, hostID: int = None, email: str = None, description: str = None, link: str = None):
    if any(t is None for t in (name, storeID, hostID, email, link)):
        return parser.form_error_bad_parsing()
    if description is None:
        description = ""

    if not censor.check_store_name(name):
        return parser.form_error(AttributeError(), "bad censor flag: store name", 406)
    if not censor.check_store_description(description):
        return parser.form_error(AttributeError(), "bad censor flag: desc", 406)

    try:
        db.insert(
            "stores",
            [
                storeID,        # ID
                name,           # name
                hostID,         # hostID
                description,    # description
                False,          # logo
                0,              # balance
                email,          # hostEmail
                None,           # auctionID
                None,           # placeID
            ]
        )
        db.insert(
            "shopkeepers",
            [
                hostID,  # userID
                storeID  # storeID
            ]
        )
        db.manual(f"DELETE * FROM store_form_link WHERE link={link}")
        firewall4.insert(
            "stores",
            [
                hostID,                              # ID
                unix(),                              # unix
                True,                                # access
                "added via automatic register code"  # comment
            ]
        )
    except Exception as e:
        return parser.form_error(e)
