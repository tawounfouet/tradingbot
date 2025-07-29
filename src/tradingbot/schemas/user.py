"""
User-related Pydantic schemas for the Crypto Trading Bot application.
Contains schemas for user creation, authentication, and responses.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from .common import BaseResponse


class ThemeEnum(str, Enum):
    """Available UI themes."""

    LIGHT = "light"
    DARK = "dark"


class RiskProfileEnum(str, Enum):
    """Available risk profiles."""

    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"


# User Creation and Updates
class UserCreate(BaseModel):
    """Schema for user creation."""

    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    password: str = Field(..., min_length=8, max_length=100)

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "username": "trader123",
                "first_name": "John",
                "last_name": "Doe",
                "password": "SecurePassword123!",
            }
        }


class UserUpdate(BaseModel):
    """Schema for user updates."""

    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None

    class Config:
        json_schema_extra = {
            "example": {"first_name": "John", "last_name": "Doe Updated"}
        }


class PasswordChange(BaseModel):
    """Schema for password change."""

    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)
    confirm_password: str


# User Settings
class UserSettingsUpdate(BaseModel):
    """Schema for user settings updates."""

    theme: Optional[ThemeEnum] = None
    risk_profile: Optional[RiskProfileEnum] = None
    notification_preferences: Optional[dict] = None

    class Config:
        json_schema_extra = {
            "example": {
                "theme": "dark",
                "risk_profile": "moderate",
                "notification_preferences": {
                    "email": True,
                    "push": False,
                    "trading_alerts": True,
                },
            }
        }


# User Responses
class UserBase(BaseModel):
    """Base user fields for responses."""

    id: str
    email: EmailStr
    username: str
    first_name: Optional[str]
    last_name: Optional[str]
    is_active: bool
    is_admin: bool
    created_at: datetime
    updated_at: datetime


class UserResponse(UserBase):
    """Complete user response."""

    class Config:
        from_attributes = True


class UserPublic(BaseModel):
    """Public user information (limited fields)."""

    id: str
    username: str
    first_name: Optional[str]

    class Config:
        from_attributes = True


class UserSettings(BaseModel):
    """User settings response."""

    theme: ThemeEnum
    risk_profile: RiskProfileEnum
    notification_preferences: dict

    class Config:
        from_attributes = True


class UserProfile(UserResponse):
    """Extended user profile with settings."""

    settings: Optional[UserSettings] = None

    class Config:
        from_attributes = True


# Authentication
class LoginRequest(BaseModel):
    """Login request schema."""

    username: str  # Can be username or email
    password: str

    class Config:
        json_schema_extra = {
            "example": {"username": "trader123", "password": "SecurePassword123!"}
        }


class TokenResponse(BaseResponse):
    """Token response after successful login."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    user: UserResponse


class TokenRefresh(BaseModel):
    """Token refresh request."""

    refresh_token: str


class LogoutRequest(BaseModel):
    """Logout request (optional token for specific session)."""

    refresh_token: Optional[str] = None


# User Lists and Statistics
class UserStats(BaseModel):
    """User statistics."""

    total_strategies: int
    active_deployments: int
    total_orders: int
    total_trades: int
    profit_loss: float
    win_rate: float

    class Config:
        from_attributes = True


class UserListResponse(BaseResponse):
    """Response for user list (admin only)."""

    users: list[UserPublic]


class UserCreateResponse(BaseResponse):
    """Response after user creation."""

    user: UserResponse


class UserUpdateResponse(BaseResponse):
    """Response after user update."""

    user: UserResponse
