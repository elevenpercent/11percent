import streamlit as st
import sys, os
sys.path.append(os.path.dirname(__file__))

from utils.styles import SHARED_CSS, LOGO_IMG
from utils.nav import navbar

st.set_page_config(page_title="11% | Free Trading Education", layout="wide", initial_sidebar_state="collapsed")
st.markdown(SHARED_CSS, unsafe_allow_html=True)
navbar()

# ── Extra home-page CSS
st.markdown("""
<style>
@keyframes fadeUp { from{opacity:0;transform:translateY(24px)} to{opacity:1;transform:translateY(0)} }
@keyframes pulse  { 0%,100%{opacity:1} 50%{opacity:0.5} }
@keyframes marquee{ from{transform:translateX(0)} to{transform:translateX(-50%)} }

.hero { padding:4.5rem 0 3.5rem; border-bottom:1px solid #1a2235; }
.hero-eyebrow {
    display:inline-flex; align-items:center; gap:0.5rem;
    background:rgba(0,230,118,0.08); border:1px solid rgba(0,230,118,0.2);
    border-radius:20px; padding:0.3rem 0.9rem;
    font-family:'IBM Plex Mono',monospace; font-size:0.58rem;
    font-weight:600; text-transform:uppercase; letter-spacing:0.16em;
    color:#00e676; margin-bottom:1.5rem;
}
.hero-eyebrow-dot { width:6px;height:6px;border-radius:50%;background:#00e676;animation:pulse 1.5s infinite; }
.hero h1 {
    font-family:'Bebas Neue',sans-serif;
    font-size:clamp(3.5rem,8vw,7rem);
    letter-spacing:0.03em; line-height:0.95;
    color:#eef2f7; margin:0 0 1.2rem;
}
.hero h1 em { color:#00e676; font-style:normal; }
.hero-sub {
    font-size:1.05rem; color:#8896ab; max-width:520px;
    line-height:1.7; margin-bottom:2rem;
}
.hero-cta { display:flex; align-items:center; gap:1rem; flex-wrap:wrap; }
.cta-primary {
    display:inline-flex; align-items:center; gap:0.5rem;
    background:linear-gradient(135deg,#007a2c,#00e676);
    color:#000; font-family:'IBM Plex Mono',monospace;
    font-size:0.7rem; font-weight:700; text-transform:uppercase;
    letter-spacing:0.14em; padding:0.7rem 1.6rem;
    border-radius:6px; text-decoration:none; transition:opacity 0.15s;
}
.cta-primary:hover { opacity:0.85; }
.cta-secondary {
    display:inline-flex; align-items:center; gap:0.4rem;
    background:transparent; border:1px solid #1a2235; color:#8896ab;
    font-family:'IBM Plex Mono',monospace; font-size:0.7rem;
    font-weight:600; text-transform:uppercase; letter-spacing:0.14em;
    padding:0.7rem 1.4rem; border-radius:6px; text-decoration:none;
    transition:all 0.15s;
}
.cta-secondary:hover { border-color:#4da6ff; color:#4da6ff; }
.hero-stats { display:flex; gap:2.5rem; margin-top:2.5rem; }
.hs { }
.hs-val { font-family:'Bebas Neue',sans-serif; font-size:2.2rem; color:#eef2f7; line-height:1; }
.hs-lbl { font-family:'IBM Plex Mono',monospace; font-size:0.52rem; text-transform:uppercase; letter-spacing:0.18em; color:#3a4a5e; margin-top:0.15rem; }

/* Ticker tape */
.tape-outer { overflow:hidden; border-top:1px solid #1a2235; border-bottom:1px solid #1a2235; background:#030508; padding:0.5rem 0; margin:0 -2.5rem; }
.tape-inner { display:flex; animation:marquee 35s linear infinite; white-space:nowrap; width:max-content; }
.tape-grp   { display:flex; }
.tape-item  { display:flex; align-items:center; gap:0.4rem; padding:0 1.5rem; border-right:1px solid #0f1621; font-family:'IBM Plex Mono',monospace; font-size:0.7rem; }
.tape-sym   { color:#3a4a5e; font-weight:600; }
.tape-price { color:#eef2f7; }
.tape-chg.u { color:#00e676; } .tape-chg.d { color:#ff3d57; }

/* Feature cards */
.feat-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:1rem; margin:2.5rem 0; }
.feat-card {
    background:#0c1018; border:1px solid #1a2235;
    border-radius:12px; padding:1.5rem;
    transition:border-color 0.2s, transform 0.2s;
    cursor:default; position:relative; overflow:hidden;
}
.feat-card:hover { border-color:#2a3550; transform:translateY(-2px); }
.feat-card::before {
    content:''; position:absolute; top:0; left:0; right:0; height:2px;
    background:var(--accent,#00e676); opacity:0;
    transition:opacity 0.2s;
}
.feat-card:hover::before { opacity:1; }
.feat-icon {
    width:40px; height:40px; border-radius:10px;
    display:flex; align-items:center; justify-content:center;
    font-size:1.2rem; margin-bottom:1rem;
}
.feat-title { font-family:'IBM Plex Mono',monospace; font-size:0.7rem; font-weight:700; text-transform:uppercase; letter-spacing:0.14em; color:#eef2f7; margin-bottom:0.5rem; }
.feat-desc  { font-size:0.82rem; color:#8896ab; line-height:1.6; }
.feat-link  { display:inline-flex; align-items:center; gap:0.3rem; margin-top:0.9rem; font-family:'IBM Plex Mono',monospace; font-size:0.58rem; font-weight:600; text-transform:uppercase; letter-spacing:0.12em; color:#3a4a5e; text-decoration:none; transition:color 0.12s; }
.feat-link:hover { color:var(--accent,#00e676); }

/* Market data section */
.mkt-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:0.8rem; margin-bottom:2rem; }
.mkt-card { background:#0c1018; border:1px solid #1a2235; border-radius:8px; padding:1rem 1.2rem; }
.mkt-sym  { font-family:'IBM Plex Mono',monospace; font-size:0.62rem; font-weight:700; text-transform:uppercase; letter-spacing:0.12em; color:#3a4a5e; margin-bottom:0.3rem; }
.mkt-val  { font-size:1.15rem; font-weight:700; color:#eef2f7; }
.mkt-chg  { font-family:'IBM Plex Mono',monospace; font-size:0.65rem; margin-top:0.15rem; }
.mkt-chg.u { color:#00e676; } .mkt-chg.d { color:#ff3d57; }

/* Learn section */
.learn-grid { display:grid; grid-template-columns:repeat(2,1fr); gap:1rem; margin-bottom:2rem; }
.learn-card { background:#0c1018; border:1px solid #1a2235; border-radius:10px; padding:1.2rem 1.4rem; display:flex; gap:1rem; align-items:flex-start; transition:border-color 0.15s; }
.learn-card:hover { border-color:#2a3550; }
.learn-num  { font-family:'Bebas Neue',sans-serif; font-size:2rem; color:#1a2235; line-height:1; min-width:2.5rem; }
.learn-title { font-size:0.85rem; font-weight:600; color:#eef2f7; margin-bottom:0.3rem; }
.learn-desc  { font-size:0.78rem; color:#8896ab; line-height:1.55; }

/* Indicator pills */
.ind-grid { display:flex; flex-wrap:wrap; gap:0.5rem; margin-bottom:2rem; }
.ind-pill {
    background:#0c1018; border:1px solid #1a2235;
    border-radius:20px; padding:0.3rem 0.9rem;
    font-family:'IBM Plex Mono',monospace; font-size:0.6rem;
    font-weight:600; text-transform:uppercase; letter-spacing:0.1em;
    color:#3a4a5e;
    transition:border-color 0.15s, color 0.15s;
}
.ind-pill:hover { border-color:#b388ff; color:#b388ff; }

/* Section titles */
.sh2 { font-family:'Bebas Neue',sans-serif; font-size:2rem; letter-spacing:0.04em; color:#eef2f7; margin:0 0 0.3rem; }
.sh2-sub { font-size:0.85rem; color:#8896ab; margin-bottom:1.5rem; }

/* Strategy rows */
.strat-row { display:flex; align-items:center; justify-content:space-between; padding:0.7rem 0; border-bottom:1px solid #0d1117; }
.strat-row:last-child { border-bottom:none; }
.strat-name { font-size:0.85rem; color:#eef2f7; font-weight:500; }
.strat-tag  { font-family:'IBM Plex Mono',monospace; font-size:0.56rem; text-transform:uppercase; letter-spacing:0.12em; padding:2px 8px; border-radius:3px; }

/* FAQ */
.faq-item { border-bottom:1px solid #0d1117; padding:1rem 0; }
.faq-item:last-child { border-bottom:none; }
.faq-q { font-size:0.88rem; font-weight:600; color:#eef2f7; margin-bottom:0.4rem; }
.faq-a { font-size:0.82rem; color:#8896ab; line-height:1.65; }
</style>
""", unsafe_allow_html=True)

