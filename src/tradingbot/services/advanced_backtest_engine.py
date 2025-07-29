"""
Advanced backtesting engine for strategy evaluation.
Provides comprehensive backtesting with performance metrics and risk analysis.
"""

import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from src.backend.services.market_data_service import market_data_service
from src.strategies.registry import strategy_registry

logger = logging.getLogger(__name__)


@dataclass
class BacktestConfig:
    """Backtesting configuration."""

    strategy_type: str
    parameters: Dict
    symbol: str
    start_date: datetime
    end_date: datetime
    initial_capital: float = 10000.0
    commission: float = 0.001  # 0.1% commission
    slippage: float = 0.0005  # 0.05% slippage
    max_position_size: float = 1.0  # 100% of capital
    risk_free_rate: float = 0.02  # 2% annual risk-free rate


@dataclass
class Trade:
    """Individual trade record."""

    entry_time: datetime
    exit_time: datetime
    symbol: str
    side: str  # 'long' or 'short'
    entry_price: float
    exit_price: float
    quantity: float
    pnl: float
    commission_paid: float
    duration_hours: float


@dataclass
class BacktestResults:
    """Comprehensive backtesting results."""

    config: BacktestConfig

    # Performance metrics
    total_return: float
    annual_return: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    max_drawdown_duration: int  # days
    calmar_ratio: float

    # Trade statistics
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    avg_win: float
    avg_loss: float
    profit_factor: float
    avg_trade_duration_hours: float

    # Risk metrics
    volatility: float
    beta: float
    var_95: float  # Value at Risk 95%

    # Capital metrics
    initial_capital: float
    final_capital: float
    peak_capital: float

    # Time series data
    equity_curve: pd.Series
    drawdown_curve: pd.Series
    trades: List[Trade]

    # Additional metrics
    start_date: datetime
    end_date: datetime
    duration_days: int


