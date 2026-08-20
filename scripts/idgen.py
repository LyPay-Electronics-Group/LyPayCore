from random import choice as r_choice, randint as r_rand
from asyncio import sleep

from datetime import datetime

from data.config import IDGEN
import database as db
from sqlalchemy.ext.asyncio import AsyncSession


class IDGenerator:
    def __init__(self) -> None:
        """
        Класс генератора ID
        """

        self.alphabet = tuple("0123456789abcdefghijklmnopqrstuvwxyz")
        self.store_id_alphabet = tuple("0123456789abcdef")

    @staticmethod
    def generate_code(length: int, alphabet: tuple[str]) -> str:
        """
        Создаёт цифро-буквенный код

        :param length: необходимая длина кода
        :param alphabet: алфавит кода
        :return: код (строка)
        """

        return ''.join(r_choice(alphabet) for _ in range(length))

    def generate_code_default(self, length: int) -> str:
        """
        Создаёт цифро-буквенный код, остоящий из символов ``0-9`` и ``a-z``

        :param length: необходимая длина кода
        :return: код (строка)
        """

        return self.generate_code(length, self.alphabet)

    @staticmethod
    def generate_id(length: int) -> str:
        """
        Создаёт числовой ID

        :param length: необходимая длина ID
        :return: ID (строка)
        """

        return str(r_rand(1, 10 ** length)).zfill(length)


    async def userID(self, session: AsyncSession) -> int:
        """
        Создаёт уникальный userID (с проверкой корректности)

        :param session: сессия подключения к БД
        :return: код
        """

        u = int(IDGEN.USER_ID.format(
            _=self.generate_id(IDGEN.USER_ID_LENGTH - 1),
            year=datetime.now().year % 10
        ))
        while (await session.get(db.User, u)) is not None:
            await sleep(IDGEN.TIMEOUT)
            u = int(IDGEN.USER_ID.format(
                _=self.generate_id(IDGEN.USER_ID_LENGTH - 1),
                year=datetime.now().year % 10
            ))
        return u

    async def storeID(self, session: AsyncSession) -> str:
        """
        Создаёт уникальный storeID (с проверкой корректности)

        :param session: сессия подключения к БД
        :return: код
        """

        s = IDGEN.STORE_ID.format(
            _=self.generate_code(IDGEN.STORE_ID_LENGTH, self.store_id_alphabet)
        )
        while (await session.get(db.Store, s)) is not None:
            await sleep(IDGEN.TIMEOUT)
            s = IDGEN.STORE_ID.format(
                _=self.generate_code(IDGEN.STORE_ID_LENGTH, self.store_id_alphabet)
            )
        return s

    async def itemID(self, storeID: str, session: AsyncSession) -> str:
        """
        Создаёт уникальный itemID (с проверкой корректности)

        :param session: сессия подключения к БД
        :param storeID: ID магазина
        :return: код
        """

        i = IDGEN.ITEM_ID.format(
            storeID=storeID,
            _=self.generate_code(IDGEN.ITEM_ID_LENGTH, self.alphabet)
        )
        while (await session.get(db.Item, i)) is not None:
            await sleep(IDGEN.TIMEOUT)
            i = IDGEN.ITEM_ID.format(
                storeID=storeID,
                _=self.generate_code(IDGEN.ITEM_ID_LENGTH, self.alphabet)
            )
        return i

    async def chequeID(self, storeID: str, session: AsyncSession) -> str:
        """
        Создаёт уникальный chequeID (с проверкой корректности)

        :param session: сессия подключения к БД
        :param storeID: ID магазина
        :return: код
        """

        c = IDGEN.CHEQUE_ID.format(
            storeID=storeID,
            _=self.generate_code(IDGEN.CHEQUE_ID_LENGTH, self.alphabet)
        )
        while (await session.get(db.Cheque, c)) is not None:
            await sleep(IDGEN.TIMEOUT)
            c = IDGEN.CHEQUE_ID.format(
                storeID=storeID,
                _=self.generate_code(IDGEN.CHEQUE_ID_LENGTH, self.alphabet)
            )
        return c

    @staticmethod
    async def lotID(session: AsyncSession) -> int:
        """
        Создаёт уникальный lotID (с проверкой корректности)

        :param session: сессия подключения к БД
        :return: код
        """

        max_lotID = await session.scalar(
            db.select(db.func.max(db.Lot.lotID))
        )
        return max_lotID + 1 if max_lotID is not None else 1

    async def fpsID(self, session: AsyncSession) -> str:
        """
        Создаёт уникальный fpsID (с проверкой корректности)

        :param session: сессия подключения к БД
        :return: код
        """

        f = IDGEN.FPS_ID.format(
            _=self.generate_code(IDGEN.FPS_ID_LENGTH, self.alphabet)
        )
        while (await session.get(db.FPS, f)) is not None:
            await sleep(IDGEN.TIMEOUT)
            f = IDGEN.FPS_ID.format(
                _=self.generate_code(IDGEN.FPS_ID_LENGTH, self.store_id_alphabet)
            )
        return f
