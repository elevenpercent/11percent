import streamlit as st
import yfinance, plotly, pandas, numpy

st.set_page_config(
    page_title="11% — Trading Platform",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=IBM+Plex+Mono:wght@300;400;600;700&family=IBM+Plex+Sans:wght@300;400;600&display=swap');

    :root {
        --bg:        #07090d;
        --surface:   #0d1117;
        --surface2:  #131923;
        --border:    #1c2333;
        --border2:   #263045;
        --green:     #00d68f;
        --red:       #ff4757;
        --gold:      #f0b429;
        --gold2:     #ffd166;
        --blue:      #4da6ff;
        --text:      #cdd5e0;
        --muted:     #3a4558;
        --grid:      rgba(255,255,255,0.03);
    }

    /* ── Base ── */
    html, body,
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"], .main {
        background-color: var(--bg) !important;
        color: var(--text) !important;
        font-family: 'IBM Plex Sans', sans-serif !important;
    }

    /* ── Chart grid background ── */
    [data-testid="stMain"] {
        background-image:
            linear-gradient(var(--grid) 1px, transparent 1px),
            linear-gradient(90deg, var(--grid) 1px, transparent 1px) !important;
        background-size: 48px 48px !important;
        background-position: 0 0 !important;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background-color: var(--surface) !important;
        border-right: 1px solid var(--border) !important;
    }

    /* ── Typography ── */
    h1 { font-family: 'Bebas Neue', sans-serif !important; letter-spacing: 0.06em; color: var(--text) !important; }
    h2 { font-family: 'Bebas Neue', sans-serif !important; letter-spacing: 0.05em; color: var(--text) !important; }
    h3 { font-family: 'IBM Plex Mono', monospace !important; font-size: 0.75rem !important;
         color: var(--gold) !important; text-transform: uppercase; letter-spacing: 0.15em; }

    /* ── Ticker tape ── */
    .ticker-wrap {
        width: 100%;
        overflow: hidden;
        background: var(--surface);
        border-top: 1px solid var(--border);
        border-bottom: 1px solid var(--border);
        padding: 0.45rem 0;
        margin-bottom: 2rem;
    }
    .ticker-tape {
        display: inline-flex;
        animation: ticker 30s linear infinite;
        white-space: nowrap;
    }
    .ticker-item {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.72rem;
        padding: 0 2rem;
        letter-spacing: 0.06em;
    }
    .ticker-up   { color: var(--green); }
    .ticker-down { color: var(--red); }
    .ticker-sym  { color: var(--text); margin-right: 0.4rem; }
    @keyframes ticker {
        0%   { transform: translateX(0); }
        100% { transform: translateX(-50%); }
    }

    /* ── Y-axis label strip ── */
    .yaxis-strip {
        position: fixed;
        right: 0;
        top: 0;
        width: 52px;
        height: 100vh;
        background: var(--surface);
        border-left: 1px solid var(--border);
        display: flex;
        flex-direction: column;
        justify-content: space-around;
        align-items: center;
        z-index: 100;
        padding: 2rem 0;
    }
    .yaxis-val {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.6rem;
        color: var(--muted);
        letter-spacing: 0.05em;
    }

    /* ── Candle decorations ── */
    .candle-green {
        display: inline-block;
        width: 12px;
        background: var(--green);
        border-radius: 1px;
        margin: 0 2px;
        vertical-align: middle;
        position: relative;
    }
    .candle-red {
        display: inline-block;
        width: 12px;
        background: var(--red);
        border-radius: 1px;
        margin: 0 2px;
        vertical-align: middle;
    }

    /* ── Hero ── */
    .hero {
        padding: 2.5rem 0 2rem 0;
        position: relative;
    }
    .hero-eyebrow {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.7rem;
        color: var(--green);
        text-transform: uppercase;
        letter-spacing: 0.25em;
        margin-bottom: 0.8rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .hero-eyebrow::before {
        content: '';
        display: inline-block;
        width: 24px;
        height: 2px;
        background: var(--green);
    }
    .hero-title {
        font-family: 'Bebas Neue', sans-serif;
        font-size: 5.5rem;
        line-height: 0.92;
        letter-spacing: 0.04em;
        margin: 0;
    }
    .hero-title .green  { color: var(--green); }
    .hero-title .red    { color: var(--red); }
    .hero-title .gold   { color: var(--gold); }
    .hero-subtitle {
        font-size: 0.9rem;
        color: var(--muted);
        margin-top: 1.2rem;
        max-width: 480px;
        line-height: 1.7;
        font-family: 'IBM Plex Sans', sans-serif;
    }

    /* ── Candle chart decoration ── */
    .chart-deco {
        display: flex;
        align-items: flex-end;
        gap: 4px;
        height: 80px;
        margin: 1.5rem 0;
        padding: 0;
    }
    .candle-body {
        width: 14px;
        border-radius: 2px;
        position: relative;
        flex-shrink: 0;
    }
    .candle-wick {
        width: 2px;
        background: inherit;
        position: absolute;
        left: 50%;
        transform: translateX(-50%);
        border-radius: 1px;
        opacity: 0.6;
    }
    .candle-wick-top    { bottom: 100%; }
    .candle-wick-bottom { top: 100%; }

    /* ── Feature cards ── */
    .feature-card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 6px;
        padding: 1.4rem;
        height: 100%;
        transition: all 0.2s;
        position: relative;
        overflow: hidden;
    }
    .feature-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0;
        width: 100%; height: 2px;
    }
    .feature-card.green::before { background: var(--green); }
    .feature-card.red::before   { background: var(--red); }
    .feature-card.gold::before  { background: var(--gold); }
    .feature-card.blue::before  { background: var(--blue); }
    .feature-card:hover {
        border-color: var(--border2);
        transform: translateY(-2px);
        box-shadow: 0 8px 32px rgba(0,0,0,0.4);
    }
    .card-icon  { font-size: 1.5rem; margin-bottom: 0.8rem; }
    .card-title {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.78rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        margin-bottom: 0.5rem;
    }
    .card-title.green { color: var(--green); }
    .card-title.gold  { color: var(--gold); }
    .card-title.red   { color: var(--red); }
    .card-title.blue  { color: var(--blue); }
    .card-desc {
        font-size: 0.78rem;
        color: var(--muted);
        line-height: 1.6;
    }

    /* ── OHLC stat boxes ── */
    .ohlc-row {
        display: flex;
        gap: 1px;
        margin: 1.5rem 0;
        background: var(--border);
        border-radius: 6px;
        overflow: hidden;
    }
    .ohlc-box {
        flex: 1;
        background: var(--surface);
        padding: 0.8rem;
        text-align: center;
    }
    .ohlc-label {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.6rem;
        text-transform: uppercase;
        letter-spacing: 0.15em;
        color: var(--muted);
        margin-bottom: 0.3rem;
    }
    .ohlc-value {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 1rem;
        font-weight: 600;
    }

    /* ── Price line divider ── */
    .price-divider {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin: 1.5rem 0;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.65rem;
        color: var(--muted);
    }
    .price-divider::before,
    .price-divider::after {
        content: '';
        flex: 1;
        height: 1px;
        background: var(--border);
    }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 4px; }
    ::-webkit-scrollbar-track { background: var(--bg); }
    ::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 2px; }

    /* ── Buttons ── */
    .stButton > button {
        background: transparent !important;
        color: var(--green) !important;
        border: 1px solid var(--green) !important;
        border-radius: 3px !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-weight: 600 !important;
        font-size: 0.78rem !important;
        letter-spacing: 0.1em !important;
        padding: 0.45rem 1.4rem !important;
        transition: all 0.15s !important;
        text-transform: uppercase !important;
    }
    .stButton > button:hover {
        background: var(--green) !important;
        color: #000 !important;
    }

    hr { border-color: var(--border) !important; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding: 1.2rem 0 1.5rem 0; border-bottom: 1px solid #1c2333;">
        <div style="font-family:'Bebas Neue',sans-serif; font-size:2.2rem; letter-spacing:0.1em;">
            <span style="color:#00d68f;">11</span><span style="color:#ff4757;">%</span>
        </div>
        <div style="font-family:'IBM Plex Mono',monospace; font-size:0.6rem; color:#3a4558;
                    text-transform:uppercase; letter-spacing:0.18em; margin-top:0.2rem;">
            Trading Platform
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="padding-top:1.2rem;">
        <div style="font-family:'IBM Plex Mono',monospace; font-size:0.6rem; color:#3a4558;
                    text-transform:uppercase; letter-spacing:0.18em; margin-bottom:1rem;">
            Navigation
        </div>
    </div>
    """, unsafe_allow_html=True)

    nav_items = [
        ("🔬", "Backtest",       "green"),
        ("📊", "Indicator Test", "gold"),
        ("▶",  "Replay",         "red"),
        ("🧠", "Analysis",       "blue"),
        ("💬", "Assistant",      "green"),
    ]
    for icon, label, color in nav_items:
        colors = {"green": "#00d68f", "gold": "#f0b429", "red": "#ff4757", "blue": "#4da6ff"}
        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:0.8rem; padding:0.5rem 0.3rem;
                    border-bottom:1px solid #1c2333; cursor:pointer;">
            <span style="font-size:0.9rem;">{icon}</span>
            <span style="font-family:'IBM Plex Mono',monospace; font-size:0.72rem;
                         color:#3a4558; text-transform:uppercase; letter-spacing:0.1em;">{label}</span>
            <span style="margin-left:auto; width:6px; height:6px; border-radius:50%;
                         background:{colors[color]};"></span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div style="position:absolute; bottom:1.5rem; left:1rem; right:1rem;">
        <div style="font-family:'IBM Plex Mono',monospace; font-size:0.6rem; color:#3a4558;
                    text-transform:uppercase; letter-spacing:0.1em; text-align:center;">
            Free · Open Source
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Ticker tape ───────────────────────────────────────────────────────────────
tape_items = [
    ("AAPL", "189.43", "+1.23%", True),
    ("TSLA", "238.71", "-2.14%", False),
    ("SPY",  "521.09", "+0.87%", True),
    ("NVDA", "875.32", "+3.41%", True),
    ("MSFT", "415.28", "-0.32%", False),
    ("AMZN", "192.54", "+1.05%", True),
    ("BTC-USD", "67,420", "+4.21%", True),
    ("META", "503.17", "-1.87%", False),
    ("GOOGL","172.63", "+0.54%", True),
    ("AMD",  "168.91", "+2.73%", True),
]

def tape_html(items):
    html = ""
    for sym, price, chg, up in items:
        cls = "ticker-up" if up else "ticker-down"
        arrow = "▲" if up else "▼"
        html += f'<span class="ticker-item"><span class="ticker-sym">{sym}</span><span class="{cls}">{price} {arrow}{chg}</span></span>'
    return html

tape = tape_html(tape_items) * 2  # duplicate for seamless loop
st.markdown(f"""
<div class="ticker-wrap">
    <div class="ticker-tape">{tape}</div>
</div>
""", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────
left, right = st.columns([3, 2])

with left:
    st.markdown("""
    <div class="hero">
        <div class="hero-eyebrow">LIVE · FREE · OPEN SOURCE</div>
        <div class="hero-title">
            <span class="green">BACK</span><br>
            <span class="red">TEST</span><br>
            <span class="gold">FREE</span>
        </div>
        <p class="hero-subtitle">
            A professional-grade trading platform built for everyone.
            Backtest strategies, study indicators, replay charts,
            and get AI-powered analysis — completely free.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Decorative candlestick chart
    candles = [
        (28, 38, "#ff4757"), (32, 44, "#00d68f"), (36, 28, "#ff4757"),
        (40, 52, "#00d68f"), (44, 60, "#00d68f"), (38, 30, "#ff4757"),
        (48, 62, "#00d68f"), (52, 70, "#00d68f"), (46, 38, "#ff4757"),
        (56, 72, "#00d68f"), (60, 78, "#00d68f"), (54, 46, "#ff4757"),
        (62, 80, "#00d68f"),
    ]
    candles_html = '<div class="chart-deco">'
    for low, high, color in candles:
        body_h = max(8, abs(high - low) * 0.7)
        wick_t = abs(high - low) * 0.15
        wick_b = abs(high - low) * 0.15
        candles_html += f"""
        <div class="candle-body" style="height:{body_h}px; background:{color};">
            <div class="candle-wick candle-wick-top" style="height:{wick_t}px; background:{color};"></div>
            <div class="candle-wick candle-wick-bottom" style="height:{wick_b}px; background:{color};"></div>
        </div>"""
    candles_html += '</div>'
    st.markdown(candles_html, unsafe_allow_html=True)

with right:
    # OHLC-style stats box
    st.markdown("""
    <div style="padding-top:2.5rem;">
        <div style="font-family:'IBM Plex Mono',monospace; font-size:0.6rem; color:#3a4558;
                    text-transform:uppercase; letter-spacing:0.18em; margin-bottom:0.8rem;">
            Platform Stats
        </div>
        <div class="ohlc-row">
            <div class="ohlc-box">
                <div class="ohlc-label">Indicators</div>
                <div class="ohlc-value" style="color:#00d68f;">9+</div>
            </div>
            <div class="ohlc-box">
                <div class="ohlc-label">Strategies</div>
                <div class="ohlc-value" style="color:#f0b429;">9</div>
            </div>
        </div>
        <div class="ohlc-row">
            <div class="ohlc-box">
                <div class="ohlc-label">Pages</div>
                <div class="ohlc-value" style="color:#4da6ff;">5</div>
            </div>
            <div class="ohlc-box">
                <div class="ohlc-label">Cost</div>
                <div class="ohlc-value" style="color:#00d68f;">$0</div>
            </div>
        </div>

        <div style="margin-top:1.5rem; font-family:'IBM Plex Mono',monospace; font-size:0.6rem;
                    color:#3a4558; text-transform:uppercase; letter-spacing:0.18em; margin-bottom:0.6rem;">
            Market Status
        </div>
        <div style="background:var(--surface); border:1px solid #1c2333; border-radius:6px; padding:1rem;">
            <div style="display:flex; justify-content:space-between; align-items:center;
                        font-family:'IBM Plex Mono',monospace; font-size:0.72rem; margin-bottom:0.6rem;">
                <span style="color:#3a4558;">NYSE</span>
                <span style="color:#00d68f;">● OPEN</span>
            </div>
            <div style="display:flex; justify-content:space-between; align-items:center;
                        font-family:'IBM Plex Mono',monospace; font-size:0.72rem; margin-bottom:0.6rem;">
                <span style="color:#3a4558;">NASDAQ</span>
                <span style="color:#00d68f;">● OPEN</span>
            </div>
            <div style="display:flex; justify-content:space-between; align-items:center;
                        font-family:'IBM Plex Mono',monospace; font-size:0.72rem;">
                <span style="color:#3a4558;">CRYPTO</span>
                <span style="color:#00d68f;">● 24/7</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Divider ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="price-divider">PLATFORM FEATURES</div>
""", unsafe_allow_html=True)

# ── Feature cards ─────────────────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
cards = [
    (c1, "🔬", "Backtest",       "green", "Test 9 pre-built strategies on any stock. Full metrics: return, drawdown, win rate, Sharpe."),
    (c2, "📊", "Indicators",     "gold",  "Single or combo indicator testing. Up to 3 indicators with AND/OR logic and custom conditions."),
    (c3, "▶",  "Replay",         "red",   "Replay any chart bar by bar. Practice entries and exits with live P&L tracking."),
    (c4, "🧠", "Analysis",       "blue",  "AI-powered fundamental analysis. Financials, risk, valuation, and personalized insights."),
    (c5, "💬", "Assistant",      "green", "Your personal AI trading coach. Knows your backtest history and trading profile."),
]
for col, icon, title, color, desc in cards:
    with col:
        st.markdown(f"""
        <div class="feature-card {color}">
            <div class="card-icon">{icon}</div>
            <div class="card-title {color}">{title}</div>
            <div class="card-desc">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

# ── Divider ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="price-divider" style="margin-top:2rem;">QUICK START</div>
""", unsafe_allow_html=True)

# ── Quick start ───────────────────────────────────────────────────────────────
q1, q2 = st.columns([2, 1])
with q1:
    steps = [
        ("01", "green",  "BACKTEST",  "Pick any stock + strategy → Run Backtest → See returns, drawdown, win rate"),
        ("02", "gold",   "INDICATORS","Choose up to 3 indicators → Set your buy/sell conditions → Run test"),
        ("03", "red",    "REPLAY",    "Pick a stock and date → Step through candles → Practice your trades"),
        ("04", "blue",   "ANALYSIS",  "Enter any ticker → Get AI financial breakdown and investment insights"),
        ("05", "green",  "ASSISTANT", "Ask anything — strategy advice, result explanations, trading concepts"),
    ]
    for num, color, title, desc in steps:
        colors = {"green": "#00d68f", "gold": "#f0b429", "red": "#ff4757", "blue": "#4da6ff"}
        st.markdown(f"""
        <div style="display:flex; gap:1.2rem; padding:0.8rem 0; border-bottom:1px solid #1c2333; align-items:flex-start;">
            <div style="font-family:'IBM Plex Mono',monospace; font-size:1.4rem; font-weight:700;
                        color:{colors[color]}; opacity:0.3; flex-shrink:0; line-height:1;">{num}</div>
            <div>
                <div style="font-family:'IBM Plex Mono',monospace; font-size:0.72rem; font-weight:700;
                            color:{colors[color]}; letter-spacing:0.12em; margin-bottom:0.2rem;">{title}</div>
                <div style="font-size:0.8rem; color:#3a4558;">{desc}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

with q2:
    st.markdown("""
    <div style="background:var(--surface); border:1px solid #1c2333; border-radius:6px;
                padding:1.2rem; margin-top:0.3rem;">
        <div style="font-family:'IBM Plex Mono',monospace; font-size:0.6rem; color:#3a4558;
                    text-transform:uppercase; letter-spacing:0.18em; margin-bottom:1rem;">
            Indicators Available
        </div>
    """, unsafe_allow_html=True)

    indicators = [
        ("SMA / EMA / WMA", "green"),
        ("RSI", "green"),
        ("Stochastic RSI", "gold"),
        ("MACD", "gold"),
        ("Bollinger Bands", "gold"),
        ("SuperTrend", "red"),
        ("Ichimoku Cloud", "blue"),
        ("VWAP", "blue"),
        ("OBV", "blue"),
    ]
    colors_map = {"green": "#00d68f", "gold": "#f0b429", "red": "#ff4757", "blue": "#4da6ff"}
    for name, color in indicators:
        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:0.6rem; padding:0.35rem 0;
                    border-bottom:1px solid #1c2333; font-family:'IBM Plex Mono',monospace;
                    font-size:0.7rem; color:#3a4558;">
            <span style="width:6px; height:6px; border-radius:50%; background:{colors_map[color]};
                         flex-shrink:0;"></span>
            {name}
        </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-top:3rem; padding:1.2rem 0; border-top:1px solid #1c2333;
            display:flex; justify-content:space-between; align-items:center;">
    <div style="font-family:'IBM Plex Mono',monospace; font-size:0.65rem; color:#3a4558;">
        <span style="color:#00d68f;">11</span><span style="color:#ff4757;">%</span>
        &nbsp;·&nbsp; Free · Open Source · Educational Use Only
    </div>
    <div style="font-family:'IBM Plex Mono',monospace; font-size:0.65rem; color:#3a4558;">
        ⚠️ Not financial advice. Past performance ≠ future results.
    </div>
</div>
""", unsafe_allow_html=True)
