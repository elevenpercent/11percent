"""
All technical indicators for 11% platform.
Every function takes a DataFrame and returns a Series or dict of Series.
"""
import pandas as pd
import numpy as np


# -----------------------------------------------------------------
# MOVING AVERAGES
# -----------------------------------------------------------------

def sma(series: pd.Series, window: int) -> pd.Series:
    """Simple Moving Average"""
    return series.rolling(window=window).mean()


def ema(series: pd.Series, window: int) -> pd.Series:
    """Exponential Moving Average"""
    return series.ewm(span=window, adjust=False).mean()


def wma(series: pd.Series, window: int) -> pd.Series:
    """Weighted Moving Average - more weight to recent prices"""
    weights = np.arange(1, window + 1)
    return series.rolling(window).apply(lambda x: np.dot(x, weights) / weights.sum(), raw=True)


# -----------------------------------------------------------------
# RSI
# -----------------------------------------------------------------

def rsi(series: pd.Series, window: int = 14) -> pd.Series:
    """Relative Strength Index (0-100). >70 overbought, <30 oversold."""
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(window).mean()
    loss = (-delta.clip(upper=0)).rolling(window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


def stoch_rsi(series: pd.Series, rsi_window: int = 14, stoch_window: int = 14,
              smooth_k: int = 3, smooth_d: int = 3) -> dict:
    """
    Stochastic RSI - applies Stochastic formula to RSI values.
    Returns dict with 'k' and 'd' lines (both 0-100).
    """
    rsi_vals = rsi(series, rsi_window)
    min_rsi = rsi_vals.rolling(stoch_window).min()
    max_rsi = rsi_vals.rolling(stoch_window).max()
    k = 100 * (rsi_vals - min_rsi) / (max_rsi - min_rsi + 1e-10)
    k = k.rolling(smooth_k).mean()
    d = k.rolling(smooth_d).mean()
    return {"k": k, "d": d}


# -----------------------------------------------------------------
# MACD
# -----------------------------------------------------------------

def macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> dict:
    """
    MACD - returns dict with 'macd', 'signal', 'histogram'.
    Buy when macd crosses above signal, sell when crosses below.
    """
    ema_fast = ema(series, fast)
    ema_slow = ema(series, slow)
    macd_line = ema_fast - ema_slow
    signal_line = ema(macd_line, signal)
    histogram = macd_line - signal_line
    return {"macd": macd_line, "signal": signal_line, "histogram": histogram}


# -----------------------------------------------------------------
# BOLLINGER BANDS
# -----------------------------------------------------------------

def bollinger_bands(series: pd.Series, window: int = 20, num_std: float = 2.0) -> dict:
    """
    Bollinger Bands - middle band is SMA, upper/lower are ?num_std standard deviations.
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


# -----------------------------------------------------------------
# ATR
# -----------------------------------------------------------------

def atr(df: pd.DataFrame, window: int = 14) -> pd.Series:
    """Average True Range - measures volatility."""
    high, low, close = df["High"], df["Low"], df["Close"]
    tr = pd.concat([
        high - low,
        (high - close.shift()).abs(),
        (low - close.shift()).abs()
    ], axis=1).max(axis=1)
    return tr.rolling(window).mean()


# -----------------------------------------------------------------
# SUPERTREND
# -----------------------------------------------------------------

def supertrend(df: pd.DataFrame, window: int = 10, multiplier: float = 3.0) -> dict:
    """
    SuperTrend - trend following indicator.
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


# -----------------------------------------------------------------
# VWAP
# -----------------------------------------------------------------

def vwap(df: pd.DataFrame) -> pd.Series:
    """
    Volume Weighted Average Price.
    Note: VWAP resets daily - best used on intraday data.
    On daily data it acts as a cumulative VWAP.
    """
    typical_price = (df["High"] + df["Low"] + df["Close"]) / 3
    return (typical_price * df["Volume"]).cumsum() / df["Volume"].cumsum()


# -----------------------------------------------------------------
# OBV
# -----------------------------------------------------------------

def obv(df: pd.DataFrame) -> pd.Series:
    """
    On Balance Volume - cumulative volume based on price direction.
    Rising OBV = buying pressure, falling = selling pressure.
    """
    direction = df["Close"].diff().apply(lambda x: 1 if x > 0 else (-1 if x < 0 else 0))
    return (direction * df["Volume"]).cumsum()


# -----------------------------------------------------------------
# ICHIMOKU CLOUD
# -----------------------------------------------------------------

def ichimoku(df: pd.DataFrame,
             tenkan_window: int = 9,
             kijun_window: int = 26,
             senkou_b_window: int = 52) -> dict:
    """
    Ichimoku Cloud - comprehensive trend indicator.
    Returns dict with all 5 Ichimoku lines:
    - tenkan_sen (Conversion Line)
    - kijun_sen (Base Line)
    - senkou_span_a (Leading Span A) - shifted forward 26 periods
    - senkou_span_b (Leading Span B) - shifted forward 26 periods
    - chikou_span (Lagging Span) - shifted back 26 periods
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


# -----------------------------------------------------------------
# INDICATOR REGISTRY
# Used by the Indicator Test page to dynamically build the UI
# -----------------------------------------------------------------

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
        "description": "Momentum oscillator 0-100. Buy <30, sell >70.",
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
    "CCI": {
        "label": "Commodity Channel Index",
        "params": {"window": {"type":"int","default":20,"min":5,"max":50,"label":"Period"}},
        "overlay": False,
        "description": "Momentum oscillator. >100 overbought, <-100 oversold.",
    },
    "Williams %R": {
        "label": "Williams %R",
        "params": {"window": {"type":"int","default":14,"min":2,"max":50,"label":"Period"}},
        "overlay": False,
        "description": "Momentum -100 to 0. Below -80 oversold, above -20 overbought.",
    },
    "Donchian": {
        "label": "Donchian Channels",
        "params": {"window": {"type":"int","default":20,"min":5,"max":100,"label":"Period"}},
        "overlay": True,
        "description": "Highest high / lowest low channel. Classic breakout indicator.",
    },
    "Keltner": {
        "label": "Keltner Channels",
        "params": {
            "ema_window":  {"type":"int",  "default":20,  "min":5,  "max":100,"label":"EMA Period"},
            "atr_window":  {"type":"int",  "default":10,  "min":3,  "max":30, "label":"ATR Period"},
            "multiplier":  {"type":"float","default":2.0, "min":0.5,"max":4.0,"label":"Multiplier"},
        },
        "overlay": True,
        "description": "EMA channel using ATR width. Tighter than Bollinger Bands.",
    },
    "Hull MA": {
        "label": "Hull Moving Average",
        "params": {"window": {"type":"int","default":20,"min":2,"max":200,"label":"Period"}},
        "overlay": True,
        "description": "Ultra-smooth fast MA. Much less lag than SMA/EMA.",
    },
    "Parabolic SAR": {
        "label": "Parabolic SAR",
        "params": {
            "af_start": {"type":"float","default":0.02,"min":0.01,"max":0.1, "label":"AF Start"},
            "af_max":   {"type":"float","default":0.2, "min":0.1, "max":0.5, "label":"AF Max"},
        },
        "overlay": True,
        "description": "Trailing stop-and-reverse. Dots below = bullish, above = bearish.",
    },
}


# -----------------------------------------------------------------
# NEW INDICATORS
# -----------------------------------------------------------------

def cci(df: pd.DataFrame, window: int = 20) -> pd.Series:
    """Commodity Channel Index. >100 overbought, <-100 oversold."""
    tp = (df["High"] + df["Low"] + df["Close"]) / 3
    mean_tp  = tp.rolling(window).mean()
    mean_dev = tp.rolling(window).apply(lambda x: np.mean(np.abs(x - x.mean())), raw=True)
    return (tp - mean_tp) / (0.015 * mean_dev + 1e-10)


def williams_r(df: pd.DataFrame, window: int = 14) -> pd.Series:
    """Williams %R - ranges -100 to 0. Below -80 oversold, above -20 overbought."""
    highest = df["High"].rolling(window).max()
    lowest  = df["Low"].rolling(window).min()
    return -100 * (highest - df["Close"]) / (highest - lowest + 1e-10)


def donchian_channels(df: pd.DataFrame, window: int = 20) -> dict:
    """Donchian Channels - highest high / lowest low over N periods."""
    upper  = df["High"].rolling(window).max()
    lower  = df["Low"].rolling(window).min()
    middle = (upper + lower) / 2
    return {"upper": upper, "middle": middle, "lower": lower}


def keltner_channels(df: pd.DataFrame, ema_window: int = 20, atr_window: int = 10, multiplier: float = 2.0) -> dict:
    """Keltner Channels - EMA ? multiplier ? ATR."""
    mid       = ema(df["Close"], ema_window)
    atr_vals  = atr(df, atr_window)
    upper     = mid + multiplier * atr_vals
    lower     = mid - multiplier * atr_vals
    return {"upper": upper, "middle": mid, "lower": lower}


def hull_ma(series: pd.Series, window: int = 20) -> pd.Series:
    """Hull Moving Average - extremely smooth, fast-reacting MA."""
    half   = max(1, window // 2)
    sqrt_w = max(1, int(np.sqrt(window)))
    raw    = 2 * wma(series, half) - wma(series, window)
    return wma(raw, sqrt_w)


def parabolic_sar(df: pd.DataFrame, af_start: float = 0.02, af_max: float = 0.2) -> dict:
    """Parabolic SAR - trailing stop-and-reverse indicator."""
    high = df["High"].values
    low  = df["Low"].values
    n    = len(df)
    sar  = np.zeros(n); ep = np.zeros(n); af = np.zeros(n); trend = np.ones(n)
    sar[0] = low[0]; ep[0] = high[0]; af[0] = af_start; trend[0] = 1
    for i in range(1, n):
        ps, pe, pa, pt = sar[i-1], ep[i-1], af[i-1], trend[i-1]
        if pt == 1:
            sar[i] = ps + pa * (pe - ps)
            sar[i] = min(sar[i], low[i-1], low[max(0, i-2)])
            if low[i] < sar[i]:
                trend[i] = -1; sar[i] = pe; ep[i] = low[i]; af[i] = af_start
            else:
                trend[i] = 1
                if high[i] > pe: ep[i] = high[i]; af[i] = min(pa + af_start, af_max)
                else: ep[i] = pe; af[i] = pa
        else:
            sar[i] = ps + pa * (pe - ps)
            sar[i] = max(sar[i], high[i-1], high[max(0, i-2)])
            if high[i] > sar[i]:
                trend[i] = 1; sar[i] = pe; ep[i] = high[i]; af[i] = af_start
            else:
                trend[i] = -1
                if low[i] < pe: ep[i] = low[i]; af[i] = min(pa + af_start, af_max)
                else: ep[i] = pe; af[i] = pa
    return {"sar": pd.Series(sar, index=df.index), "direction": pd.Series(trend.astype(int), index=df.index)}
