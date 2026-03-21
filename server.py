from fastapi import FastAPI

from source.firewall import router as firewall_router
from source.registration import router as registration_router
from source.user import router as user_router
from source.store import router as store_router
from source.admin import router as admin_router
from source.auction import router as auction_router
from source.promo import router as promo_router


app = FastAPI()
app.include_router(firewall_router, prefix="/fw")
app.include_router(registration_router, prefix="/reg")

app.include_router(user_router, prefix="/user")
app.include_router(store_router, prefix="/store")
app.include_router(admin_router, prefix="/admin")
app.include_router(auction_router, prefix="/auc")
app.include_router(promo_router, prefix="/promo")


@app.get("/")
async def root():
    return "LyPay Forever!"
