import streamlit as st
import sys, os
from datetime import datetime
import pytz
sys.path.insert(0, os.path.dirname(__file__))
from utils.styles import SHARED_CSS, LOGO_IMG
from utils.nav import navbar

st.set_page_config(page_title="11% · Trade Smarter", page_icon="$", layout="wide", initial_sidebar_state="collapsed")
st.markdown(SHARED_CSS, unsafe_allow_html=True)
st.markdown("""
<style>
@keyframes fadeUp   { from{opacity:0;transform:translateY(20px)} to{opacity:1;transform:translateY(0)} }
@keyframes fadeIn   { from{opacity:0} to{opacity:1} }
@keyframes tickerScroll { 0%{transform:translateX(0)} 100%{transform:translateX(-50%)} }

.ticker-outer {
    width:100%; overflow:hidden; background:#08100d;
    border:1px solid #1a2235; border-radius:6px; height:32px;
    display:flex; align-items:center;
    margin-bottom:1.6rem; position:relative;
}
.ticker-outer::before,.ticker-outer::after {
    content:''; position:absolute; top:0; bottom:0; width:60px; z-index:2; pointer-events:none;
}
.ticker-outer::before { left:0; background:linear-gradient(90deg,#08100d,transparent); }
.ticker-outer::after  { right:0; background:linear-gradient(-90deg,#08100d,transparent); }
.ticker-track { display:flex; white-space:nowrap; animation:tickerScroll 38s linear infinite; }
.ticker-item  {
    display:inline-flex; align-items:center; gap:6px; padding:0 20px;
    border-right:1px solid #1a2235;
    font-family:'IBM Plex Mono',monospace; font-size:0.67rem; flex-shrink:0;
}
.t-sym{color:#3a4a5e;font-weight:700} .t-up{color:#00e676} .t-dn{color:#ff3d57}

.screen-card { background:#0c1018; border:1px solid #1a2235; border-radius:12px; overflow:hidden; }
.sc-card { background:#0c1018; border:1px solid #1a2235; border-radius:12px; overflow:hidden; }
.sc-card-hdr { padding:0.8rem 1.2rem; border-bottom:1px solid #1a2235; background:#08100d;
    font-family:'IBM Plex Mono',monospace; font-size:0.52rem; text-transform:uppercase;
    letter-spacing:0.2em; color:#3a4a5e; }
.strat-row { display:flex; align-items:flex-start; gap:0.8rem; padding:0.7rem 1.1rem;
    border-bottom:1px solid #0d1117; transition:background 0.15s; }
.strat-row:last-child{border-bottom:none} .strat-row:hover{background:rgba(255,255,255,0.015)}
.strat-tag { display:inline-block; font-family:'IBM Plex Mono',monospace; font-size:0.48rem;
    text-transform:uppercase; letter-spacing:0.1em; padding:2px 6px; border-radius:3px;
    white-space:nowrap; flex-shrink:0; margin-top:3px; }
.strat-name{font-size:0.8rem;color:#eef2f7;font-weight:500;margin-bottom:0.12rem}
.strat-desc{font-size:0.7rem;color:#3a4a5e;line-height:1.5}
.concept-row { display:grid; grid-template-columns:160px 1fr; gap:0.8rem;
    align-items:baseline; padding:0.7rem 1.1rem; border-bottom:1px solid #0d1117; transition:background 0.15s; }
.concept-row:last-child{border-bottom:none} .concept-row:hover{background:rgba(255,255,255,0.015)}
.concept-term{font-family:'IBM Plex Mono',monospace;font-size:0.68rem;color:#00e676;font-weight:600}
.concept-def{font-size:0.76rem;color:#3a4a5e;line-height:1.6}
.step-num { font-family:'Bebas Neue',sans-serif; font-size:3.5rem; color:#1a2235; line-height:1; }
</style>
""", unsafe_allow_html=True)

navbar()

# ── Helpers ────────────────────────────────────────────────────────────────────
def get_market_status(name):
    now = datetime.now(pytz.utc).astimezone(pytz.timezone("America/New_York"))
    if name == "Crypto": return "24/7", "#00e676"
    if now.weekday() >= 5: return "CLOSED", "#ff3d57"
    s = now.replace(hour=9,  minute=30, second=0, microsecond=0)
    e = now.replace(hour=16, minute=0,  second=0, microsecond=0)
    return ("OPEN","#00e676") if s <= now <= e else ("CLOSED","#ff3d57")

