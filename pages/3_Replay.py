import streamlit as st
import pandas as pd
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from datetime import date, timedelta
from utils.data import get_stock_data
from utils.charts import chart_replay
from utils.indicators import sma, ema, bollinger_bands, supertrend

st.set_page_config(page_title="Replay | 11%", page_icon="▶", layout="wide")
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

if "replay_idx"     not in st.session_state: st.session_state.replay_idx = 50
if "replay_trades"  not in st.session_state: st.session_state.replay_trades = []
if "replay_cash"    not in st.session_state: st.session_state.replay_cash = 10000.0
if "replay_shares"  not in st.session_state: st.session_state.replay_shares = 0.0
if "replay_df"      not in st.session_state: st.session_state.replay_df = None

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
    st.markdown('<div style="font-family:IBM Plex Mono,monospace;font-size:0.6rem;color:#3a4558;text-transform:uppercase;letter-spacing:0.18em;margin-bottom:0.5rem;">Replay Setup</div>', unsafe_allow_html=True)
    ticker = st.text_input("Ticker", value="AAPL").upper().strip()
    col1, col2 = st.columns(2)
    with col1: start_date = st.date_input("Start", value=date.today() - timedelta(days=365*2))
    with col2: end_date   = st.date_input("End",   value=date.today())
    capital   = st.number_input("Starting Capital ($)", value=10000, min_value=100, step=1000)
    st.markdown('<div style="font-family:IBM Plex Mono,monospace;font-size:0.6rem;color:#3a4558;text-transform:uppercase;letter-spacing:0.18em;margin:1rem 0 0.5rem 0;">Overlays</div>', unsafe_allow_html=True)
    show_sma  = st.checkbox("SMA", value=True)
    sma_win   = st.slider("SMA Period", 5, 200, 20) if show_sma else 20
    show_ema  = st.checkbox("EMA", value=False)
    ema_win   = st.slider("EMA Period", 5, 200, 20) if show_ema else 20
    show_bb   = st.checkbox("Bollinger Bands", value=False)
    show_st   = st.checkbox("SuperTrend", value=False)
    step_size = st.slider("Bars per step", 1, 10, 1)
    load_btn  = st.button("⏮  LOAD / RESET", use_container_width=True)

st.markdown('''<div class="page-header"><h1>CHART REPLAY</h1><p>Step through candles, mark your trades, and track P&L in practice mode.</p></div>''', unsafe_allow_html=True)

if load_btn or st.session_state.replay_df is None:
    with st.spinner(f"Loading {ticker}..."):
        df_full = get_stock_data(ticker, str(start_date), str(end_date))
    if df_full.empty: st.stop()
    st.session_state.replay_df     = df_full
    st.session_state.replay_idx    = min(50, len(df_full)-1)
    st.session_state.replay_trades = []
    st.session_state.replay_cash   = float(capital)
    st.session_state.replay_shares = 0.0
    st.rerun()

df_full = st.session_state.replay_df
if df_full is None or df_full.empty: st.info("← Load a ticker to begin."); st.stop()

idx           = st.session_state.replay_idx
max_idx       = len(df_full) - 1
df_vis        = df_full.iloc[:idx+1]
current_price = float(df_vis["Close"].iloc[-1])
current_date  = df_vis.index[-1]
cash          = st.session_state.replay_cash
shares        = st.session_state.replay_shares
port_value    = cash + shares * current_price
pnl           = port_value - float(capital)
pnl_pct       = pnl / float(capital) * 100

overlays = {}
if show_sma: overlays[f"SMA {sma_win}"] = sma(df_vis["Close"], sma_win)
if show_ema: overlays[f"EMA {ema_win}"] = ema(df_vis["Close"], ema_win)
if show_bb:
    bb = bollinger_bands(df_vis["Close"])
    overlays["BB Upper"]=bb["upper"]; overlays["BB Middle"]=bb["middle"]; overlays["BB Lower"]=bb["lower"]
if show_st:
    st_data = supertrend(df_vis)
    overlays["ST Bull"]=st_data["supertrend"].where(st_data["direction"]==1)
    overlays["ST Bear"]=st_data["supertrend"].where(st_data["direction"]==-1)

