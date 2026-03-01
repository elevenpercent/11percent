import streamlit as st
import pandas as pd
import sys, os
from datetime import date, timedelta
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.data import get_stock_data
from utils.charts import chart_candles, chart_portfolio, chart_rsi, chart_macd
from utils.indicators import sma, ema, bollinger_bands, supertrend, rsi, macd
from utils.styles import SHARED_CSS

st.set_page_config(page_title="Replay | 11%", layout="wide", initial_sidebar_state="collapsed")
st.markdown(SHARED_CSS, unsafe_allow_html=True)

def navbar():
    st.markdown('<div class="nb"><div class="nb-brand"><span class="g">11</span><span class="r">%</span></div><div class="nb-links">', unsafe_allow_html=True)
    c = st.columns([1,1,1,1,1,1])
    with c[0]: st.page_link("app.py",                    label="Home")
    with c[1]: st.page_link("pages/1_Backtest.py",       label="Backtest")
    with c[2]: st.page_link("pages/2_Indicator_Test.py", label="Indicators")
    with c[3]: st.page_link("pages/3_Replay.py",         label="Replay")
    with c[4]: st.page_link("pages/4_Analysis.py",       label="Analysis")
    with c[5]: st.page_link("pages/5_Assistant.py",      label="Coach")
    st.markdown('</div><div class="nb-tag">FREE · OPEN SOURCE</div></div>', unsafe_allow_html=True)
navbar()

for k, v in [("replay_idx",50),("replay_trades",[]),("replay_cash",10000.0),("replay_shares",0.0),("replay_df",None),("replay_ticker",""),("replay_capital",10000.0)]:
    if k not in st.session_state: st.session_state[k] = v

# ── Page header ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
    <h1>Chart Replay</h1>
    <p>Step through historical bars one at a time. Practice reading price action without knowing what comes next.</p>
</div>
""", unsafe_allow_html=True)

# ── Setup ──────────────────────────────────────────────────────────────────────
st.markdown('<div class="config-panel">', unsafe_allow_html=True)
r1,r2,r3,r4 = st.columns([2,1.5,1.5,1.5])
with r1: ticker     = st.text_input("Ticker", value="AAPL").upper().strip()
with r2: start_date = st.date_input("From",   value=date.today()-timedelta(days=365*2))
with r3: end_date   = st.date_input("To",     value=date.today()-timedelta(days=30))
with r4: capital    = st.number_input("Capital ($)", value=10000, min_value=100, step=1000)

ov1,ov2,ov3,ov4,ov5,ov6,ov7,ov8 = st.columns(8)
with ov1: show_sma  = st.checkbox("SMA")
with ov2: sma_w     = st.slider("SMA period",5,200,20,key="sw",label_visibility="collapsed") if show_sma else 20
with ov3: show_ema  = st.checkbox("EMA")
with ov4: ema_w     = st.slider("EMA period",5,200,50,key="ew",label_visibility="collapsed") if show_ema else 50
with ov5: show_bb   = st.checkbox("BB")
with ov6: show_st   = st.checkbox("SuperTrend")
with ov7: show_rsi  = st.checkbox("RSI")
with ov8: show_macd = st.checkbox("MACD")

if st.button("Load Chart", type="primary"):
    with st.spinner(f"Loading {ticker}…"):
        df_full = get_stock_data(ticker, str(start_date), str(end_date))
    if df_full.empty: st.error("No data found."); st.stop()
    st.session_state.replay_df      = df_full
    st.session_state.replay_ticker  = ticker
    st.session_state.replay_idx     = min(50, len(df_full)-1)
    st.session_state.replay_trades  = []
    st.session_state.replay_cash    = float(capital)
    st.session_state.replay_shares  = 0.0
    st.session_state.replay_capital = float(capital)
    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

df_full = st.session_state.replay_df
if df_full is None or df_full.empty:
    st.markdown("""
    <div style="background:#0d1117;border:1px solid #1a2235;border-radius:12px;padding:3rem;text-align:center;margin:2rem 0;">
        <div style="font-size:2rem;margin-bottom:1rem;">▶</div>
        <div style="font-family:'IBM Plex Mono',monospace;font-size:0.72rem;color:#3a4558;text-transform:uppercase;letter-spacing:0.15em;margin-bottom:0.8rem;">How it works</div>
        <div style="color:#8892a4;font-size:0.88rem;line-height:1.7;max-width:480px;margin:0 auto;">
            Enter a ticker, set your date range, and click Load Chart.<br>
            The chart reveals one bar at a time — step forward to see what happened next.
            Practice making buy/sell decisions without knowing the outcome.
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