def mkt_row(label, status, color):
    return (
        '<div style="display:flex;justify-content:space-between;align-items:center;'
        'padding:0.4rem 1rem;border-top:1px solid #1a2235;">'
        '<span style="font-family:IBM Plex Mono,monospace;font-size:0.68rem;color:#8896ab;">' + label + '</span>'
        '<span style="font-family:IBM Plex Mono,monospace;font-size:0.62rem;color:' + color + ';">&#11044; ' + status + '</span>'
        '</div>'
    )

# ── Welcome banner (logged-in users only) ─────────────────────────────────────
user_email = st.session_state.get("user_email", "")
if user_email:
    user_name = user_email.split("@")[0].replace(".", " ").replace("_", " ").title()
    st.markdown(
        '<div style="background:linear-gradient(135deg,rgba(0,230,118,0.06),rgba(0,230,118,0.02));'
        'border:1px solid rgba(0,230,118,0.2);border-radius:10px;'
        'padding:0.85rem 1.4rem;margin-bottom:1.2rem;'
        'display:flex;align-items:center;justify-content:space-between;">'
        '<div style="display:flex;align-items:center;gap:0.8rem;">'
        '<div style="width:34px;height:34px;border-radius:50%;background:rgba(0,230,118,0.12);'
        'border:1px solid rgba(0,230,118,0.3);display:flex;align-items:center;justify-content:center;'
        'font-family:IBM Plex Mono,monospace;font-size:0.7rem;font-weight:700;color:#00e676;">'
        + user_name[0].upper() +
        '</div>'
        '<div>'
        '<div style="font-family:IBM Plex Mono,monospace;font-size:0.58rem;color:#3a4a5e;'
        'text-transform:uppercase;letter-spacing:0.15em;margin-bottom:0.15rem;">Welcome back</div>'
        '<div style="font-size:1.05rem;font-weight:600;color:#eef2f7;">Hi, ' + user_name + ' 👋</div>'
        '</div></div>'
        '<div style="font-family:IBM Plex Mono,monospace;font-size:0.55rem;color:#3a4a5e;">'
        'Ready to trade smarter?'
        '</div></div>',
        unsafe_allow_html=True
    )

# ── Ticker tape ────────────────────────────────────────────────────────────────
TICKERS = ["AAPL","TSLA","SPY","NVDA","MSFT","AMZN","BTC-USD","META","GOOGL","AMD",
           "NFLX","JPM","V","WMT","TSM","QQQ","GLD","PLTR","COIN","SMCI"]

@st.cache_data(ttl=3600)
def get_tape(tickers):
    import yfinance as yf
    out = []
    for s in tickers:
        try:
            h = yf.Ticker(s).history(period="2d")
            if len(h) >= 2:
                p, c = float(h["Close"].iloc[-2]), float(h["Close"].iloc[-1])
                chg = ((c - p) / p) * 100
                out.append((s, f"{c:,.2f}", f"{chg:+.2f}%", "▲" if chg >= 0 else "▼", "t-up" if chg >= 0 else "t-dn"))
        except: pass
    return out

tape = get_tape(tuple(TICKERS))
if tape:
    items = "".join(
        '<span class="ticker-item">'
        '<span class="t-sym">' + s + '</span>'
        '<span class="' + cls + '">' + p + ' ' + a + ' ' + ch + '</span>'
        '</span>'
        for s, p, ch, a, cls in tape
    )
    st.markdown('<div class="ticker-outer"><div class="ticker-track">' + items + items + '</div></div>',
                unsafe_allow_html=True)

# ── Hero ───────────────────────────────────────────────────────────────────────
hero_l, hero_r = st.columns([5, 4])

