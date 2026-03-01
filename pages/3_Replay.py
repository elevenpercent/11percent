import streamlit as st
import pandas as pd
import sys, os
from datetime import date, timedelta
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.data import get_stock_data
from utils.charts import chart_candles, chart_portfolio, chart_rsi, chart_macd, chart_bollinger, chart_supertrend
from utils.indicators import sma, ema, bollinger_bands, supertrend, rsi, macd
from utils.styles import SHARED_CSS

st.set_page_config(page_title="Replay | 11%", layout="wide", initial_sidebar_state="collapsed")
st.markdown(SHARED_CSS, unsafe_allow_html=True)
st.markdown('<div class="nb"><div class="nb-brand"><span class="g">11</span><span class="r">%</span></div><div class="nb-links">', unsafe_allow_html=True)
_nav = st.columns([1,1,1,1,1,1])
with _nav[0]: st.page_link("app.py",                    label="Home")
with _nav[1]: st.page_link("pages/1_Backtest.py",       label="Backtest")
with _nav[2]: st.page_link("pages/2_Indicator_Test.py", label="Indicators")
with _nav[3]: st.page_link("pages/3_Replay.py",         label="Replay")
with _nav[4]: st.page_link("pages/4_Analysis.py",       label="Analysis")
with _nav[5]: st.page_link("pages/5_Assistant.py",      label="Assistant")
st.markdown('</div><div class="nb-tag">FREE · OPEN SOURCE</div></div>', unsafe_allow_html=True)

for k, v in [("replay_idx", 50), ("replay_trades", []), ("replay_cash", 10000.0), ("replay_shares", 0.0), ("replay_df", None), ("replay_ticker", "")]:
    if k not in st.session_state: st.session_state[k] = v

st.markdown('''<div class="page-header"><h1>Chart Replay</h1><p>Scroll through historical price action bar by bar. Practice reading charts, test your timing, and track a simulated portfolio as you go.</p></div>''', unsafe_allow_html=True)

# ── What is chart replay ──────────────────────────────────────────────────────
with st.expander("What is Chart Replay and how do I use it?"):
    e1, e2, e3 = st.columns(3)
    with e1:
        st.markdown("""**What it does**

Chart Replay hides future price data and reveals it one bar at a time — just like watching the market live, but in the past.

This is how professional traders develop pattern recognition: by replaying historical charts and forcing themselves to make decisions without knowing what comes next.""")
    with e2:
        st.markdown("""**How to use it**

1. Enter a ticker and date range, click Load
2. Use **+1 Bar** to advance one day at a time
3. Use **+5 Bars** to step a week at a time
4. Buy/sell using the trading panel below
5. Watch your portfolio value update in real time

Try to identify setups before they play out.""")
    with e3:
        st.markdown("""**What to practise**

- Can you spot a trend before it's obvious?
- Do you buy breakouts or wait for pullbacks?
- Where would you put your stop loss?
- How do indicators behave near reversals?

The goal isn't profit — it's developing intuition that takes years to build in real trading.""")

# ── Setup ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="price-divider">SETUP</div>', unsafe_allow_html=True)
st.markdown('<div class="config-panel">', unsafe_allow_html=True)
rc1, rc2, rc3, rc4 = st.columns([2, 1.5, 1.5, 1.5])
with rc1: ticker     = st.text_input("Ticker", value="AAPL").upper().strip()
with rc2: start_date = st.date_input("Start",  value=date.today()-timedelta(days=365*2))
with rc3: end_date   = st.date_input("End",    value=date.today()-timedelta(days=30))
with rc4: capital    = st.number_input("Starting Capital ($)", value=10000, min_value=100, step=1000)

