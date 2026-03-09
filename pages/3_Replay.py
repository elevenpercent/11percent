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
    sma, ema, wma, rsi, macd, bollinger_bands, supertrend,
    hull_ma, donchian_channels, keltner_channels, parabolic_sar,
    cci, williams_r, vwap as calc_vwap
)
from utils.styles import SHARED_CSS
from utils.charts import TV_CONFIG

st.set_page_config(page_title="Replay | 11%", layout="wide", initial_sidebar_state="collapsed")
st.markdown(SHARED_CSS, unsafe_allow_html=True)

# ── Extra replay CSS ──────────────────────────────────────────────────────────
st.markdown("""
<style>
@keyframes barReveal {
    from { opacity:0; transform:scaleY(0.3); }
    to   { opacity:1; transform:scaleY(1);   }
}
.replay-chart-wrap { animation: barReveal 0.18s ease both; }

.ctrl-btn {
    background:#0c1018 !important;
    border:1px solid #1a2235 !important;
    color:#eef2f7 !important;
    font-family:'IBM Plex Mono',monospace !important;
    font-size:0.85rem !important;
    border-radius:6px !important;
    transition:border-color 0.15s, background 0.15s !important;
}
.ctrl-btn:hover { border-color:#00e676 !important; background:#0f1c14 !important; }

.tool-panel {
    background:#0c1018;
    border:1px solid #1a2235;
    border-radius:10px;
    padding:1rem 1.2rem;
    margin-bottom:0.8rem;
}
.tool-label {
    font-family:'IBM Plex Mono',monospace;
    font-size:0.55rem;
    color:#3a4a5e;
    text-transform:uppercase;
    letter-spacing:0.18em;
    margin-bottom:0.6rem;
}
.autoplay-active {
    animation: pulse 1s ease-in-out infinite;
    border-color: #00e676 !important;
}
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.5} }
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

# ── Session state init ────────────────────────────────────────────────────────
DEFAULTS = {
    "replay_idx": 60, "replay_trades": [], "replay_cash": 10000.0,
    "replay_shares": 0.0, "replay_df": None, "replay_ticker": "",
    "replay_capital": 10000.0, "replay_avg_cost": 0.0,
    "replay_autoplay": False, "replay_speed": 0.7,
    "replay_prev_idx": -1,
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
    <h1>Chart Replay</h1>
    <p>Step through history bar by bar with animated reveals. Draw on the chart, add indicators, trade live.</p>
</div>
""", unsafe_allow_html=True)

# ── Setup panel ──────────────────────────────────────────────────────────────
st.markdown('<div class="config-panel">', unsafe_allow_html=True)
s1, s2, s3, s4 = st.columns([2, 1.5, 1.5, 1.5])
with s1: ticker     = st.text_input("Ticker", value=st.session_state.replay_ticker or "AAPL").upper().strip()
with s2: start_date = st.date_input("From", value=date.today() - timedelta(days=365*2))
with s3: end_date   = st.date_input("To",   value=date.today() - timedelta(days=30))
with s4: capital    = st.number_input("Capital ($)", value=10000, min_value=100, step=1000)

load_col, _ = st.columns([1, 4])
with load_col:
    if st.button("Load Chart", type="primary", use_container_width=True):
        with st.spinner("Loading " + ticker + "..."):
            df_full = get_stock_data(ticker, str(start_date), str(end_date))
        if df_full.empty:
            st.error("No data found.")
            st.stop()
        st.session_state.update({
            "replay_df": df_full, "replay_ticker": ticker,
            "replay_idx": min(80, len(df_full) - 1),
            "replay_trades": [], "replay_cash": float(capital),
            "replay_shares": 0.0, "replay_capital": float(capital),
            "replay_avg_cost": 0.0, "replay_autoplay": False,
            "replay_prev_idx": -1,
        })
        st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# ── Empty state ───────────────────────────────────────────────────────────────
