import streamlit as st
import sys, os
from datetime import datetime
import pytz
sys.path.insert(0, os.path.dirname(__file__))
from utils.styles import SHARED_CSS

st.set_page_config(page_title="11% — Trading Platform", page_icon="💲", layout="wide", initial_sidebar_state="collapsed")
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
st.markdown('<div class="nb" style="margin-top: 2rem;"><div class="nb-brand"><span class="g">11</span><span class="r">%</span></div><div class="nb-links">', unsafe_allow_html=True)
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
    candles = [(28,38,"#ff4757"),(32,44,"#00d68f"),(36,28,"#ff4757"),(40,52,"#00d68f"),
               (44,60,"#00d68f"),(38,30,"#ff4757"),(48,62,"#00d68f"),(52,70,"#00d68f"),
               (46,38,"#ff4757"),(56,72,"#00d68f"),(60,78,"#00d68f"),(54,46,"#ff4757"),
               (62,80,"#00d68f"),(58,74,"#00d68f"),(64,82,"#00d68f")]
    ch = '<div style="display:flex;align-items:flex-end;gap:3px;height:56px;margin-bottom:-0.2rem;opacity:0.45;">'
    for lo, hi, col in candles:
        bh = max(6, abs(hi-lo)*0.6)
        ch += f'<div style="width:11px;height:{bh}px;background:{col};border-radius:1px;"></div>'
    ch += '</div>'
    st.markdown(f"""
    <div style="padding:2.5rem 0 2rem 0;">
        {ch}
        <div style="font-family:'Bebas Neue',sans-serif;font-size:5.8rem;line-height:0.88;letter-spacing:0.02em;margin-bottom:1.4rem;">
            <span style="color:#00d68f;">BACK</span><br><span style="color:#ff4757;">TEST</span>
        </div>
        <p style="font-size:0.95rem;color:#8892a4;max-width:460px;line-height:1.8;margin:0 0 2rem 0;">
            A free trading platform built for learners. Test strategies against real data,
            study indicators, replay historical charts, and get AI-powered analysis.
        </p>
    </div>
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
    ("📊","Backtest",       "Test any strategy against years of real market data. Returns, drawdown, Sharpe, win rate, alpha.",        "pages/1_Backtest.py"),
    ("🔬","Indicators",     "Build custom strategies from 9+ indicators with AND/OR logic.",                                            "pages/2_Indicator_Test.py"),
    ("▶", "Replay",         "Step through historical bars one at a time. Practice reading price action without knowing what's next.",   "pages/3_Replay.py"),
    ("🧠","Analysis",       "Fundamentals, financials, valuation and AI-powered investment breakdown for any stock.",                   "pages/4_Analysis.py"),
    ("📅","Earnings",       "See how a stock reacted to every earnings report — day-of move, pre-run, and post follow-through.",        "pages/6_Earnings.py"),
    ("💬","AI Coach",       "Overwhelmed? Just ask. Plain English explanations of anything — strategies, results, concepts.",          "pages/5_Assistant.py"),
]
f_cols = st.columns(6)
for col, (icon, title, desc, link) in zip(f_cols, features):
    col.markdown(f'<div class="feat-card"><div class="feat-icon">{icon}</div><div class="feat-title">{title}</div><div class="feat-desc">{desc}</div></div>', unsafe_allow_html=True)
    col.page_link(link, label="Open →")

# ── Strategies & Indicators ────────────────────────────────────────────────────
st.markdown('<div class="divider" style="margin-top:2.5rem;">Strategies & Indicators</div>', unsafe_allow_html=True)
sl, sr = st.columns(2)

with sl:
    st.markdown('<div style="font-family:IBM Plex Mono,monospace;font-size:0.6rem;color:#3a4558;text-transform:uppercase;letter-spacing:0.15em;margin-bottom:0.8rem;">9 pre-built strategies</div>', unsafe_allow_html=True)
    for name, tag, desc in [
        ("SMA Crossover",         "Trend",      "Classic trend-following. Fast MA crosses above slow MA → buy."),
        ("EMA Crossover",         "Trend",      "Like SMA but reacts faster to recent price changes."),
        ("RSI",                   "Mean Rev.",  "Buys oversold conditions, sells overbought."),
        ("MACD",                  "Momentum",   "Momentum crossover using MACD and signal line."),
        ("Bollinger Bands",       "Mean Rev.",  "Buys lower band, sells upper band — mean reversion."),
        ("SuperTrend",            "Trend",      "ATR-based dynamic support/resistance with clear direction."),
        ("RSI + Bollinger Bands", "Combo",      "RSI confirms BB signals to reduce false entries."),
        ("EMA + RSI Filter",      "Combo",      "EMA crossover with RSI filter to improve signal quality."),
        ("MACD + SuperTrend",     "Combo",      "Dual confirmation: MACD momentum + SuperTrend direction."),
    ]:
        tc = "#4da6ff" if tag=="Trend" else ("#b388ff" if tag=="Mean Rev." else ("#ff9f43" if tag=="Momentum" else "#00d68f"))
        st.markdown(f'<div class="row-item"><span class="tag" style="background:{tc}18;color:{tc};border:1px solid {tc}30;flex-shrink:0;">{tag}</span><div><div style="font-size:0.8rem;color:#e2e8f0;">{name}</div><div style="font-size:0.72rem;color:#3a4558;margin-top:0.1rem;">{desc}</div></div></div>', unsafe_allow_html=True)

with sr:
    st.markdown('<div style="font-family:IBM Plex Mono,monospace;font-size:0.6rem;color:#3a4558;text-transform:uppercase;letter-spacing:0.15em;margin-bottom:0.8rem;">9+ available indicators</div>', unsafe_allow_html=True)
    for name, cat, desc in [
        ("SMA / EMA / WMA",    "Trend",      "Moving averages — trend direction and dynamic support."),
        ("RSI",                "Momentum",   "Relative Strength Index — momentum oscillator, 0–100."),
        ("Stochastic RSI",     "Momentum",   "RSI of RSI — faster, more sensitive signals."),
        ("MACD",               "Momentum",   "Trend + momentum via two EMA differences."),
        ("Bollinger Bands",    "Volatility", "Volatility bands — expand in trends, contract in ranges."),
        ("SuperTrend",         "Trend",      "ATR-based trend with clear buy/sell direction signal."),
        ("Ichimoku Cloud",     "Trend",      "Japanese system: trend, momentum, support/resistance."),
        ("VWAP",               "Volume",     "Volume Weighted Average Price — institutional benchmark."),
        ("OBV",                "Volume",     "On Balance Volume — tracks buying/selling pressure."),
    ]:
        tc = "#4da6ff" if cat=="Trend" else ("#b388ff" if cat=="Momentum" else ("#ff9f43" if cat=="Volatility" else "#00d68f"))
        st.markdown(f'<div class="row-item"><span class="tag" style="background:{tc}18;color:{tc};border:1px solid {tc}30;flex-shrink:0;">{cat}</span><div><div style="font-size:0.8rem;color:#e2e8f0;">{name}</div><div style="font-size:0.72rem;color:#3a4558;margin-top:0.1rem;">{desc}</div></div></div>', unsafe_allow_html=True)

# ── How it works ───────────────────────────────────────────────────────────────
st.markdown('<div class="divider" style="margin-top:2rem;">How it works</div>', unsafe_allow_html=True)
hw_cols = st.columns(5)
for col, num, title, desc in zip(hw_cols,
    ["01","02","03","04","05"],
    ["Pick a Stock","Choose a Strategy","Configure & Run","Read Results","Get AI Insight"],
    ["Enter any ticker — stocks, ETFs, or crypto. Data pulled live from Yahoo Finance.",
     "9 pre-built strategies or build your own with up to 3 indicators and custom conditions.",
     "Set date range, capital, and parameters. Results in seconds.",
     "Return, alpha, drawdown, Sharpe, win rate — and every individual trade.",
     "Open AI Coach to get your results explained in plain English."]):
    col.markdown(f'<div style="padding:1rem 0;"><div style="font-family:Bebas Neue,sans-serif;font-size:3rem;color:#1a2235;line-height:1;margin-bottom:0.4rem;">{num}</div><div style="font-family:IBM Plex Mono,monospace;font-size:0.68rem;color:#e2e8f0;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.35rem;">{title}</div><div style="font-size:0.8rem;color:#3a4558;line-height:1.65;">{desc}</div></div>', unsafe_allow_html=True)

# ── Concepts glossary ──────────────────────────────────────────────────────────
st.markdown('<div class="divider" style="margin-top:2rem;">Key Concepts</div>', unsafe_allow_html=True)
gl, gr = st.columns(2)
terms_l = [
    ("Backtesting",   "Running a strategy against historical data to see how it would have performed."),
    ("Drawdown",      "Peak-to-trough decline. Max drawdown = worst loss streak a strategy experienced."),
    ("Sharpe Ratio",  "Risk-adjusted return. Above 1.0 is decent, above 2.0 is strong."),
    ("Win Rate",      "% of trades that were profitable. High win rate ≠ profitable if losses are larger."),
    ("Alpha",         "Return above buy & hold. Positive alpha means the strategy added real value."),
]
terms_r = [
    ("Moving Average","Average of price over N periods. Smooths noise to show trend direction."),
    ("RSI",           "Momentum on a 0–100 scale. Below 30 = oversold, above 70 = overbought."),
    ("Support & Resistance","Price levels where buyers or sellers historically step in."),
    ("Volume",        "Shares traded. Rising price + rising volume confirms a move."),
    ("ATR",           "Average True Range — daily volatility. Used by SuperTrend and position sizing."),
]
with gl:
    for t, d in terms_l:
        gl.markdown(f'<div class="row-item"><div><div style="font-family:IBM Plex Mono,monospace;font-size:0.72rem;color:#00d68f;margin-bottom:0.2rem;">{t}</div><div style="font-size:0.8rem;color:#3a4558;line-height:1.65;">{d}</div></div></div>', unsafe_allow_html=True)
with gr:
    for t, d in terms_r:
        gr.markdown(f'<div class="row-item"><div><div style="font-family:IBM Plex Mono,monospace;font-size:0.72rem;color:#00d68f;margin-bottom:0.2rem;">{t}</div><div style="font-size:0.8rem;color:#3a4558;line-height:1.65;">{d}</div></div></div>', unsafe_allow_html=True)

# ── FAQ ────────────────────────────────────────────────────────────────────────
st.markdown('<div class="divider" style="margin-top:2rem;">FAQ</div>', unsafe_allow_html=True)
faqs = [
    ("Is this real trading or simulated?",             "Simulated. No real money involved. Data from Yahoo Finance. For education and strategy research only."),
    ("How accurate is the backtesting?",               "Indicative, not guaranteed. Assumes fills at closing price — no slippage, spread, commission, or tax. Real results differ."),
    ("Do I need to know how to code?",                 "No. Everything is point-and-click. It's built in Python with Streamlit — open source if you want to extend it."),
    ("Why does past performance not guarantee future?","Markets change. A strategy that worked in a bull market may fail in a bear market. Backtesting shows what happened, not what will happen."),
    ("How do I enable AI features?",                   "Add your Gemini API key to Streamlit Secrets as GEMINI_API_KEY. Free tier covers normal usage."),
]
fq1, fq2 = st.columns(2)
for i, (q, a) in enumerate(faqs):
    with (fq1 if i % 2 == 0 else fq2).expander(q):
        st.markdown(f'<div style="font-size:0.84rem;color:#8892a4;line-height:1.75;">{a}</div>', unsafe_allow_html=True)

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-top:3rem;padding:1.5rem 0;border-top:1px solid #1a2235;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:0.5rem;">
    <div style="font-family:'IBM Plex Mono',monospace;font-size:0.65rem;color:#3a4558;">
        <span style="color:#00d68f;font-family:'Bebas Neue',sans-serif;font-size:1.1rem;">11</span><span style="color:#ff4757;font-family:'Bebas Neue',sans-serif;font-size:1.1rem;">%</span>
        &nbsp;·&nbsp; Built by Rishi Gopinath &nbsp;·&nbsp; Free &nbsp;·&nbsp; Open Source
    </div>
    <div style="font-family:'IBM Plex Mono',monospace;font-size:0.6rem;color:#1a2235;">
        ⚠ Not financial advice · Educational use only · Past performance ≠ future results
    </div>
</div>
""", unsafe_allow_html=True)
