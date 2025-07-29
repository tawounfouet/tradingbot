"""
Real-time strategy execution service.
Connects real market data to strategy evaluation and signal generation.
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Set

from src.backend.database import get_db
from src.backend.models.strategy import Strategy
from src.backend.models.user import User
from src.backend.services.real_market_data_service import (
    MarketDataPoint,
    real_market_service,
)
from src.backend.services.strategy_service import strategy_service
from src.strategies.registry import strategy_registry

logger = logging.getLogger(__name__)


@dataclass
class StrategySignal:
    """Strategy signal result."""

    strategy_id: str
    symbol: str
    signal: str  # 'BUY', 'SELL', 'HOLD'
    confidence: float
    timestamp: datetime
    price: float
    metadata: Dict


class RealTimeStrategyExecutor:
    """Executes strategies in real-time based on live market data."""

    def __init__(self):
        self.active_strategies: Dict[str, Strategy] = {}  # strategy_id -> Strategy
        self.monitored_symbols: Set[str] = set()
        self.signal_callbacks: List[callable] = []
        self.is_running = False

    async def start_strategy_execution(self, user_id: str, strategy_id: str) -> bool:
        """
        Start real-time execution for a strategy.

        Args:
            user_id: User ID who owns the strategy
            strategy_id: Strategy ID to execute

        Returns:
            bool: True if started successfully
        """
        try:
            db = next(get_db())

            # Get strategy from database
            strategy = (
                db.query(Strategy).filter_by(id=strategy_id, user_id=user_id).first()
            )

            if not strategy:
                logger.error(f"Strategy {strategy_id} not found for user {user_id}")
                return False

            # Load strategy implementation
            strategy_impl = strategy_registry.get_strategy(strategy.strategy_type)
            if not strategy_impl:
                logger.error(
                    f"Strategy implementation not found: {strategy.strategy_type}"
                )
                return False

            # Initialize strategy with parameters
            strategy_instance = strategy_impl(strategy.parameters)

            # Store active strategy
            self.active_strategies[strategy_id] = {
                "instance": strategy_instance,
                "config": strategy,
                "symbol": "BTCUSDT",  # Default symbol, can be configurable
                "last_signal": None,
                "last_execution": None,
            }

            # Start monitoring the required symbol
            symbol = "BTCUSDT"  # This should come from strategy config
            await self._ensure_symbol_monitoring(symbol)

            logger.info(f"Started real-time execution for strategy {strategy_id}")
            return True

        except Exception as e:
            logger.error(f"Error starting strategy execution: {e}")
            return False
        finally:
            if db:
                db.close()

    async def _ensure_symbol_monitoring(self, symbol: str):
        """Ensure we're monitoring a symbol for market data."""
        if symbol not in self.monitored_symbols:
            # Start market data stream
            success = await real_market_service.start_market_stream(symbol, "1m")
            if success:
                # Subscribe to market data updates
                real_market_service.subscribe_to_symbol(symbol, self._on_market_data)
                self.monitored_symbols.add(symbol)
                logger.info(f"Started monitoring {symbol}")
            else:
                logger.error(f"Failed to start monitoring {symbol}")

    def _on_market_data(self, data_point: MarketDataPoint):
        """Handle new market data by evaluating all active strategies."""
        try:
            # Evaluate all active strategies for this symbol
            for strategy_id, strategy_data in self.active_strategies.items():
                if strategy_data["symbol"] == data_point.symbol:
                    asyncio.create_task(
                        self._evaluate_strategy(strategy_id, strategy_data, data_point)
                    )

        except Exception as e:
            logger.error(f"Error handling market data: {e}")

    async def _evaluate_strategy(
        self, strategy_id: str, strategy_data: Dict, data_point: MarketDataPoint
    ):
        """Evaluate a single strategy against new market data."""
        try:
            strategy_instance = strategy_data["instance"]
            strategy_config = strategy_data["config"]

            # Get recent historical data for strategy evaluation
            historical_data = real_market_service.get_historical_data(
                data_point.symbol, "1m", limit=100
            )

            if len(historical_data) < 20:  # Minimum data required
                logger.debug(f"Insufficient data for strategy {strategy_id}")
                return

            # Convert to DataFrame format expected by strategies
            import pandas as pd

            df_data = pd.DataFrame(
                [
                    {
                        "timestamp": dp.timestamp,
                        "open": dp.open,
                        "high": dp.high,
                        "low": dp.low,
                        "close": dp.close,
                        "volume": dp.volume,
                    }
                    for dp in historical_data
                ]
            )
            df_data.set_index("timestamp", inplace=True)

            # Run strategy
            result = strategy_instance.run(df_data)

            if not result.empty:
                # Get the latest signal
                latest_signal = result.iloc[-1]
                signal_value = latest_signal.get("signal", 0)

                # Convert numeric signal to text
                if signal_value > 0.5:
                    signal = "BUY"
                elif signal_value < -0.5:
                    signal = "SELL"
                else:
                    signal = "HOLD"

                # Create signal object
                strategy_signal = StrategySignal(
                    strategy_id=strategy_id,
                    symbol=data_point.symbol,
                    signal=signal,
                    confidence=abs(signal_value),
                    timestamp=data_point.timestamp,
                    price=data_point.close,
                    metadata={
                        "strategy_type": strategy_config.strategy_type,
                        "parameters": strategy_config.parameters,
                        "volume": data_point.volume,
                    },
                )

                # Only process if signal changed
                if strategy_data["last_signal"] != signal:
                    strategy_data["last_signal"] = signal
                    strategy_data["last_execution"] = datetime.now()

                    logger.info(
                        f"Strategy {strategy_id} generated {signal} signal for {data_point.symbol} at ${data_point.close:.2f}"
                    )

                    # Notify signal callbacks
                    await self._notify_signal_callbacks(strategy_signal)

                    # Store signal in database (optional)
                    await self._store_signal(strategy_signal)

        except Exception as e:
            logger.error(f"Error evaluating strategy {strategy_id}: {e}")

    async def _notify_signal_callbacks(self, signal: StrategySignal):
        """Notify all registered signal callbacks."""
        for callback in self.signal_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(signal)
                else:
                    callback(signal)
            except Exception as e:
                logger.error(f"Error in signal callback: {e}")

    async def _store_signal(self, signal: StrategySignal):
        """Store signal in database for tracking."""
        try:
            # Here you would store the signal in your database
            # This could be a new SignalHistory table
            logger.debug(f"Signal stored: {signal.strategy_id} - {signal.signal}")

        except Exception as e:
            logger.error(f"Error storing signal: {e}")

    def add_signal_callback(self, callback: callable):
        """Add a callback to be notified of new signals."""
        self.signal_callbacks.append(callback)
        logger.info("Added signal callback")

    def remove_signal_callback(self, callback: callable):
        """Remove a signal callback."""
        if callback in self.signal_callbacks:
            self.signal_callbacks.remove(callback)
            logger.info("Removed signal callback")

    async def stop_strategy_execution(self, strategy_id: str) -> bool:
        """
        Stop real-time execution for a strategy.

        Args:
            strategy_id: Strategy ID to stop

        Returns:
            bool: True if stopped successfully
        """
        try:
            if strategy_id in self.active_strategies:
                del self.active_strategies[strategy_id]
                logger.info(f"Stopped strategy execution: {strategy_id}")

                # Check if we can stop monitoring symbols
                await self._cleanup_unused_symbols()
                return True

            return False

        except Exception as e:
            logger.error(f"Error stopping strategy execution: {e}")
            return False

    async def _cleanup_unused_symbols(self):
        """Stop monitoring symbols that are no longer needed."""
        used_symbols = {
            strategy_data["symbol"] for strategy_data in self.active_strategies.values()
        }

        symbols_to_remove = self.monitored_symbols - used_symbols

        for symbol in symbols_to_remove:
            real_market_service.stop_market_stream(symbol)
            self.monitored_symbols.remove(symbol)
            logger.info(f"Stopped monitoring unused symbol: {symbol}")

    async def stop_all_executions(self):
        """Stop all active strategy executions."""
        try:
            strategy_ids = list(self.active_strategies.keys())
            for strategy_id in strategy_ids:
                await self.stop_strategy_execution(strategy_id)

            # Stop all market data streams
            real_market_service.stop_all_streams()
            self.monitored_symbols.clear()

            logger.info("Stopped all strategy executions")

        except Exception as e:
            logger.error(f"Error stopping all executions: {e}")

    def get_active_strategies(self) -> List[str]:
        """Get list of actively executing strategy IDs."""
        return list(self.active_strategies.keys())

    def get_strategy_status(self, strategy_id: str) -> Optional[Dict]:
        """Get status information for a strategy."""
        if strategy_id in self.active_strategies:
            strategy_data = self.active_strategies[strategy_id]
            return {
                "strategy_id": strategy_id,
                "symbol": strategy_data["symbol"],
                "last_signal": strategy_data["last_signal"],
                "last_execution": strategy_data["last_execution"],
                "is_active": True,
            }
        return None


