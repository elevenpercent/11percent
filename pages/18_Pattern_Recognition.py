import streamlit as st, sys, os, pandas as pd, numpy as np, yfinance as yf
import plotly.graph_objects as go
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.styles import SHARED_CSS, PLOTLY_THEME; from utils.nav import navbar

st.set_page_config(page_title="Pattern Recognition | 11%", layout="wide", initial_sidebar_state="collapsed")
st.markdown(SHARED_CSS, unsafe_allow_html=True)
st.markdown("""<style>
.ph{background:linear-gradient(135deg,#0c1018,#0d1420);border:1px solid #1a2235;border-radius:16px;padding:2.5rem 3rem;margin-bottom:2rem}
.ph h1{font-family:'Bebas Neue',sans-serif;font-size:3.5rem;letter-spacing:0.05em;line-height:1;margin:0 0 0.5rem 0}
.ph p{font-family:'IBM Plex Mono',monospace;font-size:0.75rem;color:#8896ab;line-height:1.8;margin:0}
.ph-ey{font-family:'IBM Plex Mono',monospace;font-size:0.55rem;text-transform:uppercase;letter-spacing:0.3em;color:#3a4a5e;margin-bottom:0.5rem}
.sec-t{font-family:'IBM Plex Mono',monospace;font-size:0.55rem;text-transform:uppercase;letter-spacing:0.25em;color:#3a4a5e;padding:1.2rem 0 0.8rem;border-top:1px solid #0d1117}
.pat-card{background:#0c1018;border-left:3px solid #1a2235;border-radius:0 12px 12px 0;border-top:1px solid #1a2235;border-right:1px solid #1a2235;border-bottom:1px solid #1a2235;padding:1.2rem 1.5rem;margin-bottom:0.6rem;transition:border-color 0.2s}
.pat-card:hover{background:#0d1117}
.pat-title{font-family:'Bebas Neue',sans-serif;font-size:1.4rem;letter-spacing:0.05em;margin-bottom:0.3rem}
.pat-date{font-family:'IBM Plex Mono',monospace;font-size:0.6rem;color:#8896ab}
.pat-desc{font-family:'IBM Plex Mono',monospace;font-size:0.68rem;color:#8896ab;line-height:1.7;margin-top:0.4rem}
</style>""", unsafe_allow_html=True)
navbar()

st.markdown("""<div class="ph"><div class="ph-ey">Chart Patterns</div><h1>Pattern Recognition</h1>
<p>Automatically detect common chart patterns on any stock. Double tops, flags, support and resistance levels — flagged and explained so you know exactly what to do next.</p></div>""", unsafe_allow_html=True)

c1, c2, c3 = st.columns([2, 1.5, 1.5])
with c1: ticker = st.text_input("Ticker", value="AAPL", placeholder="AAPL, TSLA, SPY").upper().strip()
with c2: period_sel = st.selectbox("Period", ["3mo","6mo","1y","2y"], index=1,
                                    format_func=lambda x: {"3mo":"3 Months","6mo":"6 Months","1y":"1 Year","2y":"2 Years"}[x])
with c3:
    st.markdown("<br>", unsafe_allow_html=True)
    run_btn = st.button("Scan Patterns", type="primary", use_container_width=True)


def find_pivots(prices, window=5):
    """Find pivot highs and lows. prices must be a plain Python list or 1-D numpy array."""
    highs, lows = [], []
    n = len(prices)
    for i in range(window, n - window):
        seg = prices[i - window : i + window + 1]
        # Use float() to ensure scalar comparison — avoids numpy array ambiguity
        val = float(prices[i])
        seg_max = float(np.max(seg))
        seg_min = float(np.min(seg))
        if val == seg_max:
            highs.append(i)
        if val == seg_min:
            lows.append(i)
    return highs, lows


def safe_idx(arr, idx):
    """Return a plain Python float from a numpy array index."""
    return float(arr[int(idx)])


