from fastapi import APIRouter

from .transfer import router as transfer_router

router = APIRouter()

router.include_router(transfer_router)
