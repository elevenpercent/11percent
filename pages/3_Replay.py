import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys, os, time
from datetime import date, timedelta

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.data import get_stock_data
from utils.indicators import (
    sma, ema, hull_ma, rsi, macd, bollinger_bands, supertrend,
    donchian_channels, keltner_channels, parabolic_sar,
    cci, williams_r, vwap as calc_vwap
)
from utils.styles import SHARED_CSS

st.set_page_config(page_title="Replay | 11%", layout="wide", initial_sidebar_state="collapsed")
st.markdown(SHARED_CSS, unsafe_allow_html=True)

_BG = "#06080c"; _PANEL = "#0b0f17"; _PANEL2 = "#0e1420"
_GRID = "#0f1621"; _BORDER = "#1a2438"
_GREEN = "#00e676"; _RED = "#ff3d57"; _BLUE = "#4da6ff"
_YELLOW = "#ffd166"; _PURPLE = "#b388ff"; _ORANGE = "#ff9f43"
_TEXT = "#8896ab"; _DIM = "#3a4a5e"
OCOLOR = [_BLUE, _YELLOW, _PURPLE, _ORANGE, "#00e5ff", "#ea80fc", "#69ff47"]

TV_CONFIG = dict(
    displayModeBar=True, displaylogo=False, scrollZoom=True,
    modeBarButtonsToAdd=["drawline","drawopenpath","drawclosedpath","drawcircle","drawrect","eraseshape"],
    modeBarButtonsToRemove=["autoScale2d","lasso2d","select2d"],
)

st.markdown("""
<style>
@keyframes pricePulse { 0%,100%{opacity:1} 50%{opacity:0.6} }
@keyframes tickerScroll { from{transform:translateX(0)} to{transform:translateX(-50%)} }
@keyframes liveBlink { 0%,100%{opacity:1} 50%{opacity:0.15} }

.ticker-tape {
  overflow:hidden; white-space:nowrap;
  background:#0b0f17; border-top:1px solid #1a2438; border-bottom:1px solid #1a2438;
  padding:5px 0; margin-bottom:8px;
}
.ticker-inner {
  display:inline-block;
  animation:tickerScroll 28s linear infinite;
  font-family:'IBM Plex Mono',monospace; font-size:0.7rem; color:#3a4a5e;
}
.ticker-inner span { margin:0 1.5rem; }
.t-up  { color:#00e676 !important; }
.t-dn  { color:#ff3d57 !important; }
.t-neu { color:#8896ab !important; }

.live-dot {
  display:inline-block; width:6px; height:6px;
  background:#00e676; border-radius:50%;
  animation:liveBlink 1s ease-in-out infinite;
  margin-right:4px; vertical-align:middle;
}

.tool-block { background:#0b0f17; border:1px solid #1a2438; border-radius:7px; padding:0.75rem 0.85rem; margin-bottom:0.5rem; }
.tool-hdr { font-family:'IBM Plex Mono',monospace; font-size:0.5rem; color:#3a4a5e; text-transform:uppercase; letter-spacing:0.2em; margin-bottom:0.5rem; border-bottom:1px solid #1a2438; padding-bottom:0.3rem; }

.mstrip { display:flex; background:#0b0f17; border:1px solid #1a2438; border-radius:7px; overflow:hidden; margin-bottom:7px; }
.mstrip-cell { flex:1; padding:5px 8px; border-right:1px solid #1a2438; min-width:0; }
.mstrip-cell:last-child { border-right:none; }
.mstrip-val { font-family:'IBM Plex Mono',monospace; font-size:0.82rem; font-weight:600; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.mstrip-lbl { font-family:'IBM Plex Mono',monospace; font-size:0.46rem; color:#3a4a5e; text-transform:uppercase; letter-spacing:0.14em; }
.col-g{color:#00e676} .col-r{color:#ff3d57} .col-n{color:#eef2f7} .col-b{color:#4da6ff}

.stButton>button[kind="primary"]{ background:linear-gradient(135deg,#008c3a,#00e676)!important; border:none!important; color:#000!important; font-weight:700!important; letter-spacing:0.08em!important; }
.sell-btn>button{ background:linear-gradient(135deg,#aa0020,#ff3d57)!important; border:none!important; color:#fff!important; font-weight:700!important; }
</style>
""", unsafe_allow_html=True)


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

# ── Session defaults
_D = {
    "rp_idx": 60, "rp_trades": [], "rp_cash": 10000.0,
    "rp_shares": 0.0, "rp_df": None, "rp_ticker": "",
    "rp_capital": 10000.0, "rp_avg_cost": 0.0,
    "rp_playing": False, "rp_speed": 0.7,
    "rp_tick_phase": 0.5,
    "rp_last_advance": 0.0,
}
for k, v in _D.items():
    if k not in st.session_state:
        st.session_state[k] = v

st.markdown('<div class="page-header" style="margin-bottom:0.4rem;"><h1 style="margin-bottom:0.15rem;">Market Simulator</h1><p style="margin:0;font-size:0.85rem;">Live bar-by-bar replay with ticking price. Trade without a page refresh. Draw on the chart.</p></div>', unsafe_allow_html=True)