# ── HERO
st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">
        <span class="hero-eyebrow-dot"></span>
        Free · Open Source · No Ads
    </div>
    <h1>LEARN TO <em>TRADE</em><br>LIKE A PRO</h1>
    <div class="hero-sub">
        11% is a free trading education platform with a live market simulator, AI-powered analysis, and strategy backtesting — built for serious learners.
    </div>
    <div class="hero-cta">
        <a href="/Replay" class="cta-primary">&#9654; Start Replay Simulator</a>
        <a href="/Strategy_Lab" class="cta-secondary">&#9654; Test a Strategy</a>
        <a href="/Analysis" class="cta-secondary">&#9670; Analyze a Stock</a>
    </div>
    <div class="hero-stats">
        <div class="hs"><div class="hs-val">15+</div><div class="hs-lbl">Indicators</div></div>
        <div class="hs"><div class="hs-val">9</div><div class="hs-lbl">Prebuilt Strategies</div></div>
        <div class="hs"><div class="hs-val">∞</div><div class="hs-lbl">Custom Signals</div></div>
        <div class="hs"><div class="hs-val">Free</div><div class="hs-lbl">Always</div></div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Ticker tape
TAPE_ITEMS = [
    ("SPY","$568.42","+0.34%",True), ("QQQ","$481.18","+0.51%",True),
    ("AAPL","$223.45","+1.12%",True), ("TSLA","$187.32","-2.14%",False),
    ("NVDA","$892.18","+3.21%",True), ("MSFT","$415.67","+0.44%",True),
    ("AMZN","$198.23","-0.88%",False), ("META","$523.11","+1.66%",True),
    ("GOOGL","$172.89","+0.23%",True), ("AMD","$152.44","-1.03%",False),
    ("BTC","$87,420","+2.8%",True), ("GOLD","$2,847","+0.4%",True),
]
tape_html = "".join(f'<div class="tape-item"><span class="tape-sym">{s}</span><span class="tape-price">{p}</span><span class="tape-chg {"u" if u else "d"}">{c}</span></div>' for s,p,c,u in TAPE_ITEMS)
st.markdown(f'<div class="tape-outer"><div class="tape-inner"><div class="tape-grp">{tape_html}</div><div class="tape-grp">{tape_html}</div></div></div>', unsafe_allow_html=True)

