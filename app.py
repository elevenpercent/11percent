import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import sys, os
from utils.styles import SHARED_CSS

st.set_page_config(page_title="11% — Trading Platform", page_icon="💲", layout="wide", initial_sidebar_state="collapsed")
st.markdown(SHARED_CSS, unsafe_allow_html=True)

# ── Navbar ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="nb"><div class="nb-brand"><span class="g">11</span><span class="r">%</span></div><div class="nb-links">', unsafe_allow_html=True)
_nav = st.columns([1,1,1,1,1,1])
with _nav[0]: st.page_link("app.py",                    label="Home")
with _nav[1]: st.page_link("pages/1_Backtest.py",       label="Backtest")
with _nav[2]: st.page_link("pages/2_Indicator_Test.py", label="Indicators")
with _nav[3]: st.page_link("pages/3_Replay.py",         label="Replay")
with _nav[4]: st.page_link("pages/4_Analysis.py",       label="Analysis")
with _nav[5]: st.page_link("pages/5_Assistant.py",      label="Assistant")
st.markdown('</div><div class="nb-tag">FREE · OPEN SOURCE</div></div>', unsafe_allow_html=True)

# ── Live ticker tape ───────────────────────────────────────────────────────────
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

# ── Hero section ───────────────────────────────────────────────────────────────
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

    # CTA buttons
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

# ── Feature cards ──────────────────────────────────────────────────────────────
st.markdown('<div class="price-divider">WHAT YOU CAN DO</div>', unsafe_allow_html=True)

features = [
    ("Backtest", "#00d68f", "Test any strategy against years of real market data. See exactly how it would have performed — returns, drawdown, win rate, Sharpe ratio, and more. Compare against buy & hold to measure true alpha.", "pages/1_Backtest.py", "Open Backtest →"),
    ("Indicator Test", "#00d68f", "Build custom strategies from scratch using up to 3 indicators combined with AND/OR logic. Set your own buy and sell conditions and see the results instantly.", "pages/2_Indicator_Test.py", "Open Indicator Test →"),
    ("Chart Replay", "#ff4757", "Step through historical candles bar by bar with a professional chart powered by TradingView's lightweight-charts library. Practice reading price action and test your instincts.", "pages/3_Replay.py", "Open Replay →"),
    ("AI Analysis", "#00d68f", "Get a full fundamental breakdown of any stock — financials, valuation, risks, and growth potential — powered by Gemini AI. Connects to your backtest results for context.", "pages/4_Analysis.py", "Open Analysis →"),
    ("AI Assistant", "#00d68f", "Ask anything. Your personal trading coach explains strategy results, teaches concepts, compares approaches, and gives personalised advice based on your experience level and goals.", "pages/5_Assistant.py", "Open Assistant →"),
]

cols = st.columns(5)
for col, (title, accent, desc, link, cta) in zip(cols, features):
    col.markdown(f"""
    <div style="background:#0d1117;border:1px solid #1c2333;border-radius:6px;padding:1.4rem;height:100%;border-top:2px solid {accent};">
        <div style="font-family:'IBM Plex Mono',monospace;font-size:0.65rem;font-weight:700;color:{accent};text-transform:uppercase;letter-spacing:0.15em;margin-bottom:0.8rem;">{title}</div>
        <div style="font-size:0.82rem;color:#4a5568;line-height:1.7;margin-bottom:1.2rem;">{desc}</div>
    </div>
    """, unsafe_allow_html=True)
    col.page_link(link, label=cta)

# ── Strategies section ─────────────────────────────────────────────────────────
st.markdown('<div class="price-divider">STRATEGIES & INDICATORS</div>', unsafe_allow_html=True)
s_left, s_right = st.columns(2)

