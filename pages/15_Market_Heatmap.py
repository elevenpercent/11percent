import streamlit as st, sys, os, yfinance as yf, pandas as pd
import plotly.graph_objects as go
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.styles import SHARED_CSS, PLOTLY_THEME; from utils.nav import navbar

st.set_page_config(page_title="Market Heatmap | 11%", layout="wide", initial_sidebar_state="collapsed")
st.markdown(SHARED_CSS, unsafe_allow_html=True)
st.markdown("""<style>
.ph{background:linear-gradient(135deg,#0c1018,#0d1420);border:1px solid #1a2235;border-radius:16px;padding:2.5rem 3rem;margin-bottom:2rem}
.ph h1{font-family:'Bebas Neue',sans-serif;font-size:3.5rem;letter-spacing:0.05em;line-height:1;margin:0 0 0.5rem 0}
.ph p{font-family:'IBM Plex Mono',monospace;font-size:0.75rem;color:#8896ab;line-height:1.8;margin:0}
.ph-ey{font-family:'IBM Plex Mono',monospace;font-size:0.55rem;text-transform:uppercase;letter-spacing:0.3em;color:#3a4a5e;margin-bottom:0.5rem}
.sec-t{font-family:'IBM Plex Mono',monospace;font-size:0.55rem;text-transform:uppercase;letter-spacing:0.25em;color:#3a4a5e;padding:1.2rem 0 0.8rem;border-top:1px solid #0d1117}
.sector-lbl{font-family:'Bebas Neue',sans-serif;font-size:1.3rem;letter-spacing:0.05em;margin:1.2rem 0 0.5rem;display:flex;align-items:center;gap:0.8rem}
.hm-cell{border-radius:8px;padding:0.85rem 0.5rem;text-align:center;cursor:pointer;transition:transform 0.15s,box-shadow 0.15s;font-family:'IBM Plex Mono',monospace}
.hm-cell:hover{transform:scale(1.07);box-shadow:0 8px 24px rgba(0,0,0,0.6);z-index:10;position:relative}
.hm-sym{font-size:0.68rem;font-weight:700;margin-bottom:0.25rem}
.hm-ret{font-size:0.68rem;font-weight:700}
.hm-price{font-size:0.55rem;opacity:0.8;margin-top:0.15rem}
/* Fullscreen ticker display */
.fs-wrap{position:fixed;top:0;left:0;width:100vw;height:100vh;background:#06080c;z-index:99999;display:flex;flex-direction:column;align-items:center;justify-content:center}
.fs-sym{font-family:'Bebas Neue',sans-serif;font-size:8rem;letter-spacing:0.05em;line-height:1}
.fs-price{font-family:'Bebas Neue',sans-serif;font-size:10rem;letter-spacing:0.03em;line-height:1}
.fs-chg{font-family:'IBM Plex Mono',monospace;font-size:2.5rem;font-weight:700;margin-top:0.5rem}
.fs-meta{font-family:'IBM Plex Mono',monospace;font-size:0.9rem;color:#3a4a5e;margin-top:1rem;text-align:center}
.fs-exit{position:fixed;top:2rem;right:2rem;font-family:'IBM Plex Mono',monospace;font-size:0.7rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;background:#1a2235;color:#8896ab;border:1px solid #2a3550;border-radius:8px;padding:0.6rem 1.2rem;cursor:pointer;z-index:99999}
.fs-exit:hover{color:#eef2f7;border-color:#eef2f7}
/* Dashboard grid */
.dash-cell{background:#0c1018;border:1px solid #1a2235;border-radius:10px;padding:1rem;text-align:center;transition:border-color 0.2s,transform 0.15s}
.dash-cell:hover{border-color:#2a3550;transform:translateY(-2px)}
.dash-sym{font-family:'Bebas Neue',sans-serif;font-size:1.6rem;letter-spacing:0.05em;line-height:1}
.dash-price{font-family:'IBM Plex Mono',monospace;font-size:1.1rem;font-weight:700;margin-top:0.2rem}
.dash-chg{font-family:'IBM Plex Mono',monospace;font-size:0.75rem;font-weight:700;margin-top:0.1rem}
</style>""", unsafe_allow_html=True)
navbar()

