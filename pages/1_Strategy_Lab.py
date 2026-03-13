import streamlit as st
import sys, os, pandas as pd
from datetime import date, timedelta
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.styles import SHARED_CSS
from utils.nav import navbar
from utils.data import get_stock_data, get_ticker_info
from utils.strategies import STRATEGY_REGISTRY, run_backtest
from utils.charts import chart_portfolio, build_tv_chart
from utils.indicators import (
    sma, ema, wma, rsi, stoch_rsi, macd, bollinger_bands, supertrend,
    ichimoku, cci, williams_r, donchian_channels, keltner_channels,
    hull_ma, parabolic_sar, INDICATOR_INFO
)

st.set_page_config(page_title="Strategy Lab | 11%", layout="wide", initial_sidebar_state="collapsed")
st.markdown(SHARED_CSS, unsafe_allow_html=True)
navbar()

st.markdown("""
<div class="page-header">
    <div class="page-header-eyebrow">Backtest Engine</div>
    <h1>Strategy Lab</h1>
    <p>Test prebuilt strategies against real data — or build your own signal logic from 15 indicators with AND/OR combos.</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["⚡  Prebuilt Strategies", "🔬  Custom Signal Builder"])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — PREBUILT STRATEGIES
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    STRAT_META = {
        "SMA Crossover":         {"tag":"Trend",       "level":"Beginner",     "color":"#4da6ff", "desc":"Buys when the fast MA crosses above the slow one. Simple, visual, works best in trending markets."},
        "EMA Crossover":         {"tag":"Trend",       "level":"Beginner",     "color":"#4da6ff", "desc":"Same as SMA but weights recent prices more heavily — catches turns slightly earlier."},
        "RSI":                   {"tag":"Mean Rev.",   "level":"Beginner",     "color":"#b388ff", "desc":"Buys oversold (RSI < 30) and sells overbought (RSI > 70). Works in ranging markets."},
        "MACD":                  {"tag":"Momentum",    "level":"Intermediate", "color":"#ff9f43", "desc":"Momentum crossover strategy. Catches accelerating trends, lags in fast markets."},
        "Bollinger Bands":       {"tag":"Mean Rev.",   "level":"Intermediate", "color":"#b388ff", "desc":"Buys at the lower volatility band, sells at the upper, betting on mean reversion."},
        "SuperTrend":            {"tag":"Trend",       "level":"Intermediate", "color":"#4da6ff", "desc":"ATR-based system with clear green/red direction signal. One of the cleanest trend indicators."},
        "RSI + Bollinger Bands": {"tag":"Combo",       "level":"Intermediate", "color":"#00d68f", "desc":"Both RSI and BB must confirm before entering. Fewer trades but significantly higher quality."},
        "EMA + RSI Filter":      {"tag":"Combo",       "level":"Advanced",     "color":"#00d68f", "desc":"EMA crossover for direction, RSI for momentum confirmation. High quality signals."},
        "MACD + SuperTrend":     {"tag":"Combo",       "level":"Advanced",     "color":"#00d68f", "desc":"Both must agree before entering. Very patient — best in strong, clear trends."},
    }

    c1, c2, c3, c4, c5 = st.columns([2, 1.5, 1.5, 1.5, 2])
    with c1: ticker_bt      = st.text_input("Ticker", value="AAPL", key="bt_ticker", help="AAPL, TSLA, SPY, BTC-USD").upper().strip()
    with c2: start_bt       = st.date_input("From",  value=date.today()-timedelta(days=365*3), key="bt_start")
    with c3: end_bt         = st.date_input("To",    value=date.today(), key="bt_end")
    with c4: capital_bt     = st.number_input("Capital ($)", value=10000, min_value=100, step=1000, key="bt_cap")
    with c5: strategy_name  = st.selectbox("Strategy", list(STRATEGY_REGISTRY.keys()), key="bt_strat")

    meta = STRAT_META.get(strategy_name, {})
    if meta:
        level_color = {"Beginner":"#00d68f","Intermediate":"#ffd166","Advanced":"#ff4757"}.get(meta["level"],"#cdd5e0")
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:0.75rem;padding:0.7rem 0 0.4rem 0;border-top:1px solid #1a2235;margin-top:0.4rem;">
            <span class="tag" style="background:{meta['color']}18;color:{meta['color']};border:1px solid {meta['color']}30;">{meta['tag']}</span>
            <span class="tag" style="background:{level_color}18;color:{level_color};border:1px solid {level_color}30;">{meta['level']}</span>
            <span style="font-size:0.82rem;color:#8892a4;">{meta['desc']}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="section-hdr"><div class="section-hdr-label">Parameters</div></div>', unsafe_allow_html=True)
    user_params = {}
    pc = st.columns(4)
    if strategy_name == "SMA Crossover":
        with pc[0]: user_params["short"] = st.slider("Short SMA", 5, 50, 20, key="bt_p1")
        with pc[1]: user_params["long"]  = st.slider("Long SMA", 20, 200, 50, key="bt_p2")
        with pc[2]: st.caption("Tip: Classic 20/50 or 50/200. Wider gap = fewer signals.")
    elif strategy_name == "EMA Crossover":
        with pc[0]: user_params["short"] = st.slider("Short EMA", 5, 50, 12, key="bt_p1")
        with pc[1]: user_params["long"]  = st.slider("Long EMA", 20, 200, 26, key="bt_p2")
        with pc[2]: st.caption("Tip: 12/26 is the standard MACD base.")
    elif strategy_name == "RSI":
        with pc[0]: user_params["window"]     = st.slider("Period", 5, 30, 14, key="bt_p1")
        with pc[1]: user_params["oversold"]   = st.slider("Oversold", 10, 45, 30, key="bt_p2")
        with pc[2]: user_params["overbought"] = st.slider("Overbought", 55, 90, 70, key="bt_p3")
        with pc[3]: st.caption("Tip: Try 20/80 for fewer, stronger signals.")
    elif strategy_name == "MACD":
        with pc[0]: user_params["fast"]   = st.slider("Fast", 5, 30, 12, key="bt_p1")
        with pc[1]: user_params["slow"]   = st.slider("Slow", 15, 60, 26, key="bt_p2")
        with pc[2]: user_params["signal"] = st.slider("Signal", 3, 20, 9, key="bt_p3")
    elif strategy_name == "Bollinger Bands":
        with pc[0]: user_params["window"]  = st.slider("Period", 5, 50, 20, key="bt_p1")
        with pc[1]: user_params["num_std"] = st.slider("Std Dev", 1.0, 4.0, 2.0, step=0.1, key="bt_p2")
    elif strategy_name == "SuperTrend":
        with pc[0]: user_params["window"]     = st.slider("ATR Period", 5, 30, 10, key="bt_p1")
        with pc[1]: user_params["multiplier"] = st.slider("Multiplier", 1.0, 6.0, 3.0, step=0.5, key="bt_p2")
        with pc[2]: st.caption("Tip: Higher multiplier = fewer signals, less whipsaws.")
    elif strategy_name == "RSI + Bollinger Bands":
        with pc[0]: user_params["rsi_window"] = st.slider("RSI Period", 5, 30, 14, key="bt_p1")
        with pc[1]: user_params["bb_window"]  = st.slider("BB Period", 10, 50, 20, key="bt_p2")
        with pc[2]: user_params["oversold"]   = st.slider("RSI Oversold", 20, 45, 35, key="bt_p3")
        with pc[3]: user_params["overbought"] = st.slider("RSI Overbought", 55, 85, 65, key="bt_p4")
    elif strategy_name == "EMA + RSI Filter":
        with pc[0]: user_params["ema_fast"]   = st.slider("Fast EMA", 3, 30, 9, key="bt_p1")
        with pc[1]: user_params["ema_slow"]   = st.slider("Slow EMA", 10, 60, 21, key="bt_p2")
        with pc[2]: user_params["rsi_window"] = st.slider("RSI Period", 5, 30, 14, key="bt_p3")
    elif strategy_name == "MACD + SuperTrend":
        with pc[0]: user_params["fast"]      = st.slider("MACD Fast", 5, 20, 12, key="bt_p1")
        with pc[1]: user_params["slow"]      = st.slider("MACD Slow", 15, 50, 26, key="bt_p2")
        with pc[2]: user_params["st_window"] = st.slider("ST ATR Period", 5, 20, 10, key="bt_p3")
    else:
        st.caption("This strategy uses default parameters.")

    run_bt = st.button("Run Backtest", type="primary", key="run_bt")

    if not run_bt:
        g1, g2, g3 = st.columns(3)
        for col, title, items in [
            (g1, "🟢  Start here",     [("SMA Crossover","Visual, easy to understand"),("EMA Crossover","Slightly faster signals"),("RSI","Clear buy/sell levels")]),
            (g2, "📈  Trending mkt",   [("SuperTrend","Clean ATR-based signals"),("MACD + SuperTrend","Dual confirmation"),("EMA + RSI Filter","Trend + momentum")]),
            (g3, "↔️  Ranging mkt",   [("RSI","Buys dips, sells peaks"),("Bollinger Bands","Mean reversion"),("RSI + Bollinger Bands","Double confirmation")]),
        ]:
            col.markdown(f'<div style="background:#0d1117;border:1px solid #1a2235;border-radius:8px;padding:1.2rem;">', unsafe_allow_html=True)
            col.markdown(f'<div style="font-family:IBM Plex Mono,monospace;font-size:0.62rem;color:#3a4558;text-transform:uppercase;letter-spacing:0.15em;margin-bottom:0.8rem;">{title}</div>', unsafe_allow_html=True)
            for name, tip in items:
                col.markdown(f'<div class="row-item"><div><div style="font-size:0.82rem;color:#e2e8f0;">{name}</div><div style="font-size:0.74rem;color:#3a4558;margin-top:0.1rem;">{tip}</div></div></div>', unsafe_allow_html=True)
            col.markdown('</div>', unsafe_allow_html=True)
        st.stop()

    with st.spinner(f"Loading {ticker_bt}…"):
        df_bt = get_stock_data(ticker_bt, str(start_bt), str(end_bt))
    if df_bt.empty: st.error("No data found. Check the ticker."); st.stop()

    info_bt = get_ticker_info(ticker_bt)
    strategy_info = STRATEGY_REGISTRY[strategy_name]
    try:
        signals = strategy_info["fn"](df_bt, **user_params)
        result  = run_backtest(df_bt, signals, float(capital_bt))
    except Exception as e: st.error(f"Strategy error: {e}"); st.stop()

    m = result["metrics"]; port = result["portfolio"]; trades = result["trades"]
    alpha = m["total_return"] - m["bh_return"]
    cp = float(df_bt["Close"].iloc[-1])
    pct_period = (float(df_bt["Close"].iloc[-1]) - float(df_bt["Close"].iloc[0])) / float(df_bt["Close"].iloc[0]) * 100
    pct_col = "#00d68f" if pct_period >= 0 else "#ff4757"

    st.markdown(f"""
    <div style="background:#0d1117;border:1px solid #1a2235;border-radius:10px;padding:1.2rem 1.5rem;margin:1rem 0;display:flex;align-items:center;gap:2rem;flex-wrap:wrap;">
        <div>
            <div style="font-family:'Bebas Neue',sans-serif;font-size:2rem;letter-spacing:0.06em;">{ticker_bt}</div>
            <div style="font-family:'IBM Plex Mono',monospace;font-size:0.65rem;color:#3a4558;">{info_bt.get('name','')} · {info_bt.get('sector','N/A')}</div>
        </div>
        <div><div style="font-family:'IBM Plex Mono',monospace;font-size:1.2rem;">${cp:,.2f}</div>
        <div style="font-size:0.7rem;color:{pct_col};">{pct_period:+.2f}% over test period</div></div>
        <div style="font-family:'IBM Plex Mono',monospace;font-size:0.68rem;color:#3a4558;margin-left:auto;">{len(df_bt)} days · {start_bt} → {end_bt}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-hdr"><div class="section-hdr-label">Results</div></div>', unsafe_allow_html=True)
    rcols = st.columns(8)
    def mc(col, val, lbl, fmt="pct"):
        if fmt=="pct":   cls="pos" if val>=0 else "neg"; d=f"{val:+.2f}%"
        elif fmt=="usd": cls="neu"; d=f"${val:,.0f}"
        elif fmt=="raw":
            try: cls="pos" if float(val)>=1 else ("neg" if float(val)<0 else "neu")
            except: cls="neu"
            d=str(val)
        else: cls="neu"; d=str(val)
        col.markdown(f'<div class="metric-card"><div class="metric-val {cls}">{d}</div><div class="metric-lbl">{lbl}</div></div>', unsafe_allow_html=True)

    mc(rcols[0], m["total_return"], "Strategy")
    mc(rcols[1], m["bh_return"],    "Buy & Hold")
    mc(rcols[2], alpha,             "Alpha")
    mc(rcols[3], m["max_drawdown"], "Drawdown")
    mc(rcols[4], m["final_value"],  "Final Value", "usd")
    mc(rcols[5], m["win_rate"],     "Win Rate")
    mc(rcols[6], m["sharpe"],       "Sharpe", "raw")
    rcols[7].markdown(f'<div class="metric-card"><div class="metric-val neu">{m["num_trades"]}</div><div class="metric-lbl">Trades</div></div>', unsafe_allow_html=True)

    try: sr = float(m["sharpe"])
    except: sr = 0
    alpha_col = "#00d68f" if alpha >= 0 else "#ff4757"
    verdict   = "✓ Beat buy & hold" if alpha > 0 else "✗ Underperformed buy & hold"
    st.markdown(f"""
    <div style="background:#0d1117;border:1px solid #1a2235;border-radius:8px;padding:1rem 1.4rem;margin:0.8rem 0;display:flex;gap:2rem;flex-wrap:wrap;font-family:'IBM Plex Mono',monospace;font-size:0.72rem;">
        <span style="color:#8892a4;">{verdict} by <span style="color:{alpha_col};">{abs(alpha):.2f}%</span></span>
        <span style="color:#3a4558;">·</span>
        <span style="color:#8892a4;">Sharpe {"good" if sr>=1 else "weak"}: {sr:.2f}</span>
        <span style="color:#3a4558;">·</span>
        <span style="color:#8892a4;">Win rate {"above" if m["win_rate"]>=50 else "below"} 50%</span>
        <span style="color:#3a4558;">·</span>
        <span style="color:#8892a4;">{"Overtrading risk" if m["num_trades"]>60 else ("Low sample" if m["num_trades"]<8 else "Trade count OK")}</span>
    </div>
    """, unsafe_allow_html=True)

    overlays = {}
    if strategy_name == "SMA Crossover":
        overlays[f"SMA {user_params['short']}"] = sma(df_bt["Close"], user_params["short"])
        overlays[f"SMA {user_params['long']}"]  = sma(df_bt["Close"], user_params["long"])
    elif strategy_name in ["EMA Crossover", "EMA + RSI Filter"]:
        overlays["Fast EMA"] = ema(df_bt["Close"], user_params.get("ema_fast", user_params.get("short", 12)))
        overlays["Slow EMA"] = ema(df_bt["Close"], user_params.get("ema_slow", user_params.get("long",  26)))
    elif strategy_name == "Bollinger Bands":
        bb = bollinger_bands(df_bt["Close"], user_params["window"], user_params["num_std"])
        overlays["BB Upper"] = bb["upper"]; overlays["BB Middle"] = bb["middle"]; overlays["BB Lower"] = bb["lower"]
    elif strategy_name == "SuperTrend":
        st_data = supertrend(df_bt, user_params["window"], user_params["multiplier"])
        overlays["ST Bull"] = st_data["supertrend"].where(st_data["direction"] == 1)
        overlays["ST Bear"] = st_data["supertrend"].where(st_data["direction"] == -1)

    sub_panels = [{"type":"volume","label":"Volume","data":None}]
    if strategy_name in ["RSI","RSI + Bollinger Bands","EMA + RSI Filter"]:
        sub_panels.append({"type":"rsi","label":"RSI","data":rsi(df_bt["Close"], user_params.get("rsi_window", user_params.get("window",14)))})
    if strategy_name in ["MACD","MACD + SuperTrend"]:
        md = macd(df_bt["Close"], user_params.get("fast",12), user_params.get("slow",26))
        sub_panels.append({"type":"macd","label":"MACD","data":md})

    fig, cfg = build_tv_chart(df_bt, title=f"{ticker_bt} — {strategy_name}", overlays=overlays or None, sub_panels=sub_panels, trades=trades if not trades.empty else None)
    st.plotly_chart(fig, use_container_width=True, config=cfg)
    st.plotly_chart(chart_portfolio(port, df_bt, float(capital_bt)), use_container_width=True)

    if not trades.empty:
        st.markdown('<div class="section-hdr"><div class="section-hdr-label">Trade Log</div></div>', unsafe_allow_html=True)
        tl1, tl2, tl3 = st.columns(3)
        tl1.markdown(f'<div class="metric-card"><div class="metric-val neu">{len(trades)}</div><div class="metric-lbl">Total Trades</div></div>', unsafe_allow_html=True)
        sells = trades[trades["action"].str.contains("SELL")]
        if len(sells) > 0 and "profit_pct" in sells.columns:
            aw  = sells[sells["profit_pct"]>0]["profit_pct"].mean() if len(sells[sells["profit_pct"]>0])>0 else 0
            al_ = sells[sells["profit_pct"]<0]["profit_pct"].mean() if len(sells[sells["profit_pct"]<0])>0 else 0
            tl2.markdown(f'<div class="metric-card"><div class="metric-val pos">+{aw:.1f}%</div><div class="metric-lbl">Avg Win</div></div>', unsafe_allow_html=True)
            tl3.markdown(f'<div class="metric-card"><div class="metric-val neg">{al_:.1f}%</div><div class="metric-lbl">Avg Loss</div></div>', unsafe_allow_html=True)
        with st.expander(f"View all {len(trades)} trades"):
            d2 = trades.copy()
            d2["price"] = d2["price"].apply(lambda x: f"${x:,.2f}")
            if "profit_pct" in d2.columns:
                d2["profit_pct"] = d2["profit_pct"].apply(lambda x: f"{x:+.2f}%" if pd.notna(x) else "—")
            st.dataframe(d2.set_index("date"), use_container_width=True)

    st.session_state["last_backtest"] = dict(ticker=ticker_bt, strategy=strategy_name, params=user_params, metrics=m)
    st.markdown('<div class="info-box" style="margin-top:1rem;">Results saved — open AI Coach to get these explained in plain English.</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — CUSTOM SIGNAL BUILDER
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
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
        "RSI":            {"buy":["RSI below oversold","RSI crosses above 50"],          "sell":["RSI above overbought","RSI crosses below 50"]},
        "Stoch RSI":      {"buy":["%K crosses above %D","%K below 20"],                  "sell":["%K crosses below %D","%K above 80"]},
        "MACD":           {"buy":["MACD crosses above Signal","MACD above 0"],           "sell":["MACD crosses below Signal","MACD below 0"]},
        "SMA":            {"buy":["Price crosses above MA","Price above MA"],             "sell":["Price crosses below MA","Price below MA"]},
        "EMA":            {"buy":["Price crosses above MA","Price above MA"],             "sell":["Price crosses below MA","Price below MA"]},
        "WMA":            {"buy":["Price crosses above MA","Price above MA"],             "sell":["Price crosses below MA","Price below MA"]},
        "Bollinger Bands":{"buy":["Price below lower band","%B below 0"],                "sell":["Price above upper band","%B above 100"]},
        "SuperTrend":     {"buy":["Direction turns bullish","Price above SuperTrend"],   "sell":["Direction turns bearish","Price below SuperTrend"]},
        "Ichimoku":       {"buy":["Tenkan crosses above Kijun","Price above Cloud"],      "sell":["Tenkan crosses below Kijun","Price below Cloud"]},
        "CCI":            {"buy":["CCI crosses above -100","CCI below -100"],             "sell":["CCI crosses below 100","CCI above 100"]},
        "Williams %R":    {"buy":["%R below -80","%R crosses above -80"],                 "sell":["%R above -20","%R crosses below -20"]},
        "Donchian":       {"buy":["Price breaks upper channel","Price above middle"],     "sell":["Price breaks lower channel","Price below middle"]},
        "Keltner":        {"buy":["Price below lower band","Price above middle"],         "sell":["Price above upper band","Price below middle"]},
        "Hull MA":        {"buy":["Price crosses above HMA","HMA slope turns up"],        "sell":["Price crosses below HMA","HMA slope turns down"]},
        "Parabolic SAR":  {"buy":["SAR turns bullish","Price above SAR"],                 "sell":["SAR turns bearish","Price below SAR"]},
    }

    cs1, cs2, cs3, cs4, cs5 = st.columns([2, 1.5, 1.5, 1.5, 1.5])
    with cs1: ticker_cs  = st.text_input("Ticker", value="AAPL", key="cs_ticker").upper().strip()
    with cs2: start_cs   = st.date_input("From",   value=date.today()-timedelta(days=365*2), key="cs_start")
    with cs3: end_cs     = st.date_input("To",     value=date.today(), key="cs_end")
    with cs4: capital_cs = st.number_input("Capital ($)", value=10000, min_value=100, step=1000, key="cs_cap")
    with cs5: mode_cs    = st.selectbox("Mode", ["Single","Combo (2-3)"], key="cs_mode")

    ind_names = list(INDICATOR_INFO.keys())
    indicator_config = []

    if mode_cs == "Single":
        ic1, ic2, ic3 = st.columns(3)
        with ic1: ind1  = st.selectbox("Indicator", ind_names, key="cs_ind1")
        with ic2: buy1  = st.selectbox("Buy when",  COND[ind1]["buy"],  key="cs_buy1")
        with ic3: sell1 = st.selectbox("Sell when", COND[ind1]["sell"], key="cs_sell1")
        params1 = build_params(ind1, "cp1")
        indicator_config = [{"name":ind1,"params":params1,"buy":buy1,"sell":sell1}]
    else:
        n_cs = st.slider("Number of indicators", 2, 3, 2, key="cs_n")
        combo_logic = st.radio("Combine with", ["AND — all must agree (fewer, higher-quality signals)","OR — any can trigger (more signals, more noise)"], label_visibility="visible", key="cs_logic")
        for i in range(n_cs):
            st.markdown(f'<div style="font-family:IBM Plex Mono,monospace;font-size:0.58rem;color:#3a4558;text-transform:uppercase;letter-spacing:0.18em;margin:1.2rem 0 0.5rem 0;">Indicator {i+1}</div>', unsafe_allow_html=True)
            ic1, ic2, ic3 = st.columns(3)
            with ic1: ind  = st.selectbox(f"Indicator {i+1}", ind_names, key=f"cs_ind{i}")
            with ic2: buy  = st.selectbox("Buy when",  COND[ind]["buy"],  key=f"cs_buy{i}")
            with ic3: sell = st.selectbox("Sell when", COND[ind]["sell"], key=f"cs_sell{i}")
            params = build_params(ind, f"cp{i}")
            indicator_config.append({"name":ind,"params":params,"buy":buy,"sell":sell})

    run_cs = st.button("Run Test", type="primary", key="run_cs")

    if mode_cs == "Single":
        combo_logic = "AND"

    if not run_cs:
        st.markdown('<div class="section-hdr"><div class="section-hdr-label">Combinations to try</div></div>', unsafe_allow_html=True)
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

    with st.spinner(f"Loading {ticker_cs}…"):
        df_cs = get_stock_data(ticker_cs, str(start_cs), str(end_cs))
    if df_cs.empty: st.stop()

    try:
        ab, as_, comp = [], [], []
        for cfg_i in indicator_config:
            d = compute_ind(cfg_i["name"], df_cs, cfg_i["params"])
            s = gen_sigs(cfg_i["name"], d, cfg_i["buy"], cfg_i["sell"], df_cs, cfg_i["params"])
            ab.append(s==1); as_.append(s==-1)
            comp.append({"name":cfg_i["name"],"data":d,"params":cfg_i["params"]})
        if mode_cs=="Single" or "AND" in combo_logic:
            bf=pd.concat(ab,axis=1).all(axis=1); sf=pd.concat(as_,axis=1).all(axis=1)
        else:
            bf=pd.concat(ab,axis=1).any(axis=1); sf=pd.concat(as_,axis=1).any(axis=1)
        combined=pd.Series(0,index=df_cs.index); combined[bf]=1; combined[sf]=-1
        result_cs=run_backtest(df_cs,combined,float(capital_cs))
    except Exception as e: st.error(f"Error: {e}"); st.stop()

    m_cs=result_cs["metrics"]; port_cs=result_cs["portfolio"]; trades_cs=result_cs["trades"]
    alpha_cs = m_cs["total_return"] - m_cs["bh_return"]

    st.markdown('<div class="section-hdr"><div class="section-hdr-label">Results</div></div>', unsafe_allow_html=True)
    cc = st.columns(8)
    for col_,(val,lbl,fmt_) in zip(cc,[
        (m_cs["total_return"],"Strategy","pct"),(m_cs["bh_return"],"Buy & Hold","pct"),
        (alpha_cs,"Alpha","pct"),(m_cs["max_drawdown"],"Drawdown","pct"),
        (m_cs["final_value"],"Final Value","usd"),(m_cs["win_rate"],"Win Rate","pct"),
        (m_cs["sharpe"],"Sharpe","raw"),(m_cs["num_trades"],"Trades","int")
    ]):
        if fmt_=="pct":   cls="pos" if val>=0 else "neg"; dv=f"{val:+.2f}%"
        elif fmt_=="usd": cls="neu"; dv=f"${val:,.0f}"
        elif fmt_=="raw":
            try: cls="pos" if float(val)>=1 else ("neg" if float(val)<0 else "neu")
            except: cls="neu"
            dv=str(val)
        else: cls="neu"; dv=str(val)
        col_.markdown(f'<div class="metric-card"><div class="metric-val {cls}">{dv}</div><div class="metric-lbl">{lbl}</div></div>', unsafe_allow_html=True)

    ovcs = {}
    for c_ in comp:
        n = c_["name"]
        if INDICATOR_INFO[n]["overlay"]:
            if n in ["SMA","EMA","WMA"]: ovcs[n+" "+str(c_["params"]["window"])] = c_["data"]
            elif n=="SuperTrend":
                ovcs["ST Bull"] = c_["data"]["supertrend"].where(c_["data"]["direction"]==1)
                ovcs["ST Bear"] = c_["data"]["supertrend"].where(c_["data"]["direction"]==-1)
            elif n=="Hull MA": ovcs["Hull MA "+str(c_["params"]["window"])] = c_["data"]
            elif n=="Parabolic SAR":
                ovcs["SAR Bull"] = c_["data"]["sar"].where(c_["data"]["direction"]==1)
                ovcs["SAR Bear"] = c_["data"]["sar"].where(c_["data"]["direction"]==-1)
            elif n in ["Bollinger Bands","Donchian","Keltner"]:
                d=c_["data"]; ovcs[n+" Hi"]=d.get("upper"); ovcs[n+" Mid"]=d.get("middle"); ovcs[n+" Lo"]=d.get("lower")
            elif n=="Ichimoku":
                d=c_["data"]; ovcs["Tenkan"]=d.get("tenkan_sen"); ovcs["Kijun"]=d.get("kijun_sen")

    sub_cs = [{"type":"volume","label":"Volume","data":None}]
    for c_ in comp:
        n=c_["name"]
        if n=="RSI": sub_cs.append({"type":"rsi","label":"RSI","data":c_["data"]})
        elif n=="MACD": sub_cs.append({"type":"macd","label":"MACD","data":c_["data"]})
        elif n=="CCI": sub_cs.append({"type":"cci","label":"CCI","data":c_["data"]})
        elif n=="Williams %R": sub_cs.append({"type":"wpr","label":"%R","data":c_["data"]})

    strat_label = " + ".join([c_["name"] for c_ in comp])
    fig_cs, cfg_cs = build_tv_chart(df_cs, title=f"{ticker_cs} — {strat_label}", overlays=ovcs or None, sub_panels=sub_cs, trades=trades_cs if not trades_cs.empty else None)
    st.plotly_chart(fig_cs, use_container_width=True, config=cfg_cs)
    st.plotly_chart(chart_portfolio(port_cs, df_cs, float(capital_cs)), use_container_width=True)

    if not trades_cs.empty:
        with st.expander(f"Trade Log ({len(trades_cs)} trades)"):
            st.dataframe(trades_cs.set_index("date"), use_container_width=True)

    st.session_state["last_backtest"] = {"ticker":ticker_cs,"strategy":f"Custom: {strat_label}","metrics":m_cs}
    st.markdown('<div class="info-box">Results saved — open AI Coach to get these explained.</div>', unsafe_allow_html=True)