# ── Setup
with st.expander("Setup", expanded=st.session_state.rp_df is None):
    s1,s2,s3,s4,s5 = st.columns([2,1.5,1.5,1.5,1])
    with s1: ticker     = st.text_input("Ticker", value=st.session_state.rp_ticker or "AAPL").upper().strip()
    with s2: start_date = st.date_input("From",   value=date.today()-timedelta(days=730))
    with s3: end_date   = st.date_input("To",     value=date.today()-timedelta(days=30))
    with s4: capital    = st.number_input("Capital ($)", value=10000, min_value=100, step=1000)
    with s5:
        st.markdown("<div style='height:1.75rem'></div>", unsafe_allow_html=True)
        if st.button("Load", type="primary", use_container_width=True):
            with st.spinner("Fetching " + ticker + "..."):
                df = get_stock_data(ticker, str(start_date), str(end_date))
            if df.empty:
                st.error("No data.")
            else:
                st.session_state.update({
                    "rp_df": df, "rp_ticker": ticker,
                    "rp_idx": min(80, len(df)-1),
                    "rp_trades": [], "rp_cash": float(capital),
                    "rp_shares": 0.0, "rp_capital": float(capital),
                    "rp_avg_cost": 0.0, "rp_playing": False,
                    "rp_tick_phase": 0.5, "rp_last_advance": time.time(),
                })
                st.rerun()

df_full = st.session_state.rp_df
if df_full is None or df_full.empty:
    st.markdown('<div style="text-align:center;padding:5rem 2rem;border:1px dashed #1a2438;border-radius:12px;margin:2rem 0;"><div style="font-family:Bebas Neue,sans-serif;font-size:3rem;letter-spacing:0.08em;"><span style="color:#00e676;">PRACTICE</span> <span style="color:#eef2f7;">LIKE IT\'S</span> <span style="color:#ff3d57;">REAL</span></div><div style="color:#3a4a5e;font-size:0.85rem;margin-top:1rem;line-height:1.9;">Load any ticker above. Bars appear one at a time.<br>Price ticks live within each bar. Trade without page refresh.</div></div>', unsafe_allow_html=True)
    st.stop()

idx         = st.session_state.rp_idx
max_idx     = len(df_full) - 1
df_vis      = df_full.iloc[:idx+1]
bar         = df_vis.iloc[-1]
cl          = float(bar["Close"])
op          = float(bar["Open"])
hi          = float(bar["High"])
lo          = float(bar["Low"])
cd          = df_vis.index[-1]
cash        = st.session_state.rp_cash
shares      = st.session_state.rp_shares
init_cap    = st.session_state.rp_capital
avg_cost    = st.session_state.rp_avg_cost
pct_through = (idx+1)/(max_idx+1)*100

# Live tick
phase = st.session_state.rp_tick_phase
_rng  = np.random.default_rng(seed=idx*1000 + int(phase*100))
base  = op + (cl - op) * min(1.0, phase)
noise = _rng.normal(0, abs(hi-lo)*0.07)
cp    = float(np.clip(base + noise, lo, hi))
pv    = cash + shares*cp
pnl   = pv - init_cap
pnl_pct = pnl/init_cap*100
unreal  = (cp-avg_cost)*shares if avg_cost>0 and shares>0 else 0.0

# ── Ticker tape
_chg = cl-op; _pct = _chg/op*100 if op else 0
_cls = "t-up" if _chg>=0 else "t-dn"
_arr = "+" if _chg>=0 else ""
items = [
    (st.session_state.rp_ticker, "$"+f"{cp:,.2f}", _arr+f"{_pct:.2f}%", _cls),
    ("VOL", f"{int(bar['Volume']):,}", "", "t-neu"),
    ("HI",  "$"+f"{hi:,.2f}",          "", "t-up"),
    ("LO",  "$"+f"{lo:,.2f}",          "", "t-dn"),
    ("PNL", "$"+f"{pnl:+,.2f}",        f"{pnl_pct:+.2f}%", "t-up" if pnl>=0 else "t-dn"),
    ("CASH","$"+f"{cash:,.2f}",         "", "t-neu"),
    ("SH",  f"{shares:.2f}",            "", "t-neu"),
]
tape_spans = ""
for sym,val,chg,cls in items*3:
    tape_spans += f'<span class="{cls}">{sym}</span> <span style="color:#eef2f7">{val}</span> '
    if chg: tape_spans += f'<span class="{cls}">{chg}</span> '
    tape_spans += '<span style="color:#1a2438">|</span> '
st.markdown('<div class="ticker-tape"><div class="ticker-inner">' + tape_spans + '</div></div>', unsafe_allow_html=True)

# ── Main layout
chart_col, tools_col = st.columns([5,1], gap="small")

