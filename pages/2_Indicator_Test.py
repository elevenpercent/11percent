import streamlit as st
import pandas as pd
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from datetime import date, timedelta

from utils.styles import SHARED_CSS
from utils.data import get_stock_data
from utils.strategies import run_backtest
from utils.charts import chart_candles, chart_portfolio, chart_rsi, chart_stoch_rsi, chart_macd, chart_bollinger, chart_supertrend, chart_ichimoku
from utils.indicators import (
    sma, ema, wma, rsi, stoch_rsi, macd, bollinger_bands,
    atr, supertrend, vwap, obv, ichimoku, INDICATOR_INFO
)

st.set_page_config(page_title="Indicator Test | 11%", page_icon="📊", layout="wide")
st.markdown(SHARED_CSS, unsafe_allow_html=True)


def build_indicator_params(ind_name: str, key_prefix: str) -> dict:
    """Dynamically render parameter sliders for any indicator."""
    info = INDICATOR_INFO[ind_name]
    params = {}
    for param_key, p in info["params"].items():
        if p["type"] == "int":
            params[param_key] = st.slider(
                p["label"], p["min"], p["max"], p["default"], key=f"{key_prefix}_{param_key}"
            )
        elif p["type"] == "float":
            params[param_key] = st.slider(
                p["label"], float(p["min"]), float(p["max"]), float(p["default"]),
                step=0.1, key=f"{key_prefix}_{param_key}"
            )
    return params


def compute_indicator(ind_name: str, df: pd.DataFrame, params: dict):
    """Compute indicator values. Returns dict or Series."""
    if ind_name == "SMA":
        return sma(df["Close"], params["window"])
    elif ind_name == "EMA":
        return ema(df["Close"], params["window"])
    elif ind_name == "WMA":
        return wma(df["Close"], params["window"])
    elif ind_name == "RSI":
        return rsi(df["Close"], params["window"])
    elif ind_name == "Stoch RSI":
        return stoch_rsi(df["Close"], params["rsi_window"], params["stoch_window"],
                         params["smooth_k"], params["smooth_d"])
    elif ind_name == "MACD":
        return macd(df["Close"], params["fast"], params["slow"], params["signal"])
    elif ind_name == "Bollinger Bands":
        return bollinger_bands(df["Close"], params["window"], params["num_std"])
    elif ind_name == "SuperTrend":
        return supertrend(df, params["window"], params["multiplier"])
    elif ind_name == "Ichimoku":
        return ichimoku(df, params["tenkan_window"], params["kijun_window"], params["senkou_b_window"])
    return None


