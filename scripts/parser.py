from fastapi.responses import JSONResponse


def get_full_name(obj: Exception):
    """
    Возвращает полное название объекта, включая все родительские классы и портранства имён

    :param obj: объект
    """

    module = obj.__class__.__module__
    if module is None or module == str.__class__.__module__:
        return obj.__class__.__name__
    return module + '.' + obj.__class__.__name__


def form_error(error: Exception) -> JSONResponse:
    """
    Формирует респонс с ошибкой 5xx

    :param error: объект ошибки
    :return: JSONResponse
    """
    return JSONResponse({'error': get_full_name(error), "message": error.__str__()}, status_code=500)


def form_error_bad_parsing() -> JSONResponse:
    """
    Формирует респонс с ошибкой 400: bad parsing
    :return: JSONResponse
    """
    return JSONResponse({'error': "ValueError", 'message': "bad parsing"}, status_code=400)
