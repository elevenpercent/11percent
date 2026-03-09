import streamlit as st
import pandas as pd
import sys, os
from datetime import date, timedelta
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.data import get_stock_data
from utils.strategies import run_backtest
from utils.charts import chart_candles, chart_portfolio, chart_rsi, chart_stoch_rsi, chart_macd, chart_bollinger, chart_ichimoku
from utils.indicators import sma, ema, wma, rsi, stoch_rsi, macd, bollinger_bands, supertrend, ichimoku, cci, williams_r, donchian_channels, keltner_channels, hull_ma, parabolic_sar, INDICATOR_INFO
from utils.styles import SHARED_CSS

st.set_page_config(page_title="Indicators | 11%", layout="wide", initial_sidebar_state="collapsed")
st.markdown(SHARED_CSS, unsafe_allow_html=True)

def navbar():
    st.markdown('<div class="nb"><div class="nb-brand"><span class="g">11</span><span class="r">%</span></div><div class="nb-links">', unsafe_allow_html=True)
    c = st.columns([1,1,1,1,1,1,1])
    with c[0]: st.page_link("app.py",                    label="Home")
    with c[1]: st.page_link("pages/1_Backtest.py",       label="Backtest")
    with c[2]: st.page_link("pages/2_Indicator_Test.py", label="Indicators")
    with c[3]: st.page_link("pages/3_Replay.py",         label="Replay")
    with c[4]: st.page_link("pages/4_Analysis.py",       label="Analysis")
    with c[5]: st.page_link("pages/6_Earnings.py",       label="Earnings")
    with c[6]: st.page_link("pages/5_Assistant.py",      label="Coach")
    st.markdown('</div><div class="nb-tag">FREE * OPEN SOURCE</div></div>', unsafe_allow_html=True)
navbar()

def build_params(ind_name, prefix):
    info = INDICATOR_INFO[ind_name]; params = {}
    if not info["params"]: return params
    cols = st.columns(min(len(info["params"]), 4))
    for i, (pk, p) in enumerate(info["params"].items()):
        with cols[i%4]:
            if p["type"]=="int":   params[pk] = st.slider(p["label"], p["min"], p["max"], p["default"], key=f"{prefix}_{pk}")
            elif p["type"]=="float": params[pk] = st.slider(p["label"], float(p["min"]), float(p["max"]), float(p["default"]), step=0.1, key=f"{prefix}_{pk}")
    return params

def compute_ind(name, df, params):
    if name=="SMA":             return sma(df["Close"], params["window"])
    elif name=="EMA":           return ema(df["Close"], params["window"])
    elif name=="WMA":           return wma(df["Close"], params["window"])
    elif name=="RSI":           return rsi(df["Close"], params["window"])
    elif name=="Stoch RSI":     return stoch_rsi(df["Close"], params["rsi_window"], params["stoch_window"], params["smooth_k"], params["smooth_d"])
    elif name=="MACD":          return macd(df["Close"], params["fast"], params["slow"], params["signal"])
    elif name=="Bollinger Bands": return bollinger_bands(df["Close"], params["window"], params["num_std"])
    elif name=="SuperTrend":    return supertrend(df, params["window"], params["multiplier"])
    elif name=="Ichimoku":      return ichimoku(df, params["tenkan_window"], params["kijun_window"], params["senkou_b_window"])
    elif name=="CCI":           return cci(df, params["window"])
    elif name=="Williams %R":   return williams_r(df, params["window"])
    elif name=="Donchian":      return donchian_channels(df, params["window"])
    elif name=="Keltner":       return keltner_channels(df, params["ema_window"], params["atr_window"], params["multiplier"])
    elif name=="Hull MA":       return hull_ma(df["Close"], params["window"])
    elif name=="Parabolic SAR": return parabolic_sar(df, params["af_start"], params["af_max"])

