import streamlit as st
import sys, os
from datetime import date, timedelta
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.data import get_stock_data, get_ticker_info
from utils.strategies import STRATEGY_REGISTRY, run_backtest
from utils.charts import chart_candles, chart_portfolio, chart_rsi, chart_macd, chart_bollinger, chart_supertrend
from utils.indicators import rsi, macd, bollinger_bands, supertrend, sma, ema

st.set_page_config(page_title="Backtest | 11%", page_icon="🔬", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""<style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=IBM+Plex+Mono:wght@300;400;600;700&family=IBM+Plex+Sans:wght@300;400;600&display=swap');
    :root {
        --bg:#07090d; --surface:#0d1117; --border:#1c2333;
        --green:#00d68f; --red:#ff4757; --text:#cdd5e0; --muted:#3a4558;
        --grid:rgba(255,255,255,0.03);
    }
    /* ── Kill ALL Streamlit chrome ── */
    header[data-testid="stHeader"] { display:none!important; }
    [data-testid="stToolbar"] { display:none!important; }
    [data-testid="stDecoration"] { display:none!important; }
    [data-testid="stSidebar"] { display:none!important; }
    [data-testid="stSidebarNav"] { display:none!important; }
    [data-testid="collapsedControl"] { display:none!important; }
    footer { display:none!important; }
    #MainMenu { display:none!important; }
    .stDeployButton { display:none!important; }
    /* ── Layout ── */
    html,body,[data-testid="stAppViewContainer"],[data-testid="stMain"],.main {
        background-color:var(--bg)!important; color:var(--text)!important;
        font-family:'IBM Plex Sans',sans-serif!important;
    }
    [data-testid="stMain"] {
        background-image:linear-gradient(var(--grid) 1px,transparent 1px),linear-gradient(90deg,var(--grid) 1px,transparent 1px)!important;
        background-size:48px 48px!important;
        padding-top:0!important;
    }
    .block-container { padding-top:0!important; padding-left:2rem!important; padding-right:2rem!important; max-width:100%!important; }
    /* ── Navbar ── */
    .nb { background:#07090d; border-bottom:1px solid #1c2333; padding:0; margin:-1rem -2rem 2rem -2rem; display:flex; align-items:stretch; position:sticky; top:0; z-index:1000; }
    .nb-brand { font-family:'Bebas Neue',sans-serif; font-size:1.7rem; letter-spacing:0.1em; color:var(--text); padding:0.6rem 1.6rem; border-right:1px solid #1c2333; display:flex; align-items:center; flex-shrink:0; }
    .nb-brand .g { color:#00d68f; }
    .nb-brand .r { color:#ff4757; }
    .nb-links { display:flex; align-items:stretch; flex:1; }
    .nb-tag { font-family:'IBM Plex Mono',monospace; font-size:0.58rem; color:#3a4558; letter-spacing:0.15em; padding:0.6rem 1.6rem; display:flex; align-items:center; border-left:1px solid #1c2333; }
    /* Style the st.page_link elements inside the navbar */
    .nb-links [data-testid="stPageLink"] { display:flex; align-items:stretch; }
    .nb-links [data-testid="stPageLink-NavLink"] {
        font-family:'IBM Plex Mono',monospace!important;
        font-size:0.69rem!important;
        font-weight:500!important;
        text-transform:uppercase!important;
        letter-spacing:0.12em!important;
        color:#3a4558!important;
        text-decoration:none!important;
        padding:0 1.1rem!important;
        border-radius:0!important;
        border:none!important;
        border-bottom:2px solid transparent!important;
        background:transparent!important;
        display:flex!important;
        align-items:center!important;
        height:100%!important;
        transition:color 0.15s, border-color 0.15s!important;
        white-space:nowrap!important;
    }
    .nb-links [data-testid="stPageLink-NavLink"]:hover {
        color:#cdd5e0!important;
        background:transparent!important;
        text-decoration:none!important;
        border-bottom:2px solid #3a4558!important;
    }
    .nb-links [data-testid="stPageLink-NavLink"][aria-current="page"] {
        color:#00d68f!important;
        border-bottom:2px solid #00d68f!important;
    }
    /* ── Typography ── */
    h1 { font-family:'Bebas Neue',sans-serif!important; letter-spacing:0.06em; color:var(--text)!important; }
    h2 { font-family:'Bebas Neue',sans-serif!important; }
    h3 { font-family:'IBM Plex Mono',monospace!important; font-size:0.75rem!important; color:var(--green)!important; text-transform:uppercase; letter-spacing:0.15em; }
    /* ── Inputs ── */
    .stTextInput input, .stNumberInput input {
        background:#0d1117!important; border:1px solid #1c2333!important;
        color:#cdd5e0!important; font-family:'IBM Plex Mono',monospace!important;
        font-size:0.85rem!important; border-radius:3px!important;
    }
    .stTextInput input:focus, .stNumberInput input:focus { border-color:#00d68f!important; box-shadow:none!important; }
    div[data-baseweb="select"]>div { background:#0d1117!important; border:1px solid #1c2333!important; color:#cdd5e0!important; font-family:'IBM Plex Mono',monospace!important; border-radius:3px!important; }
    .stDateInput input { background:#0d1117!important; border:1px solid #1c2333!important; color:#cdd5e0!important; font-family:'IBM Plex Mono',monospace!important; border-radius:3px!important; }
    label { font-family:'IBM Plex Mono',monospace!important; font-size:0.68rem!important; color:#3a4558!important; text-transform:uppercase!important; letter-spacing:0.1em!important; }
    /* ── Buttons ── */
    .stButton>button { background:transparent!important; color:#00d68f!important; border:1px solid #00d68f!important; border-radius:3px!important; font-family:'IBM Plex Mono',monospace!important; font-weight:600!important; font-size:0.78rem!important; letter-spacing:0.1em!important; padding:0.45rem 1.4rem!important; transition:all 0.15s!important; text-transform:uppercase!important; }
    .stButton>button:hover { background:#00d68f!important; color:#000!important; }
    /* ── Cards ── */
    .metric-card { background:#0d1117; border:1px solid #1c2333; padding:1rem; border-radius:4px; text-align:center; }
    .metric-val { font-family:'IBM Plex Mono',monospace; font-size:1.1rem; font-weight:700; }
    .metric-lbl { font-family:'IBM Plex Mono',monospace; font-size:0.55rem; color:#3a4558; text-transform:uppercase; margin-top:0.3rem; }
    .pos{color:#00d68f;} .neg{color:#ff4757;} .neu{color:#cdd5e0;}
    /* ── Config panel ── */
    .config-panel { background:#0d1117; border:1px solid #1c2333; border-radius:6px; padding:1.4rem 1.4rem 0.4rem 1.4rem; margin-bottom:1.5rem; }
    /* ── Dividers ── */
    .price-divider { display:flex; align-items:center; gap:1rem; margin:1.5rem 0 1rem 0; font-family:'IBM Plex Mono',monospace; font-size:0.62rem; color:#3a4558; letter-spacing:0.12em; }
    .price-divider::before,.price-divider::after { content:''; flex:1; height:1px; background:#1c2333; }
    /* ── Page header ── */
    .page-header { padding:1.5rem 0 1rem 0; border-bottom:1px solid #1c2333; margin-bottom:1.5rem; }
    .page-header h1 { font-size:2.8rem!important; margin:0!important; }
    .page-header p { color:#3a4558; font-size:0.85rem; margin:0.3rem 0 0 0; }
    /* ── Boxes ── */
    .info-box { background:#071a0f; border:1px solid #0d3320; border-radius:4px; padding:0.8rem 1rem; font-size:0.82rem; color:#00d68f; font-family:'IBM Plex Mono',monospace; }
    .warn-box { background:#1a0a08; border:1px solid #3a1008; border-radius:4px; padding:0.8rem 1rem; font-size:0.82rem; color:#ff4757; font-family:'IBM Plex Mono',monospace; }
    /* ── Chat ── */
    .chat-user { background:#0d1117; border:1px solid #1c2333; border-radius:10px 10px 3px 10px; padding:1rem 1.2rem; margin:0.6rem 0; }
    .chat-ai { background:#071a0f; border:1px solid #0d3320; border-radius:10px 10px 10px 3px; padding:1rem 1.2rem; margin:0.6rem 0; }
    .chat-lbl { font-family:'IBM Plex Mono',monospace; font-size:0.65rem; text-transform:uppercase; letter-spacing:0.12em; color:#3a4558; margin-bottom:0.4rem; }
    /* ── Ticker ── */
    .ticker-wrap { overflow:hidden; background:#0d1117; border-bottom:1px solid #1c2333; padding:0.4rem 0; margin:-2rem -2rem 2rem -2rem; }
    .ticker-tape { display:inline-flex; animation:ticker 35s linear infinite; white-space:nowrap; }
    .ticker-item { font-family:'IBM Plex Mono',monospace; font-size:0.68rem; padding:0 1.5rem; letter-spacing:0.05em; }
    .t-up{color:#00d68f;} .t-dn{color:#ff4757;} .t-sym{color:#cdd5e0;margin-right:0.4rem;}
    @keyframes ticker{0%{transform:translateX(0)}100%{transform:translateX(-50%)}}
    /* ── Misc ── */
    ::-webkit-scrollbar{width:4px;} ::-webkit-scrollbar-track{background:#07090d;} ::-webkit-scrollbar-thumb{background:#263045;border-radius:2px;}
    hr{border-color:#1c2333!important;}
    [data-testid="stExpander"]{background:#0d1117!important;border:1px solid #1c2333!important;border-radius:4px!important;}
</style>""", unsafe_allow_html=True)
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
