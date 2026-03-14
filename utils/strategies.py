"""
Backtesting engine + pre-built strategies for 11% platform.
"""
import pandas as pd
import numpy as np
from utils.indicators import sma, ema, wma, rsi, stoch_rsi, macd, bollinger_bands, supertrend, ichimoku


# -----------------------------------------------------------------
# CORE BACKTEST ENGINE
# -----------------------------------------------------------------

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


# -----------------------------------------------------------------
# PRE-BUILT STRATEGIES
# Each returns a pd.Series of signals: 1 / -1 / 0
# -----------------------------------------------------------------

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
    """EMA crossover - faster than SMA version."""
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


# ── Additional strategies ─────────────────────────────────────────────────────
from utils.indicators import (ema, sma, rsi, macd, bollinger_bands, supertrend,
                               stochastic, mfi, roc, aroon, dmi, chaikin_money_flow,
                               vwap, obv, atr, momentum, hull_ma, cci, williams_r,
                               donchian_channels, keltner_channels, parabolic_sar,
                               tema, dema, schaff_trend_cycle, price_oscillator,
                               force_index, chande_momentum)

def strategy_stoch_rsi_combo(df, k=14, d=3, rsi_w=14, ob=80, os=20):
    stoch = stochastic(df, k, d)
    rsi_v = rsi(df["Close"], rsi_w)
    sig = pd.Series(0, index=df.index)
    sig[(stoch["k"] < os) & (rsi_v < 35)] = 1
    sig[(stoch["k"] > ob) & (rsi_v > 65)] = -1
    return sig

def strategy_dual_ma_rsi(df, fast=10, slow=30, rsi_w=14):
    f = ema(df["Close"], fast); sl = ema(df["Close"], slow)
    r = rsi(df["Close"], rsi_w)
    sig = pd.Series(0, index=df.index)
    sig[(f > sl) & (r > 50) & (f.shift() <= sl.shift())] = 1
    sig[(f < sl) & (r < 50) & (f.shift() >= sl.shift())] = -1
    return sig

def strategy_aroon_trend(df, window=25, threshold=70):
    ar = aroon(df, window)
    sig = pd.Series(0, index=df.index)
    sig[(ar["up"] > threshold) & (ar["down"] < 100-threshold)] = 1
    sig[(ar["down"] > threshold) & (ar["up"] < 100-threshold)] = -1
    return sig

def strategy_adx_directional(df, window=14, adx_thresh=25):
    dm = dmi(df, window)
    sig = pd.Series(0, index=df.index)
    sig[(dm["adx"] > adx_thresh) & (dm["plus_di"] > dm["minus_di"])] = 1
    sig[(dm["adx"] > adx_thresh) & (dm["minus_di"] > dm["plus_di"])] = -1
    return sig

def strategy_vwap_bounce(df, rsi_w=14, ob=60, os=40):
    v = vwap(df); r = rsi(df["Close"], rsi_w)
    sig = pd.Series(0, index=df.index)
    sig[(df["Close"] > v) & (r > ob) & (df["Close"].shift() <= v.shift())] = 1
    sig[(df["Close"] < v) & (r < os) & (df["Close"].shift() >= v.shift())] = -1
    return sig

def strategy_bb_squeeze(df, bb_w=20, kc_w=20, rsi_w=14):
    bb = bollinger_bands(df["Close"], bb_w)
    kc = keltner_channels(df, kc_w)
    r  = rsi(df["Close"], rsi_w)
    squeeze = (bb["upper"] < kc["upper"]) & (bb["lower"] > kc["lower"])
    sig = pd.Series(0, index=df.index)
    sig[squeeze & (r > 55)] = 1
    sig[squeeze & (r < 45)] = -1
    return sig

def strategy_hull_cross(df, fast=9, slow=25):
    hf = hull_ma(df["Close"], fast); hs = hull_ma(df["Close"], slow)
    sig = pd.Series(0, index=df.index)
    sig[(hf > hs) & (hf.shift() <= hs.shift())] = 1
    sig[(hf < hs) & (hf.shift() >= hs.shift())] = -1
    return sig

def strategy_cci_zero_cross(df, window=20):
    c = cci(df, window)
    sig = pd.Series(0, index=df.index)
    sig[(c > 0) & (c.shift() <= 0)] = 1
    sig[(c < 0) & (c.shift() >= 0)] = -1
    return sig

