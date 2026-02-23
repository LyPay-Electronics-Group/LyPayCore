from fastapi import APIRouter

from .settings import router as settings_router


router = APIRouter()

router.include_router(settings_router, prefix="/settings")
