import streamlit as st
import sys, os
from datetime import datetime
import pytz
sys.path.insert(0, os.path.dirname(__file__))
from utils.styles import SHARED_CSS

st.set_page_config(page_title="11% - Trading Platform", page_icon="$", layout="wide", initial_sidebar_state="collapsed")
st.markdown(SHARED_CSS, unsafe_allow_html=True)

st.markdown("""
<style>
@keyframes fadeUp   { from{opacity:0;transform:translateY(24px)}to{opacity:1;transform:translateY(0)} }
@keyframes fadeIn   { from{opacity:0}to{opacity:1} }
@keyframes pulse    { 0%,100%{opacity:1}50%{opacity:0.5} }
@keyframes scanline { 0%{top:-100%}100%{top:100%} }
.hero-title  { animation:fadeUp 0.7s ease both; }
.hero-sub    { animation:fadeUp 0.7s 0.15s ease both; }
.hero-ctas   { animation:fadeUp 0.7s 0.28s ease both; }
.tape-wrap   { animation:fadeIn 0.5s ease both; }
.stat-grid   { animation:fadeUp 0.6s 0.1s ease both; }
.feat-card   { animation:fadeUp 0.5s ease both; }
.hero-candles { animation:fadeIn 1s ease both; }
.live-dot {
    display:inline-block; width:7px; height:7px; border-radius:50%;
    background:#00e676; margin-right:6px;
    animation:pulse 1.8s ease-in-out infinite;
    box-shadow:0 0 6px rgba(0,230,118,0.6);
}
.screen-card {
    background:#0c1018; border:1px solid #1a2235;
    border-radius:12px; overflow:hidden; position:relative;
}
.screen-card::after {
    content:''; position:absolute; left:0;right:0;height:60px;
    background:linear-gradient(180deg,rgba(0,230,118,0.03),transparent);
    animation:scanline 3s linear infinite; pointer-events:none;
}
.screen-header {
    background:#08100d; border-bottom:1px solid #1a2235;
    padding:0.5rem 1rem; display:flex;align-items:center;gap:0.4rem;
    font-family:'IBM Plex Mono',monospace;font-size:0.6rem;color:#3a4a5e;
}
.dot-red  {width:10px;height:10px;border-radius:50%;background:#ff3d57;}
.dot-yel  {width:10px;height:10px;border-radius:50%;background:#ffd166;}
.dot-grn  {width:10px;height:10px;border-radius:50%;background:#00e676;}
.step-num {
    font-family:'Bebas Neue',sans-serif;font-size:4rem;
    color:#1a2235;line-height:1;margin-bottom:0.3rem; transition:color 0.3s;
}
.step-card:hover .step-num { color:#2a3550; }
.step-card:hover { border-color:#2a3550 !important; }
.glow-border { position:relative; }
.glow-border::before {
    content:''; position:absolute;inset:-1px;
    background:linear-gradient(135deg,rgba(0,230,118,0.3),transparent,rgba(77,166,255,0.2));
    border-radius:inherit; z-index:-1; opacity:0; transition:opacity 0.3s;
}
.glow-border:hover::before { opacity:1; }
</style>
""", unsafe_allow_html=True)


def get_market_status(market_name):
    now_utc = datetime.now(pytz.utc)
    time_ny = now_utc.astimezone(pytz.timezone("America/New_York"))
    if market_name == "Crypto":
        return "24/7", "#00e676", True
    if time_ny.weekday() >= 5:
        return "CLOSED", "#ff3d57", False
    s = time_ny.replace(hour=9,  minute=30, second=0, microsecond=0)
    e = time_ny.replace(hour=16, minute=0,  second=0, microsecond=0)
    if s <= time_ny <= e:
        return "OPEN", "#00e676", True
    return "CLOSED", "#ff3d57", False


def market_row(label, status, color):
    dot = "&#9679;" if status != "CLOSED" else "&#9675;"
    return (
        '<div style="display:flex;justify-content:space-between;align-items:center;'
        'padding:0.45rem 1rem;border-top:1px solid #1a2235;">'
        '<span style="font-family:IBM Plex Mono,monospace;font-size:0.7rem;color:#8896ab;">' + label + '</span>'
        '<span style="font-family:IBM Plex Mono,monospace;font-size:0.65rem;color:' + color + ';">' + dot + ' ' + status + '</span>'
        '</div>'
    )


