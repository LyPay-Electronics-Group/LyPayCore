from fastapi import APIRouter

from .agent import router as agent_router
from .info import router as info_router


router = APIRouter()

router.include_router(agent_router, prefix="/agent")
router.include_router(info_router)
