import streamlit as st
import pandas as pd
import json
import sys, os
from datetime import date, timedelta

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.data import get_stock_data
from utils.styles import SHARED_CSS
from utils.nav import navbar

st.set_page_config(page_title="Replay | 11%", layout="wide", initial_sidebar_state="collapsed")
st.markdown(SHARED_CSS, unsafe_allow_html=True)
navbar()

st.markdown("""
<div class="page-header">
    <div class="page-header-eyebrow">Day Trading Practice</div>
    <h1>Market Simulator</h1>
    <p>Bar-by-bar replay on a professional TradingView chart. Practice buying and selling without knowing the future.</p>
</div>
""", unsafe_allow_html=True)

for k, v in [("rp_df", None), ("rp_ticker", ""), ("rp_capital", 10000)]:
    if k not in st.session_state:
        st.session_state[k] = v

with st.expander("Setup", expanded=st.session_state.rp_df is None):
    s1, s2, s3, s4, s5 = st.columns([2, 1.5, 1.5, 1.5, 1])
    with s1: ticker     = st.text_input("Ticker", value=st.session_state.rp_ticker or "AAPL")
    with s2: start_date = st.date_input("From",   value=date.today()-timedelta(days=730))
    with s3: end_date   = st.date_input("To",     value=date.today()-timedelta(days=30))
    with s4: capital    = st.number_input("Capital ($)", value=10000, min_value=100, step=1000)
    with s5:
        st.markdown("<div style='height:1.75rem'></div>", unsafe_allow_html=True)
        if st.button("Load", type="primary", use_container_width=True):
            with st.spinner(f"Fetching {ticker.upper()}…"):
                df = get_stock_data(ticker.upper(), str(start_date), str(end_date))
            if df.empty:
                st.error("No data found.")
            else:
                st.session_state.rp_df      = df
                st.session_state.rp_ticker  = ticker.upper()
                st.session_state.rp_capital = int(capital)
                st.rerun()

df_full = st.session_state.rp_df
if df_full is None or df_full.empty:
    st.markdown("""
    <div style="text-align:center;padding:5rem 2rem;border:1px dashed #1a2438;border-radius:12px;margin:2rem 0;">
        <div style="font-family:'Bebas Neue',sans-serif;font-size:3rem;letter-spacing:0.08em;">
            <span style="color:#00e676;">PRACTICE</span>
            <span style="color:#eef2f7;"> LIKE IT'S </span>
            <span style="color:#ff3d57;">REAL</span>
        </div>
        <div style="color:#3a4a5e;font-size:0.85rem;margin-top:1rem;">
            Load any ticker above. Play bar-by-bar, draw lines, trade without knowing the future.
        </div>
    </div>""", unsafe_allow_html=True)
    st.stop()

# ── Serialize OHLCV to JSON for JS
df_full.index = pd.to_datetime(df_full.index)
candles = []
for ts, row in df_full.iterrows():
    # TradingView Lightweight Charts uses Unix timestamps (seconds)
    candles.append({
        "time":  int(ts.timestamp()),
        "ts":    ts.strftime("%Y-%m-%d"),
        "open":  round(float(row["Open"]),  4),
        "high":  round(float(row["High"]),  4),
        "low":   round(float(row["Low"]),   4),
        "close": round(float(row["Close"]), 4),
        "volume":int(row["Volume"]),
    })

config_json = json.dumps({
    "candles":  candles,
    "ticker":   st.session_state.rp_ticker,
    "capital":  st.session_state.rp_capital,
    "startIdx": min(80, len(candles) - 1),
})

