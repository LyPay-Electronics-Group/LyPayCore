from fastapi import APIRouter

from .avatar import router as avatar_router
from .name import router as name_router
from .description import router as description_router


router = APIRouter()

router.include_router(avatar_router, prefix="/avatar")
router.include_router(name_router, prefix="/name")
router.include_router(description_router, prefix="/desc")
