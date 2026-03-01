import streamlit as st
import sys, os
from datetime import date, timedelta
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.data import get_stock_data, get_ticker_info
from utils.strategies import STRATEGY_REGISTRY, run_backtest
from utils.charts import chart_candles, chart_portfolio, chart_rsi, chart_macd, chart_bollinger, chart_supertrend
from utils.indicators import rsi, macd, bollinger_bands, supertrend, sma, ema
from utils.styles import SHARED_CSS

st.set_page_config(page_title="Backtest | 11%", page_icon="🔬", layout="wide", initial_sidebar_state="collapsed")
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

st.markdown('''<div class="page-header"><h1>Backtest Lab</h1><p>Test pre-built strategies against historical price data.</p></div>''', unsafe_allow_html=True)

st.markdown('<div class="config-panel">', unsafe_allow_html=True)
r1,r2,r3,r4,r5 = st.columns([2,1.5,1.5,1.5,2])
with r1: ticker        = st.text_input("Ticker Symbol", value="AAPL").upper().strip()
with r2: start_date    = st.date_input("Start Date", value=date.today()-timedelta(days=365*3))
with r3: end_date      = st.date_input("End Date",   value=date.today())
with r4: capital       = st.number_input("Capital ($)", value=10000, min_value=100, step=1000)
with r5: strategy_name = st.selectbox("Strategy", list(STRATEGY_REGISTRY.keys()))
st.markdown('</div>', unsafe_allow_html=True)

strategy_info = STRATEGY_REGISTRY[strategy_name]
user_params = {}
st.markdown('<div class="config-panel">', unsafe_allow_html=True)
pc = st.columns(4)
if strategy_name == "SMA Crossover":
    with pc[0]: user_params["short"] = st.slider("Short SMA", 5, 50, 20)
    with pc[1]: user_params["long"]  = st.slider("Long SMA", 20, 200, 50)
elif strategy_name == "EMA Crossover":
    with pc[0]: user_params["short"] = st.slider("Short EMA", 5, 50, 12)
    with pc[1]: user_params["long"]  = st.slider("Long EMA", 20, 200, 26)
elif strategy_name == "RSI":
    with pc[0]: user_params["window"]     = st.slider("Period", 5, 30, 14)
    with pc[1]: user_params["oversold"]   = st.slider("Oversold", 10, 45, 30)
    with pc[2]: user_params["overbought"] = st.slider("Overbought", 55, 90, 70)
elif strategy_name == "MACD":
    with pc[0]: user_params["fast"]   = st.slider("Fast", 5, 30, 12)
    with pc[1]: user_params["slow"]   = st.slider("Slow", 15, 60, 26)
    with pc[2]: user_params["signal"] = st.slider("Signal", 3, 20, 9)
elif strategy_name == "Bollinger Bands":
    with pc[0]: user_params["window"]  = st.slider("Period", 5, 50, 20)
    with pc[1]: user_params["num_std"] = st.slider("Std Dev", 1.0, 4.0, 2.0, step=0.1)
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
    st.markdown('<div style="font-family:IBM Plex Mono,monospace;font-size:0.75rem;color:#3a4558;padding:0.5rem 0;">No parameters needed.</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

run_btn = st.button("Run Backtest")

if run_btn:
    with st.spinner(f"Fetching {ticker}..."): df=get_stock_data(ticker,str(start_date),str(end_date))
    if df.empty: st.error("No data found."); st.stop()
    info=get_ticker_info(ticker)
    st.markdown(f'<div style="font-family:IBM Plex Mono,monospace;font-size:0.72rem;color:#3a4558;margin-bottom:1.5rem;">{info.get("name",ticker)} · {info.get("sector","N/A")} · {len(df)} bars · {start_date} → {end_date}</div>', unsafe_allow_html=True)
    try:
        signals=strategy_info["fn"](df,**user_params)
        result=run_backtest(df,signals,float(capital))
    except Exception as e: st.error(f"Error: {e}"); st.stop()
    m=result["metrics"]; port=result["portfolio"]; trades=result["trades"]
    st.markdown('<div class="price-divider">PERFORMANCE</div>', unsafe_allow_html=True)
    cols=st.columns(8)
    def mc(col,val,lbl,fmt="pct"):
        if fmt=="pct": cls="pos" if val>=0 else "neg"; d=f"{val:+.2f}%"
        elif fmt=="usd": cls="neu"; d=f"${val:,.0f}"
        else: cls="neu"; d=str(val)
        col.markdown(f'<div class="metric-card"><div class="metric-val {cls}">{d}</div><div class="metric-lbl">{lbl}</div></div>', unsafe_allow_html=True)
    mc(cols[0],m["total_return"],"Strategy"); mc(cols[1],m["bh_return"],"Buy & Hold")
    mc(cols[2],m["max_drawdown"],"Drawdown"); mc(cols[3],m["final_value"],"Final",fmt="usd")
    mc(cols[4],m["win_rate"],"Win Rate"); mc(cols[5],m["sharpe"],"Sharpe",fmt="raw")
    cols[6].markdown(f'<div class="metric-card"><div class="metric-val neu">{m["num_trades"]}</div><div class="metric-lbl">Trades</div></div>', unsafe_allow_html=True)
    alpha=m["total_return"]-m["bh_return"]
    cols[7].markdown(f'<div class="metric-card"><div class="metric-val {"pos" if alpha>=0 else "neg"}">{alpha:+.2f}%</div><div class="metric-lbl">Alpha</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="price-divider">CHART</div>', unsafe_allow_html=True)
    overlays={}
    if strategy_name=="SMA Crossover":
        overlays[f"SMA {user_params['short']}"]=sma(df["Close"],user_params["short"])
        overlays[f"SMA {user_params['long']}"]=sma(df["Close"],user_params["long"])
    elif strategy_name in ["EMA Crossover","EMA + RSI Filter"]:
        overlays["Fast EMA"]=ema(df["Close"],user_params.get("ema_fast",user_params.get("short")))
        overlays["Slow EMA"]=ema(df["Close"],user_params.get("ema_slow",user_params.get("long")))
    if strategy_name=="Bollinger Bands": st.plotly_chart(chart_bollinger(df,bollinger_bands(df["Close"],user_params["window"],user_params["num_std"])),use_container_width=True)
    elif strategy_name=="SuperTrend": st.plotly_chart(chart_supertrend(df,supertrend(df,user_params["window"],user_params["multiplier"])),use_container_width=True)
    else: st.plotly_chart(chart_candles(df,trades,overlays=overlays if overlays else None,title=f"{ticker} — {strategy_name}"),use_container_width=True)
    if strategy_name in ["RSI","RSI + Bollinger Bands","EMA + RSI Filter"]: st.plotly_chart(chart_rsi(rsi(df["Close"],user_params.get("rsi_window",user_params.get("window",14))),user_params.get("oversold",30),user_params.get("overbought",70)),use_container_width=True)
    if strategy_name in ["MACD","MACD + SuperTrend"]:
        md=macd(df["Close"],user_params.get("fast",12),user_params.get("slow",26))
        st.plotly_chart(chart_macd(md["macd"],md["signal"],md["histogram"]),use_container_width=True)
    st.plotly_chart(chart_portfolio(port,df,float(capital)),use_container_width=True)
    if not trades.empty:
        with st.expander("Trade Log"): st.dataframe(trades.set_index("date"),use_container_width=True)
    st.session_state["last_backtest"]=dict(ticker=ticker,strategy=strategy_name,params=user_params,metrics=m)
else:
    st.markdown('<div class="info-box">Configure your strategy above and click Run Backtest.</div>', unsafe_allow_html=True)
