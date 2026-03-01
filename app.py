import streamlit as st
import sys, os

# Ensure local utils can be found
sys.path.insert(0, os.path.dirname(__file__))
from utils.styles import SHARED_CSS

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="11% — Trading Platform", page_icon="💲", layout="wide", initial_sidebar_state="collapsed")
st.markdown(SHARED_CSS, unsafe_allow_html=True)

# ── 1. SIMPLE PASSWORD PROTECTION ─────────────────────────────────────────────
def check_password():
    """Returns True if the user had the correct password."""
    def password_entered():
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show login UI
        st.markdown("""
        <div style="text-align:center; padding: 100px 0 20px 0;">
            <div style="font-family:'Bebas Neue',sans-serif; font-size:8rem; line-height:1;">
                <span style="color:#00d68f;">11</span><span style="color:#ff4757;">%</span>
            </div>
            <div style="font-family:'IBM Plex Mono',monospace; color:#4a5568; letter-spacing:0.2em; margin-bottom:2rem;">RESTRICTED ACCESS</div>
        </div>
        """, unsafe_allow_html=True)
        
        _, col_mid, _ = st.columns([2, 1, 2])
        with col_mid:
            st.text_input("Enter Platform Password", type="password", on_change=password_entered, key="password")
            if "password_correct" in st.session_state and not st.session_state["password_correct"]:
                st.error("😕 Password incorrect")
        return False
    return st.session_state["password_correct"]

if not check_password():
    st.stop() # Halt execution until password is correct

# ── 2. NAVBAR (ONLY ACCESSIBLE AFTER LOGIN) ───────────────────────────────────
st.markdown('<div class="nb"><div class="nb-brand"><span class="g">11</span><span class="r">%</span></div><div class="nb-links">', unsafe_allow_html=True)
_nav = st.columns([1,1,1,1,1,1])
with _nav[0]: st.page_link("app.py",                    label="Home")
with _nav[1]: st.page_link("pages/1_Backtest.py",       label="Backtest")
with _nav[2]: st.page_link("pages/2_Indicator_Test.py", label="Indicators")
with _nav[3]: st.page_link("pages/3_Replay.py",         label="Replay")
with _nav[4]: st.page_link("pages/4_Analysis.py",       label="Analysis")
with _nav[5]: st.page_link("pages/5_Assistant.py",      label="Assistant")
st.markdown('</div><div class="nb-tag">LIVE MARKET ACCESS</div></div>', unsafe_allow_html=True)

# ── 3. LIVE TICKER TAPE ────────────────────────────────────────────────────────
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

# ── 4. HERO SECTION ────────────────────────────────────────────────────────────
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
    for name, status, col in [("NYSE", "OPEN", "#00d68f"), ("NASDAQ", "OPEN", "#00d68f"), ("CME Futures", "OPEN", "#00d68f"), ("Crypto", "24/7", "#00d68f")]:
        st.markdown(f'<div style="display:flex;justify-content:space-between;padding:0.55rem 1rem;border-bottom:1px solid #1c2333;"><span style="font-family:IBM Plex Mono,monospace;font-size:0.72rem;color:#4a5568;">{name}</span><span style="font-family:IBM Plex Mono,monospace;font-size:0.72rem;color:{col};">● {status}</span></div>', unsafe_allow_html=True)
    st.markdown('</div></div>', unsafe_allow_html=True)

# ── 5. REST OF YOUR ORIGINAL APP (Feature cards, Strategies, etc.) ────────────
# [Paste the rest of your original feature cards and footer code here]
