from .tables import *
from .base import AsyncDatabase
from . import exceptions

from sqlalchemy import select, text, func, or_
from sqlalchemy.ext.asyncio import async_sessionmaker

database_link = AsyncDatabase()
session_link = async_sessionmaker(database_link.get_engine(), expire_on_commit=False)
