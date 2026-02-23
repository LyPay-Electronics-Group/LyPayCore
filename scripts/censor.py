from data.config import CENSOR


def censor(field: str) -> bool:
    """
    Проверяет, есть ли в строке символы, которые потенциально могут вызвать непредвиденное поведение ядра:
    '<', '>', '&' (не в составе специальных последовательностей "&amp;", "&lt;", "&gt;"

    :param field: поле для строки
    :return: True, если строка прошла проверку, False -- в обратном случае
    """

    for index in range(len(field)):
        char = field[index]
        if char == '<' or char == '>':
            return False
        if char == '&' and field[index:index+3] not in ('&lt;', '&gt;') and field[index:index+4] != '&amp;':
            return False

    return True


def check_user_name(name: str) -> bool:
    """
    Проверяет введённое пользователем имя. Имя может состоять из следующих символов:
    ``А-Я``, ``а-я``, ``-``, ``–``, ``[пробел]`` (актуальный список прописан в конфигурационном файле).
    Максимум 3 слова (разделённых пробелами последовательности символов)

    :param name: имя
    :return: True, если имя прошло проверку, False -- в обратном случае
    """

    for char in name:
        if char not in CENSOR.CORRECT_NAME_LITERALS:
            return False

    if name.count(' ') >= 3:
        return False

    return True


def check_login(login: str) -> bool:
    """
    Проверяет введённый пользователем логин. Логин может состоять из следующих символов:
    ``A-Z``, ``a-z``, ``0-9``, ``-``, ``.``, ``_`` (актуальный список прописан в конфигурационном файле)

    :param login: логин
    :return: True, если логин прошёл проверку, False -- в обратном случае
    """

    for char in login:
        if char not in CENSOR.CORRECT_LOGIN_LITERALS:
            return False

    return True


def check_store_name(name: str) -> bool:
    """
    Проверяет введённое название магазина. Название может состоять из любых неблокирующих символов
    (список блокирующих символов прописан в докстринге функции censor).

    :param name: название
    :return: True, если название прошло проверку, False -- в обратном случае
    """

    if not censor(name):
        return False

    if len(name) > CENSOR.STORE_NAME_LENGTH:
        return False

    return True


def check_store_description(description: str) -> bool:
    """
    Проверяет введённое описание магазина. Описание может состоять из любых неблокирующих символов
    (список блокирующих символов прописан в докстринге функции censor).

    :param description: описание
    :return: True, если описание прошло проверку, False -- в обратном случае
    """

    if not censor(description):
        return False

    if len(description) > CENSOR.STORE_DESCRIPTION_LENGTH:
        return False

    return True
