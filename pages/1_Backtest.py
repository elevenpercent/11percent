import streamlit as st
import sys, os
import pandas as pd
from datetime import date, timedelta
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.data import get_stock_data, get_ticker_info
from utils.strategies import STRATEGY_REGISTRY, run_backtest
from utils.charts import chart_candles, chart_portfolio, chart_rsi, chart_macd, chart_bollinger, chart_supertrend
from utils.indicators import rsi, macd, bollinger_bands, supertrend, sma, ema
from utils.styles import SHARED_CSS

st.set_page_config(page_title="Backtest | 11%", layout="wide", initial_sidebar_state="collapsed")
st.markdown(SHARED_CSS, unsafe_allow_html=True)
st.markdown('<div class="nb"><div class="nb-brand"><span class="g">11</span><span class="r">%</span></div><div class="nb-links">', unsafe_allow_html=True)
_nav = st.columns([1,1,1,1,1,1])
with _nav[0]: st.page_link("app.py",                    label="Home")
with _nav[1]: st.page_link("pages/1_Backtest.py",       label="Backtest")
with _nav[2]: st.page_link("pages/2_Indicator_Test.py", label="Indicators")
with _nav[3]: st.page_link("pages/3_Replay.py",         label="Replay")
with _nav[4]: st.page_link("pages/4_Analysis.py",       label="Analysis")
with _nav[5]: st.page_link("pages/5_Assistant.py",      label="Assistant")
st.markdown('</div><div class="nb-tag">FREE · OPEN SOURCE</div></div>', unsafe_allow_html=True)

STRAT_META = {
    "SMA Crossover":        {"level":"Beginner","type":"Trend-Following","desc":"The classic golden cross. Buys when the short moving average crosses above the long one, signalling an uptrend. Works best in strongly trending markets but gives false signals in choppy sideways action.","tip":"Try Short=20, Long=50 as a starting point. Wider gaps between the two periods = fewer but more reliable signals."},
    "EMA Crossover":        {"level":"Beginner","type":"Trend-Following","desc":"Same logic as SMA Crossover but uses Exponential Moving Averages that weight recent prices more heavily. Catches trend changes slightly earlier than SMA at the cost of more false signals.","tip":"The 12/26 combo is the same base as MACD. Try 9/21 for faster signals on swing trading."},
    "RSI":                  {"level":"Beginner","type":"Mean Reversion","desc":"Buys when the market is oversold (RSI below 30) and sells when overbought (RSI above 70). Works well in ranging sideways markets. Can be crushed in strong trends — a stock can stay overbought for months.","tip":"Lower oversold threshold (e.g. 20) = fewer, higher-confidence buy signals. Try 14 period as your starting RSI length."},
    "MACD":                 {"level":"Intermediate","type":"Momentum","desc":"Measures the difference between two EMAs to track momentum. Buys on bullish crossover of MACD and signal lines. One of the most popular indicators in existence — widely watched by institutions.","tip":"Standard 12/26/9 is fine. Try 8/17/9 for faster signals. MACD works best on daily charts with trending assets."},
    "Bollinger Bands":      {"level":"Intermediate","type":"Mean Reversion","desc":"Dynamically widens in volatile markets and narrows in calm ones. Buys at the lower band, sells at the upper, betting on mean reversion. Fails badly in breakouts when price rides the band.","tip":"When bands squeeze (narrow) it often precedes a big move. The 20-period, 2 std dev setting is industry standard."},
    "SuperTrend":           {"level":"Intermediate","type":"Trend-Following","desc":"Uses Average True Range (ATR) to build a dynamic stop line that flips bullish or bearish. Gives very clean, unambiguous signals. One of the best pure trend indicators available.","tip":"Lower multiplier (e.g. 1.5) = more sensitive, more trades. Higher (e.g. 4.0) = fewer, cleaner trends only."},
    "RSI + Bollinger Bands":{"level":"Intermediate","type":"Mean Reversion","desc":"Combination strategy — both RSI and Bollinger Bands must confirm before a trade is taken. The dual requirement dramatically reduces false signals compared to either alone.","tip":"Since two filters already reduce noise, you can widen the RSI thresholds (e.g. 35/65) to compensate for fewer signals."},
    "EMA + RSI Filter":     {"level":"Advanced","type":"Trend + Momentum","desc":"Uses the EMA crossover for trend direction and RSI as a momentum filter. Only enters when the trend is right AND momentum is confirming. Higher quality signals, fewer total trades.","tip":"The RSI filter stops you buying into an exhausted trend. Adjust RSI oversold toward 40-45 since you're already filtering by trend."},
    "MACD + SuperTrend":    {"level":"Advanced","type":"Dual Confirmation","desc":"Both MACD and SuperTrend must agree before entering. This combination is strong in clearly trending markets. Very quiet in choppy markets — which is exactly the point.","tip":"This strategy is intentionally patient. On a 3-year test you might only see 10-15 trades. Quality over quantity."},
}
LEVEL_COLOR = {"Beginner":"#00d68f","Intermediate":"#ffd166","Advanced":"#ff4757"}
TYPE_COLOR  = {"Trend-Following":"#4da6ff","Mean Reversion":"#b388ff","Momentum":"#ff9f43","Trend + Momentum":"#4da6ff","Dual Confirmation":"#4da6ff"}

