from .tables import *
from .base import AsyncDatabase
from . import exceptions

from sqlalchemy import select, text, func, or_
from sqlalchemy.ext.asyncio import async_sessionmaker


database_link = None
__session_maker = None
pool_pre_ping = True


def disable_pre_ping():
    global pool_pre_ping
    pool_pre_ping = False


def session_link():
    global __session_maker, database_link

    if database_link is None:
        database_link = AsyncDatabase(pool_pre_ping)
    if __session_maker is None:
        __session_maker = async_sessionmaker(database_link.get_engine(), expire_on_commit=False)

    return __session_maker()


__all__ = (
    'database_link',
    'session_link',
    'AsyncDatabase',
    'disable_pre_ping',
    'exceptions',
    'select', 'text', 'func', 'or_',
)
