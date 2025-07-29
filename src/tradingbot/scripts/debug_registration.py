#!/usr/bin/env python3
"""
Script de débogage pour identifier le problème de registration.
"""

import os
import sys
import traceback
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))


def test_registration_flow():
    """Test the complete registration flow to identify the exact error."""
    print("=== DEBUGGING REGISTRATION FLOW ===\n")

    try:
        # Test imports
        print("1. Testing imports...")
        from schemas.user import UserCreate
        from services.auth_service import auth_service
        from services.user_service import user_service

        print("✓ Imports successful\n")

        # Test user creation
        print("2. Testing user creation...")
        import time

        unique_suffix = str(int(time.time()))
        user_data = UserCreate(
            email=f"debug{unique_suffix}@example.com",
            username=f"debuguser{unique_suffix}",
            first_name="Debug",
            last_name="User",
            password="debugpassword123",
        )

        # Create user
        user = user_service.create_user(user_data)
        print(f"✓ User created: {user.id}")
        print(f"  - Email: {user.email}")
        print(f"  - Username: {user.username}")
        print(f"  - Is Active: {user.is_active}\n")

        # Test token creation
        print("3. Testing token creation...")
        ip_address = "127.0.0.1"
        user_agent = "debug-agent"

        # This is where the error probably occurs
        tokens = auth_service.create_user_tokens(user, ip_address, user_agent)
        print(f"✓ Tokens created successfully!")
        print(f"  - Access token length: {len(tokens.access_token)}")
        print(f"  - Has refresh token: {bool(tokens.refresh_token)}")
        print(f"  - User in response: {tokens.user.username}")

        return True

    except Exception as e:
        print(f"❌ ERROR FOUND: {type(e).__name__}: {str(e)}")
        print("\n=== FULL TRACEBACK ===")
        traceback.print_exc()
        return False


def test_individual_components():
    """Test each component individually."""
    print("\n=== TESTING INDIVIDUAL COMPONENTS ===\n")

    try:
        # Test password hashing
        print("1. Testing password hashing...")
        from services.auth_service import auth_service

        password = "test123"
        hashed = auth_service.get_password_hash(password)
        verified = auth_service.verify_password(password, hashed)
        print(f"✓ Password hashing works: {verified}\n")

        # Test JWT token creation
        print("2. Testing JWT token creation...")
        token_data = {"sub": "test-user-id", "username": "testuser"}
        access_token = auth_service.create_access_token(token_data)
        refresh_token = auth_service.create_refresh_token({"sub": "test-user-id"})
        print(f"✓ Access token created: {len(access_token)} chars")
        print(f"✓ Refresh token created: {len(refresh_token)} chars\n")

        # Test UserResponse creation
        print("3. Testing UserResponse creation...")
        from datetime import datetime

        from schemas.user import UserResponse

        user_response = UserResponse(
            id="test-id",
            email="test@example.com",
            username="testuser",
            first_name="Test",
            last_name="User",
            is_active=True,
            is_admin=False,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        print(f"✓ UserResponse created: {user_response.username}\n")

        # Test TokenResponse creation
        print("4. Testing TokenResponse creation...")
        from schemas.user import TokenResponse

        token_response = TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=1800,
            user=user_response,
        )
        print(f"✓ TokenResponse created successfully\n")

        return True

    except Exception as e:
        print(f"❌ ERROR in individual components: {type(e).__name__}: {str(e)}")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("Starting registration debug session...\n")

    # Test individual components first
    components_ok = test_individual_components()

    if components_ok:
        print("Individual components work, testing full flow...\n")
        # Test full registration flow
        flow_ok = test_registration_flow()

        if flow_ok:
            print("\n✅ ALL TESTS PASSED! The registration should work.")
        else:
            print("\n❌ REGISTRATION FLOW FAILED!")
    else:
        print("\n❌ INDIVIDUAL COMPONENTS FAILED!")
