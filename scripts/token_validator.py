from fastapi import HTTPException, Request


def token_validate_factory(*tokens: str):
    """
    Функция, создающая экземпляр функции проверки доступа токенов к роутеру
    :param tokens: разрешённые токены в этом роутере
    """

    def token_filter(request: Request) -> None:
        """
        Не допускает исполнения кода роутера, если токен не проходит проверку
        :param request: ссылка на оригинальный реквест
        """

        token = getattr(request.state, "token", None)
        if token is None:
            raise HTTPException(403)
        if token not in tokens:
            raise HTTPException(403)


    return token_filter
