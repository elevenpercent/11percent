import streamlit as st, sys, os, pandas as pd, yfinance as yf
import plotly.graph_objects as go
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.styles import SHARED_CSS, PLOTLY_THEME; from utils.nav import navbar

st.set_page_config(page_title="Sector Rotation | 11%", layout="wide", initial_sidebar_state="collapsed")
st.markdown(SHARED_CSS, unsafe_allow_html=True)
st.markdown("""<style>
.ph{background:linear-gradient(135deg,#0c1018,#0d1420);border:1px solid #1a2235;border-radius:16px;padding:2.5rem 3rem;margin-bottom:2rem}
.ph-ey{font-family:'IBM Plex Mono',monospace;font-size:0.55rem;text-transform:uppercase;letter-spacing:0.3em;color:#3a4a5e;margin-bottom:0.5rem}
.ph h1{font-family:'Bebas Neue',sans-serif;font-size:3.5rem;letter-spacing:0.05em;line-height:1;margin:0 0 0.5rem 0}
.ph p{font-family:'IBM Plex Mono',monospace;font-size:0.75rem;color:#8896ab;line-height:1.8;margin:0}
.sec-t{font-family:'IBM Plex Mono',monospace;font-size:0.55rem;text-transform:uppercase;letter-spacing:0.25em;color:#3a4a5e;padding:1.2rem 0 0.8rem;border-top:1px solid #0d1117}
.rot-card{background:#0c1018;border:1px solid #1a2235;border-radius:12px;padding:1.2rem 1.5rem;margin-bottom:0.5rem;display:flex;align-items:center;justify-content:space-between;transition:border-color 0.2s}
.rot-card:hover{border-color:#2a3550}
.rot-sym{font-family:'Bebas Neue',sans-serif;font-size:1.6rem;letter-spacing:0.05em;min-width:60px}
.rot-name{font-family:'IBM Plex Mono',monospace;font-size:0.65rem;color:#8896ab;min-width:140px}
.rot-bar-wrap{flex:1;margin:0 1.5rem}
.cycle-card{background:#0c1018;border:1px solid #1a2235;border-radius:12px;padding:1.5rem;text-align:center}
.cycle-phase{font-family:'Bebas Neue',sans-serif;font-size:1.3rem;letter-spacing:0.06em;margin-bottom:0.4rem}
.cycle-etfs{font-family:'IBM Plex Mono',monospace;font-size:0.6rem;color:#8896ab;line-height:1.6}
</style>""", unsafe_allow_html=True)
navbar()

st.markdown("""<div class="ph"><div class="ph-ey">Macro & Cycles</div><h1>Sector Rotation</h1><p>Track money flow between sectors over multiple timeframes. Institutional capital rotates through sectors on a cycle — understanding that cycle is the backbone of top-down macro investing.</p></div>""", unsafe_allow_html=True)

SECTOR_ETFS = {
    "XLK":"Technology","XLF":"Financials","XLE":"Energy","XLV":"Healthcare",
    "XLY":"Consumer Disc.","XLP":"Consumer Staples","XLI":"Industrials",
    "XLB":"Materials","XLRE":"Real Estate","XLU":"Utilities","XLC":"Comm. Services"
}
PERIODS = {"1W":5,"1M":21,"3M":63,"6M":126,"1Y":252}

@st.cache_data(ttl=3600)
def get_sector_perf(tickers, periods):
    results = {}
    for sym in tickers:
        try:
            h = yf.Ticker(sym).history(period="1y")
            if h.empty: continue
            row = {}
            for label, days in periods.items():
                if len(h) > days:
                    row[label] = round((h["Close"].iloc[-1]/h["Close"].iloc[-days]-1)*100, 2)
            results[sym] = row
        except: pass
    return results

if st.button("Load Sector Data", type="primary") or "sec_data" not in st.session_state:
    with st.spinner("Loading 11 sector ETFs..."):
        st.session_state["sec_data"] = get_sector_perf(tuple(SECTOR_ETFS.keys()), PERIODS)