SECTORS = {
    "Technology":  ["AAPL","MSFT","NVDA","AMD","GOOGL","META","TSLA","AVGO","ORCL","CRM"],
    "Finance":     ["JPM","BAC","WFC","GS","MS","V","MA","BLK","AXP","C"],
    "Energy":      ["XOM","CVX","COP","SLB","EOG","PSX","MPC","VLO","HAL","DVN"],
    "Healthcare":  ["JNJ","UNH","PFE","ABBV","MRK","LLY","BMY","AMGN","GILD","MDT"],
    "Consumer":    ["AMZN","WMT","COST","TGT","HD","LOW","NKE","MCD","SBUX","PG"],
    "Industrials": ["GE","HON","UPS","CAT","DE","RTX","BA","LMT","EMR","NOC"],
}
MACRO = {"SPY":"S&P 500","QQQ":"Nasdaq 100","IWM":"Small Cap","GLD":"Gold","TLT":"Long Bonds","BTC-USD":"Bitcoin","GC=F":"Crude Oil","DX-Y.NYB":"US Dollar"}

import pandas as _pd

@st.cache_data(ttl=120)  # 2 min cache for near-live intraday
def fetch_returns(syms, period):
    rows = {}
    for s in syms:
        try:
            if period == "1d":
                h = yf.Ticker(s).history(period="1d", interval="5m")
            else:
                h = yf.Ticker(s).history(period=period)
            if isinstance(h.columns, _pd.MultiIndex):
                h.columns = h.columns.get_level_values(0)
            if len(h) >= 2:
                current = round(float(h["Close"].iloc[-1]), 2)
                if period == "1d":
                    open_p = round(float(h["Open"].iloc[0]), 2)
                    ret    = round((current / open_p - 1) * 100, 2) if open_p else 0
                    rows[s] = {"ret": ret, "price": current, "open": open_p}
                else:
                    rows[s] = {
                        "ret":   round((h["Close"].iloc[-1]/h["Close"].iloc[0]-1)*100, 2),
                        "price": current, "open": None,
                    }
        except: pass
    return rows

def color_for(r):
    if r >= 5:     return "#00e676","#000"
    elif r >= 2:   return "#00b857","#000"
    elif r >= 0.5: return "#005a30","#cde8d4"
    elif r >= -0.5:return "#1a2235","#8896ab"
    elif r >= -2:  return "#5a1010","#e8cdcd"
    elif r >= -5:  return "#a01818","#fff"
    else:           return "#ff3d57","#000"

# ── Mode selector ─────────────────────────────────────────────────────────────
st.markdown("""<div class="ph"><div class="ph-ey">Market Overview</div><h1>Market Heatmap</h1>
<p>Live performance across sectors and stocks. Full-screen ticker mode for trading floor monitors. Custom dashboard to track exactly what you want.</p></div>""", unsafe_allow_html=True)

mode = st.radio("View Mode", ["Sector Heatmap", "Custom Dashboard", "Full-Screen Ticker"], horizontal=True)

