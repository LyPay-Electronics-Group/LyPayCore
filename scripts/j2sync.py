from json import dumps, loads


def to_(obj: dict[str, ...], *, tab: int = 4, separators: tuple[str, str] = (', ', ': '), string_mode: bool = False) -> str:
    """
    Return string in JSON format

    :param obj: dictionary object with only string-keys
    :param tab: amount of spaces in a tab char
    :param separators: separators for a return string
    :param string_mode: if true, returns a string without new lines
    :return: json-like string from input dictionary
    """

    if string_mode:
        return dumps(obj, separators=(',', ':'), ensure_ascii=False)
    return dumps(obj, indent=tab, separators=separators, ensure_ascii=False)


def from_(json: str) -> dict[str, ...]:
    """
    :param json: json-like string
    :return: dict
    """

    return loads(json)


def fromfile(abspath: str) -> dict[str, ...]:
    with open(abspath, encoding='utf8') as file:
        return from_(file.read())


__all__ = ('to_', 'from_', 'fromfile')
