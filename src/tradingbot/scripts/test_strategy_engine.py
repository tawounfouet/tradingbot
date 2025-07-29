#!/usr/bin/env python3
"""
Test script for the strategy engine.
Tests all strategy implementations and the registry system.
"""

import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

# Add the backend directory to the Python path
# sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "backend"))


# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from tradingbot.strategies import (
    BollingerBandsStrategy,
    MovingAverageCrossoverStrategy,
    MultiIndicatorStrategy,
    RSIReversalStrategy,
    get_strategy,
    list_available_strategies,
    registry,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def generate_sample_data(days: int = 100, start_price: float = 50000.0) -> pd.DataFrame:
    """
    Generate sample OHLCV data for testing.

    Args:
        days: Number of days of data
        start_price: Starting price

    Returns:
        DataFrame with OHLCV data
    """
    dates = pd.date_range(
        start=datetime.now() - timedelta(days=days), periods=days, freq="D"
    )

    # Generate price data with some trend and noise
    np.random.seed(42)  # For reproducible results

    # Create a price series with trend and volatility
    returns = np.random.normal(0.001, 0.02, days)  # Daily returns
    prices = [start_price]

    for ret in returns[1:]:
        new_price = prices[-1] * (1 + ret)
        prices.append(new_price)

    # Create OHLC data
    data = []
    for i, (date, close) in enumerate(zip(dates, prices)):
        # Add some intraday volatility
        volatility = 0.01  # 1% intraday volatility
        high = close * (1 + np.random.uniform(0, volatility))
        low = close * (1 - np.random.uniform(0, volatility))
        open_price = close * (1 + np.random.uniform(-volatility / 2, volatility / 2))

        # Ensure OHLC logic
        high = max(high, open_price, close)
        low = min(low, open_price, close)

        # Generate volume
        volume = np.random.uniform(1000000, 5000000)

        data.append(
            {
                "timestamp": date,
                "open": open_price,
                "high": high,
                "low": low,
                "close": close,
                "volume": volume,
            }
        )

    df = pd.DataFrame(data)
    df.set_index("timestamp", inplace=True)
    return df


def test_strategy_registry():
    """Test the strategy registry functionality."""
    logger.info("=== Testing Strategy Registry ===")

    # Test listing strategies
    strategies = list_available_strategies()
    logger.info(f"Available strategies: {strategies}")

    # Test getting strategy info
    for strategy_name in strategies:
        try:
            info = registry.get_strategy_info(strategy_name)
            logger.info(f"Strategy '{strategy_name}' info:")
            logger.info(f"  Class: {info['class']}")
            logger.info(f"  Module: {info['module']}")
            logger.info(f"  Metadata: {info['metadata']}")
        except Exception as e:
            logger.error(f"Failed to get info for strategy '{strategy_name}': {e}")

    logger.info("✅ Strategy registry test completed")