def generate_signals(ind_name: str, ind_data, condition_buy: str, condition_sell: str,
                     df: pd.DataFrame, params: dict) -> pd.Series:
    """
    Convert indicator data + user condition into a buy/sell signal series.
    condition_buy/sell: string description chosen from dropdown.
    """
    sig = pd.Series(0, index=df.index)

    if ind_name == "RSI":
        oversold   = params.get("oversold", 30)
        overbought = params.get("overbought", 70)
        if condition_buy  == "RSI below oversold":  sig[ind_data < oversold]  = 1
        if condition_buy  == "RSI crosses above 50": sig[ind_data > 50] = 1
        if condition_sell == "RSI above overbought": sig[ind_data > overbought] = -1
        if condition_sell == "RSI crosses below 50": sig[ind_data < 50] = -1

    elif ind_name == "Stoch RSI":
        k = ind_data["k"]
        if condition_buy  == "%K crosses above %D": sig[(k > ind_data["d"]) & (k.shift() <= ind_data["d"].shift())] = 1
        if condition_buy  == "%K below 20":          sig[k < 20] = 1
        if condition_sell == "%K crosses below %D": sig[(k < ind_data["d"]) & (k.shift() >= ind_data["d"].shift())] = -1
        if condition_sell == "%K above 80":          sig[k > 80] = -1

    elif ind_name == "MACD":
        m, s = ind_data["macd"], ind_data["signal"]
        if condition_buy  == "MACD crosses above Signal": sig[(m > s) & (m.shift() <= s.shift())] = 1
        if condition_buy  == "MACD above 0":              sig[m > 0] = 1
        if condition_sell == "MACD crosses below Signal": sig[(m < s) & (m.shift() >= s.shift())] = -1
        if condition_sell == "MACD below 0":              sig[m < 0] = -1

    elif ind_name in ["SMA", "EMA", "WMA"]:
        if condition_buy  == "Price crosses above MA": sig[(df["Close"] > ind_data) & (df["Close"].shift() <= ind_data.shift())] = 1
        if condition_buy  == "Price above MA":         sig[df["Close"] > ind_data] = 1
        if condition_sell == "Price crosses below MA": sig[(df["Close"] < ind_data) & (df["Close"].shift() >= ind_data.shift())] = -1
        if condition_sell == "Price below MA":         sig[df["Close"] < ind_data] = -1

    elif ind_name == "Bollinger Bands":
        if condition_buy  == "Price below lower band": sig[df["Close"] < ind_data["lower"]] = 1
        if condition_buy  == "%B below 0":             sig[ind_data["percent_b"] < 0] = 1
        if condition_sell == "Price above upper band": sig[df["Close"] > ind_data["upper"]] = -1
        if condition_sell == "%B above 100":           sig[ind_data["percent_b"] > 100] = -1

    elif ind_name == "SuperTrend":
        if condition_buy  == "Direction turns bullish":  sig[(ind_data["direction"] == 1) & (ind_data["direction"].shift() == -1)] = 1
        if condition_buy  == "Price above SuperTrend":   sig[df["Close"] > ind_data["supertrend"]] = 1
        if condition_sell == "Direction turns bearish":  sig[(ind_data["direction"] == -1) & (ind_data["direction"].shift() == 1)] = -1
        if condition_sell == "Price below SuperTrend":   sig[df["Close"] < ind_data["supertrend"]] = -1

    elif ind_name == "Ichimoku":
        tenkan = ind_data["tenkan_sen"]
        kijun  = ind_data["kijun_sen"]
        span_a = ind_data["senkou_span_a"]
        span_b = ind_data["senkou_span_b"]
        cloud_top    = pd.concat([span_a, span_b], axis=1).max(axis=1)
        cloud_bottom = pd.concat([span_a, span_b], axis=1).min(axis=1)
        if condition_buy  == "Tenkan crosses above Kijun": sig[(tenkan > kijun) & (tenkan.shift() <= kijun.shift())] = 1
        if condition_buy  == "Price above Cloud":          sig[df["Close"] > cloud_top] = 1
        if condition_sell == "Tenkan crosses below Kijun": sig[(tenkan < kijun) & (tenkan.shift() >= kijun.shift())] = -1
        if condition_sell == "Price below Cloud":          sig[df["Close"] < cloud_bottom] = -1

    return sig


# Conditions per indicator
CONDITIONS = {
    "RSI":           {"buy": ["RSI below oversold", "RSI crosses above 50"], "sell": ["RSI above overbought", "RSI crosses below 50"]},
    "Stoch RSI":     {"buy": ["%K crosses above %D", "%K below 20"],         "sell": ["%K crosses below %D", "%K above 80"]},
    "MACD":          {"buy": ["MACD crosses above Signal", "MACD above 0"],  "sell": ["MACD crosses below Signal", "MACD below 0"]},
    "SMA":           {"buy": ["Price crosses above MA", "Price above MA"],   "sell": ["Price crosses below MA", "Price below MA"]},
    "EMA":           {"buy": ["Price crosses above MA", "Price above MA"],   "sell": ["Price crosses below MA", "Price below MA"]},
    "WMA":           {"buy": ["Price crosses above MA", "Price above MA"],   "sell": ["Price crosses below MA", "Price below MA"]},
    "Bollinger Bands":{"buy": ["Price below lower band", "%B below 0"],       "sell": ["Price above upper band", "%B above 100"]},
    "SuperTrend":    {"buy": ["Direction turns bullish", "Price above SuperTrend"], "sell": ["Direction turns bearish", "Price below SuperTrend"]},
    "Ichimoku":      {"buy": ["Tenkan crosses above Kijun", "Price above Cloud"],   "sell": ["Tenkan crosses below Kijun", "Price below Cloud"]},
}


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div style="font-family:\'Bebas Neue\',sans-serif;font-size:1.8rem;color:#f0b429;letter-spacing:0.1em;">11%</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### SETTINGS")

    ticker = st.text_input("Ticker", value="AAPL").upper().strip()
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start", value=date.today() - timedelta(days=365*2))
    with col2:
        end_date = st.date_input("End", value=date.today())
    capital = st.number_input("Capital ($)", value=10000, min_value=100, step=1000)

    mode = st.radio("Mode", ["Single Indicator", "Combo (2–3 Indicators)"], horizontal=True)

    ind_names = list(INDICATOR_INFO.keys())
    run_btn = st.button("▶  RUN TEST", use_container_width=True)


