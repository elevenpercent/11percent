import streamlit as st
import pandas as pd
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from datetime import date, timedelta

from utils.styles import SHARED_CSS
from utils.nav import navbar
from utils.data import get_stock_data
from utils.charts import chart_replay
from utils.indicators import sma, ema, rsi, macd, bollinger_bands, supertrend

st.set_page_config(page_title="Replay | 11%", page_icon="▶", layout="wide")
st.markdown(SHARED_CSS, unsafe_allow_html=True)

# ── Session state init ────────────────────────────────────────────────────────
if "replay_idx"      not in st.session_state: st.session_state.replay_idx = 50
if "replay_trades"   not in st.session_state: st.session_state.replay_trades = []
if "replay_cash"     not in st.session_state: st.session_state.replay_cash = 10000.0
if "replay_shares"   not in st.session_state: st.session_state.replay_shares = 0.0
if "replay_df"       not in st.session_state: st.session_state.replay_df = None
if "replay_started"  not in st.session_state: st.session_state.replay_started = False

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div style="font-family:\'Bebas Neue\',sans-serif;font-size:1.8rem;color:#f0b429;letter-spacing:0.1em;">11%</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### REPLAY SETUP")

    ticker = st.text_input("Ticker", value="AAPL").upper().strip()
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start", value=date.today() - timedelta(days=365*2))
    with col2:
        end_date = st.date_input("End", value=date.today())

    capital = st.number_input("Starting Capital ($)", value=10000, min_value=100, step=1000)

    st.markdown("### OVERLAYS")
    show_sma   = st.checkbox("SMA", value=True)
    sma_window = st.slider("SMA Period", 5, 200, 20) if show_sma else 20
    show_ema   = st.checkbox("EMA", value=False)
    ema_window = st.slider("EMA Period", 5, 200, 20) if show_ema else 20
    show_bb    = st.checkbox("Bollinger Bands", value=False)
    show_st    = st.checkbox("SuperTrend", value=False)

    st.markdown("### SPEED")
    step_size = st.slider("Bars per step (auto-play)", 1, 10, 1)

    load_btn = st.button("⏮  LOAD / RESET", use_container_width=True)

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
    <h1>CHART REPLAY</h1>
    <p>Step through historical candles, mark your trades, and track your P&L in practice mode.</p>
</div>
""", unsafe_allow_html=True)

# ── Load data ─────────────────────────────────────────────────────────────────
if load_btn or st.session_state.replay_df is None:
    with st.spinner(f"Loading {ticker}..."):
        df_full = get_stock_data(ticker, str(start_date), str(end_date))
    if df_full.empty:
        st.stop()
    st.session_state.replay_df      = df_full
    st.session_state.replay_idx     = min(50, len(df_full) - 1)
    st.session_state.replay_trades  = []
    st.session_state.replay_cash    = float(capital)
    st.session_state.replay_shares  = 0.0
    st.session_state.replay_started = True
    st.rerun()

df_full = st.session_state.replay_df
if df_full is None or df_full.empty:
    st.info("← Load a ticker to begin.")
    st.stop()

idx     = st.session_state.replay_idx
max_idx = len(df_full) - 1
df_vis  = df_full.iloc[:idx + 1]
current_price = float(df_vis["Close"].iloc[-1])
current_date  = df_vis.index[-1]

# ── Compute overlays ──────────────────────────────────────────────────────────
overlays = {}
if show_sma:
    overlays[f"SMA {sma_window}"] = sma(df_vis["Close"], sma_window)
if show_ema:
    overlays[f"EMA {ema_window}"] = ema(df_vis["Close"], ema_window)
if show_bb:
    bb = bollinger_bands(df_vis["Close"])
    overlays["BB Upper"]  = bb["upper"]
    overlays["BB Middle"] = bb["middle"]
    overlays["BB Lower"]  = bb["lower"]
if show_st:
    st_data = supertrend(df_vis)
    overlays["ST Bull"] = st_data["supertrend"].where(st_data["direction"] == 1)
    overlays["ST Bear"] = st_data["supertrend"].where(st_data["direction"] == -1)

# ── Portfolio calculations ────────────────────────────────────────────────────
cash    = st.session_state.replay_cash
shares  = st.session_state.replay_shares
port_value = cash + shares * current_price
pnl        = port_value - float(capital)
pnl_pct    = pnl / float(capital) * 100

# ── Metrics row ───────────────────────────────────────────────────────────────
m1, m2, m3, m4, m5, m6 = st.columns(6)

m1.markdown(f'<div class="metric-card"><div class="metric-val neu">${current_price:,.2f}</div><div class="metric-lbl">Current Price</div></div>', unsafe_allow_html=True)
m2.markdown(f'<div class="metric-card"><div class="metric-val neu">${port_value:,.2f}</div><div class="metric-lbl">Portfolio Value</div></div>', unsafe_allow_html=True)
m3.markdown(f'<div class="metric-card"><div class="metric-val {"pos" if pnl >= 0 else "neg"}">${pnl:+,.2f}</div><div class="metric-lbl">P&L</div></div>', unsafe_allow_html=True)
m4.markdown(f'<div class="metric-card"><div class="metric-val {"pos" if pnl_pct >= 0 else "neg"}">{pnl_pct:+.2f}%</div><div class="metric-lbl">Return</div></div>', unsafe_allow_html=True)
m5.markdown(f'<div class="metric-card"><div class="metric-val neu">${cash:,.2f}</div><div class="metric-lbl">Cash</div></div>', unsafe_allow_html=True)
shares_val = shares * current_price if shares > 0 else 0
m6.markdown(f'<div class="metric-card"><div class="metric-val neu">${shares_val:,.2f}</div><div class="metric-lbl">Position Value</div></div>', unsafe_allow_html=True)

# ── Chart ─────────────────────────────────────────────────────────────────────
fig = chart_replay(df_vis, st.session_state.replay_trades, overlays=overlays if overlays else None)
st.plotly_chart(fig, use_container_width=True)

# ── Controls ──────────────────────────────────────────────────────────────────
st.markdown("""
<div style="font-family:'IBM Plex Mono',monospace; font-size:0.72rem; color:#4a5568; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:0.8rem;">
    PLAYBACK CONTROLS
