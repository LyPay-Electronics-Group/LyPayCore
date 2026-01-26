from importlib import reload
from os import mkdir
from os.path import exists

from segno import make_qr

from data.config import PATHS
from scripts import j2


async def read_sublist(__name__: str) -> dict[str, ...]:
    """
    Функция для чтения саблиста

    :param __name__: имя листа
    :return: словарь с прочитанным листом
    """
    try:
        return await j2.fromfile_async(PATHS.LISTS + __name__ + '.json')
    except FileNotFoundError:
        with open(PATHS.LISTS + __name__ + '.json', 'w', encoding='utf8') as f:
            f.write('{}')
        return dict()


async def rewrite_sublist(*, mode: str = 'add', name: str, key: str | int, data: str | int | None = None):
    """
    [LEGACY] Функция для записи/удаления значений из саблистов

    :param mode: 'add' или 'remove'
    :param name: имя листа
    :param key: ключ, по которому будет записана/удалена запись
    :param data: значение для записи
    """
    if name.count(' ') > 0:
        raise ValueError("Аргумент name функции sublist не должен содержать пробелы.")
    if mode not in ('add', 'remove'):
        raise ValueError("Аргумент mode функции sublist указан неверно.")
    if mode == 'add' and data is None:
        raise ValueError("Аргумент data функции sublist не может быть пуст в режиме записи.")

    try:
        js = await j2.fromfile_async(PATHS.LISTS + name + '.json')
    except FileNotFoundError:
        js = dict()

    if mode == 'add':
        js[key] = data
    elif key in js.keys():  # mode == 'remove'
        js.pop(key)

    sublist_path = name.replace('\\', '/')
    directory_check = sublist_path.split('/')
    for i in range(1, len(directory_check)):
        if not exists(PATHS.LISTS + '/'.join(directory_check[:i])):
            mkdir(PATHS.LISTS + '/'.join(directory_check[:i]))
    with open(PATHS.LISTS + sublist_path + '.json', 'w', encoding='utf8') as f:
        # в этом месте будут проблемы при многопоточности
        f.write(j2.to_(js))


def qr(value: int):
    """
    Создание QR-кода по введённому числовому значению.
    QR будет сохранён в config.PATHS.QR с именем файла, равным `value`

    :param value: число
    """
    make_qr(value).save(PATHS.QR + f"{value}.png", scale=5, border=5)


def update_config(__old_config_version__: list[int], __library_links__: list[...]) -> bool:
    """
    Обновляет конфигурацию сборки, перезагружая библиотеки и файл конфига

    :param __old_config_version__: номер старой версии внутри списка, в списке должен быть только он
    :param __library_links__: список библиотек для перезагрузки
    :return: True если обновление произошло, False в обратном случае
    """
    if len(__old_config_version__) > 1:
        raise ValueError("Аргументы функции update_config указаны неверно.")
    current_v = j2.fromfile(PATHS.LAUNCH_SETTINGS)["config_v"]
    if current_v != __old_config_version__[0]:
        __old_config_version__[0] = current_v
        for library in __library_links__:
            reload(library)
        return True
    return False
