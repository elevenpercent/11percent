import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys, os
from datetime import date, timedelta
sys.path.append(os.path.dirname(os.path.dirname(**file**)))
from utils.data import get_stock_data
from utils.indicators import sma, ema, wma, rsi, macd, bollinger_bands, supertrend, hull_ma, donchian_channels, keltner_channels, parabolic_sar, cci, williams_r
from utils.styles import SHARED_CSS, PLOTLY_THEME

st.set_page_config(page_title=“Replay | 11%”, layout=“wide”, initial_sidebar_state=“collapsed”)
st.markdown(SHARED_CSS, unsafe_allow_html=True)

def navbar():
st.markdown(’<div class="nb"><div class="nb-brand"><span class="g">11</span><span class="r">%</span></div><div class="nb-links">’, unsafe_allow_html=True)
c = st.columns([1,1,1,1,1,1,1])
with c[0]: st.page_link(“app.py”,                    label=“Home”)
with c[1]: st.page_link(“pages/1_Backtest.py”,       label=“Backtest”)
with c[2]: st.page_link(“pages/2_Indicator_Test.py”, label=“Indicators”)
with c[3]: st.page_link(“pages/3_Replay.py”,         label=“Replay”)
with c[4]: st.page_link(“pages/4_Analysis.py”,       label=“Analysis”)
with c[5]: st.page_link(“pages/6_Earnings.py”,       label=“Earnings”)
with c[6]: st.page_link(“pages/5_Assistant.py”,      label=“Coach”)
st.markdown(’</div><div class="nb-tag">FREE · OPEN SOURCE</div></div>’, unsafe_allow_html=True)
navbar()

# ── Session init ───────────────────────────────────────────────────────────────

for k, v in [(“replay_idx”,50),(“replay_trades”,[]),(“replay_cash”,10000.0),
(“replay_shares”,0.0),(“replay_df”,None),(“replay_ticker”,””),
(“replay_capital”,10000.0),(“replay_avg_cost”,0.0)]:
if k not in st.session_state: st.session_state[k] = v

# ── Page header ────────────────────────────────────────────────────────────────