with hero_l:
    bars_html = "".join(
        '<div style="width:10px;height:' + str(max(8,h)) + 'px;background:' + c + ';'
        'border-radius:2px;opacity:0.75;"></div>'
        for h, c in [
            (38,"#ff3d57"),(44,"#00e676"),(28,"#ff3d57"),(52,"#00e676"),(60,"#00e676"),
            (30,"#ff3d57"),(62,"#00e676"),(70,"#00e676"),(38,"#ff3d57"),(72,"#00e676"),
            (78,"#00e676"),(46,"#ff3d57"),(80,"#00e676"),(74,"#00e676"),(82,"#00e676"),
            (68,"#ff3d57"),(85,"#00e676"),(79,"#ff3d57"),(88,"#00e676"),(92,"#00e676"),
        ]
    )
    st.markdown(
        '<div style="padding:2rem 0 1.5rem;">'
        '<div style="display:flex;align-items:flex-end;gap:3px;height:64px;margin-bottom:0.6rem;">'
        + bars_html +
        '</div>'
        '<div style="font-family:\'Bebas Neue\',sans-serif;font-size:6rem;line-height:0.88;'
        'letter-spacing:0.02em;margin-bottom:1.4rem;">'
        '<span style="color:#00e676;">TRADE</span><br>'
        '<span style="color:#eef2f7;">SMARTER</span><br>'
        '<span style="color:#ff3d57;">NOT HARDER</span>'
        '</div>'
        '<div style="font-size:0.95rem;color:#8896ab;max-width:460px;line-height:1.85;margin-bottom:1.8rem;">'
        'A professional trading platform for learners. Backtest real strategies, '
        'study 15+ indicators, replay historical charts bar by bar, '
        'and get AI analysis — completely free.'
        '</div></div>',
        unsafe_allow_html=True
    )
    c1, c2, c3 = st.columns(3)
    with c1: st.page_link("pages/1_Strategy_Lab.py", label="Strategy Lab →")
    with c2: st.page_link("pages/3_Replay.py",       label="Replay →")
    with c3: st.page_link("pages/5_Assistant.py",    label="AI Coach →")

with hero_r:
    nyse_s, nyse_c = get_market_status("NYSE")
    nas_s,  nas_c  = get_market_status("NASDAQ")
    cme_s,  cme_c  = get_market_status("CME")
    cry_s,  cry_c  = get_market_status("Crypto")

    stats_html = "".join(
        '<div style="background:#0c1018;border:1px solid #1a2235;border-radius:8px;'
        'padding:0.9rem;text-align:center;">'
        '<div style="font-family:\'Bebas Neue\',sans-serif;font-size:2rem;color:#00e676;line-height:1;">' + v + '</div>'
        '<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.48rem;color:#3a4a5e;'
        'text-transform:uppercase;letter-spacing:0.14em;margin-top:0.2rem;">' + l + '</div>'
        '</div>'
        for v, l in [("15","Indicators"), ("9","Strategies"), ("8","Pages"), ("$0","Forever Free")]
    )

    # The TV chart card header + iframe merged into ONE block
    # We render the mac-style chrome as HTML, then immediately
    # inject the TV widget via components.html right after with no gap
    st.markdown(
        '<div style="padding:1.8rem 0 0;">'
        # Chart card — mac chrome header
        '<div style="background:#0c1018;border:1px solid #1a2235;border-radius:12px 12px 0 0;'
        'border-bottom:none;padding:0.45rem 0.9rem;'
        'display:flex;align-items:center;gap:0.35rem;">'
        '<div style="width:10px;height:10px;border-radius:50%;background:#ff3d57;"></div>'
        '<div style="width:10px;height:10px;border-radius:50%;background:#ffd166;"></div>'
        '<div style="width:10px;height:10px;border-radius:50%;background:#00e676;"></div>'
        '<span style="margin-left:0.5rem;font-family:IBM Plex Mono,monospace;'
        'font-size:0.52rem;color:#3a4a5e;text-transform:uppercase;letter-spacing:0.16em;">'
        'Live Chart · TradingView</span>'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )

    # TV widget — rendered immediately below, NO gap, same border radius bottom
    st.components.v1.html("""
<style>
*{margin:0;padding:0;box-sizing:border-box;}
body{background:#0c1018;}
.tv-wrap{
    height:282px;
    width:100%;
    background:#0c1018;
    border:1px solid #1a2235;
    border-top:none;
    border-radius:0 0 12px 12px;
    overflow:hidden;
}
</style>
<div class="tv-wrap">
  <div class="tradingview-widget-container" style="height:100%;width:100%;">
    <div id="tv_home_chart" style="height:100%;width:100%;"></div>
    <script src="https://s3.tradingview.com/tv.js"></script>
    <script>
    new TradingView.widget({
      autosize: true,
      symbol: "NASDAQ:AAPL",
      interval: "D",
      timezone: "America/New_York",
      theme: "dark",
      style: "1",
      locale: "en",
      toolbar_bg: "#0c1018",
      enable_publishing: false,
      hide_side_toolbar: true,
      hide_top_toolbar: false,
      withdateranges: false,
      allow_symbol_change: true,
      save_image: false,
      container_id: "tv_home_chart",
      backgroundColor: "rgba(12,16,24,1)",
      gridColor: "rgba(26,34,53,0.4)",
      overrides: {
        "mainSeriesProperties.candleStyle.upColor":        "#00e676",
        "mainSeriesProperties.candleStyle.downColor":      "#ff3d57",
        "mainSeriesProperties.candleStyle.borderUpColor":  "#00e676",
        "mainSeriesProperties.candleStyle.borderDownColor":"#ff3d57",
        "mainSeriesProperties.candleStyle.wickUpColor":    "#00e676",
        "mainSeriesProperties.candleStyle.wickDownColor":  "#ff3d57",
        "paneProperties.background":          "#0c1018",
        "paneProperties.backgroundType":      "solid",
        "paneProperties.vertGridProperties.color": "#1a2235",
        "paneProperties.horzGridProperties.color": "#1a2235",
        "scalesProperties.textColor":         "#3a4a5e",
        "scalesProperties.lineColor":         "#1a2235"
      }
    });
    </script>
  </div>
</div>
""", height=284, scrolling=False)

    # Stats + market status
    st.markdown(
        '<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin:0.7rem 0;">'
        + stats_html +
        '</div>'
        '<div style="background:#0c1018;border:1px solid #1a2235;border-radius:8px;overflow:hidden;">'
        '<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.5rem;color:#3a4a5e;'
        'text-transform:uppercase;letter-spacing:0.18em;padding:0.6rem 1rem 0.3rem;">Market Status</div>'
        + mkt_row("NYSE",       nyse_s, nyse_c)
        + mkt_row("NASDAQ",     nas_s,  nas_c)
        + mkt_row("CME Futures",cme_s,  cme_c)
        + mkt_row("Crypto",     cry_s,  cry_c)
        + '</div>',
        unsafe_allow_html=True
    )

