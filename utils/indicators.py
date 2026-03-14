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

import numpy as _np

# ── Additional indicator functions ───────────────────────────────────────────

def stochastic(df, k_window=14, d_window=3):
    low_min  = df["Low"].rolling(k_window).min()
    high_max = df["High"].rolling(k_window).max()
    k = 100 * (df["Close"] - low_min) / (high_max - low_min)
    d = k.rolling(d_window).mean()
    return {"k": k, "d": d}

def mfi(df, window=14):
    tp  = (df["High"] + df["Low"] + df["Close"]) / 3
    mf  = tp * df["Volume"]
    pos = mf.where(tp > tp.shift(1), 0).rolling(window).sum()
    neg = mf.where(tp < tp.shift(1), 0).rolling(window).sum()
    return 100 - (100 / (1 + pos / neg.abs()))

def roc(series, window=12):
    return (series - series.shift(window)) / series.shift(window) * 100

def momentum(series, window=10):
    return series - series.shift(window)

def trix(series, window=15):
    e1 = series.ewm(span=window).mean()
    e2 = e1.ewm(span=window).mean()
    e3 = e2.ewm(span=window).mean()
    return (e3 - e3.shift(1)) / e3.shift(1) * 100

def dema(series, window=20):
    e = series.ewm(span=window).mean()
    return 2 * e - e.ewm(span=window).mean()

def tema(series, window=20):
    e1 = series.ewm(span=window).mean()
    e2 = e1.ewm(span=window).mean()
    e3 = e2.ewm(span=window).mean()
    return 3*e1 - 3*e2 + e3

def vidya(series, window=14, smooth=12):
    delta = series.diff().abs()
    rsi_val = rsi(series, window)
    k  = (rsi_val / 100).ewm(span=smooth).mean()
    v  = series.copy()
    for i in range(1, len(series)):
        v.iloc[i] = k.iloc[i] * series.iloc[i] + (1 - k.iloc[i]) * v.iloc[i-1]
    return v

def elder_ray(df, window=13):
    bull = df["High"] - ema(df["Close"], window)
    bear = df["Low"]  - ema(df["Close"], window)
    return {"bull": bull, "bear": bear}

def mass_index(df, fast=9, slow=25):
    hl    = df["High"] - df["Low"]
    e1    = hl.ewm(span=fast).mean()
    e2    = e1.ewm(span=fast).mean()
    ratio = e1 / e2
    return ratio.rolling(slow).sum()

def chande_momentum(series, window=20):
    diff = series.diff()
    up   = diff.clip(lower=0).rolling(window).sum()
    down = (-diff.clip(upper=0)).rolling(window).sum()
    return 100 * (up - down) / (up + down)

