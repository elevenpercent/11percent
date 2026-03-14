import streamlit as st, sys, os, pandas as pd, numpy as np
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(__file__)))
from utils.session_persist import restore_session
import plotly.graph_objects as go
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.styles import SHARED_CSS, inject_bg, PLOTLY_THEME; from utils.nav import navbar

st.set_page_config(page_title="Trade Stats | 11%", layout="wide", initial_sidebar_state="collapsed")
restore_session()
st.markdown(SHARED_CSS, unsafe_allow_html=True)
st.markdown("""<style>
.ph{background:linear-gradient(135deg,#0c1018,#0d1420);border:1px solid #1a2235;border-radius:16px;padding:2.5rem 3rem;margin-bottom:2rem}
.ph h1{font-family:'Bebas Neue',sans-serif;font-size:3.5rem;letter-spacing:0.05em;line-height:1;margin:0 0 0.5rem 0}
.ph p{font-family:'IBM Plex Mono',monospace;font-size:0.75rem;color:#8896ab;line-height:1.8;margin:0}
.ph-ey{font-family:'IBM Plex Mono',monospace;font-size:0.55rem;text-transform:uppercase;letter-spacing:0.3em;color:#3a4a5e;margin-bottom:0.5rem}
.sec-t{font-family:'IBM Plex Mono',monospace;font-size:0.55rem;text-transform:uppercase;letter-spacing:0.25em;color:#3a4a5e;padding:1.2rem 0 0.8rem;border-top:1px solid #0d1117}
.bm{background:#0c1018;border:1px solid #1a2235;border-radius:12px;padding:1.5rem 1.8rem;transition:border-color 0.2s}
.bm:hover{border-color:#2a3550}
.bm-v{font-family:'Bebas Neue',sans-serif;font-size:2.4rem;letter-spacing:0.04em;line-height:1}
.bm-l{font-family:'IBM Plex Mono',monospace;font-size:0.5rem;text-transform:uppercase;letter-spacing:0.22em;color:#3a4a5e;margin-top:0.35rem}
.bm-s{font-family:'IBM Plex Mono',monospace;font-size:0.62rem;color:#8896ab;margin-top:0.2rem}
.upload-zone{border:2px dashed #1a2235;border-radius:12px;padding:3rem;text-align:center;margin:1rem 0}
.upload-zone-title{font-family:'Bebas Neue',sans-serif;font-size:2rem;color:#3a4a5e;letter-spacing:0.06em;margin-bottom:0.5rem}
.upload-zone-sub{font-family:'IBM Plex Mono',monospace;font-size:0.68rem;color:#3a4a5e;line-height:1.8}
</style>""", unsafe_allow_html=True)
navbar()
inject_bg()

st.markdown("""<div class="ph"><div class="ph-ey">Performance Analytics</div><h1>Trade Stats</h1>
<p>Upload a CSV of your trade history and get a full breakdown: equity curve, win rate, max drawdown, streak analysis, R-distribution, and expectancy — everything you need to know if your edge is real.</p></div>""", unsafe_allow_html=True)

st.markdown('<div class="sec-t">Upload Your Trade History</div>', unsafe_allow_html=True)
st.markdown("""<div class="upload-zone">
    <div class="upload-zone-title">Drop your CSV here</div>
    <div class="upload-zone-sub">Required columns: <strong style="color:#eef2f7">date, pnl</strong><br>Optional: symbol, direction, entry, exit, qty, strategy</div>
</div>""", unsafe_allow_html=True)

uploaded = st.file_uploader("Upload CSV", type=["csv"], label_visibility="collapsed")

DEMO_DATA = pd.DataFrame({
    "date": pd.date_range("2024-01-01", periods=50, freq="B"),
    "pnl": [120,-85,230,-40,180,95,-150,310,-90,200,
            -60,140,85,-120,175,-45,260,-80,190,110,
            -200,150,75,-110,220,-55,300,-95,180,130,
            -70,160,90,-130,195,-50,270,-85,200,120,
            -80,170,100,-140,215,-60,285,-90,210,140],
    "symbol": ["AAPL","TSLA","NVDA","AMD","MSFT","GOOGL","META","JPM","V","MA"]*5,
    "strategy": ["EMA Cross","RSI","MACD","SuperTrend","Custom"]*10,
})

use_demo = st.checkbox("Use demo data (50 trades)", value=False)

df = None
if uploaded:
    try:
        df = pd.read_csv(uploaded)
        if "pnl" not in df.columns:
            st.error("CSV must have a 'pnl' column."); df = None
        else:
            df["date"] = pd.to_datetime(df["date"])
            df = df.sort_values("date").reset_index(drop=True)
    except Exception as e:
        st.error(f"Error reading CSV: {e}")
elif use_demo:
    df = DEMO_DATA.copy()

