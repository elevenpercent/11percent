import pandas as pd
import numpy as np


# ─────────────────────────────────────────────────────────────────────────────
# INDICATOR CALCULATIONS
# ─────────────────────────────────────────────────────────────────────────────

def calc_sma(series: pd.Series, window: int) -> pd.Series:
    """Simple Moving Average"""
    return series.rolling(window=window).mean()


def calc_ema(series: pd.Series, window: int) -> pd.Series:
    """Exponential Moving Average"""
    return series.ewm(span=window, adjust=False).mean()


def calc_rsi(series: pd.Series, window: int = 14) -> pd.Series:
    """
    Relative Strength Index (RSI)
    - Above 70 = overbought (potential sell signal)
    - Below 30 = oversold (potential buy signal)
    """
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=window).mean()
    avg_loss = loss.rolling(window=window).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def calc_macd(series: pd.Series, fast=12, slow=26, signal=9):
    """
    MACD (Moving Average Convergence Divergence)
    Returns: (macd_line, signal_line, histogram)
    """
    ema_fast = calc_ema(series, fast)
    ema_slow = calc_ema(series, slow)
    macd_line = ema_fast - ema_slow
    signal_line = calc_ema(macd_line, signal)
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


# ─────────────────────────────────────────────────────────────────────────────
# BACKTESTING ENGINE
# ─────────────────────────────────────────────────────────────────────────────

def run_backtest(df: pd.DataFrame, signals: pd.Series, initial_capital: float = 10000.0) -> dict:
    """
    Core backtesting engine. Takes a signal series and simulates trades.

    Args:
        df:               DataFrame with at least a 'Close' column
        signals:          Series of 1 (buy), -1 (sell), 0 (hold) aligned with df
        initial_capital:  Starting cash amount in USD

    Returns:
        Dictionary with portfolio values, trades, and performance metrics
    """
    close = df["Close"].copy()
    signals = signals.reindex(close.index).fillna(0)

    cash = initial_capital
    shares = 0
    portfolio_values = []
    trades = []
    position = None  # Track current open position

    for date, price in close.items():
        price = float(price)
        signal = signals.loc[date]

        # BUY signal and we're not already holding
        if signal == 1 and shares == 0 and cash > 0:
            shares = cash / price
            cash = 0
            position = {"entry_date": date, "entry_price": price}
            trades.append({"date": date, "action": "BUY", "price": price, "shares": shares})

        # SELL signal and we're holding shares
        elif signal == -1 and shares > 0:
            cash = shares * price
            profit = cash - initial_capital if not trades else cash - (trades[-1]["price"] * shares)
            trades.append({
                "date": date,
                "action": "SELL",
                "price": price,
                "shares": shares,
                "profit": profit,
            })
            shares = 0
            position = None

        # Calculate current portfolio value (cash + value of any held shares)
        portfolio_value = cash + (shares * price)
        portfolio_values.append({"date": date, "value": portfolio_value})

    # If we're still holding at the end, sell at last price
    if shares > 0:
        last_price = float(close.iloc[-1])
        cash = shares * last_price
        trades.append({"date": close.index[-1], "action": "SELL (End)", "price": last_price, "shares": shares})
        portfolio_values[-1]["value"] = cash

    portfolio_df = pd.DataFrame(portfolio_values).set_index("date")

    # ── Performance Metrics ──────────────────────────────────────────────────
    final_value = portfolio_df["value"].iloc[-1]
    total_return = ((final_value - initial_capital) / initial_capital) * 100

    # Buy & Hold comparison (what if you just bought and held?)
    bh_return = ((float(close.iloc[-1]) - float(close.iloc[0])) / float(close.iloc[0])) * 100

    # Max Drawdown
    rolling_max = portfolio_df["value"].cummax()
    drawdown = (portfolio_df["value"] - rolling_max) / rolling_max * 100
    max_drawdown = drawdown.min()

    # Win rate
    sell_trades = [t for t in trades if "SELL" in t["action"] and "profit" in t]
    win_rate = 0
    if sell_trades:
        wins = sum(1 for t in sell_trades if t.get("profit", 0) > 0)
        win_rate = (wins / len(sell_trades)) * 100

    return {
        "portfolio": portfolio_df,
        "trades": pd.DataFrame(trades),
        "metrics": {
            "initial_capital": initial_capital,
            "final_value": final_value,
            "total_return": total_return,
            "bh_return": bh_return,
            "max_drawdown": max_drawdown,
            "num_trades": len([t for t in trades if t["action"] == "BUY"]),
            "win_rate": win_rate,
        },
    }