# ── TradingView Lightweight Charts Replay
HTML = r"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<script src="https://unpkg.com/lightweight-charts@4.1.3/dist/lightweight-charts.standalone.production.js"></script>
<style>
* { box-sizing:border-box; margin:0; padding:0; }
body { background:#06080c; color:#8896ab; font-family:'IBM Plex Mono',monospace; font-size:12px; overflow:hidden; }
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Bebas+Neue&display=swap');

#root { display:flex; flex-direction:column; height:100vh; padding:6px 8px; gap:5px; }

/* Tape */
#tape-wrap { overflow:hidden; height:22px; background:#030508; border:1px solid #1a2438; border-radius:4px; }
#tape { display:inline-flex; animation:scroll 24s linear infinite; white-space:nowrap; padding:3px 0; }
@keyframes scroll { from{transform:translateX(0)} to{transform:translateX(-50%)} }
.ti { padding:0 16px; border-right:1px solid #1a2438; font-size:10px; }
.ts { color:#3a4a5e; margin-right:4px; } .tv { color:#eef2f7; }
.tc.u { color:#00e676; } .tc.d { color:#ff3d57; }

/* Main body */
#body { display:flex; gap:6px; flex:1; min-height:0; }

/* Sidebar */
#sidebar { width:134px; min-width:134px; display:flex; flex-direction:column; gap:5px; overflow-y:auto; }
.panel { background:#0b0f17; border:1px solid #1a2438; border-radius:6px; padding:8px 10px; }
.ph { font-size:9px; color:#3a4a5e; text-transform:uppercase; letter-spacing:0.18em; margin-bottom:6px; padding-bottom:4px; border-bottom:1px solid #1a2438; }
.cr { display:flex; align-items:center; gap:5px; margin-bottom:3px; cursor:pointer; font-size:11px; color:#8896ab; }
.cr input { accent-color:#00e676; } .cr:hover { color:#eef2f7; }
#speed-range { width:100%; accent-color:#00e676; margin:2px 0; }
#play-btn { width:100%; padding:6px; border:none; border-radius:4px; background:linear-gradient(135deg,#007a2c,#00e676); color:#000; font-family:'IBM Plex Mono',monospace; font-size:11px; font-weight:700; letter-spacing:0.12em; cursor:pointer; margin-top:4px; }
#play-btn.p { background:linear-gradient(135deg,#6a0010,#ff3d57); color:#fff; }
.sr { display:flex; gap:3px; margin-top:4px; }
.sb { flex:1; padding:4px 2px; border:1px solid #1a2438; background:#0b0f17; color:#8896ab; border-radius:3px; font-family:'IBM Plex Mono',monospace; font-size:10px; cursor:pointer; }
.sb:hover { border-color:#00e676; color:#eef2f7; }
.db { width:100%; padding:5px; border:1px solid #1a2438; background:#0b0f17; color:#8896ab; border-radius:3px; font-family:'IBM Plex Mono',monospace; font-size:10px; cursor:pointer; margin-bottom:3px; text-align:left; }
.db:hover,.db.a { border-color:#ffd166; color:#ffd166; }
#cd { color:#ff3d57; } #cd:hover { border-color:#ff3d57; }

/* Chart area */
#chart-area { flex:1; display:flex; flex-direction:column; gap:5px; min-width:0; }
#tv-wrap { flex:1; position:relative; min-height:0; border-radius:6px; overflow:hidden; border:1px solid #1a2438; }
#tv-chart { width:100%; height:100%; }

/* Metrics */
#metrics { display:flex; background:#0b0f17; border:1px solid #1a2438; border-radius:6px; overflow:hidden; }
.mc { flex:1; padding:5px 7px; border-right:1px solid #1a2438; min-width:0; }
.mc:last-child { border-right:none; }
.mv { font-size:11px; font-weight:600; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.ml { font-size:7px; color:#3a4a5e; text-transform:uppercase; letter-spacing:0.14em; margin-top:1px; }
.g{color:#00e676;}.r{color:#ff3d57;}.b{color:#4da6ff;}.w{color:#eef2f7;}

/* Progress */
#prog-wrap { height:3px; background:#1a2438; border-radius:2px; }
#prog-fill { height:100%; background:linear-gradient(90deg,#00e676,#4da6ff); border-radius:2px; width:0%; transition:width 0.1s; }

/* Trade panel */
#trade-panel { display:flex; gap:6px; }
.tb { flex:1; background:#0b0f17; border:1px solid #1a2438; border-radius:6px; padding:9px; }
.th { font-size:9px; text-transform:uppercase; letter-spacing:0.16em; margin-bottom:7px; padding:3px 7px; border-radius:3px; }
.bh { color:#00e676; background:rgba(0,230,118,0.06); border:1px solid rgba(0,230,118,0.12); }
.sh { color:#ff3d57; background:rgba(255,61,87,0.06); border:1px solid rgba(255,61,87,0.12); }
.ph2{ color:#4da6ff; background:rgba(77,166,255,0.06); border:1px solid rgba(77,166,255,0.12); }
.or { display:flex; justify-content:space-between; margin-bottom:5px; font-size:10px; color:#3a4a5e; }
.or span:last-child { color:#eef2f7; }
.qr { display:flex; align-items:center; gap:5px; margin-bottom:5px; }
.ql { font-size:10px; color:#3a4a5e; white-space:nowrap; }
.qi { flex:1; background:#0e1420; border:1px solid #1a2438; color:#eef2f7; font-family:'IBM Plex Mono',monospace; font-size:11px; padding:3px 6px; border-radius:3px; width:0; outline:none; }
.qi:focus { border-color:#4da6ff; }
.qb { padding:3px 7px; border:1px solid #1a2438; border-radius:3px; background:#0e1420; color:#8896ab; cursor:pointer; font-family:'IBM Plex Mono',monospace; font-size:10px; }
.qb:hover { color:#eef2f7; }
.eb { width:100%; padding:6px; border:none; border-radius:4px; font-family:'IBM Plex Mono',monospace; font-size:11px; font-weight:700; letter-spacing:0.1em; cursor:pointer; }
#buy-btn { background:linear-gradient(135deg,#005c1e,#00e676); color:#000; }
#sell-btn { background:linear-gradient(135deg,#7a0015,#ff3d57); color:#fff; }
#reset-btn { width:100%; padding:4px; border:1px solid #1a2438; background:#0b0f17; color:#3a4a5e; border-radius:3px; cursor:pointer; font-family:'IBM Plex Mono',monospace; font-size:10px; margin-top:5px; }
#reset-btn:hover { border-color:#ff3d57; color:#ff3d57; }
.pg { display:grid; grid-template-columns:1fr 1fr; gap:4px; }
.pc { background:#0e1420; border-radius:3px; padding:4px 6px; }
.pv { font-size:11px; font-weight:600; }
.pl { font-size:7px; color:#3a4a5e; text-transform:uppercase; letter-spacing:0.1em; margin-top:1px; }

/* Toast */
#toast-area { position:fixed; bottom:16px; right:16px; z-index:999; display:flex; flex-direction:column; gap:5px; }
.toast { background:#0e1420; border:1px solid #1a2438; border-radius:6px; padding:7px 12px; font-size:11px; color:#eef2f7; animation:tin 0.2s ease; }
.toast.buy  { border-left:3px solid #00e676; }
.toast.sell { border-left:3px solid #ff3d57; }
@keyframes tin { from{opacity:0;transform:translateX(16px)} to{opacity:1;transform:translateX(0)} }
</style>
</head>
<body>
<div id="root">
  <div id="tape-wrap"><div id="tape"></div></div>

  <div id="body">
    <div id="sidebar">
      <div class="panel">
        <div class="ph">Overlays</div>
        <label class="cr"><input type="checkbox" id="ov-sma20"> SMA 20</label>
        <label class="cr"><input type="checkbox" id="ov-sma50"> SMA 50</label>
        <label class="cr"><input type="checkbox" id="ov-ema20"> EMA 20</label>
        <label class="cr"><input type="checkbox" id="ov-ema50"> EMA 50</label>
        <label class="cr"><input type="checkbox" id="ov-vwap">  VWAP</label>
        <label class="cr"><input type="checkbox" id="ov-bb">    BB</label>
      </div>
      <div class="panel">
        <div class="ph">Sub-chart</div>
        <label class="cr"><input type="checkbox" id="sc-vol" checked> Volume</label>
        <label class="cr"><input type="checkbox" id="sc-rsi">  RSI (14)</label>
        <label class="cr"><input type="checkbox" id="sc-macd"> MACD</label>
      </div>
      <div class="panel">
        <div class="ph">Playback</div>
        <div style="display:flex;justify-content:space-between;font-size:9px;color:#3a4a5e;">
          <span>Slow</span><span id="sp-lbl" style="color:#ffd166;">0.7s</span><span>Fast</span>
        </div>
        <input type="range" id="speed-range" min="1" max="10" value="5">
        <button id="play-btn">▶ PLAY</button>
        <div class="sr">
          <button class="sb" id="b1">-1</button><button class="sb" id="b5">-5</button>
          <button class="sb" id="f1">+1</button><button class="sb" id="f5">+5</button>
        </div>
      </div>
    </div>

    <div id="chart-area">
      <div id="tv-wrap"><div id="tv-chart"></div></div>
      <div id="metrics">
        <div class="mc"><div class="mv b" id="m-price">$0.00</div><div class="ml">Price</div></div>
        <div class="mc"><div class="mv w" id="m-port">$0.00</div><div class="ml">Portfolio</div></div>
        <div class="mc"><div class="mv" id="m-pnl">$0.00</div><div class="ml">P&L</div></div>
        <div class="mc"><div class="mv" id="m-ret">0.00%</div><div class="ml">Return</div></div>
        <div class="mc"><div class="mv" id="m-ur">$0.00</div><div class="ml">Unrealised</div></div>
        <div class="mc"><div class="mv w" id="m-cash">$0.00</div><div class="ml">Cash</div></div>
        <div class="mc"><div class="mv w" id="m-sh">0</div><div class="ml">Shares</div></div>
        <div class="mc"><div class="mv" id="m-date">---</div><div class="ml">Date</div></div>
      </div>
      <div id="prog-wrap"><div id="prog-fill"></div></div>
    </div>
  </div>

  <div id="trade-panel">
    <div class="tb">
      <div class="th bh">BUY ORDER</div>
      <div class="qr">
        <span class="ql">Qty</span>
        <button class="qb" id="buy-half">½</button>
        <input type="number" class="qi" id="buy-qty" value="1" min="0.01">
        <button class="qb" id="buy-max">Max</button>
      </div>
      <div class="or"><span>Value</span><span id="buy-val">$0.00</span></div>
      <div class="or"><span>Affordable</span><span id="buy-aff">0 sh</span></div>
      <button class="eb" id="buy-btn">BUY</button>
    </div>
    <div class="tb">
      <div class="th sh">SELL ORDER</div>
      <div class="qr">
        <span class="ql">Qty</span>
        <button class="qb" id="sell-half">½</button>
        <input type="number" class="qi" id="sell-qty" value="1" min="0.01">
        <button class="qb" id="sell-all">All</button>
      </div>
      <div class="or"><span>Proceeds</span><span id="sell-proc">$0.00</span></div>
      <div class="or"><span>P&L on trade</span><span id="sell-pnl">$0.00</span></div>
      <button class="eb" id="sell-btn">SELL</button>
    </div>
    <div class="tb">
      <div class="th ph2">POSITION</div>
      <div class="pg">
        <div class="pc"><div class="pv w" id="pos-sh">0.00</div><div class="pl">Shares</div></div>
        <div class="pc"><div class="pv w" id="pos-ac">N/A</div><div class="pl">Avg Cost</div></div>
        <div class="pc"><div class="pv" id="pos-ur">$0.00</div><div class="pl">Unrealised</div></div>
        <div class="pc"><div class="pv" id="pos-ret">0.00%</div><div class="pl">Return</div></div>
      </div>
      <button id="reset-btn">Reset Portfolio</button>
    </div>
  </div>
</div>
<div id="toast-area"></div>

<script>
// ── Config
const CFG = __CONFIG__;
const ALL = CFG.candles;
const TICKER = CFG.ticker;
const INIT_CAP = CFG.capital;

let curIdx = CFG.startIdx;
let cash = INIT_CAP, shares = 0, avgCost = 0;
let trades = [];
let playing = false, playTimer = null;

// ── TradingView Lightweight Chart setup
const tvWrap = document.getElementById('tv-wrap');

const chart = LightweightCharts.createChart(document.getElementById('tv-chart'), {
  width: tvWrap.clientWidth,
  height: tvWrap.clientHeight,
  layout: {
    background: { type: 'solid', color: '#0b0f17' },
    textColor: '#8896ab',
    fontFamily: "'IBM Plex Mono', monospace",
    fontSize: 10,
  },
  grid: {
    vertLines: { color: '#0f1621' },
    horzLines: { color: '#0f1621' },
  },
  crosshair: {
    mode: LightweightCharts.CrosshairMode.Normal,
    vertLine: { color: '#2a3550', labelBackgroundColor: '#1a2235' },
    horzLine: { color: '#2a3550', labelBackgroundColor: '#1a2235' },
  },
  rightPriceScale: {
    borderColor: '#1a2438',
    textColor: '#3a4a5e',
  },
  timeScale: {
    borderColor: '#1a2438',
    timeVisible: true,
    secondsVisible: false,
    tickMarkFormatter: (time) => {
      const d = new Date(time * 1000);
      return `${d.getMonth()+1}/${d.getDate()}`;
    },
  },
  handleScroll: true,
  handleScale: true,
});

// Main candlestick series
const candleSeries = chart.addCandlestickSeries({
  upColor:   '#00e676',
  downColor: '#ff3d57',
  borderUpColor:   '#00e676',
  borderDownColor: '#ff3d57',
  wickUpColor:   '#00e676',
  wickDownColor: '#ff3d57',
});

// Volume series (histogram)
const volSeries = chart.addHistogramSeries({
  color: '#1a2438',
  priceFormat: { type: 'volume' },
  priceScaleId: 'vol',
  scaleMargins: { top: 0.8, bottom: 0 },
});

// Overlay line series
const sma20Series = chart.addLineSeries({ color:'#4da6ff', lineWidth:1, priceLineVisible:false, lastValueVisible:false, visible:false });
const sma50Series = chart.addLineSeries({ color:'#ffd166', lineWidth:1, lineStyle:2, priceLineVisible:false, lastValueVisible:false, visible:false });
const ema20Series = chart.addLineSeries({ color:'#b388ff', lineWidth:1, priceLineVisible:false, lastValueVisible:false, visible:false });
const ema50Series = chart.addLineSeries({ color:'#ff9f43', lineWidth:1, lineStyle:2, priceLineVisible:false, lastValueVisible:false, visible:false });
const vwapSeries  = chart.addLineSeries({ color:'#00e5ff', lineWidth:1, lineStyle:3, priceLineVisible:false, lastValueVisible:false, visible:false });
const bbUpperSeries = chart.addLineSeries({ color:'rgba(77,166,255,0.5)', lineWidth:1, priceLineVisible:false, lastValueVisible:false, visible:false });
const bbLowerSeries = chart.addLineSeries({ color:'rgba(77,166,255,0.5)', lineWidth:1, priceLineVisible:false, lastValueVisible:false, visible:false });

// RSI & MACD (separate pane — rendered as overlay in lower panel via separate series)
// For simplicity we'll use a second chart for sub-panels
let subChart = null, rsiSeries = null, macdLineSeries = null, macdSignalSeries = null, macdHistSeries = null;

// ── Pre-compute indicators on full dataset
function sma(arr, p) {
  return arr.map((_, i) => {
    if (i < p-1) return null;
    let s = 0; for (let j=0; j<p; j++) s += arr[i-j];
    return s/p;
  });
}
function ema(arr, p) {
  const k = 2/(p+1), out = new Array(arr.length).fill(null);
  let e = arr[0];
  for (let i=0; i<arr.length; i++) {
    if (i < p-1) { out[i]=null; continue; }
    if (i === p-1) { let s=0; for(let j=0;j<p;j++) s+=arr[j]; e=s/p; out[i]=e; continue; }
    e = arr[i]*k + e*(1-k); out[i]=e;
  }
  return out;
}
function rsi(arr, p=14) {
  const out = new Array(arr.length).fill(null);
  let ag=0, al=0;
  for (let i=1; i<=p; i++) { const d=arr[i]-arr[i-1]; if(d>0) ag+=d; else al-=d; }
  ag/=p; al/=p;
  out[p] = al===0 ? 100 : 100-(100/(1+ag/al));
  for (let i=p+1; i<arr.length; i++) {
    const d=arr[i]-arr[i-1], g=d>0?d:0, l=d<0?-d:0;
    ag=(ag*(p-1)+g)/p; al=(al*(p-1)+l)/p;
    out[i] = al===0?100:100-(100/(1+ag/al));
  }
  return out;
}
function vwap(candles) {
  let cp=0, cv=0;
  return candles.map(c => { const t=(c.high+c.low+c.close)/3; cp+=t*c.volume; cv+=c.volume; return cv>0?cp/cv:null; });
}
function bb(arr, p=20, mult=2) {
  const mid=sma(arr,p);
  return arr.map((_,i)=>{
    if(mid[i]==null) return {u:null,l:null};
    const sl=arr.slice(Math.max(0,i-p+1),i+1);
    const std=Math.sqrt(sl.reduce((s,v)=>(s+(v-mid[i])**2),0)/sl.length);
    return {u:mid[i]+mult*std, l:mid[i]-mult*std};
  });
}
function macdCalc(arr) {
  const f=ema(arr,12), s=ema(arr,26);
  const line=arr.map((_,i)=>f[i]!=null&&s[i]!=null?f[i]-s[i]:null);
  const sig=ema(line.map(v=>v??0),9).map((v,i)=>line[i]!=null?v:null);
  const hist=line.map((v,i)=>v!=null&&sig[i]!=null?v-sig[i]:null);
  return {line,signal:sig,hist};
}

const closes  = ALL.map(c=>c.close);
const volumes = ALL.map(c=>c.volume);
const PRE = {
  sma20: sma(closes,20), sma50: sma(closes,50),
  ema20: ema(closes,20), ema50: ema(closes,50),
  vwap:  vwap(ALL.map(c=>({high:c.high,low:c.low,close:c.close,volume:c.volume}))),
  bb:    bb(closes),
  rsi:   rsi(closes),
  macd:  macdCalc(closes),
};

// ── Update chart to show up to curIdx
function updateChart() {
  const vis = ALL.slice(0, curIdx + 1);

  // Candles
  const candleData = vis.map(c => ({
    time:  c.time,
    open:  c.open,
    high:  c.high,
    low:   c.low,
    close: c.close,
  }));
  candleSeries.setData(candleData);

  // Volume
  if (document.getElementById('sc-vol').checked) {
    volSeries.applyOptions({ visible: true });
    volSeries.setData(vis.map((c,i) => ({
      time:  c.time,
      value: c.volume,
      color: c.close >= c.open ? 'rgba(0,230,118,0.4)' : 'rgba(255,61,87,0.4)',
    })));
  } else {
    volSeries.applyOptions({ visible: false });
  }

  // Overlay helpers
  function setLine(series, values, checked_id) {
    const show = document.getElementById(checked_id).checked;
    series.applyOptions({ visible: show });
    if (show) {
      series.setData(vis.map((c,i)=>({ time:c.time, value:values[i] })).filter(d=>d.value!=null));
    }
  }
  setLine(sma20Series, PRE.sma20, 'ov-sma20');
  setLine(sma50Series, PRE.sma50, 'ov-sma50');
  setLine(ema20Series, PRE.ema20, 'ov-ema20');
  setLine(ema50Series, PRE.ema50, 'ov-ema50');
  setLine(vwapSeries,  PRE.vwap,  'ov-vwap');

  const showBB = document.getElementById('ov-bb').checked;
  bbUpperSeries.applyOptions({ visible: showBB });
  bbLowerSeries.applyOptions({ visible: showBB });
  if (showBB) {
    bbUpperSeries.setData(vis.map((c,i)=>({ time:c.time, value:PRE.bb[i].u })).filter(d=>d.value!=null));
    bbLowerSeries.setData(vis.map((c,i)=>({ time:c.time, value:PRE.bb[i].l })).filter(d=>d.value!=null));
  }

  // Trade markers
  const markers = trades
    .map(tr => {
      const ci = ALL.findIndex(c => c.ts === tr.date);
      if (ci < 0 || ci > curIdx) return null;
      return {
        time:     ALL[ci].time,
        position: tr.action === 'BUY' ? 'belowBar' : 'aboveBar',
        color:    tr.action === 'BUY' ? '#00e676' : '#ff3d57',
        shape:    tr.action === 'BUY' ? 'arrowUp'  : 'arrowDown',
        text:     tr.action === 'BUY' ? `B $${tr.price.toFixed(2)}` : `S $${tr.price.toFixed(2)}`,
        size: 2,
      };
    })
    .filter(Boolean);
  candleSeries.setMarkers(markers);

  // Scroll to latest
  chart.timeScale().scrollToPosition(3, false);

  updateHUD();
}

// ── HUD update
function updateHUD() {
  const c = ALL[curIdx];
  const lp = c.close;
  const pv = cash + shares * lp;
  const pnl = pv - INIT_CAP;
  const pnlPct = pnl / INIT_CAP * 100;
  const ur = avgCost > 0 && shares > 0 ? (lp - avgCost) * shares : 0;

  set('m-price', `$${lp.toFixed(2)}`, 'b');
  set('m-port',  `$${pv.toFixed(2)}`, 'w');
  set('m-pnl',   (pnl>=0?'+':'')+`$${Math.abs(pnl).toFixed(2)}`, pnl>=0?'g':'r');
  set('m-ret',   (pnlPct>=0?'+':'')+pnlPct.toFixed(2)+'%', pnlPct>=0?'g':'r');
  set('m-ur',    (ur>=0?'+':'')+`$${Math.abs(ur).toFixed(2)}`, ur>=0?'g':'r');
  set('m-cash',  `$${cash.toFixed(2)}`, 'w');
  set('m-sh',    shares.toFixed(2), 'w');
  set('m-date',  c.ts.slice(5), '');

  document.getElementById('prog-fill').style.width = ((curIdx+1)/ALL.length*100)+'%';

  const maxQ = cash / lp;
  const bq = parseFloat(document.getElementById('buy-qty').value)||0;
  const sq = parseFloat(document.getElementById('sell-qty').value)||0;
  document.getElementById('buy-val').textContent  = `$${(bq*lp).toFixed(2)}`;
  document.getElementById('buy-aff').textContent  = maxQ.toFixed(1)+' sh';
  document.getElementById('sell-proc').textContent= `$${(sq*lp).toFixed(2)}`;
  const spnl = avgCost>0?(lp-avgCost)*sq:0;
  const spEl=document.getElementById('sell-pnl');
  spEl.textContent=(spnl>=0?'+':'')+`$${Math.abs(spnl).toFixed(2)}`;
  spEl.style.color=spnl>=0?'#00e676':'#ff3d57';

  document.getElementById('pos-sh').textContent  = shares.toFixed(2);
  document.getElementById('pos-ac').textContent  = avgCost>0?`$${avgCost.toFixed(2)}`:'N/A';
  const urEl=document.getElementById('pos-ur');
  urEl.textContent=(ur>=0?'+':'')+`$${Math.abs(ur).toFixed(2)}`;
  urEl.className='pv '+(ur>=0?'g':'r');
  const retEl=document.getElementById('pos-ret');
  retEl.textContent=(pnlPct>=0?'+':'')+pnlPct.toFixed(2)+'%';
  retEl.className='pv '+(pnlPct>=0?'g':'r');

  updateTape(lp, c);
}

function set(id, val, cls) {
  const el=document.getElementById(id);
  if(!el) return;
  el.textContent=val;
  if(cls) el.className='mv '+cls;
}

function updateTape(lp, c) {
  const chg=lp-c.open, pct=chg/c.open*100;
  const items=[
    {s:TICKER,v:`$${lp.toFixed(2)}`,c:(chg>=0?'+':'')+pct.toFixed(2)+'%',u:chg>=0},
    {s:'VOL',v:c.volume.toLocaleString(),c:'',u:true},
    {s:'HI',v:`$${c.high.toFixed(2)}`,c:'',u:true},
    {s:'LO',v:`$${c.low.toFixed(2)}`,c:'',u:false},
    {s:'OPEN',v:`$${c.open.toFixed(2)}`,c:'',u:true},
    {s:'BAR',v:`${curIdx+1}/${ALL.length}`,c:'',u:true},
  ];
  const t=document.getElementById('tape');
  const html=[...items,...items].map(i=>`<span class="ti"><span class="ts">${i.s}</span><span class="tv">${i.v}</span>${i.c?`<span class="tc ${i.u?'u':'d'}"> ${i.c}</span>`:''}</span>`).join('');
  t.innerHTML=html+html;
}

// ── Playback
const SPEEDS=[3.0,2.0,1.5,1.0,0.7,0.5,0.3,0.2,0.12,0.07];
function getSpeed(){return SPEEDS[document.getElementById('speed-range').value-1]||0.7;}
document.getElementById('speed-range').addEventListener('input',()=>{document.getElementById('sp-lbl').textContent=getSpeed().toFixed(2)+'s';});

function advance(){if(curIdx<ALL.length-1){curIdx++;updateChart();}else stopPlay();}
function startPlay(){
  playing=true;
  document.getElementById('play-btn').textContent='⏸ PAUSE';
  document.getElementById('play-btn').classList.add('p');
  function step(){advance();playTimer=setTimeout(step,getSpeed()*1000);}
  step();
}
function stopPlay(){
  playing=false;clearTimeout(playTimer);playTimer=null;
  document.getElementById('play-btn').textContent='▶ PLAY';
  document.getElementById('play-btn').classList.remove('p');
}
document.getElementById('play-btn').addEventListener('click',()=>playing?stopPlay():startPlay());
document.getElementById('b1').addEventListener('click',()=>{if(curIdx>0){curIdx--;updateChart();}});
document.getElementById('b5').addEventListener('click',()=>{curIdx=Math.max(0,curIdx-5);updateChart();});
document.getElementById('f1').addEventListener('click',()=>{if(curIdx<ALL.length-1){curIdx++;updateChart();}});
document.getElementById('f5').addEventListener('click',()=>{curIdx=Math.min(ALL.length-1,curIdx+5);updateChart();});

// ── Overlay toggles
document.querySelectorAll('.cr input').forEach(cb=>cb.addEventListener('change',()=>updateChart()));

// ── Trading
document.getElementById('buy-qty').addEventListener('input',updateHUD);
document.getElementById('sell-qty').addEventListener('input',updateHUD);
document.getElementById('buy-half').addEventListener('click',()=>{const lp=ALL[curIdx].close;document.getElementById('buy-qty').value=(cash/lp/2).toFixed(2);updateHUD();});
document.getElementById('buy-max').addEventListener('click',()=>{const lp=ALL[curIdx].close;document.getElementById('buy-qty').value=Math.floor(cash/lp*100)/100;updateHUD();});
document.getElementById('sell-half').addEventListener('click',()=>{document.getElementById('sell-qty').value=(shares/2).toFixed(2);updateHUD();});
document.getElementById('sell-all').addEventListener('click',()=>{document.getElementById('sell-qty').value=shares.toFixed(2);updateHUD();});

document.getElementById('buy-btn').addEventListener('click',()=>{
  const lp=ALL[curIdx].close, qty=parseFloat(document.getElementById('buy-qty').value)||0;
  const cost=qty*lp;
  if(qty<=0||cost>cash){toast('Insufficient funds','sell');return;}
  const ov=avgCost*shares; shares+=qty; cash-=cost; avgCost=(ov+cost)/shares;
  trades.push({date:ALL[curIdx].ts,action:'BUY',price:lp,shares:qty});
  toast(`Bought ${qty.toFixed(2)} ${TICKER} @ $${lp.toFixed(2)}`,'buy');
  updateChart();
});
document.getElementById('sell-btn').addEventListener('click',()=>{
  const lp=ALL[curIdx].close, qty=parseFloat(document.getElementById('sell-qty').value)||0;
  if(qty<=0||qty>shares){toast('Not enough shares','sell');return;}
  shares-=qty; cash+=qty*lp;
  if(shares<=0){shares=0;avgCost=0;}
  trades.push({date:ALL[curIdx].ts,action:'SELL',price:lp,shares:qty});
  toast(`Sold ${qty.toFixed(2)} ${TICKER} @ $${lp.toFixed(2)}`,'sell');
  updateChart();
});
document.getElementById('reset-btn').addEventListener('click',()=>{cash=INIT_CAP;shares=0;avgCost=0;trades=[];updateChart();});

function toast(msg,type){
  const el=document.createElement('div');el.className='toast '+type;el.textContent=msg;
  document.getElementById('toast-area').appendChild(el);
  setTimeout(()=>el.remove(),3000);
}

// ── Resize
const ro=new ResizeObserver(()=>{
  chart.resize(tvWrap.clientWidth,tvWrap.clientHeight);
});
ro.observe(tvWrap);

// ── Init
updateChart();
</script>
</body>
</html>
"""

html_out = HTML.replace("__CONFIG__", config_json)

import streamlit.components.v1 as components
components.html(html_out, height=860, scrolling=False)
