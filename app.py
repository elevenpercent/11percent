import streamlit as st
import sys, os
from datetime import datetime
import pytz
sys.path.insert(0, os.path.dirname(__file__))
from utils.styles import SHARED_CSS, LOGO_IMG
from utils.nav import navbar

st.set_page_config(page_title="11% - Trading Platform", page_icon="$", layout="wide", initial_sidebar_state="collapsed")
st.markdown(SHARED_CSS, unsafe_allow_html=True)

st.markdown("""
<style>
@keyframes fadeUp   { from{opacity:0;transform:translateY(24px)}to{opacity:1;transform:translateY(0)} }
@keyframes fadeIn   { from{opacity:0}to{opacity:1} }
@keyframes scanline { 0%{top:-100%}100%{top:100%} }
@keyframes tickerScroll { 0%{transform:translateX(0)} 100%{transform:translateX(-50%)} }
.hero-title   { animation:fadeUp 0.7s ease both; }
.hero-sub     { animation:fadeUp 0.7s 0.15s ease both; }
.stat-grid    { animation:fadeUp 0.6s 0.1s ease both; }
.hero-candles { animation:fadeIn 1s ease both; }
/* Ticker */
.ticker-outer {
    width:100%; overflow:hidden; background:#08100d; border:1px solid #1a2235;
    border-radius:6px; height:32px; display:flex; align-items:center;
    margin-bottom:1.8rem; position:relative;
}
.ticker-outer::before,.ticker-outer::after {
    content:''; position:absolute; top:0; bottom:0; width:60px; z-index:2; pointer-events:none;
}
.ticker-outer::before { left:0;  background:linear-gradient(90deg,#08100d,transparent); }
.ticker-outer::after  { right:0; background:linear-gradient(-90deg,#08100d,transparent); }
.ticker-track { display:flex; white-space:nowrap; animation:tickerScroll 40s linear infinite; }
.ticker-item {
    display:inline-flex; align-items:center; gap:6px; padding:0 22px;
    border-right:1px solid #1a2235; font-family:'IBM Plex Mono',monospace; font-size:0.68rem; flex-shrink:0;
}
.t-sym{color:#3a4a5e;font-weight:600} .t-up{color:#00e676} .t-dn{color:#ff3d57}
/* Screen card */
.screen-card {
    background:#0c1018; border:1px solid #1a2235;
    border-radius:12px; overflow:hidden; position:relative;
}
/* Step cards */
.step-num { font-family:'Bebas Neue',sans-serif; font-size:4rem; color:#1a2235; line-height:1; margin-bottom:0.3rem; transition:color 0.3s; }
.step-card:hover .step-num { color:#2a3550; }
.step-card:hover { border-color:#2a3550!important; }
/* Strategies & Concepts */
.sc-card { background:#0c1018; border:1px solid #1a2235; border-radius:12px; overflow:hidden; }
.sc-card-hdr {
    padding:0.9rem 1.2rem; border-bottom:1px solid #1a2235; background:#08100d;
    font-family:'IBM Plex Mono',monospace; font-size:0.55rem; text-transform:uppercase; letter-spacing:0.2em; color:#3a4a5e;
}
.strat-row {
    display:flex; align-items:flex-start; gap:0.8rem; padding:0.75rem 1.2rem;
    border-bottom:1px solid #0d1117; transition:background 0.15s;
}
.strat-row:last-child{border-bottom:none}
.strat-row:hover{background:rgba(255,255,255,0.015)}
.strat-tag {
    display:inline-block; font-family:'IBM Plex Mono',monospace; font-size:0.5rem;
    text-transform:uppercase; letter-spacing:0.12em; padding:2px 7px;
    border-radius:3px; white-space:nowrap; flex-shrink:0; margin-top:2px;
}
.strat-name{font-size:0.82rem;color:#eef2f7;font-weight:500;margin-bottom:0.15rem}
.strat-desc{font-size:0.72rem;color:#3a4a5e;line-height:1.5}
.concept-row {
    display:grid; grid-template-columns:160px 1fr; gap:0.8rem; align-items:baseline;
    padding:0.75rem 1.2rem; border-bottom:1px solid #0d1117; transition:background 0.15s;
}
.concept-row:last-child{border-bottom:none}
.concept-row:hover{background:rgba(255,255,255,0.015)}
.concept-term{font-family:'IBM Plex Mono',monospace;font-size:0.7rem;color:#00e676;font-weight:600}
.concept-def{font-size:0.78rem;color:#3a4a5e;line-height:1.6}
</style>
""", unsafe_allow_html=True)

