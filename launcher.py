from uvicorn import run
from server import app

from dotenv import load_dotenv
from os import getenv

load_dotenv()


run(app, host=getenv("LYPAY_HOST"), port=int(getenv("LYPAY_PORT")))