with tools_col:
    st.markdown('<div class="tool-block"><div class="tool-hdr">Overlays</div>', unsafe_allow_html=True)
    ov_sma20 = st.checkbox("SMA 20",    key="ov_s20")
    ov_sma50 = st.checkbox("SMA 50",    key="ov_s50")
    ov_ema20 = st.checkbox("EMA 20",    key="ov_e20")
    ov_ema50 = st.checkbox("EMA 50",    key="ov_e50")
    ov_hma   = st.checkbox("Hull MA",   key="ov_hma")
    ov_vwap  = st.checkbox("VWAP",      key="ov_vwap")
    ov_bb    = st.checkbox("BB",        key="ov_bb")
    ov_kelt  = st.checkbox("Keltner",   key="ov_kc")
    ov_don   = st.checkbox("Donchian",  key="ov_dc")
    ov_st    = st.checkbox("SuperTrend",key="ov_st")
    ov_sar   = st.checkbox("SAR",       key="ov_sar")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="tool-block"><div class="tool-hdr">Sub-charts</div>', unsafe_allow_html=True)
    sc_vol  = st.checkbox("Volume", value=True, key="sc_vol")
    sc_rsi  = st.checkbox("RSI",               key="sc_rsi")
    sc_macd = st.checkbox("MACD",              key="sc_macd")
    sc_cci  = st.checkbox("CCI",               key="sc_cci")
    sc_wpr  = st.checkbox("Wm %R",             key="sc_wpr")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="tool-block"><div class="tool-hdr">Playback</div>', unsafe_allow_html=True)
    speed_opts = [2.0, 1.5, 1.0, 0.7, 0.5, 0.3, 0.15]
    cur_spd = st.session_state.rp_speed
    if cur_spd not in speed_opts: cur_spd = 0.7
    speed = st.select_slider("spd", options=speed_opts, value=cur_spd,
                              format_func=lambda x: f"{x}s", label_visibility="collapsed")
    st.session_state.rp_speed = speed
    play_lbl = "PAUSE" if st.session_state.rp_playing else "PLAY"
    if st.button(play_lbl, use_container_width=True, key="play_btn"):
        st.session_state.rp_playing = not st.session_state.rp_playing
        st.session_state.rp_last_advance = time.time()
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="tool-block"><div class="tool-hdr">Draw</div><div style="font-size:0.62rem;color:#3a4a5e;line-height:2.2;"><span style="color:#ffd166;">&#8213;</span> Line<br><span style="color:#ffd166;">&#9645;</span> Rect<br><span style="color:#ffd166;">&#9679;</span> Circle<br><span style="color:#ffd166;">&#9998;</span> Free<br><span style="color:#ffd166;">&#10005;</span> Erase</div></div>', unsafe_allow_html=True)