navbar()

# ── Helpers ───────────────────────────────────────────────────────────────────
def get_market_status(name):
    now = datetime.now(pytz.utc).astimezone(pytz.timezone("America/New_York"))
    if name == "Crypto": return "24/7", "#00e676", True
    if now.weekday() >= 5: return "CLOSED", "#ff3d57", False
    s = now.replace(hour=9, minute=30, second=0, microsecond=0)
    e = now.replace(hour=16, minute=0,  second=0, microsecond=0)
    return ("OPEN","#00e676",True) if s <= now <= e else ("CLOSED","#ff3d57",False)

def mkt_row(label, status, color):
    dot = "&#9679;" if status != "CLOSED" else "&#9675;"
    return (
        f'<div style="display:flex;justify-content:space-between;align-items:center;'
        f'padding:0.45rem 1rem;border-top:1px solid #1a2235;">'
        f'<span style="font-family:IBM Plex Mono,monospace;font-size:0.7rem;color:#8896ab;">{label}</span>'
        f'<span style="font-family:IBM Plex Mono,monospace;font-size:0.65rem;color:{color};">{dot} {status}</span>'
        f'</div>'
    )

# ── Ticker tape ───────────────────────────────────────────────────────────────
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
                chg = ((c-p)/p)*100
                up = chg >= 0
                out.append((s, f"{c:,.2f}", f"{chg:+.2f}%", "▲" if up else "▼", "t-up" if up else "t-dn"))
        except: pass
    return out

tape = get_tape(tuple(TICKERS))
if tape:
    items = "".join(
        f'<span class="ticker-item"><span class="t-sym">{s}</span>'
        f'<span class="{cls}">{p} {arrow} {ch}</span></span>'
        for s,p,ch,arrow,cls in tape
    )
    st.markdown(
        '<div class="ticker-outer"><div class="ticker-track">' + items + items + '</div></div>',
        unsafe_allow_html=True
    )

# ── Hero ──────────────────────────────────────────────────────────────────────
hero_l, hero_r = st.columns([5, 4])

with hero_l:
    candle_data = [
        (38,"#ff3d57"),(44,"#00e676"),(28,"#ff3d57"),(52,"#00e676"),(60,"#00e676"),
        (30,"#ff3d57"),(62,"#00e676"),(70,"#00e676"),(38,"#ff3d57"),(72,"#00e676"),
        (78,"#00e676"),(46,"#ff3d57"),(80,"#00e676"),(74,"#00e676"),(82,"#00e676"),
        (68,"#ff3d57"),(85,"#00e676"),(79,"#ff3d57"),(88,"#00e676"),(92,"#00e676"),
    ]
    bars = "".join(
        f'<div style="width:10px;height:{max(8,h*0.7)}px;background:{c};'
        f'border-radius:1.5px;animation:fadeUp 0.4s {i*0.04:.2f}s ease both;opacity:0.7;"></div>'
        for i,(h,c) in enumerate(candle_data)
    )
    st.markdown(
        '<div style="padding:2.5rem 0 2rem 0;">'
        '<div style="display:flex;align-items:flex-end;gap:3px;height:72px;margin-bottom:0.5rem;" class="hero-candles">'
        + bars + '</div>'
        '<div class="hero-title" style="font-family:\'Bebas Neue\',sans-serif;font-size:6.5rem;'
        'line-height:0.85;letter-spacing:0.02em;margin-bottom:1.6rem;">'
        '<span style="color:#00e676;">TRADE</span><br>'
        '<span style="color:#eef2f7;">SMARTER</span><br>'
        '<span style="color:#ff3d57;">NOT HARDER</span>'
        '</div>'
        '<div class="hero-sub" style="font-size:1rem;color:#8896ab;max-width:480px;line-height:1.85;margin-bottom:2rem;">'
        'A professional trading platform for learners. Backtest real strategies, '
        'study 15+ indicators, replay historical charts bar by bar, '
        'and get AI analysis — completely free.'
        '</div></div>',
        unsafe_allow_html=True
    )
    c1, c2, c3 = st.columns(3)
    with c1: st.page_link("pages/1_Strategy_Lab.py", label="Lab →")
    with c2: st.page_link("pages/3_Replay.py",       label="Replay →")
    with c3: st.page_link("pages/5_Assistant.py",    label="AI Coach →")

