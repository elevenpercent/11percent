import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import json
import sys, os
from datetime import date, timedelta
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.data import get_stock_data
from utils.indicators import sma, ema, bollinger_bands, supertrend
from utils.styles import SHARED_CSS

st.set_page_config(page_title="Replay | 11%", page_icon="▶", layout="wide", initial_sidebar_state="collapsed")
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

for k,v in [("replay_trades",[]),("replay_cash",10000.0),("replay_shares",0.0),("replay_df",None),("replay_start_idx",50)]:
    if k not in st.session_state: st.session_state[k]=v

st.markdown('''<div class="page-header"><h1>Chart Replay</h1><p>Step through historical candles with a live chart. Keyboard: ← → to step, Space to play/pause.</p></div>''', unsafe_allow_html=True)

# ── Config ────────────────────────────────────────────────────────────────────
st.markdown('<div class="config-panel">', unsafe_allow_html=True)
rc1,rc2,rc3,rc4 = st.columns([2,1.5,1.5,1.5])
with rc1: ticker     = st.text_input("Ticker", value="AAPL").upper().strip()
with rc2: start_date = st.date_input("Start",  value=date.today()-timedelta(days=365*2))
with rc3: end_date   = st.date_input("End",    value=date.today())
with rc4: capital    = st.number_input("Starting Capital ($)", value=10000, min_value=100, step=1000)
oc1,oc2,oc3,oc4,oc5,oc6 = st.columns(6)
with oc1: show_sma = st.checkbox("SMA", value=True)
with oc2: sma_win  = st.slider("SMA Period", 5, 200, 20) if show_sma else 20
with oc3: show_ema = st.checkbox("EMA")
with oc4: ema_win  = st.slider("EMA Period", 5, 200, 50) if show_ema else 50
with oc5: show_bb  = st.checkbox("Bollinger Bands")
with oc6: show_st  = st.checkbox("SuperTrend")
load_btn = st.button("Load / Reset")
st.markdown('</div>', unsafe_allow_html=True)

# ── Load data ─────────────────────────────────────────────────────────────────
if load_btn or st.session_state.replay_df is None:
    with st.spinner(f"Loading {ticker}..."):
        df_full = get_stock_data(ticker, str(start_date), str(end_date))
    if df_full.empty: st.stop()
    st.session_state.replay_df     = df_full
    st.session_state.replay_trades  = []
    st.session_state.replay_cash    = float(capital)
    st.session_state.replay_shares  = 0.0
    st.session_state.replay_start_idx = min(50, len(df_full)-1)
    st.rerun()

df_full = st.session_state.replay_df
if df_full is None or df_full.empty:
    st.markdown('<div class="info-box">Enter a ticker above and click Load to begin.</div>', unsafe_allow_html=True)
    st.stop()

# ── Serialize candle data ─────────────────────────────────────────────────────
def to_unix(ts):
    import pandas as pd
    if hasattr(ts, "timestamp"): return int(ts.timestamp())
    return int(pd.Timestamp(ts).timestamp())

candles = [
    {"t": to_unix(row.Index), "o": round(float(row.Open),4), "h": round(float(row.High),4),
     "l": round(float(row.Low),4),  "c": round(float(row.Close),4), "v": int(row.Volume)}
    for row in df_full.itertuples()
]

# ── Build overlays ────────────────────────────────────────────────────────────
overlays = {}
def series_to_overlay(ser, df):
    out = []
    for ts, val in zip(df.index, ser):
        if pd.notna(val): out.append({"time": to_unix(ts), "value": round(float(val), 4)})
    return out

if show_sma:
    s = sma(df_full["Close"], sma_win)
    overlays[f"SMA {sma_win}"] = series_to_overlay(s, df_full)
if show_ema:
    e = ema(df_full["Close"], ema_win)
    overlays[f"EMA {ema_win}"] = series_to_overlay(e, df_full)
if show_bb:
    bb = bollinger_bands(df_full["Close"])
    overlays["BB Upper"]  = series_to_overlay(bb["upper"],  df_full)
    overlays["BB Middle"] = series_to_overlay(bb["middle"], df_full)
    overlays["BB Lower"]  = series_to_overlay(bb["lower"],  df_full)
if show_st:
    std = supertrend(df_full)
    bull = std["supertrend"].where(std["direction"]==1)
    bear = std["supertrend"].where(std["direction"]==-1)
    overlays["ST Bull"] = series_to_overlay(bull, df_full)
    overlays["ST Bear"] = series_to_overlay(bear, df_full)

# ── Trade list for chart markers ──────────────────────────────────────────────
trade_markers = [
    {"time": to_unix(t["date"]), "action": t["action"], "shares": t["shares"], "price": t["price"]}
    for t in st.session_state.replay_trades
]

