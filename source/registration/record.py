from fastapi import APIRouter, Depends as D
from fastapi.responses import JSONResponse

from os.path import exists

from scripts import parser, memory, censor
from scripts.token_validator import token_validate_factory as TVF
from scripts.idgen import IDGenerator
from scripts.unix import unix
from data.config import PATHS, TOKENIZER
import database as db


router = APIRouter()
idgen = IDGenerator()


@router.get("/user")
async def new_user(
        name:       str = None,
        login:      str = None,
        password:   str = None,
        group:      str = None,
        email:      str = None,
        tag:        str = None,
        owner_flag: str = None,
        _ = D(TVF(*TOKENIZER.ADMIN_LIST))
):
    if any(t is None for t in (name, login, password, group, email, owner_flag)) \
            or owner_flag not in ('tg_owner', 'tg_guest',
                                  'web_owner', 'web_guest',
                                  'integration'):
        return parser.form_error_bad_parsing()
    if not censor.check_user_name(name):
        return parser.form_error(AttributeError(), "bad censor flag: user name", 406)
    if not censor.check_login(login):
        return parser.form_error(AttributeError(), "bad censor flag: login", 406)
    if not await parser.get_setting("user_can_register"):
        return parser.form_error_flag_blocked()

    try:
        async with db.session_link() as session:
            if (await session.execute(
                db.select(db.User).where(db.User.login == login)
            )).scalar_one_or_none() is not None:
                raise NameError

            async with session.begin():
                if owner_flag[-5:] == 'owner':
                    link_entry = (await session.execute(
                        db.select(db.AccessCodesMain).where(db.AccessCodesMain.email == email.lower()).with_for_update()
                    )).scalar_one_or_none()
                    if link_entry is not None:
                        session.delete(link_entry)
                else:  # guest
                    link_entry = (await session.execute(
                        db.select(db.AccessCodesGuest).where(db.AccessCodesGuest.email == email.lower()).with_for_update()
                    )).scalar_one_or_none()
                    if link_entry is not None:
                        session.delete(link_entry)

                ID = await idgen.userID(session)

                session.add(db.User(
                    ID=ID,
                    name=name,
                    login=login,
                    password=password,
                    category=group,
                    email=email,
                    tag=tag,
                    balance=0,
                    owner=owner_flag,
                    last_online=unix(),
                    avatar=False
                ))

        if not exists(PATHS.QR + f"{ID}.png"):
            memory.qr(ID)
        return JSONResponse(
            {'ID': ID},
            status_code=201
        )
    except NameError as e:
        return parser.form_error(e, "login already exists", 406)
    except Exception as e:
        return parser.form_error(e)


@router.get("/store")
async def new_store(
        name:        str = None,
        storeID:     str = None,
        hostID:      int = None,
        link:        str = None,
        description: str = None,
        _ = D(TVF(*TOKENIZER.ADMIN_LIST))
):
    if any(t is None for t in (name, storeID, hostID, link)):
        return parser.form_error_bad_parsing()
    if not await parser.get_setting("store_can_register"):
        return parser.form_error_flag_blocked()

    if description is None:
        description = ""

    if not censor.check_store_name(name):
        return parser.form_error(AttributeError(), "bad censor flag: store name", 406)
    if not censor.check_store_description(description):
        return parser.form_error(AttributeError(), "bad censor flag: store desc", 406)

    try:
        async with db.session_link() as session:
            async with session.begin():
                link_entry = (await session.execute(
                    db.select(db.StoreFormLink).where(db.StoreFormLink.code == link).with_for_update()
                )).scalar_one_or_none()

                session.add(db.Store(
                    ID=storeID,
                    name=name,
                    hostID=hostID,
                    description=description,
                    avatar=False,
                    balance=0,
                    hostEmail=link_entry.email,
                    auctionID=None,
                    placeID=None
                ))

                session.delete(link_entry)

                session.add(db.Shopkeeper(
                    userID=hostID,
                    storeID=storeID
                ))
                session.add(db.FirewallStoresEntry(
                    ID=hostID,
                    unix=unix(),
                    access=True,
                    comment="added via automatic register code"
                ))
        return JSONResponse(
            {'ok': True},
            status_code=201
        )
    except Exception as e:
        return parser.form_error(e)


@router.get("/store_id")
async def get_available_store_id(
        _ = D(TVF(*TOKENIZER.ADMIN_LIST))
):
    try:
        async with db.session_link() as session:
            return JSONResponse(
                {"ID": await idgen.storeID(session)},
                status_code=201
            )
    except Exception as e:
        return parser.form_error(e)
