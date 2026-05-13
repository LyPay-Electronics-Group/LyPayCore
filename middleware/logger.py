from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from logging import Logger
from http import HTTPStatus

from colorama import Fore, Style, init as c_init

c_init(autoreset=True)


class CustomLog(BaseHTTPMiddleware):
    max_client_length = 15
    max_token_length = 9
    max_message_length = 90

    def __init__(self, app: ASGIApp, app_logger: Logger, blacklist: tuple[str]):
        super().__init__(app)
        self.app_logger = app_logger
        self.blacklist = blacklist


    async def dispatch(self, request, call_next):
        response = await call_next(request)

        if request.url.path not in self.blacklist:
            client = Fore.LIGHTBLACK_EX + Style.BRIGHT + request.client.host
            client_tab = " " * max(self.max_client_length - len(request.client.host), 0)

            token = getattr(request.state, "token", "<missing>")
            token_str = Fore.YELLOW + Style.DIM + str(token)
            token_tab = " " * max(self.max_token_length - len(token), 0)

            message = Fore.GREEN + Style.NORMAL + f"{request.method}" + \
            (' ' if request.method == "GET" else '') + \
            Fore.CYAN + Style.NORMAL + f" {request.url.path}"
            message_tab = " " * max(self.max_message_length - len(message) - 5, 0)

            if response.status_code >= 400:
                status_code = Fore.RED
            elif response.status_code >= 300:
                status_code = Fore.YELLOW
            else:
                status_code = Fore.GREEN
            status_code += f"{response.status_code} {HTTPStatus(response.status_code).phrase}"

            self.app_logger.info(
                client + Style.RESET_ALL + client_tab +
                " | " +
                token_str + Style.RESET_ALL + token_tab +
                " | " +
                message + Style.RESET_ALL + message_tab +
                " | " +
                status_code + Style.RESET_ALL
            )

        return response
