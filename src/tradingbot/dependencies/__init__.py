"""
Dependency injection modules for the Crypto Trading Bot application.
Contains reusable dependencies for authentication, database access, and more.
"""

from .auth import (
    get_current_active_user,
    get_current_admin_user,
    get_current_user,
    get_current_user_optional,
)

__all__ = [
    "get_current_user",
    "get_current_active_user",
    "get_current_admin_user",
    "get_current_user_optional",
]