def detect_patterns(df):
    patterns = []
    close = df["Close"].to_numpy(dtype=float)
    high  = df["High"].to_numpy(dtype=float)
    low   = df["Low"].to_numpy(dtype=float)
    dates = df.index.tolist()
    n = len(close)

    h_pivots, l_pivots = find_pivots(high, 8), find_pivots(low, 8)

    # ── Double Top ──────────────────────────────────────────────────────────
    if len(h_pivots) >= 2:
        p1, p2 = int(h_pivots[-2]), int(h_pivots[-1])
        h1, h2 = float(high[p1]), float(high[p2])
        if h1 > 0 and abs(h1 - h2) / h1 < 0.03 and p2 - p1 > 10:
            patterns.append({
                "name": "Double Top", "type": "bear", "idx1": p1, "idx2": p2, "price": h1,
                "date": str(dates[p2])[:10],
                "desc": f"Two peaks near ${h1:.2f}. Classic reversal signal — if the neckline breaks, the measured target is the height of the pattern subtracted from the neckline."
            })

    # ── Double Bottom ────────────────────────────────────────────────────────
    if len(l_pivots) >= 2:
        p1, p2 = int(l_pivots[-2]), int(l_pivots[-1])
        l1, l2 = float(low[p1]), float(low[p2])
        if l1 > 0 and abs(l1 - l2) / l1 < 0.03 and p2 - p1 > 10:
            patterns.append({
                "name": "Double Bottom", "type": "bull", "idx1": p1, "idx2": p2, "price": l1,
                "date": str(dates[p2])[:10],
                "desc": f"Two troughs near ${l1:.2f}. Bullish reversal — buy the breakout above the neckline with a stop below the second low."
            })

    # ── Bullish Flag ─────────────────────────────────────────────────────────
    if n > 45:
        recent_window = high[max(0, n-30) : n]
        rh_local = int(np.argmax(recent_window))   # index within recent_window
        rh_global = max(0, n-30) + rh_local         # index in full array

        if 0 < rh_local < 20:
            flag_slice  = close[max(0, n-15) : n]
            flag_high   = float(np.max(flag_slice))
            flag_low    = float(np.min(flag_slice))
            pole_slice  = close[max(0, n-45) : max(0, n-30)]
            pole_low    = float(np.min(pole_slice)) if len(pole_slice) > 0 else float(close[0])
            pole_top    = float(high[rh_global])

            if pole_low > 0 and flag_high > 0:
                pole_rise     = (pole_top - pole_low) / pole_low * 100
                consolidation = (flag_high - flag_low) / flag_high * 100
                if pole_rise > 10 and consolidation < 8:
                    patterns.append({
                        "name": "Bull Flag", "type": "bull", "idx1": max(0, n-45), "idx2": n-1,
                        "price": float(close[-1]),
                        "date": str(dates[-1])[:10],
                        "desc": f"Strong pole (+{pole_rise:.1f}%) followed by tight consolidation ({consolidation:.1f}% range). Wait for breakout above the flag highs for a continuation entry."
                    })

    # ── Support Zone ─────────────────────────────────────────────────────────
    if len(l_pivots) >= 3:
        # Use up to 5 most recent pivots safely
        use_pivots = l_pivots[-min(5, len(l_pivots)):]
        recent_lows = [float(low[int(i)]) for i in use_pivots]
        avg_low = float(np.mean(recent_lows))
        spread  = (max(recent_lows) - min(recent_lows)) / avg_low * 100 if avg_low > 0 else 999
        if spread < 5:
            patterns.append({
                "name": "Support Zone", "type": "bull",
                "idx1": int(use_pivots[0]), "idx2": int(use_pivots[-1]),
                "price": avg_low,
                "date": str(dates[int(use_pivots[-1])])[:10],
                "desc": f"Multiple touches near ${avg_low:.2f} (range ±{spread/2:.1f}%). Strong horizontal support. High-probability bounce zone with a clearly defined risk level."
            })

    # ── Resistance Zone ───────────────────────────────────────────────────────
    if len(h_pivots) >= 3:
        use_pivots = h_pivots[-min(5, len(h_pivots)):]
        recent_highs = [float(high[int(i)]) for i in use_pivots]
        avg_high = float(np.mean(recent_highs))
        spread   = (max(recent_highs) - min(recent_highs)) / avg_high * 100 if avg_high > 0 else 999
        if spread < 5:
            patterns.append({
                "name": "Resistance Zone", "type": "bear",
                "idx1": int(use_pivots[0]), "idx2": int(use_pivots[-1]),
                "price": avg_high,
                "date": str(dates[int(use_pivots[-1])])[:10],
                "desc": f"Multiple rejections near ${avg_high:.2f} (range ±{spread/2:.1f}%). Strong resistance ceiling. Wait for a confirmed breakout above, or short the rejection with a tight stop."
            })

    return patterns


if run_btn:
    with st.spinner(f"Scanning {ticker}..."):
        try:
            raw = yf.Ticker(ticker).history(period=period_sel)
            if raw.empty or len(raw) < 40:
                st.error("Not enough data. Try a longer period or different ticker."); st.stop()
            df = raw[["Open","High","Low","Close","Volume"]].copy()
            patterns = detect_patterns(df)
            st.session_state["pr_df"]       = df
            st.session_state["pr_patterns"] = patterns
            st.session_state["pr_ticker"]   = ticker
        except Exception as e:
            st.error(f"Error: {e}"); st.stop()

if "pr_df" in st.session_state:
    df       = st.session_state["pr_df"]
    patterns = st.session_state["pr_patterns"]
    ticker   = st.session_state["pr_ticker"]

    # Candlestick chart with pattern annotations
    fig = go.Figure()
    fig.add_candlestick(
        x=df.index, open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"],
        increasing_line_color="#00e676", decreasing_line_color="#ff3d57",
        increasing_fillcolor="#00e676", decreasing_fillcolor="#ff3d57",
        name=ticker
    )
    for p in patterns:
        color  = "#00e676" if p["type"] == "bull" else "#ff3d57" if p["type"] == "bear" else "#ffd166"
        idx    = min(int(p["idx2"]), len(df) - 1)
        ay_dir = -40 if p["type"] == "bull" else 40
        fig.add_annotation(
            x=df.index[idx], y=p["price"],
            text=p["name"],
            showarrow=True, arrowhead=2, arrowcolor=color,
            font=dict(color=color, family="IBM Plex Mono", size=11),
            bgcolor="#06080c", bordercolor=color,
            ax=50, ay=ay_dir
        )
        if p["name"] in ["Support Zone", "Resistance Zone"]:
            fig.add_hline(y=p["price"], line_dash="dash", line_color=color + "66", line_width=1)

    fig.update_layout(**PLOTLY_THEME, height=480,
                      title=f"{ticker} — Pattern Scan",
                      xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

    # Pattern cards
    st.markdown('<div class="sec-t">Detected Patterns</div>', unsafe_allow_html=True)
    if patterns:
        for p in patterns:
            color  = "#00e676" if p["type"] == "bull" else "#ff3d57" if p["type"] == "bear" else "#ffd166"
            bias   = "Bullish" if p["type"] == "bull" else "Bearish" if p["type"] == "bear" else "Neutral"
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
        st.markdown('<div style="font-family:IBM Plex Mono,monospace;font-size:0.75rem;color:#3a4a5e;padding:1.5rem 0;border:1px dashed #1a2235;border-radius:12px;text-align:center;">No clear patterns detected in this period. Try a longer timeframe or a different ticker.</div>', unsafe_allow_html=True)
