import streamlit as st
import sys, os
from datetime import datetime
import pytz

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))
try:
    from utils.styles import SHARED_CSS
except ImportError:
    SHARED_CSS = """<style>/* Fallback CSS if file missing */</style>"""

st.set_page_config(page_title="11% — Trading Platform", page_icon="💲", layout="wide", initial_sidebar_state="collapsed")
st.markdown(SHARED_CSS, unsafe_allow_html=True)

# ── Helper: Real-time Market Status ───────────────────────────────────────────
def get_market_status(market_name):
    """Returns (status_text, color) based on exchange hours."""
    now_utc = datetime.now(pytz.utc)
    
    # Timezone mapping
    tz_ny = pytz.timezone("America/New_York")
    time_ny = now_utc.astimezone(tz_ny)
    
    # Check for Crypto (24/7)
    if market_name == "Crypto":
        return "24/7", "#00d68f"
    
    # Check for Weekends
    if time_ny.weekday() >= 5: # 5=Sat, 6=Sun
        return "CLOSED (WKND)", "#ff4757"
    
    # Standard Market Hours (9:30 AM - 4:00 PM ET)
    start_time = time_ny.replace(hour=9, minute=30, second=0, microsecond=0)
    end_time = time_ny.replace(hour=16, minute=0, second=0, microsecond=0)
    
    if start_time <= time_ny <= end_time:
        return "OPEN", "#00d68f"
    else:
        return "CLOSED", "#ff4757"

# ── Navbar ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="nb"><div class="nb-brand"><span class="g">11</span><span class="r">%</span></div><div class="nb-links">', unsafe_allow_html=True)
_nav = st.columns([1,1,1,1,1,1])
with _nav[0]: st.page_link("app.py", label="Home")
with _nav[1]: st.page_link("pages/1_Backtest.py", label="Backtest")
with _nav[2]: st.page_link("pages/2_Indicator_Test.py", label="Indicators")
with _nav[3]: st.page_link("pages/3_Replay.py", label="Replay")
with _nav[4]: st.page_link("pages/4_Analysis.py", label="Analysis")
with _nav[5]: st.page_link("pages/5_Assistant.py", label="Assistant")
st.markdown('</div><div class="nb-tag">FREE · OPEN SOURCE</div></div>', unsafe_allow_html=True)

# ── Live ticker tape ───────────────────────────────────────────────────────────
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