if "sec_data" in st.session_state:
    data = st.session_state["sec_data"]
    rows = []
    for sym, name in SECTOR_ETFS.items():
        if sym not in data: continue
        row = {"ETF":sym,"Sector":name}; row.update(data[sym]); rows.append(row)
    df = pd.DataFrame(rows)

    st.markdown('<div class="sec-t">Performance Across Timeframes</div>', unsafe_allow_html=True)

    # Heatmap via plotly
    wanted_cols = ["1W","1M","3M","6M","1Y"]
    available_cols = [c for c in wanted_cols if c in df.columns]
    if not available_cols:
        st.warning("No performance data. Try reloading."); st.stop()
    df_heat = df.set_index("Sector")[available_cols].fillna(0)
    fig_heat = go.Figure(go.Heatmap(
        z=df_heat.values,
        x=df_heat.columns.tolist(),
        y=df_heat.index.tolist(),
        colorscale=[[0,"#ff3d57"],[0.5,"#1a2235"],[1,"#00e676"]],
        zmid=0,
        text=[[f"{v:+.1f}%" for v in row] for row in df_heat.values],
        texttemplate="%{text}",
        textfont=dict(family="IBM Plex Mono", size=12, color="#eef2f7"),
        hovertemplate="<b>%{y}</b><br>%{x}: %{z:+.1f}%<extra></extra>",
        showscale=True,
        colorbar=dict(tickfont=dict(family="IBM Plex Mono",size=10,color="#8896ab"),
                     title=dict(text="Return %",font=dict(family="IBM Plex Mono",size=10,color="#8896ab")))
    ))
    theme_heat = {**PLOTLY_THEME, "margin": dict(l=130,r=80,t=20,b=30)}
    fig_heat.update_layout(**theme_heat, height=420)
    st.plotly_chart(fig_heat, use_container_width=True)

    # Bar chart for selected period
    c1, c2 = st.columns([1, 3])
    with c1:
        sel_period = st.selectbox("Period for ranking", available_cols, index=min(1, len(available_cols)-1))
    with c2:
        st.markdown("<br>", unsafe_allow_html=True)

    df_sorted = df[["Sector", sel_period]].dropna().sort_values(sel_period, ascending=True)
    fig_bar = go.Figure(go.Bar(
        y=df_sorted["Sector"], x=df_sorted[sel_period], orientation="h",
        marker_color=["#00e676" if v >= 0 else "#ff3d57" for v in df_sorted[sel_period]],
        text=[f"{v:+.1f}%" for v in df_sorted[sel_period]], textposition="outside",
        textfont=dict(family="IBM Plex Mono", size=12)
    ))
    fig_bar.update_layout(**PLOTLY_THEME, height=380, title=f"Sector Ranking — {sel_period}",
                          showlegend=False, xaxis_title="Return (%)")
    st.plotly_chart(fig_bar, use_container_width=True)

    # Cycle guide
    st.markdown('<div class="sec-t">Economic Cycle — Where to Be and When</div>', unsafe_allow_html=True)
    phases = [
        ("Early Expansion","#00e676","XLF · XLY · XLI — Financials, discretionary, and industrials lead as rates are low and credit is easy."),
        ("Mid Expansion","#4da6ff","XLK · XLC · XLI — Tech and growth sectors take over as earnings accelerate."),
        ("Late Expansion","#ffd166","XLE · XLB · XLRE — Commodities and materials rise as inflation picks up. Defensives start working."),
        ("Contraction","#ff3d57","XLP · XLU · XLV — Staples, utilities, and healthcare — the true defensives — outperform as the economy slows."),
    ]
    pc = st.columns(4)
    for col, (phase, color, desc) in zip(pc, phases):
        col.markdown(f'<div class="cycle-card"><div class="cycle-phase" style="color:{color}">{phase}</div><div class="cycle-etfs">{desc}</div></div>', unsafe_allow_html=True)
