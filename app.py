import streamlit as st
import sys, os
from datetime import datetime
import pytz
sys.path.insert(0, os.path.dirname(__file__))
from utils.styles import SHARED_CSS, LOGO_IMG
from utils.nav import navbar
from utils.session_persist import restore_session

st.set_page_config(page_title="11% · Trade Smarter", page_icon="$", layout="wide", initial_sidebar_state="collapsed")
st.markdown(SHARED_CSS, unsafe_allow_html=True)

# ── Home page specific CSS ─────────────────────────────────────────────────────
st.markdown("""<style>
/* Animated grid background */
.home-bg {
    position:fixed; top:0; left:0; width:100%; height:100%;
    pointer-events:none; z-index:0;
    background-image:
        linear-gradient(rgba(38,217,127,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(38,217,127,0.03) 1px, transparent 1px);
    background-size:80px 80px;
    animation:bgShift 20s linear infinite;
}
@keyframes bgShift { 0%{background-position:0 0} 100%{background-position:80px 80px} }

/* Radial glow orbs */
.orb {
    position:fixed; border-radius:50%;
    pointer-events:none; z-index:0; filter:blur(80px);
}
.orb-green { width:600px; height:600px; background:rgba(38,217,127,0.04); top:-200px; right:-200px; }
.orb-red   { width:400px; height:400px; background:rgba(232,64,64,0.03);   bottom:-100px; left:-100px; }

/* Section labels */
.section-label {
    font-family:'IBM Plex Mono',monospace;
    font-size:0.5rem; text-transform:uppercase;
    letter-spacing:0.35em; color:#3d5068;
    border-top:1px solid #1e2830;
    padding-top:1.5rem; margin-top:1.5rem;
    margin-bottom:1rem;
}

/* Feature cards */
.feat-card {
    background:linear-gradient(135deg,#141a1f,#111820);
    border:1px solid #243040;
    border-radius:14px; padding:1.4rem;
    height:100%; min-height:180px;
    transition:border-color 0.25s, transform 0.25s, box-shadow 0.25s;
    position:relative; overflow:hidden;
    animation:fadeUp 0.5s ease both;
}
.feat-card:hover {
    border-color:#26d97f;
    transform:translateY(-4px);
    box-shadow:0 12px 40px rgba(0,0,0,0.4), 0 0 20px rgba(38,217,127,0.07);
}
.feat-card::before {
    content:'';
    position:absolute; top:0; left:0; right:0; height:2px;
    background:linear-gradient(90deg,transparent,var(--card-accent,#26d97f),transparent);
    opacity:0; transition:opacity 0.25s;
}
.feat-card:hover::before { opacity:1; }
.feat-card-icon {
    font-family:'Bebas Neue',sans-serif;
    font-size:0.52rem; text-transform:uppercase;
    letter-spacing:0.25em; margin-bottom:0.8rem;
    padding:3px 10px; border-radius:4px;
    display:inline-block;
}
.feat-card-title {
    font-family:'Bebas Neue',sans-serif;
    font-size:1.5rem; letter-spacing:0.05em;
    color:#e8edf2; margin-bottom:0.4rem;
}
.feat-card-desc {
    font-family:'IBM Plex Mono',monospace;
    font-size:0.67rem; color:#3d5068;
    line-height:1.7;
}

/* Stat cards */
.stat-card {
    background:#141a1f; border:1px solid #243040;
    border-radius:12px; padding:1.2rem 1.4rem;
    text-align:center; animation:fadeUp 0.6s ease both;
    transition:border-color 0.2s;
}
.stat-card:hover { border-color:#2e3d50; }
.stat-num {
    font-family:'Bebas Neue',sans-serif;
    font-size:3rem; letter-spacing:0.04em; line-height:1;
    color:#26d97f;
}
.stat-lbl {
    font-family:'IBM Plex Mono',monospace;
    font-size:0.5rem; text-transform:uppercase;
    letter-spacing:0.2em; color:#3d5068; margin-top:0.3rem;
}

/* Testimonial / why cards */
.why-card {
    background:#141a1f; border:1px solid #243040;
    border-left:3px solid var(--why-color,#26d97f);
    border-radius:0 12px 12px 0;
    padding:1.2rem 1.4rem;
    animation:fadeUp 0.5s ease both;
    transition:background 0.2s;
}
.why-card:hover { background:#181f28; }
.why-title {
    font-family:'Bebas Neue',sans-serif;
    font-size:1.2rem; letter-spacing:0.05em;
    margin-bottom:0.3rem;
}
.why-body {
    font-family:'IBM Plex Mono',monospace;
    font-size:0.68rem; color:#8896ab; line-height:1.7;
}

/* Step cards */
.step-card {
    background:#141a1f; border:1px solid #243040;
    border-radius:12px; padding:1.3rem;
    position:relative; overflow:hidden;
    animation:fadeUp 0.5s ease both;
}
.step-num {
    font-family:'Bebas Neue',sans-serif;
    font-size:4rem; color:#1e2830;
    line-height:1; margin-bottom:0.3rem;
}
.step-title {
    font-family:'IBM Plex Mono',monospace;
    font-size:0.62rem; font-weight:700;
    text-transform:uppercase; letter-spacing:0.12em;
    color:#e8edf2; margin-bottom:0.3rem;
}
.step-desc {
    font-family:'IBM Plex Mono',monospace;
    font-size:0.65rem; color:#3d5068; line-height:1.65;
}

/* Glowing hero text */
.hero-green {
    color:#26d97f;
    animation:glow 3s ease-in-out infinite;
}
@keyframes glow {
    0%,100%{text-shadow:0 0 30px rgba(38,217,127,0.3)}
    50%{text-shadow:0 0 60px rgba(38,217,127,0.6), 0 0 100px rgba(38,217,127,0.2)}
}

/* Candlestick bars animation */
@keyframes barRise { from{height:4px;opacity:0} to{opacity:1} }
.candle-bar { animation:barRise 0.5s ease both; }

/* Marquee ticker */
@keyframes marquee { 0%{transform:translateX(0)} 100%{transform:translateX(-50%)} }
.marquee-wrap {
    overflow:hidden; width:100%;
    background:#141a1f; border:1px solid #243040;
    border-radius:8px; height:36px;
    display:flex; align-items:center;
    margin-bottom:1.8rem; position:relative;
}
.marquee-wrap::before,.marquee-wrap::after {
    content:''; position:absolute; top:0; bottom:0; width:80px; z-index:2;
    pointer-events:none;
}
.marquee-wrap::before { left:0;  background:linear-gradient(90deg,#141a1f,transparent); }
.marquee-wrap::after  { right:0; background:linear-gradient(-90deg,#141a1f,transparent); }
.marquee-track {
    display:flex; white-space:nowrap;
    animation:marquee 40s linear infinite;
}
.marquee-item {
    display:inline-flex; align-items:center; gap:8px;
    padding:0 24px; border-right:1px solid #243040;
    font-family:'IBM Plex Mono',monospace; font-size:0.68rem;
    flex-shrink:0;
}

/* Tool grid */
.tool-chip {
    background:#141a1f; border:1px solid #243040;
    border-radius:8px; padding:0.7rem 1rem;
    font-family:'IBM Plex Mono',monospace;
    font-size:0.65rem; color:#8896ab;
    transition:border-color 0.2s, color 0.2s, background 0.2s;
    cursor:pointer; text-align:center;
}
.tool-chip:hover {
    border-color:#26d97f; color:#26d97f;
    background:rgba(38,217,127,0.04);
}
.tool-chip-name { font-weight:700; font-size:0.72rem; margin-bottom:0.1rem; color:#e8edf2; }

/* Market status */
.mkt-pill {
    display:inline-flex; align-items:center; gap:6px;
    font-family:'IBM Plex Mono',monospace; font-size:0.62rem;
    padding:4px 12px; border-radius:20px;
    border:1px solid; white-space:nowrap;
}

/* Animated underline on hover */
.animated-link {
    position:relative; display:inline-block;
    font-family:'IBM Plex Mono',monospace;
    font-size:0.65rem; font-weight:700;
    text-transform:uppercase; letter-spacing:0.1em;
    color:#26d97f; text-decoration:none;
    padding-bottom:2px;
}
.animated-link::after {
    content:''; position:absolute; bottom:0; left:0;
    width:0; height:1px; background:#26d97f;
    transition:width 0.3s;
}
.animated-link:hover::after { width:100%; }
</style>""", unsafe_allow_html=True)