def gen_sigs(name, data, buy_c, sell_c, df, params):
    sig = pd.Series(0, index=df.index)
    if name=="RSI":
        ov=params.get("oversold",30); ob=params.get("overbought",70)
        if buy_c=="RSI below oversold":    sig[data<ov]=1
        if buy_c=="RSI crosses above 50":  sig[data>50]=1
        if sell_c=="RSI above overbought": sig[data>ob]=-1
        if sell_c=="RSI crosses below 50": sig[data<50]=-1
    elif name=="Stoch RSI":
        k=data["k"]
        if buy_c=="%K crosses above %D":   sig[(k>data["d"])&(k.shift()<=data["d"].shift())]=1
        if buy_c=="%K below 20":           sig[k<20]=1
        if sell_c=="%K crosses below %D":  sig[(k<data["d"])&(k.shift()>=data["d"].shift())]=-1
        if sell_c=="%K above 80":          sig[k>80]=-1
    elif name=="MACD":
        m_,s_=data["macd"],data["signal"]
        if buy_c=="MACD crosses above Signal":  sig[(m_>s_)&(m_.shift()<=s_.shift())]=1
        if buy_c=="MACD above 0":               sig[m_>0]=1
        if sell_c=="MACD crosses below Signal": sig[(m_<s_)&(m_.shift()>=s_.shift())]=-1
        if sell_c=="MACD below 0":              sig[m_<0]=-1
    elif name in ["SMA","EMA","WMA"]:
        if buy_c=="Price crosses above MA":  sig[(df["Close"]>data)&(df["Close"].shift()<=data.shift())]=1
        if buy_c=="Price above MA":          sig[df["Close"]>data]=1
        if sell_c=="Price crosses below MA": sig[(df["Close"]<data)&(df["Close"].shift()>=data.shift())]=-1
        if sell_c=="Price below MA":         sig[df["Close"]<data]=-1
    elif name=="Bollinger Bands":
        if buy_c=="Price below lower band":  sig[df["Close"]<data["lower"]]=1
        if buy_c=="%B below 0":              sig[data["percent_b"]<0]=1
        if sell_c=="Price above upper band": sig[df["Close"]>data["upper"]]=-1
        if sell_c=="%B above 100":           sig[data["percent_b"]>100]=-1
    elif name=="SuperTrend":
        if buy_c=="Direction turns bullish": sig[(data["direction"]==1)&(data["direction"].shift()==-1)]=1
        if buy_c=="Price above SuperTrend":  sig[df["Close"]>data["supertrend"]]=1
        if sell_c=="Direction turns bearish":sig[(data["direction"]==-1)&(data["direction"].shift()==1)]=-1
        if sell_c=="Price below SuperTrend": sig[df["Close"]<data["supertrend"]]=-1
    elif name=="Ichimoku":
        t,k_=data["tenkan_sen"],data["kijun_sen"]
        sa,sb=data["senkou_span_a"],data["senkou_span_b"]
        ct=pd.concat([sa,sb],axis=1).max(axis=1); cb=pd.concat([sa,sb],axis=1).min(axis=1)
        if buy_c=="Tenkan crosses above Kijun":  sig[(t>k_)&(t.shift()<=k_.shift())]=1
        if buy_c=="Price above Cloud":           sig[df["Close"]>ct]=1
        if sell_c=="Tenkan crosses below Kijun": sig[(t<k_)&(t.shift()>=k_.shift())]=-1
        if sell_c=="Price below Cloud":          sig[df["Close"]<cb]=-1
    elif name=="CCI":
        if buy_c=="CCI crosses above -100": sig[(data>-100)&(data.shift()<=-100)]=1
        if buy_c=="CCI below -100":         sig[data<-100]=1
        if sell_c=="CCI crosses below 100": sig[(data<100)&(data.shift()>=100)]=-1
        if sell_c=="CCI above 100":         sig[data>100]=-1
    elif name=="Williams %R":
        if buy_c=="%R below -80":            sig[data<-80]=1
        if buy_c=="%R crosses above -80":    sig[(data>-80)&(data.shift()<=-80)]=1
        if sell_c=="%R above -20":           sig[data>-20]=-1
        if sell_c=="%R crosses below -20":   sig[(data<-20)&(data.shift()>=-20)]=-1
    elif name=="Donchian":
        if buy_c=="Price breaks upper channel":  sig[df["Close"]>=data["upper"]]=1
        if buy_c=="Price above middle":          sig[df["Close"]>data["middle"]]=1
        if sell_c=="Price breaks lower channel": sig[df["Close"]<=data["lower"]]=-1
        if sell_c=="Price below middle":         sig[df["Close"]<data["middle"]]=-1
    elif name=="Keltner":
        if buy_c=="Price below lower band":  sig[df["Close"]<data["lower"]]=1
        if buy_c=="Price above middle":      sig[df["Close"]>data["middle"]]=1
        if sell_c=="Price above upper band": sig[df["Close"]>data["upper"]]=-1
        if sell_c=="Price below middle":     sig[df["Close"]<data["middle"]]=-1
    elif name=="Hull MA":
        if buy_c=="Price crosses above HMA": sig[(df["Close"]>data)&(df["Close"].shift()<=data.shift())]=1
        if buy_c=="HMA slope turns up":      sig[(data>data.shift())&(data.shift()<=data.shift(2))]=1
        if sell_c=="Price crosses below HMA":sig[(df["Close"]<data)&(df["Close"].shift()>=data.shift())]=-1
        if sell_c=="HMA slope turns down":   sig[(data<data.shift())&(data.shift()>=data.shift(2))]=-1
    elif name=="Parabolic SAR":
        if buy_c=="SAR turns bullish":      sig[(data["direction"]==1)&(data["direction"].shift()==-1)]=1
        if buy_c=="Price above SAR":        sig[df["Close"]>data["sar"]]=1
        if sell_c=="SAR turns bearish":     sig[(data["direction"]==-1)&(data["direction"].shift()==1)]=-1
        if sell_c=="Price below SAR":       sig[df["Close"]<data["sar"]]=-1
    return sig