# ── Page header ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
    <h1>INDICATOR TEST</h1>
    <p>Set your buy/sell conditions using single or combo indicators. Max 3 indicators in combo mode.</p>
</div>
""", unsafe_allow_html=True)

# ── Indicator config ──────────────────────────────────────────────────────────
if mode == "Single Indicator":
    st.markdown("### INDICATOR")
    col_sel, col_buy, col_sell = st.columns(3)
    with col_sel:
        ind1 = st.selectbox("Indicator", ind_names, key="ind1")
    with col_buy:
        buy1 = st.selectbox("Buy When", CONDITIONS[ind1]["buy"], key="buy1")
    with col_sell:
        sell1 = st.selectbox("Sell When", CONDITIONS[ind1]["sell"], key="sell1")

    with st.expander("⚙️ Parameters"):
        params1 = build_indicator_params(ind1, "p1")

    indicator_config = [{"name": ind1, "params": params1, "buy": buy1, "sell": sell1}]

else:
    num_indicators = st.slider("Number of indicators to combine", 2, 3, 2)
    indicator_config = []
    combo_logic = st.radio("Combo Logic", ["ALL conditions must be met (AND)", "ANY condition met (OR)"], horizontal=True)

    for i in range(num_indicators):
        st.markdown(f"### INDICATOR {i+1}")
        col_sel, col_buy, col_sell = st.columns(3)
        with col_sel:
            ind = st.selectbox(f"Indicator {i+1}", ind_names, key=f"ind{i}")
        with col_buy:
            buy = st.selectbox("Buy When", CONDITIONS[ind]["buy"], key=f"buy{i}")
        with col_sell:
            sell = st.selectbox("Sell When", CONDITIONS[ind]["sell"], key=f"sell{i}")
        with st.expander(f"⚙️ Parameters — Indicator {i+1}"):
            params = build_indicator_params(ind, f"p{i}")
        indicator_config.append({"name": ind, "params": params, "buy": buy, "sell": sell})

# ── Run ───────────────────────────────────────────────────────────────────────
if run_btn:
    with st.spinner(f"Loading {ticker}..."):
        df = get_stock_data(ticker, str(start_date), str(end_date))
    if df.empty:
        st.stop()

    with st.spinner("Computing indicators and signals..."):
        try:
            all_buy_signals  = []
            all_sell_signals = []
            computed = []

            for cfg in indicator_config:
                ind_data = compute_indicator(cfg["name"], df, cfg["params"])
                sigs = generate_signals(cfg["name"], ind_data, cfg["buy"], cfg["sell"], df, cfg["params"])
                all_buy_signals.append(sigs == 1)
                all_sell_signals.append(sigs == -1)
                computed.append({"name": cfg["name"], "data": ind_data, "params": cfg["params"]})

            # Combine signals
            if mode == "Single Indicator" or "AND" in combo_logic:
                buy_final  = pd.concat(all_buy_signals,  axis=1).all(axis=1)
                sell_final = pd.concat(all_sell_signals, axis=1).all(axis=1)
            else:  # OR
                buy_final  = pd.concat(all_buy_signals,  axis=1).any(axis=1)
                sell_final = pd.concat(all_sell_signals, axis=1).any(axis=1)

            combined = pd.Series(0, index=df.index)
            combined[buy_final]  = 1
            combined[sell_final] = -1

            result = run_backtest(df, combined, float(capital))
        except Exception as e:
            st.error(f"Error: {e}")
            st.stop()

    m = result["metrics"]
    port = result["portfolio"]
    trades = result["trades"]

    # ── Metrics ───────────────────────────────────────────────────────────────
    st.markdown("### PERFORMANCE")
    cols = st.columns(7)
    metrics_data = [
        (m["total_return"], "Strategy Return", "pct"),
        (m["bh_return"],    "Buy & Hold",      "pct"),
        (m["max_drawdown"], "Max Drawdown",     "pct"),
        (m["final_value"],  "Final Value",      "usd"),
        (m["win_rate"],     "Win Rate",         "pct"),
        (m["sharpe"],       "Sharpe",           "raw"),
        (m["num_trades"],   "Trades",           "int"),
    ]
    for col, (val, lbl, fmt) in zip(cols, metrics_data):
        if fmt == "pct":
            cls = "pos" if val >= 0 else "neg"
            disp = f"{val:+.2f}%"
        elif fmt == "usd":
            cls = "neu"; disp = f"${val:,.0f}"
        else:
            cls = "neu"; disp = f"{val:.2f}" if isinstance(val, float) else str(val)
        col.markdown(f'<div class="metric-card"><div class="metric-val {cls}">{disp}</div><div class="metric-lbl">{lbl}</div></div>', unsafe_allow_html=True)

    # ── Charts ────────────────────────────────────────────────────────────────
    st.markdown("### CHARTS")

    # Main price chart with overlays
    overlays = {}
    for c in computed:
        if INDICATOR_INFO[c["name"]]["overlay"]:
            if c["name"] in ["SMA", "EMA", "WMA"]:
                overlays[f"{c['name']} {c['params']['window']}"] = c["data"]
            elif c["name"] == "SuperTrend":
                overlays["ST Bull"] = c["data"]["supertrend"].where(c["data"]["direction"] == 1)
                overlays["ST Bear"] = c["data"]["supertrend"].where(c["data"]["direction"] == -1)

    st.plotly_chart(chart_candles(df, trades, overlays=overlays if overlays else None,
                                   title=f"{ticker} — Indicator Test"), use_container_width=True)

    # Sub-charts for oscillators
    for c in computed:
        name = c["name"]
        if name == "RSI":
            st.plotly_chart(chart_rsi(c["data"], c["params"].get("oversold", 30), c["params"].get("overbought", 70)), use_container_width=True)
        elif name == "Stoch RSI":
            st.plotly_chart(chart_stoch_rsi(c["data"]["k"], c["data"]["d"]), use_container_width=True)
        elif name == "MACD":
            st.plotly_chart(chart_macd(c["data"]["macd"], c["data"]["signal"], c["data"]["histogram"]), use_container_width=True)
        elif name == "Bollinger Bands":
            st.plotly_chart(chart_bollinger(df, c["data"]), use_container_width=True)
        elif name == "Ichimoku":
            st.plotly_chart(chart_ichimoku(df, c["data"]), use_container_width=True)

    st.plotly_chart(chart_portfolio(port, df, float(capital)), use_container_width=True)

    if not trades.empty:
        with st.expander("📋 TRADE LOG"):
            st.dataframe(trades.set_index("date"), use_container_width=True)

    st.session_state["last_backtest"] = {
        "ticker": ticker,
        "strategy": f"Custom: {' + '.join([c['name'] for c in indicator_config])}",
        "params": {c["name"]: c["params"] for c in indicator_config},
        "metrics": m,
    }

else:
    st.markdown('<div class="info-box">← Pick your indicator(s), set your conditions, and hit RUN TEST.</div>', unsafe_allow_html=True)