# -- Navbar --
st.markdown('<div class="nb"><div class="nb-brand"><span class="g">11</span><span class="r">%</span></div><div class="nb-links">', unsafe_allow_html=True)
nc = st.columns([1,1,1,1,1,1,1])
with nc[0]: st.page_link("app.py",                    label="Home")
with nc[1]: st.page_link("pages/1_Backtest.py",       label="Backtest")
with nc[2]: st.page_link("pages/2_Indicator_Test.py", label="Indicators")
with nc[3]: st.page_link("pages/3_Replay.py",         label="Replay")
with nc[4]: st.page_link("pages/4_Analysis.py",       label="Analysis")
with nc[5]: st.page_link("pages/6_Earnings.py",       label="Earnings")
with nc[6]: st.page_link("pages/5_Assistant.py",      label="Coach")
st.markdown('<div></div><div class="nb-tag"><span class="live-dot"></span>LIVE DATA</div></div>', unsafe_allow_html=True)

# -- Ticker tape --
TICKERS = ["AAPL","TSLA","SPY","NVDA","MSFT","AMZN","BTC-USD","META","GOOGL","AMD","NFLX","JPM","V","WMT","TSM","QQQ","GLD","PLTR","COIN","SMCI"]

@st.cache_data(ttl=3600)
def get_tape(tickers):
    import yfinance as yf
    out = []
    for s in tickers:
        try:
            h = yf.Ticker(s).history(period="2d")
            if len(h) >= 2:
                p = float(h["Close"].iloc[-2])
                c = float(h["Close"].iloc[-1])
                chg = ((c - p) / p) * 100
                up = chg >= 0
                out.append((s, f"{c:,.2f}", f"{chg:+.2f}%", "^" if up else "v", "t-up" if up else "t-dn"))
        except:
            pass
    return out

tape = get_tape(tuple(TICKERS))
if tape:
    items = "".join(
        '<span class="ticker-item"><span class="t-sym">' + s + '</span>'
        '<span class="' + cls + '">' + p + ' ' + a + ' ' + ch + '</span></span>'
        for s, p, ch, a, cls in tape
    ) * 2
    st.markdown('<div class="ticker-wrap tape-wrap"><div class="ticker-tape">' + items + '</div></div>', unsafe_allow_html=True)

# -- Hero --
hero_l, hero_r = st.columns([5, 4])

