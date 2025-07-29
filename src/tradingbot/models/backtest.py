"""
Backtest models for the Crypto Trading Bot.
This module contains models related to backtesting functionality.

Note: The main BacktestResult model is defined in strategy.py to maintain
domain cohesion. This file contains additional backtest-related models
if needed in the future.
"""

# Import the BacktestResult model from strategy module for convenience
from .strategy import BacktestResult

__all__ = ["BacktestResult"]

# Future backtest-related models can be added here
# For example:
# - BacktestConfiguration
# - BacktestMetrics
# - BacktestComparison
# - etc.
