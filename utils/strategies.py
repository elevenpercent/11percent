"""
Backtesting engine + pre-built strategies for 11% platform.
"""
import pandas as pd
import numpy as np
from utils.indicators import sma, ema, wma, rsi, stoch_rsi, macd, bollinger_bands, supertrend, ichimoku


# ─────────────────────────────────────────────────────────────────
# CORE BACKTEST ENGINE
# ─────────────────────────────────────────────────────────────────

def run_backtest(df: pd.DataFrame, signals: pd.Series, initial_capital: float = 10000.0) -> dict:
    """
    Simulates trades based on a signal series.
    signals: 1 = BUY, -1 = SELL, 0 = HOLD
    Returns portfolio values, trade log, and performance metrics.
    """
    close = df["Close"].copy()
    signals = signals.reindex(close.index).fillna(0)

    cash, shares = initial_capital, 0.0
    portfolio_values, trades = [], []

    for date, price in close.items():
        price = float(price)
        sig = signals.loc[date]

        if sig == 1 and shares == 0 and cash > 0:
            shares = cash / price
            cash = 0.0
            trades.append({"date": date, "action": "BUY", "price": price, "shares": shares, "value": shares * price})

        elif sig == -1 and shares > 0:
            cash = shares * price
            entry = next((t for t in reversed(trades) if t["action"] == "BUY"), None)
            profit_pct = ((price - entry["price"]) / entry["price"] * 100) if entry else 0
            trades.append({"date": date, "action": "SELL", "price": price, "shares": shares,
                           "value": cash, "profit_pct": profit_pct})
            shares = 0.0

        portfolio_values.append({"date": date, "value": cash + shares * price})

    # Force close at end
    if shares > 0:
        last_price = float(close.iloc[-1])
        cash = shares * last_price
        entry = next((t for t in reversed(trades) if t["action"] == "BUY"), None)
        profit_pct = ((last_price - entry["price"]) / entry["price"] * 100) if entry else 0
        trades.append({"date": close.index[-1], "action": "SELL (End)", "price": last_price,
                       "shares": shares, "value": cash, "profit_pct": profit_pct})
        portfolio_values[-1]["value"] = cash

    port_df = pd.DataFrame(portfolio_values).set_index("date")
    trades_df = pd.DataFrame(trades) if trades else pd.DataFrame()

    final_value = port_df["value"].iloc[-1]
    total_return = (final_value - initial_capital) / initial_capital * 100
    bh_return = (float(close.iloc[-1]) - float(close.iloc[0])) / float(close.iloc[0]) * 100

    rolling_max = port_df["value"].cummax()
    max_drawdown = ((port_df["value"] - rolling_max) / rolling_max * 100).min()

    sell_trades = [t for t in trades if "SELL" in t["action"] and "profit_pct" in t]
    num_trades = sum(1 for t in trades if t["action"] == "BUY")
    win_rate = 0.0
    if sell_trades:
        wins = sum(1 for t in sell_trades if t.get("profit_pct", 0) > 0)
        win_rate = wins / len(sell_trades) * 100

    # Sharpe ratio (annualised, risk-free = 0)
    daily_returns = port_df["value"].pct_change().dropna()
    sharpe = (daily_returns.mean() / daily_returns.std() * np.sqrt(252)) if daily_returns.std() > 0 else 0

    return {
        "portfolio": port_df,
        "trades": trades_df,
        "metrics": {
            "initial_capital": initial_capital,
            "final_value":     final_value,
            "total_return":    total_return,
            "bh_return":       bh_return,
            "max_drawdown":    max_drawdown,
            "num_trades":      num_trades,
            "win_rate":        win_rate,
            "sharpe":          sharpe,
        },
    }


# ─────────────────────────────────────────────────────────────────
# PRE-BUILT STRATEGIES
# Each returns a pd.Series of signals: 1 / -1 / 0
# ─────────────────────────────────────────────────────────────────

def strategy_sma_crossover(df, short=20, long=50):
    """Golden/Death cross on SMA."""
    s = sma(df["Close"], short)
    l = sma(df["Close"], long)
    raw = pd.Series(0, index=df.index)
    raw[s > l] = 1
    raw[s < l] = -1
    sig = raw.diff().fillna(0)
    sig[sig > 0] = 1; sig[sig < 0] = -1
    return sig


def strategy_ema_crossover(df, short=12, long=26):
    """EMA crossover — faster than SMA version."""
    s = ema(df["Close"], short)
    l = ema(df["Close"], long)
    raw = pd.Series(0, index=df.index)
    raw[s > l] = 1; raw[s < l] = -1
    sig = raw.diff().fillna(0)
    sig[sig > 0] = 1; sig[sig < 0] = -1
    return sig