st.markdown('''<div class="page-header"><h1>Backtest Lab</h1><p>Test trading strategies against real historical market data. See exactly how they would have performed and understand what the numbers mean.</p></div>''', unsafe_allow_html=True)

# ── Setup ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="price-divider">SETUP</div>', unsafe_allow_html=True)
st.markdown('<div class="config-panel">', unsafe_allow_html=True)
r1,r2,r3,r4,r5 = st.columns([2,1.5,1.5,1.5,2])
with r1: ticker        = st.text_input("Ticker Symbol", value="AAPL", help="Stocks: AAPL, TSLA, MSFT. ETFs: SPY, QQQ. Crypto: BTC-USD").upper().strip()
with r2: start_date    = st.date_input("Start Date", value=date.today()-timedelta(days=365*3))
with r3: end_date      = st.date_input("End Date",   value=date.today())
with r4: capital       = st.number_input("Starting Capital ($)", value=10000, min_value=100, step=1000)
with r5: strategy_name = st.selectbox("Strategy", list(STRATEGY_REGISTRY.keys()))

meta = STRAT_META.get(strategy_name, {})
if meta:
    lc = LEVEL_COLOR.get(meta["level"], "#cdd5e0")
    tc = TYPE_COLOR.get(meta["type"],   "#cdd5e0")
    st.markdown(f'''
    <div style="display:flex;gap:1rem;align-items:flex-start;padding:0.9rem 0 0.3rem 0;">
      <div style="flex:1">
        <div style="font-size:0.83rem;color:#8892a4;line-height:1.65;margin-bottom:0.5rem;">{meta["desc"]}</div>
        <div style="font-size:0.78rem;color:#3a4558;"><span style="color:#00d68f;">Tip:</span> {meta["tip"]}</div>
      </div>
      <div style="display:flex;flex-direction:column;gap:5px;flex-shrink:0;padding-top:2px;">
        <span style="font-family:'IBM Plex Mono',monospace;font-size:0.6rem;padding:3px 10px;border-radius:2px;background:{lc}18;color:{lc};border:1px solid {lc}44;">{meta["level"]}</span>
        <span style="font-family:'IBM Plex Mono',monospace;font-size:0.6rem;padding:3px 10px;border-radius:2px;background:{tc}18;color:{tc};border:1px solid {tc}44;">{meta["type"]}</span>
      </div>
    </div>''', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ── Parameters ────────────────────────────────────────────────────────────────
strategy_info = STRATEGY_REGISTRY[strategy_name]
user_params = {}
st.markdown('<div class="price-divider">PARAMETERS</div>', unsafe_allow_html=True)
st.markdown('<div class="config-panel">', unsafe_allow_html=True)
pc = st.columns(4)
if strategy_name == "SMA Crossover":
    with pc[0]: user_params["short"] = st.slider("Short SMA", 5, 50, 20, help="Faster line — reacts to recent price")
    with pc[1]: user_params["long"]  = st.slider("Long SMA", 20, 200, 50, help="Slower line — shows the major trend")
elif strategy_name == "EMA Crossover":
    with pc[0]: user_params["short"] = st.slider("Short EMA", 5, 50, 12)
    with pc[1]: user_params["long"]  = st.slider("Long EMA", 20, 200, 26)
elif strategy_name == "RSI":
    with pc[0]: user_params["window"]     = st.slider("RSI Period", 5, 30, 14, help="Standard is 14. Lower = noisier but faster")
    with pc[1]: user_params["oversold"]   = st.slider("Oversold Level", 10, 45, 30, help="Buy signal. Below this = potential bounce")
    with pc[2]: user_params["overbought"] = st.slider("Overbought Level", 55, 90, 70, help="Sell signal. Above this = potential pullback")
elif strategy_name == "MACD":
    with pc[0]: user_params["fast"]   = st.slider("Fast EMA", 5, 30, 12)
    with pc[1]: user_params["slow"]   = st.slider("Slow EMA", 15, 60, 26)
    with pc[2]: user_params["signal"] = st.slider("Signal Line", 3, 20, 9)
elif strategy_name == "Bollinger Bands":
    with pc[0]: user_params["window"]  = st.slider("Period", 5, 50, 20)
    with pc[1]: user_params["num_std"] = st.slider("Std Deviations", 1.0, 4.0, 2.0, step=0.1)
elif strategy_name == "SuperTrend":
    with pc[0]: user_params["window"]     = st.slider("ATR Period", 5, 30, 10)
    with pc[1]: user_params["multiplier"] = st.slider("Multiplier", 1.0, 6.0, 3.0, step=0.5)
elif strategy_name == "RSI + Bollinger Bands":
    with pc[0]: user_params["rsi_window"] = st.slider("RSI Period", 5, 30, 14)
    with pc[1]: user_params["bb_window"]  = st.slider("BB Period", 10, 50, 20)
    with pc[2]: user_params["oversold"]   = st.slider("RSI Oversold", 20, 45, 35)
    with pc[3]: user_params["overbought"] = st.slider("RSI Overbought", 55, 85, 65)
elif strategy_name == "EMA + RSI Filter":
    with pc[0]: user_params["ema_fast"]   = st.slider("Fast EMA", 3, 30, 9)
    with pc[1]: user_params["ema_slow"]   = st.slider("Slow EMA", 10, 60, 21)
    with pc[2]: user_params["rsi_window"] = st.slider("RSI Period", 5, 30, 14)
elif strategy_name == "MACD + SuperTrend":
    with pc[0]: user_params["fast"]      = st.slider("MACD Fast", 5, 20, 12)
    with pc[1]: user_params["slow"]      = st.slider("MACD Slow", 15, 50, 26)
    with pc[2]: user_params["st_window"] = st.slider("ST ATR Period", 5, 20, 10)
else:
    st.markdown('<div style="font-size:0.8rem;color:#3a4558;padding:0.4rem 0;">This strategy uses default parameters.</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

run_btn = st.button("Run Backtest", use_container_width=False)

if run_btn:
    with st.spinner(f"Loading {ticker} and running simulation..."):
        df = get_stock_data(ticker, str(start_date), str(end_date))
    if df.empty: st.error("No data found. Check the ticker symbol."); st.stop()
    info = get_ticker_info(ticker)
    try:
        signals = strategy_info["fn"](df, **user_params)
        result  = run_backtest(df, signals, float(capital))
    except Exception as e: st.error(f"Error: {e}"); st.stop()

    m = result["metrics"]; port = result["portfolio"]; trades = result["trades"]

    # Stock banner
    cp = float(df["Close"].iloc[-1])
    pct_period = (float(df["Close"].iloc[-1]) - float(df["Close"].iloc[0])) / float(df["Close"].iloc[0]) * 100
    st.markdown(f'''<div style="background:#0d1117;border:1px solid #1c2333;border-radius:6px;padding:1rem 1.4rem;margin:1rem 0;display:flex;align-items:center;gap:2rem;flex-wrap:wrap;">
        <div><div style="font-family:'Bebas Neue',sans-serif;font-size:1.8rem;">{ticker}</div><div style="font-size:0.72rem;color:#3a4558;">{info.get("name","")}</div></div>
        <div style="font-size:0.72rem;color:#3a4558;">{info.get("sector","N/A")} · {info.get("industry","N/A")}</div>
        <div><div style="font-family:'IBM Plex Mono',monospace;font-size:1.1rem;">${cp:,.2f}</div><div style="font-size:0.7rem;color:{"#00d68f" if pct_period>=0 else "#ff4757"};">{pct_period:+.2f}% over test period</div></div>
        <div style="font-size:0.72rem;color:#3a4558;">{len(df)} trading days · {start_date} → {end_date}</div>
    </div>''', unsafe_allow_html=True)

    # Metrics
    st.markdown('<div class="price-divider">RESULTS</div>', unsafe_allow_html=True)
    alpha = m["total_return"] - m["bh_return"]
    c = st.columns(8)
    def mc(col, val, lbl, fmt="pct"):
        if fmt=="pct":   cls="pos" if val>=0 else "neg"; d=f"{val:+.2f}%"
        elif fmt=="usd": cls="neu"; d=f"${val:,.0f}"
        elif fmt=="raw":
            try: cls="pos" if float(val)>=1 else ("neg" if float(val)<0 else "neu")
            except: cls="neu"
            d=str(val)
        else: cls="neu"; d=str(val)
        col.markdown(f'<div class="metric-card"><div class="metric-val {cls}">{d}</div><div class="metric-lbl">{lbl}</div></div>', unsafe_allow_html=True)
    mc(c[0], m["total_return"], "Strategy Return")
    mc(c[1], m["bh_return"],    "Buy & Hold")
    mc(c[2], alpha,             "Alpha")
    mc(c[3], m["max_drawdown"], "Max Drawdown")
    mc(c[4], m["final_value"],  "Final Value", "usd")
    mc(c[5], m["win_rate"],     "Win Rate")
    mc(c[6], m["sharpe"],       "Sharpe Ratio", "raw")
    c[7].markdown(f'<div class="metric-card"><div class="metric-val neu">{m["num_trades"]}</div><div class="metric-lbl">Total Trades</div></div>', unsafe_allow_html=True)

    # Interpretation
    with st.expander("How to read these results"):
        i1, i2, i3 = st.columns(3)
        with i1:
            direction = "beat buy & hold" if alpha > 0 else "underperformed buy & hold"
            st.markdown(f"""**Return vs Buy & Hold**

Your strategy returned **{m["total_return"]:+.2f}%** while simply holding the stock returned **{m["bh_return"]:+.2f}%**.

{"✅ Alpha of " + f"{alpha:+.2f}% — your strategy added value." if alpha > 0 else "⚠️ Negative alpha of " + f"{alpha:.2f}% — holding the stock was better. This is very common and not necessarily a failure — it tells you the strategy suits a different asset or time period."}""")
        with i2:
            try: sr = float(m["sharpe"])
            except: sr = 0
            st.markdown(f"""**Sharpe Ratio: {m["sharpe"]}**

Risk-adjusted return. Above 1.0 = good, above 2.0 = excellent, below 0 = worse than cash.

{"✅ Solid risk-adjusted performance." if sr >= 1 else "⚠️ Returns don't fully justify the volatility taken." if sr > 0 else "❌ Strategy took on risk without adequate reward."}

**Max Drawdown: {m["max_drawdown"]:.2f}%** — the worst loss you would have experienced before recovery. Ask yourself: could you hold through that?""")
        with i3:
            wr = float(m["win_rate"])
            st.markdown(f"""**Win Rate: {m["win_rate"]:.1f}%** and **{m["num_trades"]} trades**

{"✅ More than half of trades were profitable." if wr >= 50 else "⚠️ Under 50% win rate — but this isn't necessarily bad."}

A 40% win rate can still be very profitable if winning trades are 3x the size of losers. Focus on the **Profit Factor** (avg win / avg loss) rather than win rate alone.

{"High trade count — verify the strategy isn't overtrading." if m["num_trades"] > 60 else "Low trade count — results have wider statistical uncertainty. Try a longer date range." if m["num_trades"] < 8 else "Reasonable trade count for statistical confidence."}""")

    # Charts
    st.markdown('<div class="price-divider">PRICE CHART + TRADE SIGNALS</div>', unsafe_allow_html=True)
    overlays = {}
    if strategy_name == "SMA Crossover":
        overlays[f"SMA {user_params['short']}"] = sma(df["Close"], user_params["short"])
        overlays[f"SMA {user_params['long']}"]  = sma(df["Close"], user_params["long"])
    elif strategy_name in ["EMA Crossover","EMA + RSI Filter"]:
        overlays["Fast EMA"] = ema(df["Close"], user_params.get("ema_fast", user_params.get("short")))
        overlays["Slow EMA"] = ema(df["Close"], user_params.get("ema_slow", user_params.get("long")))
    if   strategy_name == "Bollinger Bands": st.plotly_chart(chart_bollinger(df, bollinger_bands(df["Close"], user_params["window"], user_params["num_std"])), use_container_width=True)
    elif strategy_name == "SuperTrend":      st.plotly_chart(chart_supertrend(df, supertrend(df, user_params["window"], user_params["multiplier"])), use_container_width=True)
    else:                                    st.plotly_chart(chart_candles(df, trades, overlays=overlays or None, title=f"{ticker} — {strategy_name}"), use_container_width=True)
    if strategy_name in ["RSI","RSI + Bollinger Bands","EMA + RSI Filter"]:
        st.plotly_chart(chart_rsi(rsi(df["Close"], user_params.get("rsi_window", user_params.get("window", 14))), user_params.get("oversold", 30), user_params.get("overbought", 70)), use_container_width=True)
    if strategy_name in ["MACD","MACD + SuperTrend"]:
        md = macd(df["Close"], user_params.get("fast", 12), user_params.get("slow", 26))
        st.plotly_chart(chart_macd(md["macd"], md["signal"], md["histogram"]), use_container_width=True)

    st.markdown('<div class="price-divider">PORTFOLIO VALUE OVER TIME</div>', unsafe_allow_html=True)
    st.plotly_chart(chart_portfolio(port, df, float(capital)), use_container_width=True)

    # Trade log
    if not trades.empty:
        st.markdown('<div class="price-divider">TRADE LOG</div>', unsafe_allow_html=True)
        sells = trades[trades["action"].str.contains("SELL")]
        ta, tb, tc_ = st.columns(3)
        ta.markdown(f'<div class="metric-card"><div class="metric-val neu">{len(trades)}</div><div class="metric-lbl">Total Entries / Exits</div></div>', unsafe_allow_html=True)
        if len(sells) > 0 and "profit_pct" in sells.columns:
            wins_  = sells[sells["profit_pct"] > 0]["profit_pct"]
            losses_ = sells[sells["profit_pct"] < 0]["profit_pct"]
            aw = wins_.mean()  if len(wins_)  > 0 else 0
            al = losses_.mean() if len(losses_) > 0 else 0
            tb.markdown(f'<div class="metric-card"><div class="metric-val pos">+{aw:.1f}%</div><div class="metric-lbl">Avg Win</div></div>', unsafe_allow_html=True)
            tc_.markdown(f'<div class="metric-card"><div class="metric-val neg">{al:.1f}%</div><div class="metric-lbl">Avg Loss</div></div>', unsafe_allow_html=True)
        with st.expander(f"View all {len(trades)} trades"):
            d2 = trades.copy()
            d2["price"] = d2["price"].apply(lambda x: f"${x:,.2f}")
            if "profit_pct" in d2.columns:
                d2["profit_pct"] = d2["profit_pct"].apply(lambda x: f"{x:+.2f}%" if pd.notna(x) else "—")
            st.dataframe(d2.set_index("date"), use_container_width=True)

    st.session_state["last_backtest"] = dict(ticker=ticker, strategy=strategy_name, params=user_params, metrics=m)
    st.markdown('<div class="info-box">✓ Results saved. Open AI Assistant to get a full explanation, or AI Analysis for a fundamental stock deep-dive.</div>', unsafe_allow_html=True)

else:
    st.markdown('<div class="price-divider">WHICH STRATEGY SHOULD I PICK?</div>', unsafe_allow_html=True)
    g1, g2, g3 = st.columns(3)
    for col, title, items in [
        (g1, "Just Starting Out", [("SMA Crossover","Visual, easy to understand, great first strategy"),("RSI","Clear rules — buy low RSI, sell high RSI"),("EMA Crossover","SMA but slightly more responsive")]),
        (g2, "Trending Markets",  [("SuperTrend","Clean signals, adapts to volatility"),("MACD + SuperTrend","Double confirmation for strong trends"),("EMA + RSI Filter","Trend direction + momentum gate")]),
        (g3, "Ranging Markets",   [("RSI","Mean reversion in sideways action"),("Bollinger Bands","Price bounces between volatility bands"),("RSI + Bollinger Bands","Two filters = higher quality signals")]),
    ]:
        col.markdown(f'<div style="font-family:IBM Plex Mono,monospace;font-size:0.6rem;color:#3a4558;text-transform:uppercase;letter-spacing:0.15em;margin-bottom:0.8rem;">{title}</div>', unsafe_allow_html=True)
        for name, tip in items:
            col.markdown(f'<div style="padding:0.55rem 0;border-bottom:1px solid #1c2333;"><div style="font-size:0.8rem;color:#cdd5e0;margin-bottom:0.2rem;"><span style="color:#00d68f;margin-right:0.4rem;">—</span>{name}</div><div style="font-size:0.72rem;color:#3a4558;padding-left:0.9rem;">{tip}</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="price-divider">HOW BACKTESTING WORKS</div>', unsafe_allow_html=True)
    h1, h2, h3, h4 = st.columns(4)
    for col, num, title, body in [
        (h1,"01","Download Data","Real historical OHLCV data is pulled from Yahoo Finance for your chosen ticker and date range."),
        (h2,"02","Generate Signals","The strategy runs on the data and outputs a buy (1) or sell (-1) signal for each trading day."),
        (h3,"03","Simulate Trades","The engine walks through history day by day, buying and selling at the closing price based on signals."),
        (h4,"04","Calculate Metrics","Return, drawdown, Sharpe ratio, win rate and every individual trade are computed from the simulation."),
    ]:
        col.markdown(f'<div style="padding:1rem 0;"><div style="font-family:Bebas Neue,sans-serif;font-size:2rem;color:#1c2333;">{num}</div><div style="font-family:IBM Plex Mono,monospace;font-size:0.7rem;color:#00d68f;text-transform:uppercase;margin:0.3rem 0 0.5rem;">{title}</div><div style="font-size:0.78rem;color:#3a4558;line-height:1.65;">{body}</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="warn-box" style="margin-top:0.5rem;">⚠ Backtests assume fills at daily closing price with no slippage, commission, or taxes. Real trading results will differ. Past performance does not guarantee future results.</div>', unsafe_allow_html=True)
