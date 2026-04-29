from fastapi import APIRouter

from .test1 import router as test1_router


router = APIRouter()

router.include_router(test1_router)