def strategy_rsi(df, window=14, oversold=30, overbought=70):
    """Buy oversold, sell overbought."""
    r = rsi(df["Close"], window)
    sig = pd.Series(0, index=df.index)
    sig[r < oversold] = 1
    sig[r > overbought] = -1
    return sig


def strategy_macd(df, fast=12, slow=26, signal=9):
    """Buy when MACD crosses above signal line."""
    m = macd(df["Close"], fast, slow, signal)
    raw = pd.Series(0, index=df.index)
    raw[m["macd"] > m["signal"]] = 1
    raw[m["macd"] < m["signal"]] = -1
    sig = raw.diff().fillna(0)
    sig[sig > 0] = 1; sig[sig < 0] = -1
    return sig


def strategy_bollinger(df, window=20, num_std=2.0):
    """Buy at lower band, sell at upper band."""
    bb = bollinger_bands(df["Close"], window, num_std)
    sig = pd.Series(0, index=df.index)
    sig[df["Close"] < bb["lower"]] = 1
    sig[df["Close"] > bb["upper"]] = -1
    return sig


def strategy_supertrend(df, window=10, multiplier=3.0):
    """Follow SuperTrend direction changes."""
    st = supertrend(df, window, multiplier)
    raw = st["direction"].fillna(0)
    sig = raw.diff().fillna(0)
    sig[sig > 0] = 1; sig[sig < 0] = -1
    return sig


def strategy_rsi_bb(df, rsi_window=14, bb_window=20, oversold=35, overbought=65, num_std=2.0):
    """
    RSI + Bollinger Band combo:
    Buy when RSI oversold AND price near lower BB.
    Sell when RSI overbought AND price near upper BB.
    """
    r = rsi(df["Close"], rsi_window)
    bb = bollinger_bands(df["Close"], bb_window, num_std)
    sig = pd.Series(0, index=df.index)
    buy  = (r < oversold)  & (df["Close"] <= bb["middle"])
    sell = (r > overbought) & (df["Close"] >= bb["middle"])
    sig[buy] = 1; sig[sell] = -1
    return sig


def strategy_ema_rsi(df, ema_fast=9, ema_slow=21, rsi_window=14, oversold=40, overbought=60):
    """
    EMA trend filter + RSI confirmation:
    Buy when fast EMA > slow EMA (uptrend) AND RSI dips below oversold.
    Sell when fast EMA < slow EMA (downtrend) OR RSI above overbought.
    """
    ef = ema(df["Close"], ema_fast)
    es = ema(df["Close"], ema_slow)
    r  = rsi(df["Close"], rsi_window)
    sig = pd.Series(0, index=df.index)
    sig[(ef > es) & (r < oversold)]  = 1
    sig[(ef < es) | (r > overbought)] = -1
    return sig


def strategy_macd_supertrend(df, fast=12, slow=26, signal_p=9, st_window=10, st_mult=3.0):
    """
    MACD + SuperTrend combo:
    Buy when MACD bullish AND SuperTrend bullish.
    Sell when either turns bearish.
    """
    m  = macd(df["Close"], fast, slow, signal_p)
    st = supertrend(df, st_window, st_mult)
    sig = pd.Series(0, index=df.index)
    macd_bull = m["macd"] > m["signal"]
    st_bull   = st["direction"] == 1
    sig[macd_bull & st_bull]    = 1
    sig[~macd_bull | ~st_bull]  = -1
    raw = sig.diff().fillna(0)
    raw[raw > 0] = 1; raw[raw < 0] = -1
    return raw


# Registry of all pre-built strategies for the UI
STRATEGY_REGISTRY = {
    "SMA Crossover":          {"fn": strategy_sma_crossover,  "params": {"short": 20, "long": 50}},
    "EMA Crossover":          {"fn": strategy_ema_crossover,  "params": {"short": 12, "long": 26}},
    "RSI":                    {"fn": strategy_rsi,            "params": {"window": 14, "oversold": 30, "overbought": 70}},
    "MACD":                   {"fn": strategy_macd,           "params": {"fast": 12, "slow": 26, "signal": 9}},
    "Bollinger Bands":        {"fn": strategy_bollinger,      "params": {"window": 20, "num_std": 2.0}},
    "SuperTrend":             {"fn": strategy_supertrend,     "params": {"window": 10, "multiplier": 3.0}},
    "RSI + Bollinger Bands":  {"fn": strategy_rsi_bb,         "params": {"rsi_window": 14, "bb_window": 20, "oversold": 35, "overbought": 65}},
    "EMA + RSI Filter":       {"fn": strategy_ema_rsi,        "params": {"ema_fast": 9, "ema_slow": 21, "rsi_window": 14}},
    "MACD + SuperTrend":      {"fn": strategy_macd_supertrend,"params": {"fast": 12, "slow": 26, "st_window": 10}},
}