def strategy_mfi_reversal(df, window=14, ob=80, os=20):
    m = mfi(df, window)
    sig = pd.Series(0, index=df.index)
    sig[(m < os) & (m.shift() >= os)] = 1
    sig[(m > ob) & (m.shift() <= ob)] = -1
    return sig

def strategy_donchian_breakout(df, window=20):
    dc = donchian_channels(df, window)
    sig = pd.Series(0, index=df.index)
    sig[df["Close"] >= dc["upper"]] = 1
    sig[df["Close"] <= dc["lower"]] = -1
    return sig

def strategy_parabolic_ema(df, af_s=0.02, af_m=0.2, ema_w=50):
    psar = parabolic_sar(df, af_s, af_m)
    e    = ema(df["Close"], ema_w)
    sig  = pd.Series(0, index=df.index)
    sig[(psar["direction"] == 1) & (df["Close"] > e)] = 1
    sig[(psar["direction"] == -1) & (df["Close"] < e)] = -1
    return sig

def strategy_triple_ema(df, fast=5, mid=13, slow=34):
    f = ema(df["Close"], fast)
    m = ema(df["Close"], mid)
    s = ema(df["Close"], slow)
    sig = pd.Series(0, index=df.index)
    sig[(f > m) & (m > s) & (f.shift() <= m.shift())] = 1
    sig[(f < m) & (m < s) & (f.shift() >= m.shift())] = -1
    return sig

def strategy_roc_crossover(df, fast_w=5, slow_w=15, zero_filter=True):
    from utils.indicators import roc as _roc
    rf = _roc(df["Close"], fast_w); rs = _roc(df["Close"], slow_w)
    sig = pd.Series(0, index=df.index)
    cond_b = (rf > rs) & (rf.shift() <= rs.shift())
    cond_s = (rf < rs) & (rf.shift() >= rs.shift())
    if zero_filter:
        cond_b &= rf > 0; cond_s &= rf < 0
    sig[cond_b] = 1; sig[cond_s] = -1
    return sig

def strategy_stochastic_cross(df, k=14, d=3, ob=80, os=20):
    stoch = stochastic(df, k, d)
    sig   = pd.Series(0, index=df.index)
    sig[(stoch["k"] > stoch["d"]) & (stoch["k"].shift() <= stoch["d"].shift()) & (stoch["k"] < ob)] = 1
    sig[(stoch["k"] < stoch["d"]) & (stoch["k"].shift() >= stoch["d"].shift()) & (stoch["k"] > os)] = -1
    return sig

def strategy_chaikin_mf(df, window=20, ema_w=20):
    cmf = chaikin_money_flow(df, window)
    e   = ema(df["Close"], ema_w)
    sig = pd.Series(0, index=df.index)
    sig[(cmf > 0) & (df["Close"] > e)] = 1
    sig[(cmf < 0) & (df["Close"] < e)] = -1
    return sig

def strategy_williams_bb(df, wr_w=14, bb_w=20):
    wr  = williams_r(df, wr_w)
    bb  = bollinger_bands(df["Close"], bb_w)
    sig = pd.Series(0, index=df.index)
    sig[(wr < -80) & (df["Close"] <= bb["lower"])] = 1
    sig[(wr > -20) & (df["Close"] >= bb["upper"])] = -1
    return sig

def strategy_cmo_signal(df, window=20, threshold=10):
    c = chande_momentum(df["Close"], window)
    sig = pd.Series(0, index=df.index)
    sig[(c > threshold) & (c.shift() <= threshold)] = 1
    sig[(c < -threshold) & (c.shift() >= -threshold)] = -1
    return sig

def strategy_force_rsi(df, fi_w=13, rsi_w=14):
    fi  = force_index(df, fi_w)
    r   = rsi(df["Close"], rsi_w)
    sig = pd.Series(0, index=df.index)
    sig[(fi > 0) & (r < 60) & (fi.shift() <= 0)] = 1
    sig[(fi < 0) & (r > 40) & (fi.shift() >= 0)] = -1
    return sig

def strategy_ma_ribbon(df, periods=None):
    if periods is None: periods = [5,10,20,50]
    emas = [ema(df["Close"], p) for p in periods]
    sig  = pd.Series(0, index=df.index)
    bull = all(emas[i].iloc[-1] > emas[i+1].iloc[-1] for i in range(len(emas)-1))
    bear = all(emas[i].iloc[-1] < emas[i+1].iloc[-1] for i in range(len(emas)-1))
    for i in range(1, len(df)):
        b = all(emas[j].iloc[i] > emas[j+1].iloc[i] for j in range(len(emas)-1))
        s = all(emas[j].iloc[i] < emas[j+1].iloc[i] for j in range(len(emas)-1))
        pb = all(emas[j].iloc[i-1] > emas[j+1].iloc[i-1] for j in range(len(emas)-1))
        if b and not pb: sig.iloc[i] = 1
        elif s and pb:   sig.iloc[i] = -1
    return sig

