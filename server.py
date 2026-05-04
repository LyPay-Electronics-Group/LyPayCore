from fastapi import FastAPI, Request, Response
from typing import Callable, Awaitable

from dotenv import load_dotenv
from os import getenv

from scripts.unix import raw as unix_raw

from source.firewall import router as firewall_router
from source.registration import router as registration_router
from source.user import router as user_router
from source.store import router as store_router
from source.admin import router as admin_router
from source.auction import router as auction_router
from source.promo import router as promo_router

from source.mst import router as mst_router

from data import config as cfg


app = FastAPI()
app.include_router(firewall_router, prefix="/fw")
app.include_router(registration_router, prefix="/reg")

app.include_router(user_router, prefix="/user")
app.include_router(store_router, prefix="/store")
app.include_router(admin_router, prefix="/admin")
app.include_router(auction_router, prefix="/auc")
app.include_router(promo_router, prefix="/promo")

app.include_router(mst_router, prefix="/mst")


def update_whitelist():
    global current_IP_WHITELIST
    load_dotenv()
    for ip in getenv("LYPAY_CORE_IP_WHITELIST").split(","):
        current_IP_WHITELIST.add(ip.strip())


current_IP_WHITELIST = set()
IP_CENSOR_update_target = unix_raw() + 2 * cfg.IP_CENSOR_UPDATE_TIME
update_whitelist()


@app.middleware("http")
async def IP_censor(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
    """
    Проверяет IP отправителя реквеста на всём http поле

    :param request: исходные данные реквеста
    :param call_next: следующий миддлвэри-фильтр или целевая функция
    :return: ответ call_next
    """
    global IP_CENSOR_update_target

    if unix_raw() >= IP_CENSOR_update_target:
        IP_CENSOR_update_target = unix_raw() + cfg.IP_CENSOR_UPDATE_TIME
        update_whitelist()

    if request.client.host not in current_IP_WHITELIST:
        return Response(status_code=402)

    return await call_next(request)


@app.get("/")
async def root():
    return "LyPay Forever!"
