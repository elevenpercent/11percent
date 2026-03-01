import streamlit as st
import sys, os
from datetime import datetime
import pytz

# Setup path and styles
sys.path.insert(0, os.path.dirname(__file__))
from utils.styles import SHARED_CSS

st.set_page_config(page_title="11% — Trading Platform", page_icon="💲", layout="wide", initial_sidebar_state="collapsed")

# ── Header & Layout Fix ────────────────────────────────────────────────────────
# This CSS hides the Streamlit top bar and adds padding to the top of the app
st.markdown("""
    <style>
        [data-testid="stHeader"] {display: none;}
        .block-container {padding-top: 2rem !important;}
        .ticker-wrap {margin-top: 1rem;}
    </style>
""", unsafe_allow_html=True)
st.markdown(SHARED_CSS, unsafe_allow_html=True)

def get_market_status(market_name):
    now_utc = datetime.now(pytz.utc)
    tz_ny = pytz.timezone("America/New_York")
    time_ny = now_utc.astimezone(tz_ny)
    if market_name == "Crypto":
        return "24/7", "#00d68f"
    if time_ny.weekday() >= 5:
        return "Closed (WKND)", "#ff4757"
    start = time_ny.replace(hour=9, minute=30, second=0, microsecond=0)
    end   = time_ny.replace(hour=16, minute=0,  second=0, microsecond=0)
    if start <= time_ny <= end:
        return "Open", "#00d68f"
    return "Closed", "#ff4757"

# ── Navbar ─────────────────────────────────────────────────────────────────────
# Using a relative container to ensure it stays below the (now hidden) header area
st.markdown('<div class="nb" style="margin-top: 1rem; position: relative;"><div class="nb-brand"><span class="g">11</span><span class="r">%</span></div><div class="nb-links">', unsafe_allow_html=True)
_nav = st.columns([1,1,1,1,1,1,1])
with _nav[0]: st.page_link("app.py",                    label="Home")
with _nav[1]: st.page_link("pages/1_Backtest.py",       label="Backtest")
with _nav[2]: st.page_link("pages/2_Indicator_Test.py", label="Indicators")
with _nav[3]: st.page_link("pages/3_Replay.py",         label="Replay")
with _nav[4]: st.page_link("pages/4_Analysis.py",       label="Analysis")
with _nav[5]: st.page_link("pages/6_Earnings.py",       label="Earnings")
with _nav[6]: st.page_link("pages/5_Assistant.py",      label="Coach")
st.markdown('</div><div class="nb-tag">FREE · NO CARD REQUIRED</div></div>', unsafe_allow_html=True)

# ── Ticker tape ────────────────────────────────────────────────────────────────
TICKERS = ["AAPL","TSLA","SPY","NVDA","MSFT","AMZN","BTC-USD","META","GOOGL","AMD","NFLX","JPM","V","WMT","TSM"]
@st.cache_data(ttl=3600)
def get_tape(tickers):
    import yfinance as yf
    out = []
    for s in tickers:
        try:
            h = yf.Ticker(s).history(period="2d")
            if len(h) >= 2:
                p = float(h["Close"].iloc[-2]); c = float(h["Close"].iloc[-1])
                chg = ((c - p) / p) * 100; up = chg >= 0
                out.append((s, f"{c:,.2f}", f"{chg:+.2f}%", "▲" if up else "▼", "t-up" if up else "t-dn"))
        except: pass
    return out

tape = get_tape(tuple(TICKERS))
if tape:
    html = "".join(f'<span class="ticker-item"><span class="t-sym">{s}</span><span class="{c}">{p} {a} {ch}</span></span>' for s,p,ch,a,c in tape) * 2
    st.markdown(f'<div class="ticker-wrap"><div class="ticker-tape">{html}</div></div>', unsafe_allow_html=True)

# ── Hero ───────────────────────────────────────────────────────────────────────
left, right = st.columns([3, 2])