with s_left:
    st.markdown('<div style="font-family:IBM Plex Mono,monospace;font-size:0.58rem;color:#3a4558;text-transform:uppercase;letter-spacing:0.18em;margin-bottom:0.8rem;">Built-in Strategies</div>', unsafe_allow_html=True)
    strategies = [
        ("SMA Crossover", "Classic trend-following. Fast MA crosses above slow MA → buy."),
        ("EMA Crossover", "Like SMA but reacts faster to recent price changes."),
        ("RSI", "Buys oversold conditions, sells overbought. Mean-reversion."),
        ("MACD", "Momentum crossover strategy using MACD and signal line."),
        ("Bollinger Bands", "Buys when price touches lower band, sells at upper band."),
        ("SuperTrend", "Trend-following using ATR-based dynamic support/resistance."),
        ("RSI + Bollinger Bands", "Combo: RSI confirms BB signals to reduce false entries."),
        ("EMA + RSI Filter", "EMA crossover with RSI filter to improve signal quality."),
        ("MACD + SuperTrend", "Dual confirmation: MACD momentum + SuperTrend direction."),
    ]
    for name, desc in strategies:
        st.markdown(f'<div style="padding:0.65rem 0;border-bottom:1px solid #1c2333;"><div style="font-family:IBM Plex Mono,monospace;font-size:0.75rem;color:#cdd5e0;margin-bottom:0.2rem;"><span style="color:#00d68f;margin-right:0.5rem;">—</span>{name}</div><div style="font-size:0.77rem;color:#3a4558;padding-left:1rem;">{desc}</div></div>', unsafe_allow_html=True)

with s_right:
    st.markdown('<div style="font-family:IBM Plex Mono,monospace;font-size:0.58rem;color:#3a4558;text-transform:uppercase;letter-spacing:0.18em;margin-bottom:0.8rem;">Available Indicators</div>', unsafe_allow_html=True)
    indicators = [
        ("SMA / EMA / WMA", "Moving averages — trend direction and dynamic support/resistance."),
        ("RSI", "Relative Strength Index — momentum oscillator, 0–100 scale."),
        ("Stochastic RSI", "RSI of RSI — faster, more sensitive overbought/oversold signals."),
        ("MACD", "Moving Average Convergence Divergence — trend + momentum."),
        ("Bollinger Bands", "Volatility bands that expand in trends, contract in ranges."),
        ("SuperTrend", "ATR-based trend indicator with clear buy/sell direction signal."),
        ("Ichimoku Cloud", "Japanese system showing trend, momentum, and support/resistance."),
        ("VWAP", "Volume Weighted Average Price — institutional benchmark."),
        ("OBV", "On Balance Volume — tracks buying/selling pressure via volume."),
    ]
    for name, desc in indicators:
        st.markdown(f'<div style="padding:0.65rem 0;border-bottom:1px solid #1c2333;"><div style="font-family:IBM Plex Mono,monospace;font-size:0.75rem;color:#cdd5e0;margin-bottom:0.2rem;"><span style="color:#00d68f;margin-right:0.5rem;">—</span>{name}</div><div style="font-size:0.77rem;color:#3a4558;padding-left:1rem;">{desc}</div></div>', unsafe_allow_html=True)

# ── How it works ───────────────────────────────────────────────────────────────
st.markdown('<div class="price-divider">HOW IT WORKS</div>', unsafe_allow_html=True)

steps = [
    ("01", "Pick a Stock", "Enter any ticker symbol — stocks, ETFs, crypto. Data is pulled live from Yahoo Finance covering years of history."),
    ("02", "Choose a Strategy", "Select from 9 pre-built strategies or build your own in Indicator Test using up to 3 indicators with custom conditions."),
    ("03", "Configure & Run", "Set your date range, starting capital, and strategy parameters. Hit run and get results in seconds."),
    ("04", "Read the Results", "See every metric that matters: total return, alpha over buy & hold, max drawdown, Sharpe ratio, win rate, and every individual trade."),
    ("05", "Get AI Insight", "Paste your results into the AI Assistant or run an AI Analysis on the stock for a deeper understanding of what the numbers mean."),
]
step_cols = st.columns(5)
for col, (num, title, desc) in zip(step_cols, steps):
    col.markdown(f"""
    <div style="padding:1.2rem 0;">
        <div style="font-family:'Bebas Neue',sans-serif;font-size:2.5rem;color:#1c2333;line-height:1;">{num}</div>
        <div style="font-family:'IBM Plex Mono',monospace;font-size:0.72rem;font-weight:700;color:#cdd5e0;text-transform:uppercase;letter-spacing:0.1em;margin:0.4rem 0 0.6rem 0;">{title}</div>
        <div style="font-size:0.8rem;color:#3a4558;line-height:1.7;">{desc}</div>
    </div>
    """, unsafe_allow_html=True)

# ── Concepts glossary ──────────────────────────────────────────────────────────
st.markdown('<div class="price-divider">TRADING CONCEPTS</div>', unsafe_allow_html=True)
g_left, g_right = st.columns(2)

