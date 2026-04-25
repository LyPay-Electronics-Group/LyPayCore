from smtplib import SMTP
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.encoders import encode_base64 as encode_attachment

from asyncio import to_thread

from datetime import datetime

from os import getenv

from data.config import EMAIL


def send(*,
         path: str, sender: str | None = None, recipient: str,
         subject: str,
         keys: dict[str, ...] | None = None,
         files: list[str] | None = None):
    """
    Отправляет письмо по электронной почте из конфига с заданными параметрами (синхронно)

    :param path: (абсолютный) путь до html-файла с основой письма и текстом
    :param sender: подпись отправителя (по умолчанию: config.EMAIL.SENDER
    :param recipient: email получателя
    :param subject: тема письма
    :param keys: словарь ключей для замены (по умолчанию не используется)
    :param files: список (абсолютных) путей к файлам для отправки в качестве приложенных файлов (по умолчанию не используется)
    """

    with open(path, encoding='utf8') as html:
        text_input = html.read()
    if keys is not None:
        for key, value in keys.items():
            text_input = text_input.replace(f'{{:{key}:}}', f'{value}')
    message = MIMEMultipart()
    message["Subject"] = subject.format(year=datetime.now().year)
    message["From"] = sender if sender is not None else EMAIL.SENDER
    message["To"] = recipient
    message.attach(MIMEText(text_input, 'html'))

    if files is not None:
        for file in files:
            attachment_path = file.replace('\\', '/')
            attachment_name = attachment_path[attachment_path.rfind('/') + 1:]
            file = MIMEBase('application', 'octet-stream')
            with open(attachment_path, 'rb') as raw:
                file.set_payload(raw.read())
            encode_attachment(file)
            file.add_header('Content-Disposition', f'attachment; filename="{attachment_name}"')
            message.attach(file)

    with SMTP(getenv("LYPAY_EMAIL_HOST"), int(getenv("LYPAY_EMAIL_PORT"))) as email:
        email.starttls()
        email.login(getenv("LYPAY_EMAIL_MAIL"), getenv("LYPAY_EMAIL_PASSWORD"))
        email.send_message(message)


async def send_async(*,
                     path: str, sender: str | None = None, recipient: str,
                     subject: str,
                     keys: dict[str, ...] | None = None,
                     files: list[str] | None = None):
    """
    Отправляет письмо по электронной почте из конфига с заданными параметрами (асинхронно)

    :param path: (абсолютный) путь до html-файла с основой письма и текстом
    :param sender: подпись отправителя (по умолчанию: config.EMAIL.SENDER
    :param recipient: email получателя
    :param subject: тема письма
    :param keys: словарь ключей для замены (по умолчанию не используется)
    :param files: список (абсолютных) путей к файлам для отправки в качестве приложенных файлов (по умолчанию не используется)
    """
    await to_thread(
        send,
        path=path, sender=sender, recipient=recipient,
        subject=subject, keys=keys, files=files
    )
