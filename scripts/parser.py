from fastapi.responses import JSONResponse
from traceback import format_exc

from scripts.j2 import fromfile_async as j2_fromfile
from data.config import PATHS


def get_full_name(obj: Exception) -> str:
    """
    Возвращает полное название объекта, включая все родительские классы и портранства имён

    :param obj: объект
    """

    module = obj.__class__.__module__
    if module is None or module == str.__class__.__module__:
        return obj.__class__.__name__
    return module + '.' + obj.__class__.__name__


async def get_setting(key: str):
    """
    Возвращает значение из файла настроек лаунчера
    :param key: ключ
    :return: значение, если ключ существует, иначе -- None
    """

    try:
        return (await j2_fromfile(PATHS.LAUNCH_SETTINGS))[key]
    except KeyError:
        return None


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


def form_error_flag_blocked() -> JSONResponse:
    """
    Формирует респонс с ошибкой 403: launcher flag blocked
    :return: JSONResponse
    """

    return JSONResponse({'error': "ConnectionRefusedError", 'message': "launcher flag blocked"}, status_code=403)
