import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import json
import sys, os
from datetime import date, timedelta
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.data import get_stock_data
from utils.indicators import sma, ema, bollinger_bands, supertrend, rsi, macd
from utils.styles import SHARED_CSS

st.set_page_config(page_title="Replay | 11%", page_icon="▶", layout="wide", initial_sidebar_state="collapsed")
st.markdown(SHARED_CSS, unsafe_allow_html=True)

# Loading screen CSS — shows dark bg immediately to mask flash
st.markdown("""
<style>
  [data-testid="stAppViewContainer"] { background-color:#07090d!important; }
  .stSpinner > div { border-top-color:#00d68f!important; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="nb"><div class="nb-brand"><span class="g">11</span><span class="r">%</span></div><div class="nb-links">', unsafe_allow_html=True)
_nav = st.columns([1,1,1,1,1,1])
with _nav[0]: st.page_link("app.py",                    label="Home")
with _nav[1]: st.page_link("pages/1_Backtest.py",       label="Backtest")
with _nav[2]: st.page_link("pages/2_Indicator_Test.py", label="Indicators")
with _nav[3]: st.page_link("pages/3_Replay.py",         label="Replay")
with _nav[4]: st.page_link("pages/4_Analysis.py",       label="Analysis")
with _nav[5]: st.page_link("pages/5_Assistant.py",      label="Assistant")
st.markdown('</div><div class="nb-tag">FREE · OPEN SOURCE</div></div>', unsafe_allow_html=True)

# ── Session state init ────────────────────────────────────────────────────────
for k, v in [
    ("replay_trades", []), ("replay_cash", 10000.0), ("replay_shares", 0.0),
    ("replay_df", None), ("replay_sl", None), ("replay_tp", None),
    ("replay_entry_price", None), ("replay_pnl_history", []),
]:
    if k not in st.session_state: st.session_state[k] = v

st.markdown('''<div class="page-header"><h1>Market Replay</h1><p>Simulate trading in the past. Draw lines, set stop loss & take profit, step through bars. Keyboard: ← → arrows, Space to play/pause.</p></div>''', unsafe_allow_html=True)

# ── Config panel ──────────────────────────────────────────────────────────────
st.markdown('<div class="config-panel">', unsafe_allow_html=True)
rc1, rc2, rc3, rc4 = st.columns([2, 1.5, 1.5, 1.5])
with rc1: ticker     = st.text_input("Ticker Symbol", value="AAPL").upper().strip()
with rc2: start_date = st.date_input("Start Date", value=date.today() - timedelta(days=365*2))
with rc3: end_date   = st.date_input("End Date",   value=date.today())
with rc4: capital    = st.number_input("Starting Capital ($)", value=10000, min_value=100, step=1000)

oc1, oc2, oc3, oc4, oc5, oc6, oc7, oc8 = st.columns(8)
with oc1: show_sma = st.checkbox("SMA", value=True)
with oc2: sma_win  = st.slider("Period", 5, 200, 20, key="sma_w") if show_sma else 20
with oc3: show_ema = st.checkbox("EMA")
with oc4: ema_win  = st.slider("Period", 5, 200, 50, key="ema_w") if show_ema else 50
with oc5: show_bb  = st.checkbox("Bollinger Bands")
with oc6: show_st  = st.checkbox("SuperTrend")
with oc7: show_rsi = st.checkbox("RSI")
with oc8: show_macd = st.checkbox("MACD")

load_btn = st.button("Load Chart")
st.markdown('</div>', unsafe_allow_html=True)

# ── Load data ─────────────────────────────────────────────────────────────────
if load_btn:
    with st.spinner(f"Loading {ticker}..."):
        df_full = get_stock_data(ticker, str(start_date), str(end_date))
    if df_full.empty: st.stop()
    st.session_state.replay_df          = df_full
    st.session_state.replay_trades      = []
    st.session_state.replay_cash        = float(capital)
    st.session_state.replay_shares      = 0.0
    st.session_state.replay_sl          = None
    st.session_state.replay_tp          = None
    st.session_state.replay_entry_price = None
    st.session_state.replay_pnl_history = []
    st.rerun()

df_full = st.session_state.replay_df
if df_full is None or df_full.empty:
    st.markdown('<div class="info-box">Enter a ticker and click Load Chart to begin your simulation.</div>', unsafe_allow_html=True)
    st.stop()

# ── Serialize helpers ─────────────────────────────────────────────────────────
def to_unix(ts):
    if hasattr(ts, "timestamp"): return int(ts.timestamp())
    return int(pd.Timestamp(ts).timestamp())

candles = [
    {"t": to_unix(r.Index), "o": round(float(r.Open),4), "h": round(float(r.High),4),
     "l": round(float(r.Low),4), "c": round(float(r.Close),4), "v": int(r.Volume)}
    for r in df_full.itertuples()
]

def s2ov(ser, df):
    return [{"time": to_unix(ts), "value": round(float(v),4)}
            for ts, v in zip(df.index, ser) if pd.notna(v)]

overlays = {}
sub_indicators = {}

if show_sma:
    overlays[f"SMA {sma_win}"] = s2ov(sma(df_full["Close"], sma_win), df_full)
if show_ema:
    overlays[f"EMA {ema_win}"] = s2ov(ema(df_full["Close"], ema_win), df_full)
if show_bb:
    bb = bollinger_bands(df_full["Close"])
    overlays["BB Upper"]  = s2ov(bb["upper"],  df_full)
    overlays["BB Middle"] = s2ov(bb["middle"], df_full)
    overlays["BB Lower"]  = s2ov(bb["lower"],  df_full)
if show_st:
    std = supertrend(df_full)
    overlays["ST Bull"] = s2ov(std["supertrend"].where(std["direction"]==1),  df_full)
    overlays["ST Bear"] = s2ov(std["supertrend"].where(std["direction"]==-1), df_full)
if show_rsi:
    sub_indicators["RSI"] = s2ov(rsi(df_full["Close"]), df_full)
if show_macd:
    md = macd(df_full["Close"])
    sub_indicators["MACD"]   = s2ov(md["macd"],      df_full)
    sub_indicators["Signal"] = s2ov(md["signal"],    df_full)
    sub_indicators["Hist"]   = s2ov(md["histogram"], df_full)

trade_markers = [
    {"time": to_unix(t["date"]), "action": t["action"],
     "shares": t["shares"], "price": t["price"]}
    for t in st.session_state.replay_trades
]

sl_price = st.session_state.replay_sl or 0
tp_price = st.session_state.replay_tp or 0

# ── Lightweight-charts component ──────────────────────────────────────────────
CHART_HTML = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
*{margin:0;padding:0;box-sizing:border-box;}
body{background:#07090d;font-family:'IBM Plex Mono',monospace;color:#cdd5e0;overflow:hidden;}
#wrap{display:flex;flex-direction:column;height:100vh;}
#chart-main{flex:1;min-height:0;position:relative;}
#chart-sub{height:__SUB_H__px;border-top:1px solid #1c2333;position:relative;}
#toolbar{
  display:flex;align-items:center;gap:8px;padding:7px 12px;
  background:#0d1117;border-bottom:1px solid #1c2333;flex-wrap:wrap;flex-shrink:0;
}
#statusbar{
  display:flex;align-items:center;gap:16px;padding:5px 12px;
  background:#0d1117;border-top:1px solid #1c2333;flex-shrink:0;flex-wrap:wrap;
}
.btn{
  background:transparent;color:#00d68f;border:1px solid #00d68f;
  padding:4px 11px;border-radius:3px;font-family:'IBM Plex Mono',monospace;
  font-size:0.65rem;letter-spacing:0.08em;cursor:pointer;text-transform:uppercase;
  transition:all 0.15s;white-space:nowrap;
}
.btn:hover,.btn.on{background:#00d68f;color:#000;}
.btn.red{color:#ff4757;border-color:#ff4757;}
.btn.red:hover{background:#ff4757;color:#000;}
.btn.grey{color:#3a4558;border-color:#3a4558;}
.sep{width:1px;height:20px;background:#1c2333;flex-shrink:0;}
.stat{font-size:0.62rem;color:#3a4558;white-space:nowrap;}
.stat span{color:#cdd5e0;}
.stat.pos span{color:#00d68f;}
.stat.neg span{color:#ff4757;}
#ohlcbar{font-size:0.62rem;margin-left:auto;display:flex;gap:10px;}
.oh{color:#cdd5e0;}.hh{color:#00d68f;}.lh{color:#ff4757;}.ch{color:#00d68f;}
#prog{height:2px;background:#1c2333;flex-shrink:0;}
#prog-fill{height:100%;background:#00d68f;transition:width 0.08s;}
#draw-hint{
  position:absolute;top:8px;left:50%;transform:translateX(-50%);
  background:#0d1117cc;border:1px solid #1c2333;border-radius:4px;
  padding:4px 12px;font-size:0.62rem;color:#00d68f;pointer-events:none;
  display:none;z-index:10;
}
#sub-label{
  position:absolute;top:4px;left:8px;font-size:0.58rem;color:#3a4558;
  text-transform:uppercase;letter-spacing:0.1em;z-index:5;
}
</style>
</head>
<body>
<div id="wrap">
  <div id="toolbar">
    <button class="btn" onclick="goStart()">⏮</button>
    <button class="btn" onclick="stepBack()">◀ -1</button>
    <button class="btn btn-play" id="play-btn" onclick="togglePlay()">▶ Play</button>
    <button class="btn" onclick="stepFwd()">+1 ▶</button>
    <button class="btn" onclick="goEnd()">⏭</button>
    <div class="sep"></div>
    <span class="stat">Speed</span>
    <input type="range" id="speed" min="50" max="800" value="300" step="50"
      style="width:70px;accent-color:#00d68f;" oninput="setSpeed()">
    <span id="speed-lbl" class="stat"><span>300ms</span></span>
    <div class="sep"></div>
    <button class="btn grey" id="btn-hline" onclick="toggleDraw('hline')">— H-Line</button>
    <button class="btn grey" id="btn-tline" onclick="toggleDraw('tline')">/ Trend Line</button>
    <button class="btn grey" id="btn-rect" onclick="toggleDraw('rect')">▭ Box</button>
    <button class="btn red" onclick="clearDrawings()">✕ Clear</button>
    <div class="sep"></div>
    <span id="date-disp" class="stat"><span>—</span></span>
  </div>

  <div id="chart-main">
    <div id="draw-hint">Click to place line</div>
  </div>
  <div id="chart-sub" style="display:__SUB_DISPLAY__">
    <div id="sub-label">__SUB_LABEL__</div>
  </div>

  <div id="statusbar">
    <div class="stat">Cash <span id="s-cash">—</span></div>
    <div class="stat">Shares <span id="s-shares">—</span></div>
    <div class="stat">Price <span id="s-price">—</span></div>
    <div class="stat">Portfolio <span id="s-pv">—</span></div>
    <div id="s-pnl-wrap" class="stat">P&L <span id="s-pnl">—</span></div>
    <div class="stat" id="s-sl-wrap" style="display:none">SL <span id="s-sl" style="color:#ff4757;">—</span></div>
    <div class="stat" id="s-tp-wrap" style="display:none">TP <span id="s-tp" style="color:#00d68f;">—</span></div>
    <div id="ohlcbar">
      <span>O <span class="oh" id="oh">—</span></span>
      <span>H <span class="hh" id="hh">—</span></span>
      <span>L <span class="lh" id="lh">—</span></span>
      <span>C <span class="ch" id="ch">—</span></span>
    </div>
  </div>
  <div id="prog"><div id="prog-fill" style="width:0%"></div></div>
</div>

<script src="https://unpkg.com/lightweight-charts@4.1.1/dist/lightweight-charts.standalone.production.js"></script>
<script>
// ── Data from Python ──────────────────────────────────────────────────────────
const ALL_CANDLES  = __CANDLES__;
const OVERLAYS     = __OVERLAYS__;
const SUB_DATA     = __SUB_DATA__;
const INIT_TRADES  = __TRADES__;
const SL_PRICE     = __SL__;
const TP_PRICE     = __TP__;
const INIT_CASH    = __CASH__;
const INIT_SHARES  = __SHARES__;
const INIT_CAPITAL = __CAPITAL__;

let idx     = 0;
let playing = false;
let timer   = null;
let speed   = 300;
let cash    = INIT_CASH;
let shares  = INIT_SHARES;
let trades  = [...INIT_TRADES];
let drawMode = null;
let drawings = [];   // {type, price, price2, time, time2, series/objs}
let drawStep = 0;    // 0=waiting first click, 1=waiting second click
let drawTemp = null; // first click data

// ── Chart setup ───────────────────────────────────────────────────────────────
const mainEl = document.getElementById('chart-main');
const subEl  = document.getElementById('chart-sub');

const mainChart = LightweightCharts.createChart(mainEl, {
  width:  mainEl.clientWidth,
  height: mainEl.clientHeight,
  layout: {background:{type:'solid',color:'#07090d'}, textColor:'#cdd5e0'},
  grid:   {vertLines:{color:'#1c2333'}, horzLines:{color:'#1c2333'}},
  crosshair: {mode: LightweightCharts.CrosshairMode.Normal},
  rightPriceScale: {borderColor:'#1c2333'},
  timeScale: {borderColor:'#1c2333', timeVisible:true, rightOffset:5},
  handleScroll:true, handleScale:true,
});

const candleSeries = mainChart.addCandlestickSeries({
  upColor:'#00d68f', downColor:'#ff4757',
  borderUpColor:'#00d68f', borderDownColor:'#ff4757',
  wickUpColor:'#00d68f', wickDownColor:'#ff4757',
});
const volSeries = mainChart.addHistogramSeries({
  color:'#1c2333', priceFormat:{type:'volume'},
  priceScaleId:'vol', scaleMargins:{top:0.8, bottom:0},
});

// Overlay series
const OV_COLORS = {'BB Upper':'#4da6ff','BB Middle':'#4da6ff88','BB Lower':'#4da6ff',
  'ST Bull':'#00d68f','ST Bear':'#ff4757'};
const ovSeries = {};
const OV_NAMES = Object.keys(OVERLAYS);
for (const name of OV_NAMES) {
  const col = OV_COLORS[name] || (name.startsWith('SMA') ? '#ffd166' : '#b388ff');
  ovSeries[name] = mainChart.addLineSeries({
    color: col, lineWidth: name.includes('Middle') ? 1 : 1,
    lineStyle: name.includes('Middle') ? 2 : 0,
    title: name, priceLineVisible: false, lastValueVisible: false,
  });
}

// Sub-chart
let subChart = null, subSeries = {}, subSeries2 = null;
const hasSub = subEl.style.display !== 'none';
if (hasSub) {
  subChart = LightweightCharts.createChart(subEl, {
    width: subEl.clientWidth, height: subEl.clientHeight,
    layout:{background:{type:'solid',color:'#07090d'},textColor:'#cdd5e0'},
    grid:{vertLines:{color:'#1c2333'},horzLines:{color:'#1c2333'}},
    rightPriceScale:{borderColor:'#1c2333'},
    timeScale:{borderColor:'#1c2333',timeVisible:true,visible:false},
    crosshair:{mode:LightweightCharts.CrosshairMode.Normal},
    handleScroll:false, handleScale:false,
  });
  // Sync timescale
  mainChart.timeScale().subscribeVisibleTimeRangeChange(range => {
    if (range && subChart) subChart.timeScale().setVisibleRange(range);
  });

  const subKeys = Object.keys(SUB_DATA);
  if (subKeys.includes('RSI')) {
    subSeries['RSI'] = subChart.addLineSeries({color:'#b388ff',lineWidth:1,priceLineVisible:false,lastValueVisible:true,title:'RSI'});
    // OB/OS lines
    subChart.addLineSeries({color:'#ff475744',lineWidth:1,lineStyle:2,priceLineVisible:false,lastValueVisible:false}).setData(
      ALL_CANDLES.map(c=>({time:c.t,value:70})));
    subChart.addLineSeries({color:'#00d68f44',lineWidth:1,lineStyle:2,priceLineVisible:false,lastValueVisible:false}).setData(
      ALL_CANDLES.map(c=>({time:c.t,value:30})));
  }
  if (subKeys.includes('MACD')) {
    subSeries['MACD']   = subChart.addLineSeries({color:'#4da6ff',lineWidth:1,priceLineVisible:false,lastValueVisible:false,title:'MACD'});
    subSeries['Signal'] = subChart.addLineSeries({color:'#ff9f43',lineWidth:1,priceLineVisible:false,lastValueVisible:false,title:'Sig'});
    subSeries2 = subChart.addHistogramSeries({
      priceScaleId:'hist', scaleMargins:{top:0.7,bottom:0},
      priceLineVisible:false, lastValueVisible:false,
    });
  }
}

// SL/TP price lines
let slLine = null, tpLine = null;
function updateSLTPLines() {
  if (SL_PRICE > 0) {
    if (!slLine) slLine = candleSeries.createPriceLine({price:SL_PRICE,color:'#ff4757',lineWidth:1,lineStyle:2,title:'SL',axisLabelVisible:true});
    document.getElementById('s-sl').textContent = '$'+SL_PRICE.toFixed(2);
    document.getElementById('s-sl-wrap').style.display='';
  }
  if (TP_PRICE > 0) {
    if (!tpLine) tpLine = candleSeries.createPriceLine({price:TP_PRICE,color:'#00d68f',lineWidth:1,lineStyle:2,title:'TP',axisLabelVisible:true});
    document.getElementById('s-tp').textContent = '$'+TP_PRICE.toFixed(2);
    document.getElementById('s-tp-wrap').style.display='';
  }
}

// ── Render ────────────────────────────────────────────────────────────────────
function render() {
  const vis = ALL_CANDLES.slice(0, idx+1);

  candleSeries.setData(vis.map(c=>({time:c.t,open:c.o,high:c.h,low:c.l,close:c.c})));
  volSeries.setData(vis.map(c=>({time:c.t,value:c.v,color:c.c>=c.o?'rgba(0,214,143,0.2)':'rgba(255,71,87,0.2)'})));

  for (const name of OV_NAMES) {
    ovSeries[name].setData(OVERLAYS[name].filter(p=>p.time<=vis[vis.length-1].t));
  }

  if (hasSub) {
    const subKeys = Object.keys(SUB_DATA);
    for (const k of subKeys) {
      if (!subSeries[k]) continue;
      subSeries[k].setData(SUB_DATA[k].filter(p=>p.time<=vis[vis.length-1].t));
    }
    if (subSeries2 && SUB_DATA['Hist']) {
      subSeries2.setData(SUB_DATA['Hist'].filter(p=>p.time<=vis[vis.length-1].t).map(p=>({
        ...p, color: p.value >= 0 ? 'rgba(0,214,143,0.6)' : 'rgba(255,71,87,0.6)'
      })));
    }
  }

  // Trade markers
  const markers = trades.map(t=>({
    time: t.time,
    position: t.action==='BUY' ? 'belowBar' : 'aboveBar',
    color: t.action==='BUY' ? '#00d68f' : '#ff4757',
    shape: t.action==='BUY' ? 'arrowUp' : 'arrowDown',
    text: t.action==='BUY' ? `B ${t.shares}@${t.price.toFixed(0)}` : `S ${t.shares}@${t.price.toFixed(0)}`,
  }));
  candleSeries.setMarkers(markers);

  const cur = vis[vis.length-1];
  const cp  = cur.c;
  const pv  = cash + shares * cp;
  const pnl = pv - INIT_CAPITAL;

  document.getElementById('s-cash').textContent   = '$'+cash.toFixed(2);
  document.getElementById('s-shares').textContent = shares.toFixed(2);
  document.getElementById('s-price').textContent  = '$'+cp.toFixed(2);
  document.getElementById('s-pv').textContent     = '$'+pv.toFixed(2);
  const pnlEl = document.getElementById('s-pnl');
  pnlEl.textContent = (pnl>=0?'+':'')+pnl.toFixed(2);
  pnlEl.style.color = pnl>=0 ? '#00d68f' : '#ff4757';

  const d = new Date(cur.t*1000);
  document.getElementById('date-disp').innerHTML = '<span>'+d.toISOString().slice(0,10)+'</span>';
  document.getElementById('prog-fill').style.width = ((idx+1)/ALL_CANDLES.length*100).toFixed(1)+'%';

  // Auto SL/TP check
  if (shares > 0) {
    if (SL_PRICE > 0 && cp <= SL_PRICE) {
      executeSell(shares, cp, 'SL hit');
    } else if (TP_PRICE > 0 && cp >= TP_PRICE) {
      executeSell(shares, cp, 'TP hit');
    }
  }

  // Scroll chart to keep latest bar visible
  mainChart.timeScale().scrollToPosition(5, false);
  if (subChart) subChart.timeScale().scrollToPosition(5, false);
}

// ── Crosshair OHLC ────────────────────────────────────────────────────────────
mainChart.subscribeCrosshairMove(p => {
  if (!p?.seriesData) return;
  const d = p.seriesData.get(candleSeries);
  if (!d) return;
  document.getElementById('oh').textContent = d.open?.toFixed(2)??'';
  document.getElementById('hh').textContent = d.high?.toFixed(2)??'';
  document.getElementById('lh').textContent = d.low?.toFixed(2)??'';
  document.getElementById('ch').textContent = d.close?.toFixed(2)??'';
});

// ── Playback ──────────────────────────────────────────────────────────────────
function goStart()  { stop(); idx=0; render(); }
function goEnd()    { stop(); idx=ALL_CANDLES.length-1; render(); }
function stepBack() { stop(); if(idx>0){idx--;render();} }
function stepFwd()  { if(idx<ALL_CANDLES.length-1){idx++;render();}else stop(); }

function togglePlay(){ playing?stop():startPlay(); }
function startPlay(){
  playing=true;
  document.getElementById('play-btn').textContent='⏸ Pause';
  document.getElementById('play-btn').classList.add('on');
  timer=setInterval(()=>{
    if(idx>=ALL_CANDLES.length-1){stop();return;}
    stepFwd();
  },speed);
}
function stop(){
  playing=false;
  document.getElementById('play-btn').textContent='▶ Play';
  document.getElementById('play-btn').classList.remove('on');
  clearInterval(timer);
}
function setSpeed(){
  speed=parseInt(document.getElementById('speed').value);
  document.getElementById('speed-lbl').innerHTML='<span>'+speed+'ms</span>';
  if(playing){stop();startPlay();}
}

// ── Drawing tools ─────────────────────────────────────────────────────────────
function toggleDraw(mode){
  const btns = {hline:'btn-hline', tline:'btn-tline', rect:'btn-rect'};
  if(drawMode===mode){ drawMode=null; drawStep=0; drawTemp=null;
    document.getElementById('draw-hint').style.display='none';
    for(const id of Object.values(btns)) document.getElementById(id).classList.remove('on');
    mainEl.style.cursor='default';
    return;
  }
  drawMode=mode; drawStep=0; drawTemp=null;
  for(const id of Object.values(btns)) document.getElementById(id).classList.remove('on');
  document.getElementById(btns[mode]).classList.add('on');
  document.getElementById('draw-hint').style.display='block';
  document.getElementById('draw-hint').textContent =
    mode==='hline' ? 'Click price level to draw horizontal line' :
    mode==='tline' ? 'Click first point of trend line' :
    'Click first corner of box';
  mainEl.style.cursor='crosshair';
}

mainChart.subscribeClick(param => {
  if(!drawMode || !param.point) return;
  const price = mainChart.priceScale('right').coordinateToPrice(param.point.y);
  const time  = mainChart.timeScale().coordinateToTime(param.point.x);
  if(!price || !time) return;

  if(drawMode==='hline'){
    // Horizontal line — 1 click
    const s = mainChart.addLineSeries({
      color:'#ffd16688', lineWidth:1, lineStyle:1,
      priceLineVisible:false, lastValueVisible:false,
    });
    s.setData(ALL_CANDLES.map(c=>({time:c.t,value:price})));
    drawings.push({type:'hline',series:s});
    document.getElementById('draw-hint').textContent='Click to place another line';

  } else if(drawMode==='tline'){
    if(drawStep===0){
      drawTemp={price,time}; drawStep=1;
      document.getElementById('draw-hint').textContent='Click second point of trend line';
    } else {
      const p1=drawTemp; const p2={price,time};
      const s = mainChart.addLineSeries({
        color:'#ffd166', lineWidth:1,
        priceLineVisible:false, lastValueVisible:false,
      });
      // Build line between two time points
      const t1=typeof p1.time==='number'?p1.time:p1.time;
      const t2=typeof p2.time==='number'?p2.time:p2.time;
      const slope=(p2.price-p1.price)/(t2-t1);
      const pts=ALL_CANDLES.filter(c=>c.t>=Math.min(t1,t2)&&c.t<=Math.max(t1,t2))
        .map(c=>({time:c.t, value:p1.price+slope*(c.t-t1)}));
      if(pts.length>1) s.setData(pts);
      drawings.push({type:'tline',series:s});
      drawStep=0; drawTemp=null;
      document.getElementById('draw-hint').textContent='Click first point of trend line';
    }

  } else if(drawMode==='rect'){
    if(drawStep===0){
      drawTemp={price,time}; drawStep=1;
      document.getElementById('draw-hint').textContent='Click second corner of box';
    } else {
      const p1=drawTemp; const p2={price,time};
      // Draw box as 4 lines
      const t1=typeof p1.time==='number'?p1.time:p1.time;
      const t2=typeof p2.time==='number'?p2.time:p2.time;
      const topPrice=Math.max(p1.price,p2.price);
      const botPrice=Math.min(p1.price,p2.price);
      const leftT=Math.min(t1,t2); const rightT=Math.max(t1,t2);
      const boxColor='rgba(77,166,255,0.15)';
      const borderColor='#4da6ff88';
      const makeH=(price,tFrom,tTo)=>{
        const s=mainChart.addLineSeries({color:borderColor,lineWidth:1,priceLineVisible:false,lastValueVisible:false});
        s.setData(ALL_CANDLES.filter(c=>c.t>=tFrom&&c.t<=tTo).map(c=>({time:c.t,value:price})));
        return s;
      };
      const top=makeH(topPrice,leftT,rightT);
      const bot=makeH(botPrice,leftT,rightT);
      drawings.push({type:'rect',series:[top,bot]});
      drawStep=0; drawTemp=null;
      document.getElementById('draw-hint').textContent='Click first corner of box';
    }
  }
});

function clearDrawings(){
  for(const d of drawings){
    if(Array.isArray(d.series)) for(const s of d.series) mainChart.removeSeries(s);
    else mainChart.removeSeries(d.series);
  }
  drawings=[];
}

// ── Execute trade helpers (called from parent Streamlit via postMessage) ───────
function executeBuy(qty) {
  const cur = ALL_CANDLES[idx];
  const cost = qty * cur.c;
  if(cost > cash){ alert('Not enough cash'); return; }
  cash -= cost; shares += qty;
  trades.push({time:cur.t, action:'BUY', shares:qty, price:cur.c});
  render();
  window.parent.postMessage({type:'trade',action:'BUY',qty,price:cur.c,cash,shares},'*');
}
function executeSell(qty, price, reason) {
  const cur = ALL_CANDLES[idx];
  const p = price || cur.c;
  if(qty > shares){ alert('Not enough shares'); return; }
  cash += qty * p; shares -= qty;
  trades.push({time:cur.t, action:'SELL', shares:qty, price:p});
  render();
  window.parent.postMessage({type:'trade',action:'SELL',qty,price:p,cash,shares,reason},'*');
}

// ── Keyboard ──────────────────────────────────────────────────────────────────
document.addEventListener('keydown', e => {
  if(e.key==='ArrowRight') stepFwd();
  if(e.key==='ArrowLeft')  stepBack();
  if(e.key===' '){e.preventDefault();togglePlay();}
});

// ── Resize ────────────────────────────────────────────────────────────────────
function doResize(){
  mainChart.applyOptions({width:mainEl.clientWidth,height:mainEl.clientHeight});
  if(subChart) subChart.applyOptions({width:subEl.clientWidth,height:subEl.clientHeight});
}
window.addEventListener('resize', doResize);
new ResizeObserver(doResize).observe(mainEl);

// ── Init ──────────────────────────────────────────────────────────────────────
updateSLTPLines();
render();
</script>
</body>
</html>"""

# Determine sub-chart
has_sub = show_rsi or show_macd
sub_h      = 140 if has_sub else 0
sub_display = "block" if has_sub else "none"
sub_label   = "RSI" if show_rsi else "MACD" if show_macd else ""

CHART_HTML = CHART_HTML.replace("__SUB_H__",      str(sub_h))
CHART_HTML = CHART_HTML.replace("__SUB_DISPLAY__", sub_display)
CHART_HTML = CHART_HTML.replace("__SUB_LABEL__",  sub_label)
CHART_HTML = CHART_HTML.replace("__CANDLES__",    json.dumps(candles))
CHART_HTML = CHART_HTML.replace("__OVERLAYS__",   json.dumps(overlays))
CHART_HTML = CHART_HTML.replace("__SUB_DATA__",   json.dumps(sub_indicators))
CHART_HTML = CHART_HTML.replace("__TRADES__",     json.dumps(trade_markers))
CHART_HTML = CHART_HTML.replace("__SL__",         str(sl_price))
CHART_HTML = CHART_HTML.replace("__TP__",         str(tp_price))
CHART_HTML = CHART_HTML.replace("__CASH__",       str(st.session_state.replay_cash))
CHART_HTML = CHART_HTML.replace("__SHARES__",     str(st.session_state.replay_shares))
CHART_HTML = CHART_HTML.replace("__CAPITAL__",    str(float(capital)))

total_h = 540 + sub_h
components.html(CHART_HTML, height=total_h, scrolling=False)

# ── Trading panel ─────────────────────────────────────────────────────────────
st.markdown('<div class="price-divider">TRADING PANEL</div>', unsafe_allow_html=True)

last_price = float(df_full["Close"].iloc[-1])
cash   = st.session_state.replay_cash
shares = st.session_state.replay_shares

tc1, tc2, tc3, tc4 = st.columns(4)

with tc1:
    st.markdown('<div class="config-panel">', unsafe_allow_html=True)
    st.markdown('<div style="font-family:IBM Plex Mono,monospace;font-size:0.6rem;color:#00d68f;text-transform:uppercase;letter-spacing:0.15em;margin-bottom:0.8rem;">Buy Order</div>', unsafe_allow_html=True)
    bq = st.number_input("Shares", min_value=0.0, value=1.0, step=1.0, key="bq")
    est_cost = bq * last_price
    st.markdown(f'<div style="font-family:IBM Plex Mono,monospace;font-size:0.68rem;color:#3a4558;margin-bottom:0.6rem;">Est. cost: ${est_cost:,.2f}</div>', unsafe_allow_html=True)
    if st.button("Buy at Market", use_container_width=True, key="buy_btn"):
        cost = bq * last_price
        if cost <= cash:
            st.session_state.replay_cash   -= cost
            st.session_state.replay_shares += bq
            st.session_state.replay_entry_price = last_price
            st.session_state.replay_trades.append({"date": df_full.index[-1], "action": "BUY", "price": last_price, "shares": bq})
            st.success(f"Bought {bq:.0f} @ ${last_price:.2f}"); st.rerun()
        else:
            st.error(f"Need ${cost:,.2f}, have ${cash:,.2f}")
    st.markdown('</div>', unsafe_allow_html=True)

with tc2:
    st.markdown('<div class="config-panel">', unsafe_allow_html=True)
    st.markdown('<div style="font-family:IBM Plex Mono,monospace;font-size:0.6rem;color:#ff4757;text-transform:uppercase;letter-spacing:0.15em;margin-bottom:0.8rem;">Sell Order</div>', unsafe_allow_html=True)
    sq = st.number_input("Shares", min_value=0.0, max_value=float(shares) if shares > 0 else 0.0, value=min(1.0, float(shares)), step=1.0, key="sq")
    est_proceeds = sq * last_price
    st.markdown(f'<div style="font-family:IBM Plex Mono,monospace;font-size:0.68rem;color:#3a4558;margin-bottom:0.6rem;">Est. proceeds: ${est_proceeds:,.2f}</div>', unsafe_allow_html=True)
    if st.button("Sell at Market", use_container_width=True, key="sell_btn"):
        if sq <= shares and sq > 0:
            st.session_state.replay_cash   += sq * last_price
            st.session_state.replay_shares -= sq
            st.session_state.replay_trades.append({"date": df_full.index[-1], "action": "SELL", "price": last_price, "shares": sq})
            st.success(f"Sold {sq:.0f} @ ${last_price:.2f}"); st.rerun()
        else:
            st.error("Not enough shares.")
    st.markdown('</div>', unsafe_allow_html=True)

with tc3:
    st.markdown('<div class="config-panel">', unsafe_allow_html=True)
    st.markdown('<div style="font-family:IBM Plex Mono,monospace;font-size:0.6rem;color:#3a4558;text-transform:uppercase;letter-spacing:0.15em;margin-bottom:0.8rem;">Stop Loss / Take Profit</div>', unsafe_allow_html=True)
    new_sl = st.number_input("Stop Loss ($)", min_value=0.0, value=float(st.session_state.replay_sl or 0), step=0.5, format="%.2f", key="sl_input")
    new_tp = st.number_input("Take Profit ($)", min_value=0.0, value=float(st.session_state.replay_tp or 0), step=0.5, format="%.2f", key="tp_input")
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        if st.button("Set SL/TP", use_container_width=True):
            st.session_state.replay_sl = new_sl if new_sl > 0 else None
            st.session_state.replay_tp = new_tp if new_tp > 0 else None
            st.rerun()
    with col_s2:
        if st.button("Clear", use_container_width=True):
            st.session_state.replay_sl = None
            st.session_state.replay_tp = None
            st.rerun()
    if st.session_state.replay_sl:
        st.markdown(f'<div style="font-size:0.7rem;color:#ff4757;margin-top:0.3rem;">SL active: ${st.session_state.replay_sl:.2f}</div>', unsafe_allow_html=True)
    if st.session_state.replay_tp:
        st.markdown(f'<div style="font-size:0.7rem;color:#00d68f;margin-top:0.1rem;">TP active: ${st.session_state.replay_tp:.2f}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with tc4:
    pv  = cash + shares * last_price
    pnl = pv - float(capital)
    pnl_pct = pnl / float(capital) * 100
    ep  = st.session_state.replay_entry_price
    unrealised = (last_price - ep) * shares if ep and shares > 0 else 0.0

    st.markdown(f'''
    <div class="config-panel">
      <div style="font-family:IBM Plex Mono,monospace;font-size:0.6rem;color:#3a4558;text-transform:uppercase;letter-spacing:0.15em;margin-bottom:0.8rem;">Position Summary</div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;">
        <div class="metric-card"><div class="metric-val neu">${cash:,.0f}</div><div class="metric-lbl">Cash</div></div>
        <div class="metric-card"><div class="metric-val neu">{shares:.1f}</div><div class="metric-lbl">Shares</div></div>
        <div class="metric-card"><div class="metric-val {'pos' if pnl>=0 else 'neg'}">{pnl:+,.0f}</div><div class="metric-lbl">Total P&L</div></div>
        <div class="metric-card"><div class="metric-val {'pos' if unrealised>=0 else 'neg'}">{unrealised:+,.0f}</div><div class="metric-lbl">Unrealised</div></div>
      </div>
    </div>
    ''', unsafe_allow_html=True)

    if st.button("Reset All", use_container_width=True):
        st.session_state.replay_trades      = []
        st.session_state.replay_cash        = float(capital)
        st.session_state.replay_shares      = 0.0
        st.session_state.replay_sl          = None
        st.session_state.replay_tp          = None
        st.session_state.replay_entry_price = None
        st.rerun()

# ── Trade log ──────────────────────────────────────────────────────────────────
if st.session_state.replay_trades:
    st.markdown('<div class="price-divider">TRADE LOG</div>', unsafe_allow_html=True)
    df_log = pd.DataFrame(st.session_state.replay_trades)
    df_log["value"] = df_log["price"] * df_log["shares"]
    with st.expander(f"{len(df_log)} trades logged"):
        st.dataframe(df_log, use_container_width=True)