with hero_l:
    candle_data = [
        (38,"#ff3d57"),(44,"#00e676"),(28,"#ff3d57"),(52,"#00e676"),(60,"#00e676"),
        (30,"#ff3d57"),(62,"#00e676"),(70,"#00e676"),(38,"#ff3d57"),(72,"#00e676"),
        (78,"#00e676"),(46,"#ff3d57"),(80,"#00e676"),(74,"#00e676"),(82,"#00e676"),
        (68,"#ff3d57"),(85,"#00e676"),(79,"#ff3d57"),(88,"#00e676"),(92,"#00e676"),
    ]
    candles_html = '<div style="display:flex;align-items:flex-end;gap:3px;height:72px;margin-bottom:0.5rem;" class="hero-candles">'
    for i, (h, col) in enumerate(candle_data):
        ht = max(8, h * 0.7)
        delay = i * 0.04
        candles_html += (
            '<div style="width:10px;height:' + str(ht) + 'px;background:' + col +
            ';border-radius:1.5px;animation:fadeUp 0.4s ' + f"{delay:.2f}" + 's ease both;opacity:0.7;"></div>'
        )
    candles_html += "</div>"

    st.markdown(
        '<div style="padding:3rem 0 2rem 0;">'
        + candles_html +
        '<div class="hero-title" style="font-family:\'Bebas Neue\',sans-serif;font-size:6.5rem;line-height:0.85;letter-spacing:0.02em;margin-bottom:1.6rem;">'
        '<span style="color:#00e676;">TRADE</span><br>'
        '<span style="color:#eef2f7;">SMARTER</span><br>'
        '<span style="color:#ff3d57;">NOT HARDER</span>'
        '</div>'
        '<div class="hero-sub" style="font-size:1rem;color:#8896ab;max-width:480px;line-height:1.85;margin-bottom:2rem;">'
        'A professional trading platform for learners. Backtest real strategies, '
        'study 15+ indicators, replay historical charts bar by bar, '
        'and get AI analysis - completely free.'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown('<div class="hero-ctas">', unsafe_allow_html=True)
    cta1, cta2, cta3 = st.columns(3)
    with cta1: st.page_link("pages/1_Backtest.py",  label="Backtest ->")
    with cta2: st.page_link("pages/3_Replay.py",    label="Replay ->")
    with cta3: st.page_link("pages/5_Assistant.py", label="AI Coach ->")
    st.markdown("</div>", unsafe_allow_html=True)

with hero_r:
    nyse_status, nyse_color, _ = get_market_status("NYSE")
    nas_status,  nas_color,  _ = get_market_status("NASDAQ")
    cme_status,  cme_color,  _ = get_market_status("CME Futures")
    cry_status,  cry_color,  _ = get_market_status("Crypto")

    sp_pts = [40,45,42,50,48,55,52,58,54,62,60,65,63,70,68,75,72,78,76,82]
    sp_max, sp_min = max(sp_pts), min(sp_pts)
    sp_range = sp_max - sp_min + 1
    sw, sh = 280, 60
    coords_list = []
    for i, p in enumerate(sp_pts):
        x = (i / (len(sp_pts) - 1)) * sw
        y = sh - ((p - sp_min) / sp_range * sh * 0.85 + sh * 0.07)
        coords_list.append(f"{x:.1f},{y:.1f}")
    sp_coords = " ".join(coords_list)

    sparkline = (
        '<svg width="' + str(sw) + '" height="' + str(sh) + '" style="overflow:visible;">'
        '<defs><linearGradient id="spGrad" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0%" stop-color="#00e676" stop-opacity="0.3"/>'
        '<stop offset="100%" stop-color="#00e676" stop-opacity="0"/>'
        '</linearGradient></defs>'
        '<polyline points="' + sp_coords + '" fill="none" stroke="#00e676" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>'
        '<polygon points="' + sp_coords + ' ' + str(sw) + ',' + str(sh) + ' 0,' + str(sh) + '" fill="url(#spGrad)"/>'
        '</svg>'
    )

    market_rows_html = (
        market_row("NYSE",        nyse_status, nyse_color) +
        market_row("NASDAQ",      nas_status,  nas_color)  +
        market_row("CME Futures", cme_status,  cme_color)  +
        market_row("Crypto",      cry_status,  cry_color)
    )

    screen_html = (
        '<div style="padding:2.5rem 0 1rem 0;" class="stat-grid">'
        '<div class="screen-card" style="margin-bottom:1rem;animation:fadeUp 0.6s 0.2s ease both;opacity:0;">'
        '<div class="screen-header">'
        '<div class="dot-red"></div><div class="dot-yel"></div><div class="dot-grn"></div>'
        '<span style="margin-left:0.5rem;">AAPL &middot; LIVE CHART PREVIEW</span>'
        '</div>'
        '<div style="padding:1rem 1.2rem;">'
        '<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:0.6rem;">'
        '<div>'
        '<div style="font-family:\'Bebas Neue\',sans-serif;font-size:2rem;color:#eef2f7;line-height:1;">AAPL</div>'
        '<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.6rem;color:#3a4a5e;">Apple Inc. &middot; NASDAQ</div>'
        '</div>'
        '<div style="text-align:right;">'
        '<div style="font-family:\'IBM Plex Mono\',monospace;font-size:1.1rem;color:#eef2f7;">$195.40</div>'
        '<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.68rem;color:#00e676;">&#9650; +2.34%</div>'
        '</div></div>'
        + sparkline +
        '<div style="display:flex;justify-content:space-between;margin-top:0.6rem;font-family:\'IBM Plex Mono\',monospace;font-size:0.6rem;color:#3a4a5e;">'
        '<span>+18.4% YTD</span><span>Vol 78.2M</span><span>P/E 29.1x</span><span>52W: $164-$199</span>'
        '</div></div></div>'
        '<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:1rem;animation:fadeUp 0.6s 0.3s ease both;opacity:0;">'
        '<div style="background:#0c1018;border:1px solid #1a2235;border-radius:8px;padding:1.1rem;text-align:center;">'
        '<div style="font-family:\'Bebas Neue\',sans-serif;font-size:2.4rem;color:#00e676;line-height:1;">15</div>'
        '<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.52rem;color:#3a4a5e;text-transform:uppercase;letter-spacing:0.15em;margin-top:0.2rem;">Indicators</div>'
        '</div>'
        '<div style="background:#0c1018;border:1px solid #1a2235;border-radius:8px;padding:1.1rem;text-align:center;">'
        '<div style="font-family:\'Bebas Neue\',sans-serif;font-size:2.4rem;color:#00e676;line-height:1;">9</div>'
        '<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.52rem;color:#3a4a5e;text-transform:uppercase;letter-spacing:0.15em;margin-top:0.2rem;">Strategies</div>'
        '</div>'
        '<div style="background:#0c1018;border:1px solid #1a2235;border-radius:8px;padding:1.1rem;text-align:center;">'
        '<div style="font-family:\'Bebas Neue\',sans-serif;font-size:2.4rem;color:#00e676;line-height:1;">7</div>'
        '<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.52rem;color:#3a4a5e;text-transform:uppercase;letter-spacing:0.15em;margin-top:0.2rem;">Pages</div>'
        '</div>'
        '<div style="background:#0c1018;border:1px solid #1a2235;border-radius:8px;padding:1.1rem;text-align:center;">'
        '<div style="font-family:\'Bebas Neue\',sans-serif;font-size:2.4rem;color:#00e676;line-height:1;">$0</div>'
        '<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.52rem;color:#3a4a5e;text-transform:uppercase;letter-spacing:0.15em;margin-top:0.2rem;">Forever Free</div>'
        '</div></div>'
        '<div style="background:#0c1018;border:1px solid #1a2235;border-radius:8px;overflow:hidden;animation:fadeUp 0.6s 0.4s ease both;opacity:0;">'
        '<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.52rem;color:#3a4a5e;text-transform:uppercase;letter-spacing:0.2em;padding:0.7rem 1rem 0.4rem;">Market Status</div>'
        + market_rows_html +
        '</div></div>'
    )
    st.markdown(screen_html, unsafe_allow_html=True)

# -- Features --
st.markdown('<div class="divider">Platform</div>', unsafe_allow_html=True)
features = [
    ("[bar]",    "Backtest",   "Test any strategy on years of real data. Returns, alpha, drawdown, Sharpe, win rate.",         "pages/1_Backtest.py"),
    ("[search]", "Indicators", "Build custom strategies from 15 indicators with AND/OR combo logic and instant backtesting.",  "pages/2_Indicator_Test.py"),
    (">",        "Replay",     "Step through historical bars one at a time with 13+ overlays and 5 sub-charts. Trade live.",   "pages/3_Replay.py"),
    ("[brain]",  "Analysis",   "Full fundamental + AI breakdown. Financials, valuation, risks, and a personalised verdict.",   "pages/4_Analysis.py"),
    ("[cal]",    "Earnings",   "How did a stock react to every past earnings? Day-of move, pre-run, post follow-through.",     "pages/6_Earnings.py"),
    ("[chat]",   "AI Coach",   "Ask anything in plain English. Your coach explains results, strategies, and concepts.",        "pages/5_Assistant.py"),
]
fc = st.columns(6)
for col, (icon, title, desc, link) in zip(fc, features):
    col.markdown(
        '<div class="feat-card glow-border">'
        '<div class="feat-icon">' + icon + '</div>'
        '<div class="feat-title">' + title + '</div>'
        '<div class="feat-desc">' + desc + '</div>'
        '</div>',
        unsafe_allow_html=True
    )
    col.page_link(link, label="Open ->")

# -- Indicators showcase --
st.markdown('<div class="divider" style="margin-top:2.5rem;">15 Indicators Available</div>', unsafe_allow_html=True)
ind_groups = [
    ("Trend",              "#4da6ff", ["SMA","EMA","WMA","Hull MA","SuperTrend","Ichimoku","Parabolic SAR"]),
    ("Momentum",           "#b388ff", ["RSI","Stochastic RSI","MACD","CCI","Williams %R"]),
    ("Volatility + Volume","#ffd166", ["Bollinger Bands","Keltner Channels","Donchian Channels","VWAP","OBV"]),
]
ig_cols = st.columns(3)
for col, (cat, color, inds) in zip(ig_cols, ind_groups):
    tags = "".join(
        '<span style="display:inline-block;font-family:IBM Plex Mono,monospace;font-size:0.65rem;'
        'padding:3px 10px;border-radius:4px;background:' + color + '12;color:' + color + ';'
        'border:1px solid ' + color + '25;margin:3px 3px 3px 0;">' + ind + '</span>'
        for ind in inds
    )
    col.markdown(
        '<div style="background:#0c1018;border:1px solid #1a2235;border-radius:10px;padding:1.3rem;height:100%;">'
        '<div style="font-family:IBM Plex Mono,monospace;font-size:0.6rem;color:' + color + ';'
        'text-transform:uppercase;letter-spacing:0.18em;margin-bottom:0.9rem;">' + cat + '</div>'
        '<div>' + tags + '</div>'
        '</div>',
        unsafe_allow_html=True
    )

# -- How it works --
st.markdown('<div class="divider" style="margin-top:2.5rem;">How It Works</div>', unsafe_allow_html=True)
hw = st.columns(5)
steps = [
    ("01","Pick a Stock",    "Enter any ticker - stocks, ETFs, or crypto. Live data from Yahoo Finance."),
    ("02","Choose Strategy", "9 pre-built strategies or build your own with 15 indicators."),
    ("03","Run Backtest",    "Set date range and capital. Results computed in seconds."),
    ("04","Study Results",   "Return, alpha, drawdown, Sharpe - all explained in plain English."),
    ("05","Ask the Coach",   "The AI coach explains what the numbers mean and how to improve."),
]
for col, (num, title, desc) in zip(hw, steps):
    col.markdown(
        '<div class="step-card" style="padding:1.2rem 0.8rem;background:#0c1018;border:1px solid #1a2235;border-radius:10px;transition:border-color 0.2s;">'
        '<div class="step-num">' + num + '</div>'
        '<div style="font-family:IBM Plex Mono,monospace;font-size:0.68rem;color:#eef2f7;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.4rem;">' + title + '</div>'
        '<div style="font-size:0.8rem;color:#3a4a5e;line-height:1.65;">' + desc + '</div>'
        '</div>',
        unsafe_allow_html=True
    )

# -- Strategies + Concepts --
st.markdown('<div class="divider" style="margin-top:2.5rem;">Strategies + Concepts</div>', unsafe_allow_html=True)
sl, sr = st.columns(2)
with sl:
    st.markdown('<div style="font-family:IBM Plex Mono,monospace;font-size:0.58rem;color:#3a4a5e;text-transform:uppercase;letter-spacing:0.18em;margin-bottom:0.8rem;">9 Pre-built Strategies</div>', unsafe_allow_html=True)
    for name, tag, desc in [
        ("SMA Crossover",    "Trend",    "Classic MA cross. Fast crosses slow = buy."),
        ("EMA Crossover",    "Trend",    "Like SMA but reacts faster to recent moves."),
        ("RSI",              "Mean Rev", "Buy oversold <30, sell overbought >70."),
        ("MACD",             "Momentum", "Momentum crossover. Catches accelerating trends."),
        ("Bollinger Bands",  "Mean Rev", "Buy lower band, sell upper - mean reversion."),
        ("SuperTrend",       "Trend",    "ATR-based with clear green/red direction signal."),
        ("RSI + BB",         "Combo",    "Both must confirm - fewer but higher quality trades."),
        ("EMA + RSI Filter", "Combo",    "EMA direction + RSI momentum confirmation."),
        ("MACD + SuperTrend","Combo",    "Dual confirmation. Very patient, high conviction."),
    ]:
        tc = "#4da6ff" if tag == "Trend" else ("#b388ff" if tag == "Mean Rev" else ("#ffd166" if tag == "Momentum" else "#00e676"))
        sl.markdown(
            '<div class="row-item">'
            '<span class="tag" style="background:' + tc + '12;color:' + tc + ';border:1px solid ' + tc + '25;flex-shrink:0;">' + tag + '</span>'
            '<div><div style="font-size:0.82rem;color:#eef2f7;">' + name + '</div>'
            '<div style="font-size:0.72rem;color:#3a4a5e;margin-top:0.1rem;">' + desc + '</div></div>'
            '</div>',
            unsafe_allow_html=True
        )
with sr:
    st.markdown('<div style="font-family:IBM Plex Mono,monospace;font-size:0.58rem;color:#3a4a5e;text-transform:uppercase;letter-spacing:0.18em;margin-bottom:0.8rem;">Key Concepts Explained</div>', unsafe_allow_html=True)
    for term, defn in [
        ("Backtesting",          "Running a strategy on historical data to measure what would have happened."),
        ("Max Drawdown",         "Worst peak-to-trough loss. Tells you how much pain to expect."),
        ("Sharpe Ratio",         "Return divided by volatility. Above 1.0 is decent, above 2.0 is strong."),
        ("Alpha",                "Return above buy and hold. Positive = you actually added value."),
        ("Win Rate",             "% of trades that were profitable. Meaningless without avg win/loss size."),
        ("ATR",                  "Average True Range - how far a stock moves per day on average."),
        ("Support / Resistance", "Levels where price historically reverses. Foundation of technical analysis."),
        ("Volume",               "Number of shares traded. Rising price + rising volume confirms a trend."),
        ("Mean Reversion",       "The tendency of price to return to its historical average after extremes."),
    ]:
        sr.markdown(
            '<div class="row-item"><div>'
            '<div style="font-family:IBM Plex Mono,monospace;font-size:0.72rem;color:#00e676;margin-bottom:0.2rem;">' + term + '</div>'
            '<div style="font-size:0.79rem;color:#3a4a5e;line-height:1.6;">' + defn + '</div>'
            '</div></div>',
            unsafe_allow_html=True
        )

# -- FAQ --
st.markdown('<div class="divider" style="margin-top:2rem;">FAQ</div>', unsafe_allow_html=True)
fqa, fqb = st.columns(2)
faqs = [
    ("Is this real trading?",                     "No - fully simulated. No real money. Data from Yahoo Finance. For education only."),
    ("How accurate is the backtest?",             "Indicative, not guaranteed. Assumes closing-price fills with no slippage, spread, or tax."),
    ("Do I need to code?",                        "No. Everything is point-and-click. Open source Python/Streamlit if you want to extend it."),
    ("How do I enable AI?",                       "Add your Gemini API key to Streamlit Secrets as GEMINI_API_KEY. Free tier is enough."),
    ("Why can't past performance predict future?","Markets change. A strategy that crushed a bull market may fail in a bear market."),
    ("What data does it use?",                    "Yahoo Finance via yfinance - years of daily OHLCV for stocks, ETFs, and crypto."),
]
for i, (q, a) in enumerate(faqs):
    with (fqa if i % 2 == 0 else fqb).expander(q):
        st.markdown('<div style="font-size:0.84rem;color:#8896ab;line-height:1.75;padding:0.2rem 0;">' + a + '</div>', unsafe_allow_html=True)

# -- Footer --
st.markdown("""
<div style="margin-top:3rem;padding:1.5rem 0;border-top:1px solid #1a2235;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:0.5rem;">
    <div style="font-family:'IBM Plex Mono',monospace;font-size:0.65rem;color:#3a4a5e;">
        <span style="color:#00e676;font-family:'Bebas Neue',sans-serif;font-size:1.1rem;">11</span><span style="color:#ff3d57;font-family:'Bebas Neue',sans-serif;font-size:1.1rem;">%</span>
        &nbsp;&middot;&nbsp; Built by Rishi Gopinath &nbsp;&middot;&nbsp; Free &nbsp;&middot;&nbsp; Open Source
    </div>
    <div style="font-family:'IBM Plex Mono',monospace;font-size:0.58rem;color:#1a2235;">
        Not financial advice &middot; Educational use only &middot; Past performance does not predict future results
    </div>
</div>
""", unsafe_allow_html=True)
