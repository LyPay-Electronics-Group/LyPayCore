from random import choice as r_choice, randint as r_rand

alphabet = tuple("0123456789abcdefghijklmnopqrstuvwxyz")


def generate_code(length: int) -> str:
    """
    Создаёт цифро-буквенный код, состоящий из символов ``0-9`` и ``a-z``

    :param length: необходимая длина кода
    :return: код (строка)
    """

    return ''.join(r_choice(alphabet) for _ in range(length))


def generate_ID(upper: int = 1e9) -> int:
    """
    Создаёт числовой код

    :param upper: верхний предел генерации: [1, max]
    :return: код (число)
    """

    return r_rand(1, upper)
