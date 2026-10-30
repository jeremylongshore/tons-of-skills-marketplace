#!/usr/bin/env python3
"""
Performance and Risk Metrics for Backtesting
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional
from math import isfinite
from dataclasses import dataclass


@dataclass
class Trade:
    """Represents a completed trade."""

    entry_time: pd.Timestamp
    exit_time: pd.Timestamp
    entry_price: float
    exit_price: float
    direction: str  # "long" or "short"
    size: float
    pnl: float = 0.0
    pnl_pct: float = 0.0
    duration: pd.Timedelta = None

    def __post_init__(self):
        if self.direction == "long":
            self.pnl = (self.exit_price - self.entry_price) * self.size
            self.pnl_pct = (self.exit_price - self.entry_price) / self.entry_price * 100
        else:
            self.pnl = (self.entry_price - self.exit_price) * self.size
            self.pnl_pct = (self.entry_price - self.exit_price) / self.entry_price * 100
        self.duration = self.exit_time - self.entry_time


@dataclass
class BacktestResult:
    """Complete backtest results."""

    strategy: str
    symbol: str
    start_date: pd.Timestamp
    end_date: pd.Timestamp
    initial_capital: float
    final_capital: float
    trades: List[Trade]
    equity_curve: pd.Series
    parameters: Dict[str, Any]

    # Performance metrics
    total_return: float = 0.0
    cagr: float = 0.0
    sharpe_ratio: float = 0.0
    sortino_ratio: float = 0.0
    calmar_ratio: float = 0.0

    # Risk metrics
    max_drawdown: float = 0.0
    max_drawdown_duration: int = 0
    volatility: float = 0.0
    var_95: float = 0.0
    cvar_95: float = 0.0
    ulcer_index: float = 0.0

    # Trade statistics
    total_trades: int = 0
    win_rate: float = 0.0
    profit_factor: Optional[float] = None  # No observed losses: ratio is undefined.
    avg_win: float = 0.0
    avg_loss: float = 0.0
    expectancy: float = 0.0
    max_consecutive_wins: int = 0
    max_consecutive_losses: int = 0
    avg_trade_duration: str = ""


def calculate_returns(equity_curve: pd.Series) -> pd.Series:
    """Calculate daily returns from equity curve."""
    return equity_curve.pct_change().dropna()


def calculate_total_return(initial: float, final: float) -> float:
    """Calculate total return percentage."""
    return ((final - initial) / initial) * 100


def calculate_cagr(initial: float, final: float, years: float) -> float:
    """Calculate Compound Annual Growth Rate."""
    if years <= 0 or initial <= 0:
        return 0.0
    return ((final / initial) ** (1 / years) - 1) * 100


def calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.02) -> float:
    """Calculate annualized Sharpe Ratio.

    Sharpe = (Return - Risk Free Rate) / Volatility
    """
    if len(returns) < 2 or returns.std() == 0:
        return 0.0

    # Annualize
    annual_return = returns.mean() * 252
    annual_vol = returns.std() * np.sqrt(252)

    return (annual_return - risk_free_rate) / annual_vol


def calculate_sortino_ratio(returns: pd.Series, risk_free_rate: float = 0.02) -> float:
    """Calculate Sortino Ratio (uses downside deviation only)."""
    if len(returns) < 2:
        return 0.0

    downside_returns = returns[returns < 0]
    if len(downside_returns) == 0 or downside_returns.std() == 0:
        return float("inf") if returns.mean() > 0 else 0.0

    annual_return = returns.mean() * 252
    downside_std = downside_returns.std() * np.sqrt(252)

    return (annual_return - risk_free_rate) / downside_std


def calculate_max_drawdown(equity_curve: pd.Series) -> tuple:
    """Calculate maximum drawdown and its duration.

    Returns: (max_drawdown_pct, max_drawdown_duration_days)
    """
    if len(equity_curve) < 2:
        return 0.0, 0

    rolling_max = equity_curve.expanding().max()
    drawdowns = (equity_curve - rolling_max) / rolling_max * 100

    max_dd = drawdowns.min()

    # Calculate duration
    in_drawdown = drawdowns < 0
    if not in_drawdown.any():
        return 0.0, 0

    # Find longest drawdown period
    drawdown_periods = []
    start = None
    for i, is_dd in enumerate(in_drawdown):
        if is_dd and start is None:
            start = i
        elif not is_dd and start is not None:
            drawdown_periods.append(i - start)
            start = None
    if start is not None:
        drawdown_periods.append(len(in_drawdown) - start)

    max_duration = max(drawdown_periods) if drawdown_periods else 0

    return max_dd, max_duration


def calculate_calmar_ratio(cagr: float, max_drawdown: float) -> float:
    """Calculate Calmar Ratio = CAGR / |Max Drawdown|."""
    if max_drawdown == 0:
        return 0.0
    return cagr / abs(max_drawdown)


def calculate_var(returns: pd.Series, confidence: float = 0.95) -> float:
    """Calculate Value at Risk at given confidence level."""
    if len(returns) < 10:
        return 0.0
    return np.percentile(returns, (1 - confidence) * 100)


def calculate_cvar(returns: pd.Series, confidence: float = 0.95) -> float:
    """Calculate Conditional VaR (Expected Shortfall)."""
    var = calculate_var(returns, confidence)
    return returns[returns <= var].mean() if len(returns[returns <= var]) > 0 else var


def calculate_volatility(returns: pd.Series) -> float:
    """Calculate annualized volatility."""
    return returns.std() * np.sqrt(252) * 100


def calculate_ulcer_index(equity_curve: pd.Series) -> float:
    """Calculate Ulcer Index (duration-weighted drawdown)."""
    if len(equity_curve) < 2:
        return 0.0

    rolling_max = equity_curve.expanding().max()
    drawdowns = ((equity_curve - rolling_max) / rolling_max * 100) ** 2

    return np.sqrt(drawdowns.mean())


def calculate_trade_stats(trades: List[Trade]) -> Dict[str, Any]:
    """Calculate trade statistics."""
    if not trades:
        return {
            "total_trades": 0,
            "win_rate": 0.0,
            "profit_factor": None,
            "avg_win": 0.0,
            "avg_loss": 0.0,
            "expectancy": 0.0,
            "max_consecutive_wins": 0,
            "max_consecutive_losses": 0,
            "avg_trade_duration": "0d",
        }

    wins = [t for t in trades if t.pnl > 0]
    losses = [t for t in trades if t.pnl < 0]

    total_trades = len(trades)
    win_rate = len(wins) / total_trades * 100 if total_trades > 0 else 0

    gross_profit = sum(t.pnl for t in wins) if wins else 0
    gross_loss = abs(sum(t.pnl for t in losses)) if losses else 0
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else None

    avg_win = np.mean([t.pnl for t in wins]) if wins else 0
    avg_loss = np.mean([t.pnl for t in losses]) if losses else 0

    # Expectancy = (Win% * Avg Win) - (Loss% * |Avg Loss|)
    expectancy = (win_rate / 100 * avg_win) - ((1 - win_rate / 100) * abs(avg_loss))

    # Consecutive wins/losses
    max_consec_wins = 0
    max_consec_losses = 0
    current_wins = 0
    current_losses = 0

    for trade in trades:
        if trade.pnl > 0:
            current_wins += 1
            current_losses = 0
            max_consec_wins = max(max_consec_wins, current_wins)
        else:
            current_losses += 1
            current_wins = 0
            max_consec_losses = max(max_consec_losses, current_losses)

    # Average duration
    durations = [t.duration.days for t in trades if t.duration]
    avg_duration = f"{np.mean(durations):.1f}d" if durations else "0d"

    return {
        "total_trades": total_trades,
        "win_rate": win_rate,
        "profit_factor": profit_factor,
        "avg_win": avg_win,
        "avg_loss": avg_loss,
        "expectancy": expectancy,
        "max_consecutive_wins": max_consec_wins,
        "max_consecutive_losses": max_consec_losses,
        "avg_trade_duration": avg_duration,
    }


def calculate_all_metrics(result: BacktestResult) -> BacktestResult:
    """Calculate all performance and risk metrics for a backtest result."""

    returns = calculate_returns(result.equity_curve)
    years = (result.end_date - result.start_date).days / 365.25

    # Performance metrics
    result.total_return = calculate_total_return(result.initial_capital, result.final_capital)
    result.cagr = calculate_cagr(result.initial_capital, result.final_capital, years)
    result.sharpe_ratio = calculate_sharpe_ratio(returns)
    result.sortino_ratio = calculate_sortino_ratio(returns)

    # Risk metrics
    result.max_drawdown, result.max_drawdown_duration = calculate_max_drawdown(result.equity_curve)
    result.calmar_ratio = calculate_calmar_ratio(result.cagr, result.max_drawdown)
    result.volatility = calculate_volatility(returns)
    result.var_95 = calculate_var(returns, 0.95) * 100
    result.cvar_95 = calculate_cvar(returns, 0.95) * 100
    result.ulcer_index = calculate_ulcer_index(result.equity_curve)

    # Trade statistics
    trade_stats = calculate_trade_stats(result.trades)
    result.total_trades = trade_stats["total_trades"]
    result.win_rate = trade_stats["win_rate"]
    result.profit_factor = trade_stats["profit_factor"]
    result.avg_win = trade_stats["avg_win"]
    result.avg_loss = trade_stats["avg_loss"]
    result.expectancy = trade_stats["expectancy"]
    result.max_consecutive_wins = trade_stats["max_consecutive_wins"]
    result.max_consecutive_losses = trade_stats["max_consecutive_losses"]
    result.avg_trade_duration = trade_stats["avg_trade_duration"]

    return result


def format_metric(value: Optional[float], spec: str = ".2f") -> str:
    """Render an unavailable/non-finite metric without suggesting a numerical result."""
    return format(value, spec) if value is not None and isfinite(value) else "N/A"


def format_results(result: BacktestResult) -> str:
    """Format backtest results as ASCII table."""

    params_str = ", ".join(f"{k}={v}" for k, v in result.parameters.items())

    return f"""
