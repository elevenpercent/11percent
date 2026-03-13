import streamlit as st, sys, os, yfinance as yf, pandas as pd
import plotly.graph_objects as go
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.styles import SHARED_CSS, PLOTLY_THEME; from utils.nav import navbar

st.set_page_config(page_title="Market Heatmap | 11%", layout="wide", initial_sidebar_state="collapsed")
st.markdown(SHARED_CSS, unsafe_allow_html=True)
st.markdown("""<style>
.ph{background:linear-gradient(135deg,#0c1018,#0d1420);border:1px solid #1a2235;border-radius:16px;padding:2.5rem 3rem;margin-bottom:2rem}
.ph-ey{font-family:'IBM Plex Mono',monospace;font-size:0.55rem;text-transform:uppercase;letter-spacing:0.3em;color:#3a4a5e;margin-bottom:0.5rem}
.ph h1{font-family:'Bebas Neue',sans-serif;font-size:3.5rem;letter-spacing:0.05em;line-height:1;margin:0 0 0.5rem 0}
.ph p{font-family:'IBM Plex Mono',monospace;font-size:0.75rem;color:#8896ab;line-height:1.8;margin:0}
.sec-t{font-family:'IBM Plex Mono',monospace;font-size:0.55rem;text-transform:uppercase;letter-spacing:0.25em;color:#3a4a5e;padding:1.2rem 0 0.8rem;border-top:1px solid #0d1117;display:flex;align-items:center;justify-content:space-between}
.sector-lbl{font-family:'Bebas Neue',sans-serif;font-size:1.4rem;letter-spacing:0.06em;margin:1.2rem 0 0.6rem}
.hm-cell{border-radius:8px;padding:0.75rem 0.5rem;text-align:center;cursor:default;transition:transform 0.15s,box-shadow 0.15s;font-family:'IBM Plex Mono',monospace}
.hm-cell:hover{transform:scale(1.05);box-shadow:0 6px 20px rgba(0,0,0,0.5)}
.hm-sym{font-size:0.68rem;font-weight:700;margin-bottom:0.2rem}
.hm-ret{font-size:0.65rem;font-weight:600}
</style>""", unsafe_allow_html=True)
navbar()

st.markdown("""<div class="ph"><div class="ph-ey">Market Overview</div><h1>Market Heatmap</h1><p>See performance across sectors and asset classes at a glance. Red means money is leaving, green means money is flowing in. Size up sectors before individual stock picks.</p></div>""", unsafe_allow_html=True)

SECTORS = {
    "Technology":   ["AAPL","MSFT","NVDA","AMD","GOOGL","META","TSLA","AVGO","ORCL","CRM"],
    "Finance":      ["JPM","BAC","WFC","GS","MS","V","MA","BLK","AXP","C"],
    "Energy":       ["XOM","CVX","COP","SLB","EOG","PSX","MPC","VLO","HAL","DVN"],
    "Healthcare":   ["JNJ","UNH","PFE","ABBV","MRK","LLY","BMY","AMGN","GILD","MDT"],
    "Consumer":     ["AMZN","WMT","COST","TGT","HD","LOW","NKE","MCD","SBUX","PG"],
    "Industrials":  ["GE","HON","UPS","CAT","DE","RTX","BA","LMT","EMR","NOC"],
}

@st.cache_data(ttl=900)
def fetch_returns(syms, period):
    rows = {}
    for s in syms:
        try:
            h = yf.Ticker(s).history(period=period)
            if len(h) >= 2:
                rows[s] = round((h["Close"].iloc[-1]/h["Close"].iloc[0]-1)*100, 2)
        except: pass
    return rows

def color_for(r):
    if r >= 5:    return "#00e676","#000"
    elif r >= 2:  return "#00b857","#000"
    elif r >= 0.5:return "#005a30","#cde8d4"
    elif r >= -0.5:return "#1a2235","#8896ab"
    elif r >= -2: return "#5a1010","#e8cdcd"
    elif r >= -5: return "#a01818","#fff"
    else:          return "#ff3d57","#000"

period_map = {"1d":"1 Day","5d":"5 Days","1mo":"1 Month","3mo":"3 Months","ytd":"Year to Date","1y":"1 Year"}
c1, c2 = st.columns([2,4])
with c1: selected_period = st.selectbox("Period", list(period_map.keys()), format_func=lambda x: period_map[x], index=2)
with c2: load_btn = st.button("Load Heatmap", type="primary")

if load_btn or "hm_data" not in st.session_state:
    with st.spinner("Fetching returns across 60+ stocks..."):
        all_syms = [s for sv in SECTORS.values() for s in sv]
        macro_syms = ["SPY","QQQ","IWM","GLD","TLT","BTC-USD","GC=F","DX-Y.NYB"]
        st.session_state["hm_data"] = fetch_returns(tuple(all_syms + macro_syms), selected_period)

if "hm_data" in st.session_state:
    ret_data = st.session_state["hm_data"]

    # Asset class snapshot at top
    st.markdown('<div class="sec-t">Asset Classes</div>', unsafe_allow_html=True)
    macro = {"SPY":"S&P 500","QQQ":"Nasdaq 100","IWM":"Small Cap","GLD":"Gold","TLT":"Long Bonds","BTC-USD":"Bitcoin","GC=F":"Crude Oil","DX-Y.NYB":"US Dollar"}
    macro_cols = st.columns(len(macro))
    for col, (sym, label) in zip(macro_cols, macro.items()):
        r = ret_data.get(sym, 0)
        bg, fg = color_for(r)
        col.markdown(f'<div style="background:{bg};color:{fg};border-radius:10px;padding:1rem 0.5rem;text-align:center;font-family:IBM Plex Mono,monospace;"><div style="font-size:0.6rem;font-weight:700;margin-bottom:0.3rem;">{label}</div><div style="font-size:0.82rem;font-weight:700;">{r:+.1f}%</div></div>', unsafe_allow_html=True)

    # Sector heatmaps
    for sector, syms in SECTORS.items():
        sector_rets = [ret_data.get(s,0) for s in syms if s in ret_data]
        avg_ret = sum(sector_rets)/len(sector_rets) if sector_rets else 0
        sc, _ = color_for(avg_ret)
        st.markdown(f'<div class="sector-lbl">{sector} <span style="font-family:IBM Plex Mono,monospace;font-size:0.7rem;color:{sc};">{avg_ret:+.1f}% avg</span></div>', unsafe_allow_html=True)
        cols = st.columns(len(syms))
        for col, s in zip(cols, syms):
            r = ret_data.get(s, 0)
            bg, fg = color_for(r)
            col.markdown(f'<div class="hm-cell" style="background:{bg};color:{fg};"><div class="hm-sym">{s}</div><div class="hm-ret">{r:+.1f}%</div></div>', unsafe_allow_html=True)
