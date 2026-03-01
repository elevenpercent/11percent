import streamlit as st
import pandas as pd
import sys, os
from datetime import date, timedelta
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.data import get_stock_data
from utils.strategies import run_backtest
from utils.charts import chart_candles, chart_portfolio, chart_rsi, chart_stoch_rsi, chart_macd, chart_bollinger, chart_ichimoku
from utils.indicators import sma, ema, wma, rsi, stoch_rsi, macd, bollinger_bands, supertrend, ichimoku, INDICATOR_INFO
from utils.styles import SHARED_CSS

st.set_page_config(page_title="Indicators | 11%", layout="wide", initial_sidebar_state="collapsed")
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

IND_GUIDE = {
    "SMA":            {"cat":"Trend","desc":"Arithmetic average of price over N periods. Smooths noise to show direction. Equal weight to all bars.","use":"Trend direction, support/resistance, crossover signals."},
    "EMA":            {"cat":"Trend","desc":"Like SMA but weights recent prices more heavily. Faster to react to new moves.","use":"Same as SMA but preferred for shorter-term signals."},
    "WMA":            {"cat":"Trend","desc":"Weighted moving average — most recent bar gets the highest weight, linearly decreasing back.","use":"More responsive than SMA, smoother than EMA."},
    "RSI":            {"cat":"Momentum","desc":"Compares average gains vs average losses over N periods on a 0–100 scale. Below 30 = oversold, above 70 = overbought.","use":"Spotting exhaustion moves, divergences, momentum shifts."},
    "Stoch RSI":      {"cat":"Momentum","desc":"RSI of the RSI — extremely sensitive. Gives overbought/oversold signals faster but with more noise.","use":"Short-term timing within already-identified trends."},
    "MACD":           {"cat":"Momentum","desc":"Difference between two EMAs plotted with a signal line. Histogram shows acceleration of momentum.","use":"Trend direction, momentum crossovers, divergences."},
    "Bollinger Bands":{"cat":"Volatility","desc":"20-period SMA with upper/lower bands at ±2 standard deviations. Bands expand in volatile markets, contract in calm ones.","use":"Mean reversion setups, volatility breakouts, squeeze detection."},
    "SuperTrend":     {"cat":"Trend","desc":"ATR-based trailing stop that flips green/red depending on price position. Extremely clean buy/sell signals.","use":"Trend following, trailing stops, direction filter for other indicators."},
    "Ichimoku":       {"cat":"Trend","desc":"Japanese cloud system showing trend, momentum, and support/resistance on a single chart. Looks complex but becomes intuitive.","use":"Complete trend analysis — above cloud = bullish, below = bearish."},
}
CAT_COLOR = {"Trend":"#4da6ff","Momentum":"#b388ff","Volatility":"#ff9f43"}

def build_params(ind_name, prefix):
    info = INDICATOR_INFO[ind_name]; params = {}
    if not info["params"]: return params
    cols = st.columns(min(len(info["params"]), 4))
    for i, (pk, p) in enumerate(info["params"].items()):
        with cols[i%4]:
            if p["type"] == "int":   params[pk] = st.slider(p["label"], p["min"], p["max"], p["default"], key=f"{prefix}_{pk}")
            elif p["type"] == "float": params[pk] = st.slider(p["label"], float(p["min"]), float(p["max"]), float(p["default"]), step=0.1, key=f"{prefix}_{pk}")
    return params

def compute_ind(name, df, params):
    if name == "SMA":            return sma(df["Close"], params["window"])
    elif name == "EMA":          return ema(df["Close"], params["window"])
    elif name == "WMA":          return wma(df["Close"], params["window"])
    elif name == "RSI":          return rsi(df["Close"], params["window"])
    elif name == "Stoch RSI":    return stoch_rsi(df["Close"], params["rsi_window"], params["stoch_window"], params["smooth_k"], params["smooth_d"])
    elif name == "MACD":         return macd(df["Close"], params["fast"], params["slow"], params["signal"])
    elif name == "Bollinger Bands": return bollinger_bands(df["Close"], params["window"], params["num_std"])
    elif name == "SuperTrend":   return supertrend(df, params["window"], params["multiplier"])
    elif name == "Ichimoku":     return ichimoku(df, params["tenkan_window"], params["kijun_window"], params["senkou_b_window"])