st.markdown(”””

<div class="page-header">
    <h1>Chart Replay</h1>
    <p>Step through history bar by bar. Make buy/sell decisions — then see what actually happened.</p>
</div>
""", unsafe_allow_html=True)

# ── Setup panel ────────────────────────────────────────────────────────────────

st.markdown(’<div class="config-panel">’, unsafe_allow_html=True)
s1,s2,s3,s4 = st.columns([2,1.5,1.5,1.5])
with s1: ticker     = st.text_input(“Ticker”, value=st.session_state.replay_ticker or “AAPL”).upper().strip()
with s2: start_date = st.date_input(“From”, value=date.today()-timedelta(days=365*2))
with s3: end_date   = st.date_input(“To”,   value=date.today()-timedelta(days=30))
with s4: capital    = st.number_input(“Capital ($)”, value=10000, min_value=100, step=1000)

# Indicator toggles

i1,i2,i3,i4,i5,i6,i7,i8,i9 = st.columns(9)
with i1: show_sma  = st.checkbox(“SMA 20”)
with i2: show_ema  = st.checkbox(“EMA 50”)
with i3: show_hma  = st.checkbox(“Hull MA”)
with i4: show_bb   = st.checkbox(“Boll. Bands”)
with i5: show_kelt = st.checkbox(“Keltner”)
with i6: show_don  = st.checkbox(“Donchian”)
with i7: show_st   = st.checkbox(“SuperTrend”)
with i8: show_sar  = st.checkbox(“Parab. SAR”)
with i9: show_vwap = st.checkbox(“VWAP”)

# Sub-chart toggles

sc1,sc2,sc3,sc4,sc5 = st.columns(5)
with sc1: show_rsi   = st.checkbox(“RSI”)
with sc2: show_macd  = st.checkbox(“MACD”)
with sc3: show_cci   = st.checkbox(“CCI”)
with sc4: show_wpr   = st.checkbox(“Williams %R”)
with sc5: show_vol   = st.checkbox(“Volume”, value=True)

load_col, _ = st.columns([1, 3])
with load_col:
if st.button(“Load Chart”, type=“primary”, use_container_width=True):
with st.spinner(f”Loading {ticker}…”):
df_full = get_stock_data(ticker, str(start_date), str(end_date))
if df_full.empty: st.error(“No data found.”); st.stop()
st.session_state.update({
“replay_df”: df_full, “replay_ticker”: ticker,
“replay_idx”: min(80, len(df_full)-1),
“replay_trades”: [], “replay_cash”: float(capital),
“replay_shares”: 0.0, “replay_capital”: float(capital),
“replay_avg_cost”: 0.0,
})
st.rerun()
st.markdown(’</div>’, unsafe_allow_html=True)

# ── Empty state ────────────────────────────────────────────────────────────────

df_full = st.session_state.replay_df
if df_full is None or df_full.empty:
st.markdown(”””
<div style="background:linear-gradient(135deg,#0c1018,#0f1520);border:1px solid #1a2235;border-radius:16px;padding:4rem 2rem;text-align:center;margin:2rem 0;">
<div style="font-size:3rem;margin-bottom:1.2rem;filter:grayscale(0.3);">📈</div>
<div style="font-family:'Bebas Neue',sans-serif;font-size:2rem;letter-spacing:0.06em;margin-bottom:0.8rem;">
<span style="color:#00e676;">PRACTICE</span> <span style="color:#eef2f7;">MAKES</span> <span style="color:#ff3d57;">PROFIT</span>
</div>
<div style="color:#8896ab;font-size:0.9rem;line-height:1.8;max-width:520px;margin:0 auto 2rem auto;">
Enter a ticker above and click Load Chart.<br>
You’ll see history bar by bar — buy and sell without knowing what comes next.<br>
Review your performance vs buy & hold at the end.
</div>
<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;max-width:600px;margin:0 auto;">
<div style="background:#0c1018;border:1px solid #1a2235;border-radius:8px;padding:1rem;">
<div style="font-size:1.4rem;margin-bottom:0.4rem;">⌨️</div>
<div style="font-family:'IBM Plex Mono',monospace;font-size:0.6rem;color:#3a4a5e;text-transform:uppercase;letter-spacing:0.15em;">13+ Overlays</div>
</div>
<div style="background:#0c1018;border:1px solid #1a2235;border-radius:8px;padding:1rem;">
<div style="font-size:1.4rem;margin-bottom:0.4rem;">📊</div>
<div style="font-family:'IBM Plex Mono',monospace;font-size:0.6rem;color:#3a4a5e;text-transform:uppercase;letter-spacing:0.15em;">5 Sub-charts</div>
</div>
<div style="background:#0c1018;border:1px solid #1a2235;border-radius:8px;padding:1rem;">
<div style="font-size:1.4rem;margin-bottom:0.4rem;">💰</div>
<div style="font-family:'IBM Plex Mono',monospace;font-size:0.6rem;color:#3a4a5e;text-transform:uppercase;letter-spacing:0.15em;">Live P&L</div>
</div>
</div>
</div>
“””, unsafe_allow_html=True)
st.stop()

# ── State ──────────────────────────────────────────────────────────────────────

idx     = st.session_state.replay_idx
max_idx = len(df_full) - 1
df_vis  = df_full.iloc[:idx+1]
cp      = float(df_vis[“Close”].iloc[-1])
cd      = df_vis.index[-1]
cash    = st.session_state.replay_cash
shares  = st.session_state.replay_shares
init_capital = st.session_state.replay_capital
pv      = cash + shares * cp
pnl     = pv - init_capital
pnl_pct = pnl / init_capital * 100
avg_cost = st.session_state.replay_avg_cost
unrealised = (cp - avg_cost) * shares if avg_cost > 0 and shares > 0 else 0.0
pct_through = (idx + 1) / (max_idx + 1) * 100

# ── Portfolio bar ──────────────────────────────────────────────────────────────

mc = st.columns(8)
for col, lbl, val, cls in [
(mc[0], st.session_state.replay_ticker, cd.strftime(”%b %d %Y”), “neu”),
(mc[1], “Price”,       f”${cp:,.2f}”,       “neu”),
(mc[2], “Port. Value”, f”${pv:,.2f}”,        “neu”),
(mc[3], “P&L”,         f”${pnl:+,.2f}”,      “pos” if pnl>=0 else “neg”),
(mc[4], “P&L %”,       f”{pnl_pct:+.2f}%”,   “pos” if pnl_pct>=0 else “neg”),
(mc[5], “Unrealised”,  f”${unrealised:+.2f}”, “pos” if unrealised>=0 else “neg”),
(mc[6], “Cash”,        f”${cash:,.2f}”,       “neu”),
(mc[7], “Shares”,      f”{shares:.2f}”,       “neu”),
]:
col.markdown(f’<div class="metric-card" style="margin-bottom:0.8rem;"><div class="metric-val {cls}">{val}</div><div class="metric-lbl">{lbl}</div></div>’, unsafe_allow_html=True)

# Progress bar

st.markdown(f”””

<div class="progress-track">
    <div class="progress-fill" style="width:{pct_through:.1f}%;"></div>
</div>
<div style="font-family:'IBM Plex Mono',monospace;font-size:0.58rem;color:#3a4a5e;text-align:right;margin-bottom:0.4rem;">
    Bar {idx+1} / {max_idx+1} &nbsp;·&nbsp; {pct_through:.0f}% through
</div>
""", unsafe_allow_html=True)

