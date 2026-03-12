import streamlit as st
import sys, os
sys.path.append(os.path.dirname(__file__))

from utils.styles import SHARED_CSS, LOGO_IMG
from utils.nav import navbar

st.set_page_config(page_title="11% | Free Trading Education", layout="wide", initial_sidebar_state="collapsed")
st.markdown(SHARED_CSS, unsafe_allow_html=True)
navbar()

# ── Ticker tape
TAPE_ITEMS = [
    ("SPY","$568.42","+0.34%",True),("QQQ","$481.18","+0.51%",True),
    ("AAPL","$223.45","+1.12%",True),("TSLA","$187.32","-2.14%",False),
    ("NVDA","$892.18","+3.21%",True),("MSFT","$415.67","+0.44%",True),
    ("AMZN","$198.23","-0.88%",False),("META","$523.11","+1.66%",True),
    ("GOOGL","$172.89","+0.23%",True),("AMD","$152.44","-1.03%",False),
]
tape_html = "".join(
    f'<span class="ticker-item">'
    f'<span class="ticker-sym">{s}</span>'
    f'<span class="ticker-price">{p}</span>'
    f'<span class="ticker-chg {"pos" if up else "neg"}">{c}</span>'
    f'</span>'
    for s,p,c,up in TAPE_ITEMS
)
st.markdown(f"""
<style>
.ticker-wrap {{ overflow:hidden; border-bottom:1px solid #1a2235; background:#030508; padding:0.4rem 0; margin:0 -2.5rem; }}
.ticker-inner {{ display:inline-flex; animation:tickerScroll 28s linear infinite; white-space:nowrap; }}
@keyframes tickerScroll {{ from{{transform:translateX(0)}} to{{transform:translateX(-50%)}} }}
.ticker-item {{ padding:0 1.5rem; border-right:1px solid #0f1621; font-family:'IBM Plex Mono',monospace; font-size:0.7rem; display:inline-flex; align-items:center; gap:0.5rem; }}
.ticker-sym   {{ color:#3a4a5e; font-weight:700; letter-spacing:0.08em; }}
.ticker-price {{ color:#eef2f7; }}
.ticker-chg.pos {{ color:#00e676; }} .ticker-chg.neg {{ color:#ff3d57; }}
</style>
<div class="ticker-wrap">
  <div class="ticker-inner">
    <div>{tape_html}</div><div>{tape_html}</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Hero
st.markdown("""
<style>
.hero-wrap { padding:3.5rem 0 2.5rem; border-bottom:1px solid #1a2235; }
.hero-eyebrow {
    font-family:'IBM Plex Mono',monospace; font-size:0.6rem; font-weight:600;
    text-transform:uppercase; letter-spacing:0.2em; color:#00e676;
    margin-bottom:1rem; display:flex; align-items:center; gap:0.5rem;
}
.hero-wrap h1 {
    font-family:'Bebas Neue',sans-serif;
    font-size:clamp(3rem,7vw,6rem); letter-spacing:0.03em;
    line-height:0.95; color:#eef2f7; margin:0 0 1rem;
}
.hero-wrap h1 em { color:#00e676; font-style:normal; }
.hero-sub { font-size:0.95rem; color:#8896ab; max-width:580px; line-height:1.7; margin-bottom:2rem; }
</style>
<div class="hero-wrap">
    <div class="hero-eyebrow">
        <span style="width:6px;height:6px;border-radius:50%;background:#00e676;display:inline-block;"></span>
        Free · Open Source · No Ads
    </div>
    <h1>LEARN TO <em>TRADE</em> LIKE A PRO</h1>
    <div class="hero-sub">
        11% is a free trading education platform — market simulator, AI-powered analysis, strategy backtesting, and more.
        Built for serious learners who want to understand markets, not just follow signals.
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='height:2rem;'></div>", unsafe_allow_html=True)

# ── Feature cards
st.markdown('<div class="section-hdr">Tools</div>', unsafe_allow_html=True)

FEATURES = [
    ("🎮", "Market Replay",    "#00e676", "/Replay",       "Practice on real historical data bar-by-bar. Buy, sell, and draw on the chart without knowing the future."),
    ("⚗️", "Strategy Lab",    "#4da6ff", "/Strategy_Lab", "Backtest 9 prebuilt strategies or build a custom signal from any combination of indicators."),
    ("🤖", "AI Coach",         "#b388ff", "/Assistant",    "Ask your Gemini-powered trading coach anything — patterns, risk management, or get your backtest reviewed."),
    ("🔍", "Stock Analysis",   "#ffd166", "/Analysis",     "Full fundamentals, 1-year chart, recent news, and an AI deep-dive for any ticker."),
    ("🐋", "Whale Tracker",    "#ff9f43", "/Whale_Tracker","Spot institutional volume anomalies across any watchlist. Large orders often precede big moves."),
    ("📊", "Earnings",         "#00e5ff", "/Earnings",     "Track historical earnings reactions — day-of move, pre-run, and follow-through for any stock."),
    ("🔗", "Correlations",     "#ff3d57", "/Correlations", "Visualize correlation matrices across sectors, the Mag 7, crypto, or a custom list."),
    ("🎲", "Monte Carlo",      "#ff9f43", "/Monte_Carlo",  "Run 1,000 GBM price simulations to visualize the range of possible outcomes."),
]

cols = st.columns(4)
for i, (icon, name, accent, link, desc) in enumerate(FEATURES):
    with cols[i % 4]:
        st.markdown(
            f'<a href="{link}" target="_self" style="text-decoration:none;">'
            f'<div style="background:#0c1018;border:1px solid #1a2235;border-radius:12px;padding:1.2rem;'
            f'margin-bottom:1rem;transition:border-color 0.2s,transform 0.2s;cursor:pointer;'
            f'border-top:2px solid {accent}22;"'
            f' onmouseover="this.style.borderColor=\'{accent}44\';this.style.transform=\'translateY(-2px)\'"'
            f' onmouseout="this.style.borderColor=\'#1a2235\';this.style.transform=\'translateY(0)\'">'
            f'<div style="font-size:1.4rem;margin-bottom:0.6rem;">{icon}</div>'
            f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.65rem;font-weight:700;'
            f'text-transform:uppercase;letter-spacing:0.12em;color:{accent};margin-bottom:0.4rem;">{name}</div>'
            f'<div style="font-size:0.78rem;color:#8896ab;line-height:1.55;">{desc}</div>'
            f'</div></a>',
            unsafe_allow_html=True
        )

st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)

# ── Two column: Indicators + Strategies
col_ind, col_strat = st.columns(2)

with col_ind:
    st.markdown('<div class="section-hdr">Indicators</div>', unsafe_allow_html=True)
    CAT_COLORS = {"Trend":"#00e676","Momentum":"#4da6ff","Volatility":"#ffd166","Volume":"#b388ff"}
    INDICATORS = [
        ("SMA","Trend"),("EMA","Trend"),("WMA","Trend"),("Hull MA","Trend"),("SuperTrend","Trend"),
        ("Ichimoku","Trend"),("Parabolic SAR","Trend"),
        ("RSI","Momentum"),("Stoch RSI","Momentum"),("MACD","Momentum"),("CCI","Momentum"),("Williams %R","Momentum"),
        ("Bollinger Bands","Volatility"),("Keltner","Volatility"),("Donchian","Volatility"),
        ("VWAP","Volume"),("OBV","Volume"),
    ]
    pills = "".join(
        f'<span style="background:#0c1018;border:1px solid {CAT_COLORS.get(cat,"#1a2235")}33;'
        f'color:{CAT_COLORS.get(cat,"#3a4a5e")};border-radius:20px;padding:0.25rem 0.8rem;'
        f'font-family:IBM Plex Mono,monospace;font-size:0.58rem;font-weight:600;'
        f'text-transform:uppercase;letter-spacing:0.08em;margin:0.2rem;display:inline-block;">{name}</span>'
        for name, cat in INDICATORS
    )
    st.markdown(f'<div style="line-height:2.2;">{pills}</div>', unsafe_allow_html=True)

with col_strat:
    st.markdown('<div class="section-hdr">Prebuilt Strategies</div>', unsafe_allow_html=True)
    STRATEGIES = [
        ("SMA Crossover","Trend","#00e676"),("EMA Crossover","Trend","#00e676"),
        ("RSI Mean Reversion","Momentum","#4da6ff"),("MACD Signal","Momentum","#4da6ff"),
        ("Bollinger Bands","Volatility","#ffd166"),("SuperTrend","Trend","#00e676"),
        ("RSI + Bollinger","Combined","#b388ff"),("EMA + RSI Filter","Combined","#b388ff"),
        ("MACD + SuperTrend","Combined","#b388ff"),
    ]
    for name, cat, col in STRATEGIES:
        st.markdown(
            f'<div class="row-item">'
            f'<span style="font-size:0.84rem;color:#eef2f7;">{name}</span>'
            f'<span style="background:{col}18;color:{col};border:1px solid {col}33;'
            f'border-radius:3px;padding:2px 8px;font-family:IBM Plex Mono,monospace;'
            f'font-size:0.55rem;text-transform:uppercase;letter-spacing:0.1em;">{cat}</span>'
            f'</div>',
            unsafe_allow_html=True
        )

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ── FAQ
st.markdown('<div class="section-hdr">FAQ</div>', unsafe_allow_html=True)
FAQS = [
    ("Is 11% really free?", "Yes — completely free, no subscriptions, no ads, open source."),
    ("Do I need trading experience?", "Not at all. The AI coach and learning tools are built for beginners. Advanced traders will find backtesting and custom signals useful too."),
    ("Is this real money trading?", "No. 11% is purely educational. No real orders are placed anywhere."),
    ("Where does the data come from?", "End-of-day price data from Yahoo Finance via yfinance. Not real-time."),
    ("How is the AI analysis generated?", "Analysis and AI Coach use Google Gemini (gemini-2.5-flash)."),
    ("Can I build my own strategy?", "Yes — the Custom Signal Builder lets you combine up to 3 indicators and backtest immediately."),
]
faq_cols = st.columns(2)
for i, (q, a) in enumerate(FAQS):
    with faq_cols[i % 2]:
        st.markdown(
            f'<div style="border-bottom:1px solid #0d1117;padding:0.9rem 0;">'
            f'<div style="font-size:0.86rem;font-weight:600;color:#eef2f7;margin-bottom:0.3rem;">{q}</div>'
            f'<div style="font-size:0.8rem;color:#8896ab;line-height:1.6;">{a}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ── Footer
st.markdown("""
<div style="display:flex;justify-content:space-between;align-items:center;
            padding:1rem 0;flex-wrap:wrap;gap:0.8rem;">
    <div style="font-family:'IBM Plex Mono',monospace;font-size:0.58rem;color:#3a4a5e;letter-spacing:0.1em;">
        11% · FREE TRADING EDUCATION · OPEN SOURCE
    </div>
    <div style="font-size:0.7rem;color:#3a4a5e;">
        Educational use only. Not financial advice.
    </div>
</div>
""", unsafe_allow_html=True)