idx     = st.session_state.replay_idx
max_idx = len(df_full) - 1
df_vis  = df_full.iloc[:idx+1]
cp      = float(df_vis["Close"].iloc[-1])
cd      = df_vis.index[-1]
cash    = st.session_state.replay_cash
shares  = st.session_state.replay_shares
stored_capital = st.session_state.replay_capital
pv      = cash + shares * cp
pnl     = pv - stored_capital
pnl_pct = pnl / stored_capital * 100

# Build overlays
overlays = {}
if show_sma: overlays[f"SMA {sma_w}"] = sma(df_vis["Close"], sma_w)
if show_ema: overlays[f"EMA {ema_w}"] = ema(df_vis["Close"], ema_w)
if show_bb:
    bb_ = bollinger_bands(df_vis["Close"])
    overlays["BB Upper"]=bb_["upper"]; overlays["BB Mid"]=bb_["middle"]; overlays["BB Lower"]=bb_["lower"]
if show_st:
    std_ = supertrend(df_vis)
    overlays["ST Bull"]=std_["supertrend"].where(std_["direction"]==1)
    overlays["ST Bear"]=std_["supertrend"].where(std_["direction"]==-1)

trades_df = pd.DataFrame(st.session_state.replay_trades) if st.session_state.replay_trades else pd.DataFrame()

# ── Portfolio strip ────────────────────────────────────────────────────────────
p_cols = st.columns(7)
for col, lbl, val, cls in [
    (p_cols[0], "Ticker",  st.session_state.replay_ticker, "neu"),
    (p_cols[1], "Price",   f"${cp:,.2f}", "neu"),
    (p_cols[2], "Value",   f"${pv:,.2f}", "neu"),
    (p_cols[3], "P&L $",   f"${pnl:+,.2f}", "pos" if pnl>=0 else "neg"),
    (p_cols[4], "P&L %",   f"{pnl_pct:+.2f}%", "pos" if pnl_pct>=0 else "neg"),
    (p_cols[5], "Cash",    f"${cash:,.2f}", "neu"),
    (p_cols[6], "Shares",  f"{shares:.2f}", "neu"),
]:
    col.markdown(f'<div class="metric-card" style="margin-bottom:1rem;"><div class="metric-val {cls}">{val}</div><div class="metric-lbl">{lbl}</div></div>', unsafe_allow_html=True)

# ── Chart ──────────────────────────────────────────────────────────────────────
st.plotly_chart(
    chart_candles(df_vis, trades_df if not trades_df.empty else None,
                  overlays=overlays or None,
                  title=f"{st.session_state.replay_ticker}  ·  {cd.strftime('%b %d, %Y')}  ·  Bar {idx+1} / {max_idx+1}"),
    use_container_width=True
)
if show_rsi:
    st.plotly_chart(chart_rsi(rsi(df_vis["Close"]), 30, 70), use_container_width=True)
if show_macd:
    md_ = macd(df_vis["Close"])
    st.plotly_chart(chart_macd(md_["macd"], md_["signal"], md_["histogram"]), use_container_width=True)

# ── Playback controls ──────────────────────────────────────────────────────────
st.markdown('<div style="height:0.5rem;"></div>', unsafe_allow_html=True)
step = st.select_slider("Step size", [1,2,5,10,20], value=1, label_visibility="collapsed")

ctrl = st.columns([1,1,2,1,1,1])
with ctrl[0]:
    if st.button("⏮ Start", use_container_width=True):
        st.session_state.replay_idx = min(50, max_idx); st.rerun()
with ctrl[1]:
    if st.button(f"◀ -{step}", use_container_width=True):
        st.session_state.replay_idx = max(0, idx-step); st.rerun()
with ctrl[2]:
    st.markdown(f'<div style="text-align:center;padding:0.5rem 0;"><div style="font-family:IBM Plex Mono,monospace;font-size:0.9rem;color:#e2e8f0;">{cd.strftime("%b %d, %Y")}</div><div style="font-family:IBM Plex Mono,monospace;font-size:0.62rem;color:#3a4558;">Bar {idx+1} of {max_idx+1} · {((idx+1)/(max_idx+1)*100):.0f}% through</div></div>', unsafe_allow_html=True)
with ctrl[3]:
    if st.button(f"+{step} ▶", use_container_width=True):
        st.session_state.replay_idx = min(max_idx, idx+step); st.rerun()
with ctrl[4]:
    if st.button("End ⏭", use_container_width=True):
        st.session_state.replay_idx = max_idx; st.rerun()
with ctrl[5]:
    jump = st.number_input("Bar", 0, max_idx, idx, label_visibility="collapsed")
    if jump != idx: st.session_state.replay_idx = jump; st.rerun()

