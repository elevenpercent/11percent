import streamlit as st, sys, os, pandas as pd, yfinance as yf, numpy as np
import plotly.graph_objects as go
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.styles import SHARED_CSS, PLOTLY_THEME; from utils.nav import navbar

st.set_page_config(page_title="Screener | 11%", layout="wide", initial_sidebar_state="collapsed")
st.markdown(SHARED_CSS, unsafe_allow_html=True)
st.markdown("""<style>
.ph{background:linear-gradient(135deg,#0c1018,#0d1420);border:1px solid #1a2235;border-radius:16px;padding:2.5rem 3rem;margin-bottom:2rem}
.ph h1{font-family:"Bebas Neue",sans-serif;font-size:3.5rem;letter-spacing:0.05em;line-height:1;margin:0 0 0.5rem 0}
.ph p{font-family:"IBM Plex Mono",monospace;font-size:0.75rem;color:#8896ab;line-height:1.8;margin:0}
.ph-ey{font-family:"IBM Plex Mono",monospace;font-size:0.55rem;text-transform:uppercase;letter-spacing:0.3em;color:#3a4a5e;margin-bottom:0.5rem}
.sec-t{font-family:"IBM Plex Mono",monospace;font-size:0.55rem;text-transform:uppercase;letter-spacing:0.25em;color:#3a4a5e;padding:1.2rem 0 0.8rem;border-top:1px solid #0d1117}
.sc-row{display:grid;grid-template-columns:80px 1fr 90px 80px 90px 80px 80px;gap:8px;align-items:center;padding:0.85rem 1rem;border-bottom:1px solid #0d1117;font-family:"IBM Plex Mono",monospace;font-size:0.72rem;transition:background 0.12s}
.sc-row:hover{background:rgba(255,255,255,0.02)}
.sc-hdr{background:#0d1117;border-radius:6px 6px 0 0;font-size:0.52rem;text-transform:uppercase;letter-spacing:0.15em;color:#3a4a5e}
.pos{color:#00e676;font-weight:700}.neg{color:#ff3d57;font-weight:700}.neu{color:#8896ab}
</style>""", unsafe_allow_html=True)
navbar()

st.markdown("""<div class="ph"><div class="ph-ey">Stock Screener</div><h1>Screener</h1>
<p>Filter a curated watchlist by momentum, RSI, volume, and price change. Find the strongest setups in seconds.</p></div>""", unsafe_allow_html=True)

WATCHLIST = ["AAPL","MSFT","NVDA","GOOGL","META","AMZN","TSLA","AMD","AVGO","CRM",
             "JPM","GS","V","MA","BAC","XOM","CVX","UNH","JNJ","LLY","SPY","QQQ","IWM","GLD","TLT"]

st.markdown('<div class="sec-t">Filters</div>', unsafe_allow_html=True)
f1, f2, f3, f4 = st.columns(4)
with f1: rsi_min, rsi_max = st.slider("RSI Range", 0, 100, (0, 100))
with f2: chg_min = st.slider("Min 1-Month Return (%)", -50, 50, -50)
with f3: above_sma = st.checkbox("Price above 50-day SMA", value=False)
with f4: min_vol = st.number_input("Min Avg Volume (M)", value=0.0, step=0.5)

run_screen = st.button("Run Screener", type="primary")

@st.cache_data(ttl=600)
def screen_stock(sym):
    try:
        t = yf.Ticker(sym)
        h = t.history(period="6mo")
        if len(h) < 60: return None
        close = h["Close"]
        vol = h["Volume"]
        rsi_raw = None
        delta = close.diff()
        gain = delta.clip(lower=0).rolling(14).mean()
        loss = (-delta.clip(upper=0)).rolling(14).mean()
        rs = gain / loss
        rsi_raw = 100 - (100 / (1 + rs.iloc[-1]))
        sma50 = close.rolling(50).mean().iloc[-1]
        chg_1m = (close.iloc[-1] / close.iloc[-21] - 1) * 100
        avg_vol = vol.rolling(20).mean().iloc[-1] / 1e6
        info = t.fast_info
        market_cap = getattr(info, "market_cap", None)
        cap_str = ""
        if market_cap:
            if market_cap >= 1e12: cap_str = f"${market_cap/1e12:.1f}T"
            elif market_cap >= 1e9: cap_str = f"${market_cap/1e9:.0f}B"
            else: cap_str = f"${market_cap/1e6:.0f}M"
        return {
            "sym": sym, "price": close.iloc[-1], "rsi": rsi_raw,
            "chg_1m": chg_1m, "avg_vol": avg_vol,
            "above_sma50": close.iloc[-1] > sma50,
            "cap": cap_str
        }
    except: return None