# ── Platform features ──────────────────────────────────────────────────────────
st.markdown('<div style="margin-top:2rem;font-family:IBM Plex Mono,monospace;font-size:0.52rem;'
            'text-transform:uppercase;letter-spacing:0.22em;color:#1a2235;'
            'border-top:1px solid #1a2235;padding-top:1.5rem;margin-bottom:1rem;">Platform</div>',
            unsafe_allow_html=True)

for col, (icon, title, desc, link) in zip(st.columns(6), [
    ("⚡","Strategy Lab",  "9 prebuilt strategies + custom signal builder with 15 indicators.","pages/1_Strategy_Lab.py"),
    ("▶","Replay",         "Step through bars one at a time. Trade without knowing the future.","pages/3_Replay.py"),
    ("🔍","Analysis",      "Full fundamental + AI breakdown. Financials, valuation, risks.","pages/4_Analysis.py"),
    ("🐋","Whale Tracker", "Flags unusual volume spikes. Large orders often precede big moves.","pages/8_Whale_Tracker.py"),
    ("〰","Monte Carlo",   "1,000 simulations showing where price could go. A probability cone.","pages/9_Monte_Carlo.py"),
    ("🤖","AI Coach",      "Ask anything in plain English. Explains strategies and concepts.","pages/5_Assistant.py"),
]):
    col.markdown(
        '<div style="background:#0c1018;border:1px solid #1a2235;border-radius:10px;'
        'padding:1.1rem;margin-bottom:0.4rem;min-height:150px;">'
        '<div style="font-size:1.3rem;margin-bottom:0.5rem;">' + icon + '</div>'
        '<div style="font-family:IBM Plex Mono,monospace;font-size:0.6rem;font-weight:600;'
        'text-transform:uppercase;letter-spacing:0.1em;color:#eef2f7;margin-bottom:0.45rem;">' + title + '</div>'
        '<div style="font-size:0.73rem;color:#3a4a5e;line-height:1.6;">' + desc + '</div>'
        '</div>',
        unsafe_allow_html=True
    )
    col.page_link(link, label="Open →")

