from fastapi import APIRouter

from src.modules import users

from . import health

__all__ = ("router",)

router = APIRouter()

router.include_router(health.router)

router.include_router(users.router)