restore_session()
navbar()

# Animated background
st.markdown('<div class="home-bg"></div><div class="orb orb-green"></div><div class="orb orb-red"></div>', unsafe_allow_html=True)

# ── Helpers ──────────────────────────────────────────────────────────────────
def get_market_status(name):
    now = datetime.now(pytz.utc).astimezone(pytz.timezone("America/New_York"))
    if name == "Crypto": return "OPEN 24/7", "#26d97f"
    if now.weekday() >= 5: return "CLOSED", "#e84040"
    s = now.replace(hour=9,  minute=30, second=0, microsecond=0)
    e = now.replace(hour=16, minute=0,  second=0, microsecond=0)
    if s <= now <= e: return "OPEN", "#26d97f"
    elif now < s:     return f"PRE-MARKET", "#f0c040"
    else:             return "AFTER-HOURS", "#f0c040"

import yfinance as yf

@st.cache_data(ttl=1800)
def get_tape(tickers):
    out = []
    for s in tickers:
        try:
            h = yf.Ticker(s).history(period="2d")
            if len(h) >= 2:
                p, c = float(h["Close"].iloc[-2]), float(h["Close"].iloc[-1])
                chg = (c - p) / p * 100
                out.append((s, f"{c:,.2f}", f"{chg:+.2f}%", "▲" if chg >= 0 else "▼", "t-up" if chg >= 0 else "t-dn"))
        except: pass
    return out

