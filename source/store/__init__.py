from fastapi import APIRouter

from .settings import router as settings_router
from .items import router as items_router
from .info import router as info_router
from .access import router as access_router


router = APIRouter()

router.include_router(settings_router, prefix="/settings")
router.include_router(items_router, prefix="/items")
router.include_router(info_router, prefix="/info")
router.include_router(access_router, prefix="/access")
