"""
FastAPI dependencies for the Crypto Trading Bot application.
Contains reusable dependencies for authentication, pagination, etc.
"""

from typing import Optional

from fastapi import Depends, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from ..database.connection import get_session
from ..models.user import User
from ..schemas.common import PaginationParams
from ..services.auth_service import auth_service

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> User:
    """
    Get current authenticated user from access token.

    Args:
        credentials: HTTP Bearer token credentials

    Returns:
        User: Current authenticated user

    Raises:
        HTTPException: If token is invalid or user not found
    """
    token = credentials.credentials
    user = await auth_service.get_current_user(token)
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current active user (must be active).

    Args:
        current_user: Current authenticated user

    Returns:
        User: Current active user

    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    return current_user


async def get_current_admin_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Get current admin user (must be active admin).

    Args:
        current_user: Current active user

    Returns:
        User: Current admin user

    Raises:
        HTTPException: If user is not admin
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )
    return current_user


async def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    ),
) -> Optional[User]:
    """
    Get current user if token is provided, None otherwise.

    Args:
        credentials: Optional HTTP Bearer token credentials

    Returns:
        Optional[User]: Current user if authenticated, None otherwise
    """
    if not credentials:
        return None

    try:
        token = credentials.credentials
        user = await auth_service.get_current_user(token)
        return user
    except HTTPException:
        return None


def get_db_session() -> Session:
    """
    Get database session.

    Returns:
        Session: Database session
    """
    return get_session()


def get_pagination_params(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    sort_by: Optional[str] = Query(None, description="Sort field"),
    sort_order: str = Query("asc", regex="^(asc|desc)$", description="Sort order"),
) -> PaginationParams:
    """
    Get pagination parameters.

    Args:
        page: Page number (starts from 1)
        size: Page size (1-100)
        sort_by: Field to sort by
        sort_order: Sort order (asc/desc)

    Returns:
        PaginationParams: Pagination parameters
    """
    return PaginationParams(
        page=page, size=size, sort_by=sort_by, sort_order=sort_order
    )


def get_search_params(
    q: Optional[str] = Query(None, description="Search query"),
    filter_by: Optional[str] = Query(None, description="Filter field"),
    filter_value: Optional[str] = Query(None, description="Filter value"),
) -> dict:
    """
    Get search and filter parameters.

    Args:
        q: Search query string
        filter_by: Field to filter by
        filter_value: Value to filter by

    Returns:
        dict: Search and filter parameters
    """
    return {"search_query": q, "filter_by": filter_by, "filter_value": filter_value}


class RateLimitDependency:
    """Rate limiting dependency."""

    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        # TODO: Implement rate limiting logic with Redis

    async def __call__(self, request):
        # TODO: Implement rate limiting check
        return True


class PermissionChecker:
    """Permission checking dependency."""

    def __init__(self, required_permission: str):
        self.required_permission = required_permission

    async def __call__(self, current_user: User = Depends(get_current_active_user)):
        # TODO: Implement permission checking logic
        # For now, just check if user is admin for admin permissions
        if self.required_permission.startswith("admin:") and not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
            )
        return current_user


# Common permission dependencies
require_admin = PermissionChecker("admin:read")
require_user_management = PermissionChecker("admin:user_management")
require_strategy_management = PermissionChecker("user:strategy_management")
require_trading = PermissionChecker("user:trading")

# Rate limiting dependencies
rate_limit_auth = RateLimitDependency(max_requests=10, window_seconds=60)
rate_limit_api = RateLimitDependency(max_requests=100, window_seconds=60)
rate_limit_trading = RateLimitDependency(max_requests=50, window_seconds=60)