with chart_col:
    # Overlays
    overlays = {}
    if ov_sma20: overlays["SMA 20"]  = sma(df_vis["Close"], 20)
    if ov_sma50: overlays["SMA 50"]  = sma(df_vis["Close"], 50)
    if ov_ema20: overlays["EMA 20"]  = ema(df_vis["Close"], 20)
    if ov_ema50: overlays["EMA 50"]  = ema(df_vis["Close"], 50)
    if ov_hma:   overlays["Hull MA"] = hull_ma(df_vis["Close"], 20)
    if ov_vwap:  overlays["VWAP"]    = calc_vwap(df_vis)

    sub_panels = []
    if sc_vol:  sub_panels.append({"type":"volume"})
    if sc_rsi:  sub_panels.append({"type":"rsi",  "data": rsi(df_vis["Close"])})
    if sc_macd: sub_panels.append({"type":"macd", "data": macd(df_vis["Close"])})
    if sc_cci:  sub_panels.append({"type":"cci",  "data": cci(df_vis)})
    if sc_wpr:  sub_panels.append({"type":"wpr",  "data": williams_r(df_vis)})

    n_sub  = len(sub_panels)
    n_rows = 1 + n_sub
    row_h  = [0.60]+[0.40/n_sub]*n_sub if n_sub else [1.0]

    fig = make_subplots(rows=n_rows, cols=1, shared_xaxes=True,
                        vertical_spacing=0.015, row_heights=row_h)

    # Confirmed candles (all but last)
    conf = df_vis.iloc[:-1]
    fig.add_trace(go.Candlestick(
        x=conf.index, open=conf["Open"], high=conf["High"],
        low=conf["Low"], close=conf["Close"], name="Price",
        increasing=dict(line=dict(color=_GREEN,width=1), fillcolor=_GREEN),
        decreasing=dict(line=dict(color=_RED,  width=1), fillcolor=_RED),
        whiskerwidth=0.3, showlegend=False,
    ), row=1, col=1)

    # Live ticking candle
    live = df_vis.iloc[-1:]
    live_hi  = max(float(live["High"].iloc[0]), cp)
    live_lo  = min(float(live["Low"].iloc[0]),  cp)
    is_up    = cp >= op
    live_col = _GREEN if is_up else _RED
    live_fill= "rgba(0,230,118,0.5)" if is_up else "rgba(255,61,87,0.5)"
    fig.add_trace(go.Candlestick(
        x=live.index, open=[op], high=[live_hi],
        low=[live_lo], close=[cp], name="Live",
        increasing=dict(line=dict(color=live_col,width=2.5), fillcolor=live_fill),
        decreasing=dict(line=dict(color=live_col,width=2.5), fillcolor=live_fill),
        whiskerwidth=0.5, showlegend=False, opacity=0.9,
    ), row=1, col=1)

    # Live price horizontal line
    fig.add_hline(y=cp, line_dash="dot", line_color=live_col, line_width=1.2,
                  annotation_text="  $"+f"{cp:,.2f}",
                  annotation_position="right",
                  annotation_font=dict(color=live_col, size=11, family="IBM Plex Mono"),
                  row=1, col=1)

    # Overlays
    for i,(label,series) in enumerate(overlays.items()):
        fig.add_trace(go.Scatter(x=series.index, y=series, mode="lines", name=label,
            line=dict(color=OCOLOR[i%len(OCOLOR)], width=1.5), opacity=0.88), row=1, col=1)

    # Band indicators
    if ov_bb:
        bb = bollinger_bands(df_vis["Close"])
        fig.add_trace(go.Scatter(x=bb["upper"].index, y=bb["upper"], mode="lines", name="BB Hi",
            line=dict(color=_BLUE,width=1,dash="dot"), opacity=0.5, showlegend=False), row=1,col=1)
        fig.add_trace(go.Scatter(x=bb["lower"].index, y=bb["lower"], mode="lines", name="BB Lo",
            line=dict(color=_BLUE,width=1,dash="dot"), opacity=0.5,
            fill="tonexty", fillcolor="rgba(77,166,255,0.03)", showlegend=False), row=1,col=1)
        fig.add_trace(go.Scatter(x=bb["middle"].index, y=bb["middle"], mode="lines", name="BB Mid",
            line=dict(color=_BLUE,width=0.8), opacity=0.4, showlegend=False), row=1,col=1)
    if ov_kelt:
        kc = keltner_channels(df_vis)
        fig.add_trace(go.Scatter(x=kc["upper"].index, y=kc["upper"], mode="lines", name="KC Hi",
            line=dict(color=_PURPLE,width=1,dash="dot"), opacity=0.5, showlegend=False), row=1,col=1)
        fig.add_trace(go.Scatter(x=kc["lower"].index, y=kc["lower"], mode="lines", name="KC Lo",
            line=dict(color=_PURPLE,width=1,dash="dot"), opacity=0.5,
            fill="tonexty", fillcolor="rgba(179,136,255,0.03)", showlegend=False), row=1,col=1)
        fig.add_trace(go.Scatter(x=kc["middle"].index, y=kc["middle"], mode="lines", name="Keltner",
            line=dict(color=_PURPLE,width=0.8), opacity=0.4, showlegend=False), row=1,col=1)
    if ov_don:
        dc = donchian_channels(df_vis)
        fig.add_trace(go.Scatter(x=dc["upper"].index, y=dc["upper"], mode="lines", name="Don Hi",
            line=dict(color=_YELLOW,width=1.2,dash="dash"), opacity=0.6), row=1,col=1)
        fig.add_trace(go.Scatter(x=dc["lower"].index, y=dc["lower"], mode="lines", name="Don Lo",
            line=dict(color=_YELLOW,width=1.2,dash="dash"), opacity=0.6, showlegend=False), row=1,col=1)
    if ov_st:
        std = supertrend(df_vis)
        fig.add_trace(go.Scatter(x=std["supertrend"].where(std["direction"]==1).index,
            y=std["supertrend"].where(std["direction"]==1), mode="lines", name="ST+",
            line=dict(color=_GREEN,width=2)), row=1,col=1)
        fig.add_trace(go.Scatter(x=std["supertrend"].where(std["direction"]==-1).index,
            y=std["supertrend"].where(std["direction"]==-1), mode="lines", name="ST-",
            line=dict(color=_RED,width=2)), row=1,col=1)
    if ov_sar:
        psar = parabolic_sar(df_vis)
        fig.add_trace(go.Scatter(x=psar["sar"].where(psar["direction"]==1).index,
            y=psar["sar"].where(psar["direction"]==1), mode="markers", name="SAR+",
            marker=dict(symbol="circle",size=3,color=_GREEN), showlegend=False), row=1,col=1)
        fig.add_trace(go.Scatter(x=psar["sar"].where(psar["direction"]==-1).index,
            y=psar["sar"].where(psar["direction"]==-1), mode="markers", name="SAR-",
            marker=dict(symbol="circle",size=3,color=_RED), showlegend=False), row=1,col=1)

    # Trade markers
    tl = st.session_state.rp_trades
    if tl:
        buys  = [t for t in tl if t["action"]=="BUY"]
        sells = [t for t in tl if t["action"]=="SELL"]
        if buys:
            fig.add_trace(go.Scatter(x=[t["date"] for t in buys], y=[t["price"] for t in buys],
                mode="markers+text", name="Buy", text=["B"]*len(buys), textposition="middle center",
                textfont=dict(color="#000",size=8,family="IBM Plex Mono"),
                marker=dict(symbol="circle",size=18,color=_GREEN,line=dict(color="#000",width=1)),
                showlegend=False), row=1,col=1)
        if sells:
            fig.add_trace(go.Scatter(x=[t["date"] for t in sells], y=[t["price"] for t in sells],
                mode="markers+text", name="Sell", text=["S"]*len(sells), textposition="middle center",
                textfont=dict(color="#fff",size=8,family="IBM Plex Mono"),
                marker=dict(symbol="circle",size=18,color=_RED,line=dict(color="#000",width=1)),
                showlegend=False), row=1,col=1)

    # Sub-charts
    for si, panel in enumerate(sub_panels):
        row   = 2+si
        ptype = panel["type"]
        axkw  = dict(title_font=dict(size=8, color=_DIM))
        if ptype == "volume":
            vc = [_GREEN if c>=o else _RED for c,o in zip(df_vis["Close"],df_vis["Open"])]
            fig.add_trace(go.Bar(x=df_vis.index, y=df_vis["Volume"],
                name="Vol", marker_color=vc, opacity=0.5, showlegend=False), row=row,col=1)
            fig.update_yaxes(title_text="VOL",**axkw,row=row,col=1)
        elif ptype == "rsi":
            r = panel["data"]
            fig.add_trace(go.Scatter(x=r.index,y=r,mode="lines",name="RSI",
                line=dict(color=_YELLOW,width=1.4),showlegend=False),row=row,col=1)
            fig.add_hrect(y0=70,y1=100,fillcolor="rgba(255,61,87,0.04)",line_width=0,row=row,col=1)
            fig.add_hrect(y0=0,y1=30,fillcolor="rgba(0,230,118,0.04)",line_width=0,row=row,col=1)
            fig.add_hline(y=70,line_dash="dot",line_color=_RED,  line_width=0.6,row=row,col=1)
            fig.add_hline(y=30,line_dash="dot",line_color=_GREEN,line_width=0.6,row=row,col=1)
            fig.update_yaxes(range=[0,100],title_text="RSI",**axkw,row=row,col=1)
        elif ptype == "macd":
            md = panel["data"]
            bc = [_GREEN if v>=0 else _RED for v in md["histogram"].fillna(0)]
            fig.add_trace(go.Bar(x=md["histogram"].index,y=md["histogram"],
                name="Hist",marker_color=bc,opacity=0.55,showlegend=False),row=row,col=1)
            fig.add_trace(go.Scatter(x=md["macd"].index,y=md["macd"],mode="lines",
                name="MACD",line=dict(color=_BLUE,width=1.4),showlegend=False),row=row,col=1)
            fig.add_trace(go.Scatter(x=md["signal"].index,y=md["signal"],mode="lines",
                name="Sig",line=dict(color=_YELLOW,width=1.2),showlegend=False),row=row,col=1)
            fig.update_yaxes(title_text="MACD",**axkw,row=row,col=1)
        elif ptype == "cci":
            cd2 = panel["data"]
            fig.add_trace(go.Scatter(x=cd2.index,y=cd2,mode="lines",name="CCI",
                line=dict(color=_PURPLE,width=1.4),showlegend=False),row=row,col=1)
            fig.add_hline(y=100, line_dash="dot",line_color=_RED,  line_width=0.6,row=row,col=1)
            fig.add_hline(y=-100,line_dash="dot",line_color=_GREEN,line_width=0.6,row=row,col=1)
            fig.update_yaxes(title_text="CCI",**axkw,row=row,col=1)
        elif ptype == "wpr":
            wd = panel["data"]
            fig.add_trace(go.Scatter(x=wd.index,y=wd,mode="lines",name="%R",
                line=dict(color=_ORANGE,width=1.4),showlegend=False),row=row,col=1)
            fig.add_hline(y=-20,line_dash="dot",line_color=_RED,  line_width=0.6,row=row,col=1)
            fig.add_hline(y=-80,line_dash="dot",line_color=_GREEN,line_width=0.6,row=row,col=1)
            fig.update_yaxes(range=[-100,0],title_text="%R",**axkw,row=row,col=1)

    title_txt = st.session_state.rp_ticker + "   " + cd.strftime("%b %d, %Y") + "   $" + f"{cp:,.2f}"
    total_h   = 580 + n_sub*125
    axis_s    = dict(gridcolor=_GRID, linecolor=_BORDER, tickfont=dict(size=9,color=_DIM), zeroline=False, showgrid=True)
    fig.update_layout(
        paper_bgcolor=_BG, plot_bgcolor=_PANEL,
        font=dict(family="IBM Plex Mono", size=10, color=_TEXT),
        height=total_h, margin=dict(l=8,r=60,t=40,b=8),
        xaxis_rangeslider_visible=False,
        title=dict(text=title_txt, font=dict(family="IBM Plex Mono",size=12,color=_TEXT), x=0.01),
        showlegend=True,
        legend=dict(bgcolor="rgba(11,15,23,0.92)", bordercolor=_BORDER, borderwidth=1,
                    font=dict(size=9), orientation="h", y=1.02, x=0),
        hovermode="x unified",
        hoverlabel=dict(bgcolor=_PANEL2, bordercolor=_BORDER, font=dict(family="IBM Plex Mono",size=10)),
        dragmode="pan", barmode="relative",
        newshape=dict(line=dict(color=_YELLOW,width=2), fillcolor="rgba(255,209,102,0.07)"),
    )
    for i in range(1, n_rows+1):
        fig.update_xaxes(**axis_s, row=i, col=1)
        fig.update_yaxes(**axis_s, row=i, col=1)

    st.plotly_chart(fig, use_container_width=True, config=TV_CONFIG, key="replay_chart_main")