# ─────────────────────────────────────────────────────────────────────────────
# STRATEGIES  (each returns a pd.Series of signals: 1=buy, -1=sell, 0=hold)
# ─────────────────────────────────────────────────────────────────────────────

def strategy_sma_crossover(df: pd.DataFrame, short_window: int = 20, long_window: int = 50) -> pd.Series:
    """
    SMA Crossover: Buy when short SMA crosses above long SMA, sell when it crosses below.
    Classic momentum strategy.
    """
    short_sma = calc_sma(df["Close"], short_window)
    long_sma = calc_sma(df["Close"], long_window)

    signals = pd.Series(0, index=df.index)
    # When short crosses above long → BUY
    signals[short_sma > long_sma] = 1
    # When short crosses below long → SELL
    signals[short_sma < long_sma] = -1

    # Only fire on crossover (change in signal), not sustained position
    signals = signals.diff().fillna(0)
    signals[signals > 0] = 1
    signals[signals < 0] = -1
    return signals


def strategy_ema_crossover(df: pd.DataFrame, short_window: int = 12, long_window: int = 26) -> pd.Series:
    """
    EMA Crossover: Same logic as SMA but uses Exponential Moving Averages.
    Reacts faster to recent price changes.
    """
    short_ema = calc_ema(df["Close"], short_window)
    long_ema = calc_ema(df["Close"], long_window)

    signals = pd.Series(0, index=df.index)
    signals[short_ema > long_ema] = 1
    signals[short_ema < long_ema] = -1
    signals = signals.diff().fillna(0)
    signals[signals > 0] = 1
    signals[signals < 0] = -1
    return signals


def strategy_rsi(df: pd.DataFrame, window: int = 14, oversold: int = 30, overbought: int = 70) -> pd.Series:
    """
    RSI Strategy: Buy when RSI drops below oversold level, sell when it rises above overbought.
    """
    rsi = calc_rsi(df["Close"], window)
    signals = pd.Series(0, index=df.index)

    signals[rsi < oversold] = 1   # Oversold → BUY
    signals[rsi > overbought] = -1  # Overbought → SELL
    return signals


def strategy_macd(df: pd.DataFrame) -> pd.Series:
    """
    MACD Strategy: Buy when MACD line crosses above signal line, sell when it crosses below.
    """
    macd_line, signal_line, _ = calc_macd(df["Close"])
    signals = pd.Series(0, index=df.index)

    above = macd_line > signal_line
    signals[above] = 1
    signals[~above] = -1
    signals = signals.diff().fillna(0)
    signals[signals > 0] = 1
    signals[signals < 0] = -1
    return signals


def strategy_custom(df: pd.DataFrame, code: str) -> pd.Series:
    """
    Runs user-provided Python code to generate signals.
    The code has access to: df, pd, np, calc_sma, calc_ema, calc_rsi, calc_macd
    It must define a variable called `signals` (a pd.Series of 1/-1/0).
    """
    local_vars = {
        "df": df.copy(),
        "pd": pd,
        "np": np,
        "calc_sma": calc_sma,
        "calc_ema": calc_ema,
        "calc_rsi": calc_rsi,
        "calc_macd": calc_macd,
    }
    exec(code, {}, local_vars)  # noqa: S102
    if "signals" not in local_vars:
        raise ValueError("Your code must define a variable called `signals`.")
    return local_vars["signals"]