Historical simulation only; results describe the supplied data and assumptions.
Profit factor is N/A without observed losses; zero/one-trade samples are insufficient for inference.
╔══════════════════════════════════════════════════════════════════════╗
║            BACKTEST RESULTS: {result.strategy.upper():^20}              ║
║            {result.symbol} | {result.start_date.strftime("%Y-%m-%d")} to {result.end_date.strftime("%Y-%m-%d")}             ║
╠══════════════════════════════════════════════════════════════════════╣
║ PERFORMANCE                          │ RISK                          ║
║ ─────────────────────────────────────┼─────────────────────────────  ║
║ Total Return:     {format_metric(result.total_return, "+.2f"):>10}%         │ Max Drawdown:   {format_metric(result.max_drawdown, "+.2f"):>10}%    ║
║ CAGR:             {format_metric(result.cagr, "+.2f"):>10}%         │ VaR (95%):      {format_metric(result.var_95, "+.2f"):>10}%    ║
║ Sharpe Ratio:     {format_metric(result.sharpe_ratio, ".2f"):>10}          │ Volatility:     {format_metric(result.volatility, ".2f"):>10}%    ║
║ Sortino Ratio:    {format_metric(result.sortino_ratio):>10}          │ Ulcer Index:    {format_metric(result.ulcer_index, ".2f"):>10}     ║
║ Calmar Ratio:     {format_metric(result.calmar_ratio, ".2f"):>10}          │ CVaR (95%):     {format_metric(result.cvar_95, "+.2f"):>10}%    ║
╠══════════════════════════════════════════════════════════════════════╣
║ TRADE STATISTICS                                                     ║
║ ─────────────────────────────────────────────────────────────────────║
║ Total Trades:     {result.total_trades:>10}          │ Profit Factor:  {format_metric(result.profit_factor):>10}     ║
║ Win Rate:         {format_metric(result.win_rate, ".1f"):>10}%         │ Expectancy:     ${format_metric(result.expectancy, ".2f"):>10}    ║
║ Avg Win:          ${format_metric(result.avg_win, ".2f"):>10}         │ Max Consec. Losses: {result.max_consecutive_losses:>5}    ║
║ Avg Loss:         ${format_metric(result.avg_loss, ".2f"):>10}         │ Avg Duration:   {result.avg_trade_duration:>10}     ║
╠══════════════════════════════════════════════════════════════════════╣
║ Capital: ${format_metric(result.initial_capital, ",.0f")} → ${format_metric(result.final_capital, ",.0f")}                                  ║
║ Parameters: {params_str:<56} ║
╚══════════════════════════════════════════════════════════════════════╝
"""
