from segno import make_qr
from aiofiles import open as a_open

from fastapi import UploadFile

from data.config import PATHS, CHUNK_SIZE


def qr(value: int):
    """
    Создание QR-кода по введённому числовому значению.
    QR будет сохранён в config.PATHS.QR с именем файла, равным `value`

    :param value: число
    """
    make_qr(value).save(PATHS.QR + f"{value}.png", scale=5, border=5)


async def save_iterative(origin: UploadFile, target_path: str):
    """
    Записывает контент из файлового потока в новый файл

    :param origin: исходный файловый поток
    :param target_path: путь к файлу для записи
    """

    async with a_open(target_path, 'wb') as target:
        while chunk := await origin.read(CHUNK_SIZE):
            await target.write(chunk)