st.markdown('<div style="margin-top:0.6rem;margin-bottom:0.2rem;font-family:IBM Plex Mono,monospace;font-size:0.62rem;color:#3a4558;text-transform:uppercase;letter-spacing:0.12em;">Overlays</div>', unsafe_allow_html=True)
ov1,ov2,ov3,ov4,ov5,ov6,ov7,ov8 = st.columns(8)
with ov1: show_sma  = st.checkbox("SMA")
with ov2: sma_w     = st.slider("SMA", 5, 200, 20, key="sma_win", label_visibility="collapsed") if show_sma else 20
with ov3: show_ema  = st.checkbox("EMA")
with ov4: ema_w     = st.slider("EMA", 5, 200, 50, key="ema_win", label_visibility="collapsed") if show_ema else 50
with ov5: show_bb   = st.checkbox("Bollinger")
with ov6: show_st   = st.checkbox("SuperTrend")
with ov7: show_rsi  = st.checkbox("RSI")
with ov8: show_macd = st.checkbox("MACD")

load_btn = st.button("Load Chart", use_container_width=False)
st.markdown('</div>', unsafe_allow_html=True)

if load_btn:
    with st.spinner(f"Loading {ticker}..."):
        df_full = get_stock_data(ticker, str(start_date), str(end_date))
    if df_full.empty: st.error("No data found."); st.stop()
    st.session_state.replay_df      = df_full
    st.session_state.replay_ticker  = ticker
    st.session_state.replay_idx     = min(50, len(df_full)-1)
    st.session_state.replay_trades  = []
    st.session_state.replay_cash    = float(capital)
    st.session_state.replay_shares  = 0.0
    st.rerun()

df_full = st.session_state.replay_df
if df_full is None or df_full.empty:
    st.markdown('<div class="info-box">Enter a ticker above and click Load Chart to begin.</div>', unsafe_allow_html=True)
    st.stop()

idx      = st.session_state.replay_idx
max_idx  = len(df_full) - 1
df_vis   = df_full.iloc[:idx+1]
cp       = float(df_vis["Close"].iloc[-1])
cd       = df_vis.index[-1]
cash     = st.session_state.replay_cash
shares   = st.session_state.replay_shares
pv       = cash + shares * cp
pnl      = pv - float(capital)
pnl_pct  = pnl / float(capital) * 100

# Build overlays
overlays = {}
if show_sma:
    s = sma(df_vis["Close"], sma_w)
    overlays[f"SMA {sma_w}"] = s
if show_ema:
    e = ema(df_vis["Close"], ema_w)
    overlays[f"EMA {ema_w}"] = e
if show_bb:
    bb = bollinger_bands(df_vis["Close"])
    overlays["BB Upper"] = bb["upper"]; overlays["BB Mid"] = bb["middle"]; overlays["BB Lower"] = bb["lower"]
if show_st:
    std = supertrend(df_vis)
    overlays["ST Bull"] = std["supertrend"].where(std["direction"]==1)
    overlays["ST Bear"] = std["supertrend"].where(std["direction"]==-1)

trades_df = pd.DataFrame(st.session_state.replay_trades) if st.session_state.replay_trades else pd.DataFrame()

# ── Portfolio strip ───────────────────────────────────────────────────────────
st.markdown('<div class="price-divider">PORTFOLIO</div>', unsafe_allow_html=True)
m1,m2,m3,m4,m5,m6,m7 = st.columns(7)
m1.markdown(f'<div class="metric-card"><div class="metric-val neu">{st.session_state.replay_ticker}</div><div class="metric-lbl">Ticker</div></div>', unsafe_allow_html=True)
m2.markdown(f'<div class="metric-card"><div class="metric-val neu">${cp:,.2f}</div><div class="metric-lbl">Current Price</div></div>', unsafe_allow_html=True)
m3.markdown(f'<div class="metric-card"><div class="metric-val neu">${pv:,.2f}</div><div class="metric-lbl">Portfolio Value</div></div>', unsafe_allow_html=True)
m4.markdown(f'<div class="metric-card"><div class="metric-val {"pos" if pnl>=0 else "neg"}">${pnl:+,.2f}</div><div class="metric-lbl">P&L ($)</div></div>', unsafe_allow_html=True)
m5.markdown(f'<div class="metric-card"><div class="metric-val {"pos" if pnl_pct>=0 else "neg"}">{pnl_pct:+.2f}%</div><div class="metric-lbl">P&L (%)</div></div>', unsafe_allow_html=True)
m6.markdown(f'<div class="metric-card"><div class="metric-val neu">${cash:,.2f}</div><div class="metric-lbl">Cash</div></div>', unsafe_allow_html=True)
m7.markdown(f'<div class="metric-card"><div class="metric-val neu">{shares:.2f} sh</div><div class="metric-lbl">Shares Held</div></div>', unsafe_allow_html=True)

