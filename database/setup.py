from asyncio import run
from sqlalchemy.ext.asyncio import create_async_engine
from tables import Base
from tables import *


user = ''
password = ''
db = ''

async def main():
    engine = create_async_engine(f"postgresql+asyncpg://{user}:{password}@localhost/{db}")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    await engine.dispose()


if __name__ == "__main__":
    run(main())

"""
сброс всех таблиц и создание пустых шаблонов
для загрузки дампа в готовый шаблон: pg_restore -U <user> -d <db> -a -1 <path/to/dump>
"""