# Global instance
real_time_executor = RealTimeStrategyExecutor()


# Example signal handlers
async def example_signal_handler(signal: StrategySignal):
    """Example signal handler that could execute trades."""
    print(f"🚨 SIGNAL: {signal.signal} for {signal.symbol} at ${signal.price:.2f}")
    print(f"   Strategy: {signal.strategy_id}")
    print(f"   Confidence: {signal.confidence:.2f}")
    print(f"   Time: {signal.timestamp}")

    # Here you would implement actual trade execution
    # if signal.signal == 'BUY':
    #     await execute_buy_order(signal.symbol, signal.price)
    # elif signal.signal == 'SELL':
    #     await execute_sell_order(signal.symbol, signal.price)


def log_signal_handler(signal: StrategySignal):
    """Simple logging signal handler."""
    logger.info(
        f"Signal received: {signal.strategy_id} -> {signal.signal} for {signal.symbol}"
    )


# Example usage
async def example_real_time_execution():
    """Example of how to use the real-time strategy executor."""

    # Add signal handlers
    real_time_executor.add_signal_callback(example_signal_handler)
    real_time_executor.add_signal_callback(log_signal_handler)

    # Start executing a strategy (you'd get these IDs from your database)
    user_id = "example-user-id"
    strategy_id = "example-strategy-id"

    success = await real_time_executor.start_strategy_execution(user_id, strategy_id)
    if success:
        print(f"✅ Started real-time execution for strategy {strategy_id}")
    else:
        print(f"❌ Failed to start strategy execution")

    print(f"Active strategies: {real_time_executor.get_active_strategies()}")

    # Keep running
    try:
        while True:
            await asyncio.sleep(10)  # Check every 10 seconds

            # Print status
            for strategy_id in real_time_executor.get_active_strategies():
                status = real_time_executor.get_strategy_status(strategy_id)
                if status:
                    print(
                        f"Strategy {strategy_id}: {status['last_signal']} on {status['symbol']}"
                    )

    except KeyboardInterrupt:
        print("Stopping all executions...")
        await real_time_executor.stop_all_executions()


if __name__ == "__main__":
    # Test the real-time strategy executor
    asyncio.run(example_real_time_execution())
