import streamlit as st, sys, os, pandas as pd, numpy as np, yfinance as yf
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(__file__)))
from utils.session_persist import restore_session
import plotly.graph_objects as go
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.styles import SHARED_CSS, inject_bg, PLOTLY_THEME; from utils.nav import navbar

st.set_page_config(page_title="Pattern Recognition | 11%", layout="wide", initial_sidebar_state="collapsed")
restore_session()
st.markdown(SHARED_CSS, unsafe_allow_html=True)
st.markdown("""<style>
.ph{background:linear-gradient(135deg,#0c1018,#0d1420);border:1px solid #1a2235;border-radius:16px;padding:2.5rem 3rem;margin-bottom:2rem}
.ph h1{font-family:'Bebas Neue',sans-serif;font-size:3.5rem;letter-spacing:0.05em;line-height:1;margin:0 0 0.5rem 0}
.ph p{font-family:'IBM Plex Mono',monospace;font-size:0.75rem;color:#8896ab;line-height:1.8;margin:0}
.ph-ey{font-family:'IBM Plex Mono',monospace;font-size:0.55rem;text-transform:uppercase;letter-spacing:0.3em;color:#3a4a5e;margin-bottom:0.5rem}
.sec-t{font-family:'IBM Plex Mono',monospace;font-size:0.55rem;text-transform:uppercase;letter-spacing:0.25em;color:#3a4a5e;padding:1.2rem 0 0.8rem;border-top:1px solid #0d1117}
.pat-card{background:#0c1018;border-left:3px solid #1a2235;border-top:1px solid #1a2235;border-right:1px solid #1a2235;border-bottom:1px solid #1a2235;border-radius:0 12px 12px 0;padding:1.2rem 1.5rem;margin-bottom:0.6rem}
.pat-card:hover{background:#0d1117}
.pat-title{font-family:'Bebas Neue',sans-serif;font-size:1.4rem;letter-spacing:0.05em;margin-bottom:0.3rem}
.pat-date{font-family:'IBM Plex Mono',monospace;font-size:0.6rem;color:#8896ab}
.pat-desc{font-family:'IBM Plex Mono',monospace;font-size:0.68rem;color:#8896ab;line-height:1.7;margin-top:0.4rem}
</style>""", unsafe_allow_html=True)
navbar()
inject_bg()

st.markdown("""<div class="ph"><div class="ph-ey">Chart Patterns</div><h1>Pattern Recognition</h1>
<p>Automatically detect common chart patterns on any stock. Double tops, flags, support and resistance levels — flagged and explained.</p></div>""", unsafe_allow_html=True)

c1, c2, c3 = st.columns([2, 1.5, 1.5])
with c1: ticker = st.text_input("Ticker", value="AAPL", placeholder="AAPL, TSLA, SPY").upper().strip()
with c2: period_sel = st.selectbox("Period", ["3mo","6mo","1y","2y"], index=1,
                                    format_func=lambda x: {"3mo":"3 Months","6mo":"6 Months","1y":"1 Year","2y":"2 Years"}[x])
with c3:
    st.markdown("<br>", unsafe_allow_html=True)
    run_btn = st.button("Scan Patterns", type="primary", use_container_width=True)


def scalar(x):
    """Convert anything (numpy scalar, array, list) to a plain Python float."""
    if isinstance(x, (list, np.ndarray)):
        x = np.asarray(x, dtype=float).flat[0]
    return float(x)


def find_pivots(close_list, high_list, low_list, window=8):
    """
    All inputs are plain Python lists of floats.
    Returns lists of integer positions (plain Python ints).
    """
    n = len(close_list)
    h_pivots, l_pivots = [], []
    for i in range(window, n - window):
        hi_window = high_list[i - window : i + window + 1]
        lo_window = low_list[i - window : i + window + 1]
        if high_list[i] == max(hi_window):
            h_pivots.append(i)          # plain Python int from range()
        if low_list[i] == min(lo_window):
            l_pivots.append(i)
    return h_pivots, l_pivots


