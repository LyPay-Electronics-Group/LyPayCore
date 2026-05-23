from fastapi import APIRouter

from .transfer import router as transfer_router
from .lot import router as lot_router
from .lottery import router as lottery_router

router = APIRouter()

router.include_router(transfer_router)
router.include_router(lot_router, prefix="/lot")
router.include_router(lottery_router)