if run_screen:
    with st.spinner("Scanning watchlist..."):
        results = []
        for sym in WATCHLIST:
            r = screen_stock(sym)
            if r: results.append(r)
        df = pd.DataFrame(results)
        if rsi_min > 0 or rsi_max < 100:
            df = df[(df["rsi"] >= rsi_min) & (df["rsi"] <= rsi_max)]
        if chg_min > -50:
            df = df[df["chg_1m"] >= chg_min]
        if above_sma:
            df = df[df["above_sma50"] == True]
        if min_vol > 0:
            df = df[df["avg_vol"] >= min_vol]
        df = df.sort_values("chg_1m", ascending=False)
        st.session_state["screen_results"] = df
        st.session_state["screen_count"] = len(df)

if "screen_results" in st.session_state:
    df = st.session_state["screen_results"]
    total = st.session_state.get("screen_count", len(df))
    st.markdown(f'<div style="font-family:IBM Plex Mono,monospace;font-size:0.72rem;color:#8896ab;margin:0.5rem 0 1rem;">{len(df)} stocks passed your filters out of {len(WATCHLIST)} screened.</div>', unsafe_allow_html=True)
    
    if not df.empty:
        fig = go.Figure(go.Bar(
            x=df["sym"], y=df["chg_1m"],
            marker_color=["#00e676" if v >= 0 else "#ff3d57" for v in df["chg_1m"]],
            text=[f"{v:+.1f}%" for v in df["chg_1m"]], textposition="outside",
            textfont=dict(family="IBM Plex Mono", size=11)
        ))
        fig.update_layout(**PLOTLY_THEME, height=280, title="1-Month Return by Stock",
                          showlegend=False, yaxis_title="Return (%)")
        st.plotly_chart(fig, use_container_width=True)

        st.markdown('<div class="sc-row sc-hdr"><span>Ticker</span><span>Market Cap</span><span>Price</span><span>RSI</span><span>1M Return</span><span>Avg Vol</span><span>50d SMA</span></div>', unsafe_allow_html=True)
        for _, r in df.iterrows():
            chg_c = "pos" if r["chg_1m"] >= 0 else "neg"
            rsi_c = "pos" if r["rsi"] < 40 else ("neg" if r["rsi"] > 70 else "neu")
            sma_txt = '<span style="color:#00e676">Above</span>' if r["above_sma50"] else '<span style="color:#ff3d57">Below</span>'
            st.markdown(f'''<div class="sc-row">
                <span style="font-weight:700;font-size:0.85rem;color:#eef2f7">{r["sym"]}</span>
                <span class="neu">{r["cap"]}</span>
                <span class="neu">${r["price"]:.2f}</span>
                <span class="{rsi_c}">{r["rsi"]:.0f}</span>
                <span class="{chg_c}">{r["chg_1m"]:+.1f}%</span>
                <span class="neu">{r["avg_vol"]:.1f}M</span>
                {sma_txt}
            </div>''', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.download_button("Download Results CSV", df.to_csv(index=False),
                          file_name="screen_results.csv", mime="text/csv")
    else:
        st.markdown('<div style="text-align:center;padding:3rem;color:#3a4a5e;font-family:IBM Plex Mono,monospace;font-size:0.75rem;border:1px dashed #1a2235;border-radius:12px;">No stocks matched your filters. Try wider ranges.</div>', unsafe_allow_html=True)
else:
    st.markdown('<div style="text-align:center;padding:4rem;color:#3a4a5e;font-family:IBM Plex Mono,monospace;font-size:0.75rem;border:1px dashed #1a2235;border-radius:12px;margin-top:1rem;">Set your filters above and click Run Screener.</div>', unsafe_allow_html=True)
