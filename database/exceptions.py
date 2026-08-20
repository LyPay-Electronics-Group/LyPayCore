import inspect


class BaseDriverException(Exception):
    def __init__(self):
        """
        Класс ошибки драйвера базы данных
        """

        frame = inspect.currentframe().f_back
        if hasattr(frame.f_code, 'co_qualname'):
            self.method = frame.f_code.co_qualname
        else:
            self.method = frame.f_code.co_name

    def form_str_message(self, custom_message: str = '–') -> str:
        return f"""\
    Получено исключение при вызове {self.method}. \
    Сообщение: {custom_message}\
    """


class NotFound(BaseDriverException):
    def __str__(self):
        super().form_str_message("запрашиваемый объект не найден")


class ValueLoE0(BaseDriverException):
    def __str__(self):
        super().form_str_message("недопустимое неположительное значение аргумента")


class NotEnoughBalance(BaseDriverException):
    def __str__(self):
        super().form_str_message("недостаточно Тугриков на счёте")


__all__ = (
    'NotFound',
    'ValueLoE0',
    'NotEnoughBalance'
)
