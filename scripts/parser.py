from fastapi.responses import JSONResponse
from traceback import format_exc

from data.config import PATHS
from scripts.lpsql import DataBase, Tables

firewall4 = DataBase(PATHS.DATA + "lypay_firewall.db", Tables.FIREWALL)


def get_full_name(obj: Exception) -> str:
    """
    Возвращает полное название объекта, включая все родительские классы и портранства имён

    :param obj: объект
    """

    module = obj.__class__.__module__
    if module is None or module == str.__class__.__module__:
        return obj.__class__.__name__
    return module + '.' + obj.__class__.__name__


def form_error(error: Exception, message: str | None = None, status_code: int = 500) -> JSONResponse:
    """
    Формирует респонс с ошибкой 5xx

    :param error: объект ошибки
    :param message: текст для отображения
    :param status_code: http код ошибки
    :return: JSONResponse
    """

    if message is None:
        print("got an error during handling an event call:", format_exc(), sep='\n')
    return JSONResponse(
        {
            'error': get_full_name(error),
            'message': error.__str__() if message is None else message
        },
        status_code=status_code
    )


def form_error_bad_parsing() -> JSONResponse:
    """
    Формирует респонс с ошибкой 400: bad parsing
    :return: JSONResponse
    """

    return JSONResponse({'error': "ValueError", 'message': "bad parsing"}, status_code=400)


def form_error_bad_firewall_check() -> JSONResponse:
    """
    Формирует респонс с ошибкой 403: bad fw check
    :return: JSONResponse
    """

    return JSONResponse({'error': "ConnectionRefusedError", 'message': "bad fw check"}, status_code=403)


async def check_firewall(ID: int | str, fw: str) -> bool:
    """
    Проверяет, есть ли нужный ID в файерволле
    :param ID: ID для проверки
    :param fw: раздел файерволла (``main``, ``stores``, ``admins``)
    :return: True, если введённому ID предоставлен доступ, и False в обратном случае
    """

    if fw not in ('main', 'stores', 'admins'):
        raise AttributeError("введённый параметр fw не соответствует ожидаемому")

    return firewall4.search(fw, "ID", ID) is not None