def gen_sigs(name, data, buy_c, sell_c, df, params):
    sig = pd.Series(0, index=df.index)
    if name == "RSI":
        ov = params.get("oversold", 30); ob = params.get("overbought", 70)
        if buy_c  == "RSI below oversold":    sig[data < ov] = 1
        if buy_c  == "RSI crosses above 50":  sig[data > 50] = 1
        if sell_c == "RSI above overbought":  sig[data > ob] = -1
        if sell_c == "RSI crosses below 50":  sig[data < 50] = -1
    elif name == "Stoch RSI":
        k = data["k"]
        if buy_c  == "%K crosses above %D":   sig[(k > data["d"]) & (k.shift() <= data["d"].shift())] = 1
        if buy_c  == "%K below 20":           sig[k < 20] = 1
        if sell_c == "%K crosses below %D":   sig[(k < data["d"]) & (k.shift() >= data["d"].shift())] = -1
        if sell_c == "%K above 80":           sig[k > 80] = -1
    elif name == "MACD":
        m, s = data["macd"], data["signal"]
        if buy_c  == "MACD crosses above Signal": sig[(m > s) & (m.shift() <= s.shift())] = 1
        if buy_c  == "MACD above 0":              sig[m > 0] = 1
        if sell_c == "MACD crosses below Signal": sig[(m < s) & (m.shift() >= s.shift())] = -1
        if sell_c == "MACD below 0":              sig[m < 0] = -1
    elif name in ["SMA","EMA","WMA"]:
        if buy_c  == "Price crosses above MA": sig[(df["Close"] > data) & (df["Close"].shift() <= data.shift())] = 1
        if buy_c  == "Price above MA":         sig[df["Close"] > data] = 1
        if sell_c == "Price crosses below MA": sig[(df["Close"] < data) & (df["Close"].shift() >= data.shift())] = -1
        if sell_c == "Price below MA":         sig[df["Close"] < data] = -1
    elif name == "Bollinger Bands":
        if buy_c  == "Price below lower band": sig[df["Close"] < data["lower"]] = 1
        if buy_c  == "%B below 0":             sig[data["percent_b"] < 0] = 1
        if sell_c == "Price above upper band": sig[df["Close"] > data["upper"]] = -1
        if sell_c == "%B above 100":           sig[data["percent_b"] > 100] = -1
    elif name == "SuperTrend":
        if buy_c  == "Direction turns bullish": sig[(data["direction"]==1) & (data["direction"].shift()==-1)] = 1
        if buy_c  == "Price above SuperTrend":  sig[df["Close"] > data["supertrend"]] = 1
        if sell_c == "Direction turns bearish": sig[(data["direction"]==-1) & (data["direction"].shift()==1)] = -1
        if sell_c == "Price below SuperTrend":  sig[df["Close"] < data["supertrend"]] = -1
    elif name == "Ichimoku":
        t, k = data["tenkan_sen"], data["kijun_sen"]
        sa, sb = data["senkou_span_a"], data["senkou_span_b"]
        ct = pd.concat([sa,sb], axis=1).max(axis=1); cb = pd.concat([sa,sb], axis=1).min(axis=1)
        if buy_c  == "Tenkan crosses above Kijun": sig[(t > k) & (t.shift() <= k.shift())] = 1
        if buy_c  == "Price above Cloud":          sig[df["Close"] > ct] = 1
        if sell_c == "Tenkan crosses below Kijun": sig[(t < k) & (t.shift() >= k.shift())] = -1
        if sell_c == "Price below Cloud":          sig[df["Close"] < cb] = -1
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
    "Ichimoku":       {"buy":["Tenkan crosses above Kijun","Price above Cloud"], "sell":["Tenkan crosses below Kijun","Price below Cloud"]},
}