# ── Metric strip
bh_now   = float(df_full["Close"].iloc[idx])/float(df_full["Close"].iloc[0])*init_cap
bh_delta = pnl - (bh_now - init_cap)
cells = [
    ("col-b", "$"+f"{cp:,.2f}",      "Live Price"),
    ("col-g" if pnl>=0 else "col-r", "$"+f"{pv:,.2f}",   "Portfolio"),
    ("col-g" if pnl>=0 else "col-r", "$"+f"{pnl:+,.2f}", "P&L"),
    ("col-g" if pnl>=0 else "col-r", f"{pnl_pct:+.2f}%", "Return"),
    ("col-g" if unreal>=0 else "col-r", "$"+f"{unreal:+,.2f}", "Unrealised"),
    ("col-n", "$"+f"{cash:,.2f}",    "Cash"),
    ("col-n", f"{shares:.2f}",       "Shares"),
    ("col-g" if bh_delta>=0 else "col-r", "$"+f"{bh_delta:+,.2f}", "vs B&H"),
]
cells_html = "".join(
    '<div class="mstrip-cell"><div class="mstrip-val ' + c + '">' + v + '</div>'
    '<div class="mstrip-lbl">' + l + '</div></div>'
    for c,v,l in cells
)
st.markdown('<div class="mstrip">' + cells_html + '</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="progress-track"><div class="progress-fill" style="width:' + f"{pct_through:.1f}" + '%;"></div></div>'
    '<div style="font-family:IBM Plex Mono,monospace;font-size:0.5rem;color:#3a4a5e;text-align:right;margin-top:2px;margin-bottom:0.3rem;">BAR ' + str(idx+1) + ' / ' + str(max_idx+1) + '</div>',
    unsafe_allow_html=True
)

