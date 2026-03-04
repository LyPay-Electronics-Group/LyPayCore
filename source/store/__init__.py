from fastapi import APIRouter

from .settings import router as settings_router
from .items import router as items_router


router = APIRouter()

router.include_router(settings_router, prefix="/settings")
router.include_router(items_router, prefix="/items")
