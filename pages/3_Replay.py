import streamlit as st
import pandas as pd
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from datetime import date, timedelta

from utils.styles import SHARED_CSS
from utils.nav import navbar
from utils.data import get_stock_data
from utils.charts import chart_replay
from utils.indicators import sma, ema, bollinger_bands, supertrend

st.set_page_config(page_title="Replay | 11%", layout="wide", initial_sidebar_state="collapsed")
st.markdown(SHARED_CSS, unsafe_allow_html=True)
navbar()

for k, v in [
    ("replay_idx", 50), ("replay_trades", []), ("replay_cash", 10000.0),
    ("replay_shares", 0.0), ("replay_df", None), ("replay_ticker", "AAPL"),
    ("replay_capital", 10000.0),
]:
    if k not in st.session_state: st.session_state[k] = v

st.markdown("""
<div class="page-header">
    <div class="page-header-eyebrow">Day Trading Practice</div>
    <h1>Chart Replay</h1>
    <p>Step through real historical bars one at a time. You can't see the future — make buy and sell decisions as if it's live.</p>
</div>
""", unsafe_allow_html=True)

s1, s2, s3, s4, s5 = st.columns([1.2, 1, 1, 1, 1])
with s1: ticker     = st.text_input("Ticker", value=st.session_state.replay_ticker).upper().strip()
with s2: start_date = st.date_input("From", value=date.today()-timedelta(days=365*2), key="rp_start")
with s3: end_date   = st.date_input("To",   value=date.today(), key="rp_end")
with s4: capital    = st.number_input("Capital ($)", value=10000, min_value=100, step=1000, key="rp_cap")
with s5:
    st.markdown("<div style='height:1.75rem'></div>", unsafe_allow_html=True)
    load_btn = st.button("Load / Reset", type="primary", use_container_width=True)

o1, o2, o3, o4, o5, o6 = st.columns(6)
with o1: show_sma   = st.checkbox("SMA",             value=True,  key="rp_sma")
with o2: sma_window = st.slider("SMA Period", 5, 200, 20, key="rp_smap") if show_sma else 20
with o3: show_ema   = st.checkbox("EMA",             value=False, key="rp_ema")
with o4: ema_window = st.slider("EMA Period", 5, 200, 20, key="rp_emap") if show_ema else 20
with o5: show_bb    = st.checkbox("Bollinger Bands", value=False, key="rp_bb")
with o6: show_st    = st.checkbox("SuperTrend",      value=False, key="rp_st")

step_size = st.slider("Bars per step", 1, 10, 1, key="rp_step")

if load_btn:
    with st.spinner(f"Loading {ticker}..."):
        df_full = get_stock_data(ticker, str(start_date), str(end_date))
    if df_full.empty:
        st.error("No data. Check ticker."); st.stop()
    st.session_state.replay_df      = df_full
    st.session_state.replay_ticker  = ticker
    st.session_state.replay_idx     = min(50, len(df_full) - 1)
    st.session_state.replay_trades  = []
    st.session_state.replay_cash    = float(capital)
    st.session_state.replay_capital = float(capital)
    st.session_state.replay_shares  = 0.0
    st.rerun()

df_full = st.session_state.replay_df
if df_full is None or df_full.empty:
    st.markdown('<div class="info-box" style="margin-top:1rem;">Load a ticker above to begin.</div>', unsafe_allow_html=True)
    st.stop()

idx           = st.session_state.replay_idx
max_idx       = len(df_full) - 1
df_vis        = df_full.iloc[:idx + 1]
current_price = float(df_vis["Close"].iloc[-1])
current_date  = df_vis.index[-1]
start_capital = st.session_state.replay_capital
cash          = st.session_state.replay_cash
shares        = st.session_state.replay_shares
port_value    = cash + shares * current_price
pnl           = port_value - start_capital
pnl_pct       = pnl / start_capital * 100

mc = st.columns(6)
for col, (val, lbl, cls) in zip(mc, [
    (f"${current_price:,.2f}", "Price",     "neu"),
    (f"${port_value:,.2f}",    "Portfolio", "neu"),
    (f"${pnl:+,.2f}",          "P&L",       "pos" if pnl>=0 else "neg"),
    (f"{pnl_pct:+.2f}%",      "Return",    "pos" if pnl_pct>=0 else "neg"),
    (f"${cash:,.2f}",          "Cash",      "neu"),
    (f"{shares:.2f} sh",       "Position",  "neu"),
]):
    col.markdown(f'<div class="metric-card"><div class="metric-val {cls}">{val}</div><div class="metric-lbl">{lbl}</div></div>', unsafe_allow_html=True)

overlays = {}
if show_sma: overlays[f"SMA {sma_window}"] = sma(df_vis["Close"], sma_window)
if show_ema: overlays[f"EMA {ema_window}"] = ema(df_vis["Close"], ema_window)
if show_bb:
    bb = bollinger_bands(df_vis["Close"])
    overlays["BB Upper"]=bb["upper"]; overlays["BB Middle"]=bb["middle"]; overlays["BB Lower"]=bb["lower"]
