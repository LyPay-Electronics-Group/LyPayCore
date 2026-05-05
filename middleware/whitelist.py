from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from fastapi import Request, Response

from dotenv import load_dotenv
from os import getenv

from scripts.unix import raw as unix_raw
from data.config import IP_CENSOR_UPDATE_TIME



class IPWhitelist(BaseHTTPMiddleware):
    def __init__(
        self,
        app: ASGIApp,
        update_interval: float = IP_CENSOR_UPDATE_TIME
    ):
        super().__init__(app)

        self.update_interval = update_interval
        self.next_update = unix_raw() + 2 * self.update_interval

        self.whitelist = set()
        self._update_whitelist()


    async def dispatch(self, request: Request, call_next):
        now = unix_raw()
        if now >= self.next_update:
            self.next_update = now + self.update_interval
            self._update_whitelist()

        if request.client.host not in self.whitelist:
            return Response(status_code=402)

        return await call_next(request)


    def _update_whitelist(self):
        load_dotenv()
        self.whitelist.clear()
        for ip in getenv("LYPAY_CORE_IP_WHITELIST").split(","):
            self.whitelist.add(ip.strip())
