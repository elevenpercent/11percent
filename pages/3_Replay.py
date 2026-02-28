import streamlit as st
import pandas as pd
import sys, os
from datetime import date, timedelta
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.data import get_stock_data
from utils.charts import chart_replay
from utils.indicators import sma, ema, bollinger_bands, supertrend

st.set_page_config(page_title="Replay | 11%", page_icon="▶", layout="wide", initial_sidebar_state="collapsed")
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
        background-size:48px 48px!important; padding-top:0!important;
    }
    .block-container { padding-top:0!important; padding-left:2rem!important; padding-right:2rem!important; max-width:100%!important; }
    [data-testid="stSidebar"],[data-testid="stSidebarNav"],[data-testid="collapsedControl"] { display:none!important; }
    /* Navbar */
    .navbar { background:#07090d; border-bottom:1px solid #1c2333; padding:0.7rem 2rem; display:flex; align-items:center; gap:2rem; margin-left:-2rem; margin-right:-2rem; margin-bottom:2rem; position:sticky; top:0; z-index:999; }
    .navbar-brand { font-family:'Bebas Neue',sans-serif; font-size:1.8rem; letter-spacing:0.1em; text-decoration:none; flex-shrink:0; }
    .navbar-brand .g { color:#00d68f; }
    .navbar-brand .r { color:#ff4757; }
    .nav-links { display:flex; gap:0.2rem; flex:1; }
    .nav-link { font-family:'IBM Plex Mono',monospace; font-size:0.68rem; text-transform:uppercase; letter-spacing:0.1em; color:#3a4558; text-decoration:none; padding:0.38rem 0.9rem; border-radius:3px; transition:all 0.15s; }
    .nav-link:hover { color:#00d68f; background:#0d1117; }
    .nav-link.active { color:#00d68f; background:#071a0f; border:1px solid #0d3320; }
    .nav-badge { font-family:'IBM Plex Mono',monospace; font-size:0.58rem; color:#3a4558; letter-spacing:0.12em; }
    /* Typography */
    h1 { font-family:'Bebas Neue',sans-serif!important; letter-spacing:0.06em; color:var(--text)!important; }
    h2 { font-family:'Bebas Neue',sans-serif!important; }
    h3 { font-family:'IBM Plex Mono',monospace!important; font-size:0.75rem!important; color:var(--green)!important; text-transform:uppercase; letter-spacing:0.15em; }
    /* Inputs */
    .stTextInput input, .stNumberInput input { background:#0d1117!important; border:1px solid #1c2333!important; color:#cdd5e0!important; font-family:'IBM Plex Mono',monospace!important; font-size:0.85rem!important; border-radius:3px!important; }
    .stTextInput input:focus, .stNumberInput input:focus { border-color:#00d68f!important; box-shadow:none!important; }
    div[data-baseweb="select"]>div { background:#0d1117!important; border:1px solid #1c2333!important; color:#cdd5e0!important; font-family:'IBM Plex Mono',monospace!important; border-radius:3px!important; }
    .stDateInput input { background:#0d1117!important; border:1px solid #1c2333!important; color:#cdd5e0!important; font-family:'IBM Plex Mono',monospace!important; border-radius:3px!important; }
    label { font-family:'IBM Plex Mono',monospace!important; font-size:0.68rem!important; color:#3a4558!important; text-transform:uppercase!important; letter-spacing:0.1em!important; }
    /* Buttons */
    .stButton>button { background:transparent!important; color:#00d68f!important; border:1px solid #00d68f!important; border-radius:3px!important; font-family:'IBM Plex Mono',monospace!important; font-weight:600!important; font-size:0.78rem!important; letter-spacing:0.1em!important; padding:0.45rem 1.4rem!important; transition:all 0.15s!important; text-transform:uppercase!important; }
    .stButton>button:hover { background:#00d68f!important; color:#000!important; }
    /* Metrics */
    .metric-card { background:#0d1117; border:1px solid #1c2333; padding:1rem; border-radius:4px; text-align:center; }
    .metric-val { font-family:'IBM Plex Mono',monospace; font-size:1.1rem; font-weight:700; }
    .metric-lbl { font-family:'IBM Plex Mono',monospace; font-size:0.55rem; color:#3a4558; text-transform:uppercase; margin-top:0.3rem; }
    .pos{color:#00d68f;} .neg{color:#ff4757;} .neu{color:#cdd5e0;}
    /* Config panel */
    .config-panel { background:#0d1117; border:1px solid #1c2333; border-radius:6px; padding:1.5rem 1.5rem 0.5rem 1.5rem; margin-bottom:1.5rem; }
    /* Dividers */
    .price-divider { display:flex; align-items:center; gap:1rem; margin:1.5rem 0; font-family:'IBM Plex Mono',monospace; font-size:0.65rem; color:#3a4558; }
    .price-divider::before,.price-divider::after { content:''; flex:1; height:1px; background:#1c2333; }
    /* Page header */
    .page-header { border-left:3px solid #00d68f; padding-left:1rem; margin-bottom:1.5rem; }
    .page-header p { color:#3a4558; font-size:0.88rem; margin-top:0.2rem; }
    /* Boxes */
    .info-box { background:#071a0f; border:1px solid #0d3320; border-radius:6px; padding:0.8rem 1rem; font-size:0.82rem; color:#00d68f; font-family:'IBM Plex Mono',monospace; }
    .warn-box { background:#1a0a08; border:1px solid #3a1008; border-radius:6px; padding:0.8rem 1rem; font-size:0.82rem; color:#ff4757; font-family:'IBM Plex Mono',monospace; }
    /* Chat */
    .chat-user { background:#0d1117; border:1px solid #1c2333; border-radius:10px 10px 3px 10px; padding:1rem 1.2rem; margin:0.6rem 0; }
    .chat-ai { background:#071a0f; border:1px solid #0d3320; border-radius:10px 10px 10px 3px; padding:1rem 1.2rem; margin:0.6rem 0; }
    .chat-lbl { font-family:'IBM Plex Mono',monospace; font-size:0.65rem; text-transform:uppercase; letter-spacing:0.12em; color:#3a4558; margin-bottom:0.4rem; }
    /* Ticker tape */
    .ticker-wrap { width:100%; overflow:hidden; background:#0d1117; border-bottom:1px solid #1c2333; padding:0.4rem 0; }
    .ticker-tape { display:inline-flex; animation:ticker 30s linear infinite; white-space:nowrap; }
    .ticker-item { font-family:'IBM Plex Mono',monospace; font-size:0.68rem; padding:0 1.5rem; letter-spacing:0.06em; }
    .ticker-up{color:#00d68f;} .ticker-down{color:#ff4757;}
    .ticker-sym { color:#cdd5e0; margin-right:0.4rem; }
    @keyframes ticker { 0%{transform:translateX(0)} 100%{transform:translateX(-50%)} }
    ::-webkit-scrollbar{width:4px;} ::-webkit-scrollbar-track{background:#07090d;} ::-webkit-scrollbar-thumb{background:#263045;border-radius:2px;}
    hr{border-color:#1c2333!important;}
    [data-testid="stExpander"]{background:#0d1117!important;border:1px solid #1c2333!important;border-radius:4px!important;}
</style>
""", unsafe_allow_html=True)
st.markdown('''<div class="navbar"><a class="navbar-brand" href="/app"><span class="g">11</span><span class="r">%</span></a><div class="nav-links"><a class="nav-link" href="/app">🏠 Home</a><a class="nav-link" href="/1_Backtest">🔬 Backtest</a><a class="nav-link" href="/2_Indicator_Test">📊 Indicators</a><a class="nav-link active" href="/3_Replay">▶ Replay</a><a class="nav-link" href="/4_Analysis">🧠 Analysis</a><a class="nav-link" href="/5_Assistant">💬 Assistant</a></div><span class="nav-badge">FREE · OPEN SOURCE</span></div>''', unsafe_allow_html=True)

for k,v in [("replay_idx",50),("replay_trades",[]),("replay_cash",10000.0),("replay_shares",0.0),("replay_df",None)]:
    if k not in st.session_state: st.session_state[k]=v

st.markdown('''<div class="page-header"><h1>CHART REPLAY</h1><p>Step through candles, mark your trades, and track P&L in practice mode.</p></div>''', unsafe_allow_html=True)

st.markdown('<div class="price-divider">SETUP</div>', unsafe_allow_html=True)
st.markdown('<div class="config-panel">', unsafe_allow_html=True)
rc1,rc2,rc3,rc4 = st.columns([2,1.5,1.5,2])
with rc1: ticker     = st.text_input("Ticker", value="AAPL").upper().strip()
with rc2: start_date = st.date_input("Start",  value=date.today()-timedelta(days=365*2))
with rc3: end_date   = st.date_input("End",    value=date.today())
with rc4: capital    = st.number_input("Starting Capital ($)", value=10000, min_value=100, step=1000)
oc1,oc2,oc3,oc4,oc5,oc6 = st.columns(6)
with oc1: show_sma = st.checkbox("SMA", value=True)
with oc2: sma_win  = st.slider("SMA Period", 5, 200, 20) if show_sma else 20
with oc3: show_ema = st.checkbox("EMA", value=False)
with oc4: ema_win  = st.slider("EMA Period", 5, 200, 20) if show_ema else 20
with oc5: show_bb  = st.checkbox("Bollinger Bands", value=False)
with oc6: show_st  = st.checkbox("SuperTrend", value=False)
step_size = st.slider("Bars per step", 1, 10, 1)
load_btn  = st.button("⏮  LOAD / RESET")
st.markdown('</div>', unsafe_allow_html=True)

if load_btn or st.session_state.replay_df is None:
    with st.spinner(f"Loading {ticker}..."):
        df_full=get_stock_data(ticker,str(start_date),str(end_date))
    if df_full.empty: st.stop()
    st.session_state.replay_df=df_full; st.session_state.replay_idx=min(50,len(df_full)-1)
    st.session_state.replay_trades=[]; st.session_state.replay_cash=float(capital); st.session_state.replay_shares=0.0
    st.rerun()

df_full=st.session_state.replay_df
if df_full is None or df_full.empty: st.markdown('<div class="info-box">↑ Enter a ticker and hit LOAD to begin.</div>', unsafe_allow_html=True); st.stop()

idx=st.session_state.replay_idx; max_idx=len(df_full)-1
df_vis=df_full.iloc[:idx+1]; current_price=float(df_vis["Close"].iloc[-1]); current_date=df_vis.index[-1]
cash=st.session_state.replay_cash; shares=st.session_state.replay_shares
port_value=cash+shares*current_price; pnl=port_value-float(capital); pnl_pct=pnl/float(capital)*100

overlays={}
if show_sma: overlays[f"SMA {sma_win}"]=sma(df_vis["Close"],sma_win)
if show_ema: overlays[f"EMA {ema_win}"]=ema(df_vis["Close"],ema_win)
if show_bb:
    bb=bollinger_bands(df_vis["Close"]); overlays["BB Upper"]=bb["upper"]; overlays["BB Middle"]=bb["middle"]; overlays["BB Lower"]=bb["lower"]
if show_st:
    st_d=supertrend(df_vis); overlays["ST Bull"]=st_d["supertrend"].where(st_d["direction"]==1); overlays["ST Bear"]=st_d["supertrend"].where(st_d["direction"]==-1)

st.markdown('<div class="price-divider">PORTFOLIO</div>', unsafe_allow_html=True)
m1,m2,m3,m4,m5,m6=st.columns(6)
m1.markdown(f'<div class="metric-card"><div class="metric-val neu">${current_price:,.2f}</div><div class="metric-lbl">Price</div></div>', unsafe_allow_html=True)
m2.markdown(f'<div class="metric-card"><div class="metric-val neu">${port_value:,.2f}</div><div class="metric-lbl">Portfolio</div></div>', unsafe_allow_html=True)
m3.markdown(f'<div class="metric-card"><div class="metric-val {"pos" if pnl>=0 else "neg"}">${pnl:+,.2f}</div><div class="metric-lbl">P&L</div></div>', unsafe_allow_html=True)
m4.markdown(f'<div class="metric-card"><div class="metric-val {"pos" if pnl_pct>=0 else "neg"}">{pnl_pct:+.2f}%</div><div class="metric-lbl">Return</div></div>', unsafe_allow_html=True)
m5.markdown(f'<div class="metric-card"><div class="metric-val neu">${cash:,.2f}</div><div class="metric-lbl">Cash</div></div>', unsafe_allow_html=True)
m6.markdown(f'<div class="metric-card"><div class="metric-val neu">${shares*current_price:,.2f}</div><div class="metric-lbl">Position</div></div>', unsafe_allow_html=True)

fig=chart_replay(df_vis,st.session_state.replay_trades,overlays=overlays if overlays else None)
st.plotly_chart(fig,use_container_width=True)

st.markdown('<div class="price-divider">PLAYBACK</div>', unsafe_allow_html=True)
c1,c2,c3,c4,c5=st.columns(5)
with c1:
    if st.button("⏮  Start"): st.session_state.replay_idx=50; st.rerun()
with c2:
    if st.button(f"◀  -{step_size}"): st.session_state.replay_idx=max(50,idx-step_size); st.rerun()
with c3:
    st.markdown(f'<div style="text-align:center;font-family:IBM Plex Mono,monospace;font-size:0.85rem;padding:0.4rem 0;color:#00d68f;">{current_date.strftime("%Y-%m-%d")}<br><span style="color:#3a4558;font-size:0.65rem;">Bar {idx}/{max_idx}</span></div>', unsafe_allow_html=True)
with c4:
    if st.button(f"+{step_size}  ▶"): st.session_state.replay_idx=min(max_idx,idx+step_size); st.rerun()
with c5:
    if st.button("End  ⏭"): st.session_state.replay_idx=max_idx; st.rerun()
new_idx=st.slider("Jump to bar",50,max_idx,idx,key="scrubber")
if new_idx!=idx: st.session_state.replay_idx=new_idx; st.rerun()

st.markdown('<div class="price-divider">PRACTICE TRADING</div>', unsafe_allow_html=True)
t1,t2,t3=st.columns(3)
with t1:
    buy_qty=st.number_input("Shares to Buy",min_value=0.0,value=1.0,step=1.0)
    if st.button("🟢  BUY",use_container_width=True):
        cost=buy_qty*current_price
        if cost<=cash:
            st.session_state.replay_cash-=cost; st.session_state.replay_shares+=buy_qty
            st.session_state.replay_trades.append({"date":current_date,"action":"BUY","price":current_price,"shares":buy_qty})
            st.success(f"Bought {buy_qty} @ ${current_price:.2f}"); st.rerun()
        else: st.error(f"Not enough cash. Need ${cost:,.2f}, have ${cash:,.2f}")
with t2:
    sell_qty=st.number_input("Shares to Sell",min_value=0.0,max_value=float(shares) if shares>0 else 0.0,value=min(1.0,float(shares)),step=1.0)
    if st.button("🔴  SELL",use_container_width=True):
        if sell_qty<=shares and sell_qty>0:
            st.session_state.replay_cash+=sell_qty*current_price; st.session_state.replay_shares-=sell_qty
            st.session_state.replay_trades.append({"date":current_date,"action":"SELL","price":current_price,"shares":sell_qty})
            st.success(f"Sold {sell_qty} @ ${current_price:.2f}"); st.rerun()
        else: st.error("Not enough shares.")
with t3:
    st.markdown(f'<div class="metric-card"><div class="metric-lbl">Position</div><div class="metric-val neu" style="margin-top:0.3rem;">{shares:.2f} shares</div><div style="font-family:IBM Plex Mono,monospace;font-size:0.72rem;color:#3a4558;">@ ${current_price:.2f} = ${shares*current_price:,.2f}</div></div>', unsafe_allow_html=True)
    if st.button("🔄  Reset Trades",use_container_width=True):
        st.session_state.replay_trades=[]; st.session_state.replay_cash=float(capital); st.session_state.replay_shares=0.0; st.rerun()

if st.session_state.replay_trades:
    with st.expander("📋 YOUR TRADE LOG"): st.dataframe(pd.DataFrame(st.session_state.replay_trades),use_container_width=True)