# ── Build main chart ────────────────────────────────────────────────────────────

sub_charts = [s for s in [show_rsi, show_macd, show_cci, show_wpr, show_vol] if s]
n_rows = 1 + len(sub_charts)
row_heights = [0.55] + [0.45 / max(len(sub_charts), 1)] * len(sub_charts) if sub_charts else [1.0]

specs = [[{“secondary_y”: False}]] * n_rows
fig = make_subplots(rows=n_rows, cols=1, shared_xaxes=True,
vertical_spacing=0.02, row_heights=row_heights, specs=specs)

# ── Candlestick ──

fig.add_trace(go.Candlestick(
x=df_vis.index, open=df_vis[“Open”], high=df_vis[“High”],
low=df_vis[“Low”], close=df_vis[“Close”],
name=“Price”,
increasing=dict(line=dict(color=”#00e676”, width=1), fillcolor=”#00e676”),
decreasing=dict(line=dict(color=”#ff3d57”, width=1), fillcolor=”#ff3d57”),
whiskerwidth=0.3,
), row=1, col=1)

# ── Overlays ──

OCOLOR = [”#4da6ff”,”#ffd166”,”#b388ff”,”#ff9f43”,”#00e5ff”,”#ea80fc”,”#69ff47”]
oi = 0
def add_ol(series, name, dash=“solid”, width=1.5):
global oi
fig.add_trace(go.Scatter(x=series.index, y=series, mode=“lines”, name=name,
line=dict(color=OCOLOR[oi % len(OCOLOR)], width=width, dash=dash),
opacity=0.85), row=1, col=1)
oi += 1

if show_sma:  add_ol(sma(df_vis[“Close”], 20),      “SMA 20”,  width=1.5)
if show_ema:  add_ol(ema(df_vis[“Close”], 50),      “EMA 50”,  dash=“dot”)
if show_hma:  add_ol(hull_ma(df_vis[“Close”], 20),  “HMA 20”,  width=2)
if show_vwap:
from utils.indicators import vwap as calc_vwap
add_ol(calc_vwap(df_vis), “VWAP”, dash=“dashdot”, width=1.5)

if show_bb:
bb = bollinger_bands(df_vis[“Close”])
fig.add_trace(go.Scatter(x=bb[“upper”].index, y=bb[“upper”], mode=“lines”, name=“BB Upper”,
line=dict(color=”#4da6ff”, width=1, dash=“dot”), opacity=0.6), row=1, col=1)
fig.add_trace(go.Scatter(x=bb[“lower”].index, y=bb[“lower”], mode=“lines”, name=“BB Lower”,
line=dict(color=”#4da6ff”, width=1, dash=“dot”), opacity=0.6,
fill=“tonexty”, fillcolor=“rgba(77,166,255,0.04)”), row=1, col=1)
fig.add_trace(go.Scatter(x=bb[“middle”].index, y=bb[“middle”], mode=“lines”, name=“BB Mid”,
line=dict(color=”#4da6ff”, width=1), opacity=0.5), row=1, col=1)

if show_kelt:
kc = keltner_channels(df_vis)
fig.add_trace(go.Scatter(x=kc[“upper”].index, y=kc[“upper”], mode=“lines”, name=“Kelt Upper”,
line=dict(color=”#b388ff”, width=1, dash=“dot”), opacity=0.6), row=1, col=1)
fig.add_trace(go.Scatter(x=kc[“lower”].index, y=kc[“lower”], mode=“lines”, name=“Kelt Lower”,
line=dict(color=”#b388ff”, width=1, dash=“dot”), opacity=0.6,
fill=“tonexty”, fillcolor=“rgba(179,136,255,0.04)”), row=1, col=1)
fig.add_trace(go.Scatter(x=kc[“middle”].index, y=kc[“middle”], mode=“lines”, name=“Kelt Mid”,
line=dict(color=”#b388ff”, width=1), opacity=0.5), row=1, col=1)

if show_don:
dc = donchian_channels(df_vis)
fig.add_trace(go.Scatter(x=dc[“upper”].index, y=dc[“upper”], mode=“lines”, name=“Don Upper”,
line=dict(color=”#ffd166”, width=1.2, dash=“dash”), opacity=0.7), row=1, col=1)
fig.add_trace(go.Scatter(x=dc[“lower”].index, y=dc[“lower”], mode=“lines”, name=“Don Lower”,
line=dict(color=”#ffd166”, width=1.2, dash=“dash”), opacity=0.7), row=1, col=1)

if show_st:
std = supertrend(df_vis)
bull = std[“supertrend”].where(std[“direction”] == 1)
bear = std[“supertrend”].where(std[“direction”] == -1)
fig.add_trace(go.Scatter(x=bull.index, y=bull, mode=“lines”, name=“ST Bull”,
line=dict(color=”#00e676”, width=2.5)), row=1, col=1)
fig.add_trace(go.Scatter(x=bear.index, y=bear, mode=“lines”, name=“ST Bear”,
line=dict(color=”#ff3d57”, width=2.5)), row=1, col=1)

if show_sar:
psar = parabolic_sar(df_vis)
bull_sar = psar[“sar”].where(psar[“direction”] == 1)
bear_sar = psar[“sar”].where(psar[“direction”] == -1)
fig.add_trace(go.Scatter(x=bull_sar.index, y=bull_sar, mode=“markers”, name=“SAR Bull”,
marker=dict(symbol=“circle”, size=4, color=”#00e676”)), row=1, col=1)
fig.add_trace(go.Scatter(x=bear_sar.index, y=bear_sar, mode=“markers”, name=“SAR Bear”,
marker=dict(symbol=“circle”, size=4, color=”#ff3d57”)), row=1, col=1)

# ── Trade markers ──

if st.session_state.replay_trades:
buys  = [t for t in st.session_state.replay_trades if t[“action”]==“BUY”]
sells = [t for t in st.session_state.replay_trades if t[“action”]==“SELL”]
if buys:
fig.add_trace(go.Scatter(
x=[t[“date”] for t in buys], y=[t[“price”] for t in buys],
mode=“markers+text”, name=“Your Buy”,
text=[“B”]*len(buys), textposition=“middle center”,
textfont=dict(color=”#000”, size=9, family=“IBM Plex Mono”),
marker=dict(symbol=“circle”, size=20, color=”#00e676”,
line=dict(color=”#000”, width=1))), row=1, col=1)
if sells:
fig.add_trace(go.Scatter(
x=[t[“date”] for t in sells], y=[t[“price”] for t in sells],
mode=“markers+text”, name=“Your Sell”,
text=[“S”]*len(sells), textposition=“middle center”,
textfont=dict(color=”#fff”, size=9, family=“IBM Plex Mono”),
marker=dict(symbol=“circle”, size=20, color=”#ff3d57”,
line=dict(color=”#000”, width=1))), row=1, col=1)

# ── Sub-charts ──

sub_row = 2
sub_colors = {“RSI”:”#ffd166”,“MACD”:”#4da6ff”,“CCI”:”#b388ff”,“Williams %R”:”#ff9f43”,“Volume”:”#4da6ff”}

if show_rsi:
r = rsi(df_vis[“Close”])
fig.add_trace(go.Scatter(x=r.index, y=r, mode=“lines”, name=“RSI”,
line=dict(color=sub_colors[“RSI”], width=1.5)), row=sub_row, col=1)
fig.add_hrect(y0=70, y1=100, fillcolor=“rgba(255,61,87,0.06)”, line_width=0, row=sub_row, col=1)
fig.add_hrect(y0=0,  y1=30,  fillcolor=“rgba(0,230,118,0.06)”, line_width=0, row=sub_row, col=1)
fig.add_hline(y=70, line_dash=“dot”, line_color=”#ff3d57”, line_width=0.8, row=sub_row, col=1)
fig.add_hline(y=30, line_dash=“dot”, line_color=”#00e676”, line_width=0.8, row=sub_row, col=1)
fig.update_yaxes(range=[0,100], row=sub_row, col=1)
sub_row += 1

if show_macd:
md = macd(df_vis[“Close”])
bar_colors = [”#00e676” if v >= 0 else “#ff3d57” for v in md[“histogram”].fillna(0)]
fig.add_trace(go.Bar(x=md[“histogram”].index, y=md[“histogram”], name=“MACD Hist”,
marker_color=bar_colors, opacity=0.65), row=sub_row, col=1)
fig.add_trace(go.Scatter(x=md[“macd”].index, y=md[“macd”], mode=“lines”, name=“MACD”,
line=dict(color=”#4da6ff”, width=1.5)), row=sub_row, col=1)
fig.add_trace(go.Scatter(x=md[“signal”].index, y=md[“signal”], mode=“lines”, name=“Signal”,
line=dict(color=”#ffd166”, width=1.2)), row=sub_row, col=1)
sub_row += 1

if show_cci:
c_vals = cci(df_vis)
fig.add_trace(go.Scatter(x=c_vals.index, y=c_vals, mode=“lines”, name=“CCI”,
line=dict(color=sub_colors[“CCI”], width=1.5)), row=sub_row, col=1)
fig.add_hline(y=100,  line_dash=“dot”, line_color=”#ff3d57”, line_width=0.8, row=sub_row, col=1)
fig.add_hline(y=-100, line_dash=“dot”, line_color=”#00e676”, line_width=0.8, row=sub_row, col=1)
sub_row += 1

if show_wpr:
w_vals = williams_r(df_vis)
fig.add_trace(go.Scatter(x=w_vals.index, y=w_vals, mode=“lines”, name=“Williams %R”,
line=dict(color=sub_colors[“Williams %R”], width=1.5)), row=sub_row, col=1)
fig.add_hline(y=-20,  line_dash=“dot”, line_color=”#ff3d57”, line_width=0.8, row=sub_row, col=1)
fig.add_hline(y=-80,  line_dash=“dot”, line_color=”#00e676”, line_width=0.8, row=sub_row, col=1)
fig.update_yaxes(range=[-100, 0], row=sub_row, col=1)
sub_row += 1

if show_vol:
vol_colors = [”#00e676” if c >= o else “#ff3d57”
for c, o in zip(df_vis[“Close”], df_vis[“Open”])]
fig.add_trace(go.Bar(x=df_vis.index, y=df_vis[“Volume”], name=“Volume”,
marker_color=vol_colors, opacity=0.6), row=sub_row, col=1)

# ── Chart layout ──

title_str = f”{st.session_state.replay_ticker}  ·  {cd.strftime(’%b %d, %Y’)}  ·  ${cp:,.2f}”
fig.update_layout(
**{k: v for k, v in PLOTLY_THEME.items() if k not in (“xaxis”,“yaxis”,“margin”)},
margin=dict(l=10, r=10, t=45, b=10),
height=580 + len(sub_charts) * 140,
xaxis_rangeslider_visible=False,
title=dict(text=title_str, font=dict(family=“IBM Plex Mono”, size=13, color=”#8896ab”), x=0.01),
showlegend=True,
legend=dict(bgcolor=”#0c1018”, bordercolor=”#1a2235”, borderwidth=1,
font=dict(size=10), orientation=“h”, y=1.02, x=0),
hovermode=“x unified”,
hoverlabel=dict(bgcolor=”#0c1018”, bordercolor=”#1a2235”, font=dict(family=“IBM Plex Mono”, size=11)),
dragmode=“pan”,
)

# Style all axes

for i in range(1, n_rows + 1):
fig.update_xaxes(gridcolor=”#1a2235”, linecolor=”#1a2235”,
tickfont=dict(size=10, color=”#3a4a5e”), zeroline=False, row=i, col=1)
fig.update_yaxes(gridcolor=”#1a2235”, linecolor=”#1a2235”,
tickfont=dict(size=10, color=”#3a4a5e”), zeroline=False, row=i, col=1)

# Animate on the last candle reveal (highlight current bar)

last_date = df_vis.index[-1]
fig.add_vline(x=last_date, line_dash=“dot”, line_color=“rgba(255,255,255,0.12)”, line_width=1)

config = dict(
displayModeBar=True,
modeBarButtonsToRemove=[“autoScale2d”,“lasso2d”,“select2d”,“toImage”],
scrollZoom=True,
displaylogo=False,
)
st.plotly_chart(fig, use_container_width=True, config=config)

# ── Playback controls ──────────────────────────────────────────────────────────

step = st.select_slider(“Step”, [1,2,3,5,10,20,50], value=1, label_visibility=“collapsed”)
pc = st.columns([1,1,1,3,1,1,1])
with pc[0]:
if st.button(“⏮”, use_container_width=True, help=“Jump to start”):
st.session_state.replay_idx = min(80, max_idx); st.rerun()
with pc[1]:
if st.button(f”◀  {step}”, use_container_width=True):
st.session_state.replay_idx = max(0, idx-step); st.rerun()
with pc[2]:
pass
with pc[3]:
st.markdown(f”””
<div style="display:flex;align-items:center;justify-content:center;gap:1.5rem;padding:0.4rem 0;">
<span style="font-family:'IBM Plex Mono',monospace;font-size:1rem;color:#eef2f7;">{cd.strftime(”%b %d, %Y”)}</span>
<span style="font-family:'IBM Plex Mono',monospace;font-size:0.65rem;color:#3a4a5e;">BAR {idx+1} / {max_idx+1}</span>
<span style="font-family:'IBM Plex Mono',monospace;font-size:0.65rem;color:#3a4a5e;">{pct_through:.0f}%</span>
</div>”””, unsafe_allow_html=True)
with pc[5]:
if st.button(f”{step}  ▶”, use_container_width=True):
st.session_state.replay_idx = min(max_idx, idx+step); st.rerun()
with pc[6]:
if st.button(“⏭”, use_container_width=True, help=“Jump to end”):
st.session_state.replay_idx = max_idx; st.rerun()

# Jump to bar

j1, j2 = st.columns([1, 5])
with j1:
jump = st.number_input(“Jump to bar”, 0, max_idx, idx, label_visibility=“visible”)
if jump != idx: st.session_state.replay_idx = jump; st.rerun()

# ── Trade panel ────────────────────────────────────────────────────────────────

st.markdown(’<div class="divider">Execute Trade</div>’, unsafe_allow_html=True)
t1, t2, t3 = st.columns(3)

with t1:
st.markdown(”””<div style="font-family:'IBM Plex Mono',monospace;font-size:0.62rem;color:#00e676;
text-transform:uppercase;letter-spacing:0.18em;margin-bottom:0.8rem;
padding:0.5rem 0.8rem;background:rgba(0,230,118,0.06);border:1px solid rgba(0,230,118,0.15);
border-radius:6px;">▲ Buy Order</div>”””, unsafe_allow_html=True)
bq = st.number_input(“Quantity”, min_value=0.01, value=1.0, step=1.0, key=“bq”, format=”%.2f”)
bcost = bq * cp
max_shares = cash / cp if cp > 0 else 0
st.markdown(f”””
<div style="background:#0c1018;border:1px solid #1a2235;border-radius:6px;padding:0.75rem;margin:0.5rem 0;font-family:'IBM Plex Mono',monospace;font-size:0.72rem;">
<div style="display:flex;justify-content:space-between;color:#3a4a5e;margin-bottom:0.3rem;">
<span>Order value</span><span style="color:#eef2f7;">${bcost:,.2f}</span>
</div>
<div style="display:flex;justify-content:space-between;color:#3a4a5e;">
<span>Max affordable</span><span style="color:#eef2f7;">{max_shares:.1f} shares</span>
</div>
</div>”””, unsafe_allow_html=True)
if st.button(“BUY”, type=“primary”, use_container_width=True, key=“do_buy”):
if bcost <= cash:
old_val = st.session_state.replay_avg_cost * st.session_state.replay_shares
st.session_state.replay_shares += bq
st.session_state.replay_cash   -= bcost
new_val = old_val + bcost
st.session_state.replay_avg_cost = new_val / st.session_state.replay_shares
st.session_state.replay_trades.append({“date”:cd,“action”:“BUY”,“price”:cp,“shares”:bq})
st.toast(f”✅ Bought {bq:.2f} {ticker} @ ${cp:,.2f}”); st.rerun()
else: st.error(f”Need ${bcost:,.2f} — only ${cash:,.2f} available.”)

with t2:
st.markdown(”””<div style="font-family:'IBM Plex Mono',monospace;font-size:0.62rem;color:#ff3d57;
text-transform:uppercase;letter-spacing:0.18em;margin-bottom:0.8rem;
padding:0.5rem 0.8rem;background:rgba(255,61,87,0.06);border:1px solid rgba(255,61,87,0.15);
border-radius:6px;">▼ Sell Order</div>”””, unsafe_allow_html=True)
sq = st.number_input(“Quantity”, min_value=0.01, max_value=float(shares) if shares > 0 else 0.01,
value=min(1.0, float(shares)) if shares > 0 else 0.01, step=1.0, key=“sq”, format=”%.2f”)
sproc = sq * cp
sell_pnl_col = “#00e676” if cp >= avg_cost else “#ff3d57”
st.markdown(f”””
<div style="background:#0c1018;border:1px solid #1a2235;border-radius:6px;padding:0.75rem;margin:0.5rem 0;font-family:'IBM Plex Mono',monospace;font-size:0.72rem;">
<div style="display:flex;justify-content:space-between;color:#3a4a5e;margin-bottom:0.3rem;">
<span>Proceeds</span><span style="color:#eef2f7;">${sproc:,.2f}</span>
</div>
<div style="display:flex;justify-content:space-between;color:#3a4a5e;">
<span>Realised P&L</span><span style="color:{sell_pnl_col};">${(cp-avg_cost)*sq:+,.2f}</span>
</div>
</div>”””, unsafe_allow_html=True)
if st.button(“SELL”, use_container_width=True, key=“do_sell”):
if shares > 0 and sq <= shares:
st.session_state.replay_shares -= sq
st.session_state.replay_cash   += sproc
if st.session_state.replay_shares <= 0: st.session_state.replay_avg_cost = 0.0
st.session_state.replay_trades.append({“date”:cd,“action”:“SELL”,“price”:cp,“shares”:sq})
st.toast(f”✅ Sold {sq:.2f} {ticker} @ ${cp:,.2f}”); st.rerun()
else: st.error(“Not enough shares.”)

with t3:
pnl_color = “#00e676” if pnl >= 0 else “#ff3d57”
ur_color  = “#00e676” if unrealised >= 0 else “#ff3d57”
bh_now = float(df_full[“Close”].iloc[idx]) / float(df_full[“Close”].iloc[0]) * init_capital
bh_pnl = bh_now - init_capital
bh_color = “#00e676” if pnl >= bh_pnl else “#ff3d57”
bh_word = “Beating” if pnl >= bh_pnl else “Trailing”
avg_cost_str = f”${avg_cost:.2f}” if avg_cost else “N/A”
pos_html = f”””
<div style="background:#0c1018;border:1px solid #1a2235;border-radius:10px;padding:1.2rem;">
<div style="font-family:'IBM Plex Mono',monospace;font-size:0.6rem;color:#3a4a5e;text-transform:uppercase;letter-spacing:0.18em;margin-bottom:0.9rem;">Position Summary</div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:1rem;">
<div class="metric-card" style="padding:0.7rem;"><div class="metric-val neu" style="font-size:1rem;">{shares:.2f}</div><div class="metric-lbl">Shares</div></div>
<div class="metric-card" style="padding:0.7rem;"><div class="metric-val neu" style="font-size:1rem;">{avg_cost_str}</div><div class="metric-lbl">Avg Cost</div></div>
<div class="metric-card" style="padding:0.7rem;"><div class="metric-val" style="color:{ur_color};font-size:1rem;">${unrealised:+,.2f}</div><div class="metric-lbl">Unrealised</div></div>
<div class="metric-card" style="padding:0.7rem;"><div class="metric-val" style="color:{pnl_color};font-size:1rem;">{pnl_pct:+.2f}%</div><div class="metric-lbl">Total Return</div></div>
</div>
<div style="border-top:1px solid #1a2235;padding-top:0.8rem;font-family:'IBM Plex Mono',monospace;font-size:0.7rem;color:#3a4a5e;">
vs Buy & Hold: <span style="color:{bh_color};">{bh_word} B&H by ${abs(pnl-bh_pnl):,.2f}</span>
</div>
</div>”””
st.markdown(pos_html, unsafe_allow_html=True)
if st.button(“Reset Portfolio”, use_container_width=True, key=“reset”):
st.session_state.replay_trades  = []
st.session_state.replay_cash    = init_capital
st.session_state.replay_shares  = 0.0
st.session_state.replay_avg_cost = 0.0
st.rerun()

# ── Trade log ──────────────────────────────────────────────────────────────────

if st.session_state.replay_trades:
st.markdown(’<div class="divider">Trade Log</div>’, unsafe_allow_html=True)
trades_list = st.session_state.replay_trades
wins  = sum(1 for i,t in enumerate(trades_list) if t[“action”]==“SELL” and i>0 and t[“price”]>trades_list[i-1][“price”])
total_sells = sum(1 for t in trades_list if t[“action”]==“SELL”)
tl1, tl2, tl3, tl4 = st.columns(4)
tl1.markdown(f’<div class="metric-card"><div class="metric-val neu">{len(trades_list)}</div><div class="metric-lbl">Total Trades</div></div>’, unsafe_allow_html=True)
tl2.markdown(f’<div class="metric-card"><div class="metric-val neu">{sum(1 for t in trades_list if t[“action”]==“BUY”)}</div><div class="metric-lbl">Buys</div></div>’, unsafe_allow_html=True)
tl3.markdown(f’<div class="metric-card"><div class="metric-val neu">{total_sells}</div><div class="metric-lbl">Sells</div></div>’, unsafe_allow_html=True)
tl4.markdown(f’<div class="metric-card"><div class="metric-val pos">${pnl:+,.2f}</div><div class="metric-lbl">Net P&L</div></div>’, unsafe_allow_html=True)

```
with st.expander(f"All {len(trades_list)} trades"):
    log = pd.DataFrame(trades_list)
    log["value"] = (log["price"] * log["shares"]).apply(lambda x: f"${x:,.2f}")
    log["price"] = log["price"].apply(lambda x: f"${x:,.2f}")
    log["shares"] = log["shares"].apply(lambda x: f"{x:.2f}")
    st.dataframe(log.set_index("date"), use_container_width=True)
```