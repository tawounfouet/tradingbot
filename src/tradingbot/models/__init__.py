"""
Models package for the Crypto Trading Bot.
Contains all SQLAlchemy models organized by domain.
"""

# Import backtest models (convenience import)
from .backtest import (
    BacktestResult as BacktestResultAlias,  # Already imported from strategy
)

# Import base classes
from .base import (
    AuditMixin,
    Base,
    BaseAuditModel,
    BaseFullAuditModel,
    BaseModel,
    BaseModelWithSoftDelete,
    ModelRegistry,
    SoftDeleteMixin,
    TimestampMixin,
    UUIDMixin,
    bulk_create_or_update,
    get_or_create,
    register_model,
)

# Import market data models
from .market import (
    MarketData,
)

# Import strategy domain models
from .strategy import (
    BacktestResult,
    Strategy,
    StrategyDeployment,
    StrategyState,
    TradingSession,
)

# Import trading domain models
from .trading import (
    Order,
    OrderFill,
    Transaction,
)

# Import user domain models
from .user import (
    User,
    UserAccount,
    UserSession,
    UserSettings,
)

# Export all models
__all__ = [
    # Base classes
    "Base",
    "BaseModel",
    "BaseModelWithSoftDelete",
    "BaseAuditModel",
    "BaseFullAuditModel",
    "UUIDMixin",
    "TimestampMixin",
    "SoftDeleteMixin",
    "AuditMixin",
    "ModelRegistry",
    "register_model",
    "get_or_create",
    "bulk_create_or_update",
    # User domain
    "User",
    "UserSession",
    "UserAccount",
    "UserSettings",
    # Strategy domain
    "Strategy",
    "StrategyDeployment",
    "StrategyState",
    "TradingSession",
    "BacktestResult",
    # Trading domain
    "Order",
    "OrderFill",
    "Transaction",
    # Market data
    "MarketData",
]

# Model registry for introspection
ALL_MODELS = [
    User,
    UserSession,
    UserAccount,
    UserSettings,
    Strategy,
    StrategyDeployment,
    StrategyState,
    TradingSession,
    BacktestResult,
    Order,
    OrderFill,
    Transaction,
    MarketData,
]

# Models organized by domain
USER_MODELS = [User, UserSession, UserAccount, UserSettings]
STRATEGY_MODELS = [
    Strategy,
    StrategyDeployment,
    StrategyState,
    TradingSession,
    BacktestResult,
]
TRADING_MODELS = [Order, OrderFill, Transaction]
MARKET_MODELS = [MarketData]


# Create all tables function
def create_all_tables(engine):
    """
    Create all tables in the database.

    Args:
        engine: SQLAlchemy engine
    """
    Base.metadata.create_all(bind=engine)


def drop_all_tables(engine):
    """
    Drop all tables in the database.

    Args:
        engine: SQLAlchemy engine
    """
    Base.metadata.drop_all(bind=engine)


def get_model_by_table_name(table_name: str):
    """
    Get model class by table name.

    Args:
        table_name: Name of the table

    Returns:
        Model class or None
    """
    for model in ALL_MODELS:
        if hasattr(model, "__tablename__") and model.__tablename__ == table_name:
            return model
    return None


def get_models_by_domain(domain: str) -> list:
    """
    Get models by domain name.

    Args:
        domain: Domain name ('user', 'strategy', 'trading', 'market')

    Returns:
        List of model classes
    """
    domain_map = {
        "user": USER_MODELS,
        "strategy": STRATEGY_MODELS,
        "trading": TRADING_MODELS,
        "market": MARKET_MODELS,
    }
    return domain_map.get(domain, [])


# Validation function
def validate_model_relationships():
    """
    Validate that all model relationships are properly defined.
    This function can be called during application startup.

    Returns:
        bool: True if all relationships are valid
    """
    try:
        # Create a test engine to validate relationships
        from sqlalchemy import create_engine

        engine = create_engine("sqlite:///:memory:")

        # Try to create all tables
        create_all_tables(engine)

        return True
    except Exception as e:
        print(f"Model validation error: {e}")
        return False
