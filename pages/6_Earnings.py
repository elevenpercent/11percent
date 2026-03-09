import streamlit as st
import sys, os
import pandas as pd
import numpy as np
from datetime import date, timedelta
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.styles import SHARED_CSS

st.set_page_config(page_title="Earnings | 11%", layout="wide", initial_sidebar_state="collapsed")
st.markdown(SHARED_CSS, unsafe_allow_html=True)

def navbar():
    st.markdown('<div class="nb"><div class="nb-brand"><span class="g">11</span><span class="r">%</span></div><div class="nb-links">', unsafe_allow_html=True)
    c = st.columns([1,1,1,1,1,1,1])
    with c[0]: st.page_link("app.py",                    label="Home")
    with c[1]: st.page_link("pages/1_Backtest.py",       label="Backtest")
    with c[2]: st.page_link("pages/2_Indicator_Test.py", label="Indicators")
    with c[3]: st.page_link("pages/3_Replay.py",         label="Replay")
    with c[4]: st.page_link("pages/4_Analysis.py",       label="Analysis")
    with c[5]: st.page_link("pages/6_Earnings.py",       label="Earnings")
    with c[6]: st.page_link("pages/5_Assistant.py",      label="Coach")
    st.markdown('</div><div class="nb-tag">FREE * OPEN SOURCE</div></div>', unsafe_allow_html=True)
navbar()

@st.cache_data(ttl=3600)
def load_earnings_data(ticker: str):
    import yfinance as yf
    t = yf.Ticker(ticker)
    cal = None
    hist_earnings = None
    price_hist = pd.DataFrame()
    info = {}

    # Load price history - try multiple approaches
    try:
        price_hist = t.history(period="5y", auto_adjust=True)
        if isinstance(price_hist.columns, pd.MultiIndex):
            price_hist.columns = price_hist.columns.get_level_values(0)
        price_hist = price_hist[["Open","High","Low","Close","Volume"]].dropna()
    except Exception:
        pass

    # Load info
    try:
        info = t.info or {}
    except Exception:
        info = {}

    # Load earnings history - try multiple yfinance API paths
    try:
        hist_earnings = t.earnings_history
    except Exception:
        hist_earnings = None

    try:
        cal = t.calendar
    except Exception:
        cal = None

    return cal, hist_earnings, price_hist, info

def compute_reaction(price_df: pd.DataFrame, earnings_dates: list, window: int = 5):
    """For each earnings date, compute price change in window before/after."""
    results = []
    if price_df.empty or not earnings_dates: return []
    price_df = price_df.copy()
    price_df.index = pd.to_datetime(price_df.index).tz_localize(None)

    for ed in earnings_dates:
        ed = pd.Timestamp(ed).tz_localize(None) if hasattr(pd.Timestamp(ed), 'tz') and pd.Timestamp(ed).tz else pd.Timestamp(ed)
        # Find nearest trading day at or after earnings
        idx_arr = price_df.index.searchsorted(ed)
        if idx_arr >= len(price_df) or idx_arr < window: continue

        day0_price = float(price_df["Close"].iloc[idx_arr])
        day_before = float(price_df["Close"].iloc[idx_arr - 1])

        # Day-of reaction
        day_of_chg = (day0_price - day_before) / day_before * 100

        # 5-day follow-through
        end_idx = min(idx_arr + window, len(price_df) - 1)
        day5_price = float(price_df["Close"].iloc[end_idx])
        followthrough = (day5_price - day0_price) / day0_price * 100

        # 5 days before
        pre_start = max(0, idx_arr - window - 1)
        pre_price = float(price_df["Close"].iloc[pre_start])
        pre_run = (day_before - pre_price) / pre_price * 100

        results.append({
            "date": ed.strftime("%b %d, %Y"),
            "day_of": day_of_chg,
            "5d_follow": followthrough,
            "5d_pre": pre_run,
            "price": day0_price,
        })
    return results

# -- Page header ----------------------------------------------------------------
st.markdown("""
<div class="page-header">
    <h1>Earnings Tracker</h1>
    <p>See how a stock historically reacted to each earnings announcement - before, on the day, and after.</p>
</div>
""", unsafe_allow_html=True)

