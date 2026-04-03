from fastapi import FastAPI, Request, Response
from typing import Callable, Awaitable

from importlib import reload

from scripts.unix import raw as unix_raw

from source.firewall import router as firewall_router
from source.registration import router as registration_router
from source.user import router as user_router
from source.store import router as store_router
from source.admin import router as admin_router
from source.auction import router as auction_router
from source.promo import router as promo_router

from data import config as cfg


app = FastAPI()
app.include_router(firewall_router, prefix="/fw")
app.include_router(registration_router, prefix="/reg")

app.include_router(user_router, prefix="/user")
app.include_router(store_router, prefix="/store")
app.include_router(admin_router, prefix="/admin")
app.include_router(auction_router, prefix="/auc")
app.include_router(promo_router, prefix="/promo")


IP_BLACKLIST_update_target = unix_raw() + 2 * cfg.BLACKLIST_UPDATE_TIME

@app.middleware("http")
async def IP_censor(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
    """
    Проверяет IP отправителя реквеста на всём http поле

    :param request: исходные данные реквеста
    :param call_next: следующий миддлвэри-фильтр или целевая функция
    :return: ответ call_next
    """
    global IP_BLACKLIST_update_target

    if unix_raw() >= IP_BLACKLIST_update_target:
        IP_BLACKLIST_update_target = unix_raw() + cfg.BLACKLIST_UPDATE_TIME
        reload(cfg)

    if request.client.host in cfg.IP_BLACKLIST:
        return Response(status_code=402)

    return await call_next(request)


@app.get("/")
async def root():
    return "LyPay Forever!"
