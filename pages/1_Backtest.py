import streamlit as st
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from datetime import date, timedelta

from utils.styles import SHARED_CSS
from utils.data import get_stock_data, get_ticker_info
from utils.strategies import STRATEGY_REGISTRY, run_backtest
from utils.charts import chart_candles, chart_portfolio, chart_rsi, chart_macd, chart_bollinger, chart_supertrend, chart_ichimoku
from utils.indicators import rsi, macd, bollinger_bands, supertrend, ichimoku

st.set_page_config(page_title="Backtest | 11%", page_icon="🔬", layout="wide")
st.markdown(SHARED_CSS, unsafe_allow_html=True)

with st.sidebar:
    st.markdown('<div style="font-family:\'Bebas Neue\',sans-serif;font-size:1.8rem;color:#f0b429;letter-spacing:0.1em;">11%</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### SETTINGS")

    ticker = st.text_input("Ticker Symbol", value="AAPL", help="e.g. AAPL, TSLA, SPY, BTC-USD").upper().strip()

    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start", value=date.today() - timedelta(days=365*3))
    with col2:
        end_date = st.date_input("End", value=date.today())

    capital = st.number_input("Capital ($)", value=10000, min_value=100, step=1000)
    strategy_name = st.selectbox("Strategy", list(STRATEGY_REGISTRY.keys()))

    # Strategy params
    st.markdown("### PARAMETERS")
    strategy_info = STRATEGY_REGISTRY[strategy_name]
    user_params = {}

    if strategy_name == "SMA Crossover":
        user_params["short"] = st.slider("Short SMA", 5, 50, 20)
        user_params["long"]  = st.slider("Long SMA", 20, 200, 50)
    elif strategy_name == "EMA Crossover":
        user_params["short"] = st.slider("Short EMA", 5, 50, 12)
        user_params["long"]  = st.slider("Long EMA", 20, 200, 26)
    elif strategy_name == "RSI":
        user_params["window"]     = st.slider("Period", 5, 30, 14)
        user_params["oversold"]   = st.slider("Oversold", 10, 45, 30)
        user_params["overbought"] = st.slider("Overbought", 55, 90, 70)
    elif strategy_name == "MACD":
        user_params["fast"]   = st.slider("Fast", 5, 30, 12)
        user_params["slow"]   = st.slider("Slow", 15, 60, 26)
        user_params["signal"] = st.slider("Signal", 3, 20, 9)
    elif strategy_name == "Bollinger Bands":
        user_params["window"]   = st.slider("Period", 5, 50, 20)
        user_params["num_std"]  = st.slider("Std Dev", 1.0, 4.0, 2.0, step=0.1)
    elif strategy_name == "SuperTrend":
        user_params["window"]     = st.slider("ATR Period", 5, 30, 10)
        user_params["multiplier"] = st.slider("Multiplier", 1.0, 6.0, 3.0, step=0.5)
    elif strategy_name == "RSI + Bollinger Bands":
        user_params["rsi_window"] = st.slider("RSI Period", 5, 30, 14)
        user_params["bb_window"]  = st.slider("BB Period", 10, 50, 20)
        user_params["oversold"]   = st.slider("RSI Oversold", 20, 45, 35)
        user_params["overbought"] = st.slider("RSI Overbought", 55, 85, 65)
    elif strategy_name == "EMA + RSI Filter":
        user_params["ema_fast"]   = st.slider("Fast EMA", 3, 30, 9)
        user_params["ema_slow"]   = st.slider("Slow EMA", 10, 60, 21)
        user_params["rsi_window"] = st.slider("RSI Period", 5, 30, 14)
    elif strategy_name == "MACD + SuperTrend":
        user_params["fast"]      = st.slider("MACD Fast", 5, 20, 12)
        user_params["slow"]      = st.slider("MACD Slow", 15, 50, 26)
        user_params["st_window"] = st.slider("ST ATR Period", 5, 20, 10)

    run_btn = st.button("▶  RUN BACKTEST", use_container_width=True)

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
    <h1>BACKTEST</h1>
    <p>Test pre-built strategies against historical price data.</p>
</div>
""", unsafe_allow_html=True)

# ── Run ───────────────────────────────────────────────────────────────────────
if run_btn:
    with st.spinner(f"Loading {ticker}..."):
        df = get_stock_data(ticker, str(start_date), str(end_date))
    if df.empty:
        st.stop()

    info = get_ticker_info(ticker)
    st.markdown(f"""
    <div style="font-family:'IBM Plex Mono',monospace; font-size:0.78rem; color:#4a5568; margin-bottom:1.5rem;">
        {info.get('name', ticker)} &nbsp;·&nbsp; {info.get('sector','N/A')} &nbsp;·&nbsp;
        {len(df)} trading days &nbsp;·&nbsp; {str(start_date)} → {str(end_date)}
    </div>
    """, unsafe_allow_html=True)

    with st.spinner("Running backtest..."):
        try:
            fn = strategy_info["fn"]
            signals = fn(df, **user_params)
            result = run_backtest(df, signals, float(capital))
        except Exception as e:
            st.error(f"Error: {e}")
            st.stop()

    m = result["metrics"]
    port = result["portfolio"]
    trades = result["trades"]

    # ── Metrics ───────────────────────────────────────────────────────────────
    st.markdown("### PERFORMANCE")
    cols = st.columns(8)
    def mcard(col, val, lbl, fmt="pct"):
        if fmt == "pct":
            cls = "pos" if val >= 0 else "neg"
            display = f"{val:+.2f}%"
        elif fmt == "usd":
            cls = "neu"
            display = f"${val:,.0f}"
        elif fmt == "raw":
            cls = "neu"
            display = str(val)
        else:
            cls = "neu"
            display = val
        col.markdown(f'<div class="metric-card"><div class="metric-val {cls}">{display}</div><div class="metric-lbl">{lbl}</div></div>', unsafe_allow_html=True)

    mcard(cols[0], m["total_return"],  "Strategy Return")
    mcard(cols[1], m["bh_return"],     "Buy & Hold")
    mcard(cols[2], m["max_drawdown"],  "Max Drawdown")
    mcard(cols[3], m["final_value"],   "Final Value", fmt="usd")
    mcard(cols[4], m["win_rate"],      "Win Rate")
    mcard(cols[5], m["sharpe"],        "Sharpe Ratio", fmt="pct")
    cols[6].markdown(f'<div class="metric-card"><div class="metric-val neu">{m["num_trades"]}</div><div class="metric-lbl">Trades</div></div>', unsafe_allow_html=True)
    alpha = m["total_return"] - m["bh_return"]
    cols[7].markdown(f'<div class="metric-card"><div class="metric-val {"pos" if alpha>=0 else "neg"}">{alpha:+.2f}%</div><div class="metric-lbl">Alpha</div></div>', unsafe_allow_html=True)

    # ── Charts ────────────────────────────────────────────────────────────────
    st.markdown("### CHART")

    # Build overlays for price chart
    overlays = {}
    if strategy_name in ["SMA Crossover"]:
        from utils.indicators import sma
        overlays[f"SMA {user_params['short']}"] = sma(df["Close"], user_params["short"])
        overlays[f"SMA {user_params['long']}"]  = sma(df["Close"], user_params["long"])
    elif strategy_name in ["EMA Crossover", "EMA + RSI Filter"]:
        from utils.indicators import ema
        overlays[f"EMA {user_params['ema_fast' if 'ema_fast' in user_params else 'short']}"] = \
            ema(df["Close"], user_params.get("ema_fast", user_params.get("short")))
        overlays[f"EMA {user_params['ema_slow' if 'ema_slow' in user_params else 'long']}"] = \
            ema(df["Close"], user_params.get("ema_slow", user_params.get("long")))

    if strategy_name == "Bollinger Bands":
        st.plotly_chart(chart_bollinger(df, bollinger_bands(df["Close"], user_params["window"], user_params["num_std"])), use_container_width=True)
    elif strategy_name == "SuperTrend":
        st.plotly_chart(chart_supertrend(df, supertrend(df, user_params["window"], user_params["multiplier"])), use_container_width=True)
    elif strategy_name == "Ichimoku":
        st.plotly_chart(chart_ichimoku(df, ichimoku(df)), use_container_width=True)
    else:
        st.plotly_chart(chart_candles(df, trades, overlays=overlays, title=f"{ticker} — {strategy_name}"), use_container_width=True)

    # Sub-indicator charts
    if strategy_name in ["RSI", "RSI + Bollinger Bands", "EMA + RSI Filter"]:
        rsi_data = rsi(df["Close"], user_params.get("rsi_window", user_params.get("window", 14)))
        st.plotly_chart(chart_rsi(rsi_data, user_params.get("oversold", 30), user_params.get("overbought", 70)), use_container_width=True)
    if strategy_name in ["MACD", "MACD + SuperTrend"]:
        macd_data = macd(df["Close"], user_params.get("fast", 12), user_params.get("slow", 26))
        st.plotly_chart(chart_macd(macd_data["macd"], macd_data["signal"], macd_data["histogram"]), use_container_width=True)

    st.plotly_chart(chart_portfolio(port, df, float(capital)), use_container_width=True)

    # ── Trade log ─────────────────────────────────────────────────────────────
    if not trades.empty:
        with st.expander("📋 TRADE LOG"):
            st.dataframe(trades.set_index("date").style.applymap(
                lambda v: "color:#00d68f" if v == "BUY" else ("color:#ff4757" if "SELL" in str(v) else ""),
                subset=["action"]
            ), use_container_width=True)

    # Save for assistant context
    st.session_state["last_backtest"] = {
        "ticker": ticker, "strategy": strategy_name,
        "params": user_params, "metrics": m,
    }
    st.success("✅ Done! Visit the **AI Assistant** page to get these results explained.")

else:
    st.markdown("""
    <div class="info-box">
        ← Configure your strategy in the sidebar and hit RUN BACKTEST to get started.
    </div>
    """, unsafe_allow_html=True)