# ── Chart ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="price-divider">CHART</div>', unsafe_allow_html=True)
st.plotly_chart(
    chart_candles(df_vis, trades_df if not trades_df.empty else None, overlays=overlays or None, title=f"{st.session_state.replay_ticker} · {cd.strftime('%Y-%m-%d')} · Bar {idx+1}/{max_idx+1}"),
    use_container_width=True
)

# Sub-indicator charts
if show_rsi:
    st.plotly_chart(chart_rsi(rsi(df_vis["Close"]), 30, 70), use_container_width=True)
if show_macd:
    md = macd(df_vis["Close"])
    st.plotly_chart(chart_macd(md["macd"], md["signal"], md["histogram"]), use_container_width=True)

# ── Playback controls ─────────────────────────────────────────────────────────
st.markdown('<div class="price-divider">PLAYBACK</div>', unsafe_allow_html=True)
step = st.select_slider("Step size", options=[1, 2, 5, 10, 20], value=1, label_visibility="collapsed")
pc1,pc2,pc3,pc4,pc5,pc6 = st.columns(6)
with pc1:
    if st.button("⏮ Start", use_container_width=True):
        st.session_state.replay_idx = 50; st.rerun()
with pc2:
    if st.button(f"◀  -{step}", use_container_width=True):
        st.session_state.replay_idx = max(0, idx-step); st.rerun()
with pc3:
    st.markdown(f'<div style="text-align:center;font-family:IBM Plex Mono,monospace;font-size:0.82rem;color:#00d68f;padding:0.4rem 0;">{cd.strftime("%b %d, %Y")}</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="text-align:center;font-family:IBM Plex Mono,monospace;font-size:0.62rem;color:#3a4558;">Bar {idx+1} of {max_idx+1}</div>', unsafe_allow_html=True)
with pc4:
    if st.button(f"+{step}  ▶", use_container_width=True):
        st.session_state.replay_idx = min(max_idx, idx+step); st.rerun()
with pc5:
    if st.button("End ⏭", use_container_width=True):
        st.session_state.replay_idx = max_idx; st.rerun()
with pc6:
    jump = st.number_input("Jump to bar", min_value=0, max_value=max_idx, value=idx, step=1, label_visibility="collapsed")
    if jump != idx: st.session_state.replay_idx = jump; st.rerun()

# ── Trading ───────────────────────────────────────────────────────────────────
st.markdown('<div class="price-divider">PRACTICE TRADING</div>', unsafe_allow_html=True)
t1, t2, t3 = st.columns(3)
with t1:
    st.markdown('<div class="config-panel">', unsafe_allow_html=True)
    st.markdown('<div style="font-family:IBM Plex Mono,monospace;font-size:0.62rem;color:#00d68f;text-transform:uppercase;letter-spacing:0.12em;margin-bottom:0.7rem;">Buy Order</div>', unsafe_allow_html=True)
    bq = st.number_input("Shares to buy", min_value=0.0, value=1.0, step=1.0, key="bq")
    st.markdown(f'<div style="font-size:0.72rem;color:#3a4558;margin-bottom:0.5rem;">Cost estimate: ${bq*cp:,.2f}</div>', unsafe_allow_html=True)
    if st.button("Buy at Market", use_container_width=True, key="buy_btn"):
        cost = bq * cp
        if cost <= cash:
            st.session_state.replay_cash -= cost
            st.session_state.replay_shares += bq
            st.session_state.replay_trades.append({"date": cd, "action": "BUY", "price": cp, "shares": bq})
            st.success(f"Bought {bq:.0f} shares @ ${cp:.2f}"); st.rerun()
        else: st.error(f"Not enough cash. Need ${cost:,.2f}")
    st.markdown('</div>', unsafe_allow_html=True)
