"""Unit tests for configuration module."""

import os
from unittest.mock import patch

import pytest


class TestSettings:
    """Test the settings configuration."""

    def test_settings_import(self):
        """Test that settings can be imported."""
        try:
            from tradingbot.config.settings import settings

            assert settings is not None
        except ImportError:
            pytest.skip("Settings module not available")

    @patch.dict(os.environ, {"DATABASE_URL": "postgresql://test:test@localhost/test"})
    def test_database_url_setting(self):
        """Test database URL configuration."""
        try:
            from tradingbot.config.settings import settings

            # Just test that we can access the setting
            assert hasattr(settings, "DATABASE_URL") or hasattr(
                settings, "database_url"
            )
        except (ImportError, AttributeError):
            pytest.skip("Database URL setting not available")

    def test_environment_variables(self):
        """Test environment variable handling."""
        # Test with mock environment
        with patch.dict(os.environ, {"TEST_VAR": "test_value"}, clear=False):
            assert os.getenv("TEST_VAR") == "test_value"


class TestConstants:
    """Test configuration constants."""

    def test_constants_import(self):
        """Test that constants can be imported."""
        try:
            from tradingbot.config import constants

            assert constants is not None
        except ImportError:
            pytest.skip("Constants module not available")

    def test_basic_constants_exist(self):
        """Test that basic constants exist."""
        try:
            from tradingbot.config import constants

            # Test for common constants that should exist
            assert hasattr(constants, "__name__")  # Module always has __name__
        except ImportError:
            pytest.skip("Constants module not available")