# ── SECTOR HEATMAP ────────────────────────────────────────────────────────────
if mode == "Sector Heatmap":
    period_map = {"1d":"Today","5d":"5 Days","1mo":"1 Month","3mo":"3 Months","ytd":"Year to Date","1y":"1 Year"}
    c1, c2 = st.columns([2, 4])
    with c1: selected_period = st.selectbox("Period", list(period_map.keys()), format_func=lambda x: period_map[x], index=0)
    with c2: load_btn = st.button("Refresh Data", type="primary")

    if load_btn or "hm_data" not in st.session_state or st.session_state.get("hm_period") != selected_period:
        with st.spinner("Fetching live data..."):
            all_syms = [s for sv in SECTORS.values() for s in sv] + list(MACRO.keys())
            st.session_state["hm_data"]   = fetch_returns(tuple(all_syms), selected_period)
            st.session_state["hm_period"] = selected_period

    if "hm_data" in st.session_state:
        ret_data = st.session_state["hm_data"]

        # Asset classes
        st.markdown('<div class="sec-t">Asset Classes</div>', unsafe_allow_html=True)
        macro_cols = st.columns(len(MACRO))
        for col, (sym, label) in zip(macro_cols, MACRO.items()):
            d = ret_data.get(sym, {})
            r = d.get("ret", 0) if isinstance(d, dict) else 0
            p = d.get("price", 0) if isinstance(d, dict) else 0
            bg, fg = color_for(r)
            col.markdown(f'<div style="background:{bg};color:{fg};border-radius:10px;padding:1rem 0.5rem;text-align:center;font-family:IBM Plex Mono,monospace;"><div style="font-size:0.58rem;font-weight:700;margin-bottom:0.2rem;">{label}</div><div style="font-size:0.85rem;font-weight:700;">{r:+.1f}%</div><div style="font-size:0.55rem;opacity:0.8;">${p:,.2f}</div></div>', unsafe_allow_html=True)

        # Sectors
        for sector, syms in SECTORS.items():
            vals = [ret_data.get(s, {}).get("ret", 0) if isinstance(ret_data.get(s,{}), dict) else 0 for s in syms if s in ret_data]
            avg  = sum(vals)/len(vals) if vals else 0
            sc, _ = color_for(avg)
            st.markdown(f'<div class="sector-lbl">{sector}<span style="font-family:IBM Plex Mono,monospace;font-size:0.72rem;color:{sc};">{avg:+.1f}% avg</span></div>', unsafe_allow_html=True)
            cols = st.columns(len(syms))
            for col, s in zip(cols, syms):
                d  = ret_data.get(s, {})
                r  = d.get("ret", 0) if isinstance(d, dict) else 0
                p  = d.get("price", 0) if isinstance(d, dict) else 0
                bg, fg = color_for(r)
                col.markdown(f'<div class="hm-cell" style="background:{bg};color:{fg};"><div class="hm-sym">{s}</div><div class="hm-ret">{r:+.1f}%</div><div class="hm-price">${p:,.2f}</div></div>', unsafe_allow_html=True)

# ── CUSTOM DASHBOARD ──────────────────────────────────────────────────────────
elif mode == "Custom Dashboard":
    st.markdown('<div class="sec-t">Build Your Dashboard</div>', unsafe_allow_html=True)

    default_tickers = "AAPL, MSFT, NVDA, TSLA, SPY, QQQ, BTC-USD, GLD"
    ticker_input = st.text_area("Tickers (comma-separated)", value=default_tickers, height=80,
                                 help="Enter any tickers: stocks, ETFs, crypto, forex")
    cols_per_row = st.slider("Columns per row", 2, 8, 4)
    refresh_btn  = st.button("Load Dashboard", type="primary")

    if refresh_btn or "dash_data" not in st.session_state:
        raw_tickers = [t.strip().upper() for t in ticker_input.replace("\n",",").split(",") if t.strip()]
        if raw_tickers:
            with st.spinner(f"Fetching {len(raw_tickers)} tickers..."):
                data = fetch_returns(tuple(raw_tickers), "1d")
                st.session_state["dash_data"]    = data
                st.session_state["dash_tickers"] = raw_tickers

    if "dash_data" in st.session_state:
        data    = st.session_state["dash_data"]
        tickers = st.session_state.get("dash_tickers", [])
        rows    = [tickers[i:i+cols_per_row] for i in range(0, len(tickers), cols_per_row)]
        for row in rows:
            cols = st.columns(cols_per_row)
            for col, sym in zip(cols, row):
                d = data.get(sym, {})
                if not isinstance(d, dict): d = {}
                r = d.get("ret", 0); p = d.get("price", 0)
                bg, fg = color_for(r)
                chg_color = "#00e676" if r >= 0 else "#ff3d57"
                col.markdown(f"""
                <div class="dash-cell">
                    <div class="dash-sym" style="color:#eef2f7">{sym}</div>
                    <div class="dash-price" style="color:#eef2f7">${p:,.2f}</div>
                    <div class="dash-chg" style="color:{chg_color}">{r:+.2f}%</div>
                    <div style="height:6px;background:{bg};border-radius:3px;margin-top:0.5rem;width:100%"></div>
                </div>
                """, unsafe_allow_html=True)

