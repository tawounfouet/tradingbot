"""
Test script for the refactored crypto trading bot configuration.

This script tests the new architecture with:
- Database management in database/ package
- Configuration management in config/ package
- Clear separation of concerns
"""

import logging
import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def test_config_imports():
    """Test configuration package imports."""
    print("\n=== Testing Configuration Imports ===")

    try:
        from config import SecurityConfig, Settings, get_settings
        from config.constants import OrderSide, OrderType, StrategyStatus

        print("✅ Configuration imports successful")
        return True
    except ImportError as e:
        print(f"❌ Configuration import failed: {e}")
        return False


def test_database_imports():
    """Test database package imports."""
    print("\n=== Testing Database Imports ===")

    try:
        from database import (
            DatabaseManager,
            db_manager,
            get_database_info,
            get_db_session,
            init_database,
        )

        print("✅ Database imports successful")
        return True
    except ImportError as e:
        print(f"❌ Database import failed: {e}")
        return False


def test_settings():
    """Test settings configuration."""
    print("\n=== Testing Settings Configuration ===")

    try:
        from config import get_settings

        settings = get_settings()
        print(f"✅ Settings loaded: {settings.APP_NAME}")
        print(f"   Environment: {settings.ENVIRONMENT}")
        print(f"   Debug mode: {settings.DEBUG}")

        return True
    except Exception as e:
        print(f"❌ Settings test failed: {e}")
        return False


def test_database_connection():
    """Test database connection and setup."""
    print("\n=== Testing Database Connection ===")

    try:
        from database import db_manager, get_database_info

        # Get database info
        db_info = get_database_info()
        print(f"✅ Database info retrieved:")
        for key, value in db_info.items():
            print(f"   {key}: {value}")

        # Test connection
        if db_manager.check_connection():
            print("✅ Database connection successful")
        else:
            print("❌ Database connection failed")
            return False

        return True
    except Exception as e:
        print(f"❌ Database connection test failed: {e}")
        return False


def test_table_creation():
    """Test database table creation."""
    print("\n=== Testing Table Creation ===")

    try:
        from database import init_database

        if init_database():
            print("✅ Database tables created successfully")
            return True
        else:
            print("❌ Database table creation failed")
            return False
    except Exception as e:
        print(f"❌ Table creation test failed: {e}")
        return False


def test_session_management():
    """Test database session management."""
    print("\n=== Testing Session Management ===")

    try:
        from database import get_db_session
        from sqlalchemy import text

        with get_db_session() as session:
            result = session.execute(text("SELECT 1")).scalar()
            if result == 1:
                print("✅ Database session management working")
                return True
            else:
                print("❌ Database session query failed")
                return False
    except Exception as e:
        print(f"❌ Session management test failed: {e}")
        return False


def test_security_config():
    """Test security configuration."""
    print("\n=== Testing Security Configuration ===")

    try:
        from config import SecurityConfig

        security = SecurityConfig()

        # Test password hashing
        password = "test_password_123"
        hashed = security.hash_password(password)

        if security.verify_password(password, hashed):
            print("✅ Password hashing and verification working")
        else:
            print("❌ Password verification failed")
            return False

        # Test token generation
        token = security.create_access_token({"sub": "test_user"})
        if token:
            print("✅ Token generation working")
        else:
            print("❌ Token generation failed")
            return False

        return True
    except Exception as e:
        print(f"❌ Security configuration test failed: {e}")
        return False


def run_all_tests():
    """Run all tests and provide summary."""
    print("🚀 Starting Crypto Trading Bot Configuration Tests")
    print("=" * 60)

    tests = [
        ("Config Imports", test_config_imports),
        ("Database Imports", test_database_imports),
        ("Settings", test_settings),
        ("Database Connection", test_database_connection),
        ("Table Creation", test_table_creation),
        ("Session Management", test_session_management),
        ("Security Config", test_security_config),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"Test {test_name} crashed: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)

    passed = 0
    total = len(results)

    for test_name, passed_test in results:
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"{status} - {test_name}")
        if passed_test:
            passed += 1

    print(f"\nResults: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Configuration is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")

    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
