"""
Users router for the Crypto Trading Bot API.
Provides endpoints for user management, profiles, and settings.
"""

from typing import List, Optional

from tradingbot.dependencies.auth import get_current_admin_user, get_current_user
from fastapi import APIRouter, Depends, HTTPException, Query, status
from tradingbot.models.user import User as UserModel
from tradingbot.schemas.user import UserResponse, UserSettingsUpdate, UserUpdate
from tradingbot.services.user_service import user_service

# Define a constant for the error message
USER_NOT_FOUND_MSG = "User not found"

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: UserModel = Depends(get_current_user),
) -> UserResponse:
    """
    Get current user's profile information.

    Returns the authenticated user's profile data.
    """
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    user_update: UserUpdate, current_user: UserModel = Depends(get_current_user)
) -> UserResponse:
    """
    Update current user's profile information.

    - **email**: New email address (must be unique)
    - **username**: New username (must be unique)
    - **first_name**: New first name
    - **last_name**: New last name
    """
    try:
        updated_user = await user_service.update_user(current_user.id, user_update)
        return updated_user

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user profile: {str(e)}",
        )


@router.delete("/me")
async def delete_current_user_account(
    current_user: UserModel = Depends(get_current_user),
) -> dict:
    """
    Delete current user's account.

    This action is irreversible and will remove all user data.
    """
    try:
        success = await user_service.delete_user(current_user.id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to delete user account",
            )

        return {"message": "Account successfully deleted"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete account: {str(e)}",
        )


@router.get("/me/settings")
async def get_user_settings(
    current_user: UserModel = Depends(get_current_user),
) -> dict:
    """
    Get current user's settings and preferences.
    """
    try:
        settings = await user_service.get_user_settings(current_user.id)
        return settings or {}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user settings: {str(e)}",
        )


@router.put("/me/settings")
async def update_user_settings(
    settings_update: UserSettingsUpdate,
    current_user: UserModel = Depends(get_current_user),
) -> dict:
    """
    Update current user's settings and preferences.

    - **theme**: UI theme preference
    - **risk_profile**: Risk tolerance level
    - **notification_preferences**: Notification settings
    """
    try:
        updated_settings = await user_service.update_user_settings(
            current_user.id, settings_update
        )
        return updated_settings

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user settings: {str(e)}",
        )


# Admin-only endpoints
@router.get("/", response_model=List[UserResponse])
async def list_users(
    skip: int = Query(0, ge=0, description="Number of users to skip"),
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of users to return"
    ),
    search: Optional[str] = Query(
        None, description="Search users by username or email"
    ),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    is_admin: Optional[bool] = Query(None, description="Filter by admin status"),
    current_admin: UserModel = Depends(get_current_admin_user),
) -> List[UserResponse]:
    """
    List all users (admin only).

    Supports pagination, search, and filtering options.
    """
    try:
        users = await user_service.get_users(
            skip=skip,
            limit=limit,
            search=search,
            is_active=is_active,
            is_admin=is_admin,
        )
        return users

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list users: {str(e)}",
        )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: str, current_admin: UserModel = Depends(get_current_admin_user)
) -> UserResponse:
    """
    Get user by ID (admin only).

    - **user_id**: UUID of the user to retrieve
    """
    try:
        user = await user_service.get_user_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=USER_NOT_FOUND_MSG
            )

        return user

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user: {str(e)}",
        )


@router.put("/{user_id}", response_model=UserResponse)
async def update_user_by_id(
    user_id: str,
    user_update: UserUpdate,
    current_admin: UserModel = Depends(get_current_admin_user),
) -> UserResponse:
    """
    Update user by ID (admin only).

    - **user_id**: UUID of the user to update
    - **email**: New email address (must be unique)
    - **username**: New username (must be unique)
    - **first_name**: New first name
    - **last_name**: New last name
    - **is_active**: Enable/disable user account
    """
    try:
        user = await user_service.get_user_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=USER_NOT_FOUND_MSG
            )

        updated_user = await user_service.update_user(user_id, user_update)
        return updated_user

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user: {str(e)}",
        )


@router.delete("/{user_id}")
async def delete_user_by_id(
    user_id: str, current_admin: UserModel = Depends(get_current_admin_user)
) -> dict:
    """
    Delete user by ID (admin only).

    - **user_id**: UUID of the user to delete
    """
    try:
        user = await user_service.get_user_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=USER_NOT_FOUND_MSG
            )

        # Prevent self-deletion
        if user_id == current_admin.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete your own account",
            )

        success = await user_service.delete_user(user_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to delete user"
            )

        return {"message": f"User {user_id} successfully deleted"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete user: {str(e)}",
        )


@router.post("/{user_id}/activate")
async def activate_user(
    user_id: str, current_admin: UserModel = Depends(get_current_admin_user)
) -> dict:
    """
    Activate user account (admin only).

    - **user_id**: UUID of the user to activate
    """
    try:
        user = await user_service.get_user_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=USER_NOT_FOUND_MSG
            )

        if user.is_active:
            return {"message": "User is already active"}

        await user_service.update_user(user_id, UserUpdate(is_active=True))

        return {"message": f"User {user_id} successfully activated"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to activate user: {str(e)}",
        )


@router.post("/{user_id}/deactivate")
async def deactivate_user(
    user_id: str, current_admin: UserModel = Depends(get_current_admin_user)
) -> dict:
    """
    Deactivate user account (admin only).

    - **user_id**: UUID of the user to deactivate
    """
    try:
        user = await user_service.get_user_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=USER_NOT_FOUND_MSG
            )

        # Prevent self-deactivation
        if user_id == current_admin.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot deactivate your own account",
            )

        if not user.is_active:
            return {"message": "User is already inactive"}

        await user_service.update_user(user_id, UserUpdate(is_active=False))

        return {"message": f"User {user_id} successfully deactivated"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to deactivate user: {str(e)}",
        )
