import streamlit as st
import yfinance, plotly, pandas, numpy

st.set_page_config(
    page_title="11% — Trading Platform",
    page_icon="💲",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=IBM+Plex+Mono:wght@300;400;600;700&family=IBM+Plex+Sans:wght@300;400;600&display=swap');
    :root {
        --bg:#07090d; --surface:#0d1117; --border:#1c2333; --border2:#263045;
        --green:#00d68f; --red:#ff4757; --text:#cdd5e0; --muted:#3a4558;
        --grid:rgba(255,255,255,0.03);
    }
    html,body,[data-testid="stAppViewContainer"],[data-testid="stMain"],.main {
        background-color:var(--bg)!important; color:var(--text)!important;
        font-family:'IBM Plex Sans',sans-serif!important;
    }
    [data-testid="stMain"] {
        background-image:linear-gradient(var(--grid) 1px,transparent 1px),linear-gradient(90deg,var(--grid) 1px,transparent 1px)!important;
        background-size:48px 48px!important;
    }
    [data-testid="stSidebar"] { background-color:var(--surface)!important; border-right:1px solid var(--border)!important; }
    [data-testid="stSidebarNav"] { display:none!important; }
    h1 { font-family:'Bebas Neue',sans-serif!important; letter-spacing:0.06em; color:var(--text)!important; }
    h2 { font-family:'Bebas Neue',sans-serif!important; letter-spacing:0.05em; color:var(--text)!important; }
    h3 { font-family:'IBM Plex Mono',monospace!important; font-size:0.75rem!important; color:var(--green)!important; text-transform:uppercase; letter-spacing:0.15em; }
    .ticker-wrap { width:100%; overflow:hidden; background:var(--surface); border-top:1px solid var(--border); border-bottom:1px solid var(--border); padding:0.45rem 0; margin-bottom:2rem; }
    .ticker-tape { display:inline-flex; animation:ticker 30s linear infinite; white-space:nowrap; }
    .ticker-item { font-family:'IBM Plex Mono',monospace; font-size:0.72rem; padding:0 2rem; letter-spacing:0.06em; }
    .ticker-up { color:var(--green); }
    .ticker-down { color:var(--red); }
    .ticker-sym { color:var(--text); margin-right:0.4rem; }
    @keyframes ticker { 0%{transform:translateX(0)} 100%{transform:translateX(-50%)} }
    .hero { padding:2.5rem 0 2rem 0; }
    .hero-eyebrow { font-family:'IBM Plex Mono',monospace; font-size:0.7rem; color:var(--green); text-transform:uppercase; letter-spacing:0.25em; margin-bottom:0.8rem; }
    .hero-title { font-family:'Bebas Neue',sans-serif; font-size:5.5rem; line-height:0.92; letter-spacing:0.04em; margin:0; }
    .hero-title .green { color:var(--green); }
    .hero-title .red   { color:var(--red); }
    .hero-subtitle { font-size:0.9rem; color:var(--muted); margin-top:1.2rem; max-width:480px; line-height:1.7; }
    .chart-deco { display:flex; align-items:flex-end; gap:4px; height:80px; margin:1.5rem 0; }
    .candle-body { width:14px; border-radius:2px; position:relative; flex-shrink:0; }
    .candle-wick { width:2px; background:inherit; position:absolute; left:50%; transform:translateX(-50%); border-radius:1px; opacity:0.6; }
    .candle-wick-top { bottom:100%; }
    .candle-wick-bottom { top:100%; }
    .ohlc-row { display:flex; gap:1px; margin:0.8rem 0; background:var(--border); border-radius:6px; overflow:hidden; }
    .ohlc-box { flex:1; background:var(--surface); padding:0.8rem; text-align:center; }
    .ohlc-label { font-family:'IBM Plex Mono',monospace; font-size:0.6rem; text-transform:uppercase; letter-spacing:0.15em; color:var(--muted); margin-bottom:0.3rem; }
    .ohlc-value { font-family:'IBM Plex Mono',monospace; font-size:1rem; font-weight:600; }
    .price-divider { display:flex; align-items:center; gap:1rem; margin:1.5rem 0; font-family:'IBM Plex Mono',monospace; font-size:0.65rem; color:var(--muted); }
    .price-divider::before,.price-divider::after { content:''; flex:1; height:1px; background:var(--border); }
    ::-webkit-scrollbar { width:4px; }
    ::-webkit-scrollbar-track { background:var(--bg); }
    ::-webkit-scrollbar-thumb { background:var(--border2); border-radius:2px; }
    .stButton>button { background:transparent!important; color:var(--green)!important; border:1px solid var(--green)!important; border-radius:3px!important; font-family:'IBM Plex Mono',monospace!important; font-weight:600!important; font-size:0.78rem!important; letter-spacing:0.1em!important; padding:0.45rem 1.4rem!important; transition:all 0.15s!important; text-transform:uppercase!important; }
    .stButton>button:hover { background:var(--green)!important; color:#000!important; }
    hr { border-color:var(--border)!important; }
    [data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"] { font-family:'IBM Plex Mono',monospace!important; font-size:0.72rem!important; text-transform:uppercase!important; letter-spacing:0.1em!important; color:#3a4558!important; padding:0.45rem 0.3rem!important; border-bottom:1px solid #1c2333!important; border-radius:0!important; display:block!important; }
    [data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"]:hover { color:#00d68f!important; background:transparent!important; }
    [data-testid="stSidebar"] a[aria-current="page"] { color:#00d68f!important; background:transparent!important; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("assets/logo.png", width=120)
    st.markdown('''<div style="padding-top:1rem;padding-bottom:0.5rem;border-top:1px solid #1c2333;"><div style="font-family:IBM Plex Mono,monospace;font-size:0.6rem;color:#3a4558;text-transform:uppercase;letter-spacing:0.18em;margin-bottom:0.5rem;">Navigation</div></div>''', unsafe_allow_html=True)
    st.page_link("app.py",                       label=" Home")
    st.page_link("pages/1_Backtest.py",          label=" Backtest")
    st.page_link("pages/2_Indicator_Test.py",    label=" Indicator")
    st.page_link("pages/3_Replay.py",            label="  Replay")
    st.page_link("pages/4_Analysis.py",          label=" Analysis")
    st.page_link("pages/5_Assistant.py",         label=" Assistant")
    st.markdown('''<div style="position:absolute;bottom:1.5rem;left:1rem;right:1rem;text-align:center;font-family:IBM Plex Mono,monospace;font-size:0.6rem;color:#3a4558;text-transform:uppercase;letter-spacing:0.1em;">Free · Open Source</div>''', unsafe_allow_html=True)

# ── Ticker tape ───────────────────────────────────────────────────────────────
TAPE_TICKERS = ["AAPL","TSLA","SPY","NVDA","MSFT","AMZN","BTC-USD","META","GOOGL","AMD","SOFI","HOOD","ETH-USD"]

@st.cache_data(ttl=3600)
def get_tape_data(tickers):
    import yfinance as yf
    items = []
    for sym in tickers:
        try:
            hist = yf.Ticker(sym).history(period="2d")
            if len(hist) >= 2:
                prev  = float(hist["Close"].iloc[-2])
                close = float(hist["Close"].iloc[-1])
                chg   = ((close - prev) / prev) * 100
                up    = chg >= 0
                items.append((sym, f"{close:,.2f}", f"{chg:+.2f}%", "▲" if up else "▼", "ticker-up" if up else "ticker-down"))
        except Exception:
            pass
    return items

with st.spinner("Loading market data..."):
    tape_items = get_tape_data(tuple(TAPE_TICKERS))

if tape_items:
    tape_html = ""
    for sym, price, chg, arrow, cls in tape_items:
        tape_html += f'<span class="ticker-item"><span class="ticker-sym">{sym}</span><span class="{cls}">{price} {arrow}{chg}</span></span>'
    tape_html = tape_html * 2
    st.markdown(f'<div class="ticker-wrap"><div class="ticker-tape">{tape_html}</div></div>', unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────
left, right = st.columns([3, 2])

with left:
    st.markdown("""
    <div class="hero">
        <div class="hero-eyebrow">LIVE · FREE · OPEN SOURCE</div>
        <div class="hero-title">
            <span class="green">BACK</span><br>
            <span class="red">TEST</span>
        </div>
        <p class="hero-subtitle">
            A professional-grade trading platform built for everyone.
            Backtest strategies, study indicators, replay charts,
            and get AI-powered analysis — completely free.
        </p>
    </div>
    """, unsafe_allow_html=True)

    candles = [
        (28,38,"#ff4757"),(32,44,"#00d68f"),(36,28,"#ff4757"),
        (40,52,"#00d68f"),(44,60,"#00d68f"),(38,30,"#ff4757"),
        (48,62,"#00d68f"),(52,70,"#00d68f"),(46,38,"#ff4757"),
        (56,72,"#00d68f"),(60,78,"#00d68f"),(54,46,"#ff4757"),
        (62,80,"#00d68f"),
    ]
    ch = '<div class="chart-deco">'
    for low, high, color in candles:
        bh = max(8, abs(high-low)*0.7)
        wt = abs(high-low)*0.15
        wb = abs(high-low)*0.15
        ch += f'<div class="candle-body" style="height:{bh}px;background:{color};"><div class="candle-wick candle-wick-top" style="height:{wt}px;background:{color};"></div><div class="candle-wick candle-wick-bottom" style="height:{wb}px;background:{color};"></div></div>'
    ch += '</div>'
    st.markdown(ch, unsafe_allow_html=True)

with right:
    st.markdown("""
    <div style="padding-top:2.5rem;">
        <div style="font-family:'IBM Plex Mono',monospace;font-size:0.6rem;color:#3a4558;
                    text-transform:uppercase;letter-spacing:0.18em;margin-bottom:0.8rem;">
            Platform Stats
        </div>
        <div class="ohlc-row">
            <div class="ohlc-box"><div class="ohlc-label">Indicators</div><div class="ohlc-value" style="color:#00d68f;">9+</div></div>
            <div class="ohlc-box"><div class="ohlc-label">Strategies</div><div class="ohlc-value" style="color:#00d68f;">9</div></div>
        </div>
        <div class="ohlc-row">
            <div class="ohlc-box"><div class="ohlc-label">Pages</div><div class="ohlc-value" style="color:#00d68f;">5</div></div>
            <div class="ohlc-box"><div class="ohlc-label">Cost</div><div class="ohlc-value" style="color:#00d68f;">$0</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="font-family:IBM Plex Mono,monospace;font-size:0.6rem;color:#3a4558;text-transform:uppercase;letter-spacing:0.18em;margin:1.2rem 0 0.5rem 0;">Market Status</div>', unsafe_allow_html=True)
    for exchange, status in {"NYSE":"OPEN","NASDAQ":"OPEN","CRYPTO":"24/7"}.items():
        c1, c2 = st.columns(2)
        c1.markdown(f'<div style="font-family:IBM Plex Mono,monospace;font-size:0.7rem;color:#3a4558;padding:0.3rem 0;">{exchange}</div>', unsafe_allow_html=True)
        c2.markdown(f'<div style="font-family:IBM Plex Mono,monospace;font-size:0.7rem;color:#00d68f;padding:0.3rem 0;">● {status}</div>', unsafe_allow_html=True)

# ── Quick start ───────────────────────────────────────────────────────────────
st.markdown('<div class="price-divider" style="margin-top:2rem;">QUICK START</div>', unsafe_allow_html=True)

q1, q2 = st.columns([2, 1])

with q1:
    steps = [
        ("01","#00d68f","BACKTEST",   "Pick any stock + strategy → Run Backtest → See returns, drawdown, win rate"),
        ("02","#00d68f","INDICATORS", "Choose up to 3 indicators → Set your buy/sell conditions → Run test"),
        ("03","#ff4757","REPLAY",     "Pick a stock and date → Step through candles → Practice your trades"),
        ("04","#00d68f","ANALYSIS",   "Enter any ticker → Get AI financial breakdown and investment insights"),
        ("05","#00d68f","ASSISTANT",  "Ask anything — strategy advice, result explanations, trading concepts"),
    ]
    for num, color, title, desc in steps:
        st.markdown(f"""
        <div style="padding:0.8rem 0;border-bottom:1px solid #1c2333;">
            <div style="font-family:'IBM Plex Mono',monospace;font-size:0.72rem;font-weight:700;
                        color:{color};letter-spacing:0.12em;margin-bottom:0.2rem;">
                <span style="opacity:0.3;margin-right:0.8rem;">{num}</span>{title}
            </div>
            <div style="font-size:0.8rem;color:#3a4558;">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

with q2:
    st.markdown('<div style="background:#0d1117;border:1px solid #1c2333;border-radius:6px;padding:1.2rem;"><div style="font-family:IBM Plex Mono,monospace;font-size:0.6rem;color:#3a4558;text-transform:uppercase;letter-spacing:0.18em;margin-bottom:1rem;">Indicators Available</div>', unsafe_allow_html=True)
    for name in ["SMA / EMA / WMA","RSI","Stochastic RSI","MACD","Bollinger Bands","SuperTrend","Ichimoku Cloud","VWAP","OBV"]:
        st.markdown(f'<div style="padding:0.35rem 0;border-bottom:1px solid #1c2333;font-family:IBM Plex Mono,monospace;font-size:0.7rem;color:#3a4558;"><span style="color:#00d68f;margin-right:0.6rem;">▸</span>{name}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-top:3rem;padding:1.2rem 0;border-top:1px solid #1c2333;">
    <div style="font-family:'IBM Plex Mono',monospace;font-size:0.65rem;color:#3a4558;">
        <span style="color:#00d68f;">11</span><span style="color:#ff4757;">%</span>
        &nbsp;·&nbsp; Free · Open Source · Educational Use Only · Rishi Gopinath
    </div>
    <div style="font-family:'IBM Plex Mono',monospace;font-size:0.65rem;color:#3a4558;margin-top:0.3rem;">
         Not financial advice. Past performance ≠ future results.
    </div>
</div>
""", unsafe_allow_html=True)