# ── FEATURES
st.markdown("""
<div style="margin-top:3rem;">
<div class="sh2">EVERYTHING YOU NEED</div>
<div class="sh2-sub">8 powerful tools — all free, all in one place.</div>
<div class="feat-grid">
    <div class="feat-card" style="--accent:#00e676;">
        <div class="feat-icon" style="background:rgba(0,230,118,0.1);">🎮</div>
        <div class="feat-title">Market Replay</div>
        <div class="feat-desc">Practice on real historical data, bar-by-bar. Buy, sell, draw trendlines — without knowing the future. The closest thing to live trading without real money.</div>
        <a class="feat-link" href="/Replay">Open Simulator →</a>
    </div>
    <div class="feat-card" style="--accent:#4da6ff;">
        <div class="feat-icon" style="background:rgba(77,166,255,0.1);">⚗️</div>
        <div class="feat-title">Strategy Lab</div>
        <div class="feat-desc">Backtest 9 prebuilt strategies or build your own custom signal from any combination of indicators. See real P&L, drawdown, Sharpe, and win rate.</div>
        <a class="feat-link" href="/Strategy_Lab">Open Lab →</a>
    </div>
    <div class="feat-card" style="--accent:#b388ff;">
        <div class="feat-icon" style="background:rgba(179,136,255,0.1);">🤖</div>
        <div class="feat-title">AI Coach</div>
        <div class="feat-desc">Ask your Gemini-powered trading mentor anything — chart patterns, risk management, strategy review, or a plain-English explanation of any concept.</div>
        <a class="feat-link" href="/Assistant">Open Coach →</a>
    </div>
    <div class="feat-card" style="--accent:#ffd166;">
        <div class="feat-icon" style="background:rgba(255,209,102,0.1);">🔍</div>
        <div class="feat-title">Stock Analysis</div>
        <div class="feat-desc">Full fundamentals, 1-year chart, recent news, and a structured AI deep-dive for any ticker — bull case, bear case, technical picture, and bottom line.</div>
        <a class="feat-link" href="/Analysis">Analyze a Stock →</a>
    </div>
    <div class="feat-card" style="--accent:#ff9f43;">
        <div class="feat-icon" style="background:rgba(255,159,67,0.1);">🐋</div>
        <div class="feat-title">Whale Tracker</div>
        <div class="feat-desc">Detect statistically anomalous volume spikes across any watchlist. Institutional activity often precedes big moves — see it before it's obvious.</div>
        <a class="feat-link" href="/Whale_Tracker">Track Whales →</a>
    </div>
    <div class="feat-card" style="--accent:#ff3d57;">
        <div class="feat-icon" style="background:rgba(255,61,87,0.1);">🎲</div>
        <div class="feat-title">Monte Carlo</div>
        <div class="feat-desc">Run 1,000 GBM price simulations to see the range of possible outcomes for any stock. Visualize risk with probability cones and percentile bands.</div>
        <a class="feat-link" href="/Monte_Carlo">Run Simulation →</a>
    </div>
</div>
</div>
""", unsafe_allow_html=True)

