"""Basic test to verify the package can be imported."""
import pytest


def test_tradingbot_import():
    """Test that the main tradingbot package can be imported."""
    try:
        import tradingbot

        assert hasattr(tradingbot, "__version__") or True  # Package exists
    except ImportError:
        pytest.fail("Could not import tradingbot package")


def test_main_module_import():
    """Test that the main module can be imported."""
    try:
        from tradingbot import main

        assert hasattr(main, "app")
    except ImportError:
        pytest.fail("Could not import tradingbot.main module")


def test_config_import():
    """Test that config modules can be imported."""
    try:
        from tradingbot.config import settings

        assert settings is not None
    except ImportError:
        pytest.fail("Could not import tradingbot.config.settings")


def test_models_import():
    """Test that model modules can be imported."""
    try:
        from tradingbot.models import base

        assert hasattr(base, "Base")
    except ImportError:
        pytest.fail("Could not import tradingbot.models.base")


def test_sample_calculation():
    """Simple test to ensure pytest is working correctly."""
    assert 2 + 2 == 4
    assert "hello" + " world" == "hello world"


@pytest.mark.parametrize(
    "input,expected",
    [
        (1, 2),
        (2, 3),
        (3, 4),
    ],
)
def test_parametrized(input, expected):
    """Test parametrized functionality."""
    assert input + 1 == expected
