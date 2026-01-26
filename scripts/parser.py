def get_full_name(obj: Exception):
    """
    Возвращает полное название объекта, включая все родительские классы и портранства имён

    :param obj: объект
    """

    module = obj.__class__.__module__
    if module is None or module == str.__class__.__module__:
        return obj.__class__.__name__
    return module + '.' + obj.__class__.__name__