class AdvancedBacktester:
    """Advanced backtesting engine with comprehensive analysis."""

    def __init__(self):
        self.market_service = market_data_service

    async def run_backtest(self, config: BacktestConfig) -> BacktestResults:
        """
        Run a comprehensive backtest.

        Args:
            config: Backtesting configuration

        Returns:
            BacktestResults: Comprehensive results
        """
        try:
            logger.info(
                f"Starting backtest for {config.strategy_type} on {config.symbol}"
            )

            # Get market data
            market_data = await self._get_market_data(config)
            if market_data.empty:
                raise ValueError("No market data available for the specified period")

            # Get strategy instance
            strategy_class = strategy_registry.get_strategy(config.strategy_type)
            if not strategy_class:
                raise ValueError(f"Strategy {config.strategy_type} not found")

            strategy = strategy_class(config.parameters)

            # Generate signals
            signals = strategy.run(market_data)

            # Execute backtest
            results = self._execute_backtest(config, market_data, signals)

            logger.info(f"Backtest completed. Total return: {results.total_return:.2%}")
            return results

        except Exception as e:
            logger.error(f"Error running backtest: {e}")
            raise

    async def _get_market_data(self, config: BacktestConfig) -> pd.DataFrame:
        """Get historical market data for backtesting."""
        try:
            # Calculate required data points
            days = (config.end_date - config.start_date).days
            # Add buffer for indicators that need historical data
            buffer_days = 50
            start_with_buffer = config.start_date - timedelta(days=buffer_days)

            # Get data from market service (simulated for now)
            data = self.market_service.get_historical_data(
                symbol=config.symbol,
                interval="1h",  # Use hourly data for more precision
                start_date=start_with_buffer,
                end_date=config.end_date,
                limit=days * 24 + buffer_days * 24,
            )

            if data.empty:
                logger.warning("No data from market service, generating simulated data")
                data = self._generate_simulated_data(config, start_with_buffer)

            # Filter to actual backtest period (keep buffer for indicator calculation)
            return data[data.index >= config.start_date - timedelta(days=30)]

        except Exception as e:
            logger.error(f"Error getting market data: {e}")
            # Fallback to simulated data
            return self._generate_simulated_data(
                config, config.start_date - timedelta(days=50)
            )

    def _generate_simulated_data(
        self, config: BacktestConfig, start_date: datetime
    ) -> pd.DataFrame:
        """Generate simulated market data for backtesting."""
        end_date = config.end_date
        hours = int((end_date - start_date).total_seconds() / 3600)

        # Generate realistic price movement
        np.random.seed(42)  # For reproducible results

        # Base price and volatility
        base_price = 50000 if "BTC" in config.symbol else 3000
        volatility = 0.02  # 2% hourly volatility

        # Generate price series with trend and noise
        returns = np.random.normal(0.0001, volatility, hours)  # Slight upward trend

        # Add some trend cycles
        trend_cycle = (
            np.sin(np.arange(hours) * 2 * np.pi / (24 * 7)) * 0.001
        )  # Weekly cycle
        returns += trend_cycle

        prices = base_price * np.cumprod(1 + returns)

        # Generate OHLCV data
        data = []
        timestamps = pd.date_range(start=start_date, periods=hours, freq="H")

        for i, (timestamp, close) in enumerate(zip(timestamps, prices)):
            # Generate realistic OHLC from close price
            volatility_factor = np.random.uniform(0.5, 1.5)
            high_low_range = close * volatility * volatility_factor

            high = close + np.random.uniform(0, high_low_range)
            low = close - np.random.uniform(0, high_low_range)

            if i == 0:
                open_price = close
            else:
                open_price = prices[i - 1] * np.random.uniform(0.999, 1.001)

            volume = np.random.uniform(100, 1000) * np.random.exponential(1)

            data.append(
                {
                    "open": open_price,
                    "high": max(open_price, high, close),
                    "low": min(open_price, low, close),
                    "close": close,
                    "volume": volume,
                }
            )

        df = pd.DataFrame(data, index=timestamps)
        return df

    def _execute_backtest(
        self, config: BacktestConfig, market_data: pd.DataFrame, signals: pd.DataFrame
    ) -> BacktestResults:
        """Execute the backtest simulation."""

        # Initialize portfolio state
        capital = config.initial_capital
        position = 0.0  # Current position size
        trades = []
        equity_curve = []

        # Track performance
        peak_capital = capital
        max_drawdown = 0.0
        drawdown_start = None
        max_dd_duration = 0

        # Merge market data with signals
        data = market_data.join(signals, how="left")
        data["signal"] = data["signal"].fillna(0)

        current_trade = None

        for timestamp, row in data.iterrows():
            price = row["close"]
            signal = row["signal"]

            # Calculate current equity
            if position != 0:
                position_value = position * price
                current_equity = capital + position_value - abs(position) * price
            else:
                current_equity = capital

            equity_curve.append(current_equity)

            # Update peak and drawdown
            if current_equity > peak_capital:
                peak_capital = current_equity
                drawdown_start = None
            else:
                if drawdown_start is None:
                    drawdown_start = timestamp

                current_drawdown = (peak_capital - current_equity) / peak_capital
                if current_drawdown > max_drawdown:
                    max_drawdown = current_drawdown
                    if drawdown_start:
                        dd_duration = (timestamp - drawdown_start).days
                        if dd_duration > max_dd_duration:
                            max_dd_duration = dd_duration

            # Process signals
            if signal > 0.5 and position <= 0:  # Buy signal
                if current_trade and position < 0:  # Close short position
                    trade = self._close_trade(
                        current_trade, timestamp, price, position, config
                    )
                    trades.append(trade)
                    capital += trade.pnl - trade.commission_paid

                # Open long position
                position_size = min(capital * config.max_position_size, capital * 0.95)
                quantity = position_size / price
                commission = position_size * config.commission

                position = quantity
                capital -= position_size + commission

                current_trade = {
                    "entry_time": timestamp,
                    "entry_price": price
                    * (1 + config.slippage),  # Account for slippage
                    "side": "long",
                    "quantity": quantity,
                    "commission": commission,
                }

            elif signal < -0.5 and position >= 0:  # Sell signal
                if current_trade and position > 0:  # Close long position
                    trade = self._close_trade(
                        current_trade, timestamp, price, position, config
                    )
                    trades.append(trade)
                    capital += trade.pnl - trade.commission_paid

                # Open short position (if allowed)
                position_size = min(capital * config.max_position_size, capital * 0.95)
                quantity = position_size / price
                commission = position_size * config.commission

                position = -quantity
                capital -= commission  # For short, we get cash upfront

                current_trade = {
                    "entry_time": timestamp,
                    "entry_price": price
                    * (1 - config.slippage),  # Account for slippage
                    "side": "short",
                    "quantity": quantity,
                    "commission": commission,
                }

        # Close any remaining position
        if current_trade and position != 0:
            final_price = market_data.iloc[-1]["close"]
            trade = self._close_trade(
                current_trade, market_data.index[-1], final_price, position, config
            )
            trades.append(trade)

        # Create equity curve series
        equity_series = pd.Series(equity_curve, index=data.index)

        # Calculate performance metrics
        results = self._calculate_metrics(config, equity_series, trades, market_data)

        return results

    def _close_trade(
        self,
        trade_info: Dict,
        exit_time: datetime,
        exit_price: float,
        position: float,
        config: BacktestConfig,
    ) -> Trade:
        """Close a trade and calculate P&L."""

        quantity = trade_info["quantity"]
        entry_price = trade_info["entry_price"]
        side = trade_info["side"]

        # Account for slippage on exit
        actual_exit_price = exit_price * (
            1 - config.slippage if side == "long" else 1 + config.slippage
        )

        # Calculate P&L
        if side == "long":
            pnl = quantity * (actual_exit_price - entry_price)
        else:  # short
            pnl = quantity * (entry_price - actual_exit_price)

        # Calculate commission
        exit_commission = abs(position) * actual_exit_price * config.commission
        total_commission = trade_info["commission"] + exit_commission

        # Calculate duration
        duration = (exit_time - trade_info["entry_time"]).total_seconds() / 3600

        return Trade(
            entry_time=trade_info["entry_time"],
            exit_time=exit_time,
            symbol=config.symbol,
            side=side,
            entry_price=entry_price,
            exit_price=actual_exit_price,
            quantity=quantity,
            pnl=pnl,
            commission_paid=total_commission,
            duration_hours=duration,
        )

    def _calculate_metrics(
        self,
        config: BacktestConfig,
        equity_curve: pd.Series,
        trades: List[Trade],
        market_data: pd.DataFrame,
    ) -> BacktestResults:
        """Calculate comprehensive performance metrics."""

        # Basic metrics
        initial_capital = config.initial_capital
        final_capital = equity_curve.iloc[-1]
        total_return = (final_capital - initial_capital) / initial_capital

        # Time-based metrics
        days = (config.end_date - config.start_date).days
        years = days / 365.25
        annual_return = (
            (1 + total_return) ** (1 / years) - 1 if years > 0 else total_return
        )

        # Drawdown calculation
        peak = equity_curve.expanding().max()
        drawdown = (equity_curve - peak) / peak
        max_drawdown = abs(drawdown.min())

        # Volatility and Sharpe ratio
        returns = equity_curve.pct_change().dropna()
        volatility = returns.std() * np.sqrt(365 * 24)  # Annualized volatility

        if volatility > 0:
            sharpe_ratio = (annual_return - config.risk_free_rate) / volatility
        else:
            sharpe_ratio = 0

        # Sortino ratio (using downside deviation)
        negative_returns = returns[returns < 0]
        if len(negative_returns) > 0:
            downside_deviation = negative_returns.std() * np.sqrt(365 * 24)
            sortino_ratio = (
                (annual_return - config.risk_free_rate) / downside_deviation
                if downside_deviation > 0
                else 0
            )
        else:
            sortino_ratio = float("inf") if annual_return > config.risk_free_rate else 0

        # Calmar ratio
        calmar_ratio = annual_return / max_drawdown if max_drawdown > 0 else 0

        # Trade statistics
        if trades:
            winning_trades = len([t for t in trades if t.pnl > 0])
            losing_trades = len([t for t in trades if t.pnl <= 0])
            win_rate = winning_trades / len(trades)

            wins = [t.pnl for t in trades if t.pnl > 0]
            losses = [t.pnl for t in trades if t.pnl <= 0]

            avg_win = np.mean(wins) if wins else 0
            avg_loss = np.mean(losses) if losses else 0

            gross_profit = sum(wins)
            gross_loss = abs(sum(losses))
            profit_factor = (
                gross_profit / gross_loss if gross_loss > 0 else float("inf")
            )

            avg_duration = np.mean([t.duration_hours for t in trades])
        else:
            winning_trades = losing_trades = 0
            win_rate = avg_win = avg_loss = profit_factor = avg_duration = 0

        # Risk metrics
        var_95 = np.percentile(returns, 5) if len(returns) > 0 else 0

        # Beta calculation (against benchmark - simplified as market volatility)
        market_returns = market_data["close"].pct_change().dropna()
        if len(returns) > 1 and len(market_returns) > 1:
            # Align returns
            aligned_returns = returns.reindex(
                market_returns.index, method="nearest"
            ).dropna()
            aligned_market = market_returns.reindex(
                aligned_returns.index, method="nearest"
            ).dropna()

            if len(aligned_returns) > 1 and len(aligned_market) > 1:
                covariance = np.cov(aligned_returns, aligned_market)[0, 1]
                market_variance = np.var(aligned_market)
                beta = covariance / market_variance if market_variance > 0 else 0
            else:
                beta = 0
        else:
            beta = 0

        # Drawdown duration
        in_drawdown = drawdown < 0
        if in_drawdown.any():
            drawdown_periods = []
            start = None
            for i, (timestamp, is_dd) in enumerate(in_drawdown.items()):
                if is_dd and start is None:
                    start = timestamp
                elif not is_dd and start is not None:
                    drawdown_periods.append((timestamp - start).days)
                    start = None

            if start is not None:  # Still in drawdown at end
                drawdown_periods.append((equity_curve.index[-1] - start).days)

            max_dd_duration = max(drawdown_periods) if drawdown_periods else 0
        else:
            max_dd_duration = 0

        return BacktestResults(
            config=config,
            total_return=total_return,
            annual_return=annual_return,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            max_drawdown=max_drawdown,
            max_drawdown_duration=max_dd_duration,
            calmar_ratio=calmar_ratio,
            total_trades=len(trades),
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            win_rate=win_rate,
            avg_win=avg_win,
            avg_loss=avg_loss,
            profit_factor=profit_factor,
            avg_trade_duration_hours=avg_duration,
            volatility=volatility,
            beta=beta,
            var_95=var_95,
            initial_capital=initial_capital,
            final_capital=final_capital,
            peak_capital=equity_curve.max(),
            equity_curve=equity_curve,
            drawdown_curve=drawdown,
            trades=trades,
            start_date=config.start_date,
            end_date=config.end_date,
            duration_days=days,
        )

    def generate_report(self, results: BacktestResults) -> str:
        """Generate a comprehensive backtest report."""

        report = f"""
# Backtest Report

## Strategy Configuration
- **Strategy**: {results.config.strategy_type}
- **Symbol**: {results.config.symbol}
- **Period**: {results.start_date.strftime('%Y-%m-%d')} to {results.end_date.strftime('%Y-%m-%d')} ({results.duration_days} days)
- **Initial Capital**: ${results.initial_capital:,.2f}
- **Parameters**: {results.config.parameters}

## Performance Summary
- **Total Return**: {results.total_return:.2%}
- **Annual Return**: {results.annual_return:.2%}
- **Final Capital**: ${results.final_capital:,.2f}
- **Peak Capital**: ${results.peak_capital:,.2f}

## Risk Metrics
- **Maximum Drawdown**: {results.max_drawdown:.2%}
- **Drawdown Duration**: {results.max_drawdown_duration} days
- **Volatility**: {results.volatility:.2%}
- **Sharpe Ratio**: {results.sharpe_ratio:.2f}
- **Sortino Ratio**: {results.sortino_ratio:.2f}
- **Calmar Ratio**: {results.calmar_ratio:.2f}
- **Beta**: {results.beta:.2f}
- **VaR (95%)**: {results.var_95:.2%}

## Trading Statistics
- **Total Trades**: {results.total_trades}
- **Winning Trades**: {results.winning_trades}
- **Losing Trades**: {results.losing_trades}
- **Win Rate**: {results.win_rate:.2%}
- **Average Win**: ${results.avg_win:.2f}
- **Average Loss**: ${results.avg_loss:.2f}
- **Profit Factor**: {results.profit_factor:.2f}
- **Average Trade Duration**: {results.avg_trade_duration_hours:.1f} hours

## Grade: {self._calculate_grade(results)}
"""
        return report

    def _calculate_grade(self, results: BacktestResults) -> str:
        """Calculate an overall grade for the strategy."""
        score = 0

        # Return component (30%)
        if results.annual_return > 0.20:
            score += 30
        elif results.annual_return > 0.10:
            score += 25
        elif results.annual_return > 0.05:
            score += 20
        elif results.annual_return > 0:
            score += 15

        # Risk component (25%)
        if results.sharpe_ratio > 2.0:
            score += 25
        elif results.sharpe_ratio > 1.5:
            score += 22
        elif results.sharpe_ratio > 1.0:
            score += 18
        elif results.sharpe_ratio > 0.5:
            score += 15
        elif results.sharpe_ratio > 0:
            score += 10

        # Drawdown component (25%)
        if results.max_drawdown < 0.05:
            score += 25
        elif results.max_drawdown < 0.10:
            score += 22
        elif results.max_drawdown < 0.15:
            score += 18
        elif results.max_drawdown < 0.25:
            score += 15
        elif results.max_drawdown < 0.35:
            score += 10

        # Trading component (20%)
        if results.win_rate > 0.60 and results.total_trades > 10:
            score += 20
        elif results.win_rate > 0.50 and results.total_trades > 5:
            score += 15
        elif results.win_rate > 0.40 and results.total_trades > 0:
            score += 10
        elif results.total_trades > 0:
            score += 5

        # Convert to letter grade
        if score >= 85:
            return "A+ (Excellent)"
        elif score >= 75:
            return "A (Very Good)"
        elif score >= 65:
            return "B (Good)"
        elif score >= 55:
            return "C (Average)"
        elif score >= 45:
            return "D (Below Average)"
        else:
            return "F (Poor)"


