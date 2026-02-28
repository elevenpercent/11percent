import streamlit as st
import pandas as pd
import sys, os
from datetime import date, timedelta
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.data import get_stock_data
from utils.strategies import run_backtest
from utils.charts import chart_candles, chart_portfolio, chart_rsi, chart_stoch_rsi, chart_macd, chart_bollinger, chart_ichimoku
from utils.indicators import sma, ema, wma, rsi, stoch_rsi, macd, bollinger_bands, supertrend, ichimoku, INDICATOR_INFO

st.set_page_config(page_title="Indicator Test | 11%", page_icon="📊", layout="wide", initial_sidebar_state="collapsed")
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

def build_params(ind_name, prefix):
    info=INDICATOR_INFO[ind_name]; params={}
    if not info["params"]: return params
    cols=st.columns(min(len(info["params"]),4))
    for i,(pk,p) in enumerate(info["params"].items()):
        with cols[i%4]:
            if p["type"]=="int": params[pk]=st.slider(p["label"],p["min"],p["max"],p["default"],key=f"{prefix}_{pk}")
            elif p["type"]=="float": params[pk]=st.slider(p["label"],float(p["min"]),float(p["max"]),float(p["default"]),step=0.1,key=f"{prefix}_{pk}")
    return params

def compute_ind(name,df,params):
    if name=="SMA": return sma(df["Close"],params["window"])
    elif name=="EMA": return ema(df["Close"],params["window"])
    elif name=="WMA": return wma(df["Close"],params["window"])
    elif name=="RSI": return rsi(df["Close"],params["window"])
    elif name=="Stoch RSI": return stoch_rsi(df["Close"],params["rsi_window"],params["stoch_window"],params["smooth_k"],params["smooth_d"])
    elif name=="MACD": return macd(df["Close"],params["fast"],params["slow"],params["signal"])
    elif name=="Bollinger Bands": return bollinger_bands(df["Close"],params["window"],params["num_std"])
    elif name=="SuperTrend": return supertrend(df,params["window"],params["multiplier"])
    elif name=="Ichimoku": return ichimoku(df,params["tenkan_window"],params["kijun_window"],params["senkou_b_window"])

def gen_sigs(name,data,buy_c,sell_c,df,params):
    sig=pd.Series(0,index=df.index)
    if name=="RSI":
        ov=params.get("oversold",30); ob=params.get("overbought",70)
        if buy_c=="RSI below oversold": sig[data<ov]=1
        if buy_c=="RSI crosses above 50": sig[data>50]=1
        if sell_c=="RSI above overbought": sig[data>ob]=-1
        if sell_c=="RSI crosses below 50": sig[data<50]=-1
    elif name=="Stoch RSI":
        k=data["k"]
        if buy_c=="%K crosses above %D": sig[(k>data["d"])&(k.shift()<=data["d"].shift())]=1
        if buy_c=="%K below 20": sig[k<20]=1
        if sell_c=="%K crosses below %D": sig[(k<data["d"])&(k.shift()>=data["d"].shift())]=-1
        if sell_c=="%K above 80": sig[k>80]=-1
    elif name=="MACD":
        m,s=data["macd"],data["signal"]
        if buy_c=="MACD crosses above Signal": sig[(m>s)&(m.shift()<=s.shift())]=1
        if buy_c=="MACD above 0": sig[m>0]=1
        if sell_c=="MACD crosses below Signal": sig[(m<s)&(m.shift()>=s.shift())]=-1
        if sell_c=="MACD below 0": sig[m<0]=-1
    elif name in ["SMA","EMA","WMA"]:
        if buy_c=="Price crosses above MA": sig[(df["Close"]>data)&(df["Close"].shift()<=data.shift())]=1
        if buy_c=="Price above MA": sig[df["Close"]>data]=1
        if sell_c=="Price crosses below MA": sig[(df["Close"]<data)&(df["Close"].shift()>=data.shift())]=-1
        if sell_c=="Price below MA": sig[df["Close"]<data]=-1
    elif name=="Bollinger Bands":
        if buy_c=="Price below lower band": sig[df["Close"]<data["lower"]]=1
        if buy_c=="%B below 0": sig[data["percent_b"]<0]=1
        if sell_c=="Price above upper band": sig[df["Close"]>data["upper"]]=-1
        if sell_c=="%B above 100": sig[data["percent_b"]>100]=-1
    elif name=="SuperTrend":
        if buy_c=="Direction turns bullish": sig[(data["direction"]==1)&(data["direction"].shift()==-1)]=1
        if buy_c=="Price above SuperTrend": sig[df["Close"]>data["supertrend"]]=1
        if sell_c=="Direction turns bearish": sig[(data["direction"]==-1)&(data["direction"].shift()==1)]=-1
        if sell_c=="Price below SuperTrend": sig[df["Close"]<data["supertrend"]]=-1
    elif name=="Ichimoku":
        t,k=data["tenkan_sen"],data["kijun_sen"]; sa,sb=data["senkou_span_a"],data["senkou_span_b"]
        ct=pd.concat([sa,sb],axis=1).max(axis=1); cb=pd.concat([sa,sb],axis=1).min(axis=1)
        if buy_c=="Tenkan crosses above Kijun": sig[(t>k)&(t.shift()<=k.shift())]=1
        if buy_c=="Price above Cloud": sig[df["Close"]>ct]=1
        if sell_c=="Tenkan crosses below Kijun": sig[(t<k)&(t.shift()>=k.shift())]=-1
        if sell_c=="Price below Cloud": sig[df["Close"]<cb]=-1
    return sig

