import streamlit as st
import sys, os
from datetime import date, timedelta
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.data import get_stock_data, get_ticker_info
from utils.strategies import STRATEGY_REGISTRY, run_backtest
from utils.charts import chart_candles, chart_portfolio, chart_rsi, chart_macd, chart_bollinger, chart_supertrend, chart_ichimoku
from utils.indicators import rsi, macd, bollinger_bands, supertrend, ichimoku

st.set_page_config(page_title="Backtest | 11%", page_icon="🔬", layout="wide")
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=IBM+Plex+Mono:wght@300;400;600;700&family=IBM+Plex+Sans:wght@300;400;600&display=swap');
    :root {
        --bg:#07090d; --surface:#0d1117; --border:#1c2333; --border2:#263045;
        --green:#00d68f; --red:#ff4757; --text:#cdd5e0; --muted:#3a4558;
        --grid:rgba(255,255,255,0.03);
    }
    html,body,[data-testid="stAppViewContainer"],[data-testid="stMain"],.main {
        background-color:var(--bg)!important; color:var(--text)!important;
        font-family:'IBM Plex Sans',sans-serif!important;
    }
    [data-testid="stMain"] {
        background-image:linear-gradient(var(--grid) 1px,transparent 1px),linear-gradient(90deg,var(--grid) 1px,transparent 1px)!important;
        background-size:48px 48px!important;
    }
    [data-testid="stSidebar"] { background-color:var(--surface)!important; border-right:1px solid var(--border)!important; }
    [data-testid="stSidebarNav"] { display:none!important; }
    h1 { font-family:'Bebas Neue',sans-serif!important; letter-spacing:0.06em; color:var(--text)!important; }
    h2 { font-family:'Bebas Neue',sans-serif!important; letter-spacing:0.05em; color:var(--text)!important; }
    h3 { font-family:'IBM Plex Mono',monospace!important; font-size:0.75rem!important; color:var(--green)!important; text-transform:uppercase; letter-spacing:0.15em; }
    .ticker-wrap { width:100%; overflow:hidden; background:var(--surface); border-top:1px solid var(--border); border-bottom:1px solid var(--border); padding:0.45rem 0; margin-bottom:2rem; }
    .ticker-tape { display:inline-flex; animation:ticker 30s linear infinite; white-space:nowrap; }
    .ticker-item { font-family:'IBM Plex Mono',monospace; font-size:0.72rem; padding:0 2rem; letter-spacing:0.06em; }
    .ticker-up { color:var(--green); }
    .ticker-down { color:var(--red); }
    .ticker-sym { color:var(--text); margin-right:0.4rem; }
    @keyframes ticker { 0%{transform:translateX(0)} 100%{transform:translateX(-50%)} }
    .hero { padding:2.5rem 0 2rem 0; }
    .hero-eyebrow { font-family:'IBM Plex Mono',monospace; font-size:0.7rem; color:var(--green); text-transform:uppercase; letter-spacing:0.25em; margin-bottom:0.8rem; }
    .hero-title { font-family:'Bebas Neue',sans-serif; font-size:5.5rem; line-height:0.92; letter-spacing:0.04em; margin:0; }
    .hero-title .green { color:var(--green); }
    .hero-title .red   { color:var(--red); }
    .hero-subtitle { font-size:0.9rem; color:var(--muted); margin-top:1.2rem; max-width:480px; line-height:1.7; }
    .chart-deco { display:flex; align-items:flex-end; gap:4px; height:80px; margin:1.5rem 0; }
    .candle-body { width:14px; border-radius:2px; position:relative; flex-shrink:0; }
    .candle-wick { width:2px; background:inherit; position:absolute; left:50%; transform:translateX(-50%); border-radius:1px; opacity:0.6; }
    .candle-wick-top { bottom:100%; }
    .candle-wick-bottom { top:100%; }
    .ohlc-row { display:flex; gap:1px; margin:0.8rem 0; background:var(--border); border-radius:6px; overflow:hidden; }
    .ohlc-box { flex:1; background:var(--surface); padding:0.8rem; text-align:center; }
    .ohlc-label { font-family:'IBM Plex Mono',monospace; font-size:0.6rem; text-transform:uppercase; letter-spacing:0.15em; color:var(--muted); margin-bottom:0.3rem; }
    .ohlc-value { font-family:'IBM Plex Mono',monospace; font-size:1rem; font-weight:600; }
    .price-divider { display:flex; align-items:center; gap:1rem; margin:1.5rem 0; font-family:'IBM Plex Mono',monospace; font-size:0.65rem; color:var(--muted); }
    .price-divider::before,.price-divider::after { content:''; flex:1; height:1px; background:var(--border); }
    ::-webkit-scrollbar { width:4px; }
    ::-webkit-scrollbar-track { background:var(--bg); }
    ::-webkit-scrollbar-thumb { background:var(--border2); border-radius:2px; }
    .stButton>button { background:transparent!important; color:var(--green)!important; border:1px solid var(--green)!important; border-radius:3px!important; font-family:'IBM Plex Mono',monospace!important; font-weight:600!important; font-size:0.78rem!important; letter-spacing:0.1em!important; padding:0.45rem 1.4rem!important; transition:all 0.15s!important; text-transform:uppercase!important; }
    .stButton>button:hover { background:var(--green)!important; color:#000!important; }
    hr { border-color:var(--border)!important; }
    [data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"] { font-family:'IBM Plex Mono',monospace!important; font-size:0.72rem!important; text-transform:uppercase!important; letter-spacing:0.1em!important; color:#3a4558!important; padding:0.45rem 0.3rem!important; border-bottom:1px solid #1c2333!important; border-radius:0!important; display:block!important; }
    [data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"]:hover { color:#00d68f!important; background:transparent!important; }
    [data-testid="stSidebar"] a[aria-current="page"] { color:#00d68f!important; background:transparent!important; }

    .metric-card { background:#0d1117; border:1px solid #1c2333; padding:1rem; border-radius:4px; text-align:center; }
    .metric-val { font-family:'IBM Plex Mono',monospace; font-size:1.1rem; font-weight:700; }
    .metric-lbl { font-family:'IBM Plex Mono',monospace; font-size:0.55rem; color:#3a4558; text-transform:uppercase; margin-top:0.3rem; }
    .pos { color:#00d68f; } .neg { color:#ff4757; } .neu { color:#cdd5e0; }
    .page-header { border-left:3px solid #00d68f; padding-left:1rem; margin-bottom:1.5rem; }
    .page-header p { color:#3a4558; font-size:0.88rem; margin-top:0.2rem; }
    .info-box { background:#071a0f; border:1px solid #0d3320; border-radius:6px; padding:0.8rem 1rem; font-size:0.82rem; color:#00d68f; font-family:'IBM Plex Mono',monospace; }
    .warn-box { background:#1a0a08; border:1px solid #3a1008; border-radius:6px; padding:0.8rem 1rem; font-size:0.82rem; color:#ff4757; font-family:'IBM Plex Mono',monospace; }
    .chat-user { background:#0d1117; border:1px solid #1c2333; border-radius:10px 10px 3px 10px; padding:1rem 1.2rem; margin:0.6rem 0; }
    .chat-ai { background:#071a0f; border:1px solid #0d3320; border-radius:10px 10px 10px 3px; padding:1rem 1.2rem; margin:0.6rem 0; }
    .chat-lbl { font-family:'IBM Plex Mono',monospace; font-size:0.65rem; text-transform:uppercase; letter-spacing:0.12em; color:#3a4558; margin-bottom:0.4rem; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("assets/logo.png", width=120)
    st.markdown('<div style="padding-top:1rem;padding-bottom:0.5rem;border-top:1px solid #1c2333;"><div style="font-family:IBM Plex Mono,monospace;font-size:0.6rem;color:#3a4558;text-transform:uppercase;letter-spacing:0.18em;margin-bottom:0.5rem;">Navigation</div></div>', unsafe_allow_html=True)
    st.page_link("app.py",                       label="🏠  Home")
    st.page_link("pages/1_Backtest.py",          label="🔬  Backtest")
    st.page_link("pages/2_Indicator_Test.py",    label="📊  Indicator Test")
    st.page_link("pages/3_Replay.py",            label="▶   Replay")
    st.page_link("pages/4_Analysis.py",          label="🧠  Analysis")
    st.page_link("pages/5_Assistant.py",         label="💬  Assistant")
    st.markdown('<div style="position:absolute;bottom:1.5rem;left:1rem;right:1rem;text-align:center;font-family:IBM Plex Mono,monospace;font-size:0.6rem;color:#3a4558;text-transform:uppercase;letter-spacing:0.1em;">Free · Open Source</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown('<div style="font-family:IBM Plex Mono,monospace;font-size:0.6rem;color:#3a4558;text-transform:uppercase;letter-spacing:0.18em;margin-bottom:0.5rem;">Strategy Config</div>', unsafe_allow_html=True)
    ticker = st.text_input("Ticker Symbol", value="AAPL").upper().strip()
    col1, col2 = st.columns(2)
    with col1: start_date = st.date_input("Start", value=date.today() - __import__('datetime').timedelta(days=365*3))
    with col2: end_date = st.date_input("End", value=date.today())
    capital = st.number_input("Capital ($)", value=10000, min_value=100, step=1000)
    strategy_name = st.selectbox("Strategy", list(STRATEGY_REGISTRY.keys()))
    st.markdown('<div style="font-family:IBM Plex Mono,monospace;font-size:0.6rem;color:#3a4558;text-transform:uppercase;letter-spacing:0.18em;margin:1rem 0 0.5rem 0;">Parameters</div>', unsafe_allow_html=True)
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
        user_params["window"]  = st.slider("Period", 5, 50, 20)
        user_params["num_std"] = st.slider("Std Dev", 1.0, 4.0, 2.0, step=0.1)
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
st.markdown('''<div class="page-header"><h1>BACKTEST LAB</h1><p>Test pre-built strategies against historical price data.</p></div>''', unsafe_allow_html=True)

if run_btn:
    with st.spinner(f"Fetching {ticker}..."):
        df = get_stock_data(ticker, str(start_date), str(end_date))
    if df.empty:
        st.stop()
    info = get_ticker_info(ticker)
    st.markdown(f'<div style="font-family:IBM Plex Mono,monospace;font-size:0.72rem;color:#3a4558;margin-bottom:1.5rem;text-transform:uppercase;letter-spacing:0.05em;">{info.get("name",ticker)} &nbsp;·&nbsp; {info.get("sector","N/A")} &nbsp;·&nbsp; {len(df)} candles &nbsp;·&nbsp; {start_date} → {end_date}</div>', unsafe_allow_html=True)
    try:
        signals = strategy_info["fn"](df, **user_params)
        result  = run_backtest(df, signals, float(capital))
    except Exception as e:
        st.error(f"Error: {e}"); st.stop()
    m = result["metrics"]; port = result["portfolio"]; trades = result["trades"]

    st.markdown('<div class="price-divider">PERFORMANCE</div>', unsafe_allow_html=True)
    cols = st.columns(8)
    def mcard(col, val, lbl, fmt="pct"):
        if fmt=="pct": cls="pos" if val>=0 else "neg"; disp=f"{val:+.2f}%"
        elif fmt=="usd": cls="neu"; disp=f"${val:,.0f}"
        else: cls="neu"; disp=str(val)
        col.markdown(f'<div class="metric-card"><div class="metric-val {cls}">{disp}</div><div class="metric-lbl">{lbl}</div></div>', unsafe_allow_html=True)
    mcard(cols[0], m["total_return"], "Strategy")
    mcard(cols[1], m["bh_return"],    "Buy & Hold")
    mcard(cols[2], m["max_drawdown"], "Drawdown")
    mcard(cols[3], m["final_value"],  "Final Value", fmt="usd")
    mcard(cols[4], m["win_rate"],     "Win Rate")
    mcard(cols[5], m["sharpe"],       "Sharpe", fmt="raw")
    cols[6].markdown(f'<div class="metric-card"><div class="metric-val neu">{m["num_trades"]}</div><div class="metric-lbl">Trades</div></div>', unsafe_allow_html=True)
    alpha = m["total_return"] - m["bh_return"]
    cols[7].markdown(f'<div class="metric-card"><div class="metric-val {"pos" if alpha>=0 else "neg"}">{alpha:+.2f}%</div><div class="metric-lbl">Alpha</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="price-divider">CHART</div>', unsafe_allow_html=True)
    overlays = {}
    if strategy_name == "SMA Crossover":
        from utils.indicators import sma
        overlays[f"SMA {user_params['short']}"] = sma(df["Close"], user_params["short"])
        overlays[f"SMA {user_params['long']}"]  = sma(df["Close"], user_params["long"])
    elif strategy_name in ["EMA Crossover", "EMA + RSI Filter"]:
        from utils.indicators import ema
        overlays["Fast EMA"] = ema(df["Close"], user_params.get("ema_fast", user_params.get("short")))
        overlays["Slow EMA"] = ema(df["Close"], user_params.get("ema_slow", user_params.get("long")))
    if strategy_name == "Bollinger Bands":
        st.plotly_chart(chart_bollinger(df, bollinger_bands(df["Close"], user_params["window"], user_params["num_std"])), use_container_width=True)
    elif strategy_name == "SuperTrend":
        st.plotly_chart(chart_supertrend(df, supertrend(df, user_params["window"], user_params["multiplier"])), use_container_width=True)
    else:
        st.plotly_chart(chart_candles(df, trades, overlays=overlays if overlays else None, title=f"{ticker} — {strategy_name}"), use_container_width=True)
    if strategy_name in ["RSI", "RSI + Bollinger Bands", "EMA + RSI Filter"]:
        st.plotly_chart(chart_rsi(rsi(df["Close"], user_params.get("rsi_window", user_params.get("window",14))), user_params.get("oversold",30), user_params.get("overbought",70)), use_container_width=True)
    if strategy_name in ["MACD", "MACD + SuperTrend"]:
        md = macd(df["Close"], user_params.get("fast",12), user_params.get("slow",26))
        st.plotly_chart(chart_macd(md["macd"], md["signal"], md["histogram"]), use_container_width=True)
    st.plotly_chart(chart_portfolio(port, df, float(capital)), use_container_width=True)
    if not trades.empty:
        with st.expander("📋 TRADE LOG"):
            st.dataframe(trades.set_index("date"), use_container_width=True)
    st.session_state["last_backtest"] = {"ticker": ticker, "strategy": strategy_name, "params": user_params, "metrics": m}
    st.markdown('<div class="info-box">✅ Done! Visit the AI Assistant page to get these results explained.</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="info-box">← Configure your strategy in the sidebar and hit RUN BACKTEST.</div>', unsafe_allow_html=True)
