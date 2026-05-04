from fastapi import FastAPI

from source.firewall import router as firewall_router
from source.registration import router as registration_router
from source.user import router as user_router
from source.store import router as store_router
from source.admin import router as admin_router
from source.auction import router as auction_router
from source.promo import router as promo_router

from source.mst import router as mst_router

from logging import getLogger, StreamHandler
from sys import stdout
from middleware.logger import CustomLog

from middleware.whitelist import IPWhitelist


app = FastAPI()
app.include_router(firewall_router, prefix="/fw")
app.include_router(registration_router, prefix="/reg")

app.include_router(user_router, prefix="/user")
app.include_router(store_router, prefix="/store")
app.include_router(admin_router, prefix="/admin")
app.include_router(auction_router, prefix="/auc")
app.include_router(promo_router, prefix="/promo")

app.include_router(mst_router, prefix="/mst")


logger = getLogger("app.requests")
logger.setLevel(20)  # level INFO
logger.addHandler(StreamHandler(stdout))

app.add_middleware(CustomLog, app_logger=logger, blacklist=[
    "/mst/machine/local_stats",
    "/mst/machine/core_stats"
])


app.add_middleware(IPWhitelist)


@app.get("/")
async def root():
    return "LyPay Forever!"
