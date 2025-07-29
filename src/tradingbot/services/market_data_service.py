"""
Market data service for handling market data operations.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class MarketDataService:
    """
    Service for handling market data operations.

    In a real implementation, this would connect to external APIs
    like Binance, fetch real market data, and handle caching.
    For now, it provides simulated data for testing.
    """

    def __init__(self):
        self.data_cache = {}

    async def get_historical_data(
        self,
        symbol: str,
        timeframe: str,
        start_date: datetime,
        end_date: datetime,
        limit: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Get historical market data.

        Args:
            symbol: Trading symbol (e.g., 'BTCUSDT')
            timeframe: Timeframe (e.g., '1h', '4h', '1d')
            start_date: Start date
            end_date: End date
            limit: Maximum number of records

        Returns:
            DataFrame with OHLCV data
        """
        logger.info(
            f"Getting historical data for {symbol} ({timeframe}) from {start_date} to {end_date}"
        )

        # For testing, generate simulated data
        return self._generate_simulated_data(
            symbol, timeframe, start_date, end_date, limit
        )

    async def get_latest_data(
        self, symbol: str, timeframe: str, periods: int = 100
    ) -> pd.DataFrame:
        """
        Get latest market data.

        Args:
            symbol: Trading symbol
            timeframe: Timeframe
            periods: Number of periods to fetch

        Returns:
            DataFrame with OHLCV data
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=periods)

        return await self.get_historical_data(
            symbol, timeframe, start_date, end_date, periods
        )

    def _generate_simulated_data(
        self,
        symbol: str,
        timeframe: str,
        start_date: datetime,
        end_date: datetime,
        limit: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Generate simulated market data for testing.

        Args:
            symbol: Trading symbol
            timeframe: Timeframe
            start_date: Start date
            end_date: End date
            limit: Maximum number of records

        Returns:
            DataFrame with OHLCV data
        """
        # Convert timeframe to pandas frequency
        freq_map = {
            "1m": "1T",
            "5m": "5T",
            "15m": "15T",
            "30m": "30T",
            "1h": "1H",
            "4h": "4H",
            "1d": "1D",
            "1w": "1W",
        }

        freq = freq_map.get(timeframe, "1H")

        # Generate date range
        dates = pd.date_range(start=start_date, end=end_date, freq=freq)

        if limit and len(dates) > limit:
            dates = dates[-limit:]

        # Base price (varies by symbol)
        base_prices = {
            "BTCUSDT": 45000,
            "ETHUSDT": 3000,
            "ADAUSDT": 0.5,
            "SOLUSDT": 100,
            "DOTUSDT": 8,
        }

        base_price = base_prices.get(symbol, 50000)

        # Generate price series with realistic characteristics
        np.random.seed(hash(symbol) % 2**32)  # Consistent seed per symbol

        # Create returns with some autocorrelation and volatility clustering
        n_periods = len(dates)
        returns = np.random.normal(0, 0.02, n_periods)  # Base volatility

        # Add trend component
        trend = np.linspace(-0.1, 0.1, n_periods) * np.random.choice([-1, 1])
        returns += trend / n_periods

        # Add volatility clustering
        volatility = np.abs(np.random.normal(0.02, 0.005, n_periods))
        for i in range(1, n_periods):
            volatility[i] = 0.1 * volatility[i] + 0.9 * volatility[i - 1]

        returns = returns * volatility

        # Generate price series
        prices = [base_price]
        for ret in returns[1:]:
            new_price = prices[-1] * (1 + ret)
            prices.append(max(new_price, 0.01))  # Prevent negative prices

        # Create OHLCV data
        data = []
        for i, (date, close) in enumerate(zip(dates, prices)):
            # Intraday volatility based on timeframe
            intraday_vol = {
                "1m": 0.001,
                "5m": 0.002,
                "15m": 0.003,
                "30m": 0.005,
                "1h": 0.008,
                "4h": 0.015,
                "1d": 0.025,
                "1w": 0.05,
            }.get(timeframe, 0.01)

            # Generate OHLC
            open_price = close * (
                1 + np.random.uniform(-intraday_vol / 2, intraday_vol / 2)
            )
            high = max(open_price, close) * (1 + np.random.uniform(0, intraday_vol))
            low = min(open_price, close) * (1 - np.random.uniform(0, intraday_vol))

            # Ensure OHLC logic
            high = max(high, open_price, close)
            low = min(low, open_price, close)

            # Generate volume (higher volume during high volatility)
            base_volume = {
                "BTCUSDT": 1e9,
                "ETHUSDT": 5e8,
                "ADAUSDT": 1e8,
                "SOLUSDT": 1e7,
                "DOTUSDT": 1e7,
            }.get(symbol, 1e8)

            volume_multiplier = (
                1 + abs(returns[i]) * 10
            )  # Higher volume during big moves
            volume = base_volume * volume_multiplier * np.random.uniform(0.5, 2.0)

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
        df = df.sort_index()

        logger.info(f"Generated {len(df)} data points for {symbol}")
        return df

    async def get_available_symbols(self) -> List[str]:
        """
        Get list of available trading symbols.

        Returns:
            List of available symbols
        """
        # Return a list of common crypto pairs for testing
        return [
            "BTCUSDT",
            "ETHUSDT",
            "ADAUSDT",
            "SOLUSDT",
            "DOTUSDT",
            "LINKUSDT",
            "MATICUSDT",
            "AVAXUSDT",
        ]

    async def get_symbol_info(self, symbol: str) -> Dict[str, Any]:
        """
        Get information about a trading symbol.

        Args:
            symbol: Trading symbol

        Returns:
            Symbol information
        """
        symbol_info = {
            "BTCUSDT": {
                "base_asset": "BTC",
                "quote_asset": "USDT",
                "price_precision": 2,
                "quantity_precision": 6,
                "min_quantity": 0.00001,
                "min_notional": 10.0,
            },
            "ETHUSDT": {
                "base_asset": "ETH",
                "quote_asset": "USDT",
                "price_precision": 2,
                "quantity_precision": 5,
                "min_quantity": 0.0001,
                "min_notional": 10.0,
            },
            "ADAUSDT": {
                "base_asset": "ADA",
                "quote_asset": "USDT",
                "price_precision": 4,
                "quantity_precision": 1,
                "min_quantity": 1.0,
                "min_notional": 10.0,
            },
        }

        return symbol_info.get(
            symbol,
            {
                "base_asset": symbol.replace("USDT", ""),
                "quote_asset": "USDT",
                "price_precision": 4,
                "quantity_precision": 4,
                "min_quantity": 0.001,
                "min_notional": 10.0,
            },
        )

    async def validate_symbol(self, symbol: str) -> bool:
        """
        Validate if a symbol is available for trading.

        Args:
            symbol: Trading symbol

        Returns:
            True if symbol is valid
        """
        available_symbols = await self.get_available_symbols()
        return symbol in available_symbols
