from fastapi import APIRouter

from src.services.users import web as users_web

from . import health

__all__ = ("router",)

router = APIRouter()

router.include_router(health.router)
router.include_router(users_web.router)