with left:
    # 1. Main Title FIRST
    st.markdown("""
    <div style="padding:2.5rem 0 1rem 0;">
        <div style="font-family:'Bebas Neue',sans-serif;font-size:5.8rem;line-height:0.88;letter-spacing:0.02em;margin-bottom:1.5rem;">
            <span style="color:#00d68f;">BACK</span><br><span style="color:#ff4757;">TEST</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 2. Candlesticks SECOND (Spaced out)
    candles = [(28,38,"#ff4757"),(32,44,"#00d68f"),(36,28,"#ff4757"),(40,52,"#00d68f"),
               (44,60,"#00d68f"),(38,30,"#ff4757"),(48,62,"#00d68f"),(52,70,"#00d68f"),
               (46,38,"#ff4757"),(56,72,"#00d68f"),(60,78,"#00d68f"),(54,46,"#ff4757"),
               (62,80,"#00d68f"),(58,74,"#00d68f"),(64,82,"#00d68f")]
    
    # Gap increased to 14px for more airiness
    ch = '<div style="display:flex;align-items:flex-end;gap:14px;height:45px;margin-bottom:2rem;opacity:0.5;">'
    for lo, hi, col in candles:
        bh = max(8, abs(hi-lo)*0.6)
        ch += f'<div style="width:7px;height:{bh}px;background:{col};border-radius:1px;"></div>'
    ch += '</div>'
    st.markdown(ch, unsafe_allow_html=True)

    # 3. Description
    st.markdown("""
        <p style="font-size:0.95rem;color:#8892a4;max-width:460px;line-height:1.8;margin:0 0 2rem 0;">
            A free trading platform built for learners. Test strategies against real data,
            study indicators, replay historical charts, and get AI-powered analysis.
        </p>
    """, unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1: st.page_link("pages/1_Backtest.py",  label="Start Backtesting →")
    with c2: st.page_link("pages/5_Assistant.py", label="Ask AI Coach →")

with right:
    # Stats + market status
    stats_html = '<div style="padding:2.5rem 0 1rem 0;">'
    stats_html += '<div style="display:grid;grid-template-columns:1fr 1fr;gap:1px;background:#1a2235;border-radius:10px;overflow:hidden;margin-bottom:1.2rem;">'
    for label, val in [("Strategies","9"),("Indicators","9+"),("Pages","6"),("Cost","$0")]:
        stats_html += f'<div style="background:#0d1117;padding:1.3rem;text-align:center;"><div style="font-family:Bebas Neue,sans-serif;font-size:2.2rem;color:#00d68f;line-height:1;">{val}</div><div style="font-family:IBM Plex Mono,monospace;font-size:0.55rem;color:#3a4558;text-transform:uppercase;letter-spacing:0.15em;margin-top:0.3rem;">{label}</div></div>'
    stats_html += '</div>'
    stats_html += '<div style="background:#0d1117;border:1px solid #1a2235;border-radius:10px;overflow:hidden;">'
    stats_html += '<div style="font-family:IBM Plex Mono,monospace;font-size:0.55rem;color:#3a4558;text-transform:uppercase;letter-spacing:0.18em;padding:0.9rem 1.2rem 0.5rem;">Market Status</div>'
    for market in ["NYSE","NASDAQ","CME Futures","Crypto"]:
        status, mcol = get_market_status(market)
        dot = "●" if status in ("OPEN","24/7") else "○"
        stats_html += f'<div style="display:flex;justify-content:space-between;align-items:center;padding:0.5rem 1.2rem;border-top:1px solid #1a2235;"><span style="font-family:IBM Plex Mono,monospace;font-size:0.72rem;color:#8892a4;">{market}</span><span style="font-family:IBM Plex Mono,monospace;font-size:0.68rem;color:{mcol};">{dot} {status}</span></div>'
    stats_html += '</div></div>'
    st.markdown(stats_html, unsafe_allow_html=True)

# ── Feature cards ──────────────────────────────────────────────────────────────
st.markdown('<div class="divider">What you can do</div>', unsafe_allow_html=True)

features = [
    ("📊","Backtest",       "Test any strategy against years of real market data.",        "pages/1_Backtest.py"),
    ("🔬","Indicators",     "Build custom strategies from 9+ indicators.",                  "pages/2_Indicator_Test.py"),
    ("▶", "Replay",          "Step through historical bars one at a time.",                "pages/3_Replay.py"),
    ("🧠","Analysis",        "Fundamentals and AI-powered investment breakdown.",           "pages/4_Analysis.py"),
    ("📅","Earnings",        "See how a stock reacted to every earnings report.",           "pages/6_Earnings.py"),
    ("💬","AI Coach",        "Ask questions in plain English.",                             "pages/5_Assistant.py"),
]
f_cols = st.columns(6)
for col, (icon, title, desc, link) in zip(f_cols, features):
    col.markdown(f'<div class="feat-card"><div class="feat-icon">{icon}</div><div class="feat-title">{title}</div><div class="feat-desc" style="font-size:0.75rem;">{desc}</div></div>', unsafe_allow_html=True)
    col.page_link(link, label="Open →")

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-top:5rem;padding:2rem 0;border-top:1px solid #1a2235;display:flex;justify-content:space-between;align-items:center;">
    <div style="font-family:'IBM Plex Mono',monospace;font-size:0.65rem;color:#3a4558;">
        <span style="color:#00d68f;font-family:'Bebas Neue',sans-serif;font-size:1.1rem;">11</span><span style="color:#ff4757;font-family:'Bebas Neue',sans-serif;font-size:1.1rem;">%</span>
        &nbsp;·&nbsp; Free &nbsp;·&nbsp; Open Source
    </div>
    <div style="font-family:'IBM Plex Mono',monospace;font-size:0.6rem;color:#1a2235;">
        ⚠ Not financial advice · Educational use only
    </div>
</div>
""", unsafe_allow_html=True)