with hero_r:
    nyse_s,nyse_c,_ = get_market_status("NYSE")
    nas_s,nas_c,_   = get_market_status("NASDAQ")
    cme_s,cme_c,_   = get_market_status("CME")
    cry_s,cry_c,_   = get_market_status("Crypto")

    stats_html = "".join(
        f'<div style="background:#0c1018;border:1px solid #1a2235;border-radius:8px;padding:1rem;text-align:center;">'
        f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:2.2rem;color:#00e676;line-height:1;">{v}</div>'
        f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.5rem;color:#3a4a5e;'
        f'text-transform:uppercase;letter-spacing:0.15em;margin-top:0.2rem;">{l}</div></div>'
        for v,l in [("15","Indicators"),("9","Strategies"),("8","Pages"),("$0","Forever Free")]
    )

    # TradingView mini chart widget for hero
    tv_hero = """
<div class="screen-card" style="margin-bottom:1rem;animation:fadeUp 0.6s 0.2s ease both;opacity:0;">
  <div class="screen-header">
    <div class="dot-red"></div><div class="dot-yel"></div><div class="dot-grn"></div>
    <span style="margin-left:0.5rem;">LIVE CHART · TRADINGVIEW</span>
  </div>
  <div style="height:280px;">
    <div class="tradingview-widget-container" style="height:100%;width:100%;">
      <div id="tv_hero_chart" style="height:100%;width:100%;"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget({
        "autosize": true,
        "symbol": "NASDAQ:AAPL",
        "interval": "D",
        "timezone": "America/New_York",
        "theme": "dark",
        "style": "1",
        "locale": "en",
        "toolbar_bg": "#0c1018",
        "enable_publishing": false,
        "hide_side_toolbar": true,
        "hide_top_toolbar": false,
        "withdateranges": false,
        "allow_symbol_change": true,
        "save_image": false,
        "container_id": "tv_hero_chart",
        "backgroundColor": "rgba(12,16,24,1)",
        "gridColor": "rgba(26,34,53,0.4)",
        "overrides": {
          "mainSeriesProperties.candleStyle.upColor": "#00e676",
          "mainSeriesProperties.candleStyle.downColor": "#ff3d57",
          "mainSeriesProperties.candleStyle.borderUpColor": "#00e676",
          "mainSeriesProperties.candleStyle.borderDownColor": "#ff3d57",
          "mainSeriesProperties.candleStyle.wickUpColor": "#00e676",
          "mainSeriesProperties.candleStyle.wickDownColor": "#ff3d57",
          "paneProperties.background": "#0c1018",
          "paneProperties.backgroundType": "solid",
          "paneProperties.vertGridProperties.color": "#1a2235",
          "paneProperties.horzGridProperties.color": "#1a2235",
          "scalesProperties.textColor": "#3a4a5e",
          "scalesProperties.lineColor": "#1a2235"
        }
      });
      </script>
    </div>
  </div>
</div>
"""
    st.markdown(
        '<div style="padding:2rem 0 1rem 0;" class="stat-grid">'
        + tv_hero +
        f'<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-bottom:1rem;'
        f'animation:fadeUp 0.6s 0.3s ease both;opacity:0;">{stats_html}</div>'
        '<div style="background:#0c1018;border:1px solid #1a2235;border-radius:8px;overflow:hidden;'
        'animation:fadeUp 0.6s 0.4s ease both;opacity:0;">'
        '<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.52rem;color:#3a4a5e;'
        'text-transform:uppercase;letter-spacing:0.2em;padding:0.7rem 1rem 0.4rem;">Market Status</div>'
        + mkt_row("NYSE",nyse_s,nyse_c) + mkt_row("NASDAQ",nas_s,nas_c)
        + mkt_row("CME Futures",cme_s,cme_c) + mkt_row("Crypto",cry_s,cry_c)
        + '</div></div>',
        unsafe_allow_html=True
    )

