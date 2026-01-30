from fastapi import APIRouter

from .email import router as email_router
from .record import router as record_router


router = APIRouter()

router.include_router(email_router, prefix="/email")
router.include_router(record_router)
