"""
Real-time market data service using Binance WebSockets.
Replaces the simulated market data service with live data feeds.
"""

import asyncio
import json
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Dict, List, Optional

from sqlalchemy.orm import Session

from src.backend.database import get_db
from src.backend.models.market_data import MarketData
from src.tools.client_binance import ClientBinance

logger = logging.getLogger(__name__)


@dataclass
class MarketDataPoint:
    """Market data point structure."""

    symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    interval: str
    exchange: str = "binance"


class RealMarketDataService:
    """Real-time market data service using Binance WebSockets."""

    def __init__(self):
        self.client = ClientBinance()
        self.active_streams: Dict[str, str] = {}  # symbol -> connection_key
        self.subscribers: Dict[str, List[Callable]] = {}  # symbol -> callbacks
        self.latest_data: Dict[str, MarketDataPoint] = {}

    async def start_market_stream(self, symbol: str, interval: str = "1m") -> bool:
        """
        Start a real-time market data stream for a symbol.

        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            interval: Kline interval (1m, 5m, 1h, etc.)

        Returns:
            bool: True if stream started successfully
        """
        try:

            def handle_kline_message(msg):
                """Handle incoming kline data."""
                if msg.get("e") == "error":
                    logger.error(f"WebSocket error for {symbol}: {msg.get('m')}")
                    return

                kline = msg.get("k", {})
                is_closed = kline.get("x", False)

                if is_closed:  # Only process closed candles
                    data_point = MarketDataPoint(
                        symbol=symbol,
                        timestamp=datetime.fromtimestamp(kline.get("t", 0) / 1000),
                        open=float(kline.get("o", 0)),
                        high=float(kline.get("h", 0)),
                        low=float(kline.get("l", 0)),
                        close=float(kline.get("c", 0)),
                        volume=float(kline.get("v", 0)),
                        interval=interval,
                    )

                    # Store latest data
                    self.latest_data[symbol] = data_point

                    # Notify subscribers
                    self._notify_subscribers(symbol, data_point)

                    # Store in database
                    self._store_market_data(data_point)

                    logger.info(
                        f"New {symbol} candle: {data_point.close} at {data_point.timestamp}"
                    )

            # Start WebSocket stream
            conn_key = self.client.start_kline_socket(
                symbol=symbol, interval=interval, callback=handle_kline_message
            )

            if conn_key:
                self.active_streams[symbol] = conn_key
                logger.info(
                    f"Started market stream for {symbol} with interval {interval}"
                )
                return True
            else:
                logger.error(f"Failed to start market stream for {symbol}")
                return False

        except Exception as e:
            logger.error(f"Error starting market stream for {symbol}: {e}")
            return False

    def subscribe_to_symbol(
        self, symbol: str, callback: Callable[[MarketDataPoint], None]
    ):
        """
        Subscribe to market data updates for a symbol.

        Args:
            symbol: Trading pair to subscribe to
            callback: Function to call when new data arrives
        """
        if symbol not in self.subscribers:
            self.subscribers[symbol] = []

        self.subscribers[symbol].append(callback)
        logger.info(f"Added subscriber for {symbol}")

        # If we have latest data, send it immediately
        if symbol in self.latest_data:
            callback(self.latest_data[symbol])

    def unsubscribe_from_symbol(
        self, symbol: str, callback: Callable[[MarketDataPoint], None]
    ):
        """
        Unsubscribe from market data updates for a symbol.

        Args:
            symbol: Trading pair to unsubscribe from
            callback: Callback function to remove
        """
        if symbol in self.subscribers and callback in self.subscribers[symbol]:
            self.subscribers[symbol].remove(callback)
            logger.info(f"Removed subscriber for {symbol}")

    def _notify_subscribers(self, symbol: str, data_point: MarketDataPoint):
        """Notify all subscribers of new data."""
        if symbol in self.subscribers:
            for callback in self.subscribers[symbol]:
                try:
                    callback(data_point)
                except Exception as e:
                    logger.error(f"Error notifying subscriber for {symbol}: {e}")

    def _store_market_data(self, data_point: MarketDataPoint):
        """Store market data in database."""
        try:
            db = next(get_db())

            # Check if data already exists
            existing = (
                db.query(MarketData)
                .filter_by(
                    symbol=data_point.symbol,
                    exchange=data_point.exchange,
                    interval_timeframe=data_point.interval,
                    open_time=data_point.timestamp,
                )
                .first()
            )

            if not existing:
                market_data = MarketData(
                    symbol=data_point.symbol,
                    exchange=data_point.exchange,
                    interval_timeframe=data_point.interval,
                    open_time=data_point.timestamp,
                    open_price=data_point.open,
                    high_price=data_point.high,
                    low_price=data_point.low,
                    close_price=data_point.close,
                    volume=data_point.volume,
                    close_time=data_point.timestamp,  # Simplified for now
                )

                db.add(market_data)
                db.commit()
                logger.debug(f"Stored market data for {data_point.symbol}")

        except Exception as e:
            logger.error(f"Error storing market data: {e}")
        finally:
            if db:
                db.close()

    def get_latest_price(self, symbol: str) -> Optional[float]:
        """
        Get the latest price for a symbol.

        Args:
            symbol: Trading pair

        Returns:
            Latest close price or None if not available
        """
        if symbol in self.latest_data:
            return self.latest_data[symbol].close
        return None

    def get_historical_data(
        self, symbol: str, interval: str, limit: int = 100
    ) -> List[MarketDataPoint]:
        """
        Get historical market data from Binance API.

        Args:
            symbol: Trading pair
            interval: Kline interval
            limit: Number of data points to retrieve

        Returns:
            List of historical market data points
        """
        try:
            klines = self.client.get_historical_klines(
                symbol=symbol, interval=interval, start_str=f"{limit} minutes ago UTC"
            )

            data_points = []
            for kline in klines:
                data_point = MarketDataPoint(
                    symbol=symbol,
                    timestamp=datetime.fromtimestamp(int(kline[0]) / 1000),
                    open=float(kline[1]),
                    high=float(kline[2]),
                    low=float(kline[3]),
                    close=float(kline[4]),
                    volume=float(kline[5]),
                    interval=interval,
                )
                data_points.append(data_point)

            return data_points

        except Exception as e:
            logger.error(f"Error getting historical data for {symbol}: {e}")
            return []

    def stop_market_stream(self, symbol: str) -> bool:
        """
        Stop market data stream for a symbol.

        Args:
            symbol: Trading pair

        Returns:
            bool: True if stream stopped successfully
        """
        try:
            if symbol in self.active_streams:
                conn_key = self.active_streams[symbol]
                self.client.stop_socket(conn_key)
                del self.active_streams[symbol]

                # Clean up subscribers
                if symbol in self.subscribers:
                    del self.subscribers[symbol]

                # Clean up latest data
                if symbol in self.latest_data:
                    del self.latest_data[symbol]

                logger.info(f"Stopped market stream for {symbol}")
                return True

            return False

        except Exception as e:
            logger.error(f"Error stopping market stream for {symbol}: {e}")
            return False

    def stop_all_streams(self):
        """Stop all active market data streams."""
        try:
            symbols = list(self.active_streams.keys())
            for symbol in symbols:
                self.stop_market_stream(symbol)

            # Stop all WebSocket connections
            self.client.stop_all_sockets()

            logger.info("Stopped all market data streams")

        except Exception as e:
            logger.error(f"Error stopping all streams: {e}")

    def get_active_symbols(self) -> List[str]:
        """Get list of symbols with active streams."""
        return list(self.active_streams.keys())


# Global instance
real_market_service = RealMarketDataService()


# Example usage functions for testing
async def example_real_time_integration():
    """Example of how to integrate real-time data with strategies."""

    def on_new_data(data_point: MarketDataPoint):
        """Callback for new market data."""
        print(
            f"New data for {data_point.symbol}: Price=${data_point.close:.2f}, Volume={data_point.volume:.2f}"
        )

        # Here you would trigger strategy evaluation
        # strategy_service.evaluate_strategies(data_point.symbol, data_point)

    # Start streams for multiple symbols
    symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]

    for symbol in symbols:
        success = await real_market_service.start_market_stream(symbol, "1m")
        if success:
            real_market_service.subscribe_to_symbol(symbol, on_new_data)
            print(f"✅ Started real-time stream for {symbol}")
        else:
            print(f"❌ Failed to start stream for {symbol}")

    print(f"Active streams: {real_market_service.get_active_symbols()}")

    # Keep running to receive data
    # In a real application, this would be managed by the main application loop
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("Stopping all streams...")
        real_market_service.stop_all_streams()


if __name__ == "__main__":
    # Test the real-time market data service
    asyncio.run(example_real_time_integration())
