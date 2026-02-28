import streamlit as st
import pandas as pd
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from datetime import date, timedelta
from utils.data import get_stock_data
from utils.strategies import run_backtest
from utils.charts import chart_candles, chart_portfolio, chart_rsi, chart_stoch_rsi, chart_macd, chart_bollinger, chart_supertrend, chart_ichimoku
from utils.indicators import sma, ema, wma, rsi, stoch_rsi, macd, bollinger_bands, atr, supertrend, vwap, obv, ichimoku, INDICATOR_INFO

st.set_page_config(page_title="Indicator Test | 11%", page_icon="📊", layout="wide")
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

    .metric-card { background:#0d1117; border:1px solid #1c2333; padding:1rem; border-radius:4px; text-align:center; }
    .metric-val { font-family:'IBM Plex Mono',monospace; font-size:1.1rem; font-weight:700; }
    .metric-lbl { font-family:'IBM Plex Mono',monospace; font-size:0.55rem; color:#3a4558; text-transform:uppercase; margin-top:0.3rem; }
    .pos { color:#00d68f; } .neg { color:#ff4757; } .neu { color:#cdd5e0; }
    .page-header { border-left:3px solid #00d68f; padding-left:1rem; margin-bottom:1.5rem; }
    .page-header p { color:#3a4558; font-size:0.88rem; margin-top:0.2rem; }
    .info-box { background:#071a0f; border:1px solid #0d3320; border-radius:6px; padding:0.8rem 1rem; font-size:0.82rem; color:#00d68f; font-family:'IBM Plex Mono',monospace; }
    .warn-box { background:#1a0a08; border:1px solid #3a1008; border-radius:6px; padding:0.8rem 1rem; font-size:0.82rem; color:#ff4757; font-family:'IBM Plex Mono',monospace; }
    .chat-user { background:#0d1117; border:1px solid #1c2333; border-radius:10px 10px 3px 10px; padding:1rem 1.2rem; margin:0.6rem 0; }
    .chat-ai { background:#071a0f; border:1px solid #0d3320; border-radius:10px 10px 10px 3px; padding:1rem 1.2rem; margin:0.6rem 0; }
    .chat-lbl { font-family:'IBM Plex Mono',monospace; font-size:0.65rem; text-transform:uppercase; letter-spacing:0.12em; color:#3a4558; margin-bottom:0.4rem; }
</style>
""", unsafe_allow_html=True)

def build_indicator_params(ind_name, key_prefix):
    info = INDICATOR_INFO[ind_name]; params = {}
    for pk, p in info["params"].items():
        if p["type"] == "int":
            params[pk] = st.slider(p["label"], p["min"], p["max"], p["default"], key=f"{key_prefix}_{pk}")
        elif p["type"] == "float":
            params[pk] = st.slider(p["label"], float(p["min"]), float(p["max"]), float(p["default"]), step=0.1, key=f"{key_prefix}_{pk}")
    return params

def compute_indicator(ind_name, df, params):
    if ind_name=="SMA": return sma(df["Close"], params["window"])
    elif ind_name=="EMA": return ema(df["Close"], params["window"])
    elif ind_name=="WMA": return wma(df["Close"], params["window"])
    elif ind_name=="RSI": return rsi(df["Close"], params["window"])
    elif ind_name=="Stoch RSI": return stoch_rsi(df["Close"], params["rsi_window"], params["stoch_window"], params["smooth_k"], params["smooth_d"])
    elif ind_name=="MACD": return macd(df["Close"], params["fast"], params["slow"], params["signal"])
    elif ind_name=="Bollinger Bands": return bollinger_bands(df["Close"], params["window"], params["num_std"])
    elif ind_name=="SuperTrend": return supertrend(df, params["window"], params["multiplier"])
    elif ind_name=="Ichimoku": return ichimoku(df, params["tenkan_window"], params["kijun_window"], params["senkou_b_window"])
    return None

def generate_signals(ind_name, ind_data, condition_buy, condition_sell, df, params):
    sig = pd.Series(0, index=df.index)
    if ind_name=="RSI":
        ov=params.get("oversold",30); ob=params.get("overbought",70)
        if condition_buy=="RSI below oversold": sig[ind_data<ov]=1
        if condition_buy=="RSI crosses above 50": sig[ind_data>50]=1
        if condition_sell=="RSI above overbought": sig[ind_data>ob]=-1
        if condition_sell=="RSI crosses below 50": sig[ind_data<50]=-1
    elif ind_name=="Stoch RSI":
        k=ind_data["k"]
        if condition_buy=="%K crosses above %D": sig[(k>ind_data["d"])&(k.shift()<=ind_data["d"].shift())]=1
        if condition_buy=="%K below 20": sig[k<20]=1
        if condition_sell=="%K crosses below %D": sig[(k<ind_data["d"])&(k.shift()>=ind_data["d"].shift())]=-1
        if condition_sell=="%K above 80": sig[k>80]=-1
    elif ind_name=="MACD":
        m,s=ind_data["macd"],ind_data["signal"]
        if condition_buy=="MACD crosses above Signal": sig[(m>s)&(m.shift()<=s.shift())]=1
        if condition_buy=="MACD above 0": sig[m>0]=1
        if condition_sell=="MACD crosses below Signal": sig[(m<s)&(m.shift()>=s.shift())]=-1
        if condition_sell=="MACD below 0": sig[m<0]=-1
    elif ind_name in ["SMA","EMA","WMA"]:
        if condition_buy=="Price crosses above MA": sig[(df["Close"]>ind_data)&(df["Close"].shift()<=ind_data.shift())]=1
        if condition_buy=="Price above MA": sig[df["Close"]>ind_data]=1
        if condition_sell=="Price crosses below MA": sig[(df["Close"]<ind_data)&(df["Close"].shift()>=ind_data.shift())]=-1
        if condition_sell=="Price below MA": sig[df["Close"]<ind_data]=-1
    elif ind_name=="Bollinger Bands":
        if condition_buy=="Price below lower band": sig[df["Close"]<ind_data["lower"]]=1
        if condition_buy=="%B below 0": sig[ind_data["percent_b"]<0]=1
        if condition_sell=="Price above upper band": sig[df["Close"]>ind_data["upper"]]=-1
        if condition_sell=="%B above 100": sig[ind_data["percent_b"]>100]=-1
    elif ind_name=="SuperTrend":
        if condition_buy=="Direction turns bullish": sig[(ind_data["direction"]==1)&(ind_data["direction"].shift()==-1)]=1
        if condition_buy=="Price above SuperTrend": sig[df["Close"]>ind_data["supertrend"]]=1
        if condition_sell=="Direction turns bearish": sig[(ind_data["direction"]==-1)&(ind_data["direction"].shift()==1)]=-1
        if condition_sell=="Price below SuperTrend": sig[df["Close"]<ind_data["supertrend"]]=-1
    elif ind_name=="Ichimoku":
        t,k=ind_data["tenkan_sen"],ind_data["kijun_sen"]
        sa,sb=ind_data["senkou_span_a"],ind_data["senkou_span_b"]
        ct=pd.concat([sa,sb],axis=1).max(axis=1); cb=pd.concat([sa,sb],axis=1).min(axis=1)
        if condition_buy=="Tenkan crosses above Kijun": sig[(t>k)&(t.shift()<=k.shift())]=1
        if condition_buy=="Price above Cloud": sig[df["Close"]>ct]=1
        if condition_sell=="Tenkan crosses below Kijun": sig[(t<k)&(t.shift()>=k.shift())]=-1
        if condition_sell=="Price below Cloud": sig[df["Close"]<cb]=-1
    return sig

CONDITIONS = {
    "RSI":{"buy":["RSI below oversold","RSI crosses above 50"],"sell":["RSI above overbought","RSI crosses below 50"]},
    "Stoch RSI":{"buy":["%K crosses above %D","%K below 20"],"sell":["%K crosses below %D","%K above 80"]},
    "MACD":{"buy":["MACD crosses above Signal","MACD above 0"],"sell":["MACD crosses below Signal","MACD below 0"]},
    "SMA":{"buy":["Price crosses above MA","Price above MA"],"sell":["Price crosses below MA","Price below MA"]},
    "EMA":{"buy":["Price crosses above MA","Price above MA"],"sell":["Price crosses below MA","Price below MA"]},
    "WMA":{"buy":["Price crosses above MA","Price above MA"],"sell":["Price crosses below MA","Price below MA"]},
    "Bollinger Bands":{"buy":["Price below lower band","%B below 0"],"sell":["Price above upper band","%B above 100"]},
    "SuperTrend":{"buy":["Direction turns bullish","Price above SuperTrend"],"sell":["Direction turns bearish","Price below SuperTrend"]},
    "Ichimoku":{"buy":["Tenkan crosses above Kijun","Price above Cloud"],"sell":["Tenkan crosses below Kijun","Price below Cloud"]},
}

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("assets/logo.png", width=120)
    st.markdown('<div style="padding-top:1rem;padding-bottom:0.5rem;border-top:1px solid #1c2333;"><div style="font-family:IBM Plex Mono,monospace;font-size:0.6rem;color:#3a4558;text-transform:uppercase;letter-spacing:0.18em;margin-bottom:0.5rem;">Navigation</div></div>', unsafe_allow_html=True)
    st.page_link("app.py",                       label="🏠  Home")
    st.page_link("pages/1_Backtest.py",          label="🔬  Backtest")
    st.page_link("pages/2_Indicator_Test.py",    label="📊  Indicator Test")
    st.page_link("pages/3_Replay.py",            label="▶   Replay")
    st.page_link("pages/4_Analysis.py",          label="🧠  Analysis")
    st.page_link("pages/5_Assistant.py",         label="💬  Assistant")
    st.markdown('<div style="position:absolute;bottom:1.5rem;left:1rem;right:1rem;text-align:center;font-family:IBM Plex Mono,monospace;font-size:0.6rem;color:#3a4558;text-transform:uppercase;letter-spacing:0.1em;">Free · Open Source</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown('<div style="font-family:IBM Plex Mono,monospace;font-size:0.6rem;color:#3a4558;text-transform:uppercase;letter-spacing:0.18em;margin-bottom:0.5rem;">Settings</div>', unsafe_allow_html=True)
    ticker = st.text_input("Ticker", value="AAPL").upper().strip()
    col1, col2 = st.columns(2)
    with col1: start_date = st.date_input("Start", value=date.today() - timedelta(days=365*2))
    with col2: end_date   = st.date_input("End",   value=date.today())
    capital  = st.number_input("Capital ($)", value=10000, min_value=100, step=1000)
    mode     = st.radio("Mode", ["Single Indicator", "Combo (2–3 Indicators)"], horizontal=True)
    ind_names = list(INDICATOR_INFO.keys())
    run_btn  = st.button("▶  RUN TEST", use_container_width=True)

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown('''<div class="page-header"><h1>INDICATOR TEST</h1><p>Set buy/sell conditions using single or combo indicators. Max 3 in combo mode.</p></div>''', unsafe_allow_html=True)

if mode == "Single Indicator":
    st.markdown('<div class="price-divider">INDICATOR</div>', unsafe_allow_html=True)
    col_sel, col_buy, col_sell = st.columns(3)
    with col_sel: ind1  = st.selectbox("Indicator", ind_names, key="ind1")
    with col_buy: buy1  = st.selectbox("Buy When",  CONDITIONS[ind1]["buy"],  key="buy1")
    with col_sell: sell1 = st.selectbox("Sell When", CONDITIONS[ind1]["sell"], key="sell1")
    with st.expander("⚙️ Parameters"): params1 = build_indicator_params(ind1, "p1")
    indicator_config = [{"name": ind1, "params": params1, "buy": buy1, "sell": sell1}]
else:
    num_indicators = st.slider("Number of indicators to combine", 2, 3, 2)
    combo_logic    = st.radio("Combo Logic", ["ALL conditions must be met (AND)", "ANY condition met (OR)"], horizontal=True)
    indicator_config = []
    for i in range(num_indicators):
        st.markdown(f'<div class="price-divider">INDICATOR {i+1}</div>', unsafe_allow_html=True)
        col_sel, col_buy, col_sell = st.columns(3)
        with col_sel:  ind  = st.selectbox(f"Indicator {i+1}", ind_names, key=f"ind{i}")
        with col_buy:  buy  = st.selectbox("Buy When",  CONDITIONS[ind]["buy"],  key=f"buy{i}")
        with col_sell: sell = st.selectbox("Sell When", CONDITIONS[ind]["sell"], key=f"sell{i}")
        with st.expander(f"⚙️ Parameters — Indicator {i+1}"): params = build_indicator_params(ind, f"p{i}")
        indicator_config.append({"name": ind, "params": params, "buy": buy, "sell": sell})

if run_btn:
    with st.spinner(f"Loading {ticker}..."):
        df = get_stock_data(ticker, str(start_date), str(end_date))
    if df.empty: st.stop()
    with st.spinner("Computing indicators..."):
        try:
            all_buy, all_sell, computed = [], [], []
            for cfg in indicator_config:
                ind_data = compute_indicator(cfg["name"], df, cfg["params"])
                sigs = generate_signals(cfg["name"], ind_data, cfg["buy"], cfg["sell"], df, cfg["params"])
                all_buy.append(sigs==1); all_sell.append(sigs==-1)
                computed.append({"name": cfg["name"], "data": ind_data, "params": cfg["params"]})
            if mode=="Single Indicator" or "AND" in combo_logic:
                buy_f=pd.concat(all_buy,axis=1).all(axis=1); sell_f=pd.concat(all_sell,axis=1).all(axis=1)
            else:
                buy_f=pd.concat(all_buy,axis=1).any(axis=1); sell_f=pd.concat(all_sell,axis=1).any(axis=1)
            combined=pd.Series(0,index=df.index); combined[buy_f]=1; combined[sell_f]=-1
            result = run_backtest(df, combined, float(capital))
        except Exception as e:
            st.error(f"Error: {e}"); st.stop()
    m=result["metrics"]; port=result["portfolio"]; trades=result["trades"]
    st.markdown('<div class="price-divider">PERFORMANCE</div>', unsafe_allow_html=True)
    cols = st.columns(7)
    data = [(m["total_return"],"Strategy","pct"),(m["bh_return"],"Buy & Hold","pct"),(m["max_drawdown"],"Drawdown","pct"),(m["final_value"],"Final Value","usd"),(m["win_rate"],"Win Rate","pct"),(m["sharpe"],"Sharpe","raw"),(m["num_trades"],"Trades","int")]
    for col,(val,lbl,fmt) in zip(cols,data):
        if fmt=="pct": cls="pos" if val>=0 else "neg"; disp=f"{val:+.2f}%"
        elif fmt=="usd": cls="neu"; disp=f"${val:,.0f}"
        else: cls="neu"; disp=f"{val:.2f}" if isinstance(val,float) else str(val)
        col.markdown(f'<div class="metric-card"><div class="metric-val {cls}">{disp}</div><div class="metric-lbl">{lbl}</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="price-divider">CHARTS</div>', unsafe_allow_html=True)
    overlays={}
    for c in computed:
        if INDICATOR_INFO[c["name"]]["overlay"]:
            if c["name"] in ["SMA","EMA","WMA"]: overlays[f"{c['name']} {c['params']['window']}"] = c["data"]
            elif c["name"]=="SuperTrend":
                overlays["ST Bull"]=c["data"]["supertrend"].where(c["data"]["direction"]==1)
                overlays["ST Bear"]=c["data"]["supertrend"].where(c["data"]["direction"]==-1)
    st.plotly_chart(chart_candles(df, trades, overlays=overlays if overlays else None, title=f"{ticker} — Indicator Test"), use_container_width=True)
    for c in computed:
        n=c["name"]
        if n=="RSI": st.plotly_chart(chart_rsi(c["data"],c["params"].get("oversold",30),c["params"].get("overbought",70)), use_container_width=True)
        elif n=="Stoch RSI": st.plotly_chart(chart_stoch_rsi(c["data"]["k"],c["data"]["d"]), use_container_width=True)
        elif n=="MACD": st.plotly_chart(chart_macd(c["data"]["macd"],c["data"]["signal"],c["data"]["histogram"]), use_container_width=True)
        elif n=="Bollinger Bands": st.plotly_chart(chart_bollinger(df,c["data"]), use_container_width=True)
        elif n=="Ichimoku": st.plotly_chart(chart_ichimoku(df,c["data"]), use_container_width=True)
    st.plotly_chart(chart_portfolio(port, df, float(capital)), use_container_width=True)
    if not trades.empty:
        with st.expander("📋 TRADE LOG"): st.dataframe(trades.set_index("date"), use_container_width=True)
    st.session_state["last_backtest"] = {"ticker":ticker,"strategy":f"Custom: {' + '.join([c['name'] for c in indicator_config])}","params":{c["name"]:c["params"] for c in indicator_config},"metrics":m}
else:
    st.markdown('<div class="info-box">← Pick your indicator(s), set your conditions, and hit RUN TEST.</div>', unsafe_allow_html=True)