# ── TWO-COLUMN: Indicators + Strategies
col_ind, col_strat = st.columns(2)

with col_ind:
    st.markdown('<div class="sh2">INDICATORS</div><div class="sh2-sub">15 built-in, all configurable.</div>', unsafe_allow_html=True)
    INDICATORS = [
        ("SMA","Trend"),("EMA","Trend"),("WMA","Trend"),("Hull MA","Trend"),
        ("RSI","Momentum"),("Stoch RSI","Momentum"),("MACD","Momentum"),
        ("CCI","Momentum"),("Williams %R","Momentum"),
        ("Bollinger Bands","Volatility"),("Keltner","Volatility"),("Donchian","Volatility"),
        ("SuperTrend","Trend"),("Ichimoku","Trend"),("Parabolic SAR","Trend"),
        ("VWAP","Volume"),("OBV","Volume"),
    ]
    CAT_COLORS = {"Trend":"#00e676","Momentum":"#4da6ff","Volatility":"#ffd166","Volume":"#b388ff"}
    pills_html = "".join(
        f'<span class="ind-pill" style="border-color:{CAT_COLORS.get(cat,"#1a2235")}22;color:{CAT_COLORS.get(cat,"#8896ab")};">{name}</span>'
        for name, cat in INDICATORS
    )
    st.markdown(f'<div class="ind-grid">{pills_html}</div>', unsafe_allow_html=True)

