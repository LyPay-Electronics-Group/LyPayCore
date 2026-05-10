from fastapi import APIRouter

from .info import router as info_router
from .access import router as access_router


router = APIRouter()

router.include_router(info_router)
router.include_router(access_router)