# ── Indicators ────────────────────────────────────────────────────────────────
st.markdown('<div style="margin-top:1.5rem;font-family:IBM Plex Mono,monospace;font-size:0.52rem;'
            'text-transform:uppercase;letter-spacing:0.22em;color:#1a2235;'
            'border-top:1px solid #1a2235;padding-top:1.5rem;margin-bottom:1rem;">15 Indicators Available</div>',
            unsafe_allow_html=True)
for col, (cat, color, inds) in zip(st.columns(3), [
    ("Trend",              "#4da6ff", ["SMA","EMA","WMA","Hull MA","SuperTrend","Ichimoku","Parabolic SAR"]),
    ("Momentum",           "#b388ff", ["RSI","Stochastic RSI","MACD","CCI","Williams %R"]),
    ("Volatility + Volume","#ffd166", ["Bollinger Bands","Keltner Channels","Donchian Channels","VWAP","OBV"]),
]):
    tags = "".join(
        '<span style="display:inline-block;font-family:IBM Plex Mono,monospace;font-size:0.63rem;'
        'padding:3px 10px;border-radius:4px;background:' + color + '12;color:' + color + ';'
        'border:1px solid ' + color + '25;margin:3px 3px 3px 0;">' + ind + '</span>'
        for ind in inds
    )
    col.markdown(
        '<div style="background:#0c1018;border:1px solid #1a2235;border-radius:10px;padding:1.2rem;height:100%;">'
        '<div style="font-family:IBM Plex Mono,monospace;font-size:0.58rem;color:' + color + ';'
        'text-transform:uppercase;letter-spacing:0.16em;margin-bottom:0.8rem;">' + cat + '</div>'
        '<div>' + tags + '</div>'
        '</div>',
        unsafe_allow_html=True
    )

# ── How it works ──────────────────────────────────────────────────────────────
st.markdown('<div style="margin-top:1.5rem;font-family:IBM Plex Mono,monospace;font-size:0.52rem;'
            'text-transform:uppercase;letter-spacing:0.22em;color:#1a2235;'
            'border-top:1px solid #1a2235;padding-top:1.5rem;margin-bottom:1rem;">How It Works</div>',
            unsafe_allow_html=True)
for col, (num, title, desc) in zip(st.columns(5), [
    ("01","Pick a Stock",    "Enter any ticker — stocks, ETFs, or crypto. Live data from Yahoo Finance."),
    ("02","Choose Strategy", "9 pre-built strategies or build your own with 15 indicators."),
    ("03","Run Backtest",    "Set date range and capital. Results computed in seconds."),
    ("04","Study Results",   "Return, alpha, drawdown, Sharpe — all explained in plain English."),
    ("05","Ask the Coach",   "The AI coach explains what the numbers mean and how to improve."),
]):
    col.markdown(
        '<div style="padding:1.1rem 0.7rem;background:#0c1018;border:1px solid #1a2235;border-radius:10px;">'
        '<div class="step-num">' + num + '</div>'
        '<div style="font-family:IBM Plex Mono,monospace;font-size:0.66rem;color:#eef2f7;'
        'text-transform:uppercase;letter-spacing:0.09em;margin-bottom:0.35rem;">' + title + '</div>'
        '<div style="font-size:0.77rem;color:#3a4a5e;line-height:1.65;">' + desc + '</div>'
        '</div>',
        unsafe_allow_html=True
    )

# ── Strategies + Concepts ─────────────────────────────────────────────────────
st.markdown('<div style="margin-top:1.5rem;font-family:IBM Plex Mono,monospace;font-size:0.52rem;'
            'text-transform:uppercase;letter-spacing:0.22em;color:#1a2235;'
            'border-top:1px solid #1a2235;padding-top:1.5rem;margin-bottom:1rem;">Strategies + Concepts</div>',
            unsafe_allow_html=True)