def detect_patterns(df):
    """
    df has columns Open/High/Low/Close/Volume with a DatetimeIndex.
    All arithmetic done entirely on plain Python lists of floats.
    """
    patterns = []
    n = len(df)
    if n < 40:
        return patterns

    # Extract as plain Python lists of floats — bulletproof against any array shape
    close_list = [scalar(v) for v in df["Close"].tolist()]
    high_list  = [scalar(v) for v in df["High"].tolist()]
    low_list   = [scalar(v) for v in df["Low"].tolist()]
    dates      = df.index.tolist()   # list of Timestamps

    h_pivots, l_pivots = find_pivots(close_list, high_list, low_list, window=8)

    # ── Double Top ──────────────────────────────────────────────────────────
    if len(h_pivots) >= 2:
        p1 = h_pivots[-2]   # plain int
        p2 = h_pivots[-1]   # plain int
        h1 = high_list[p1]  # plain float
        h2 = high_list[p2]  # plain float
        if h1 > 0 and abs(h1 - h2) / h1 < 0.03 and (p2 - p1) > 10:
            patterns.append({
                "name": "Double Top", "type": "bear",
                "chart_idx": p2,       # plain int for df.index[]
                "price": h1,
                "date": str(dates[p2])[:10],
                "desc": f"Two peaks near ${h1:.2f}. Classic reversal — neckline break targets the pattern height below the neckline.",
            })

    # ── Double Bottom ───────────────────────────────────────────────────────
    if len(l_pivots) >= 2:
        p1 = l_pivots[-2]
        p2 = l_pivots[-1]
        l1 = low_list[p1]
        l2 = low_list[p2]
        if l1 > 0 and abs(l1 - l2) / l1 < 0.03 and (p2 - p1) > 10:
            patterns.append({
                "name": "Double Bottom", "type": "bull",
                "chart_idx": p2,
                "price": l1,
                "date": str(dates[p2])[:10],
                "desc": f"Two troughs near ${l1:.2f}. Bullish reversal — buy the breakout above the neckline with stop below the second low.",
            })

    # ── Bullish Flag ────────────────────────────────────────────────────────
    if n > 50:
        # Find highest point in the last 30 bars
        window_start = n - 30
        recent_highs = high_list[window_start : n]   # plain list slice
        peak_val     = max(recent_highs)
        peak_local   = recent_highs.index(peak_val)  # index within slice
        peak_global  = window_start + peak_local      # index in full list

        if 0 < peak_local < 20:  # peak is in middle of window, not at edge
            flag_hi   = max(close_list[n - 15 : n])
            flag_lo   = min(close_list[n - 15 : n])
            pole_lo   = min(close_list[max(0, n - 50) : window_start])
            pole_rise = (peak_val - pole_lo) / pole_lo * 100 if pole_lo > 0 else 0
            consol    = (flag_hi - flag_lo) / flag_hi * 100 if flag_hi > 0 else 999

            if pole_rise > 10 and consol < 8:
                patterns.append({
                    "name": "Bull Flag", "type": "bull",
                    "chart_idx": n - 1,
                    "price": close_list[-1],
                    "date": str(dates[-1])[:10],
                    "desc": f"Strong pole (+{pole_rise:.1f}%) followed by tight {consol:.1f}% consolidation. Wait for breakout above flag highs.",
                })

    # ── Support Zone ────────────────────────────────────────────────────────
    if len(l_pivots) >= 3:
        k    = min(5, len(l_pivots))
        use  = l_pivots[-k:]                      # list of k plain ints
        lows = [low_list[i] for i in use]         # list of k floats
        avg  = sum(lows) / len(lows)
        rng  = (max(lows) - min(lows)) / avg * 100 if avg > 0 else 999
        if rng < 5:
            last_idx = use[-1]   # plain int
            patterns.append({
                "name": "Support Zone", "type": "bull",
                "chart_idx": last_idx,
                "price": avg,
                "date": str(dates[last_idx])[:10],
                "desc": f"Multiple touches near ${avg:.2f} (±{rng/2:.1f}% spread). Strong horizontal support — high-probability bounce zone.",
            })

    # ── Resistance Zone ─────────────────────────────────────────────────────
    if len(h_pivots) >= 3:
        k     = min(5, len(h_pivots))
        use   = h_pivots[-k:]
        highs = [high_list[i] for i in use]
        avg   = sum(highs) / len(highs)
        rng   = (max(highs) - min(highs)) / avg * 100 if avg > 0 else 999
        if rng < 5:
            last_idx = use[-1]
            patterns.append({
                "name": "Resistance Zone", "type": "bear",
                "chart_idx": last_idx,
                "price": avg,
                "date": str(dates[last_idx])[:10],
                "desc": f"Multiple rejections near ${avg:.2f} (±{rng/2:.1f}% spread). Strong resistance — wait for confirmed breakout or short the rejection.",
            })

    return patterns