st.markdown('<div class="price-divider">PORTFOLIO</div>', unsafe_allow_html=True)
m1,m2,m3,m4,m5,m6 = st.columns(6)
m1.markdown(f'<div class="metric-card"><div class="metric-val neu">${current_price:,.2f}</div><div class="metric-lbl">Price</div></div>', unsafe_allow_html=True)
m2.markdown(f'<div class="metric-card"><div class="metric-val neu">${port_value:,.2f}</div><div class="metric-lbl">Portfolio</div></div>', unsafe_allow_html=True)
m3.markdown(f'<div class="metric-card"><div class="metric-val {"pos" if pnl>=0 else "neg"}">${pnl:+,.2f}</div><div class="metric-lbl">P&L</div></div>', unsafe_allow_html=True)
m4.markdown(f'<div class="metric-card"><div class="metric-val {"pos" if pnl_pct>=0 else "neg"}">{pnl_pct:+.2f}%</div><div class="metric-lbl">Return</div></div>', unsafe_allow_html=True)
m5.markdown(f'<div class="metric-card"><div class="metric-val neu">${cash:,.2f}</div><div class="metric-lbl">Cash</div></div>', unsafe_allow_html=True)
m6.markdown(f'<div class="metric-card"><div class="metric-val neu">${shares*current_price:,.2f}</div><div class="metric-lbl">Position</div></div>', unsafe_allow_html=True)

fig = chart_replay(df_vis, st.session_state.replay_trades, overlays=overlays if overlays else None)
st.plotly_chart(fig, use_container_width=True)

st.markdown('<div class="price-divider">PLAYBACK</div>', unsafe_allow_html=True)
c1,c2,c3,c4,c5 = st.columns(5)
with c1:
    if st.button("⏮  Start"): st.session_state.replay_idx=50; st.rerun()
with c2:
    if st.button(f"◀  -{step_size}"): st.session_state.replay_idx=max(50,idx-step_size); st.rerun()
with c3:
    st.markdown(f'<div style="text-align:center;font-family:IBM Plex Mono,monospace;font-size:0.8rem;padding:0.5rem 0;color:#00d68f;">{current_date.strftime("%Y-%m-%d")}<br><span style="color:#3a4558;font-size:0.65rem;">Bar {idx}/{max_idx}</span></div>', unsafe_allow_html=True)
with c4:
    if st.button(f"+{step_size}  ▶"): st.session_state.replay_idx=min(max_idx,idx+step_size); st.rerun()
with c5:
    if st.button("⏭  End"): st.session_state.replay_idx=max_idx; st.rerun()

new_idx = st.slider("Jump to bar", 50, max_idx, idx, key="scrubber")
if new_idx != idx: st.session_state.replay_idx=new_idx; st.rerun()

st.markdown('<div class="price-divider">PRACTICE TRADING</div>', unsafe_allow_html=True)
t1,t2,t3 = st.columns(3)
with t1:
    buy_qty = st.number_input("Shares to Buy", min_value=0.0, value=1.0, step=1.0)
    if st.button("🟢  BUY", use_container_width=True):
        cost = buy_qty * current_price
        if cost <= cash:
            st.session_state.replay_cash   -= cost
            st.session_state.replay_shares += buy_qty
            st.session_state.replay_trades.append({"date":current_date,"action":"BUY","price":current_price,"shares":buy_qty})
            st.success(f"Bought {buy_qty} @ ${current_price:.2f}"); st.rerun()
        else: st.error(f"Not enough cash. Need ${cost:,.2f}, have ${cash:,.2f}")
with t2:
    sell_qty = st.number_input("Shares to Sell", min_value=0.0, max_value=float(shares) if shares>0 else 0.0, value=min(1.0,float(shares)), step=1.0)
    if st.button("🔴  SELL", use_container_width=True):
        if sell_qty<=shares and sell_qty>0:
            st.session_state.replay_cash   += sell_qty*current_price
            st.session_state.replay_shares -= sell_qty
            st.session_state.replay_trades.append({"date":current_date,"action":"SELL","price":current_price,"shares":sell_qty})
            st.success(f"Sold {sell_qty} @ ${current_price:.2f}"); st.rerun()
        else: st.error("Not enough shares.")
with t3:
    st.markdown(f'<div class="metric-card"><div class="metric-lbl">Position</div><div class="metric-val neu" style="margin-top:0.3rem;">{shares:.2f} shares</div><div style="font-family:IBM Plex Mono,monospace;font-size:0.72rem;color:#3a4558;">@ ${current_price:.2f} = ${shares*current_price:,.2f}</div></div>', unsafe_allow_html=True)
    if st.button("🔄  Reset Trades", use_container_width=True):
        st.session_state.replay_trades=[]; st.session_state.replay_cash=float(capital); st.session_state.replay_shares=0.0; st.rerun()

if st.session_state.replay_trades:
    with st.expander("📋 YOUR TRADE LOG"):
        st.dataframe(pd.DataFrame(st.session_state.replay_trades), use_container_width=True)