# ── Trade panel ────────────────────────────────────────────────────────────────
st.markdown('<div class="divider">Trade</div>', unsafe_allow_html=True)
t1, t2, t3 = st.columns(3)

with t1:
    st.markdown('<div class="panel-sm">', unsafe_allow_html=True)
    st.markdown('<div style="font-family:IBM Plex Mono,monospace;font-size:0.6rem;color:#00d68f;text-transform:uppercase;letter-spacing:0.15em;margin-bottom:0.6rem;">Buy</div>', unsafe_allow_html=True)
    bq = st.number_input("Shares", min_value=0.0, value=1.0, step=1.0, key="bq")
    st.markdown(f'<div style="font-family:IBM Plex Mono,monospace;font-size:0.7rem;color:#3a4558;margin-bottom:0.5rem;">Cost: ${bq*cp:,.2f}</div>', unsafe_allow_html=True)
    if st.button("Buy at Market", use_container_width=True):
        cost = bq * cp
        if cost <= cash:
            st.session_state.replay_cash -= cost
            st.session_state.replay_shares += bq
            st.session_state.replay_trades.append({"date":cd,"action":"BUY","price":cp,"shares":bq})
            st.success(f"Bought {bq:.0f} @ ${cp:.2f}"); st.rerun()
        else: st.error("Not enough cash.")
    st.markdown('</div>', unsafe_allow_html=True)

with t2:
    st.markdown('<div class="panel-sm">', unsafe_allow_html=True)
    st.markdown('<div style="font-family:IBM Plex Mono,monospace;font-size:0.6rem;color:#ff4757;text-transform:uppercase;letter-spacing:0.15em;margin-bottom:0.6rem;">Sell</div>', unsafe_allow_html=True)
    sq = st.number_input("Shares", min_value=0.0, max_value=float(shares) if shares>0 else 0.0, value=min(1.0,float(shares)), step=1.0, key="sq")
    st.markdown(f'<div style="font-family:IBM Plex Mono,monospace;font-size:0.7rem;color:#3a4558;margin-bottom:0.5rem;">Proceeds: ${sq*cp:,.2f}</div>', unsafe_allow_html=True)
    if st.button("Sell at Market", use_container_width=True):
        if sq <= shares and sq > 0:
            st.session_state.replay_cash += sq * cp
            st.session_state.replay_shares -= sq
            st.session_state.replay_trades.append({"date":cd,"action":"SELL","price":cp,"shares":sq})
            st.success(f"Sold {sq:.0f} @ ${cp:.2f}"); st.rerun()
        else: st.error("Not enough shares.")
    st.markdown('</div>', unsafe_allow_html=True)

with t3:
    entry_list = [t for t in st.session_state.replay_trades if t["action"]=="BUY"]
    last_entry = entry_list[-1]["price"] if entry_list else None
    unrealised = (cp - last_entry) * shares if last_entry and shares > 0 else 0.0
    st.markdown(f"""
    <div class="panel-sm">
        <div style="font-family:IBM Plex Mono,monospace;font-size:0.6rem;color:#3a4558;text-transform:uppercase;letter-spacing:0.15em;margin-bottom:0.7rem;">Position</div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;">
            <div class="metric-card" style="padding:0.6rem;"><div class="metric-val neu" style="font-size:0.9rem;">{shares:.1f}</div><div class="metric-lbl">Shares</div></div>
            <div class="metric-card" style="padding:0.6rem;"><div class="metric-val neu" style="font-size:0.9rem;">${last_entry:.2f if last_entry else "—"}</div><div class="metric-lbl">Entry</div></div>
            <div class="metric-card" style="padding:0.6rem;"><div class="metric-val {'pos' if unrealised>=0 else 'neg'}" style="font-size:0.9rem;">${unrealised:+.2f}</div><div class="metric-lbl">Unrealised</div></div>
            <div class="metric-card" style="padding:0.6rem;"><div class="metric-val neu" style="font-size:0.9rem;">{len(st.session_state.replay_trades)}</div><div class="metric-lbl">Trades</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Reset", use_container_width=True):
        st.session_state.replay_trades=[]; st.session_state.replay_cash=stored_capital; st.session_state.replay_shares=0.0; st.rerun()

# ── Trade log ──────────────────────────────────────────────────────────────────
if st.session_state.replay_trades:
    st.markdown('<div class="divider">Trade Log</div>', unsafe_allow_html=True)
    log = pd.DataFrame(st.session_state.replay_trades)
    log["value"] = (log["price"]*log["shares"]).apply(lambda x: f"${x:,.2f}")
    log["price"] = log["price"].apply(lambda x: f"${x:,.2f}")
    with st.expander(f"{len(log)} trades"):
        st.dataframe(log, use_container_width=True)
