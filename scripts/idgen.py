from random import choice as r_choice, randint as r_rand
from asyncio import sleep

from data.config import IDGEN
from scripts.lpsql import DataBase


class IDGenerator:
    def __init__(self, database: DataBase) -> None:
        """
        Класс генератора ID

        :param database: экземпляр базы данных (для проверок)
        """
        self.db = database

        self.alphabet = tuple("0123456789abcdefghijklmnopqrstuvwxyz")

    def generate_code(self, length: int) -> str:
        """
        Создаёт цифро-буквенный код, состоящий из символов ``0-9`` и ``a-z``

        :param length: необходимая длина кода
        :return: код (строка)
        """

        return ''.join(r_choice(self.alphabet) for _ in range(length))

    @staticmethod
    def generate_id(length: int) -> int:
        """
        Создаёт числовой ID

        :param length: необходимая длина ID
        :return: ID (число)
        """

        return r_rand(1, 10 ** length)


    async def userID(self) -> str:
        """
        Создаёт уникальный userID (с проверкой корректности)

        :return: код
        """

        u = IDGEN.USER_ID.format(
            _=self.generate_id(IDGEN.USER_ID_LENGTH)
        )
        while u in self.db.searchall("users", "ID"):
            await sleep(IDGEN.TIMEOUT)
            u = IDGEN.USER_ID.format(
                _=self.generate_id(IDGEN.USER_ID_LENGTH)
            )
        return u

    async def storeID(self) -> str:
        """
        Создаёт уникальный storeID (с проверкой корректности)

        :return: код
        """

        s = IDGEN.STORE_ID.format(
            _=self.generate_code(IDGEN.STORE_ID_LENGTH)
        )
        while s in self.db.searchall("stores", "ID"):
            await sleep(IDGEN.TIMEOUT)
            s = IDGEN.STORE_ID.format(
                _=self.generate_code(IDGEN.STORE_ID_LENGTH)
            )
        return s

    async def itemID(self, storeID: str) -> str:
        """
        Создаёт уникальный itemID (с проверкой корректности)

        :param storeID: ID магазина
        :return: код
        """

        i = IDGEN.ITEM_ID.format(
            storeID=storeID,
            _=self.generate_code(IDGEN.ITEM_ID_LENGTH)
        )
        while i in self.db.searchall("items", "itemID"):
            await sleep(IDGEN.TIMEOUT)
            i = IDGEN.ITEM_ID.format(
                storeID=storeID,
                _=self.generate_code(IDGEN.ITEM_ID_LENGTH)
            )
        return i

    async def chequeID(self, storeID: str) -> str:
        """
        Создаёт уникальный chequeID (с проверкой корректности)

        :param storeID: ID магазина
        :return: код
        """

        c = IDGEN.CHEQUE_ID.format(
            storeID=storeID,
            _=self.generate_code(IDGEN.CHEQUE_ID_LENGTH)
        )
        while c in self.db.searchall("cheques", "chequeID"):
            await sleep(IDGEN.TIMEOUT)
            c = IDGEN.CHEQUE_ID.format(
                storeID=storeID,
                _=self.generate_code(IDGEN.CHEQUE_ID_LENGTH)
            )
        return c