def dpo(series, window=20):
    shifted = series.shift(window // 2 + 1)
    return series - sma(series, window).shift(window // 2 + 1)

def aroon(df, window=25):
    high_idx = df["High"].rolling(window+1).apply(lambda x: x.argmax(), raw=True)
    low_idx  = df["Low"].rolling(window+1).apply(lambda x: x.argmin(), raw=True)
    up   = 100 * high_idx / window
    down = 100 * low_idx  / window
    return {"up": up, "down": down, "oscillator": up - down}

def ultimate_oscillator(df, p1=7, p2=14, p3=28):
    bp  = df["Close"] - df[["Low", "Close"]].shift(1).min(axis=1)
    tr  = df["High"]  - df[["Low", "Close"]].shift(1).min(axis=1)
    avg1 = bp.rolling(p1).sum() / tr.rolling(p1).sum()
    avg2 = bp.rolling(p2).sum() / tr.rolling(p2).sum()
    avg3 = bp.rolling(p3).sum() / tr.rolling(p3).sum()
    return 100 * (4*avg1 + 2*avg2 + avg3) / 7

def cmo(series, window=14):
    return chande_momentum(series, window)

def pivot_points(df):
    p  = (df["High"] + df["Low"] + df["Close"]) / 3
    r1 = 2*p - df["Low"]
    s1 = 2*p - df["High"]
    r2 = p + (df["High"] - df["Low"])
    s2 = p - (df["High"] - df["Low"])
    return {"pivot": p, "r1": r1, "s1": s1, "r2": r2, "s2": s2}

def standard_deviation(series, window=20):
    return series.rolling(window).std()

def historical_volatility(series, window=20):
    log_ret = (series / series.shift(1)).apply(_np.log)
    return log_ret.rolling(window).std() * _np.sqrt(252) * 100

def linear_regression_slope(series, window=14):
    def _slope(x):
        n = len(x)
        xi = _np.arange(n)
        return _np.polyfit(xi, x, 1)[0]
    return series.rolling(window).apply(_slope, raw=True)

def envelope(series, window=20, pct=0.025):
    mid = sma(series, window)
    return {"upper": mid*(1+pct), "mid": mid, "lower": mid*(1-pct)}

def price_channel(df, window=20):
    return {"upper": df["High"].rolling(window).max(),
            "lower": df["Low"].rolling(window).min()}

def chaikin_money_flow(df, window=20):
    mfm  = ((df["Close"]-df["Low"]) - (df["High"]-df["Close"])) / (df["High"]-df["Low"])
    mfv  = mfm * df["Volume"]
    return mfv.rolling(window).sum() / df["Volume"].rolling(window).sum()

def chaikin_oscillator(df, fast=3, slow=10):
    adl  = ((df["Close"]-df["Low"]) - (df["High"]-df["Close"])) / (df["High"]-df["Low"]) * df["Volume"]
    adl  = adl.cumsum()
    return adl.ewm(span=fast).mean() - adl.ewm(span=slow).mean()

def klinger_oscillator(df, fast=34, slow=55):
    dm   = df["High"] - df["Low"]
    trend = df["Close"].diff()
    sv   = dm * df["Volume"] * trend.apply(lambda x: 1 if x > 0 else -1)
    return sv.ewm(span=fast).mean() - sv.ewm(span=slow).mean()

def ease_of_movement(df, window=14):
    dm   = (df["High"]+df["Low"])/2 - (df["High"].shift(1)+df["Low"].shift(1))/2
    br   = df["Volume"] / (df["High"] - df["Low"])
    eom  = dm / br
    return eom.rolling(window).mean()

def force_index(df, window=13):
    fi = df["Close"].diff() * df["Volume"]
    return fi.ewm(span=window).mean()

def negative_volume_index(df):
    nvi = _pd_series_ones(df)
    for i in range(1, len(df)):
        if df["Volume"].iloc[i] < df["Volume"].iloc[i-1]:
            nvi.iloc[i] = nvi.iloc[i-1] * (1 + (df["Close"].iloc[i]-df["Close"].iloc[i-1])/df["Close"].iloc[i-1])
        else:
            nvi.iloc[i] = nvi.iloc[i-1]
    return nvi

def _pd_series_ones(df):
    import pandas as _pd
    return _pd.Series(1.0, index=df.index)

def accumulation_distribution(df):
    mfm = ((df["Close"]-df["Low"]) - (df["High"]-df["Close"])) / (df["High"]-df["Low"])
    return (mfm * df["Volume"]).cumsum()

def vortex(df, window=14):
    vm_pos = (df["High"] - df["Low"].shift(1)).abs().rolling(window).sum()
    vm_neg = (df["Low"]  - df["High"].shift(1)).abs().rolling(window).sum()
    tr_sum = atr(df, 1).rolling(window).sum()
    return {"vi_pos": vm_pos/tr_sum, "vi_neg": vm_neg/tr_sum}

def know_sure_thing(series):
    r1  = roc(series, 10).rolling(10).mean()
    r2  = roc(series, 15).rolling(10).mean()
    r3  = roc(series, 20).rolling(10).mean()
    r4  = roc(series, 30).rolling(15).mean()
    kst = r1 + 2*r2 + 3*r3 + 4*r4
    sig = kst.rolling(9).mean()
    return {"kst": kst, "signal": sig}

def schaff_trend_cycle(series, fast=23, slow=50, cycle=10):
    macd_line = series.ewm(span=fast).mean() - series.ewm(span=slow).mean()
    stc = _stoch_of(macd_line, cycle)
    return stc

def _stoch_of(series, window):
    lo = series.rolling(window).min()
    hi = series.rolling(window).max()
    return 100*(series - lo)/(hi - lo).replace(0, 1)

def rainbow_ma(series, periods=[2,3,4,5,6,7,8,9,10]):
    return {f"ema_{p}": ema(series, p) for p in periods}

def adaptive_moving_average(series, fast=2, slow=30):
    direction = (series - series.shift(10)).abs()
    noise     = (series.diff().abs()).rolling(10).sum()
    er        = (direction / noise).fillna(0)
    fast_sc   = 2/(fast+1); slow_sc = 2/(slow+1)
    sc        = (er*(fast_sc-slow_sc)+slow_sc)**2
    ama       = series.copy().astype(float)
    for i in range(1, len(series)):
        ama.iloc[i] = ama.iloc[i-1] + sc.iloc[i]*(series.iloc[i]-ama.iloc[i-1])
    return ama

def coppock_curve(series):
    r1  = roc(series, 14).rolling(11).mean()
    r2  = roc(series, 11).rolling(11).mean()
    return (r1 + r2).rolling(10).mean()

def connors_rsi(series, rsi_len=3, streak_len=2, pct_rank_len=100):
    rsi_main   = rsi(series, rsi_len)
    streaks    = _streak(series)
    rsi_streak = rsi(streaks, streak_len)
    pct        = series.pct_change() * 100
    pct_rank   = pct.rolling(pct_rank_len).apply(lambda x: (x[:-1] < x[-1]).mean() * 100, raw=True)
    return (rsi_main + rsi_streak + pct_rank) / 3

def _streak(series):
    import pandas as _pd
    streak = _pd.Series(0.0, index=series.index)
    for i in range(1, len(series)):
        if series.iloc[i] > series.iloc[i-1]:
            streak.iloc[i] = streak.iloc[i-1] + 1 if streak.iloc[i-1] > 0 else 1
        elif series.iloc[i] < series.iloc[i-1]:
            streak.iloc[i] = streak.iloc[i-1] - 1 if streak.iloc[i-1] < 0 else -1
        else:
            streak.iloc[i] = 0
    return streak

def dmi(df, window=14):
    plus_dm  = (df["High"] - df["High"].shift(1)).clip(lower=0)
    minus_dm = (df["Low"].shift(1) - df["Low"]).clip(lower=0)
    tr_s     = atr(df, 1).rolling(window).sum()
    plus_di  = 100 * plus_dm.rolling(window).sum()  / tr_s
    minus_di = 100 * minus_dm.rolling(window).sum() / tr_s
    dx       = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di)
    adx      = dx.rolling(window).mean()
    return {"adx": adx, "plus_di": plus_di, "minus_di": minus_di}

def price_oscillator(series, fast=12, slow=26):
    return (ema(series, fast) - ema(series, slow)) / ema(series, slow) * 100

def detrended_price(series, window=20):
    return dpo(series, window)

def qstick(df, window=8):
    return (df["Close"] - df["Open"]).rolling(window).mean()

def market_facilitation(df):
    return (df["High"] - df["Low"]) / df["Volume"]

# ── Extended INDICATOR_INFO ────────────────────────────────────────────────────
INDICATOR_INFO.update({
    "Stochastic": {
        "label": "Stochastic Oscillator", "overlay": False,
        "params": {"k_window":{"type":"int","default":14,"min":2,"max":50,"label":"K Period"},
                   "d_window":{"type":"int","default":3,"min":1,"max":10,"label":"D Period"}},
        "description": "K% and D% momentum oscillator. <20 oversold, >80 overbought.",
    },
    "MFI": {
        "label": "Money Flow Index", "overlay": False,
        "params": {"window":{"type":"int","default":14,"min":2,"max":50,"label":"Period"}},
        "description": "Volume-weighted RSI. Measures buying and selling pressure.",
    },
    "ROC": {
        "label": "Rate of Change", "overlay": False,
        "params": {"window":{"type":"int","default":12,"min":1,"max":50,"label":"Period"}},
        "description": "Percentage change in price over N periods. Momentum.",
    },
    "Momentum": {
        "label": "Momentum", "overlay": False,
        "params": {"window":{"type":"int","default":10,"min":1,"max":50,"label":"Period"}},
        "description": "Raw price difference over N periods. Trend strength.",
    },
    "TRIX": {
        "label": "TRIX", "overlay": False,
        "params": {"window":{"type":"int","default":15,"min":2,"max":50,"label":"Period"}},
        "description": "Triple-smoothed EMA rate of change. Filters noise well.",
    },
    "DEMA": {
        "label": "Double EMA", "overlay": True,
        "params": {"window":{"type":"int","default":20,"min":2,"max":200,"label":"Period"}},
        "description": "Double Exponential Moving Average. Less lag than EMA.",
    },
    "TEMA": {
        "label": "Triple EMA", "overlay": True,
        "params": {"window":{"type":"int","default":20,"min":2,"max":200,"label":"Period"}},
        "description": "Triple Exponential Moving Average. Minimal lag.",
    },
    "Aroon": {
        "label": "Aroon Indicator", "overlay": False,
        "params": {"window":{"type":"int","default":25,"min":5,"max":100,"label":"Period"}},
        "description": "Measures time since last high/low. Identifies trend changes.",
    },
    "Ultimate Oscillator": {
        "label": "Ultimate Oscillator", "overlay": False,
        "params": {},
        "description": "Combines 3 timeframes to reduce false signals.",
    },
    "CMO": {
        "label": "Chande Momentum Oscillator", "overlay": False,
        "params": {"window":{"type":"int","default":20,"min":5,"max":50,"label":"Period"}},
        "description": "Unbounded momentum. +100 max bullish, -100 max bearish.",
    },
    "DPO": {
        "label": "Detrended Price Oscillator", "overlay": False,
        "params": {"window":{"type":"int","default":20,"min":5,"max":50,"label":"Period"}},
        "description": "Removes long-term trend to identify cycles.",
    },
    "Mass Index": {
        "label": "Mass Index", "overlay": False,
        "params": {"slow":{"type":"int","default":25,"min":10,"max":50,"label":"Sum Period"}},
        "description": "Identifies reversals using high-low range expansion.",
    },
    "ADX": {
        "label": "Average Directional Index", "overlay": False,
        "params": {"window":{"type":"int","default":14,"min":2,"max":50,"label":"Period"}},
        "description": "Trend strength 0-100. >25 strong trend, <20 weak.",
    },
    "Chaikin MF": {
        "label": "Chaikin Money Flow", "overlay": False,
        "params": {"window":{"type":"int","default":20,"min":5,"max":50,"label":"Period"}},
        "description": "Accumulation/distribution over period. Positive = buying pressure.",
    },
    "Force Index": {
        "label": "Force Index", "overlay": False,
        "params": {"window":{"type":"int","default":13,"min":2,"max":50,"label":"Period"}},
        "description": "Price change × volume. Measures force behind price moves.",
    },
    "Ease of Movement": {
        "label": "Ease of Movement", "overlay": False,
        "params": {"window":{"type":"int","default":14,"min":2,"max":50,"label":"Period"}},
        "description": "Relates price movement to volume. High = easy price movement.",
    },
    "Vortex": {
        "label": "Vortex Indicator", "overlay": False,
        "params": {"window":{"type":"int","default":14,"min":2,"max":50,"label":"Period"}},
        "description": "VI+ and VI- identify start of new trends.",
    },
    "KST": {
        "label": "Know Sure Thing", "overlay": False,
        "params": {},
        "description": "Momentum oscillator combining 4 smoothed ROC periods.",
    },
    "STC": {
        "label": "Schaff Trend Cycle", "overlay": False,
        "params": {"fast":{"type":"int","default":23,"min":5,"max":50,"label":"Fast"},
                   "slow":{"type":"int","default":50,"min":10,"max":100,"label":"Slow"}},
        "description": "Combines MACD and Stochastic to identify cycle turns.",
    },
    "AMA": {
        "label": "Adaptive Moving Average", "overlay": True,
        "params": {"fast":{"type":"int","default":2,"min":2,"max":20,"label":"Fast"},
                   "slow":{"type":"int","default":30,"min":10,"max":100,"label":"Slow"}},
        "description": "Adjusts speed based on market efficiency. Kaufman's AMA.",
    },
    "Coppock Curve": {
        "label": "Coppock Curve", "overlay": False,
        "params": {},
        "description": "Long-term buy signal. Developed for monthly charts.",
    },
    "Connors RSI": {
        "label": "Connors RSI", "overlay": False,
        "params": {},
        "description": "3-component RSI for short-term mean reversion.",
    },
    "Price Oscillator": {
        "label": "Price Oscillator (PPO)", "overlay": False,
        "params": {"fast":{"type":"int","default":12,"min":2,"max":50,"label":"Fast"},
                   "slow":{"type":"int","default":26,"min":5,"max":200,"label":"Slow"}},
        "description": "EMA difference as percentage. Like MACD but normalised.",
    },
    "Historical Volatility": {
        "label": "Historical Volatility", "overlay": False,
        "params": {"window":{"type":"int","default":20,"min":5,"max":100,"label":"Period"}},
        "description": "Annualised standard deviation of log returns.",
    },
    "Std Deviation": {
        "label": "Standard Deviation", "overlay": False,
        "params": {"window":{"type":"int","default":20,"min":5,"max":100,"label":"Period"}},
        "description": "Rolling price standard deviation. Volatility measure.",
    },
    "Linear Reg Slope": {
        "label": "Linear Regression Slope", "overlay": False,
        "params": {"window":{"type":"int","default":14,"min":3,"max":100,"label":"Period"}},
        "description": "Slope of linear regression line. Positive = uptrend.",
    },
    "Envelope": {
        "label": "Moving Average Envelope", "overlay": True,
        "params": {"window":{"type":"int","default":20,"min":5,"max":200,"label":"Period"},
                   "pct":{"type":"float","default":0.025,"min":0.005,"max":0.2,"label":"% Width"}},
        "description": "Upper/lower bands at fixed % from SMA. Trend channel.",
    },
    "Price Channel": {
        "label": "Price Channel", "overlay": True,
        "params": {"window":{"type":"int","default":20,"min":5,"max":200,"label":"Period"}},
        "description": "Highest high / lowest low channel over N periods.",
    },
    "QStick": {
        "label": "QStick", "overlay": False,
        "params": {"window":{"type":"int","default":8,"min":2,"max":50,"label":"Period"}},
        "description": "Average of open-close difference. Candlestick momentum.",
    },
    "AD Line": {
        "label": "Accumulation/Distribution", "overlay": False,
        "params": {},
        "description": "Cumulative volume-weighted price indicator. Divergence signals.",
    },
    "VWAP": {
        "label": "VWAP", "overlay": True,
        "params": {},
        "description": "Volume Weighted Average Price. Institutional reference level.",
    },
    "OBV": {
        "label": "On-Balance Volume", "overlay": False,
        "params": {},
        "description": "Cumulative volume flow. Divergence with price = signal.",
    },
    "Pivot Points": {
        "label": "Pivot Points", "overlay": True,
        "params": {},
        "description": "Daily pivot, S1/S2, R1/R2 support/resistance levels.",
    },
    "Elder Ray": {
        "label": "Elder Ray Index", "overlay": False,
        "params": {"window":{"type":"int","default":13,"min":2,"max":50,"label":"EMA Period"}},
        "description": "Bull/bear power relative to EMA. Elder's system.",
    },
    "Chaikin Osc": {
        "label": "Chaikin Oscillator", "overlay": False,
        "params": {"fast":{"type":"int","default":3,"min":1,"max":20,"label":"Fast"},
                   "slow":{"type":"int","default":10,"min":3,"max":50,"label":"Slow"}},
        "description": "EMA difference of Accumulation/Distribution line.",
    },
    "Klinger Osc": {
        "label": "Klinger Volume Oscillator", "overlay": False,
        "params": {},
        "description": "Long-term money flow trend with short-term fluctuations.",
    },
    "NVI": {
        "label": "Negative Volume Index", "overlay": False,
        "params": {},
        "description": "Tracks price change on down-volume days. Smart money proxy.",
    },
    "MFI Divergence": {
        "label": "MFI (Extended)", "overlay": False,
        "params": {"window":{"type":"int","default":14,"min":2,"max":50,"label":"Period"}},
        "description": "Money Flow Index with divergence detection.",
    },
    "Market Facilitation": {
        "label": "Market Facilitation Index", "overlay": False,
        "params": {},
        "description": "(High-Low)/Volume. Measures efficiency of price movement.",
    },
    "Rainbow MA": {
        "label": "Rainbow Moving Averages", "overlay": True,
        "params": {},
        "description": "9 EMAs (2-10 periods). Creates a rainbow of trend bands.",
    },
    "Vidya": {
        "label": "Variable Index Dynamic Average", "overlay": True,
        "params": {"window":{"type":"int","default":14,"min":2,"max":50,"label":"VI Period"}},
        "description": "Adaptive MA using RSI-based volatility index.",
    },
})
