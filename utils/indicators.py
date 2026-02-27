"""
All technical indicators for 11% platform.
Every function takes a DataFrame and returns a Series or dict of Series.
"""
import pandas as pd
import numpy as np


# ─────────────────────────────────────────────────────────────────
# MOVING AVERAGES
# ─────────────────────────────────────────────────────────────────

def sma(series: pd.Series, window: int) -> pd.Series:
    """Simple Moving Average"""
    return series.rolling(window=window).mean()


def ema(series: pd.Series, window: int) -> pd.Series:
    """Exponential Moving Average"""
    return series.ewm(span=window, adjust=False).mean()


def wma(series: pd.Series, window: int) -> pd.Series:
    """Weighted Moving Average — more weight to recent prices"""
    weights = np.arange(1, window + 1)
    return series.rolling(window).apply(lambda x: np.dot(x, weights) / weights.sum(), raw=True)


# ─────────────────────────────────────────────────────────────────
# RSI
# ─────────────────────────────────────────────────────────────────

def rsi(series: pd.Series, window: int = 14) -> pd.Series:
    """Relative Strength Index (0–100). >70 overbought, <30 oversold."""
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(window).mean()
    loss = (-delta.clip(upper=0)).rolling(window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


def stoch_rsi(series: pd.Series, rsi_window: int = 14, stoch_window: int = 14,
              smooth_k: int = 3, smooth_d: int = 3) -> dict:
    """
    Stochastic RSI — applies Stochastic formula to RSI values.
    Returns dict with 'k' and 'd' lines (both 0–100).
    """
    rsi_vals = rsi(series, rsi_window)
    min_rsi = rsi_vals.rolling(stoch_window).min()
    max_rsi = rsi_vals.rolling(stoch_window).max()
    k = 100 * (rsi_vals - min_rsi) / (max_rsi - min_rsi + 1e-10)
    k = k.rolling(smooth_k).mean()
    d = k.rolling(smooth_d).mean()
    return {"k": k, "d": d}


# ─────────────────────────────────────────────────────────────────
# MACD
# ─────────────────────────────────────────────────────────────────

def macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> dict:
    """
    MACD — returns dict with 'macd', 'signal', 'histogram'.
    Buy when macd crosses above signal, sell when crosses below.
    """
    ema_fast = ema(series, fast)
    ema_slow = ema(series, slow)
    macd_line = ema_fast - ema_slow
    signal_line = ema(macd_line, signal)
    histogram = macd_line - signal_line
    return {"macd": macd_line, "signal": signal_line, "histogram": histogram}


# ─────────────────────────────────────────────────────────────────
# BOLLINGER BANDS
# ─────────────────────────────────────────────────────────────────

def bollinger_bands(series: pd.Series, window: int = 20, num_std: float = 2.0) -> dict:
    """
    Bollinger Bands — middle band is SMA, upper/lower are ±num_std standard deviations.
    Returns dict with 'upper', 'middle', 'lower', 'bandwidth', 'percent_b'.
    """
    middle = sma(series, window)
    std = series.rolling(window).std()
    upper = middle + (std * num_std)
    lower = middle - (std * num_std)
    bandwidth = (upper - lower) / middle * 100
    percent_b = (series - lower) / (upper - lower + 1e-10) * 100
    return {"upper": upper, "middle": middle, "lower": lower,
            "bandwidth": bandwidth, "percent_b": percent_b}


# ─────────────────────────────────────────────────────────────────
# ATR
# ─────────────────────────────────────────────────────────────────

def atr(df: pd.DataFrame, window: int = 14) -> pd.Series:
    """Average True Range — measures volatility."""
    high, low, close = df["High"], df["Low"], df["Close"]
    tr = pd.concat([
        high - low,
        (high - close.shift()).abs(),
        (low - close.shift()).abs()
    ], axis=1).max(axis=1)
    return tr.rolling(window).mean()


# ─────────────────────────────────────────────────────────────────
# SUPERTREND
# ─────────────────────────────────────────────────────────────────

def supertrend(df: pd.DataFrame, window: int = 10, multiplier: float = 3.0) -> dict:
    """
    SuperTrend — trend following indicator.
    Returns dict with 'supertrend' (line), 'direction' (1=bullish, -1=bearish).
    """
    atr_vals = atr(df, window)
    hl2 = (df["High"] + df["Low"]) / 2
    upper_band = hl2 + multiplier * atr_vals
    lower_band = hl2 - multiplier * atr_vals

    supertrend_line = pd.Series(index=df.index, dtype=float)
    direction = pd.Series(index=df.index, dtype=int)
    close = df["Close"]

    for i in range(1, len(df)):
        # Adjust bands
        if lower_band.iloc[i] > lower_band.iloc[i-1] or close.iloc[i-1] < supertrend_line.iloc[i-1]:
            lb = lower_band.iloc[i]
        else:
            lb = lower_band.iloc[i-1]

        if upper_band.iloc[i] < upper_band.iloc[i-1] or close.iloc[i-1] > supertrend_line.iloc[i-1]:
            ub = upper_band.iloc[i]
        else:
            ub = upper_band.iloc[i-1]

        prev_st = supertrend_line.iloc[i-1] if i > 1 else ub

        if prev_st == ub:
            if close.iloc[i] <= ub:
                supertrend_line.iloc[i] = ub
                direction.iloc[i] = -1
            else:
                supertrend_line.iloc[i] = lb
                direction.iloc[i] = 1
        else:
            if close.iloc[i] >= lb:
                supertrend_line.iloc[i] = lb
                direction.iloc[i] = 1
            else:
                supertrend_line.iloc[i] = ub
                direction.iloc[i] = -1

    return {"supertrend": supertrend_line, "direction": direction}


# ─────────────────────────────────────────────────────────────────
# VWAP
# ─────────────────────────────────────────────────────────────────

def vwap(df: pd.DataFrame) -> pd.Series:
    """
    Volume Weighted Average Price.
    Note: VWAP resets daily — best used on intraday data.
    On daily data it acts as a cumulative VWAP.
    """
    typical_price = (df["High"] + df["Low"] + df["Close"]) / 3
    return (typical_price * df["Volume"]).cumsum() / df["Volume"].cumsum()


# ─────────────────────────────────────────────────────────────────
# OBV
# ─────────────────────────────────────────────────────────────────

def obv(df: pd.DataFrame) -> pd.Series:
    """
    On Balance Volume — cumulative volume based on price direction.
    Rising OBV = buying pressure, falling = selling pressure.
    """
    direction = df["Close"].diff().apply(lambda x: 1 if x > 0 else (-1 if x < 0 else 0))
    return (direction * df["Volume"]).cumsum()


# ─────────────────────────────────────────────────────────────────
# ICHIMOKU CLOUD
# ─────────────────────────────────────────────────────────────────

def ichimoku(df: pd.DataFrame,
             tenkan_window: int = 9,
             kijun_window: int = 26,
             senkou_b_window: int = 52) -> dict:
    """
    Ichimoku Cloud — comprehensive trend indicator.
    Returns dict with all 5 Ichimoku lines:
    - tenkan_sen (Conversion Line)
    - kijun_sen (Base Line)
    - senkou_span_a (Leading Span A) — shifted forward 26 periods
    - senkou_span_b (Leading Span B) — shifted forward 26 periods
    - chikou_span (Lagging Span) — shifted back 26 periods
    """
    def midpoint(series: pd.Series, window: int) -> pd.Series:
        return (series.rolling(window).max() + series.rolling(window).min()) / 2

    tenkan = midpoint(df["Close"], tenkan_window)
    kijun = midpoint(df["Close"], kijun_window)
    senkou_a = ((tenkan + kijun) / 2).shift(kijun_window)
    senkou_b = midpoint(df["Close"], senkou_b_window).shift(kijun_window)
    chikou = df["Close"].shift(-kijun_window)

    return {
        "tenkan_sen":    tenkan,
        "kijun_sen":     kijun,
        "senkou_span_a": senkou_a,
        "senkou_span_b": senkou_b,
        "chikou_span":   chikou,
    }


# ─────────────────────────────────────────────────────────────────
# INDICATOR REGISTRY
# Used by the Indicator Test page to dynamically build the UI
# ─────────────────────────────────────────────────────────────────

INDICATOR_INFO = {
    "SMA": {
        "label": "Simple Moving Average",
        "params": {"window": {"type": "int", "default": 20, "min": 2, "max": 200, "label": "Period"}},
        "overlay": True,   # drawn on price chart
        "description": "Average price over N periods. Trend following.",
    },
    "EMA": {
        "label": "Exponential Moving Average",
        "params": {"window": {"type": "int", "default": 20, "min": 2, "max": 200, "label": "Period"}},
        "overlay": True,
        "description": "Like SMA but reacts faster to recent price changes.",
    },
    "WMA": {
        "label": "Weighted Moving Average",
        "params": {"window": {"type": "int", "default": 20, "min": 2, "max": 200, "label": "Period"}},
        "overlay": True,
        "description": "Moving average giving more weight to recent prices.",
    },
    "RSI": {
        "label": "RSI",
        "params": {
            "window":     {"type": "int",   "default": 14, "min": 2,  "max": 50,  "label": "Period"},
            "oversold":   {"type": "int",   "default": 30, "min": 10, "max": 49,  "label": "Oversold Level"},
            "overbought": {"type": "int",   "default": 70, "min": 51, "max": 90,  "label": "Overbought Level"},
        },
        "overlay": False,
        "description": "Momentum oscillator 0–100. Buy <30, sell >70.",
    },
    "Stoch RSI": {
        "label": "Stochastic RSI",
        "params": {
            "rsi_window":   {"type": "int", "default": 14, "min": 2, "max": 50, "label": "RSI Period"},
            "stoch_window": {"type": "int", "default": 14, "min": 2, "max": 50, "label": "Stoch Period"},
            "smooth_k":     {"type": "int", "default": 3,  "min": 1, "max": 10, "label": "Smooth K"},
            "smooth_d":     {"type": "int", "default": 3,  "min": 1, "max": 10, "label": "Smooth D"},
        },
        "overlay": False,
        "description": "RSI of RSI. More sensitive than standard RSI.",
    },
    "MACD": {
        "label": "MACD",
        "params": {
            "fast":   {"type": "int", "default": 12, "min": 2,  "max": 50,  "label": "Fast Period"},
            "slow":   {"type": "int", "default": 26, "min": 5,  "max": 200, "label": "Slow Period"},
            "signal": {"type": "int", "default": 9,  "min": 2,  "max": 50,  "label": "Signal Period"},
        },
        "overlay": False,
        "description": "Trend & momentum. Buy when MACD crosses above signal.",
    },
    "Bollinger Bands": {
        "label": "Bollinger Bands",
        "params": {
            "window":   {"type": "int",   "default": 20,  "min": 5,   "max": 200, "label": "Period"},
            "num_std":  {"type": "float", "default": 2.0, "min": 0.5, "max": 4.0, "label": "Std Dev"},
        },
        "overlay": True,
        "description": "Volatility bands. Buy near lower band, sell near upper.",
    },
    "SuperTrend": {
        "label": "SuperTrend",
        "params": {
            "window":     {"type": "int",   "default": 10,  "min": 3,   "max": 50,  "label": "ATR Period"},
            "multiplier": {"type": "float", "default": 3.0, "min": 0.5, "max": 6.0, "label": "Multiplier"},
        },
        "overlay": True,
        "description": "Trend direction indicator. Green = bullish, red = bearish.",
    },
    "Ichimoku": {
        "label": "Ichimoku Cloud",
        "params": {
            "tenkan_window":   {"type": "int", "default": 9,  "min": 3, "max": 30,  "label": "Tenkan Period"},
            "kijun_window":    {"type": "int", "default": 26, "min": 5, "max": 60,  "label": "Kijun Period"},
            "senkou_b_window": {"type": "int", "default": 52, "min": 10,"max": 120, "label": "Senkou B Period"},
        },
        "overlay": True,
        "description": "All-in-one trend, support/resistance, and momentum indicator.",
    },
}
