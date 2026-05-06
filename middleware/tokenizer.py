from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from fastapi import Request, Response

from urllib.parse import urlencode

from scripts.unix import raw as unix_raw
from scripts.j2 import fromfile_async as j2_fromfile_async

from data.config import IP_CONFIG_REFRESH_DELTA, IP_CONFIG_FILE



class Tokenizer(BaseHTTPMiddleware):
    def __init__(
        self,
        app: ASGIApp,
        update_interval: float = IP_CONFIG_REFRESH_DELTA
    ):
        super().__init__(app)

        self.update_interval = update_interval
        self.next_update = 0
        self.config = dict()


    async def dispatch(self, request: Request, call_next):
        query = dict(request.query_params)
        token = query.pop("token", "default")

        await self._refresh_config()
        whitelist = self.config.get(token, None)

        if whitelist is None:
            return Response(status_code=402)
        if request.client.host not in whitelist:
            return Response(status_code=403)

        new_query = urlencode(query) if len(query) > 0 else ''
        request.scope["query_string"] = new_query.encode("utf8")
        request.state.token = token

        return await call_next(request)


    async def _refresh_config(self):
        now = unix_raw()
        if now >= self.next_update:
            self.next_update = now + self.update_interval
            self.config = await j2_fromfile_async(IP_CONFIG_FILE)
