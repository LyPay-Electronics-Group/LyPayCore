from sqlalchemy.ext.asyncio import create_async_engine
from os import getenv


class AsyncDatabase:
    def __init__(self):
        self.engine = create_async_engine(
            "postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}".format(
                user=getenv("LYPAY_DB_USER"),
                password=getenv("LYPAY_DB_PASSWORD"),
                host=getenv("LYPAY_DB_HOST", "localhost"),
                port=getenv("LYPAY_DB_PORT", 5432),
                database=getenv("LYPAY_DB_NAME")
            ),
            pool_pre_ping=True, echo=False
        )

    def get_engine(self):
        return self.engine