COND = {
    "RSI":            {"buy":["RSI below oversold","RSI crosses above 50"],     "sell":["RSI above overbought","RSI crosses below 50"]},
    "Stoch RSI":      {"buy":["%K crosses above %D","%K below 20"],             "sell":["%K crosses below %D","%K above 80"]},
    "MACD":           {"buy":["MACD crosses above Signal","MACD above 0"],      "sell":["MACD crosses below Signal","MACD below 0"]},
    "SMA":            {"buy":["Price crosses above MA","Price above MA"],        "sell":["Price crosses below MA","Price below MA"]},
    "EMA":            {"buy":["Price crosses above MA","Price above MA"],        "sell":["Price crosses below MA","Price below MA"]},
    "WMA":            {"buy":["Price crosses above MA","Price above MA"],        "sell":["Price crosses below MA","Price below MA"]},
    "Bollinger Bands":{"buy":["Price below lower band","%B below 0"],           "sell":["Price above upper band","%B above 100"]},
    "SuperTrend":     {"buy":["Direction turns bullish","Price above SuperTrend"],"sell":["Direction turns bearish","Price below SuperTrend"]},
    "Ichimoku":       {"buy":["Tenkan crosses above Kijun","Price above Cloud"],   "sell":["Tenkan crosses below Kijun","Price below Cloud"]},
    "CCI":            {"buy":["CCI crosses above -100","CCI below -100"],         "sell":["CCI crosses below 100","CCI above 100"]},
    "Williams %R":    {"buy":["%R below -80","%R crosses above -80"],             "sell":["%R above -20","%R crosses below -20"]},
    "Donchian":       {"buy":["Price breaks upper channel","Price above middle"],  "sell":["Price breaks lower channel","Price below middle"]},
    "Keltner":        {"buy":["Price below lower band","Price above middle"],      "sell":["Price above upper band","Price below middle"]},
    "Hull MA":        {"buy":["Price crosses above HMA","HMA slope turns up"],     "sell":["Price crosses below HMA","HMA slope turns down"]},
    "Parabolic SAR":  {"buy":["SAR turns bullish","Price above SAR"],              "sell":["SAR turns bearish","Price below SAR"]},
}

st.markdown('<div class="page-header"><h1>Indicator Lab</h1><p>Set your own buy/sell rules using any indicator - or combine up to 3 with AND/OR logic.</p></div>', unsafe_allow_html=True)