# ── Build and inject the component ───────────────────────────────────────────
COMPONENT = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  body { background:#07090d; font-family:'IBM Plex Mono',monospace; color:#cdd5e0; }
  #chart { width:100%; height:480px; }
  #controls {
    display:flex; align-items:center; gap:12px; padding:10px 12px;
    background:#0d1117; border-top:1px solid #1c2333; flex-wrap:wrap;
  }
  .ctrl-btn {
    background:transparent; color:#00d68f; border:1px solid #00d68f;
    padding:5px 14px; border-radius:3px; font-family:'IBM Plex Mono',monospace;
    font-size:0.7rem; letter-spacing:0.08em; cursor:pointer; text-transform:uppercase;
    transition:all 0.15s;
  }
  .ctrl-btn:hover, .ctrl-btn.active { background:#00d68f; color:#000; }
  .ctrl-btn.danger { color:#ff4757; border-color:#ff4757; }
  .ctrl-btn.danger:hover { background:#ff4757; color:#000; }
  #date-display {
    font-size:0.75rem; color:#00d68f; letter-spacing:0.06em; min-width:110px;
  }
  #bar-display { font-size:0.65rem; color:#3a4558; }
  #speed-wrap { display:flex; align-items:center; gap:8px; font-size:0.65rem; color:#3a4558; }
  #speed { width:80px; accent-color:#00d68f; }
  #ohlc-display { font-size:0.65rem; color:#cdd5e0; letter-spacing:0.04em; margin-left:auto; }
  .ohlc-o{color:#cdd5e0;} .ohlc-h{color:#00d68f;} .ohlc-l{color:#ff4757;} .ohlc-c{color:#00d68f;}
  #progress-bar { height:2px; background:#1c2333; position:relative; }
  #progress-fill { height:100%; background:#00d68f; transition:width 0.1s; }
</style>
</head>
<body>
<div id="progress-bar"><div id="progress-fill" style="width:0%"></div></div>
<div id="chart"></div>
<div id="controls">
  <button class="ctrl-btn" onclick="goStart()">⏮ Start</button>
  <button class="ctrl-btn" onclick="stepBack()">◀ -1</button>
  <button class="ctrl-btn" id="play-btn" onclick="togglePlay()">▶ Play</button>
  <button class="ctrl-btn" onclick="stepForward()">+1 ▶</button>
  <button class="ctrl-btn" onclick="goEnd()">End ⏭</button>
  <div id="speed-wrap">
    Speed: <input type="range" id="speed" min="50" max="1000" value="300" step="50" oninput="updateSpeed()">
    <span id="speed-label">300ms</span>
  </div>
  <div id="date-display">—</div>
  <div id="bar-display"></div>
  <div id="ohlc-display"></div>
</div>

<script src="https://unpkg.com/lightweight-charts@4.1.1/dist/lightweight-charts.standalone.production.js"></script>
<script>
const RAW      = __CANDLES__;
const TRADES   = __TRADES__;
const OVERLAYS = __OVERLAYS__;
const START_IDX = __START_IDX__;

let idx = START_IDX;
let playing = false;
let playInterval = null;
let speed = 300;

// ── Chart setup ──────────────────────────────────────────────────
const chart = LightweightCharts.createChart(document.getElementById('chart'), {
  width:  document.getElementById('chart').clientWidth,
  height: 480,
  layout: { background:{type:'solid',color:'#07090d'}, textColor:'#cdd5e0' },
  grid:   { vertLines:{color:'#1c2333'}, horzLines:{color:'#1c2333'} },
  crosshair: { mode: LightweightCharts.CrosshairMode.Normal },
  rightPriceScale: { borderColor:'#1c2333', textColor:'#cdd5e0' },
  timeScale: { borderColor:'#1c2333', textColor:'#3a4558', timeVisible:true },
  handleScroll: true, handleScale: true,
});

// Candlestick series
const candleSeries = chart.addCandlestickSeries({
  upColor:'#00d68f', downColor:'#ff4757',
  borderUpColor:'#00d68f', borderDownColor:'#ff4757',
  wickUpColor:'#00d68f', wickDownColor:'#ff4757',
});

// Volume series
const volSeries = chart.addHistogramSeries({
  color:'#1c2333', priceFormat:{type:'volume'},
  priceScaleId:'vol', scaleMargins:{top:0.85,bottom:0},
});

// Overlay series
const overlaySeries = {};
const OVERLAY_COLORS = ['#4da6ff','#b388ff','#ff9f43','#cdd5e0','#00d68f'];
let ci = 0;
for (const [name, vals] of Object.entries(OVERLAYS)) {
  overlaySeries[name] = chart.addLineSeries({
    color: name.includes('Bear') ? '#ff4757' : OVERLAY_COLORS[ci % OVERLAY_COLORS.length],
    lineWidth: 1, title: name, priceLineVisible: false,
  });
  ci++;
}

// Trade markers store
let allMarkers = [];

// ── Crosshair OHLC display ────────────────────────────────────────
chart.subscribeCrosshairMove(p => {
  if (!p || !p.seriesData) return;
  const d = p.seriesData.get(candleSeries);
  if (!d) return;
  document.getElementById('ohlc-display').innerHTML =
    `<span class="ohlc-o">O ${d.open?.toFixed(2)}</span>  ` +
    `<span class="ohlc-h">H ${d.high?.toFixed(2)}</span>  ` +
    `<span class="ohlc-l">L ${d.low?.toFixed(2)}</span>  ` +
    `<span class="ohlc-c">C ${d.close?.toFixed(2)}</span>`;
});

// ── Render up to idx ─────────────────────────────────────────────
function render() {
  const visible = RAW.slice(0, idx + 1);

  candleSeries.setData(visible.map(c => ({
    time: c.t, open: c.o, high: c.h, low: c.l, close: c.c
  })));

  volSeries.setData(visible.map(c => ({
    time: c.t, value: c.v,
    color: c.c >= c.o ? 'rgba(0,214,143,0.25)' : 'rgba(255,71,87,0.25)'
  })));

  for (const [name, vals] of Object.entries(OVERLAYS)) {
    const sliced = vals.slice(0, idx + 1).filter(v => v.value !== null && v.value !== undefined);
    overlaySeries[name].setData(sliced);
  }

  // Trade markers
  const markers = TRADES
    .filter(t => {
      const tTime = typeof t.time === 'number' ? t.time : Math.floor(new Date(t.time).getTime()/1000);
      return tTime <= RAW[idx].t;
    })
    .map(t => ({
      time: typeof t.time === 'number' ? t.time : Math.floor(new Date(t.time).getTime()/1000),
      position: t.action === 'BUY' ? 'belowBar' : 'aboveBar',
      color: t.action === 'BUY' ? '#00d68f' : '#ff4757',
      shape: t.action === 'BUY' ? 'arrowUp' : 'arrowDown',
      text: t.action === 'BUY' ? `B ${t.shares}` : `S ${t.shares}`,
    }));
  candleSeries.setMarkers(markers);

  // Update displays
  const cur = RAW[idx];
  const d = new Date(cur.t * 1000);
  document.getElementById('date-display').textContent =
    d.toISOString().slice(0, 10);
  document.getElementById('bar-display').textContent =
    `Bar ${idx + 1} / ${RAW.length}`;
  document.getElementById('progress-fill').style.width =
    `${((idx + 1) / RAW.length * 100).toFixed(1)}%`;

  // Scroll to latest bar
  chart.timeScale().scrollToPosition(3, false);

  // Post state back to Streamlit
  if (window.Streamlit) {
    Streamlit.setComponentValue({ idx: idx, ts: cur.t });
  }
}

// ── Controls ─────────────────────────────────────────────────────
function goStart()    { stopPlay(); idx = START_IDX; render(); }
function goEnd()      { stopPlay(); idx = RAW.length - 1; render(); }
function stepBack()   { stopPlay(); if (idx > START_IDX) { idx--; render(); } }
function stepForward(){ if (idx < RAW.length - 1) { idx++; render(); } else stopPlay(); }

function togglePlay() {
  playing ? stopPlay() : startPlay();
}
function startPlay() {
  playing = true;
  document.getElementById('play-btn').textContent = '⏸ Pause';
  document.getElementById('play-btn').classList.add('active');
  playInterval = setInterval(() => {
    if (idx >= RAW.length - 1) { stopPlay(); return; }
    stepForward();
  }, speed);
}
function stopPlay() {
  playing = false;
  document.getElementById('play-btn').textContent = '▶ Play';
  document.getElementById('play-btn').classList.remove('active');
  clearInterval(playInterval);
}
function updateSpeed() {
  speed = parseInt(document.getElementById('speed').value);
  document.getElementById('speed-label').textContent = speed + 'ms';
  if (playing) { stopPlay(); startPlay(); }
}

// Keyboard shortcuts
document.addEventListener('keydown', e => {
  if (e.key === 'ArrowRight') stepForward();
  if (e.key === 'ArrowLeft')  stepBack();
  if (e.key === ' ')          { e.preventDefault(); togglePlay(); }
});

// Responsive resize
window.addEventListener('resize', () => {
  chart.applyOptions({ width: document.getElementById('chart').clientWidth });
});

// ── Initial render ────────────────────────────────────────────────
render();
</script>
</body>
</html>
"""
COMPONENT = COMPONENT.replace("__CANDLES__",   json.dumps(candles))
COMPONENT = COMPONENT.replace("__TRADES__",    json.dumps(trade_markers))
COMPONENT = COMPONENT.replace("__OVERLAYS__",  json.dumps(overlays))
COMPONENT = COMPONENT.replace("__START_IDX__", str(st.session_state.replay_start_idx))

components.html(COMPONENT, height=560, scrolling=False)

# ── Portfolio metrics ─────────────────────────────────────────────────────────
# Use last known price from last candle
last_price = float(df_full["Close"].iloc[-1])
cash   = st.session_state.replay_cash
shares = st.session_state.replay_shares
pv     = cash + shares * last_price
pnl    = pv - float(capital)
pnl_pct = pnl / float(capital) * 100

st.markdown('<div class="price-divider">PORTFOLIO</div>', unsafe_allow_html=True)
m1,m2,m3,m4,m5,m6 = st.columns(6)
m1.markdown(f'<div class="metric-card"><div class="metric-val neu">${last_price:,.2f}</div><div class="metric-lbl">Last Price</div></div>', unsafe_allow_html=True)
m2.markdown(f'<div class="metric-card"><div class="metric-val neu">${pv:,.2f}</div><div class="metric-lbl">Portfolio</div></div>', unsafe_allow_html=True)
m3.markdown(f'<div class="metric-card"><div class="metric-val {"pos" if pnl>=0 else "neg"}">${pnl:+,.2f}</div><div class="metric-lbl">P&L</div></div>', unsafe_allow_html=True)
m4.markdown(f'<div class="metric-card"><div class="metric-val {"pos" if pnl_pct>=0 else "neg"}">{pnl_pct:+.2f}%</div><div class="metric-lbl">Return</div></div>', unsafe_allow_html=True)
m5.markdown(f'<div class="metric-card"><div class="metric-val neu">${cash:,.2f}</div><div class="metric-lbl">Cash</div></div>', unsafe_allow_html=True)
m6.markdown(f'<div class="metric-card"><div class="metric-val neu">${shares*last_price:,.2f}</div><div class="metric-lbl">Position</div></div>', unsafe_allow_html=True)

# ── Trading controls ─────────────────────────────────────────────────────────
st.markdown('<div class="price-divider">PRACTICE TRADING</div>', unsafe_allow_html=True)
st.markdown('<div style="font-family:IBM Plex Mono,monospace;font-size:0.65rem;color:#3a4558;margin-bottom:0.8rem;">Trades are logged and shown as markers on the chart. Click Load/Reset to replay from the start.</div>', unsafe_allow_html=True)
t1,t2,t3 = st.columns(3)
with t1:
    bq = st.number_input("Shares to Buy", min_value=0.0, value=1.0, step=1.0)
    if st.button("Buy", use_container_width=True):
        cost = bq * last_price
        if cost <= cash:
            st.session_state.replay_cash   -= cost
            st.session_state.replay_shares += bq
            st.session_state.replay_trades.append({"date": df_full.index[-1], "action": "BUY", "price": last_price, "shares": bq})
            st.success(f"Bought {bq} shares @ ${last_price:.2f}"); st.rerun()
        else: st.error(f"Not enough cash. Need ${cost:,.2f}, have ${cash:,.2f}")
with t2:
    sq = st.number_input("Shares to Sell", min_value=0.0, max_value=float(shares) if shares>0 else 0.0, value=min(1.0,float(shares)), step=1.0)
    if st.button("Sell", use_container_width=True):
        if sq <= shares and sq > 0:
            st.session_state.replay_cash   += sq * last_price
            st.session_state.replay_shares -= sq
            st.session_state.replay_trades.append({"date": df_full.index[-1], "action": "SELL", "price": last_price, "shares": sq})
            st.success(f"Sold {sq} shares @ ${last_price:.2f}"); st.rerun()
        else: st.error("Not enough shares.")
with t3:
    st.markdown(f'<div class="metric-card"><div class="metric-lbl">Current Position</div><div class="metric-val neu" style="margin-top:0.4rem;">{shares:.2f} shares</div><div style="font-family:IBM Plex Mono,monospace;font-size:0.7rem;color:#3a4558;margin-top:0.3rem;">Value: ${shares*last_price:,.2f}</div></div>', unsafe_allow_html=True)
    if st.button("Reset Trades", use_container_width=True):
        st.session_state.replay_trades  = []
        st.session_state.replay_cash    = float(capital)
        st.session_state.replay_shares  = 0.0
        st.rerun()

if st.session_state.replay_trades:
    st.markdown('<div class="price-divider">TRADE LOG</div>', unsafe_allow_html=True)
    with st.expander(f"View {len(st.session_state.replay_trades)} trades"):
        st.dataframe(pd.DataFrame(st.session_state.replay_trades), use_container_width=True)