with col_strat:
    st.markdown('<div class="sh2">STRATEGIES</div><div class="sh2-sub">Ready to backtest in one click.</div>', unsafe_allow_html=True)
    STRATEGIES = [
        ("SMA Crossover",        "Trend",      "#00e676"),
        ("EMA Crossover",        "Trend",      "#00e676"),
        ("RSI Mean Reversion",   "Momentum",   "#4da6ff"),
        ("MACD Signal",          "Momentum",   "#4da6ff"),
        ("Bollinger Bands",      "Volatility", "#ffd166"),
        ("SuperTrend",           "Trend",      "#00e676"),
        ("RSI + Bollinger",      "Combined",   "#b388ff"),
        ("EMA + RSI Filter",     "Combined",   "#b388ff"),
        ("MACD + SuperTrend",    "Combined",   "#b388ff"),
    ]
    for name, cat, col in STRATEGIES:
        st.markdown(
            f'<div class="strat-row">'
            f'<span class="strat-name">{name}</span>'
            f'<span class="strat-tag" style="background:{col}18;color:{col};border:1px solid {col}33;">{cat}</span>'
            f'</div>',
            unsafe_allow_html=True
        )

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ── LEARNING PATH
st.markdown('<div class="sh2">LEARNING PATH</div><div class="sh2-sub">Start here if you\'re new to trading.</div>', unsafe_allow_html=True)
LESSONS = [
    ("How markets work", "Understand price discovery, bid/ask spreads, market orders vs limit orders, and how exchanges match buyers with sellers."),
    ("Reading candlestick charts", "Every candle tells a story: open, high, low, close. Learn to read individual candles and spot patterns like doji, engulfing, and hammer."),
    ("Trend, momentum & volume", "The three pillars of technical analysis. Trend tells you direction, momentum tells you strength, volume confirms conviction."),
    ("Risk management fundamentals", "Position sizing, stop losses, risk/reward ratios, and why protecting capital matters more than finding winners."),
    ("Using indicators without overcomplicating", "Indicators are lagging tools, not crystal balls. Learn how to combine 2-3 indicators cleanly without analysis paralysis."),
    ("Backtesting & avoiding overfitting", "Why past performance is a starting point, not a guarantee. How to test strategies properly and avoid curve-fitting."),
    ("Paper trading & the psychology of practice", "Why Replay mode matters. Building discipline, following rules, and developing intuition through repetition without risk."),
    ("Building your first trading plan", "A trading plan covers entries, exits, position size, max daily loss, and criteria for sitting out. Every serious trader has one."),
]
learn_cols = st.columns(2)
for i, (title, desc) in enumerate(LESSONS):
    with learn_cols[i % 2]:
        st.markdown(
            f'<div class="learn-card">'
            f'<div class="learn-num">0{i+1}</div>'
            f'<div><div class="learn-title">{title}</div>'
            f'<div class="learn-desc">{desc}</div></div>'
            f'</div>',
            unsafe_allow_html=True
        )

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ── FAQ
st.markdown('<div class="sh2">FAQ</div><div class="sh2-sub">Common questions answered.</div>', unsafe_allow_html=True)
FAQS = [
    ("Is 11% really free?", "Yes — completely free. No subscriptions, no paywalls, no ads. The platform is open source."),
    ("Do I need trading experience?", "Not at all. The learning path and AI coach are designed for beginners. Advanced traders will find the backtesting and custom signal builder useful too."),
    ("Is this real money trading?", "No. 11% is purely educational. No real orders are placed. The replay simulator and paper trading are for learning only."),
    ("Where does the market data come from?", "Price data is pulled from Yahoo Finance via yfinance. It's end-of-day data — not real-time tick data."),
    ("How is the AI analysis generated?", "The Analysis and AI Coach pages use Google Gemini (gemini-2.5-flash). The model sees the stock's fundamentals, price history, and recent news."),
    ("Can I build my own strategy?", "Yes — the Custom Signal Builder in Strategy Lab lets you combine up to 3 indicators with AND logic and backtest the result immediately."),
]
faq_cols = st.columns(2)
for i, (q, a) in enumerate(FAQS):
    with faq_cols[i % 2]:
        st.markdown(f'<div class="faq-item"><div class="faq-q">{q}</div><div class="faq-a">{a}</div></div>', unsafe_allow_html=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ── Footer
st.markdown("""
<div style="display:flex;justify-content:space-between;align-items:center;padding:1.5rem 0 0.5rem;flex-wrap:wrap;gap:1rem;">
    <div style="font-family:'IBM Plex Mono',monospace;font-size:0.6rem;color:#3a4a5e;letter-spacing:0.1em;">
        11% · FREE TRADING EDUCATION · OPEN SOURCE · NO ADS
    </div>
    <div style="font-family:'IBM Plex Mono',monospace;font-size:0.58rem;color:#3a4a5e;">
        DATA: YAHOO FINANCE · AI: GOOGLE GEMINI · BUILT WITH STREAMLIT
    </div>
    <div style="font-size:0.72rem;color:#3a4a5e;">
        Educational use only. Not financial advice. Past performance ≠ future results.
    </div>
</div>
""", unsafe_allow_html=True)