df_full = st.session_state.replay_df
if df_full is None or df_full.empty:
    st.markdown("""
    <div style="background:linear-gradient(135deg,#0c1018,#0f1520);border:1px solid #1a2235;
                border-radius:16px;padding:4rem 2rem;text-align:center;margin:2rem 0;">
        <div style="font-family:'Bebas Neue',sans-serif;font-size:2.4rem;letter-spacing:0.06em;margin-bottom:1rem;">
            <span style="color:#00e676;">PRACTICE</span>
            <span style="color:#eef2f7;"> MAKES </span>
            <span style="color:#ff3d57;">PROFIT</span>
        </div>
        <div style="color:#8896ab;font-size:0.9rem;line-height:1.8;max-width:520px;margin:0 auto;">
            Enter a ticker and click Load Chart.<br>
            Bars reveal one at a time - buy and sell without knowing what comes next.<br>
            Draw trendlines, channels and notes directly on the chart.
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── Core state ────────────────────────────────────────────────────────────────
idx          = st.session_state.replay_idx
max_idx      = len(df_full) - 1
df_vis       = df_full.iloc[:idx + 1]
cp           = float(df_vis["Close"].iloc[-1])
cd           = df_vis.index[-1]
cash         = st.session_state.replay_cash
shares       = st.session_state.replay_shares
init_capital = st.session_state.replay_capital
pv           = cash + shares * cp
pnl          = pv - init_capital
pnl_pct      = pnl / init_capital * 100
avg_cost     = st.session_state.replay_avg_cost
unrealised   = (cp - avg_cost) * shares if avg_cost > 0 and shares > 0 else 0.0
pct_through  = (idx + 1) / (max_idx + 1) * 100
bar_is_new   = idx != st.session_state.replay_prev_idx

# ── Portfolio strip ───────────────────────────────────────────────────────────
mc = st.columns(8)
for col, lbl, val, cls in [
    (mc[0], st.session_state.replay_ticker, cd.strftime("%b %d %Y"),  "neu"),
    (mc[1], "Price",       "$" + f"{cp:,.2f}",                        "neu"),
    (mc[2], "Port. Value", "$" + f"{pv:,.2f}",                        "neu"),
    (mc[3], "P&L",         ("+" if pnl >= 0 else "") + "$" + f"{abs(pnl):,.2f}", "pos" if pnl >= 0 else "neg"),
    (mc[4], "P&L %",       f"{pnl_pct:+.2f}%",                        "pos" if pnl_pct >= 0 else "neg"),
    (mc[5], "Unrealised",  ("+" if unrealised >= 0 else "") + "$" + f"{abs(unrealised):,.2f}", "pos" if unrealised >= 0 else "neg"),
    (mc[6], "Cash",        "$" + f"{cash:,.2f}",                      "neu"),
    (mc[7], "Shares",      f"{shares:.2f}",                           "neu"),
]:
    col.markdown(
        '<div class="metric-card" style="margin-bottom:0.8rem;">'
        '<div class="metric-val ' + cls + '">' + val + '</div>'
        '<div class="metric-lbl">' + lbl + '</div>'
        '</div>',
        unsafe_allow_html=True
    )

# Progress bar
st.markdown(
    '<div class="progress-track"><div class="progress-fill" style="width:' + f"{pct_through:.1f}" + '%;"></div></div>'
    '<div style="font-family:IBM Plex Mono,monospace;font-size:0.58rem;color:#3a4a5e;text-align:right;margin-bottom:0.3rem;">'
    'Bar ' + str(idx+1) + ' / ' + str(max_idx+1) + '  *  ' + f"{pct_through:.0f}" + '% through</div>',
    unsafe_allow_html=True
)

# ── Two-column layout: chart left, tools right ────────────────────────────────
chart_col, tool_col = st.columns([4, 1])

with tool_col:
    # ── Overlay indicators ──
    st.markdown('<div class="tool-panel"><div class="tool-label">Overlay Indicators</div>', unsafe_allow_html=True)
    show_sma20 = st.checkbox("SMA 20",       key="ov_sma20")
    show_sma50 = st.checkbox("SMA 50",       key="ov_sma50")
    show_ema20 = st.checkbox("EMA 20",       key="ov_ema20")
    show_ema50 = st.checkbox("EMA 50",       key="ov_ema50")
    show_hma   = st.checkbox("Hull MA",      key="ov_hma")
    show_vwap  = st.checkbox("VWAP",         key="ov_vwap")
    show_bb    = st.checkbox("Bollinger",    key="ov_bb")
    show_kelt  = st.checkbox("Keltner",      key="ov_kelt")
    show_don   = st.checkbox("Donchian",     key="ov_don")
    show_st    = st.checkbox("SuperTrend",   key="ov_st")
    show_sar   = st.checkbox("Parab. SAR",   key="ov_sar")
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Sub-chart indicators ──
    st.markdown('<div class="tool-panel"><div class="tool-label">Sub-charts</div>', unsafe_allow_html=True)
    show_vol  = st.checkbox("Volume",     value=True, key="sc_vol")
    show_rsi  = st.checkbox("RSI",               key="sc_rsi")
    show_macd = st.checkbox("MACD",              key="sc_macd")
    show_cci  = st.checkbox("CCI",               key="sc_cci")
    show_wpr  = st.checkbox("Williams %R",       key="sc_wpr")
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Drawing tools info ──
    st.markdown("""
    <div class="tool-panel">
        <div class="tool-label">Drawing Tools</div>
        <div style="font-size:0.72rem;color:#3a4a5e;line-height:1.8;">
            Use the toolbar above the chart:<br>
            <span style="color:#ffd166;">&#9135;</span> Trendline<br>
            <span style="color:#ffd166;">&#9679;</span> Circle / Ellipse<br>
            <span style="color:#ffd166;">&#9645;</span> Rectangle<br>
            <span style="color:#ffd166;">&#9998;</span> Freehand draw<br>
            <span style="color:#ffd166;">&#10005;</span> Erase shapes<br>
            <span style="color:#3a4a5e;">Drag to pan * Scroll to zoom</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Autoplay controls ──
    st.markdown('<div class="tool-panel"><div class="tool-label">Autoplay</div>', unsafe_allow_html=True)
    speed = st.select_slider(
        "Speed", options=[2.0, 1.5, 1.0, 0.7, 0.4, 0.2, 0.1],
        value=st.session_state.replay_speed,
        format_func=lambda x: f"{x}s",
        label_visibility="collapsed",
        key="speed_slider",
    )
    st.session_state.replay_speed = speed
    auto_label = "Stop" if st.session_state.replay_autoplay else "Auto Play"
    if st.button(auto_label, use_container_width=True, key="autoplay_toggle"):
        st.session_state.replay_autoplay = not st.session_state.replay_autoplay
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with chart_col:
    # ── Build overlays ──
    overlays = {}
    if show_sma20: overlays["SMA 20"]  = sma(df_vis["Close"], 20)
    if show_sma50: overlays["SMA 50"]  = sma(df_vis["Close"], 50)
    if show_ema20: overlays["EMA 20"]  = ema(df_vis["Close"], 20)
    if show_ema50: overlays["EMA 50"]  = ema(df_vis["Close"], 50)
    if show_hma:   overlays["Hull MA"] = hull_ma(df_vis["Close"], 20)
    if show_vwap:  overlays["VWAP"]    = calc_vwap(df_vis)

    # ── Build sub-panels ──
    sub_panels = []
    if show_vol:
        sub_panels.append({"type": "volume", "label": "Volume", "data": None})
    if show_rsi:
        sub_panels.append({"type": "rsi", "label": "RSI", "data": rsi(df_vis["Close"])})
    if show_macd:
        sub_panels.append({"type": "macd", "label": "MACD", "data": macd(df_vis["Close"])})
    if show_cci:
        sub_panels.append({"type": "cci", "label": "CCI", "data": cci(df_vis)})
    if show_wpr:
        sub_panels.append({"type": "wpr", "label": "%R", "data": williams_r(df_vis)})

    # ── Build figure ──
    n_sub = len(sub_panels)
    n_rows = 1 + n_sub
    if n_sub > 0:
        row_heights = [0.58] + [0.42 / n_sub] * n_sub
    else:
        row_heights = [1.0]

    fig = make_subplots(
        rows=n_rows, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.018,
        row_heights=row_heights,
    )

    # Candlesticks
    _BG, _PANEL, _GRID, _BORDER = "#06080c", "#0c1018", "#111927", "#1a2235"
    _GREEN, _RED = "#00e676", "#ff3d57"
    _BLUE, _YELLOW, _PURPLE, _ORANGE = "#4da6ff", "#ffd166", "#b388ff", "#ff9f43"
    _TEXT, _TEXT_DIM = "#8896ab", "#3a4a5e"

    fig.add_trace(go.Candlestick(
        x=df_vis.index,
        open=df_vis["Open"], high=df_vis["High"],
        low=df_vis["Low"],   close=df_vis["Close"],
        name="Price",
        increasing=dict(line=dict(color=_GREEN, width=1), fillcolor=_GREEN),
        decreasing=dict(line=dict(color=_RED,   width=1), fillcolor=_RED),
        whiskerwidth=0.3, showlegend=False,
    ), row=1, col=1)

    # Overlays
    for i, (label, series) in enumerate(overlays.items()):
        fig.add_trace(go.Scatter(
            x=series.index, y=series, mode="lines", name=label,
            line=dict(color=OCOLOR[i % len(OCOLOR)], width=1.6),
            opacity=0.9,
        ), row=1, col=1)

    # Bollinger / Keltner / Donchian / SuperTrend / SAR (handled separately as multi-trace)
    if show_bb:
        bb = bollinger_bands(df_vis["Close"])
        fig.add_trace(go.Scatter(x=bb["upper"].index, y=bb["upper"], mode="lines", name="BB Up",
            line=dict(color=_BLUE, width=1, dash="dot"), opacity=0.6, showlegend=False), row=1, col=1)
        fig.add_trace(go.Scatter(x=bb["lower"].index, y=bb["lower"], mode="lines", name="BB Lo",
            line=dict(color=_BLUE, width=1, dash="dot"), opacity=0.6,
            fill="tonexty", fillcolor="rgba(77,166,255,0.04)", showlegend=False), row=1, col=1)
        fig.add_trace(go.Scatter(x=bb["middle"].index, y=bb["middle"], mode="lines", name="BB Mid",
            line=dict(color=_BLUE, width=1), opacity=0.5), row=1, col=1)

    if show_kelt:
        kc = keltner_channels(df_vis)
        fig.add_trace(go.Scatter(x=kc["upper"].index, y=kc["upper"], mode="lines", name="KC Up",
            line=dict(color=_PURPLE, width=1, dash="dot"), opacity=0.6, showlegend=False), row=1, col=1)
        fig.add_trace(go.Scatter(x=kc["lower"].index, y=kc["lower"], mode="lines", name="KC Lo",
            line=dict(color=_PURPLE, width=1, dash="dot"), opacity=0.6,
            fill="tonexty", fillcolor="rgba(179,136,255,0.04)", showlegend=False), row=1, col=1)
        fig.add_trace(go.Scatter(x=kc["middle"].index, y=kc["middle"], mode="lines", name="Keltner",
            line=dict(color=_PURPLE, width=1), opacity=0.5), row=1, col=1)

    if show_don:
        dc = donchian_channels(df_vis)
        fig.add_trace(go.Scatter(x=dc["upper"].index, y=dc["upper"], mode="lines", name="Don Hi",
            line=dict(color=_YELLOW, width=1.2, dash="dash"), opacity=0.7), row=1, col=1)
        fig.add_trace(go.Scatter(x=dc["lower"].index, y=dc["lower"], mode="lines", name="Don Lo",
            line=dict(color=_YELLOW, width=1.2, dash="dash"), opacity=0.7, showlegend=False), row=1, col=1)

    if show_st:
        std = supertrend(df_vis)
        bull = std["supertrend"].where(std["direction"] == 1)
        bear = std["supertrend"].where(std["direction"] == -1)
        fig.add_trace(go.Scatter(x=bull.index, y=bull, mode="lines", name="ST Bull",
            line=dict(color=_GREEN, width=2.5)), row=1, col=1)
        fig.add_trace(go.Scatter(x=bear.index, y=bear, mode="lines", name="ST Bear",
            line=dict(color=_RED, width=2.5)), row=1, col=1)

    if show_sar:
        psar = parabolic_sar(df_vis)
        bull_sar = psar["sar"].where(psar["direction"] == 1)
        bear_sar = psar["sar"].where(psar["direction"] == -1)
        fig.add_trace(go.Scatter(x=bull_sar.index, y=bull_sar, mode="markers", name="SAR +",
            marker=dict(symbol="circle", size=4, color=_GREEN)), row=1, col=1)
        fig.add_trace(go.Scatter(x=bear_sar.index, y=bear_sar, mode="markers", name="SAR -",
            marker=dict(symbol="circle", size=4, color=_RED)), row=1, col=1)

    # Trade markers
    if st.session_state.replay_trades:
        buys  = [t for t in st.session_state.replay_trades if t["action"] == "BUY"]
        sells = [t for t in st.session_state.replay_trades if t["action"] == "SELL"]
        if buys:
            fig.add_trace(go.Scatter(
                x=[t["date"] for t in buys], y=[t["price"] for t in buys],
                mode="markers+text", name="Buy",
                text=["B"] * len(buys), textposition="middle center",
                textfont=dict(color="#000", size=9, family="IBM Plex Mono"),
                marker=dict(symbol="circle", size=20, color=_GREEN,
                            line=dict(color="#000", width=1)),
            ), row=1, col=1)
        if sells:
            fig.add_trace(go.Scatter(
                x=[t["date"] for t in sells], y=[t["price"] for t in sells],
                mode="markers+text", name="Sell",
                text=["S"] * len(sells), textposition="middle center",
                textfont=dict(color="#fff", size=9, family="IBM Plex Mono"),
                marker=dict(symbol="circle", size=20, color=_RED,
                            line=dict(color="#000", width=1)),
            ), row=1, col=1)

    # Current bar highlight
    fig.add_vline(x=cd, line_dash="dot", line_color="rgba(255,255,255,0.15)", line_width=1)

    # Sub-charts
    for si, panel in enumerate(sub_panels):
        row = 2 + si
        ptype = panel["type"]

        if ptype == "volume":
            vol_c = [_GREEN if c >= o else _RED
                     for c, o in zip(df_vis["Close"], df_vis["Open"])]
            fig.add_trace(go.Bar(x=df_vis.index, y=df_vis["Volume"],
                name="Vol", marker_color=vol_c, opacity=0.55), row=row, col=1)
            fig.update_yaxes(title_text="Vol", title_font=dict(size=9, color=_TEXT_DIM), row=row, col=1)

        elif ptype == "rsi":
            r = panel["data"]
            fig.add_trace(go.Scatter(x=r.index, y=r, mode="lines", name="RSI",
                line=dict(color=_YELLOW, width=1.5)), row=row, col=1)
            fig.add_hrect(y0=70, y1=100, fillcolor="rgba(255,61,87,0.05)",  line_width=0, row=row, col=1)
            fig.add_hrect(y0=0,  y1=30,  fillcolor="rgba(0,230,118,0.05)", line_width=0, row=row, col=1)
            fig.add_hline(y=70, line_dash="dot", line_color=_RED,   line_width=0.7, row=row, col=1)
            fig.add_hline(y=30, line_dash="dot", line_color=_GREEN, line_width=0.7, row=row, col=1)
            fig.update_yaxes(range=[0, 100], title_text="RSI",
                             title_font=dict(size=9, color=_TEXT_DIM), row=row, col=1)

        elif ptype == "macd":
            md = panel["data"]
            bar_c = [_GREEN if v >= 0 else _RED for v in md["histogram"].fillna(0)]
            fig.add_trace(go.Bar(x=md["histogram"].index, y=md["histogram"],
                name="Hist", marker_color=bar_c, opacity=0.6), row=row, col=1)
            fig.add_trace(go.Scatter(x=md["macd"].index, y=md["macd"], mode="lines",
                name="MACD", line=dict(color=_BLUE, width=1.5)), row=row, col=1)
            fig.add_trace(go.Scatter(x=md["signal"].index, y=md["signal"], mode="lines",
                name="Sig",  line=dict(color=_YELLOW, width=1.2)), row=row, col=1)
            fig.update_yaxes(title_text="MACD", title_font=dict(size=9, color=_TEXT_DIM), row=row, col=1)

        elif ptype == "cci":
            c_data = panel["data"]
            fig.add_trace(go.Scatter(x=c_data.index, y=c_data, mode="lines", name="CCI",
                line=dict(color=_PURPLE, width=1.5)), row=row, col=1)
            fig.add_hline(y=100,  line_dash="dot", line_color=_RED,   line_width=0.7, row=row, col=1)
            fig.add_hline(y=-100, line_dash="dot", line_color=_GREEN, line_width=0.7, row=row, col=1)
            fig.update_yaxes(title_text="CCI", title_font=dict(size=9, color=_TEXT_DIM), row=row, col=1)

        elif ptype == "wpr":
            w_data = panel["data"]
            fig.add_trace(go.Scatter(x=w_data.index, y=w_data, mode="lines", name="%R",
                line=dict(color=_ORANGE, width=1.5)), row=row, col=1)
            fig.add_hline(y=-20, line_dash="dot", line_color=_RED,   line_width=0.7, row=row, col=1)
            fig.add_hline(y=-80, line_dash="dot", line_color=_GREEN, line_width=0.7, row=row, col=1)
            fig.update_yaxes(range=[-100, 0], title_text="%R",
                             title_font=dict(size=9, color=_TEXT_DIM), row=row, col=1)

    # Layout
    title_str = (st.session_state.replay_ticker + "  *  " +
                 cd.strftime("%b %d, %Y") + "  *  $" + f"{cp:,.2f}")
    total_h = 560 + n_sub * 130
    axis_style = dict(gridcolor=_GRID, linecolor=_BORDER,
                      tickfont=dict(size=10, color=_TEXT_DIM), zeroline=False)
    fig.update_layout(
        paper_bgcolor=_BG, plot_bgcolor=_PANEL,
        font=dict(family="IBM Plex Mono", size=11, color=_TEXT),
        height=total_h,
        margin=dict(l=8, r=8, t=44, b=8),
        xaxis_rangeslider_visible=False,
        title=dict(text=title_str, font=dict(family="IBM Plex Mono", size=13, color=_TEXT), x=0.01),
        showlegend=True,
        legend=dict(bgcolor="rgba(12,16,24,0.9)", bordercolor=_BORDER, borderwidth=1,
                    font=dict(size=10), orientation="h", y=1.02, x=0),
        hovermode="x unified",
        hoverlabel=dict(bgcolor=_PANEL, bordercolor=_BORDER,
                        font=dict(family="IBM Plex Mono", size=11)),
        dragmode="pan",
        barmode="relative",
        newshape=dict(
            line=dict(color=_YELLOW, width=2),
            fillcolor="rgba(255,209,102,0.08)",
        ),
    )
    for i in range(1, n_rows + 1):
        fig.update_xaxes(**axis_style, row=i, col=1)
        fig.update_yaxes(**axis_style, row=i, col=1)

    # Animate new bar
    anim_div_open  = '<div class="replay-chart-wrap">' if bar_is_new else '<div>'
    st.markdown(anim_div_open, unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True, config=TV_CONFIG)
    st.markdown('</div>', unsafe_allow_html=True)
    st.session_state.replay_prev_idx = idx

# ── Playback controls ─────────────────────────────────────────────────────────
step = st.select_slider(
    "Step size", [1, 2, 3, 5, 10, 20, 50], value=1,
    label_visibility="collapsed", key="step_slider"
)
pc = st.columns([1, 1, 1, 3, 1, 1, 1])
with pc[0]:
    if st.button("<<", use_container_width=True, help="Back to start"):
        st.session_state.replay_idx = min(80, max_idx)
        st.rerun()
with pc[1]:
    if st.button("< " + str(step), use_container_width=True):
        st.session_state.replay_idx = max(0, idx - step)
        st.rerun()
with pc[3]:
    st.markdown(
        '<div style="display:flex;align-items:center;justify-content:center;gap:1.5rem;padding:0.4rem 0;">'
        '<span style="font-family:IBM Plex Mono,monospace;font-size:1rem;color:#eef2f7;">' + cd.strftime("%b %d, %Y") + '</span>'
        '<span style="font-family:IBM Plex Mono,monospace;font-size:0.65rem;color:#3a4a5e;">BAR ' + str(idx+1) + ' / ' + str(max_idx+1) + '</span>'
        '</div>',
        unsafe_allow_html=True
    )
with pc[5]:
    if st.button(str(step) + " >", use_container_width=True):
        st.session_state.replay_idx = min(max_idx, idx + step)
        st.rerun()
with pc[6]:
    if st.button(">>", use_container_width=True, help="Jump to end"):
        st.session_state.replay_idx = max_idx
        st.rerun()

j1, j2 = st.columns([1, 5])
with j1:
    jump = st.number_input("Jump to bar", 0, max_idx, idx, label_visibility="visible")
    if jump != idx:
        st.session_state.replay_idx = jump
        st.rerun()

# ── Autoplay loop ─────────────────────────────────────────────────────────────
if st.session_state.replay_autoplay:
    if idx < max_idx:
        time.sleep(st.session_state.replay_speed)
        st.session_state.replay_idx = idx + 1
        st.rerun()
    else:
        st.session_state.replay_autoplay = False

# ── Trade panel ───────────────────────────────────────────────────────────────
st.markdown('<div class="divider">Execute Trade</div>', unsafe_allow_html=True)
t1, t2, t3 = st.columns(3)

with t1:
    st.markdown(
        '<div style="font-family:IBM Plex Mono,monospace;font-size:0.62rem;color:#00e676;'
        'text-transform:uppercase;letter-spacing:0.18em;margin-bottom:0.8rem;'
        'padding:0.5rem 0.8rem;background:rgba(0,230,118,0.06);border:1px solid rgba(0,230,118,0.15);'
        'border-radius:6px;">Buy Order</div>',
        unsafe_allow_html=True
    )
    bq    = st.number_input("Quantity", min_value=0.01, value=1.0, step=1.0, key="bq", format="%.2f")
    bcost = bq * cp
    max_shares = cash / cp if cp > 0 else 0
    st.markdown(
        '<div style="background:#0c1018;border:1px solid #1a2235;border-radius:6px;padding:0.75rem;'
        'margin:0.5rem 0;font-family:IBM Plex Mono,monospace;font-size:0.72rem;">'
        '<div style="display:flex;justify-content:space-between;color:#3a4a5e;margin-bottom:0.3rem;">'
        '<span>Order value</span><span style="color:#eef2f7;">$' + f"{bcost:,.2f}" + '</span></div>'
        '<div style="display:flex;justify-content:space-between;color:#3a4a5e;">'
        '<span>Max affordable</span><span style="color:#eef2f7;">' + f"{max_shares:.1f}" + ' shares</span></div>'
        '</div>',
        unsafe_allow_html=True
    )
    if st.button("BUY", type="primary", use_container_width=True, key="do_buy"):
        if bcost <= cash:
            old_val = st.session_state.replay_avg_cost * st.session_state.replay_shares
            st.session_state.replay_shares   += bq
            st.session_state.replay_cash     -= bcost
            new_val = old_val + bcost
            st.session_state.replay_avg_cost  = new_val / st.session_state.replay_shares
            st.session_state.replay_trades.append({"date": cd, "action": "BUY", "price": cp, "shares": bq})
            st.toast("Bought " + f"{bq:.2f}" + " " + ticker + " @ $" + f"{cp:,.2f}")
            st.rerun()
        else:
            st.error("Need $" + f"{bcost:,.2f}" + " - only $" + f"{cash:,.2f}" + " available.")

with t2:
    st.markdown(
        '<div style="font-family:IBM Plex Mono,monospace;font-size:0.62rem;color:#ff3d57;'
        'text-transform:uppercase;letter-spacing:0.18em;margin-bottom:0.8rem;'
        'padding:0.5rem 0.8rem;background:rgba(255,61,87,0.06);border:1px solid rgba(255,61,87,0.15);'
        'border-radius:6px;">Sell Order</div>',
        unsafe_allow_html=True
    )
    sq = st.number_input(
        "Quantity",
        min_value=0.01,
        max_value=float(shares) if shares > 0 else 0.01,
        value=min(1.0, float(shares)) if shares > 0 else 0.01,
        step=1.0, key="sq", format="%.2f",
    )
    sproc = sq * cp
    sell_pnl = (cp - avg_cost) * sq
    sell_pnl_col = "#00e676" if sell_pnl >= 0 else "#ff3d57"
    st.markdown(
        '<div style="background:#0c1018;border:1px solid #1a2235;border-radius:6px;padding:0.75rem;'
        'margin:0.5rem 0;font-family:IBM Plex Mono,monospace;font-size:0.72rem;">'
        '<div style="display:flex;justify-content:space-between;color:#3a4a5e;margin-bottom:0.3rem;">'
        '<span>Proceeds</span><span style="color:#eef2f7;">$' + f"{sproc:,.2f}" + '</span></div>'
        '<div style="display:flex;justify-content:space-between;color:#3a4a5e;">'
        '<span>Realised P&amp;L</span>'
        '<span style="color:' + sell_pnl_col + ';">$' + f"{sell_pnl:+,.2f}" + '</span></div>'
        '</div>',
        unsafe_allow_html=True
    )
    if st.button("SELL", use_container_width=True, key="do_sell"):
        if shares > 0 and sq <= shares:
            st.session_state.replay_shares -= sq
            st.session_state.replay_cash   += sproc
            if st.session_state.replay_shares <= 0:
                st.session_state.replay_avg_cost = 0.0
            st.session_state.replay_trades.append({"date": cd, "action": "SELL", "price": cp, "shares": sq})
            st.toast("Sold " + f"{sq:.2f}" + " " + ticker + " @ $" + f"{cp:,.2f}")
            st.rerun()
        else:
            st.error("Not enough shares.")

with t3:
    pnl_color = "#00e676" if pnl >= 0 else "#ff3d57"
    ur_color  = "#00e676" if unrealised >= 0 else "#ff3d57"
    bh_now    = float(df_full["Close"].iloc[idx]) / float(df_full["Close"].iloc[0]) * init_capital
    bh_pnl    = bh_now - init_capital
    bh_color  = "#00e676" if pnl >= bh_pnl else "#ff3d57"
    bh_word   = "Beating" if pnl >= bh_pnl else "Trailing"
    ac_str    = "$" + f"{avg_cost:.2f}" if avg_cost else "N/A"
    st.markdown(
        '<div style="background:#0c1018;border:1px solid #1a2235;border-radius:10px;padding:1.2rem;">'
        '<div style="font-family:IBM Plex Mono,monospace;font-size:0.6rem;color:#3a4a5e;'
        'text-transform:uppercase;letter-spacing:0.18em;margin-bottom:0.9rem;">Position Summary</div>'
        '<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:1rem;">'
        '<div class="metric-card" style="padding:0.7rem;"><div class="metric-val neu" style="font-size:1rem;">' + f"{shares:.2f}" + '</div><div class="metric-lbl">Shares</div></div>'
        '<div class="metric-card" style="padding:0.7rem;"><div class="metric-val neu" style="font-size:1rem;">' + ac_str + '</div><div class="metric-lbl">Avg Cost</div></div>'
        '<div class="metric-card" style="padding:0.7rem;"><div class="metric-val" style="color:' + ur_color + ';font-size:1rem;">$' + f"{unrealised:+,.2f}" + '</div><div class="metric-lbl">Unrealised</div></div>'
        '<div class="metric-card" style="padding:0.7rem;"><div class="metric-val" style="color:' + pnl_color + ';font-size:1rem;">' + f"{pnl_pct:+.2f}" + '%</div><div class="metric-lbl">Total Return</div></div>'
        '</div>'
        '<div style="border-top:1px solid #1a2235;padding-top:0.8rem;font-family:IBM Plex Mono,monospace;font-size:0.7rem;color:#3a4a5e;">'
        'vs B&amp;H: <span style="color:' + bh_color + ';">' + bh_word + ' by $' + f"{abs(pnl-bh_pnl):,.2f}" + '</span>'
        '</div></div>',
        unsafe_allow_html=True
    )
    if st.button("Reset Portfolio", use_container_width=True, key="reset"):
        st.session_state.replay_trades   = []
        st.session_state.replay_cash     = init_capital
        st.session_state.replay_shares   = 0.0
        st.session_state.replay_avg_cost = 0.0
        st.rerun()

# ── Trade log ─────────────────────────────────────────────────────────────────
if st.session_state.replay_trades:
    st.markdown('<div class="divider">Trade Log</div>', unsafe_allow_html=True)
    trades_list = st.session_state.replay_trades
    total_sells = sum(1 for t in trades_list if t["action"] == "SELL")
    tl1, tl2, tl3, tl4 = st.columns(4)
    tl1.markdown('<div class="metric-card"><div class="metric-val neu">' + str(len(trades_list)) + '</div><div class="metric-lbl">Total Trades</div></div>', unsafe_allow_html=True)
    tl2.markdown('<div class="metric-card"><div class="metric-val neu">' + str(sum(1 for t in trades_list if t["action"] == "BUY")) + '</div><div class="metric-lbl">Buys</div></div>', unsafe_allow_html=True)
    tl3.markdown('<div class="metric-card"><div class="metric-val neu">' + str(total_sells) + '</div><div class="metric-lbl">Sells</div></div>', unsafe_allow_html=True)
    pnl_cls = "pos" if pnl >= 0 else "neg"
    tl4.markdown('<div class="metric-card"><div class="metric-val ' + pnl_cls + '">$' + f"{pnl:+,.2f}" + '</div><div class="metric-lbl">Net P&L</div></div>', unsafe_allow_html=True)
    with st.expander("All " + str(len(trades_list)) + " trades"):
        log = pd.DataFrame(trades_list)
        log["value"]  = (log["price"] * log["shares"]).apply(lambda x: "$" + f"{x:,.2f}")
        log["price"]  = log["price"].apply(lambda x: "$" + f"{x:,.2f}")
        log["shares"] = log["shares"].apply(lambda x: f"{x:.2f}")
        st.dataframe(log.set_index("date"), use_container_width=True)
    
