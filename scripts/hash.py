from os import getenv
from dotenv import load_dotenv

from hmac import new as hmac
from hashlib import sha256

load_dotenv()


def code(data: str) -> str:
    """
    Функция хэширования строки с ключом
    :param data: исходная строка
    :return: хэш-код
    """

    data = data.encode("utf8")
    key = getenv("LYPAY_HASH_KEY").encode("utf8")

    return hmac(key, data, sha256).hexdigest()