with t2:
    st.markdown('<div class="config-panel">', unsafe_allow_html=True)
    st.markdown('<div style="font-family:IBM Plex Mono,monospace;font-size:0.62rem;color:#ff4757;text-transform:uppercase;letter-spacing:0.12em;margin-bottom:0.7rem;">Sell Order</div>', unsafe_allow_html=True)
    sq = st.number_input("Shares to sell", min_value=0.0, max_value=float(shares) if shares > 0 else 0.0, value=min(1.0, float(shares)), step=1.0, key="sq")
    st.markdown(f'<div style="font-size:0.72rem;color:#3a4558;margin-bottom:0.5rem;">Proceeds estimate: ${sq*cp:,.2f}</div>', unsafe_allow_html=True)
    if st.button("Sell at Market", use_container_width=True, key="sell_btn"):
        if sq <= shares and sq > 0:
            st.session_state.replay_cash += sq * cp
            st.session_state.replay_shares -= sq
            st.session_state.replay_trades.append({"date": cd, "action": "SELL", "price": cp, "shares": sq})
            st.success(f"Sold {sq:.0f} shares @ ${cp:.2f}"); st.rerun()
        else: st.error("Not enough shares.")
    st.markdown('</div>', unsafe_allow_html=True)
with t3:
    entry_trades = [t for t in st.session_state.replay_trades if t["action"]=="BUY"]
    last_entry = entry_trades[-1]["price"] if entry_trades else None
    unrealised = (cp - last_entry) * shares if last_entry and shares > 0 else 0.0
    st.markdown(f'''<div class="config-panel">
        <div style="font-family:IBM Plex Mono,monospace;font-size:0.62rem;color:#3a4558;text-transform:uppercase;letter-spacing:0.12em;margin-bottom:0.7rem;">Open Position</div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-bottom:0.8rem;">
          <div class="metric-card"><div class="metric-val neu">{shares:.2f}</div><div class="metric-lbl">Shares</div></div>
          <div class="metric-card"><div class="metric-val neu">${last_entry:.2f}</div><div class="metric-lbl">Avg Entry</div></div>
          <div class="metric-card"><div class="metric-val {'pos' if unrealised>=0 else 'neg'}">${unrealised:+.2f}</div><div class="metric-lbl">Unrealised P&L</div></div>
          <div class="metric-card"><div class="metric-val neu">{len(st.session_state.replay_trades)}</div><div class="metric-lbl">Trades Made</div></div>
        </div>
    </div>''' if last_entry else f'''<div class="config-panel">
        <div style="font-family:IBM Plex Mono,monospace;font-size:0.62rem;color:#3a4558;text-transform:uppercase;letter-spacing:0.12em;margin-bottom:0.7rem;">Open Position</div>
        <div style="font-size:0.8rem;color:#3a4558;">No open position.</div>
    </div>''', unsafe_allow_html=True)
    if st.button("Reset All Trades", use_container_width=True):
        st.session_state.replay_trades  = []
        st.session_state.replay_cash    = float(capital)
        st.session_state.replay_shares  = 0.0
        st.rerun()

# ── Trade log ─────────────────────────────────────────────────────────────────
if st.session_state.replay_trades:
    st.markdown('<div class="price-divider">TRADE LOG</div>', unsafe_allow_html=True)
    log_df = pd.DataFrame(st.session_state.replay_trades)
    log_df["value"] = (log_df["price"] * log_df["shares"]).apply(lambda x: f"${x:,.2f}")
    log_df["price"] = log_df["price"].apply(lambda x: f"${x:,.2f}")
    with st.expander(f"{len(log_df)} trades recorded"):
        st.dataframe(log_df, use_container_width=True)

    # Mini portfolio chart
    st.markdown('<div class="price-divider">PORTFOLIO HISTORY</div>', unsafe_allow_html=True)
    st.plotly_chart(chart_portfolio(
        pd.DataFrame([{"date": df_full.index[i], "value": st.session_state.replay_cash + st.session_state.replay_shares * float(df_full["Close"].iloc[i])} for i in range(idx+1)]),
        df_full.iloc[:idx+1], float(capital)
    ), use_container_width=True)