# Global instance
backtest_engine = AdvancedBacktester()


# Example usage
async def example_backtest():
    """Example of running a comprehensive backtest."""

    config = BacktestConfig(
        strategy_type="moving_average_crossover",
        parameters={
            "fast_period": 10,
            "slow_period": 20,
            "stop_loss": 0.02,
            "take_profit": 0.05,
        },
        symbol="BTCUSDT",
        start_date=datetime(2023, 1, 1),
        end_date=datetime(2023, 12, 31),
        initial_capital=10000.0,
        commission=0.001,
        max_position_size=0.95,
    )

    try:
        results = await backtest_engine.run_backtest(config)

        # Print report
        report = backtest_engine.generate_report(results)
        print(report)

        # Print some key metrics
        print(f"\n🎯 Key Results:")
        print(f"   Total Return: {results.total_return:.2%}")
        print(f"   Sharpe Ratio: {results.sharpe_ratio:.2f}")
        print(f"   Max Drawdown: {results.max_drawdown:.2%}")
        print(f"   Win Rate: {results.win_rate:.2%}")
        print(f"   Total Trades: {results.total_trades}")

        return results

    except Exception as e:
        print(f"❌ Backtest failed: {e}")
        return None


if __name__ == "__main__":
    import asyncio

    asyncio.run(example_backtest())
