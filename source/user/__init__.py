from fastapi import APIRouter

from .transactions import router as transactions_router
from .info import router as info_router
from .qr import router as qr_router
from .settings import router as settings_router


router = APIRouter()

router.include_router(transactions_router)
router.include_router(info_router)
router.include_router(qr_router, prefix="/qr")
router.include_router(settings_router, prefix="/settings")