# -- Setup ----------------------------------------------------------------------
st.markdown('<div class="config-panel">', unsafe_allow_html=True)
s1,s2,s3,s4,s5 = st.columns([2,1.5,1.5,1.5,1.5])
with s1: ticker     = st.text_input("Ticker", value="AAPL").upper().strip()
with s2: start_date = st.date_input("From",   value=date.today()-timedelta(days=365*2))
with s3: end_date   = st.date_input("To",     value=date.today())
with s4: capital    = st.number_input("Capital ($)", value=10000, min_value=100, step=1000)
with s5: mode       = st.selectbox("Mode", ["Single","Combo (2-3)"])
st.markdown('</div>', unsafe_allow_html=True)

ind_names = list(INDICATOR_INFO.keys())
indicator_config = []

if mode == "Single":
    st.markdown('<div class="config-panel">', unsafe_allow_html=True)
    i1,i2,i3 = st.columns(3)
    with i1: ind1  = st.selectbox("Indicator", ind_names, key="ind1")
    with i2: buy1  = st.selectbox("Buy when",  COND[ind1]["buy"],  key="buy1")
    with i3: sell1 = st.selectbox("Sell when", COND[ind1]["sell"], key="sell1")
    params1 = build_params(ind1, "p1")
    st.markdown('</div>', unsafe_allow_html=True)
    indicator_config = [{"name":ind1,"params":params1,"buy":buy1,"sell":sell1}]
else:
    n = st.slider("Number of indicators", 2, 3, 2)
    st.markdown('<div class="config-panel" style="margin-bottom:1rem;">', unsafe_allow_html=True)
    combo_logic = st.radio("Logic", ["AND - all must agree (fewer, higher-quality signals)","OR - any can trigger (more signals, more noise)"], label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)
    for i in range(n):
        st.markdown(f'<div class="divider">Indicator {i+1}</div>', unsafe_allow_html=True)
        st.markdown('<div class="config-panel">', unsafe_allow_html=True)
        ic1,ic2,ic3 = st.columns(3)
        with ic1: ind  = st.selectbox(f"Indicator {i+1}", ind_names, key=f"ind{i}")
        with ic2: buy  = st.selectbox("Buy when",  COND[ind]["buy"],  key=f"buy{i}")
        with ic3: sell = st.selectbox("Sell when", COND[ind]["sell"], key=f"sell{i}")
        params = build_params(ind, f"p{i}")
        st.markdown('</div>', unsafe_allow_html=True)
        indicator_config.append({"name":ind,"params":params,"buy":buy,"sell":sell})

run_btn = st.button("Run Test", type="primary")

if not run_btn:
    st.markdown('<div class="divider">Combinations to try</div>', unsafe_allow_html=True)
    ci1, ci2, ci3 = st.columns(3)
    for col, title, combos in [
        (ci1, "Classic",  [("RSI + BB","Mean reversion with confirmation"),("EMA + MACD","Trend + momentum"),("SMA + RSI","Filter + oscillator")]),
        (ci2, "Trending", [("SuperTrend + MACD","Strong confirmation"),("EMA + SuperTrend","Two trend tools"),("SMA + SuperTrend","Slow filter + ATR signal")]),
        (ci3, "Advanced", [("RSI + Stoch RSI + MACD","Triple momentum"),("Ichimoku + RSI","Cloud + timing"),("BB + Stoch RSI","Volatility + oversold")]),
    ]:
        col.markdown(f'<div style="background:#0d1117;border:1px solid #1a2235;border-radius:8px;padding:1.2rem;">', unsafe_allow_html=True)
        col.markdown(f'<div style="font-family:IBM Plex Mono,monospace;font-size:0.62rem;color:#3a4558;text-transform:uppercase;letter-spacing:0.15em;margin-bottom:0.8rem;">{title}</div>', unsafe_allow_html=True)
        for combo, tip in combos:
            col.markdown(f'<div class="row-item"><div><div style="font-size:0.82rem;color:#e2e8f0;">{combo}</div><div style="font-size:0.74rem;color:#3a4558;margin-top:0.1rem;">{tip}</div></div></div>', unsafe_allow_html=True)
        col.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# -- Run ------------------------------------------------------------------------
with st.spinner(f"Loading {ticker}?"):
    df = get_stock_data(ticker, str(start_date), str(end_date))
if df.empty: st.stop()