# ── Platform features ─────────────────────────────────────────────────────────
st.markdown('<div class="divider" style="margin-top:1rem;">Platform</div>', unsafe_allow_html=True)
_features = [
    ("⚡","Strategy Lab",  "9 prebuilt strategies + custom signal builder with 15 indicators and AND/OR combo logic.","pages/1_Strategy_Lab.py"),
    ("▶", "Replay",        "Step through bars one at a time with live ticking price. Trade without knowing the future.","pages/3_Replay.py"),
    ("🔍","Analysis",      "Full fundamental + AI breakdown. Financials, valuation, risks, and a personalised verdict.","pages/4_Analysis.py"),
    ("🐋","Whale Tracker", "Flags unusual volume spikes across your watch list. Large orders often precede big moves.","pages/8_Whale_Tracker.py"),
    ("〰","Monte Carlo",   "1,000 random simulations showing where price could go. A probability cone, not a prediction.","pages/9_Monte_Carlo.py"),
    ("🤖","AI Coach",      "Ask anything in plain English. Explains your results, strategies, and trading concepts.","pages/5_Assistant.py"),
]
for col,(icon,title,desc,link) in zip(st.columns(6), _features):
    col.markdown(
        f'<div style="background:#0c1018;border:1px solid #1a2235;border-radius:10px;'
        f'padding:1.2rem;margin-bottom:0.5rem;min-height:160px;">'
        f'<div style="font-size:1.4rem;margin-bottom:0.6rem;">{icon}</div>'
        f'<div style="font-family:IBM Plex Mono,monospace;font-size:0.62rem;font-weight:600;'
        f'text-transform:uppercase;letter-spacing:0.12em;color:#eef2f7;margin-bottom:0.5rem;">{title}</div>'
        f'<div style="font-size:0.75rem;color:#3a4a5e;line-height:1.6;">{desc}</div></div>',
        unsafe_allow_html=True
    )
    col.page_link(link, label="Open →")

# ── Indicators ────────────────────────────────────────────────────────────────
st.markdown('<div class="divider" style="margin-top:2rem;">15 Indicators Available</div>', unsafe_allow_html=True)
for col,(cat,color,inds) in zip(st.columns(3), [
    ("Trend","#4da6ff",["SMA","EMA","WMA","Hull MA","SuperTrend","Ichimoku","Parabolic SAR"]),
    ("Momentum","#b388ff",["RSI","Stochastic RSI","MACD","CCI","Williams %R"]),
    ("Volatility + Volume","#ffd166",["Bollinger Bands","Keltner Channels","Donchian Channels","VWAP","OBV"]),
]):
    tags = "".join(
        f'<span style="display:inline-block;font-family:IBM Plex Mono,monospace;font-size:0.65rem;'
        f'padding:3px 10px;border-radius:4px;background:{color}12;color:{color};'
        f'border:1px solid {color}25;margin:3px 3px 3px 0;">{ind}</span>'
        for ind in inds
    )
    col.markdown(
        f'<div style="background:#0c1018;border:1px solid #1a2235;border-radius:10px;padding:1.3rem;height:100%;">'
        f'<div style="font-family:IBM Plex Mono,monospace;font-size:0.6rem;color:{color};'
        f'text-transform:uppercase;letter-spacing:0.18em;margin-bottom:0.9rem;">{cat}</div>'
        f'<div>{tags}</div></div>',
        unsafe_allow_html=True
    )