# ── Run ──────────────────────────────────────────────────────────────────────
if run_btn:
    with st.spinner(f"Scanning {ticker}..."):
        try:
            raw = yf.Ticker(ticker).history(period=period_sel)
            if raw.empty or len(raw) < 40:
                st.error("Not enough data. Try a longer period or different ticker."); st.stop()

            # Flatten MultiIndex columns (yfinance sometimes returns these)
            if isinstance(raw.columns, pd.MultiIndex):
                raw.columns = raw.columns.get_level_values(0)
            # Drop duplicated columns (keep first occurrence)
            raw = raw.loc[:, ~raw.columns.duplicated()]

            df = raw[["Open","High","Low","Close","Volume"]].copy()
            patterns = detect_patterns(df)
            st.session_state["pr_df"]       = df
            st.session_state["pr_patterns"] = patterns
            st.session_state["pr_ticker"]   = ticker
        except Exception as e:
            import traceback
            st.error(f"Error scanning {ticker}: {e}")
            with st.expander("Full traceback"):
                st.code(traceback.format_exc())
            st.stop()

# ── Display ──────────────────────────────────────────────────────────────────
if "pr_df" in st.session_state:
    df       = st.session_state["pr_df"]
    patterns = st.session_state["pr_patterns"]
    ticker   = st.session_state["pr_ticker"]

    fig = go.Figure()
    fig.add_candlestick(
        x=df.index,
        open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"],
        increasing_line_color="#00e676", decreasing_line_color="#ff3d57",
        increasing_fillcolor="#00e676", decreasing_fillcolor="#ff3d57",
        name=ticker,
    )

    for p in patterns:
        color  = "#00e676" if p["type"] == "bull" else "#ff3d57"
        # Use df.index with a safe plain-int position
        idx    = min(max(0, p["chart_idx"]), len(df) - 1)
        x_val  = df.index[idx]          # Timestamp — safe to pass to plotly
        y_val  = p["price"]             # float
        ay_dir = -45 if p["type"] == "bull" else 45
        fig.add_annotation(
            x=x_val, y=y_val, text=p["name"],
            showarrow=True, arrowhead=2, arrowcolor=color, arrowwidth=1.5,
            font=dict(color=color, family="IBM Plex Mono", size=11),
            bgcolor="#06080c", bordercolor=color, borderpad=4,
            ax=50, ay=ay_dir,
        )
        if p["name"] in ("Support Zone", "Resistance Zone"):
            fig.add_hline(y=y_val, line_dash="dash", line_color=color + "55", line_width=1)

    fig.update_layout(
        **PLOTLY_THEME, height=480,
        title=f"{ticker} — Pattern Scan ({period_sel})",
        xaxis_rangeslider_visible=False,
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="sec-t">Detected Patterns</div>', unsafe_allow_html=True)
    if patterns:
        for p in patterns:
            color = "#00e676" if p["type"] == "bull" else "#ff3d57"
            bias  = "Bullish" if p["type"] == "bull" else "Bearish"
            st.markdown(f"""
            <div class="pat-card" style="border-left-color:{color}">
                <div class="pat-title" style="color:{color}">{p["name"]}
                    <span style="font-family:IBM Plex Mono,monospace;font-size:0.6rem;font-weight:400"> — {bias}</span>
                </div>
                <div class="pat-date">Detected at ${p["price"]:.2f} · {p["date"]}</div>
                <div class="pat-desc">{p["desc"]}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown(
            '<div style="font-family:IBM Plex Mono,monospace;font-size:0.75rem;color:#3a4a5e;'
            'padding:1.5rem;border:1px dashed #1a2235;border-radius:12px;text-align:center;">'
            'No clear patterns detected. Try a longer timeframe or a different ticker.</div>',
            unsafe_allow_html=True,
        )