# ── Welcome banner ─────────────────────────────────────────────────────────────
user_email = st.session_state.get("user_email", "")
if user_email:
    uname = user_email.split("@")[0].replace(".", " ").replace("_", " ").title()
    st.markdown(f"""
    <div style="background:rgba(38,217,127,0.05);border:1px solid rgba(38,217,127,0.2);
    border-radius:10px;padding:0.85rem 1.4rem;margin-bottom:1.2rem;
    display:flex;align-items:center;justify-content:space-between;animation:fadeUp 0.3s ease both;">
        <div style="display:flex;align-items:center;gap:0.8rem;">
            <div style="width:36px;height:36px;border-radius:50%;background:rgba(38,217,127,0.12);
            border:1px solid rgba(38,217,127,0.3);display:flex;align-items:center;justify-content:center;
            font-family:IBM Plex Mono,monospace;font-size:0.72rem;font-weight:700;color:#26d97f;">
            {uname[0].upper()}</div>
            <div>
                <div style="font-family:IBM Plex Mono,monospace;font-size:0.55rem;color:#3d5068;
                text-transform:uppercase;letter-spacing:0.15em;margin-bottom:0.1rem;">Welcome back</div>
                <div style="font-size:1rem;font-weight:600;color:#e8edf2;">Hi, {uname}</div>
            </div>
        </div>
        <div style="font-family:IBM Plex Mono,monospace;font-size:0.55rem;color:#3d5068;">
            Ready to trade smarter today?
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Ticker tape ─────────────────────────────────────────────────────────────────
TICKERS = ["AAPL","TSLA","SPY","NVDA","MSFT","AMZN","BTC-USD","META","GOOGL","AMD",
           "NFLX","JPM","V","WMT","QQQ","GLD","PLTR","COIN","TSM","SMCI"]
tape = get_tape(tuple(TICKERS))
if tape:
    items = "".join(
        f'<span class="marquee-item">'
        f'<span style="color:#3d5068;font-weight:700">{s}</span>'
        f'<span style="color:{"#26d97f" if "▲" in a else "#e84040"}">{p} {a} {ch}</span>'
        f'</span>'
        for s, p, ch, a, _ in tape
    )
    st.markdown(f'<div class="marquee-wrap"><div class="marquee-track">{items}{items}</div></div>', unsafe_allow_html=True)

# ── HERO ────────────────────────────────────────────────────────────────────────
hero_l, hero_r = st.columns([6, 5])

with hero_l:
    # Animated candlestick bars
    bars = [(38,"#e84040"),(44,"#26d97f"),(28,"#e84040"),(52,"#26d97f"),(60,"#26d97f"),
            (30,"#e84040"),(62,"#26d97f"),(70,"#26d97f"),(38,"#e84040"),(72,"#26d97f"),
            (78,"#26d97f"),(46,"#e84040"),(80,"#26d97f"),(74,"#26d97f"),(85,"#26d97f"),
            (65,"#e84040"),(88,"#26d97f"),(79,"#e84040"),(92,"#26d97f"),(95,"#26d97f")]
    bars_html = "".join(
        f'<div class="candle-bar" style="width:12px;height:{h}px;background:{c};border-radius:3px;'
        f'opacity:0.85;animation-delay:{i*0.05}s"></div>'
        for i, (h, c) in enumerate(bars)
    )

    # Market status pills
    mkt_items = ""
    for label, mname in [("NYSE","NYSE"),("NASDAQ","NASDAQ"),("Crypto","Crypto")]:
        ms, mc = get_market_status(mname)
        dot_anim = 'animation:ep-pulse 2s ease-in-out infinite' if "OPEN" in ms else ''
        mkt_items += f'<span class="mkt-pill" style="color:{mc};border-color:{mc}30;background:{mc}08"><span style="width:6px;height:6px;border-radius:50%;background:{mc};display:inline-block;{dot_anim}"></span>{label} {ms}</span>'

    st.markdown(f"""
    <div style="padding:1.5rem 0 1rem;animation:fadeUp 0.4s ease both">
        <div style="display:flex;align-items:flex-end;gap:4px;height:72px;margin-bottom:1rem">
            {bars_html}
        </div>
        <div style="font-family:'Bebas Neue',sans-serif;font-size:5.5rem;line-height:0.88;
        letter-spacing:0.02em;margin-bottom:1.4rem">
            <span class="hero-green">TRADE</span><br>
            <span style="color:#e8edf2">SMARTER</span><br>
            <span style="color:#e84040">NOT HARDER</span>
        </div>
        <div style="font-family:'IBM Plex Mono',monospace;font-size:0.82rem;color:#8896ab;
        max-width:480px;line-height:1.9;margin-bottom:1.6rem">
            A professional-grade trading education platform. Backtest real strategies,
            replay historical charts bar-by-bar, get AI analysis, and build real edge —
            completely free.
        </div>
        <div style="display:flex;gap:0.5rem;flex-wrap:wrap;margin-bottom:1.4rem">
            {mkt_items}
        </div>
    </div>
    """, unsafe_allow_html=True)

    btn1, btn2, btn3 = st.columns(3)
    with btn1: st.page_link("pages/1_Strategy_Lab.py", label="Strategy Lab")
    with btn2: st.page_link("pages/3_Replay.py",       label="Market Replay")
    with btn3: st.page_link("pages/5_Assistant.py",    label="AI Coach")

with hero_r:
    st.markdown("""
    <div style="padding:1.5rem 0;animation:fadeUp 0.5s ease both">
        <div style="background:#141a1f;border:1px solid #243040;border-radius:14px 14px 0 0;
        border-bottom:none;padding:0.5rem 1rem;
        display:flex;align-items:center;gap:6px">
            <div style="width:10px;height:10px;border-radius:50%;background:#e84040"></div>
            <div style="width:10px;height:10px;border-radius:50%;background:#f0c040"></div>
            <div style="width:10px;height:10px;border-radius:50%;background:#26d97f"></div>
            <span style="margin-left:6px;font-family:IBM Plex Mono,monospace;font-size:0.5rem;
            color:#3d5068;text-transform:uppercase;letter-spacing:0.16em">Live Chart · TradingView</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.components.v1.html("""
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#141a1f}
.wrap{height:300px;width:100%;background:#141a1f;border:1px solid #243040;
border-top:none;border-radius:0 0 14px 14px;overflow:hidden}
</style>
<div class="wrap">
  <div class="tradingview-widget-container" style="height:100%;width:100%">
    <div id="tv_home" style="height:100%;width:100%"></div>
    <script src="https://s3.tradingview.com/tv.js"></script>
    <script>
    new TradingView.widget({
      autosize:true, symbol:"NASDAQ:AAPL", interval:"D",
      timezone:"America/New_York", theme:"dark", style:"1", locale:"en",
      toolbar_bg:"#141a1f", enable_publishing:false, hide_side_toolbar:true,
      allow_symbol_change:true, save_image:false, container_id:"tv_home",
      backgroundColor:"rgba(20,26,31,1)", gridColor:"rgba(30,40,50,0.4)",
      overrides:{
        "mainSeriesProperties.candleStyle.upColor":"#26d97f",
        "mainSeriesProperties.candleStyle.downColor":"#e84040",
        "mainSeriesProperties.candleStyle.borderUpColor":"#26d97f",
        "mainSeriesProperties.candleStyle.borderDownColor":"#e84040",
        "mainSeriesProperties.candleStyle.wickUpColor":"#26d97f",
        "mainSeriesProperties.candleStyle.wickDownColor":"#e84040",
        "paneProperties.background":"#141a1f",
        "paneProperties.backgroundType":"solid",
        "paneProperties.vertGridProperties.color":"#1e2830",
        "paneProperties.horzGridProperties.color":"#1e2830",
        "scalesProperties.textColor":"#3d5068",
        "scalesProperties.lineColor":"#1e2830"
      }
    });
    </script>
  </div>
</div>
""", height=310, scrolling=False)

    # Quick stats
    st.markdown("""
    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-top:0.8rem">
        <div class="stat-card" style="animation-delay:0.1s"><div class="stat-num">15</div><div class="stat-lbl">Indicators</div></div>
        <div class="stat-card" style="animation-delay:0.2s"><div class="stat-num" style="color:#e84040">9</div><div class="stat-lbl">Strategies</div></div>
        <div class="stat-card" style="animation-delay:0.3s"><div class="stat-num">20+</div><div class="stat-lbl">Tools</div></div>
        <div class="stat-card" style="animation-delay:0.4s"><div class="stat-num" style="color:#f0c040">$0</div><div class="stat-lbl">Forever Free</div></div>
    </div>
    """, unsafe_allow_html=True)

# ── PLATFORM FEATURES ──────────────────────────────────────────────────────────
st.markdown('<div class="section-label">Platform Features</div>', unsafe_allow_html=True)

features = [
    ("Strategy Lab", "BACKTEST", "#26d97f",
     "9 pre-built strategies plus a custom signal builder with 15 indicators. Run backtests with real data, see equity curves, trade logs, and alpha vs buy-and-hold.",
     "pages/1_Strategy_Lab.py"),
    ("Market Replay", "FLAGSHIP", "#e84040",
     "Step through history bar by bar. Execute trades without knowing what comes next. Build real muscle memory for reading price action under pressure.",
     "pages/3_Replay.py"),
    ("AI Coach", "AI-POWERED", "#4da6ff",
     "Ask anything in plain English. Get your backtest results explained, strategy ideas, risk management advice, and real-time market breakdowns.",
     "pages/5_Assistant.py"),
    ("Options Chain", "NEW", "#a78bfa",
     "Live options chain with open interest chart, full Greeks, Black-Scholes pricer, and a Play Advisor that scores every strategy for your specific setup.",
     "pages/11_Options_Chain.py"),
    ("Market Heatmap", "LIVE", "#f0c040",
     "See every sector and stock colour-coded by today's performance. Full-screen ticker mode for trading monitors. Custom dashboard for any tickers you want.",
     "pages/15_Market_Heatmap.py"),
    ("Screener", "PRO", "#26d97f",
     "Filter 70+ stocks across 6 sectors by RSI, momentum, SMA position, volume spikes, and market cap. TradingView-style sortable results table.",
     "pages/12_Screener.py"),
]

cols = st.columns(3)
for i, (title, badge, color, desc, link) in enumerate(features):
    with cols[i % 3]:
        st.markdown(f"""
        <div class="feat-card" style="--card-accent:{color};animation-delay:{i*0.08}s">
            <div class="feat-card-icon" style="background:{color}15;color:{color};border:1px solid {color}30">{badge}</div>
            <div class="feat-card-title">{title}</div>
            <div class="feat-card-desc">{desc}</div>
        </div>
        """, unsafe_allow_html=True)
        st.page_link(link, label=f"Open {title}")

# ── MORE TOOLS GRID ────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">All Tools</div>', unsafe_allow_html=True)

tools = [
    ("Risk Calculator",    "Position sizing, R-multiples, Kelly",     "pages/10_Risk_Calculator.py"),
    ("Trade Journal",      "Log trades, emotions, mistakes",          "pages/14_Trade_Journal.py"),
    ("Portfolio Tracker",  "Live P&L, allocation charts",             "pages/13_Portfolio_Tracker.py"),
    ("Monte Carlo",        "1,000 price path simulations",            "pages/9_Monte_Carlo.py"),
    ("Earnings Tracker",   "Historical earnings reactions",           "pages/6_Earnings.py"),
    ("Sector Rotation",    "Follow institutional money",              "pages/16_Sector_Rotation.py"),
    ("Whale Tracker",      "Unusual volume anomalies",                "pages/8_Whale_Tracker.py"),
    ("Correlations",       "Asset correlation matrix",                "pages/7_Correlations.py"),
    ("Pattern Recognition","Auto-detect chart patterns",              "pages/18_Pattern_Recognition.py"),
    ("Trade Stats",        "Upload CSV, full analytics",              "pages/19_Trade_Stats.py"),
    ("Econ Calendar",      "FOMC, CPI, NFP, GDP — 2026",             "pages/20_Economic_Calendar.py"),
    ("Analysis",           "Fundamentals + AI breakdown",             "pages/4_Analysis.py"),
]

tool_cols = st.columns(4)
for i, (name, desc, link) in enumerate(tools):
    with tool_cols[i % 4]:
        st.markdown(f"""
        <div class="tool-chip" style="margin-bottom:8px;animation:fadeUp 0.4s ease both;animation-delay:{i*0.04}s">
            <div class="tool-chip-name">{name}</div>
            <div>{desc}</div>
        </div>
        """, unsafe_allow_html=True)
        st.page_link(link, label="Open")

# ── WHY 11% ────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">Why 11%</div>', unsafe_allow_html=True)

why_items = [
    ("#26d97f", "Learn by doing, not reading",
     "Most trading education is theory. 11% puts you in the market — with real historical data, real backtests, and real replay sessions. You will make mistakes in simulation before you make them with real money."),
    ("#e84040", "Built by traders, for traders",
     "Every feature was designed around actual trading workflows. The replay engine is bar-by-bar. The screener shows what TV shows. The journal captures emotions not just entries."),
    ("#4da6ff", "AI that actually explains things",
     "Our AI Coach doesn't just answer questions — it connects your backtest results to actionable next steps, explains why a strategy failed, and suggests improvements specific to your setup."),
    ("#f0c040", "Everything in one place",
     "Backtest, replay, analyze, screen, journal, track portfolio, calculate risk — all linked. Your replay trades inform your journal. Your journal feeds your AI coach. Context stays connected."),
]

why_cols = st.columns(2)
for i, (color, title, body) in enumerate(why_items):
    with why_cols[i % 2]:
        st.markdown(f"""
        <div class="why-card" style="--why-color:{color};margin-bottom:10px;animation-delay:{i*0.1}s">
            <div class="why-title" style="color:{color}">{title}</div>
            <div class="why-body">{body}</div>
        </div>
        """, unsafe_allow_html=True)

# ── HOW IT WORKS ───────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">How It Works</div>', unsafe_allow_html=True)

steps = [
    ("01", "Pick Your Stock", "Enter any ticker. Stocks, ETFs, indices, crypto. Live data from Yahoo Finance."),
    ("02", "Choose a Strategy", "Select from 9 pre-built strategies or build your own with our 15-indicator signal builder."),
    ("03", "Run the Backtest", "Set date range and capital. Results — return, alpha, drawdown, Sharpe — in seconds."),
    ("04", "Replay the Moves", "Step through the same period bar-by-bar and trade it in real time without knowing the outcome."),
    ("05", "Ask the Coach", "Paste your results into the AI Coach. Get plain-English explanation of what worked and why."),
]

step_cols = st.columns(5)
for i, (num, title, desc) in enumerate(steps):
    with step_cols[i]:
        st.markdown(f"""
        <div class="step-card" style="animation-delay:{i*0.08}s">
            <div class="step-num">{num}</div>
            <div class="step-title">{title}</div>
            <div class="step-desc">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

# ── INDICATORS ─────────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">15 Indicators Available</div>', unsafe_allow_html=True)

ind_cols = st.columns(3)
for col, (cat, color, inds) in zip(ind_cols, [
    ("Trend",               "#4da6ff", ["SMA","EMA","WMA","Hull MA","SuperTrend","Ichimoku","Parabolic SAR"]),
    ("Momentum",            "#a78bfa", ["RSI","Stochastic RSI","MACD","CCI","Williams %R"]),
    ("Volatility & Volume", "#f0c040", ["Bollinger Bands","Keltner Channels","Donchian Channels","VWAP","OBV"]),
]):
    tags = "".join(
        f'<span style="display:inline-block;font-family:IBM Plex Mono,monospace;font-size:0.62rem;'
        f'padding:3px 10px;border-radius:4px;background:{color}12;color:{color};'
        f'border:1px solid {color}25;margin:3px 3px 3px 0;">{ind}</span>'
        for ind in inds
    )
    col.markdown(f"""
    <div style="background:#141a1f;border:1px solid #243040;border-radius:12px;padding:1.2rem;height:100%">
        <div style="font-family:IBM Plex Mono,monospace;font-size:0.55rem;color:{color};
        text-transform:uppercase;letter-spacing:0.18em;margin-bottom:0.8rem">{cat}</div>
        <div>{tags}</div>
    </div>
    """, unsafe_allow_html=True)

# ── ABOUT THE NAME ─────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">Why 11%?</div>', unsafe_allow_html=True)
st.markdown("""
<div style="background:linear-gradient(135deg,#141a1f,#111820);border:1px solid #243040;
border-radius:16px;padding:2.5rem 3rem;position:relative;overflow:hidden;animation:fadeUp 0.5s ease both">
    <div style="position:absolute;top:-60px;right:-60px;width:200px;height:200px;
    background:radial-gradient(circle,rgba(38,217,127,0.06),transparent 70%);pointer-events:none"></div>
    <div style="font-family:'Bebas Neue',sans-serif;font-size:4rem;letter-spacing:0.04em;margin-bottom:0.8rem">
        <span style="color:#26d97f">11</span><span style="color:#e84040">%</span>
        <span style="color:#e8edf2;font-size:2rem;margin-left:0.5rem">— THE EDGE THAT CHANGES EVERYTHING</span>
    </div>
    <div style="font-family:'IBM Plex Mono',monospace;font-size:0.75rem;color:#8896ab;
    line-height:2;max-width:800px">
        The S&amp;P 500 returns roughly 10% per year. Most retail traders underperform it.
        Getting to <strong style="color:#26d97f">11%</strong> — just one percentage point above the index —
        means your edge is real, your process is sound, and compounding is working in your favour.
        <br><br>
        That's the mission. Not moon shots. Not leverage. Not tips.
        <strong style="color:#e8edf2">Consistent, process-driven outperformance.</strong>
        The tools on this platform are built to help you get there.
    </div>
</div>
""", unsafe_allow_html=True)

# ── FAQ ────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">FAQ</div>', unsafe_allow_html=True)

fqa, fqb = st.columns(2)
faq_items = [
    ("Is this real trading?",                     "No — fully simulated. No real money involved. Data from Yahoo Finance. Educational use only."),
    ("How accurate is the backtest?",             "Indicative, not guaranteed. Assumes closing-price fills with no slippage, spread, or commission. Real results will differ."),
    ("Do I need to know how to code?",            "No. Everything is point-and-click. The platform is built on open-source Python/Streamlit if you want to extend it."),
    ("How do I enable the AI features?",          "Add your Gemini API key to Streamlit Secrets as GEMINI_API_KEY. The free tier is more than enough."),
    ("Is my data saved between sessions?",        "Yes — if you create an account. Trade journal, portfolio, and replay trades sync to your profile via Supabase."),
    ("Why can't past performance predict future?","Markets adapt. A strategy that worked in a bull run may fail in a bear market. The goal is to understand why a strategy works, not just that it worked."),
    ("What data does it use?",                    "Yahoo Finance via yfinance. Years of daily OHLCV for US stocks, ETFs, indices, and major crypto pairs."),
    ("Is it really free?",                        "Yes. No credit card. No trial period. No premium tier. The full platform is free."),
]
for i, (q, a) in enumerate(faq_items):
    with (fqa if i % 2 == 0 else fqb).expander(q):
        st.markdown(f'<div style="font-family:IBM Plex Mono,monospace;font-size:0.75rem;color:#8896ab;line-height:1.8">{a}</div>', unsafe_allow_html=True)

# ── FOOTER ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-top:3rem;padding:1.5rem 0;border-top:1px solid #1e2830;
display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:0.5rem">
    <div style="font-family:'Bebas Neue',sans-serif;font-size:1.2rem;letter-spacing:0.06em">
        <span style="color:#26d97f">11</span><span style="color:#e84040">%</span>
        <span style="font-family:IBM Plex Mono,monospace;font-size:0.58rem;color:#3d5068;
        font-family:normal;letter-spacing:0.1em;margin-left:0.5rem">TRADE SMARTER</span>
    </div>
    <div style="font-family:'IBM Plex Mono',monospace;font-size:0.55rem;color:#3d5068">
        Not financial advice &nbsp;·&nbsp; Educational use only &nbsp;·&nbsp; Data: Yahoo Finance
    </div>
</div>
""", unsafe_allow_html=True)