def test_strategy_execution(strategy_name: str, params: dict = None):
    """
    Test strategy execution with sample data.

    Args:
        strategy_name: Name of the strategy to test
        params: Strategy parameters
    """
    logger.info(f"=== Testing Strategy: {strategy_name} ===")

    try:
        # Create strategy instance
        strategy = get_strategy(strategy_name, params)
        logger.info(f"Created strategy instance: {strategy}")

        # Validate parameters
        is_valid, error_msg = strategy.validate_parameters()
        if not is_valid:
            logger.error(f"Parameter validation failed: {error_msg}")
            return False

        logger.info("✅ Parameters are valid")

        # Generate test data
        data = generate_sample_data(100)
        logger.info(f"Generated {len(data)} data points")

        # Run strategy
        start_time = datetime.now()
        results = strategy.run(data)
        execution_time = (datetime.now() - start_time).total_seconds()

        logger.info(f"Strategy executed in {execution_time:.3f} seconds")
        logger.info(f"Results shape: {results.shape}")

        # Analyze results
        if "signal" in results.columns:
            signals = results[results["signal"] != 0]
            buy_signals = len(signals[signals["signal"] == 1])
            sell_signals = len(signals[signals["signal"] == -1])

            logger.info(f"Generated {len(signals)} total signals:")
            logger.info(f"  Buy signals: {buy_signals}")
            logger.info(f"  Sell signals: {sell_signals}")

            if len(signals) > 0:
                logger.info("First few signals:")
                for idx, (timestamp, row) in enumerate(signals.head().iterrows()):
                    signal_type = "BUY" if row["signal"] == 1 else "SELL"
                    logger.info(f"  {timestamp}: {signal_type} @ {row['close']:.2f}")

        # Test strategy info
        info = strategy.get_strategy_info()
        logger.info(f"Strategy info: {info}")

        logger.info(f"✅ Strategy '{strategy_name}' test completed successfully")
        return True

    except Exception as e:
        logger.error(f"❌ Strategy '{strategy_name}' test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_all_strategies():
    """Test all available strategies."""
    logger.info("=== Testing All Strategies ===")

    # Test configurations for each strategy
    test_configs = {
        "moving_average_crossover": {
            "fast_period": 10,
            "slow_period": 20,
            "stop_loss": 0.02,
            "take_profit": 0.05,
        },
        "rsi_reversal": {
            "rsi_period": 14,
            "oversold_threshold": 30,
            "overbought_threshold": 70,
            "stop_loss": 0.03,
            "take_profit": 0.06,
        },
        "bollinger_bands": {
            "bb_period": 20,
            "bb_std": 2.0,
            "rsi_period": 14,
            "rsi_oversold": 30,
            "rsi_overbought": 70,
            "stop_loss": 0.025,
            "take_profit": 0.05,
        },
        "multi_indicator": {
            "rsi_period": 14,
            "rsi_oversold": 30,
            "rsi_overbought": 70,
            "macd_fast": 12,
            "macd_slow": 26,
            "macd_signal": 9,
            "bb_period": 20,
            "bb_std": 2.0,
            "volume_threshold": 1.2,
            "min_confirmations": 2,
            "stop_loss": 0.02,
            "take_profit": 0.04,
        },
    }

    strategies = list_available_strategies()
    passed = 0
    failed = 0

    for strategy_name in strategies:
        params = test_configs.get(strategy_name, {})
        if test_strategy_execution(strategy_name, params):
            passed += 1
        else:
            failed += 1

    logger.info(f"=== Test Summary ===")
    logger.info(f"Strategies tested: {len(strategies)}")
    logger.info(f"Passed: {passed}")
    logger.info(f"Failed: {failed}")

    return failed == 0


def test_parameter_validation():
    """Test parameter validation for strategies."""
    logger.info("=== Testing Parameter Validation ===")

    # Test with invalid parameters
    test_cases = [
        {
            "strategy": "moving_average_crossover",
            "params": {"fast_period": 30, "slow_period": 20},  # fast >= slow
            "should_fail": True,
        },
        {
            "strategy": "rsi_reversal",
            "params": {"rsi_period": -5},  # negative period
            "should_fail": True,
        },
        {
            "strategy": "bollinger_bands",
            "params": {"bb_std": -1.0},  # negative std
            "should_fail": True,
        },
        {
            "strategy": "moving_average_crossover",
            "params": {"fast_period": 10, "slow_period": 20, "stop_loss": 0.02},
            "should_fail": False,
        },
    ]

    for i, test_case in enumerate(test_cases):
        logger.info(
            f"Test case {i+1}: {test_case['strategy']} with {test_case['params']}"
        )

        try:
            is_valid, error_msg = registry.validate_strategy(
                test_case["strategy"], test_case["params"]
            )

            if test_case["should_fail"]:
                if is_valid:
                    logger.error(f"❌ Expected validation to fail, but it passed")
                else:
                    logger.info(f"✅ Correctly failed validation: {error_msg}")
            else:
                if is_valid:
                    logger.info(f"✅ Correctly passed validation")
                else:
                    logger.error(
                        f"❌ Expected validation to pass, but it failed: {error_msg}"
                    )

        except Exception as e:
            logger.error(f"❌ Validation test failed with exception: {e}")

    logger.info("✅ Parameter validation test completed")


def main():
    """Main test function."""
    logger.info("🚀 Starting Strategy Engine Tests")

    try:
        # Test registry
        test_strategy_registry()

        # Test parameter validation
        test_parameter_validation()

        # Test all strategies
        success = test_all_strategies()

        if success:
            logger.info("🎉 All tests passed successfully!")
            return 0
        else:
            logger.error("💥 Some tests failed!")
            return 1

    except Exception as e:
        logger.error(f"💥 Test execution failed: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