# ── Playback controls
step = st.select_slider("step", options=[1,2,3,5,10,20,50], value=1,
                         label_visibility="collapsed", key="step_sl")
pc = st.columns([1,1,4,1,1])
with pc[0]:
    if st.button("< "+str(step), use_container_width=True, key="back_btn"):
        st.session_state.rp_idx = max(0, idx-step)
        st.session_state.rp_tick_phase = 0.5
        st.rerun()
with pc[1]:
    if st.button("<<", use_container_width=True, key="rst_bar"):
        st.session_state.rp_idx = min(80, max_idx)
        st.session_state.rp_tick_phase = 0.5
        st.rerun()
with pc[2]:
    st.markdown(
        '<div style="display:flex;align-items:center;justify-content:center;height:100%;gap:1rem;">'
        '<span class="live-dot"></span>'
        '<span style="font-family:IBM Plex Mono,monospace;font-size:0.9rem;color:#eef2f7;">' + cd.strftime("%b %d, %Y") + '</span>'
        '<span style="font-family:IBM Plex Mono,monospace;font-size:0.58rem;color:#3a4a5e;">' + f"{pct_through:.0f}" + '% through</span>'
        '</div>', unsafe_allow_html=True
    )
with pc[3]:
    if st.button(">>", use_container_width=True, key="end_btn"):
        st.session_state.rp_idx = max_idx
        st.session_state.rp_tick_phase = 0.9
        st.rerun()
with pc[4]:
    if st.button(str(step)+" >", use_container_width=True, key="fwd_btn"):
        st.session_state.rp_idx = min(max_idx, idx+step)
        st.session_state.rp_tick_phase = 0.1
        st.rerun()

