"""
Authentication service for the Crypto Trading Bot application.
Handles user authentication, JWT tokens, and session management.
"""

import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from tradingbot.config.settings import get_settings
from tradingbot.database.connection import get_db_session
from fastapi import HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from tradingbot.models.user import User, UserSession
from passlib.context import CryptContext
from tradingbot.schemas.user import (
    LoginRequest,
    TokenResponse,
    UserCreate,
    UserResponse,
)

settings = get_settings()
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Service for handling authentication operations."""

    def __init__(self):
        self.secret_key = settings.SECRET_KEY.get_secret_value()
        self.algorithm = settings.ALGORITHM
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_token_expire_days = settings.REFRESH_TOKEN_EXPIRE_DAYS

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Generate password hash."""
        return pwd_context.hash(password)

    def create_access_token(
        self, data: dict, expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=self.access_token_expire_minutes
            )

        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def create_refresh_token(self, data: dict) -> str:
        """Create refresh token."""
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(
            days=self.refresh_token_expire_days
        )
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def verify_token(self, token: str, token_type: str = "access") -> dict:
        """Verify and decode token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            if payload.get("type") != token_type:
                raise JWTError("Invalid token type")
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user with username/email and password."""
        with get_db_session() as session:
            # Try to find user by username or email
            user = (
                session.query(User)
                .filter((User.username == username) | (User.email == username))
                .first()
            )

            if not user:
                return None

            if not self.verify_password(password, user.hashed_password):
                return None

            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
                )

            # Detach the user from the session to make it independent
            session.expunge(user)
            return user

    def create_user_tokens(
        self, user: User, ip_address: str, user_agent: str
    ) -> TokenResponse:
        """Create access and refresh tokens for user."""
        # Create token data
        token_data = {
            "sub": user.id,
            "username": user.username,
            "email": user.email,
            "is_admin": user.is_admin,
        }

        # Generate tokens
        access_token = self.create_access_token(token_data)
        refresh_token = self.create_refresh_token({"sub": user.id})

        # Create user response object while we have access to user data
        user_response = UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            is_active=user.is_active,
            is_admin=user.is_admin,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

        # Store refresh token in database
        with get_db_session() as session:
            db_session = UserSession(
                id=str(uuid.uuid4()),
                user_id=user.id,
                token=refresh_token,
                expires_at=datetime.now(timezone.utc)
                + timedelta(days=self.refresh_token_expire_days),
                ip_address=ip_address,
                user_agent=user_agent,
            )
            session.add(db_session)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=self.access_token_expire_minutes * 60,
            user=user_response,
        )

    def refresh_access_token(self, refresh_token: str) -> str:
        """Generate new access token from refresh token."""
        # Verify refresh token
        payload = self.verify_token(refresh_token, "refresh")
        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
            )

        # Check if refresh token exists in database
        with get_db_session() as session:
            db_session = (
                session.query(UserSession)
                .filter(
                    UserSession.token == refresh_token,
                    UserSession.expires_at > datetime.now(timezone.utc),
                )
                .first()
            )

            if not db_session:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired refresh token",
                )

            # Get user
            user = session.query(User).filter(User.id == user_id).first()
            if not user or not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found or inactive",
                )

            # Create new access token
            token_data = {
                "sub": user.id,
                "username": user.username,
                "email": user.email,
                "is_admin": user.is_admin,
            }

            return self.create_access_token(token_data)

    def logout_user(self, refresh_token: str) -> bool:
        """Logout user by invalidating refresh token."""
        with get_db_session() as session:
            db_session = (
                session.query(UserSession)
                .filter(UserSession.token == refresh_token)
                .first()
            )

            if db_session:
                session.delete(db_session)
                return True
            return False

    def logout_all_sessions(self, user_id: str) -> int:
        """Logout user from all sessions."""
        with get_db_session() as session:
            count = (
                session.query(UserSession)
                .filter(UserSession.user_id == user_id)
                .delete()
            )
            return count

    def get_current_user(self, token: str) -> User:
        """Get current user from access token."""
        payload = self.verify_token(token)
        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )

        with get_db_session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
                )

            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user"
                )

            # Detach the user from the session to make it independent
            session.expunge(user)
            return user


# Global auth service instance
auth_service = AuthService()