st.markdown('''<div class="page-header"><h1>Indicator Lab</h1><p>Build your own buy/sell rules using any combination of indicators. Test single indicators or combine up to 3 with AND/OR logic.</p></div>''', unsafe_allow_html=True)

# Indicator reference
with st.expander("Indicator Reference — what does each one do?"):
    cats = {}
    for name, info in IND_GUIDE.items():
        cats.setdefault(info["cat"], []).append((name, info))
    for cat, items in cats.items():
        cc = CAT_COLOR.get(cat, "#cdd5e0")
        st.markdown(f'<div style="font-family:IBM Plex Mono,monospace;font-size:0.6rem;color:{cc};text-transform:uppercase;letter-spacing:0.15em;margin:0.8rem 0 0.5rem 0;border-bottom:1px solid #1c2333;padding-bottom:0.3rem;">{cat}</div>', unsafe_allow_html=True)
        cols = st.columns(3)
        for i, (name, info) in enumerate(items):
            cols[i%3].markdown(f'<div style="padding:0.6rem 0;border-bottom:1px solid #07090d;margin-bottom:0.3rem;"><div style="font-size:0.78rem;color:#cdd5e0;margin-bottom:0.25rem;">{name}</div><div style="font-size:0.72rem;color:#3a4558;line-height:1.6;margin-bottom:0.2rem;">{info["desc"]}</div><div style="font-size:0.7rem;color:#00d68f;"><span style="color:#3a4558;">Best for: </span>{info["use"]}</div></div>', unsafe_allow_html=True)

# ── Setup ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="price-divider">SETUP</div>', unsafe_allow_html=True)
st.markdown('<div class="config-panel">', unsafe_allow_html=True)
sc1,sc2,sc3,sc4,sc5 = st.columns([2,1.5,1.5,1.5,1.5])
with sc1: ticker     = st.text_input("Ticker", value="AAPL").upper().strip()
with sc2: start_date = st.date_input("Start", value=date.today()-timedelta(days=365*2))
with sc3: end_date   = st.date_input("End",   value=date.today())
with sc4: capital    = st.number_input("Capital ($)", value=10000, min_value=100, step=1000)
with sc5: mode       = st.selectbox("Mode", ["Single Indicator","Combo (2–3 indicators)"])
st.markdown('</div>', unsafe_allow_html=True)

# ── Indicator config ──────────────────────────────────────────────────────────
ind_names = list(INDICATOR_INFO.keys())
indicator_config = []

if mode == "Single Indicator":
    st.markdown('<div class="price-divider">INDICATOR</div>', unsafe_allow_html=True)
    st.markdown('<div class="config-panel">', unsafe_allow_html=True)
    ic1,ic2,ic3 = st.columns(3)
    with ic1: ind1  = st.selectbox("Indicator",  ind_names, key="ind1")
    with ic2: buy1  = st.selectbox("Buy When",   COND[ind1]["buy"],  key="buy1")
    with ic3: sell1 = st.selectbox("Sell When",  COND[ind1]["sell"], key="sell1")
    g = IND_GUIDE.get(ind1, {})
    if g:
        cc = CAT_COLOR.get(g["cat"], "#cdd5e0")
        st.markdown(f'<div style="font-size:0.78rem;color:#3a4558;margin:0.4rem 0 0.6rem 0;">{g["desc"]} <span style="color:{cc};">[{g["cat"]}]</span></div>', unsafe_allow_html=True)
    params1 = build_params(ind1, "p1")
    st.markdown('</div>', unsafe_allow_html=True)
    indicator_config = [{"name":ind1,"params":params1,"buy":buy1,"sell":sell1}]