</div>
""", unsafe_allow_html=True)

ctrl1, ctrl2, ctrl3, ctrl4, ctrl5 = st.columns(5)

with ctrl1:
    if st.button("⏮  Start"):
        st.session_state.replay_idx = 50
        st.rerun()

with ctrl2:
    if st.button(f"◀  -{step_size} Bar{'s' if step_size > 1 else ''}"):
        st.session_state.replay_idx = max(50, idx - step_size)
        st.rerun()

with ctrl3:
    st.markdown(f"""
    <div style="text-align:center; font-family:'IBM Plex Mono',monospace; font-size:0.8rem; padding:0.5rem 0;">
        <div style="color:#f0b429;">{current_date.strftime('%Y-%m-%d')}</div>
        <div style="color:#4a5568; font-size:0.65rem;">Bar {idx} / {max_idx}</div>
    </div>
    """, unsafe_allow_html=True)

with ctrl4:
    if st.button(f"+{step_size} Bar{'s' if step_size > 1 else ''}  ▶"):
        st.session_state.replay_idx = min(max_idx, idx + step_size)
        st.rerun()

with ctrl5:
    if st.button("⏭  End"):
        st.session_state.replay_idx = max_idx
        st.rerun()

# Scrubber
new_idx = st.slider("Jump to bar", 50, max_idx, idx, key="scrubber")
if new_idx != idx:
    st.session_state.replay_idx = new_idx
    st.rerun()

st.markdown("---")

# ── Trading controls ──────────────────────────────────────────────────────────
st.markdown("""
<div style="font-family:'IBM Plex Mono',monospace; font-size:0.72rem; color:#4a5568; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:0.8rem;">
    PRACTICE TRADING
</div>
""", unsafe_allow_html=True)

t1, t2, t3 = st.columns(3)

with t1:
    buy_qty = st.number_input("Shares to Buy", min_value=0.0, value=1.0, step=1.0)
    if st.button("🟢  BUY", use_container_width=True):
        cost = buy_qty * current_price
        if cost <= cash:
            st.session_state.replay_cash   -= cost
            st.session_state.replay_shares += buy_qty
            st.session_state.replay_trades.append({
                "date": current_date, "action": "BUY",
                "price": current_price, "shares": buy_qty,
            })
            st.success(f"Bought {buy_qty} shares @ ${current_price:.2f}")
            st.rerun()
        else:
            st.error(f"Not enough cash. Need ${cost:,.2f}, have ${cash:,.2f}")

with t2:
    sell_qty = st.number_input("Shares to Sell", min_value=0.0,
                                max_value=float(shares) if shares > 0 else 0.0,
                                value=min(1.0, float(shares)), step=1.0)
    if st.button("🔴  SELL", use_container_width=True):
        if sell_qty <= shares and sell_qty > 0:
            proceeds = sell_qty * current_price
            st.session_state.replay_cash   += proceeds
            st.session_state.replay_shares -= sell_qty
            st.session_state.replay_trades.append({
                "date": current_date, "action": "SELL",
                "price": current_price, "shares": sell_qty,
            })
            st.success(f"Sold {sell_qty} shares @ ${current_price:.2f}")
            st.rerun()
        else:
            st.error("You don't have enough shares to sell.")

with t3:
    st.markdown(f"""
    <div class="metric-card" style="margin-top:0.3rem;">
        <div style="font-family:'IBM Plex Mono',monospace; font-size:0.7rem; color:#4a5568; text-transform:uppercase; letter-spacing:0.1em;">Position</div>
        <div style="font-family:'IBM Plex Mono',monospace; font-size:1.3rem; color:#f0b429; margin-top:0.3rem;">
            {shares:.2f} shares
        </div>
        <div style="font-family:'IBM Plex Mono',monospace; font-size:0.78rem; color:#4a5568;">
            @ ${current_price:.2f} = ${shares * current_price:,.2f}
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🔄  Reset Trades", use_container_width=True):
        st.session_state.replay_trades  = []
        st.session_state.replay_cash    = float(capital)
        st.session_state.replay_shares  = 0.0
        st.rerun()

# ── Trade log ─────────────────────────────────────────────────────────────────
if st.session_state.replay_trades:
    st.markdown("---")
    with st.expander("📋 YOUR TRADE LOG"):
        trades_df = pd.DataFrame(st.session_state.replay_trades)
        st.dataframe(trades_df, use_container_width=True)
