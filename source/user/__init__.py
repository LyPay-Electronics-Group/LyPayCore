from fastapi import APIRouter

from .balance import router as balance_router
from .info import router as info_router
from .qr import router as qr_router


router = APIRouter()

router.include_router(balance_router)
router.include_router(info_router)
router.include_router(qr_router)