# ── Trade panel — @st.fragment prevents chart from re-rendering on buy/sell
@st.fragment
def trade_panel():
    _idx    = st.session_state.rp_idx
    _df     = st.session_state.rp_df
    _bar    = _df.iloc[_idx]
    _op2    = float(_bar["Open"]); _cl2 = float(_bar["Close"])
    _hi2    = float(_bar["High"]); _lo2  = float(_bar["Low"])
    _ph     = st.session_state.rp_tick_phase
    _rng2   = np.random.default_rng(seed=_idx*1000+int(_ph*100))
    _base2  = _op2 + (_cl2-_op2)*min(1.0,_ph)
    _noise2 = _rng2.normal(0, abs(_hi2-_lo2)*0.07)
    _cp2    = float(np.clip(_base2+_noise2, _lo2, _hi2))
    _cash   = st.session_state.rp_cash
    _sh     = st.session_state.rp_shares
    _cap    = st.session_state.rp_capital
    _ac     = st.session_state.rp_avg_cost
    _pv2    = _cash + _sh*_cp2
    _pnl2   = _pv2 - _cap
    _ur2    = (_cp2-_ac)*_sh if _ac>0 and _sh>0 else 0.0
    _tick   = st.session_state.rp_ticker
    _cd2    = _df.index[_idx]

    st.markdown('<div class="divider">Execute Trade</div>', unsafe_allow_html=True)
    t1,t2,t3 = st.columns(3)

    with t1:
        st.markdown('<div style="font-family:IBM Plex Mono,monospace;font-size:0.56rem;color:#00e676;letter-spacing:0.2em;text-transform:uppercase;margin-bottom:0.65rem;padding:0.35rem 0.65rem;background:rgba(0,230,118,0.05);border:1px solid rgba(0,230,118,0.12);border-radius:4px;">BUY ORDER</div>', unsafe_allow_html=True)
        bq    = st.number_input("Qty", min_value=0.01, value=1.0, step=1.0, key="fr_bq", format="%.2f")
        bcost = bq * _cp2
        maxq  = _cash/_cp2 if _cp2>0 else 0
        st.markdown(
            '<div style="background:#0b0f17;border:1px solid #1a2438;border-radius:4px;padding:0.6rem;margin:0.35rem 0;font-family:IBM Plex Mono,monospace;font-size:0.68rem;">'
            '<div style="display:flex;justify-content:space-between;color:#3a4a5e;margin-bottom:0.2rem;"><span>Value</span><span style="color:#eef2f7;">$'+f"{bcost:,.2f}"+'</span></div>'
            '<div style="display:flex;justify-content:space-between;color:#3a4a5e;"><span>Max</span><span style="color:#eef2f7;">'+f"{maxq:.1f}"+' sh</span></div>'
            '</div>', unsafe_allow_html=True
        )
        if st.button("BUY  $"+f"{_cp2:,.2f}", type="primary", use_container_width=True, key="fr_buy"):
            if bcost <= _cash:
                old_val = st.session_state.rp_avg_cost * st.session_state.rp_shares
                st.session_state.rp_shares   += bq
                st.session_state.rp_cash     -= bcost
                st.session_state.rp_avg_cost  = (old_val + bcost) / st.session_state.rp_shares
                st.session_state.rp_trades.append({"date":_cd2,"action":"BUY","price":_cp2,"shares":bq})
                st.toast("Bought "+f"{bq:.2f}"+" "+_tick+" @ $"+f"{_cp2:,.2f}", icon="")
            else:
                st.error("Insufficient funds.")

    with t2:
        st.markdown('<div style="font-family:IBM Plex Mono,monospace;font-size:0.56rem;color:#ff3d57;letter-spacing:0.2em;text-transform:uppercase;margin-bottom:0.65rem;padding:0.35rem 0.65rem;background:rgba(255,61,87,0.05);border:1px solid rgba(255,61,87,0.12);border-radius:4px;">SELL ORDER</div>', unsafe_allow_html=True)
        _maxs = float(_sh) if _sh>0 else 0.01
        sq    = st.number_input("Qty", min_value=0.01, max_value=_maxs, value=min(1.0,_maxs),
                                 step=1.0, key="fr_sq", format="%.2f")
        sproc = sq * _cp2
        spnl  = (_cp2-_ac)*sq
        sp_c  = "#00e676" if spnl>=0 else "#ff3d57"
        st.markdown(
            '<div style="background:#0b0f17;border:1px solid #1a2438;border-radius:4px;padding:0.6rem;margin:0.35rem 0;font-family:IBM Plex Mono,monospace;font-size:0.68rem;">'
            '<div style="display:flex;justify-content:space-between;color:#3a4a5e;margin-bottom:0.2rem;"><span>Proceeds</span><span style="color:#eef2f7;">$'+f"{sproc:,.2f}"+'</span></div>'
            '<div style="display:flex;justify-content:space-between;color:#3a4a5e;"><span>P&amp;L</span><span style="color:'+sp_c+';">$'+f"{spnl:+,.2f}"+'</span></div>'
            '</div>', unsafe_allow_html=True
        )
        st.markdown('<div class="sell-btn">', unsafe_allow_html=True)
        if st.button("SELL  $"+f"{_cp2:,.2f}", use_container_width=True, key="fr_sell"):
            if _sh>0 and sq<=_sh:
                st.session_state.rp_shares -= sq
                st.session_state.rp_cash   += sproc
                if st.session_state.rp_shares <= 0: st.session_state.rp_avg_cost = 0.0
                st.session_state.rp_trades.append({"date":_cd2,"action":"SELL","price":_cp2,"shares":sq})
                st.toast("Sold "+f"{sq:.2f}"+" "+_tick+" @ $"+f"{_cp2:,.2f}", icon="")
            else:
                st.error("Not enough shares.")
        st.markdown('</div>', unsafe_allow_html=True)

    with t3:
        pc2 = "#00e676" if _pnl2>=0 else "#ff3d57"
        uc2 = "#00e676" if _ur2>=0 else "#ff3d57"
        pp  = _pnl2/_cap*100
        ac2 = "$"+f"{_ac:.2f}" if _ac else "N/A"
        st.markdown(
            '<div style="background:#0b0f17;border:1px solid #1a2438;border-radius:7px;padding:0.9rem;">'
            '<div style="font-family:IBM Plex Mono,monospace;font-size:0.48rem;color:#3a4a5e;text-transform:uppercase;letter-spacing:0.2em;margin-bottom:0.7rem;border-bottom:1px solid #1a2438;padding-bottom:0.35rem;">Position</div>'
            '<div style="display:grid;grid-template-columns:1fr 1fr;gap:5px;">'
            '<div style="background:#0e1420;border-radius:3px;padding:0.45rem;"><div style="font-family:IBM Plex Mono,monospace;font-size:0.85rem;color:#eef2f7;">'+f"{_sh:.2f}"+'</div><div style="font-family:IBM Plex Mono,monospace;font-size:0.45rem;color:#3a4a5e;text-transform:uppercase;">Shares</div></div>'
            '<div style="background:#0e1420;border-radius:3px;padding:0.45rem;"><div style="font-family:IBM Plex Mono,monospace;font-size:0.85rem;color:#eef2f7;">'+ac2+'</div><div style="font-family:IBM Plex Mono,monospace;font-size:0.45rem;color:#3a4a5e;text-transform:uppercase;">Avg Cost</div></div>'
            '<div style="background:#0e1420;border-radius:3px;padding:0.45rem;"><div style="font-family:IBM Plex Mono,monospace;font-size:0.85rem;color:'+uc2+';">$'+f"{_ur2:+,.2f}"+'</div><div style="font-family:IBM Plex Mono,monospace;font-size:0.45rem;color:#3a4a5e;text-transform:uppercase;">Unrealised</div></div>'
            '<div style="background:#0e1420;border-radius:3px;padding:0.45rem;"><div style="font-family:IBM Plex Mono,monospace;font-size:0.85rem;color:'+pc2+';">'+f"{pp:+.2f}"+'%</div><div style="font-family:IBM Plex Mono,monospace;font-size:0.45rem;color:#3a4a5e;text-transform:uppercase;">Return</div></div>'
            '</div></div>', unsafe_allow_html=True
        )
        if st.button("Reset", use_container_width=True, key="fr_reset"):
            st.session_state.rp_trades   = []
            st.session_state.rp_cash     = st.session_state.rp_capital
            st.session_state.rp_shares   = 0.0
            st.session_state.rp_avg_cost = 0.0
            st.rerun()

    if st.session_state.rp_trades:
        st.markdown('<div class="divider">Trade Log</div>', unsafe_allow_html=True)
        _tl = st.session_state.rp_trades
        nb = sum(1 for t in _tl if t["action"]=="BUY")
        ns = sum(1 for t in _tl if t["action"]=="SELL")
        lc = st.columns(4)
        lc[0].markdown('<div class="metric-card"><div class="metric-val neu">'+str(len(_tl))+'</div><div class="metric-lbl">Trades</div></div>', unsafe_allow_html=True)
        lc[1].markdown('<div class="metric-card"><div class="metric-val pos">'+str(nb)+'</div><div class="metric-lbl">Buys</div></div>', unsafe_allow_html=True)
        lc[2].markdown('<div class="metric-card"><div class="metric-val neg">'+str(ns)+'</div><div class="metric-lbl">Sells</div></div>', unsafe_allow_html=True)
        pc3 = "pos" if _pnl2>=0 else "neg"
        lc[3].markdown('<div class="metric-card"><div class="metric-val '+pc3+'">$'+f"{_pnl2:+,.2f}"+'</div><div class="metric-lbl">Net P&L</div></div>', unsafe_allow_html=True)
        with st.expander("All trades"):
            d = pd.DataFrame(_tl)
            d["value"]  = (d["price"]*d["shares"]).apply(lambda x: "$"+f"{x:,.2f}")
            d["price"]  = d["price"].apply(lambda x: "$"+f"{x:,.2f}")
            d["shares"] = d["shares"].apply(lambda x: f"{x:.2f}")
            st.dataframe(d.set_index("date"), use_container_width=True)

trade_panel()

# ── Autoplay engine — advances bar + drives tick animation
if st.session_state.rp_playing:
    now     = time.time()
    elapsed = now - st.session_state.rp_last_advance
    spd     = st.session_state.rp_speed

    # Smoothly advance tick phase
    new_phase = min(1.0, st.session_state.rp_tick_phase + 0.18)
    st.session_state.rp_tick_phase = new_phase

    if elapsed >= spd:
        if idx < max_idx:
            st.session_state.rp_idx += 1
            st.session_state.rp_tick_phase = 0.05
            st.session_state.rp_last_advance = now
        else:
            st.session_state.rp_playing = False

    time.sleep(0.1)
    st.rerun()
