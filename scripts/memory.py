from segno import make_qr

from data.config import PATHS


def qr(value: int):
    """
    Создание QR-кода по введённому числовому значению.
    QR будет сохранён в config.PATHS.QR с именем файла, равным `value`

    :param value: число
    """
    make_qr(value).save(PATHS.QR + f"{value}.png", scale=5, border=5)