# ── How it works ──────────────────────────────────────────────────────────────
st.markdown('<div class="divider" style="margin-top:2rem;">How It Works</div>', unsafe_allow_html=True)
for col,(num,title,desc) in zip(st.columns(5), [
    ("01","Pick a Stock",    "Enter any ticker — stocks, ETFs, or crypto. Live data from Yahoo Finance."),
    ("02","Choose Strategy", "9 pre-built strategies or build your own with 15 indicators."),
    ("03","Run Backtest",    "Set date range and capital. Results computed in seconds."),
    ("04","Study Results",   "Return, alpha, drawdown, Sharpe — all explained in plain English."),
    ("05","Ask the Coach",   "The AI coach explains what the numbers mean and how to improve."),
]):
    col.markdown(
        f'<div class="step-card" style="padding:1.2rem 0.8rem;background:#0c1018;'
        f'border:1px solid #1a2235;border-radius:10px;transition:border-color 0.2s;">'
        f'<div class="step-num">{num}</div>'
        f'<div style="font-family:IBM Plex Mono,monospace;font-size:0.68rem;color:#eef2f7;'
        f'text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.4rem;">{title}</div>'
        f'<div style="font-size:0.8rem;color:#3a4a5e;line-height:1.65;">{desc}</div></div>',
        unsafe_allow_html=True
    )

# ── Strategies + Concepts ─────────────────────────────────────────────────────
st.markdown('<div class="divider" style="margin-top:2rem;">Strategies + Concepts</div>', unsafe_allow_html=True)
sc_l, sc_r = st.columns(2)
with sc_l:
    rows = "".join(
        f'<div class="strat-row">'
        f'<span class="strat-tag" style="background:{c}18;color:{c};border:1px solid {c}30;">{tag}</span>'
        f'<div><div class="strat-name">{name}</div><div class="strat-desc">{desc}</div></div>'
        f'</div>'
        for name,tag,c,desc in [
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
        f'<div class="concept-row"><span class="concept-term">{t}</span><span class="concept-def">{d}</span></div>'
        for t,d in [
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
st.markdown('<div class="divider" style="margin-top:2rem;">FAQ</div>', unsafe_allow_html=True)
fqa, fqb = st.columns(2)
for i,(q,a) in enumerate([
    ("Is this real trading?",                      "No — fully simulated. No real money. Data from Yahoo Finance. For education only."),
    ("How accurate is the backtest?",              "Indicative, not guaranteed. Assumes closing-price fills with no slippage, spread, or tax."),
    ("Do I need to code?",                         "No. Everything is point-and-click. Open source Python/Streamlit if you want to extend it."),
    ("How do I enable AI?",                        "Add your Gemini API key to Streamlit Secrets as GEMINI_API_KEY. Free tier is enough."),
    ("Why can't past performance predict future?", "Markets change. A strategy that crushed a bull market may fail in a bear market."),
    ("What data does it use?",                     "Yahoo Finance via yfinance — years of daily OHLCV for stocks, ETFs, and crypto."),
]):
    with (fqa if i%2==0 else fqb).expander(q):
        st.markdown(f'<div style="font-size:0.84rem;color:#8896ab;line-height:1.75;padding:0.2rem 0;">{a}</div>', unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-top:3rem;padding:1.5rem 0;border-top:1px solid #1a2235;
display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:0.5rem;">
    <div style="font-family:'IBM Plex Mono',monospace;font-size:0.65rem;color:#3a4a5e;">
        <span style="color:#00e676;font-family:'Bebas Neue',sans-serif;font-size:1.1rem;">11</span>
        <span style="color:#ff3d57;font-family:'Bebas Neue',sans-serif;font-size:1.1rem;">%</span>
        &nbsp;·&nbsp; Built by Rishi Gopinath &nbsp;·&nbsp; Free &nbsp;·&nbsp; Open Source
    </div>
    <div style="font-family:'IBM Plex Mono',monospace;font-size:0.58rem;color:#1a2235;">
        Not financial advice · Educational use only · Past performance does not predict future results
    </div>
</div>
""", unsafe_allow_html=True)
