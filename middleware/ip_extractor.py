from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp


class RealIPExtractor(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)


    async def dispatch(self, request, call_next):
        client_host, client_port = request.client if request.client else (None, None)

        real_ip = None
        x_real_ip = request.headers.get("X-Real-IP")
        x_forwarded_for = request.headers.get("X-Forwarded-For")

        if x_real_ip:
            real_ip = x_real_ip.strip()
        elif x_forwarded_for:
            first_ip = x_forwarded_for.split(",")[0].strip()
            real_ip = first_ip

        if real_ip:
            request.scope["client"] = (real_ip, client_port)

        return await call_next(request)
