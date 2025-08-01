"""
API routers for the Crypto Trading Bot application.
Contains all FastAPI route definitions organized by domain.
"""

from .auth import router as auth_router
from .users import router as users_router

__all__ = ["auth_router", "users_router"]