# Setup
st.markdown('<div class="config-panel">', unsafe_allow_html=True)
e1, e2 = st.columns([1, 3])
with e1: ticker = st.text_input("Ticker", value="AAPL").upper().strip()
with e2:
    st.markdown('<div style="padding-top:1.8rem;font-size:0.82rem;color:#8892a4;line-height:1.6;">Pulls 5 years of earnings dates and measures the price reaction: how much the stock moved the day earnings dropped, the 5-day run up before, and the 5-day follow-through after.</div>', unsafe_allow_html=True)
run_btn = st.button("Load Earnings", type="primary")
st.markdown('</div>', unsafe_allow_html=True)

if not run_btn:
    st.markdown("""
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;margin-top:1rem;">
        <div class="panel-sm"><div style="font-family:'IBM Plex Mono',monospace;font-size:0.62rem;color:#00d68f;text-transform:uppercase;letter-spacing:0.12em;margin-bottom:0.5rem;">Why this matters</div><div style="font-size:0.82rem;color:#8892a4;line-height:1.65;">Earnings are the single biggest driver of short-term price moves. Knowing how a stock historically reacts tells you the risk going into the next report.</div></div>
        <div class="panel-sm"><div style="font-family:'IBM Plex Mono',monospace;font-size:0.62rem;color:#00d68f;text-transform:uppercase;letter-spacing:0.12em;margin-bottom:0.5rem;">What you'll see</div><div style="font-size:0.82rem;color:#8892a4;line-height:1.65;">Day-of move, 5-day pre-earnings run, 5-day post-earnings follow-through, average reactions, and whether the stock tends to gap up or down on earnings.</div></div>
        <div class="panel-sm"><div style="font-family:'IBM Plex Mono',monospace;font-size:0.62rem;color:#00d68f;text-transform:uppercase;letter-spacing:0.12em;margin-bottom:0.5rem;">The key insight</div><div style="font-size:0.82rem;color:#8892a4;line-height:1.65;">Markets price in expectations. A stock can beat earnings and still drop if expectations were too high. This tracker shows you the actual price history - not the headlines.</div></div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

with st.spinner(f"Loading earnings data for {ticker}?"):
    cal, hist_earnings, price_df, info = load_earnings_data(ticker)

if price_df.empty:
    st.error("Could not load data. Check the ticker.")
    st.stop()

# Extract earnings dates - try every yfinance API path
def _strip_tz(ts):
    t = pd.Timestamp(ts)
    return t.tz_localize(None) if t.tzinfo is not None else t

earnings_dates = []
import yfinance as yf
t2 = yf.Ticker(ticker)

# Method 1: earnings_history (older yfinance)
try:
    if hist_earnings is not None:
        df_eh = pd.DataFrame(hist_earnings) if not isinstance(hist_earnings, pd.DataFrame) else hist_earnings
        if not df_eh.empty:
            if "Earnings Date" in df_eh.columns:
                earnings_dates = [_strip_tz(d) for d in df_eh["Earnings Date"].dropna()]
            else:
                earnings_dates = [_strip_tz(d) for d in df_eh.index if pd.notna(d)]
except Exception:
    pass

# Method 2: earnings_dates property — filter to past dates only
if not earnings_dates:
    try:
        ed = t2.earnings_dates
        if ed is not None and not ed.empty:
            now = pd.Timestamp.now()
            earnings_dates = [
                _strip_tz(d) for d in ed.index
                if pd.notna(d) and _strip_tz(d) < now
            ][:20]
    except Exception:
        pass

# Method 3: get_earnings_dates(limit=40)
if not earnings_dates:
    try:
        ed = t2.get_earnings_dates(limit=40)
        if ed is not None and not ed.empty:
            now = pd.Timestamp.now()
            earnings_dates = [
                _strip_tz(d) for d in ed.index
                if pd.notna(d) and _strip_tz(d) < now
            ][:20]
    except Exception:
        pass

# Method 4: income_stmt quarterly index dates as last resort
if not earnings_dates:
    try:
        qs = t2.quarterly_income_stmt
        if qs is not None and not qs.empty:
            earnings_dates = [_strip_tz(d) for d in qs.columns if pd.notna(d)][:16]
    except Exception:
        pass

if not earnings_dates:
    st.markdown('<div class="warn-box">Could not retrieve earnings dates for this ticker. Try a major US stock like AAPL, MSFT, or TSLA.</div>', unsafe_allow_html=True)
    st.stop()

reactions = compute_reaction(price_df, earnings_dates[:20])

if not reactions:
    st.markdown('<div class="warn-box">Could not compute reactions - not enough price history.</div>', unsafe_allow_html=True)
    st.stop()

# -- Summary stats --------------------------------------------------------------
cp = float(price_df["Close"].iloc[-1])
name = info.get("longName") or info.get("shortName") or ticker

st.markdown(f"""
<div style="background:#0d1117;border:1px solid #1a2235;border-radius:10px;padding:1.2rem 1.5rem;margin:1rem 0;display:flex;align-items:center;gap:2rem;flex-wrap:wrap;">
    <div>
        <div style="font-family:'Bebas Neue',sans-serif;font-size:2rem;">{ticker}</div>
        <div style="font-family:'IBM Plex Mono',monospace;font-size:0.65rem;color:#3a4558;">{name}</div>
    </div>
    <div style="font-family:'IBM Plex Mono',monospace;font-size:1.2rem;">${cp:,.2f}</div>
    <div style="font-family:'IBM Plex Mono',monospace;font-size:0.68rem;color:#3a4558;margin-left:auto;">{len(reactions)} earnings events analysed</div>
</div>
""", unsafe_allow_html=True)

day_of_moves    = [r["day_of"]    for r in reactions]
followthrough   = [r["5d_follow"] for r in reactions]
pre_runs        = [r["5d_pre"]    for r in reactions]
avg_day_of      = np.mean(day_of_moves)
avg_follow      = np.mean(followthrough)
avg_pre         = np.mean(pre_runs)
beat_pct        = sum(1 for x in day_of_moves if x > 0) / len(day_of_moves) * 100
avg_up_move     = np.mean([x for x in day_of_moves if x > 0]) if any(x > 0 for x in day_of_moves) else 0
avg_down_move   = np.mean([x for x in day_of_moves if x < 0]) if any(x < 0 for x in day_of_moves) else 0

st.markdown('<div class="divider">Average Reaction</div>', unsafe_allow_html=True)
avg_cols = st.columns(6)
for col, lbl, val, fmt in [
    (avg_cols[0], "Avg Day-of Move",    avg_day_of,    "pct"),
    (avg_cols[1], "Avg Up Move",        avg_up_move,   "pct"),
    (avg_cols[2], "Avg Down Move",      avg_down_move, "pct"),
    (avg_cols[3], "Beat Rate",          beat_pct,      "beat"),
    (avg_cols[4], "Avg Pre-Earnings",   avg_pre,       "pct"),
    (avg_cols[5], "Avg Post-Earnings",  avg_follow,    "pct"),
]:
    if fmt == "beat": cls = "pos" if beat_pct>=50 else "neg"; d = f"{val:.0f}%"
    else: cls = "pos" if val>=0 else "neg"; d = f"{val:+.2f}%"
    col.markdown(f'<div class="metric-card"><div class="metric-val {cls}">{d}</div><div class="metric-lbl">{lbl}</div></div>', unsafe_allow_html=True)

# -- Visual chart ---------------------------------------------------------------
st.markdown('<div class="divider">Day-of Reaction Per Earnings</div>', unsafe_allow_html=True)
import plotly.graph_objects as go

dates_short = [r["date"] for r in reactions]
moves       = [r["day_of"] for r in reactions]
colors_     = ["#00d68f" if m >= 0 else "#ff4757" for m in moves]

fig = go.Figure()
fig.add_trace(go.Bar(
    x=dates_short, y=moves, marker_color=colors_,
    text=[f"{m:+.1f}%" for m in moves], textposition="outside",
    textfont=dict(size=10, color="#8892a4"),
    hovertemplate="<b>%{x}</b><br>Day-of: %{y:+.2f}%<extra></extra>"
))
fig.add_hline(y=0, line_color="#1a2235", line_width=1)
fig.update_layout(
    paper_bgcolor="#07090d", plot_bgcolor="#07090d",
    font=dict(family="IBM Plex Mono", color="#8892a4", size=11),
    xaxis=dict(gridcolor="#1a2235", linecolor="#1a2235", tickangle=-45),
    yaxis=dict(gridcolor="#1a2235", linecolor="#1a2235", ticksuffix="%"),
    margin=dict(l=10,r=10,t=30,b=60), height=320, showlegend=False,
    title=dict(text=f"{ticker} - Earnings Day-of Price Move", font=dict(size=12,color="#8892a4"))
)
st.plotly_chart(fig, use_container_width=True)

# -- Pre vs Post scatter --------------------------------------------------------
st.markdown('<div class="divider">Pre-Earnings Run vs Post-Earnings Follow-Through</div>', unsafe_allow_html=True)
fig2 = go.Figure()
fig2.add_trace(go.Scatter(
    x=pre_runs, y=followthrough,
    mode="markers+text",
    text=[r["date"][:6] for r in reactions],
    textposition="top center", textfont=dict(size=9, color="#3a4558"),
    marker=dict(
        size=10, color=day_of_moves,
        colorscale=[[0,"#ff4757"],[0.5,"#3a4558"],[1,"#00d68f"]],
        colorbar=dict(title="Day-of %", tickfont=dict(size=9)),
        showscale=True
    ),
    hovertemplate="<b>%{text}</b><br>Pre: %{x:+.1f}%<br>Post: %{y:+.1f}%<extra></extra>"
))
fig2.add_hline(y=0, line_color="#1a2235", line_width=1)
fig2.add_vline(x=0, line_color="#1a2235", line_width=1)
fig2.update_layout(
    paper_bgcolor="#07090d", plot_bgcolor="#07090d",
    font=dict(family="IBM Plex Mono", color="#8892a4", size=11),
    xaxis=dict(gridcolor="#1a2235", linecolor="#1a2235", ticksuffix="%", title="5-day pre-earnings"),
    yaxis=dict(gridcolor="#1a2235", linecolor="#1a2235", ticksuffix="%", title="5-day post-earnings"),
    margin=dict(l=50,r=10,t=20,b=50), height=380,
)
st.plotly_chart(fig2, use_container_width=True)

# -- Detailed table -------------------------------------------------------------
st.markdown('<div class="divider">All Events</div>', unsafe_allow_html=True)
table_data = []
for r in reactions:
    table_data.append({
        "Date":          r["date"],
        "Price":         f"${r['price']:,.2f}",
        "Day-of Move":   f"{r['day_of']:+.2f}%",
        "5d Pre-Run":    f"{r['5d_pre']:+.2f}%",
        "5d Follow":     f"{r['5d_follow']:+.2f}%",
        "Reaction":      "Gap Up [G]" if r["day_of"] > 2 else ("Gap Down [R]" if r["day_of"] < -2 else "Flat [W]"),
    })
df_table = pd.DataFrame(table_data)
st.dataframe(df_table, use_container_width=True, hide_index=True)

# -- Key takeaway ---------------------------------------------------------------
gap_up_count   = sum(1 for r in reactions if r["day_of"] > 2)
gap_down_count = sum(1 for r in reactions if r["day_of"] < -2)
st.markdown(f"""
<div style="background:#0d1117;border:1px solid #1a2235;border-radius:8px;padding:1.2rem 1.5rem;margin-top:1rem;">
    <div style="font-family:'IBM Plex Mono',monospace;font-size:0.6rem;color:#3a4558;text-transform:uppercase;letter-spacing:0.15em;margin-bottom:0.6rem;">Pattern Summary</div>
    <div style="display:flex;gap:2rem;flex-wrap:wrap;font-size:0.84rem;color:#8892a4;line-height:1.7;">
        <span>[G] Gap ups (+2%): <strong style="color:#e2e8f0;">{gap_up_count}</strong></span>
        <span>[R] Gap downs (-2%): <strong style="color:#e2e8f0;">{gap_down_count}</strong></span>
        <span>Average reaction: <strong style="color:{'#00d68f' if avg_day_of>=0 else '#ff4757'};">{avg_day_of:+.2f}%</strong></span>
        <span>Stock tends to {'gap up' if avg_day_of > 0 else 'gap down'} on earnings.</span>
        <span>After a gap up, averages <strong style="color:{'#00d68f' if avg_follow>=0 else '#ff4757'};">{avg_follow:+.2f}%</strong> over the next 5 days.</span>
    </div>
</div>
""", unsafe_allow_html=True)