if df is not None:
    pnl = df["pnl"]
    n = len(pnl)
    wins = (pnl > 0).sum(); losses = (pnl < 0).sum()
    wr = wins/n*100
    avg_win  = pnl[pnl>0].mean() if wins > 0 else 0
    avg_loss = pnl[pnl<0].mean() if losses > 0 else 0
    expectancy = (wr/100 * avg_win) + ((1-wr/100) * avg_loss)
    total_pnl = pnl.sum()
    cum_pnl = pnl.cumsum()
    peak = cum_pnl.cummax()
    drawdown = cum_pnl - peak
    max_dd = drawdown.min()
    profit_factor = abs(pnl[pnl>0].sum() / pnl[pnl<0].sum()) if losses > 0 else 999

    # Streak
    streak = max_streak = 0; cur_streak = 0
    for p in pnl:
        if p > 0: cur_streak = max(cur_streak+1, 1)
        else: cur_streak = min(cur_streak-1, -1)
        if abs(cur_streak) > abs(streak): streak = cur_streak

    st.markdown('<div class="sec-t">Key Statistics</div>', unsafe_allow_html=True)
    r1 = st.columns(4)
    r2 = st.columns(4)
    for col,(v,l,s,c) in zip(r1,[
        (f"{wr:.1f}%","Win Rate",f"{wins}W / {losses}L","#00e676" if wr>=50 else "#ff3d57"),
        (f"${total_pnl:+,.0f}","Total P&L",f"{n} trades total","#00e676" if total_pnl>=0 else "#ff3d57"),
        (f"${expectancy:+.0f}","Expectancy","per trade","#4da6ff"),
        (f"{profit_factor:.2f}x","Profit Factor",">1.5 is good","#ffd166"),
    ]): col.markdown(f'<div class="bm"><div class="bm-v" style="color:{c}">{v}</div><div class="bm-l">{l}</div><div class="bm-s">{s}</div></div>', unsafe_allow_html=True)
    for col,(v,l,s,c) in zip(r2,[
        (f"${avg_win:+.0f}","Avg Win","per winning trade","#00e676"),
        (f"${avg_loss:+.0f}","Avg Loss","per losing trade","#ff3d57"),
        (f"${max_dd:+,.0f}","Max Drawdown","peak to trough","#ff3d57"),
        (f"{streak:+d}","Best Streak",f"consecutive","#4da6ff"),
    ]): col.markdown(f'<div class="bm"><div class="bm-v" style="color:{c}">{v}</div><div class="bm-l">{l}</div><div class="bm-s">{s}</div></div>', unsafe_allow_html=True)

    # Equity Curve
    st.markdown('<div class="sec-t">Equity Curve</div>', unsafe_allow_html=True)
    fig_eq = go.Figure()
    fig_eq.add_scatter(x=list(range(1,n+1)), y=cum_pnl, fill="tozeroy",
                       fillcolor="rgba(0,230,118,0.07)",
                       line=dict(color="#00e676", width=2), name="Cumulative P&L")
    fig_eq.add_scatter(x=list(range(1,n+1)), y=peak, line=dict(color="#4da6ff", width=1, dash="dot"),
                       name="Peak", opacity=0.5)
    fig_eq.update_layout(**PLOTLY_THEME, height=300, xaxis_title="Trade #", yaxis_title="Cumulative P&L ($)")
    st.plotly_chart(fig_eq, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        # Drawdown chart
        st.markdown('<div class="sec-t">Drawdown</div>', unsafe_allow_html=True)
        fig_dd = go.Figure()
        fig_dd.add_scatter(x=list(range(1,n+1)), y=drawdown, fill="tozeroy",
                           fillcolor="rgba(255,61,87,0.1)",
                           line=dict(color="#ff3d57", width=1.5), name="Drawdown")
        fig_dd.update_layout(**PLOTLY_THEME, height=240, xaxis_title="Trade #", yaxis_title="Drawdown ($)")
        st.plotly_chart(fig_dd, use_container_width=True)
    with c2:
        # P&L distribution
        st.markdown('<div class="sec-t">P&L Distribution</div>', unsafe_allow_html=True)
        fig_dist = go.Figure()
        fig_dist.add_histogram(x=pnl, nbinsx=20,
                               marker_color=["#00e676" if v>=0 else "#ff3d57" for v in pnl],
                               marker_line=dict(width=0.5, color="#06080c"))
        fig_dist.update_layout(**PLOTLY_THEME, height=240, xaxis_title="P&L ($)", yaxis_title="Frequency",
                               showlegend=False)
        st.plotly_chart(fig_dist, use_container_width=True)

    # Per-symbol breakdown if available
    if "symbol" in df.columns:
        st.markdown('<div class="sec-t">P&L by Symbol</div>', unsafe_allow_html=True)
        sym_stats = df.groupby("symbol")["pnl"].agg(["sum","mean","count"]).reset_index()
        sym_stats.columns = ["Symbol","Total P&L","Avg P&L","Trades"]
        sym_stats = sym_stats.sort_values("Total P&L", ascending=True)
        fig_sym = go.Figure(go.Bar(
            y=sym_stats["Symbol"], x=sym_stats["Total P&L"], orientation="h",
            marker_color=["#00e676" if v>=0 else "#ff3d57" for v in sym_stats["Total P&L"]],
            text=[f"${v:+,.0f}" for v in sym_stats["Total P&L"]], textposition="outside",
            textfont=dict(family="IBM Plex Mono", size=11)
        ))
        fig_sym.update_layout(**PLOTLY_THEME, height=max(240, len(sym_stats)*40),
                              showlegend=False, xaxis_title="Total P&L ($)")
        st.plotly_chart(fig_sym, use_container_width=True)
else:
    st.markdown('<div style="text-align:center;padding:3rem;color:#3a4a5e;font-family:IBM Plex Mono,monospace;font-size:0.75rem;border:1px dashed #1a2235;border-radius:12px;margin-top:1rem;">Upload a CSV or enable demo data to see your trade analytics.</div>', unsafe_allow_html=True)
