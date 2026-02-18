from fastapi import APIRouter
from fastapi.responses import JSONResponse

from os.path import exists
from dotenv import load_dotenv
from random import randint

from scripts import parser, memory, lpsql
from scripts.unix import unix
from data.config import PATHS


router = APIRouter()
db = lpsql.DataBase(PATHS.DATA + "lypay_database.db", lpsql.Tables.MAIN)
firewall3 = lpsql.DataBase(PATHS.DATA + "lypay_firewall.db", lpsql.Tables.FIREWALL)
load_dotenv()


def generate_new_user_ID():
    return randint(1, int(1e9))


@router.get("/user")
async def new_user(name: str = None, login: str = None, password: str = None, group: str = None, email: str = None, tag: str = None, owner_flag: str = None):
    if any(t is None for t in (name, group, email, owner_flag)) or owner_flag not in ('tg_owner', 'tg_guest',
                                                                                      'web_owner', 'web_guest',
                                                                                      'integration'):
        return parser.form_error_bad_parsing()

    try:
        ID = generate_new_user_ID()
        while ID in db.searchall("users", "ID"):
            ID = generate_new_user_ID()

        db.insert("users",
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
                  ])
        if not exists(PATHS.QR + f"{ID}.png"):
            memory.qr(ID)
        return JSONResponse(
            {'ID': ID},
            status_code=201
        )
    except Exception as e:
        return parser.form_error(e)


@router.get("/store")
async def new_store(name: str = None, storeID: str = None, hostID: int = None, email: str = None, description: str = None):
    if any(t is None for t in (name, storeID, hostID, email)):
        return parser.form_error_bad_parsing()

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
        # TODO: удалить из store_form_link
        firewall3.insert(
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