sc_l, sc_r = st.columns(2)
with sc_l:
    rows = "".join(
        '<div class="strat-row">'
        '<span class="strat-tag" style="background:' + c + '18;color:' + c + ';border:1px solid ' + c + '30;">' + tag + '</span>'
        '<div><div class="strat-name">' + name + '</div><div class="strat-desc">' + desc + '</div></div>'
        '</div>'
        for name, tag, c, desc in [
            ("SMA Crossover",    "Trend",    "#4da6ff","Classic MA cross. Fast crosses slow = buy signal."),
            ("EMA Crossover",    "Trend",    "#4da6ff","Like SMA but reacts faster to recent price moves."),
            ("RSI",              "Mean Rev", "#b388ff","Buy oversold <30, sell overbought >70."),
            ("MACD",             "Momentum", "#ffd166","Momentum crossover. Catches accelerating trends."),
            ("Bollinger Bands",  "Mean Rev", "#b388ff","Buy lower band, sell upper — mean reversion."),
            ("SuperTrend",       "Trend",    "#4da6ff","ATR-based with clean green/red direction signal."),
            ("RSI + BB",         "Combo",    "#00e676","Both must confirm — fewer but higher quality trades."),
            ("EMA + RSI Filter", "Combo",    "#00e676","EMA direction with RSI momentum confirmation."),
            ("MACD + SuperTrend","Combo",    "#00e676","Dual confirmation. Very patient, high conviction."),
        ]
    )
    st.markdown('<div class="sc-card"><div class="sc-card-hdr">9 Pre-built Strategies</div>' + rows + '</div>', unsafe_allow_html=True)
with sc_r:
    rows = "".join(
        '<div class="concept-row">'
        '<span class="concept-term">' + t + '</span>'
        '<span class="concept-def">' + d + '</span>'
        '</div>'
        for t, d in [
            ("Backtesting",        "Running a strategy on historical data to see what would have happened."),
            ("Max Drawdown",       "Worst peak-to-trough loss. Tells you the pain to expect in bad runs."),
            ("Sharpe Ratio",       "Return divided by volatility. Above 1.0 is decent, above 2.0 is strong."),
            ("Alpha",              "Return above buy-and-hold. Positive means you actually added value."),
            ("Win Rate",           "% of trades that were profitable. Meaningless without avg win/loss size."),
            ("ATR",                "Average True Range — how far a stock typically moves per day."),
            ("Support/Resistance", "Levels where price historically reverses. Foundation of technical analysis."),
            ("Volume",             "Shares traded. Rising price + rising volume confirms a trend."),
            ("Mean Reversion",     "Tendency of price to return to its historical average after extremes."),
        ]
    )
    st.markdown('<div class="sc-card"><div class="sc-card-hdr">Key Concepts Explained</div>' + rows + '</div>', unsafe_allow_html=True)

# ── FAQ ───────────────────────────────────────────────────────────────────────
st.markdown('<div style="margin-top:1.5rem;font-family:IBM Plex Mono,monospace;font-size:0.52rem;'
            'text-transform:uppercase;letter-spacing:0.22em;color:#1a2235;'
            'border-top:1px solid #1a2235;padding-top:1.5rem;margin-bottom:1rem;">FAQ</div>',
            unsafe_allow_html=True)
fqa, fqb = st.columns(2)
for i, (q, a) in enumerate([
    ("Is this real trading?",                      "No — fully simulated. No real money. Data from Yahoo Finance. For education only."),
    ("How accurate is the backtest?",              "Indicative, not guaranteed. Assumes closing-price fills with no slippage, spread, or tax."),
    ("Do I need to code?",                         "No. Everything is point-and-click. Open source Python/Streamlit if you want to extend it."),
    ("How do I enable AI?",                        "Add your Gemini API key to Streamlit Secrets as GEMINI_API_KEY. Free tier is enough."),
    ("Why can't past performance predict future?", "Markets change. A strategy that crushed a bull market may fail in a bear market."),
    ("What data does it use?",                     "Yahoo Finance via yfinance — years of daily OHLCV for stocks, ETFs, and crypto."),
]):
    with (fqa if i % 2 == 0 else fqb).expander(q):
        st.markdown('<div style="font-size:0.83rem;color:#8896ab;line-height:1.75;">' + a + '</div>', unsafe_allow_html=True)

st.markdown(
    '<div style="margin-top:2.5rem;padding:1.2rem 0;border-top:1px solid #1a2235;'
    'display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:0.4rem;">'
    '<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.62rem;color:#3a4a5e;">'
    '<span style="color:#00e676;font-family:\'Bebas Neue\',sans-serif;font-size:1.05rem;">11</span>'
    '<span style="color:#ff3d57;font-family:\'Bebas Neue\',sans-serif;font-size:1.05rem;">%</span>'
    ' · Free · Open Source'
    '</div>'
    '<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.56rem;color:#1a2235;">'
    'Not financial advice · Educational use only'
    '</div>'
    '</div>',
    unsafe_allow_html=True
)