# ── FULL-SCREEN TICKER ────────────────────────────────────────────────────────
elif mode == "Full-Screen Ticker":
    st.markdown('<div class="sec-t">Full-Screen Display — for trading monitors and desks</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-family:IBM Plex Mono,monospace;font-size:0.72rem;color:#8896ab;margin-bottom:1.2rem;line-height:1.8;">Enter a ticker and press Launch. The display fills your entire screen showing live price and % change. Press ESC or the exit button to return. Ideal for monitor setups in trading offices.</div>', unsafe_allow_html=True)

    fs_col1, fs_col2 = st.columns([2, 4])
    with fs_col1:
        fs_ticker = st.text_input("Ticker", value="SPY", placeholder="SPY, AAPL, BTC-USD").upper().strip()
    with fs_col2:
        st.markdown("<br>", unsafe_allow_html=True)
        launch_btn = st.button("Launch Full-Screen", type="primary")

    if launch_btn and fs_ticker:
        with st.spinner(f"Fetching {fs_ticker}..."):
            try:
                d = fetch_returns((fs_ticker,), "1d")
                info = d.get(fs_ticker, {})
                price  = info.get("price", 0)
                ret    = info.get("ret", 0)
                open_p = info.get("open", price)
                chg    = price - open_p if open_p else 0
                color  = "#00e676" if ret >= 0 else "#ff3d57"
                arrow  = "▲" if ret >= 0 else "▼"

                # Inject full-screen HTML overlay via components
                import streamlit.components.v1 as components
                html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=IBM+Plex+Mono:wght@400;700&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:#06080c;color:#eef2f7;font-family:'IBM Plex Mono',monospace;display:flex;flex-direction:column;align-items:center;justify-content:center;height:100vh;overflow:hidden}}
.sym{{font-family:'Bebas Neue',sans-serif;font-size:6vw;letter-spacing:0.05em;color:#3a4a5e;margin-bottom:0.5rem}}
.price{{font-family:'Bebas Neue',sans-serif;font-size:18vw;letter-spacing:0.02em;line-height:0.9;color:{color}}}
.chg{{font-family:'Bebas Neue',sans-serif;font-size:6vw;color:{color};margin-top:1rem}}
.meta{{font-size:1.5vw;color:#3a4a5e;margin-top:2rem;text-align:center;line-height:2}}
.exit-btn{{position:fixed;top:2vw;right:2vw;font-family:'IBM Plex Mono',monospace;font-size:1vw;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;background:#1a2235;color:#8896ab;border:1px solid #2a3550;border-radius:8px;padding:0.8vw 1.6vw;cursor:pointer}}
.exit-btn:hover{{color:#eef2f7;border-color:#eef2f7}}
.pulse{{animation:pulse 2s ease-in-out infinite}}
@keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:0.7}}}}
</style></head><body>
<button class="exit-btn" onclick="window.parent.postMessage('exit_fullscreen','*')">Press ESC to exit</button>
<div class="sym">{fs_ticker}</div>
<div class="price pulse">${price:,.2f}</div>
<div class="chg">{arrow} {abs(chg):.2f} &nbsp; ({ret:+.2f}%)</div>
<div class="meta">Open ${open_p:,.2f} &nbsp;·&nbsp; Today's change &nbsp;·&nbsp; Data delayed ~15 min</div>
<script>
document.addEventListener('keydown', function(e){{
  if(e.key==='Escape') window.parent.postMessage('exit_fullscreen','*');
}});
</script>
</body></html>"""
                components.html(html, height=700, scrolling=False)

            except Exception as e:
                st.error(f"Error loading {fs_ticker}: {e}")
    else:
        # Preview grid of common tickers
        st.markdown('<div class="sec-t">Common Tickers for Display</div>', unsafe_allow_html=True)
        suggestions = [["SPY","S&P 500 ETF"],["QQQ","Nasdaq 100"],["BTC-USD","Bitcoin"],["GLD","Gold"],["AAPL","Apple"],["NVDA","Nvidia"]]
        sg_cols = st.columns(6)
        for col, (sym, name) in zip(sg_cols, suggestions):
            col.markdown(f'<div style="background:#0c1018;border:1px solid #1a2235;border-radius:8px;padding:0.8rem;text-align:center;cursor:pointer;font-family:IBM Plex Mono,monospace"><div style="font-size:0.82rem;color:#eef2f7;font-weight:700">{sym}</div><div style="font-size:0.6rem;color:#3a4a5e;margin-top:0.2rem">{name}</div></div>', unsafe_allow_html=True)