COND={"RSI":{"buy":["RSI below oversold","RSI crosses above 50"],"sell":["RSI above overbought","RSI crosses below 50"]},"Stoch RSI":{"buy":["%K crosses above %D","%K below 20"],"sell":["%K crosses below %D","%K above 80"]},"MACD":{"buy":["MACD crosses above Signal","MACD above 0"],"sell":["MACD crosses below Signal","MACD below 0"]},"SMA":{"buy":["Price crosses above MA","Price above MA"],"sell":["Price crosses below MA","Price below MA"]},"EMA":{"buy":["Price crosses above MA","Price above MA"],"sell":["Price crosses below MA","Price below MA"]},"WMA":{"buy":["Price crosses above MA","Price above MA"],"sell":["Price crosses below MA","Price below MA"]},"Bollinger Bands":{"buy":["Price below lower band","%B below 0"],"sell":["Price above upper band","%B above 100"]},"SuperTrend":{"buy":["Direction turns bullish","Price above SuperTrend"],"sell":["Direction turns bearish","Price below SuperTrend"]},"Ichimoku":{"buy":["Tenkan crosses above Kijun","Price above Cloud"],"sell":["Tenkan crosses below Kijun","Price below Cloud"]}}

st.markdown('''<div class="page-header"><h1>Indicator Test</h1><p>Set buy/sell conditions using single or combo indicators.</p></div>''', unsafe_allow_html=True)

st.markdown('<div class="config-panel">', unsafe_allow_html=True)
sc1,sc2,sc3,sc4,sc5 = st.columns([2,1.5,1.5,1.5,1.5])
with sc1: ticker    = st.text_input("Ticker", value="AAPL").upper().strip()
with sc2: start_date = st.date_input("Start", value=date.today()-timedelta(days=365*2))
with sc3: end_date   = st.date_input("End",   value=date.today())
with sc4: capital    = st.number_input("Capital ($)", value=10000, min_value=100, step=1000)
with sc5: mode       = st.selectbox("Mode", ["Single Indicator","Combo (2–3)"])
st.markdown('</div>', unsafe_allow_html=True)

ind_names=list(INDICATOR_INFO.keys())
if mode=="Single Indicator":
    st.markdown('<div class="config-panel">', unsafe_allow_html=True)
    ic1,ic2,ic3=st.columns(3)
    with ic1: ind1  = st.selectbox("Indicator", ind_names, key="ind1")
    with ic2: buy1  = st.selectbox("Buy When",  COND[ind1]["buy"],  key="buy1")
    with ic3: sell1 = st.selectbox("Sell When", COND[ind1]["sell"], key="sell1")
    params1=build_params(ind1,"p1")
    st.markdown('</div>', unsafe_allow_html=True)
    indicator_config=[{"name":ind1,"params":params1,"buy":buy1,"sell":sell1}]
else:
    num_inds=st.slider("Number of indicators",2,3,2)
    combo_logic=st.radio("Logic",["ALL conditions (AND)","ANY condition (OR)"],horizontal=True)
    indicator_config=[]
    for i in range(num_inds):
        st.markdown(f'<div class="price-divider">INDICATOR {i+1}</div>', unsafe_allow_html=True)
        st.markdown('<div class="config-panel">', unsafe_allow_html=True)
        ic1,ic2,ic3=st.columns(3)
        with ic1: ind  = st.selectbox(f"Indicator {i+1}",ind_names,key=f"ind{i}")
        with ic2: buy  = st.selectbox("Buy When",COND[ind]["buy"],key=f"buy{i}")
        with ic3: sell = st.selectbox("Sell When",COND[ind]["sell"],key=f"sell{i}")
        params=build_params(ind,f"p{i}")
        st.markdown('</div>', unsafe_allow_html=True)
        indicator_config.append({"name":ind,"params":params,"buy":buy,"sell":sell})