else:
    num_inds = st.slider("How many indicators?", 2, 3, 2)
    st.markdown('<div class="config-panel" style="margin-bottom:1rem;">', unsafe_allow_html=True)
    st.markdown('<div style="font-family:IBM Plex Mono,monospace;font-size:0.62rem;color:#3a4558;text-transform:uppercase;letter-spacing:0.12em;margin-bottom:0.6rem;">Logic — how should conditions combine?</div>', unsafe_allow_html=True)
    combo_logic = st.radio("Combination logic", ["ALL must trigger (AND — fewer but higher quality signals)","ANY can trigger (OR — more signals, more risk of false entries)"], label_visibility="collapsed")
    st.markdown('<div style="font-size:0.75rem;color:#3a4558;margin-top:0.3rem;">' + ("AND logic: both indicators must agree. Reduces false signals significantly. Expect fewer total trades." if "AND" in combo_logic else "OR logic: either indicator can trigger. More opportunities but also more noise. Best when indicators are very different types.") + '</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    for i in range(num_inds):
        st.markdown(f'<div class="price-divider">INDICATOR {i+1}</div>', unsafe_allow_html=True)
        st.markdown('<div class="config-panel">', unsafe_allow_html=True)
        ic1,ic2,ic3 = st.columns(3)
        with ic1: ind  = st.selectbox(f"Indicator {i+1}", ind_names, key=f"ind{i}")
        with ic2: buy  = st.selectbox("Buy When", COND[ind]["buy"],  key=f"buy{i}")
        with ic3: sell = st.selectbox("Sell When",COND[ind]["sell"], key=f"sell{i}")
        g = IND_GUIDE.get(ind, {})
        if g:
            cc = CAT_COLOR.get(g["cat"], "#cdd5e0")
            st.markdown(f'<div style="font-size:0.78rem;color:#3a4558;margin:0.3rem 0 0.5rem;">{g["desc"]} <span style="color:{cc};">[{g["cat"]}]</span></div>', unsafe_allow_html=True)
        params = build_params(ind, f"p{i}")
        st.markdown('</div>', unsafe_allow_html=True)
        indicator_config.append({"name":ind,"params":params,"buy":buy,"sell":sell})

run_btn = st.button("Run Test", use_container_width=False)

if run_btn:
    with st.spinner(f"Loading {ticker}..."):
        df = get_stock_data(ticker, str(start_date), str(end_date))
    if df.empty: st.stop()
    try:
        ab, as_, comp = [], [], []
        for cfg in indicator_config:
            d = compute_ind(cfg["name"], df, cfg["params"])
            s = gen_sigs(cfg["name"], d, cfg["buy"], cfg["sell"], df, cfg["params"])
            ab.append(s==1); as_.append(s==-1)
            comp.append({"name":cfg["name"],"data":d,"params":cfg["params"]})
        if mode=="Single Indicator" or "AND" in combo_logic:
            bf = pd.concat(ab, axis=1).all(axis=1); sf = pd.concat(as_, axis=1).all(axis=1)
        else:
            bf = pd.concat(ab, axis=1).any(axis=1); sf = pd.concat(as_, axis=1).any(axis=1)
        combined = pd.Series(0, index=df.index); combined[bf]=1; combined[sf]=-1
        result = run_backtest(df, combined, float(capital))
    except Exception as e: st.error(f"Error: {e}"); st.stop()

    m = result["metrics"]; port = result["portfolio"]; trades = result["trades"]

    st.markdown('<div class="price-divider">RESULTS</div>', unsafe_allow_html=True)
    alpha = m["total_return"] - m["bh_return"]
    c = st.columns(8)
    items = [(m["total_return"],"Strategy","pct"),(m["bh_return"],"Buy & Hold","pct"),(alpha,"Alpha","pct"),(m["max_drawdown"],"Drawdown","pct"),(m["final_value"],"Final Value","usd"),(m["win_rate"],"Win Rate","pct"),(m["sharpe"],"Sharpe","raw"),(m["num_trades"],"Trades","int")]
    for col,(val,lbl,fmt) in zip(c,items):
        if fmt=="pct":   cls="pos" if val>=0 else "neg"; d=f"{val:+.2f}%"
        elif fmt=="usd": cls="neu"; d=f"${val:,.0f}"
        elif fmt=="raw":
            try: cls="pos" if float(val)>=1 else ("neg" if float(val)<0 else "neu")
            except: cls="neu"
            d=str(val)
        else: cls="neu"; d=str(val)
        col.markdown(f'<div class="metric-card"><div class="metric-val {cls}">{d}</div><div class="metric-lbl">{lbl}</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="price-divider">CHARTS</div>', unsafe_allow_html=True)
    overlays = {}
    for c_ in comp:
        if INDICATOR_INFO[c_["name"]]["overlay"]:
            if c_["name"] in ["SMA","EMA","WMA"]: overlays[f"{c_['name']} {c_['params']['window']}"] = c_["data"]
            elif c_["name"] == "SuperTrend":
                overlays["ST Bull"] = c_["data"]["supertrend"].where(c_["data"]["direction"]==1)
                overlays["ST Bear"] = c_["data"]["supertrend"].where(c_["data"]["direction"]==-1)
    st.plotly_chart(chart_candles(df, trades, overlays=overlays or None, title=f"{ticker} — Custom Strategy"), use_container_width=True)
    for c_ in comp:
        n = c_["name"]
        if n=="RSI":            st.plotly_chart(chart_rsi(c_["data"], c_["params"].get("oversold",30), c_["params"].get("overbought",70)), use_container_width=True)
        elif n=="Stoch RSI":    st.plotly_chart(chart_stoch_rsi(c_["data"]["k"], c_["data"]["d"]), use_container_width=True)
        elif n=="MACD":         st.plotly_chart(chart_macd(c_["data"]["macd"], c_["data"]["signal"], c_["data"]["histogram"]), use_container_width=True)
        elif n=="Bollinger Bands": st.plotly_chart(chart_bollinger(df, c_["data"]), use_container_width=True)
        elif n=="Ichimoku":     st.plotly_chart(chart_ichimoku(df, c_["data"]), use_container_width=True)
    st.plotly_chart(chart_portfolio(port, df, float(capital)), use_container_width=True)

    if not trades.empty:
        with st.expander(f"Trade Log ({len(trades)} trades)"):
            st.dataframe(trades.set_index("date"), use_container_width=True)
    st.session_state["last_backtest"] = {"ticker":ticker,"strategy":f"Custom: {' + '.join([c_['name'] for c_ in comp])}","metrics":m}
    st.markdown('<div class="info-box">✓ Results saved. Open AI Assistant to get these explained.</div>', unsafe_allow_html=True)

else:
    st.markdown('<div class="price-divider">COMBINATION IDEAS TO TRY</div>', unsafe_allow_html=True)
    ci1, ci2, ci3 = st.columns(3)
    for col, title, combos in [
        (ci1, "Classic Combos", [("RSI + Bollinger Bands","Mean reversion with double confirmation — great starting point"),("EMA + MACD","Trend direction + momentum confirmation"),("SMA + RSI","Simple trend filter + overbought/oversold exits")]),
        (ci2, "Trend Combos",   [("SuperTrend + MACD","Strong trend confirmation setup"),("EMA + SuperTrend","Two trend tools agreeing = high confidence"),("SMA + SuperTrend","Slow trend filter + fast ATR-based signal")]),
        (ci3, "Advanced",       [("RSI + Stoch RSI + MACD","Triple momentum confirmation — very selective"),("Ichimoku + RSI","Cloud for trend, RSI for entry timing"),("BB + Stoch RSI","Volatility band with overbought/oversold timing")]),
    ]:
        col.markdown(f'<div style="font-family:IBM Plex Mono,monospace;font-size:0.6rem;color:#3a4558;text-transform:uppercase;letter-spacing:0.15em;margin-bottom:0.8rem;">{title}</div>', unsafe_allow_html=True)
        for combo, tip in combos:
            col.markdown(f'<div style="padding:0.55rem 0;border-bottom:1px solid #1c2333;"><div style="font-size:0.78rem;color:#cdd5e0;margin-bottom:0.2rem;">{combo}</div><div style="font-size:0.72rem;color:#3a4558;">{tip}</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="info-box" style="margin-top:1rem;">Select your indicator, set buy/sell conditions and click Run Test to see results.</div>', unsafe_allow_html=True)