# ── Hero section ───────────────────────────────────────────────────────────────
left, right = st.columns([3, 2])
with left:
    st.markdown("""
    <div style="padding:2.5rem 0 1.5rem 0;">
        <div style="font-family:'IBM Plex Mono',monospace;font-size:0.68rem;color:#00d68f;text-transform:uppercase;letter-spacing:0.25em;margin-bottom:1rem;">Free · Open Source · Educational</div>
        <div style="font-family:'Bebas Neue',sans-serif;font-size:5.5rem;line-height:0.9;letter-spacing:0.03em;">
            <span style="color:#00d68f;">BACK</span><br><span style="color:#ff4757;">TEST</span>
        </div>
        <p style="font-size:0.92rem;color:#4a5568;margin-top:1.3rem;max-width:500px;line-height:1.8;">
            A professional-grade trading platform built for everyone — from complete beginners to experienced traders.
            Backtest strategies against real market data, study indicators, replay historical charts bar by bar,
            and get AI-powered stock analysis. Completely free, forever.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Animated candle bar chart
    candles = [(28,38,"#ff4757"),(32,44,"#00d68f"),(36,28,"#ff4757"),(40,52,"#00d68f"),
               (44,60,"#00d68f"),(38,30,"#ff4757"),(48,62,"#00d68f"),(52,70,"#00d68f"),
               (46,38,"#ff4757"),(56,72,"#00d68f"),(60,78,"#00d68f"),(54,46,"#ff4757"),
               (62,80,"#00d68f"),(58,74,"#00d68f"),(64,82,"#00d68f")]
    ch = '<div style="display:flex;align-items:flex-end;gap:4px;height:80px;margin:1rem 0 2rem 0;">'
    for lo, hi, col in candles:
        bh = max(8, abs(hi-lo)*0.75); wt = abs(hi-lo)*0.18
        ch += f'<div style="width:14px;height:{bh}px;background:{col};border-radius:2px;position:relative;opacity:0.9;"><div style="width:2px;height:{wt}px;background:{col};position:absolute;left:50%;transform:translateX(-50%);bottom:100%;opacity:0.45;"></div></div>'
    st.markdown(ch + "</div>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1: st.page_link("pages/1_Backtest.py", label="Start Backtesting →")
    with c2: st.page_link("pages/5_Assistant.py", label="Ask AI Coach →")

with right:
    st.markdown("""
    <div style="padding:2.5rem 0 1rem 0;">
        <div style="font-family:'IBM Plex Mono',monospace;font-size:0.58rem;color:#3a4558;text-transform:uppercase;letter-spacing:0.18em;margin-bottom:0.8rem;">Platform at a Glance</div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:1px;background:#1c2333;border-radius:4px;overflow:hidden;margin-bottom:1.5rem;">
            <div style="background:#0d1117;padding:1.2rem;text-align:center;"><div style="font-family:'IBM Plex Mono',monospace;font-size:0.58rem;color:#3a4558;text-transform:uppercase;margin-bottom:0.5rem;">Strategies</div><div style="font-family:'Bebas Neue',sans-serif;font-size:2rem;color:#00d68f;">9</div></div>
            <div style="background:#0d1117;padding:1.2rem;text-align:center;"><div style="font-family:'IBM Plex Mono',monospace;font-size:0.58rem;color:#3a4558;text-transform:uppercase;margin-bottom:0.5rem;">Indicators</div><div style="font-family:'Bebas Neue',sans-serif;font-size:2rem;color:#00d68f;">9+</div></div>
            <div style="background:#0d1117;padding:1.2rem;text-align:center;"><div style="font-family:'IBM Plex Mono',monospace;font-size:0.58rem;color:#3a4558;text-transform:uppercase;margin-bottom:0.5rem;">Cost</div><div style="font-family:'Bebas Neue',sans-serif;font-size:2rem;color:#00d68f;">$0</div></div>
            <div style="background:#0d1117;padding:1.2rem;text-align:center;"><div style="font-family:'IBM Plex Mono',monospace;font-size:0.58rem;color:#3a4558;text-transform:uppercase;margin-bottom:0.5rem;">Pages</div><div style="font-family:'Bebas Neue',sans-serif;font-size:2rem;color:#00d68f;">5</div></div>
        </div>
        <div style="font-family:'IBM Plex Mono',monospace;font-size:0.58rem;color:#3a4558;text-transform:uppercase;letter-spacing:0.18em;margin-bottom:0.6rem;">Market Status</div>
        <div style="background:#0d1117;border:1px solid #1c2333;border-radius:4px;overflow:hidden;">
    """, unsafe_allow_html=True)
    
    # Accurate Dynamic Markets
    for m_name in ["NYSE", "NASDAQ", "CME Futures", "Crypto"]:
        status, color = get_market_status(m_name)
        st.markdown(f'<div style="display:flex;justify-content:space-between;padding:0.55rem 1rem;border-bottom:1px solid #1c2333;"><span style="font-family:IBM Plex Mono,monospace;font-size:0.72rem;color:#4a5568;">{m_name}</span><span style="font-family:IBM Plex Mono,monospace;font-size:0.72rem;color:{color};">● {status}</span></div>', unsafe_allow_html=True)
    st.markdown('</div></div>', unsafe_allow_html=True)

# ── Feature cards ──────────────────────────────────────────────────────────────
st.markdown('<div class="price-divider">WHAT YOU CAN DO</div>', unsafe_allow_html=True)

features = [
    ("Backtest", "#00d68f", "Test any strategy against years of real market data. See exactly how it would have performed — returns, drawdown, win rate, Sharpe ratio, and more.", "pages/1_Backtest.py", "Open Backtest →"),
    ("Indicator Test", "#00d68f", "Build custom strategies from scratch using up to 3 indicators combined with AND/OR logic. Set your own buy and sell conditions.", "pages/2_Indicator_Test.py", "Open Indicator Test →"),
    ("Chart Replay", "#ff4757", "Step through historical candles bar by bar with a professional chart powered by TradingView. Practice reading price action.", "pages/3_Replay.py", "Open Replay →"),
    ("AI Analysis", "#00d68f", "Get a full fundamental breakdown of any stock — financials, valuation, and growth — powered by Gemini AI.", "pages/4_Analysis.py", "Open Analysis →"),
    ("AI Assistant", "#00d68f", "Ask anything. Your personal trading coach explains strategy results, teaches concepts, and gives personalised advice.", "pages/5_Assistant.py", "Open Assistant →"),
]

cols = st.columns(5)
for col, (title, accent, desc, link, cta) in zip(cols, features):
    col.markdown(f"""
    <div style="background:#0d1117;border:1px solid #1c2333;border-radius:6px;padding:1.4rem;height:100%;border-top:2px solid {accent};">
        <div style="font-family:'IBM Plex Mono',monospace;font-size:0.65rem;font-weight:700;color:{accent};text-transform:uppercase;letter-spacing:0.15em;margin-bottom:0.8rem;">{title}</div>
        <div style="font-size:0.82rem;color:#4a5568;line-height:1.7;margin-bottom:1.2rem;">{desc}</div>
    </div>
    """, unsafe_allow_html=True)
    col.page_link(link, label=cta)

# ── Strategies & Indicators ────────────────────────────────────────────────────
st.markdown('<div class="price-divider">STRATEGIES & INDICATORS</div>', unsafe_allow_html=True)
s_left, s_right = st.columns(2)

with s_left:
    st.markdown('<div style="font-family:IBM Plex Mono,monospace;font-size:0.58rem;color:#3a4558;text-transform:uppercase;letter-spacing:0.18em;margin-bottom:0.8rem;">Built-in Strategies</div>', unsafe_allow_html=True)
    strategies = [("SMA Crossover", "Fast MA crosses above slow MA."), ("RSI", "Buys oversold, sells overbought."), ("Bollinger Bands", "Buys at lower band, sells at upper.")]
    for name, desc in strategies:
        st.markdown(f'<div style="padding:0.65rem 0;border-bottom:1px solid #1c2333;"><div style="font-family:IBM Plex Mono,monospace;font-size:0.75rem;color:#cdd5e0;margin-bottom:0.2rem;"><span style="color:#00d68f;margin-right:0.5rem;">—</span>{name}</div><div style="font-size:0.77rem;color:#3a4558;padding-left:1rem;">{desc}</div></div>', unsafe_allow_html=True)

with s_right:
    st.markdown('<div style="font-family:IBM Plex Mono,monospace;font-size:0.58rem;color:#3a4558;text-transform:uppercase;letter-spacing:0.18em;margin-bottom:0.8rem;">Available Indicators</div>', unsafe_allow_html=True)
    indicators = [("SMA / EMA / WMA", "Trend direction averages."), ("MACD", "Momentum convergence/divergence."), ("VWAP", "Volume weighted benchmark.")]
    for name, desc in indicators:
        st.markdown(f'<div style="padding:0.65rem 0;border-bottom:1px solid #1c2333;"><div style="font-family:IBM Plex Mono,monospace;font-size:0.75rem;color:#cdd5e0;margin-bottom:0.2rem;"><span style="color:#00d68f;margin-right:0.5rem;">—</span>{name}</div><div style="font-size:0.77rem;color:#3a4558;padding-left:1rem;">{desc}</div></div>', unsafe_allow_html=True)

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-top:3rem;padding:1.5rem 0;border-top:1px solid #1c2333;display:flex;justify-content:space-between;align-items:center;">
    <div style="font-family:'IBM Plex Mono',monospace;font-size:0.65rem;color:#3a4558;">
        <span style="color:#00d68f;font-family:'Bebas Neue',sans-serif;font-size:1rem;">11</span><span style="color:#ff4757;font-family:'Bebas Neue',sans-serif;font-size:1rem;">%</span>
        &nbsp;·&nbsp; Built by Rishi Gopinath &nbsp;·&nbsp; Open Source
    </div>
    <div style="font-family:'IBM Plex Mono',monospace;font-size:0.62rem;color:#1c2333;">
        ⚠ Educational use only. Not financial advice.
    </div>
</div>
""", unsafe_allow_html=True)