run_btn=st.button("Run Test")

if run_btn:
    with st.spinner(f"Loading {ticker}..."): df=get_stock_data(ticker,str(start_date),str(end_date))
    if df.empty: st.stop()
    try:
        ab,as_,comp=[],[],[]
        for cfg in indicator_config:
            d=compute_ind(cfg["name"],df,cfg["params"])
            s=gen_sigs(cfg["name"],d,cfg["buy"],cfg["sell"],df,cfg["params"])
            ab.append(s==1); as_.append(s==-1)
            comp.append({"name":cfg["name"],"data":d,"params":cfg["params"]})
        if mode=="Single Indicator" or "AND" in combo_logic:
            bf=pd.concat(ab,axis=1).all(axis=1); sf=pd.concat(as_,axis=1).all(axis=1)
        else:
            bf=pd.concat(ab,axis=1).any(axis=1); sf=pd.concat(as_,axis=1).any(axis=1)
        combined=pd.Series(0,index=df.index); combined[bf]=1; combined[sf]=-1
        result=run_backtest(df,combined,float(capital))
    except Exception as e: st.error(f"Error: {e}"); st.stop()
    m=result["metrics"]; port=result["portfolio"]; trades=result["trades"]
    st.markdown('<div class="price-divider">PERFORMANCE</div>', unsafe_allow_html=True)
    cols=st.columns(7)
    rows=[(m["total_return"],"Strategy","pct"),(m["bh_return"],"Buy & Hold","pct"),(m["max_drawdown"],"Drawdown","pct"),(m["final_value"],"Final","usd"),(m["win_rate"],"Win Rate","pct"),(m["sharpe"],"Sharpe","raw"),(m["num_trades"],"Trades","int")]
    for col,(val,lbl,fmt) in zip(cols,rows):
        if fmt=="pct": cls="pos" if val>=0 else "neg"; d=f"{val:+.2f}%"
        elif fmt=="usd": cls="neu"; d=f"${val:,.0f}"
        else: cls="neu"; d=f"{val:.2f}" if isinstance(val,float) else str(val)
        col.markdown(f'<div class="metric-card"><div class="metric-val {cls}">{d}</div><div class="metric-lbl">{lbl}</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="price-divider">CHARTS</div>', unsafe_allow_html=True)
    overlays={}
    for c in comp:
        if INDICATOR_INFO[c["name"]]["overlay"]:
            if c["name"] in ["SMA","EMA","WMA"]: overlays[f"{c['name']} {c['params']['window']}"]=c["data"]
            elif c["name"]=="SuperTrend":
                overlays["ST Bull"]=c["data"]["supertrend"].where(c["data"]["direction"]==1)
                overlays["ST Bear"]=c["data"]["supertrend"].where(c["data"]["direction"]==-1)
    st.plotly_chart(chart_candles(df,trades,overlays=overlays if overlays else None,title=f"{ticker} — Indicator Test"),use_container_width=True)
    for c in comp:
        n=c["name"]
        if n=="RSI": st.plotly_chart(chart_rsi(c["data"],c["params"].get("oversold",30),c["params"].get("overbought",70)),use_container_width=True)
        elif n=="Stoch RSI": st.plotly_chart(chart_stoch_rsi(c["data"]["k"],c["data"]["d"]),use_container_width=True)
        elif n=="MACD": st.plotly_chart(chart_macd(c["data"]["macd"],c["data"]["signal"],c["data"]["histogram"]),use_container_width=True)
        elif n=="Bollinger Bands": st.plotly_chart(chart_bollinger(df,c["data"]),use_container_width=True)
        elif n=="Ichimoku": st.plotly_chart(chart_ichimoku(df,c["data"]),use_container_width=True)
    st.plotly_chart(chart_portfolio(port,df,float(capital)),use_container_width=True)
    if not trades.empty:
        with st.expander("Trade Log"): st.dataframe(trades.set_index("date"),use_container_width=True)
    st.session_state["last_backtest"]={"ticker":ticker,"strategy":f"Custom: {chr(43).join([c['name'] for c in indicator_config])}","metrics":m}
else:
    st.markdown('<div class="info-box">Configure your indicators above and click Run Test.</div>', unsafe_allow_html=True)