try:
    ab,as_,comp=[],[],[]
    for cfg in indicator_config:
        d = compute_ind(cfg["name"], df, cfg["params"])
        s = gen_sigs(cfg["name"], d, cfg["buy"], cfg["sell"], df, cfg["params"])
        ab.append(s==1); as_.append(s==-1)
        comp.append({"name":cfg["name"],"data":d,"params":cfg["params"]})
    if mode=="Single" or "AND" in combo_logic:
        bf=pd.concat(ab,axis=1).all(axis=1); sf=pd.concat(as_,axis=1).all(axis=1)
    else:
        bf=pd.concat(ab,axis=1).any(axis=1); sf=pd.concat(as_,axis=1).any(axis=1)
    combined=pd.Series(0,index=df.index); combined[bf]=1; combined[sf]=-1
    result=run_backtest(df,combined,float(capital))
except Exception as e: st.error(f"Error: {e}"); st.stop()

m=result["metrics"]; port=result["portfolio"]; trades=result["trades"]
alpha = m["total_return"] - m["bh_return"]

st.markdown('<div class="divider">Results</div>', unsafe_allow_html=True)
cols=st.columns(8)
for col,(val,lbl,fmt_) in zip(cols,[
    (m["total_return"],"Strategy","pct"),(m["bh_return"],"Buy & Hold","pct"),
    (alpha,"Alpha","pct"),(m["max_drawdown"],"Drawdown","pct"),
    (m["final_value"],"Final Value","usd"),(m["win_rate"],"Win Rate","pct"),
    (m["sharpe"],"Sharpe","raw"),(m["num_trades"],"Trades","int")
]):
    if fmt_=="pct":   cls="pos" if val>=0 else "neg"; d=f"{val:+.2f}%"
    elif fmt_=="usd": cls="neu"; d=f"${val:,.0f}"
    elif fmt_=="raw":
        try: cls="pos" if float(val)>=1 else ("neg" if float(val)<0 else "neu")
        except: cls="neu"
        d=str(val)
    else: cls="neu"; d=str(val)
    col.markdown(f'<div class="metric-card"><div class="metric-val {cls}">{d}</div><div class="metric-lbl">{lbl}</div></div>', unsafe_allow_html=True)

st.markdown('<div class="divider">Charts</div>', unsafe_allow_html=True)
overlays={}
for c_ in comp:
    if INDICATOR_INFO[c_["name"]]["overlay"]:
        if c_["name"] in ["SMA","EMA","WMA"]: overlays[f"{c_['name']} {c_['params']['window']}"]=c_["data"]
        elif c_["name"]=="SuperTrend":
            overlays["ST Bull"]=c_["data"]["supertrend"].where(c_["data"]["direction"]==1)
            overlays["ST Bear"]=c_["data"]["supertrend"].where(c_["data"]["direction"]==-1)
st.plotly_chart(chart_candles(df,trades,overlays=overlays or None,title=f"{ticker} - Custom"),use_container_width=True)
for c_ in comp:
    n=c_["name"]
    if n=="RSI":             st.plotly_chart(chart_rsi(c_["data"],c_["params"].get("oversold",30),c_["params"].get("overbought",70)),use_container_width=True)
    elif n=="Stoch RSI":     st.plotly_chart(chart_stoch_rsi(c_["data"]["k"],c_["data"]["d"]),use_container_width=True)
    elif n=="MACD":          st.plotly_chart(chart_macd(c_["data"]["macd"],c_["data"]["signal"],c_["data"]["histogram"]),use_container_width=True)
    elif n=="Bollinger Bands": st.plotly_chart(chart_bollinger(df,c_["data"]),use_container_width=True)
    elif n=="Ichimoku":      st.plotly_chart(chart_ichimoku(df,c_["data"]),use_container_width=True)
st.plotly_chart(chart_portfolio(port,df,float(capital)),use_container_width=True)

if not trades.empty:
    with st.expander(f"Trade Log ({len(trades)} trades)"):
        st.dataframe(trades.set_index("date"),use_container_width=True)
st.session_state["last_backtest"]={"ticker":ticker,"strategy":f"Custom: {' + '.join([c_['name'] for c_ in comp])}","metrics":m}
st.markdown('<div class="info-box">Results saved - open AI Coach to get these explained.</div>', unsafe_allow_html=True)