if show_st:
    st_data = supertrend(df_vis)
    overlays["ST Bull"]=st_data["supertrend"].where(st_data["direction"]==1)
    overlays["ST Bear"]=st_data["supertrend"].where(st_data["direction"]==-1)

fig = chart_replay(df_vis, st.session_state.replay_trades, overlays=overlays or None,
                   title=f"{ticker} — Bar {idx}/{max_idx}")
st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

st.markdown('<div class="section-hdr"><div class="section-hdr-label">Playback</div></div>', unsafe_allow_html=True)
ctrl1, ctrl2, ctrl3, ctrl4, ctrl5 = st.columns(5)
with ctrl1:
    if st.button("⏮  Start", use_container_width=True):
        st.session_state.replay_idx = 50; st.rerun()
with ctrl2:
    if st.button(f"◀  −{step_size}", use_container_width=True):
        st.session_state.replay_idx = max(50, idx-step_size); st.rerun()
with ctrl3:
    st.markdown(f"""
    <div style="text-align:center;font-family:'IBM Plex Mono',monospace;padding:0.4rem 0;">
        <div style="color:#00e676;font-size:0.82rem;">{current_date.strftime('%Y-%m-%d')}</div>
        <div style="color:#3a4558;font-size:0.62rem;margin-top:2px;">Bar {idx} of {max_idx}</div>
    </div>""", unsafe_allow_html=True)
with ctrl4:
    if st.button(f"+{step_size}  ▶", use_container_width=True):
        st.session_state.replay_idx = min(max_idx, idx+step_size); st.rerun()
with ctrl5:
    if st.button("⏭  End", use_container_width=True):
        st.session_state.replay_idx = max_idx; st.rerun()

new_idx = st.slider("Scrub to bar", 50, max_idx, idx, key="rp_scrub")
if new_idx != idx:
    st.session_state.replay_idx = new_idx; st.rerun()

st.markdown('<div class="section-hdr"><div class="section-hdr-label">Practice Trading</div></div>', unsafe_allow_html=True)
t1, t2, t3 = st.columns(3)

with t1:
    buy_qty = st.number_input("Shares to buy", min_value=0.0, value=1.0, step=1.0, key="rp_buyq")
    max_can = int(cash / current_price) if current_price > 0 else 0
    st.markdown(f'<div style="font-family:IBM Plex Mono,monospace;font-size:0.62rem;color:#3a4558;margin-bottom:0.4rem;">Max: {max_can} sh · Cost: ${buy_qty*current_price:,.2f}</div>', unsafe_allow_html=True)
    if st.button("▲  BUY", use_container_width=True, type="primary"):
        cost = buy_qty * current_price
        if cost <= cash and buy_qty > 0:
            st.session_state.replay_cash   -= cost
            st.session_state.replay_shares += buy_qty
            st.session_state.replay_trades.append({"date":current_date,"action":"BUY","price":current_price,"shares":buy_qty})
            st.rerun()
        else:
            st.error(f"Need ${cost:,.2f}, have ${cash:,.2f}")

with t2:
    sell_qty = st.number_input("Shares to sell", min_value=0.0,
                               max_value=float(shares) if shares>0 else 0.0,
                               value=min(1.0, float(shares)), step=1.0, key="rp_sellq")
    st.markdown(f'<div style="font-family:IBM Plex Mono,monospace;font-size:0.62rem;color:#3a4558;margin-bottom:0.4rem;">Holding: {shares:.2f} sh · Value: ${shares*current_price:,.2f}</div>', unsafe_allow_html=True)
    if st.button("▼  SELL", use_container_width=True):
        if sell_qty <= shares and sell_qty > 0:
            st.session_state.replay_cash   += sell_qty * current_price
            st.session_state.replay_shares -= sell_qty
            st.session_state.replay_trades.append({"date":current_date,"action":"SELL","price":current_price,"shares":sell_qty})
            st.rerun()
        else:
            st.error("Not enough shares.")

with t3:
    st.markdown(f"""
    <div style="background:#0c1018;border:1px solid #1a2235;border-radius:10px;padding:1rem;text-align:center;">
        <div style="font-family:'IBM Plex Mono',monospace;font-size:0.56rem;color:#3a4558;text-transform:uppercase;letter-spacing:0.15em;margin-bottom:0.5rem;">Current Position</div>
        <div style="font-family:'IBM Plex Mono',monospace;font-size:1.4rem;color:{'#00e676' if shares>0 else '#3a4558'};">{shares:.2f} shares</div>
        <div style="font-family:'IBM Plex Mono',monospace;font-size:0.72rem;color:#8896ab;margin-top:2px;">${shares*current_price:,.2f}</div>
    </div>""", unsafe_allow_html=True)
    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    if st.button("Reset Trades", use_container_width=True):
        st.session_state.replay_trades = []
        st.session_state.replay_cash   = start_capital
        st.session_state.replay_shares = 0.0
        st.rerun()

if st.session_state.replay_trades:
    with st.expander(f"Trade log ({len(st.session_state.replay_trades)} trades)"):
        st.dataframe(pd.DataFrame(st.session_state.replay_trades), use_container_width=True)
