from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from hashlib import sha256

from scripts import parser


router = APIRouter()


@router.post("/test1")
async def test1(request: Request):
    try:
        data = await request.body()
        return JSONResponse(
            {"hash": sha256(data).hexdigest()},
            status_code=200
        )
    except Exception as e:
        return parser.form_error(e)
