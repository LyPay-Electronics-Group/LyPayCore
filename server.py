from fastapi import FastAPI

from source.user import router as user_router
from source.firewall import router as firewall_router


app = FastAPI()
app.include_router(user_router, prefix="/user")
app.include_router(firewall_router, prefix="/fw")


@app.get("/")
async def root():
    return "LyPay Forever!"