terms_left = [
    ("Backtesting", "Running a trading strategy against historical price data to see how it would have performed. The core feature of this platform."),
    ("Drawdown", "The peak-to-trough decline during a specific period. Max drawdown tells you the worst loss streak a strategy experienced."),
    ("Sharpe Ratio", "Risk-adjusted return. Divides return by volatility. Above 1.0 is decent, above 2.0 is strong. Penalises volatile strategies."),
    ("Win Rate", "Percentage of trades that closed in profit. A 60% win rate isn't necessarily better than 40% — it depends on the size of wins vs losses."),
    ("Alpha", "Return above the benchmark (here, buy & hold). Positive alpha means the strategy beat doing nothing."),
]
terms_right = [
    ("Moving Average", "Average price over N periods. Smooths out noise to show trend direction. SMA weights all days equally; EMA weights recent days more."),
    ("RSI (Relative Strength Index)", "Measures speed and magnitude of price changes on a 0–100 scale. Below 30 = oversold, above 70 = overbought."),
    ("Support & Resistance", "Price levels where buyers (support) or sellers (resistance) historically step in. Key to many technical strategies."),
    ("Volume", "Number of shares traded. Rising price + rising volume confirms a move. Rising price + falling volume is a warning sign."),
    ("ATR (Average True Range)", "Measures volatility — how much a stock moves on average per day. Used by SuperTrend and position sizing."),
]

with g_left:
    for term, definition in terms_left:
        st.markdown(f'<div style="padding:0.75rem 0;border-bottom:1px solid #1c2333;"><div style="font-family:IBM Plex Mono,monospace;font-size:0.75rem;color:#00d68f;margin-bottom:0.3rem;">{term}</div><div style="font-size:0.8rem;color:#3a4558;line-height:1.65;">{definition}</div></div>', unsafe_allow_html=True)

with g_right:
    for term, definition in terms_right:
        st.markdown(f'<div style="padding:0.75rem 0;border-bottom:1px solid #1c2333;"><div style="font-family:IBM Plex Mono,monospace;font-size:0.75rem;color:#00d68f;margin-bottom:0.3rem;">{term}</div><div style="font-size:0.8rem;color:#3a4558;line-height:1.65;">{definition}</div></div>', unsafe_allow_html=True)

# ── FAQ ────────────────────────────────────────────────────────────────────────
st.markdown('<div class="price-divider">FAQ</div>', unsafe_allow_html=True)

faqs = [
    ("Is this real trading or simulated?", "Simulated. No real money is involved. Data comes from Yahoo Finance (delayed). This platform is for education and strategy research only."),
    ("How accurate is the backtesting?", "Results are indicative, not guaranteed. Backtests assume you can always buy/sell at the closing price and don't account for slippage, spreads, or taxes. Real results will differ."),
    ("Do I need to know how to code?", "No. Everything is point-and-click. If you want to extend the platform, it's built in Python with Streamlit — the code is open source."),
    ("Why does past performance not guarantee future results?", "Markets change. A strategy that worked in a bull market may fail in a bear market. Backtesting shows what happened, not what will happen."),
    ("How do I get the AI features?", "Add your Gemini API key to Streamlit Secrets as GEMINI_API_KEY. The Gemini API has a free tier that covers normal usage."),
]
for q, a in faqs:
    with st.expander(q):
        st.markdown(f'<div style="font-size:0.85rem;color:#4a5568;line-height:1.75;padding:0.2rem 0;">{a}</div>', unsafe_allow_html=True)

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-top:3rem;padding:1.5rem 0;border-top:1px solid #1c2333;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:0.5rem;">
    <div style="font-family:'IBM Plex Mono',monospace;font-size:0.65rem;color:#3a4558;">
        <span style="color:#00d68f;font-family:'Bebas Neue',sans-serif;font-size:1rem;">11</span><span style="color:#ff4757;font-family:'Bebas Neue',sans-serif;font-size:1rem;">%</span>
        &nbsp;·&nbsp; Built by Rishi Gopinath &nbsp;·&nbsp; Free &nbsp;·&nbsp; Open Source
    </div>
    <div style="font-family:'IBM Plex Mono',monospace;font-size:0.62rem;color:#1c2333;">
        ⚠ Not financial advice. Past performance does not guarantee future results. For educational use only.
    </div>
</div>
""", unsafe_allow_html=True)