def strategy_keltner_rsi(df, kc_w=20, rsi_w=14):
    kc = keltner_channels(df, kc_w)
    r  = rsi(df["Close"], rsi_w)
    sig = pd.Series(0, index=df.index)
    sig[(df["Close"] < kc["lower"]) & (r < 35)] = 1
    sig[(df["Close"] > kc["upper"]) & (r > 65)] = -1
    return sig

def strategy_tema_cross(df, fast=12, slow=26):
    tf = tema(df["Close"], fast); ts = tema(df["Close"], slow)
    sig = pd.Series(0, index=df.index)
    sig[(tf > ts) & (tf.shift() <= ts.shift())] = 1
    sig[(tf < ts) & (tf.shift() >= ts.shift())] = -1
    return sig

def strategy_ppo_signal(df, fast=12, slow=26):
    ppo = price_oscillator(df["Close"], fast, slow)
    sig = pd.Series(0, index=df.index)
    sig[(ppo > 0) & (ppo.shift() <= 0)] = 1
    sig[(ppo < 0) & (ppo.shift() >= 0)] = -1
    return sig

def strategy_atr_breakout(df, window=14, mult=1.5, ema_w=20):
    a   = atr(df, window)
    e   = ema(df["Close"], ema_w)
    upper = e + mult * a; lower = e - mult * a
    sig = pd.Series(0, index=df.index)
    sig[(df["Close"] > upper) & (df["Close"].shift() <= upper.shift())] = 1
    sig[(df["Close"] < lower) & (df["Close"].shift() >= lower.shift())] = -1
    return sig

def strategy_supertrend_ema(df, st_w=10, st_m=3.0, ema_w=200):
    st  = supertrend(df, st_w, st_m)
    e   = ema(df["Close"], ema_w)
    sig = pd.Series(0, index=df.index)
    sig[(st["direction"] == 1) & (df["Close"] > e)] = 1
    sig[(st["direction"] == -1) & (df["Close"] < e)] = -1
    return sig

# Register new strategies
STRATEGY_REGISTRY.update({
    "Stoch + RSI":         {"fn": strategy_stoch_rsi_combo,  "params": []},
    "Dual EMA + RSI":      {"fn": strategy_dual_ma_rsi,      "params": []},
    "Aroon Trend":         {"fn": strategy_aroon_trend,       "params": []},
    "ADX Directional":     {"fn": strategy_adx_directional,  "params": []},
    "VWAP Bounce":         {"fn": strategy_vwap_bounce,       "params": []},
    "BB Squeeze":          {"fn": strategy_bb_squeeze,        "params": []},
    "Hull MA Cross":       {"fn": strategy_hull_cross,        "params": []},
    "CCI Zero Cross":      {"fn": strategy_cci_zero_cross,    "params": []},
    "MFI Reversal":        {"fn": strategy_mfi_reversal,      "params": []},
    "Donchian Breakout":   {"fn": strategy_donchian_breakout, "params": []},
    "Parabolic + EMA":     {"fn": strategy_parabolic_ema,     "params": []},
    "Triple EMA":          {"fn": strategy_triple_ema,        "params": []},
    "ROC Crossover":       {"fn": strategy_roc_crossover,     "params": []},
    "Stochastic Cross":    {"fn": strategy_stochastic_cross,  "params": []},
    "Chaikin MF + EMA":    {"fn": strategy_chaikin_mf,        "params": []},
    "Williams + BB":       {"fn": strategy_williams_bb,       "params": []},
    "CMO Signal":          {"fn": strategy_cmo_signal,        "params": []},
    "Force + RSI":         {"fn": strategy_force_rsi,         "params": []},
    "MA Ribbon":           {"fn": strategy_ma_ribbon,         "params": []},
    "Keltner + RSI":       {"fn": strategy_keltner_rsi,       "params": []},
    "TEMA Cross":          {"fn": strategy_tema_cross,        "params": []},
    "PPO Signal":          {"fn": strategy_ppo_signal,        "params": []},
    "ATR Breakout":        {"fn": strategy_atr_breakout,      "params": []},
    "SuperTrend + EMA200": {"fn": strategy_supertrend_ema,    "params": []},
})
