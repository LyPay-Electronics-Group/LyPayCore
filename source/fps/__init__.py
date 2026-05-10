from fastapi import APIRouter

from .info import router as info_router
from .create import router as create_router


router = APIRouter()

router.include_router(info_router)
router.include_router(create_router)
