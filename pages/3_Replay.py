import streamlit as st
import pandas as pd
import numpy as np
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
    <p>Bar-by-bar replay with a live ticking price. Buy and sell without knowing the future. Draw on the chart. Zero page refreshes.</p>
</div>
""", unsafe_allow_html=True)

for k, v in [("rp_df", None), ("rp_ticker", ""), ("rp_capital", 10000)]:
    if k not in st.session_state:
        st.session_state[k] = v

with st.expander("Setup", expanded=st.session_state.rp_df is None):
    s1,s2,s3,s4,s5 = st.columns([2,1.5,1.5,1.5,1])
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
                st.error("No data.")
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
        <div style="color:#3a4a5e;font-size:0.85rem;margin-top:1rem;">Load any ticker above to begin.</div>
    </div>""", unsafe_allow_html=True)
    st.stop()

df_full.index = pd.to_datetime(df_full.index)
candles = []
for ts, row in df_full.iterrows():
    candles.append({
        "t": ts.strftime("%Y-%m-%d"),
        "o": round(float(row["Open"]),  4),
        "h": round(float(row["High"]),  4),
        "l": round(float(row["Low"]),   4),
        "c": round(float(row["Close"]), 4),
        "v": int(row["Volume"]),
    })

config_json = json.dumps({
    "candles":  candles,
    "ticker":   st.session_state.rp_ticker,
    "capital":  st.session_state.rp_capital,
    "startIdx": min(80, len(candles)-1),
})

HTML = r"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
*{box-sizing:border-box;margin:0;padding:0;}
body{background:#06080c;color:#8896ab;font-family:'IBM Plex Mono',monospace;font-size:13px;overflow:hidden;user-select:none;}
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Bebas+Neue&display=swap');
#root{display:flex;flex-direction:column;height:100vh;padding:6px 8px;gap:5px;}
#tape-wrap{overflow:hidden;height:24px;background:#0b0f17;border:1px solid #1a2438;border-radius:4px;}
#tape{display:inline-flex;gap:0;white-space:nowrap;animation:scroll 22s linear infinite;padding:4px 0;}
@keyframes scroll{from{transform:translateX(100%)}to{transform:translateX(-100%)}}
.tape-item{padding:0 18px;border-right:1px solid #1a2438;font-size:11px;}
.tape-sym{color:#3a4a5e;margin-right:5px;}.tape-val{color:#eef2f7;}
.tape-chg.up{color:#00e676;}.tape-chg.down{color:#ff3d57;}
#body{display:flex;gap:6px;flex:1;min-height:0;}
#sidebar{width:130px;min-width:130px;display:flex;flex-direction:column;gap:5px;overflow-y:auto;}
.panel{background:#0b0f17;border:1px solid #1a2438;border-radius:6px;padding:8px 10px;}
.panel-hdr{font-size:9px;color:#3a4a5e;text-transform:uppercase;letter-spacing:0.18em;margin-bottom:6px;padding-bottom:5px;border-bottom:1px solid #1a2438;}
.chk-row{display:flex;align-items:center;gap:6px;margin-bottom:4px;cursor:pointer;font-size:11px;color:#8896ab;}
.chk-row input{accent-color:#00e676;cursor:pointer;}.chk-row:hover{color:#eef2f7;}
#speed-range{width:100%;accent-color:#00e676;}
#play-btn{width:100%;padding:6px;border:none;border-radius:4px;background:linear-gradient(135deg,#007a2c,#00e676);color:#000;font-family:'IBM Plex Mono',monospace;font-size:11px;font-weight:700;letter-spacing:0.15em;cursor:pointer;margin-top:5px;transition:opacity 0.15s;}
#play-btn:hover{opacity:0.85;}#play-btn.playing{background:linear-gradient(135deg,#6a0010,#ff3d57);color:#fff;}
.step-row{display:flex;gap:4px;margin-top:4px;}
.step-btn{flex:1;padding:4px 2px;border:1px solid #1a2438;background:#0b0f17;color:#8896ab;border-radius:3px;font-family:'IBM Plex Mono',monospace;font-size:10px;cursor:pointer;transition:border-color 0.1s,color 0.1s;}
.step-btn:hover{border-color:#00e676;color:#eef2f7;}
.draw-btn{width:100%;padding:5px;border:1px solid #1a2438;background:#0b0f17;color:#8896ab;border-radius:3px;font-family:'IBM Plex Mono',monospace;font-size:10px;cursor:pointer;margin-bottom:3px;text-align:left;transition:border-color 0.1s,color 0.1s;}
.draw-btn:hover,.draw-btn.active{border-color:#ffd166;color:#ffd166;}
#clear-draw{color:#ff3d57;}#clear-draw:hover{border-color:#ff3d57;}
#chart-area{flex:1;display:flex;flex-direction:column;gap:5px;min-width:0;}
#canvas-wrap{flex:1;position:relative;background:#0b0f17;border:1px solid #1a2438;border-radius:6px;overflow:hidden;min-height:0;}
#main-canvas{display:block;}
#crosshair-canvas{position:absolute;top:0;left:0;}
#price-badge{position:absolute;right:65px;top:10px;background:#0b0f17;border:1px solid #1a2438;border-radius:4px;padding:3px 8px;font-size:11px;color:#eef2f7;pointer-events:none;}
#live-dot{display:inline-block;width:6px;height:6px;background:#00e676;border-radius:50%;margin-right:5px;vertical-align:middle;animation:blink 1s ease-in-out infinite;}
@keyframes blink{0%,100%{opacity:1}50%{opacity:0.1}}
#metric-strip{display:flex;background:#0b0f17;border:1px solid #1a2438;border-radius:6px;overflow:hidden;}
.mc{flex:1;padding:5px 8px;border-right:1px solid #1a2438;min-width:0;}.mc:last-child{border-right:none;}
.mc-val{font-size:12px;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.mc-lbl{font-size:8px;color:#3a4a5e;text-transform:uppercase;letter-spacing:0.14em;margin-top:1px;}
.g{color:#00e676;}.r{color:#ff3d57;}.b{color:#4da6ff;}.w{color:#eef2f7;}
#progress-wrap{height:3px;background:#1a2438;border-radius:2px;}
#progress-fill{height:100%;background:linear-gradient(90deg,#00e676,#4da6ff);border-radius:2px;transition:width 0.2s;}
#trade-panel{display:flex;gap:6px;}
.trade-box{flex:1;background:#0b0f17;border:1px solid #1a2438;border-radius:6px;padding:10px;}
.trade-hdr{font-size:9px;text-transform:uppercase;letter-spacing:0.18em;margin-bottom:8px;padding:4px 8px;border-radius:3px;}
.buy-hdr{color:#00e676;background:rgba(0,230,118,0.06);border:1px solid rgba(0,230,118,0.12);}
.sell-hdr{color:#ff3d57;background:rgba(255,61,87,0.06);border:1px solid rgba(255,61,87,0.12);}
.pos-hdr{color:#4da6ff;background:rgba(77,166,255,0.06);border:1px solid rgba(77,166,255,0.12);}
.order-row{display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;font-size:11px;color:#3a4a5e;}
.order-row span:last-child{color:#eef2f7;}
.qty-row{display:flex;align-items:center;gap:6px;margin-bottom:6px;}
.qty-label{font-size:10px;color:#3a4a5e;white-space:nowrap;}
.qty-input{flex:1;background:#0e1420;border:1px solid #1a2438;color:#eef2f7;font-family:'IBM Plex Mono',monospace;font-size:12px;padding:4px 7px;border-radius:3px;width:0;outline:none;}
.qty-input:focus{border-color:#4da6ff;}
.qty-btn{padding:4px 8px;border:1px solid #1a2438;border-radius:3px;background:#0e1420;color:#8896ab;cursor:pointer;font-family:'IBM Plex Mono',monospace;font-size:11px;}
.qty-btn:hover{color:#eef2f7;border-color:#8896ab;}
.exec-btn{width:100%;padding:7px;border:none;border-radius:4px;font-family:'IBM Plex Mono',monospace;font-size:12px;font-weight:700;letter-spacing:0.1em;cursor:pointer;transition:opacity 0.12s;}
.exec-btn:hover{opacity:0.85;}
#buy-btn{background:linear-gradient(135deg,#005c1e,#00e676);color:#000;}
#sell-btn{background:linear-gradient(135deg,#7a0015,#ff3d57);color:#fff;}
#reset-btn{width:100%;padding:5px;border:1px solid #1a2438;background:#0b0f17;color:#3a4a5e;border-radius:3px;cursor:pointer;font-family:'IBM Plex Mono',monospace;font-size:10px;margin-top:6px;}
#reset-btn:hover{border-color:#ff3d57;color:#ff3d57;}
.pos-grid{display:grid;grid-template-columns:1fr 1fr;gap:5px;}
.pos-cell{background:#0e1420;border-radius:3px;padding:5px 7px;}
.pos-val{font-size:11px;font-weight:600;}.pos-lbl{font-size:8px;color:#3a4a5e;text-transform:uppercase;letter-spacing:0.12em;margin-top:1px;}
#toast-area{position:fixed;bottom:20px;right:20px;z-index:999;display:flex;flex-direction:column;gap:6px;}
.toast{background:#0e1420;border:1px solid #1a2438;border-radius:6px;padding:8px 14px;font-size:11px;color:#eef2f7;animation:toastIn 0.2s ease both;max-width:300px;}
.toast.buy{border-left:3px solid #00e676;}.toast.sell{border-left:3px solid #ff3d57;}
@keyframes toastIn{from{opacity:0;transform:translateX(20px)}to{opacity:1;transform:translateX(0)}}
/* ── DRAW CURSOR STYLES ── */
body.drawing #crosshair-canvas { cursor: crosshair !important; }
body.panning  #crosshair-canvas { cursor: grab !important; }
body.panning.dragging #crosshair-canvas { cursor: grabbing !important; }
</style>
</head>
<body>
<div id="root">
  <div id="tape-wrap"><div id="tape"></div></div>
  <div id="body">
    <div id="sidebar">
      <div class="panel">
        <div class="panel-hdr">Overlays</div>
        <label class="chk-row"><input type="checkbox" id="ov-sma20"> SMA 20</label>
        <label class="chk-row"><input type="checkbox" id="ov-sma50"> SMA 50</label>
        <label class="chk-row"><input type="checkbox" id="ov-ema20"> EMA 20</label>
        <label class="chk-row"><input type="checkbox" id="ov-ema50"> EMA 50</label>
        <label class="chk-row"><input type="checkbox" id="ov-vwap">  VWAP</label>
        <label class="chk-row"><input type="checkbox" id="ov-bb">    BB</label>
        <label class="chk-row"><input type="checkbox" id="ov-st">    SuperTrend</label>
      </div>
      <div class="panel">
        <div class="panel-hdr">Sub-charts</div>
        <label class="chk-row"><input type="checkbox" id="sc-vol" checked> Volume</label>
        <label class="chk-row"><input type="checkbox" id="sc-rsi">  RSI</label>
        <label class="chk-row"><input type="checkbox" id="sc-macd"> MACD</label>
      </div>
      <div class="panel">
        <div class="panel-hdr">Playback</div>
        <div style="display:flex;justify-content:space-between;font-size:10px;color:#3a4a5e;margin-bottom:3px;">
          <span>Slow</span><span id="speed-lbl" style="color:#ffd166">0.7s</span><span>Fast</span>
        </div>
        <input type="range" id="speed-range" min="1" max="10" value="5">
        <button id="play-btn">PLAY</button>
        <div class="step-row" style="margin-top:6px;">
          <button class="step-btn" id="btn-back1">-1</button>
          <button class="step-btn" id="btn-back5">-5</button>
          <button class="step-btn" id="btn-fwd1">+1</button>
          <button class="step-btn" id="btn-fwd5">+5</button>
        </div>
      </div>
      <div class="panel">
        <div class="panel-hdr">Draw</div>
        <button class="draw-btn active" id="tool-none">✦ Pan</button>
        <button class="draw-btn" id="tool-line">― Trendline</button>
        <button class="draw-btn" id="tool-hline">― H-Line</button>
        <button class="draw-btn" id="tool-rect">▭ Box</button>
        <button class="draw-btn" id="clear-draw">✕ Clear all</button>
      </div>
    </div>
    <div id="chart-area">
      <div id="canvas-wrap">
        <canvas id="main-canvas"></canvas>
        <canvas id="crosshair-canvas"></canvas>
        <div id="price-badge"><span id="live-dot"></span><span id="live-price-text">$0.00</span></div>
      </div>
      <div id="metric-strip">
        <div class="mc"><div class="mc-val b" id="m-price">$0.00</div><div class="mc-lbl">Live</div></div>
        <div class="mc"><div class="mc-val w" id="m-port">$0.00</div><div class="mc-lbl">Portfolio</div></div>
        <div class="mc"><div class="mc-val" id="m-pnl">$0.00</div><div class="mc-lbl">P&L</div></div>
        <div class="mc"><div class="mc-val" id="m-ret">0.00%</div><div class="mc-lbl">Return</div></div>
        <div class="mc"><div class="mc-val" id="m-unreal">$0.00</div><div class="mc-lbl">Unrealised</div></div>
        <div class="mc"><div class="mc-val w" id="m-cash">$0.00</div><div class="mc-lbl">Cash</div></div>
        <div class="mc"><div class="mc-val w" id="m-shares">0</div><div class="mc-lbl">Shares</div></div>
        <div class="mc"><div class="mc-val" id="m-date">---</div><div class="mc-lbl">Date</div></div>
      </div>
      <div id="progress-wrap"><div id="progress-fill"></div></div>
    </div>
  </div>
  <div id="trade-panel">
    <div class="trade-box">
      <div class="trade-hdr buy-hdr">BUY ORDER</div>
      <div class="qty-row">
        <span class="qty-label">Qty</span>
        <button class="qty-btn" id="buy-half">½</button>
        <input type="number" class="qty-input" id="buy-qty" value="1" min="0.01" step="1">
        <button class="qty-btn" id="buy-max">Max</button>
      </div>
      <div class="order-row"><span>Value</span><span id="buy-value">$0.00</span></div>
      <div class="order-row"><span>Max affordable</span><span id="buy-maxq">0 sh</span></div>
      <button class="exec-btn" id="buy-btn">BUY</button>
    </div>
    <div class="trade-box">
      <div class="trade-hdr sell-hdr">SELL ORDER</div>
      <div class="qty-row">
        <span class="qty-label">Qty</span>
        <button class="qty-btn" id="sell-half">½</button>
        <input type="number" class="qty-input" id="sell-qty" value="1" min="0.01" step="1">
        <button class="qty-btn" id="sell-all">All</button>
      </div>
      <div class="order-row"><span>Proceeds</span><span id="sell-proc">$0.00</span></div>
      <div class="order-row"><span>P&L on trade</span><span id="sell-pnl">$0.00</span></div>
      <button class="exec-btn" id="sell-btn">SELL</button>
    </div>
    <div class="trade-box">
      <div class="trade-hdr pos-hdr">POSITION</div>
      <div class="pos-grid">
        <div class="pos-cell"><div class="pos-val w" id="pos-sh">0.00</div><div class="pos-lbl">Shares</div></div>
        <div class="pos-cell"><div class="pos-val w" id="pos-ac">N/A</div><div class="pos-lbl">Avg Cost</div></div>
        <div class="pos-cell"><div class="pos-val" id="pos-ur">$0.00</div><div class="pos-lbl">Unrealised</div></div>
        <div class="pos-cell"><div class="pos-val" id="pos-ret">0.00%</div><div class="pos-lbl">Return</div></div>
      </div>
      <button id="reset-btn">Reset Portfolio</button>
    </div>
  </div>
</div>
<div id="toast-area"></div>
<script>
const CFG=__CONFIG__;
const CANDLES=CFG.candles,TICKER=CFG.ticker,INIT_CAP=CFG.capital;
let curIdx=CFG.startIdx,tickPhase=0.5,cash=INIT_CAP,shares=0,avgCost=0;
let trades=[],playing=false,playTimer=null;
let drawings=[],activeTool="none",drawStart=null,currentDraw=null;
let viewStart=0,viewCount=80,isDragging=false,dragStartX=0,dragStartView=0;

const wrap=document.getElementById("canvas-wrap");
const mc=document.getElementById("main-canvas");
const cc=document.getElementById("crosshair-canvas");
const mctx=mc.getContext("2d");
const cctx=cc.getContext("2d");

function resize(){
  const w=wrap.clientWidth,h=wrap.clientHeight;
  mc.width=cc.width=w; mc.height=cc.height=h;
  drawChart();
}
window.addEventListener("resize",resize);

const C={bg:"#0b0f17",grid:"#0f1621",border:"#1a2438",green:"#00e676",red:"#ff3d57",
          blue:"#4da6ff",yellow:"#ffd166",purple:"#b388ff",orange:"#ff9f43",
          text:"#8896ab",dim:"#3a4a5e",white:"#eef2f7"};

// ── Indicator math
function sma(d,p){return d.map((_,i)=>{if(i<p-1)return null;let s=0;for(let j=0;j<p;j++)s+=d[i-j];return s/p;});}
function ema(d,p){const k=2/(p+1),out=new Array(d.length).fill(null);let e=d[0];
  for(let i=0;i<d.length;i++){if(i<p-1){out[i]=null;continue;}if(i===p-1){let s=0;for(let j=0;j<p;j++)s+=d[j];e=s/p;out[i]=e;continue;}e=d[i]*k+e*(1-k);out[i]=e;}return out;}
function rsiCalc(c,p=14){const out=new Array(c.length).fill(null);let g=0,l=0;
  for(let i=1;i<=p;i++){const d=c[i]-c[i-1];if(d>0)g+=d;else l-=d;}
  let ag=g/p,al=l/p;out[p]=al===0?100:100-(100/(1+ag/al));
  for(let i=p+1;i<c.length;i++){const d=c[i]-c[i-1];const gd=d>0?d:0,ld=d<0?-d:0;ag=(ag*(p-1)+gd)/p;al=(al*(p-1)+ld)/p;out[i]=al===0?100:100-(100/(1+ag/al));}return out;}
function macdCalc(c){const f=ema(c,12),s=ema(c,26);
  const line=c.map((_,i)=>f[i]!=null&&s[i]!=null?f[i]-s[i]:null);
  const sig=ema(line.map(v=>v??0),9).map((v,i)=>line[i]!=null?v:null);
  const hist=line.map((v,i)=>v!=null&&sig[i]!=null?v-sig[i]:null);return{line,signal:sig,hist};}
function bbCalc(c,p=20,mult=2){const mid=sma(c,p);
  return c.map((_,i)=>{if(mid[i]==null)return{u:null,m:null,l:null};
    const sl=c.slice(Math.max(0,i-p+1),i+1),mn=mid[i];
    const std=Math.sqrt(sl.reduce((s,v)=>(s+(v-mn)**2),0)/sl.length);
    return{u:mn+mult*std,m:mn,l:mn-mult*std};});}
function stCalc(ca,p=10,mult=3){const hl2=ca.map(c=>(c.h+c.l)/2);
  const tr=ca.map((c,i)=>i===0?c.h-c.l:Math.max(c.h-c.l,Math.abs(c.h-ca[i-1].c),Math.abs(c.l-ca[i-1].c)));
  const atr=new Array(tr.length).fill(null);let a=tr.slice(0,p).reduce((s,v)=>s+v,0)/p;atr[p-1]=a;
  for(let i=p;i<tr.length;i++){a=(a*(p-1)+tr[i])/p;atr[i]=a;}
  const up=ca.map((_,i)=>atr[i]!=null?hl2[i]+mult*atr[i]:null);
  const dn=ca.map((_,i)=>atr[i]!=null?hl2[i]-mult*atr[i]:null);
  const st=new Array(ca.length).fill(null),dir=new Array(ca.length).fill(1);
  for(let i=p;i<ca.length;i++){const fu=up[i]>(st[i-1]??up[i])||ca[i-1].c<(st[i-1]??0)?up[i]:Math.min(up[i],st[i-1]);
    const fd=dn[i]<(st[i-1]??dn[i])||ca[i-1].c>(st[i-1]??999999)?dn[i]:Math.max(dn[i],st[i-1]);
    if(ca[i].c>=(dir[i-1]===-1?st[i-1]:fu)){st[i]=fd;dir[i]=1;}else{st[i]=fu;dir[i]=-1;}}return{st,dir};}
function vwapCalc(ca){let cpv=0,cv=0;return ca.map(c=>{const t=(c.h+c.l+c.c)/3;cpv+=t*c.v;cv+=c.v;return cv>0?cpv/cv:null;});}

const closes=CANDLES.map(c=>c.c);
const PRE={sma20:sma(closes,20),sma50:sma(closes,50),ema20:ema(closes,20),ema50:ema(closes,50),
           vwap:vwapCalc(CANDLES),bb:bbCalc(closes),st:stCalc(CANDLES),
           rsi:rsiCalc(closes),macd:macdCalc(closes)};

function getTickPrice(idx){
  const c=CANDLES[idx],t=Math.min(1,tickPhase);
  const base=c.o+(c.c-c.o)*t;
  const seed=idx*137+Math.floor(tickPhase*20);
  const noise=(Math.sin(seed*9301+49297)+Math.cos(seed*233+41))*0.5*Math.abs(c.h-c.l)*0.06;
  return Math.max(c.l,Math.min(c.h,base+noise));
}

const YPAD=12,XPAD_R=72;
function getSubPanels(){const p=[];if(document.getElementById("sc-vol").checked)p.push("vol");if(document.getElementById("sc-rsi").checked)p.push("rsi");if(document.getElementById("sc-macd").checked)p.push("macd");return p;}
function getPanelRects(){const W=mc.width,H=mc.height,subs=getSubPanels(),n=subs.length;
  const subH=n>0?Math.floor(H*0.28/n):0,mainH=H-n*subH-4;
  const r={main:{x:0,y:0,w:W-XPAD_R,h:mainH}};
  subs.forEach((s,i)=>{r[s]={x:0,y:mainH+i*subH,w:W-XPAD_R,h:subH};});return r;}
function priceToY(price,minP,maxP,rect){return rect.y+YPAD+(1-(price-minP)/(maxP-minP))*(rect.h-2*YPAD);}
function yToPrice(y,minP,maxP,rect){return maxP-((y-rect.y-YPAD)/(rect.h-2*YPAD))*(maxP-minP);}

// CRITICAL FIX: use getBoundingClientRect for correct canvas coords
function relXY(e){
  const r=cc.getBoundingClientRect();
  // Scale for device pixel ratio and CSS sizing
  const scaleX=cc.width/r.width;
  const scaleY=cc.height/r.height;
  return{x:(e.clientX-r.left)*scaleX,y:(e.clientY-r.top)*scaleY};
}

let _priceCache=null;
function getPriceRange(){
  if(_priceCache)return _priceCache;
  const ve=Math.min(curIdx+1,CANDLES.length),vs=Math.max(0,ve-viewCount);
  const vis=CANDLES.slice(vs,ve),lp=getTickPrice(curIdx);
  let mn=Infinity,mx=-Infinity;
  vis.forEach(c=>{mn=Math.min(mn,c.l);mx=Math.max(mx,c.h);});
  mx=Math.max(mx,lp);mn=Math.min(mn,lp);
  const p=(mx-mn)*0.08;mn-=p;mx+=p;if(mn===mx){mn-=1;mx+=1;}
  _priceCache={min:mn,max:mx};return _priceCache;
}

function drawLine(values,color,dash=[],width=1.5){
  const R=getPanelRects().main,{min:minP,max:maxP}=getPriceRange();
  const ve=Math.min(curIdx+1,CANDLES.length),vs=Math.max(0,ve-viewCount);
  const candleW=R.w/viewCount;
  mctx.save();mctx.strokeStyle=color;mctx.lineWidth=width;mctx.setLineDash(dash);mctx.beginPath();
  let started=false;
  values.forEach((v,i)=>{if(v==null){started=false;return;}const ri=vs+i;if(ri>curIdx)return;
    const x=R.x+(i+0.5)*candleW,y=priceToY(v,minP,maxP,R);
    if(!started){mctx.moveTo(x,y);started=true;}else mctx.lineTo(x,y);});
  mctx.stroke();mctx.restore();
}

function drawUserShapes(R,minP,maxP,candleW,vs){
  [...drawings,...(currentDraw?[currentDraw]:[])].forEach(d=>{
    mctx.save();mctx.strokeStyle=d.color||C.yellow;mctx.lineWidth=2;mctx.setLineDash([]);mctx.globalAlpha=0.9;
    if(d.type==="line"||d.type==="hline"){
      const x1=R.x+(d.x1-vs+0.5)*candleW,y1=priceToY(d.p1,minP,maxP,R);
      let x2,y2;
      if(d.type==="hline"){x2=R.w;y2=y1;}
      else{x2=R.x+(d.x2-vs+0.5)*candleW;y2=priceToY(d.p2,minP,maxP,R);}
      mctx.beginPath();mctx.moveTo(x1,y1);mctx.lineTo(x2,y2);mctx.stroke();
      // Draw endpoint dots for visibility
      mctx.fillStyle=d.color||C.yellow;
      mctx.beginPath();mctx.arc(x1,y1,4,0,Math.PI*2);mctx.fill();
      if(d.type==="line"){mctx.beginPath();mctx.arc(x2,y2,4,0,Math.PI*2);mctx.fill();}
    }else if(d.type==="rect"){
      const x1=R.x+(d.x1-vs+0.5)*candleW,y1=priceToY(d.p1,minP,maxP,R);
      const x2=R.x+(d.x2-vs+0.5)*candleW,y2=priceToY(d.p2,minP,maxP,R);
      const rx=Math.min(x1,x2),ry=Math.min(y1,y2),rw=Math.abs(x2-x1),rh=Math.abs(y2-y1);
      mctx.fillStyle=(d.color||C.yellow)+"22";mctx.fillRect(rx,ry,rw,rh);
      mctx.strokeRect(rx,ry,rw,rh);
    }
    mctx.restore();
  });
}

function drawChart(){
  if(!mc.width||!mc.height)return;
  _priceCache=null;
  const W=mc.width,H=mc.height,rects=getPanelRects(),R=rects.main;
  const ve=Math.min(curIdx+1,CANDLES.length);
  const vs=Math.max(0,Math.min(curIdx-viewCount+2,ve-viewCount));
  viewStart=vs;
  const visC=CANDLES.slice(vs,ve),candleW=R.w/viewCount,bodyW=Math.max(1,candleW*0.6);
  const liveP=getTickPrice(curIdx);
  const{min:minP,max:maxP}=getPriceRange();

  mctx.clearRect(0,0,W,H);mctx.fillStyle=C.bg;mctx.fillRect(0,0,W,H);

  // Grid
  mctx.strokeStyle=C.grid;mctx.lineWidth=0.5;
  for(let i=0;i<=5;i++){const y=R.y+i*(R.h/5);mctx.beginPath();mctx.moveTo(0,y);mctx.lineTo(W,y);mctx.stroke();}
  const gs=Math.max(1,Math.round(viewCount/8));
  for(let i=0;i<viewCount;i+=gs){const x=R.x+(i+0.5)*candleW;mctx.beginPath();mctx.moveTo(x,0);mctx.lineTo(x,R.h);mctx.stroke();}

  // Y labels
  mctx.fillStyle=C.dim;mctx.font="9px 'IBM Plex Mono'";mctx.textAlign="left";
  for(let i=0;i<=5;i++){const p=maxP-i*(maxP-minP)/5,y=priceToY(p,minP,maxP,R);mctx.fillText("$"+p.toFixed(2),R.w+4,y+3);}

  // X labels
  mctx.fillStyle=C.dim;mctx.textAlign="center";
  for(let i=0;i<visC.length;i+=gs){const c=visC[i],x=R.x+(i+0.5)*candleW;mctx.fillText(c.t.slice(5),x,R.y+R.h-2);}

  const sf=vs,st2=vs+visC.length;
  // Overlays
  if(document.getElementById("ov-sma20").checked)drawLine(PRE.sma20.slice(sf,st2),C.blue);
  if(document.getElementById("ov-sma50").checked)drawLine(PRE.sma50.slice(sf,st2),C.yellow,[3,2]);
  if(document.getElementById("ov-ema20").checked)drawLine(PRE.ema20.slice(sf,st2),C.purple);
  if(document.getElementById("ov-ema50").checked)drawLine(PRE.ema50.slice(sf,st2),C.orange,[3,2]);
  if(document.getElementById("ov-vwap").checked)drawLine(PRE.vwap.slice(sf,st2),"#00e5ff",[2,2]);

  if(document.getElementById("ov-bb").checked){
    const bbS=PRE.bb.slice(sf,st2);
    const R2=getPanelRects().main,{min:mn,max:mx}=getPriceRange(),cW=R2.w/viewCount;
    drawLine(bbS.map(b=>b.u),C.blue,[2,2],1);drawLine(bbS.map(b=>b.m),C.blue,[],0.8);drawLine(bbS.map(b=>b.l),C.blue,[2,2],1);
    mctx.save();mctx.fillStyle="rgba(77,166,255,0.04)";mctx.beginPath();let s2=false;
    bbS.forEach((b,i)=>{if(!b.u)return;const x=R2.x+(i+0.5)*cW,y=priceToY(b.u,mn,mx,R2);if(!s2){mctx.moveTo(x,y);s2=true;}else mctx.lineTo(x,y);});
    bbS.slice().reverse().forEach((b,i)=>{if(!b.l)return;const ri=bbS.length-1-i,x=R2.x+(ri+0.5)*cW,y=priceToY(b.l,mn,mx,R2);mctx.lineTo(x,y);});
    mctx.fill();mctx.restore();
  }

  if(document.getElementById("ov-st").checked){
    const stS=PRE.st.st.slice(sf,st2),dirS=PRE.st.dir.slice(sf,st2);
    const R2=getPanelRects().main,{min:mn,max:mx}=getPriceRange(),cW=R2.w/viewCount;
    mctx.save();mctx.strokeStyle=C.green;mctx.lineWidth=2;mctx.beginPath();let s3=false;
    stS.forEach((v,i)=>{if(v==null||dirS[i]!==1){s3=false;return;}const x=R2.x+(i+0.5)*cW,y=priceToY(v,mn,mx,R2);if(!s3){mctx.moveTo(x,y);s3=true;}else mctx.lineTo(x,y);});
    mctx.stroke();mctx.strokeStyle=C.red;mctx.beginPath();s3=false;
    stS.forEach((v,i)=>{if(v==null||dirS[i]!==(-1)){s3=false;return;}const x=R2.x+(i+0.5)*cW,y=priceToY(v,mn,mx,R2);if(!s3){mctx.moveTo(x,y);s3=true;}else mctx.lineTo(x,y);});
    mctx.stroke();mctx.restore();
  }

  // Candles
  visC.forEach((c,i)=>{
    const ri=vs+i,isLive=ri===curIdx;
    const price=isLive?liveP:c.c,hi=isLive?Math.max(c.h,liveP):c.h,lo=isLive?Math.min(c.l,liveP):c.l,op=c.o;
    const up=price>=op,col=up?C.green:C.red,x=R.x+(i+0.5)*candleW;
    mctx.strokeStyle=isLive?col+"cc":col;mctx.lineWidth=1;
    mctx.beginPath();mctx.moveTo(x,priceToY(hi,minP,maxP,R));mctx.lineTo(x,priceToY(lo,minP,maxP,R));mctx.stroke();
    const y1=priceToY(Math.max(op,price),minP,maxP,R),y2=priceToY(Math.min(op,price),minP,maxP,R);
    const bh=Math.max(1,y2-y1),bx=x-bodyW/2;
    if(isLive){const g=mctx.createLinearGradient(bx,y1,bx,y2);g.addColorStop(0,col+"99");g.addColorStop(1,col+"44");mctx.fillStyle=g;mctx.strokeStyle=col;mctx.lineWidth=1.8;}
    else{mctx.fillStyle=col;mctx.strokeStyle=col;mctx.lineWidth=0.5;}
    mctx.fillRect(bx,y1,bodyW,bh);if(isLive)mctx.strokeRect(bx,y1,bodyW,bh);
  });

  // Live price line
  const liveY=priceToY(liveP,minP,maxP,R),liveCol=liveP>=CANDLES[curIdx].o?C.green:C.red;
  mctx.save();mctx.strokeStyle=liveCol;mctx.lineWidth=1;mctx.setLineDash([4,3]);
  mctx.beginPath();mctx.moveTo(0,liveY);mctx.lineTo(R.w,liveY);mctx.stroke();mctx.restore();
  mctx.fillStyle=liveCol;mctx.fillRect(R.w,liveY-9,XPAD_R,18);
  mctx.fillStyle="#000";mctx.font="bold 10px 'IBM Plex Mono'";mctx.textAlign="left";
  mctx.fillText("$"+liveP.toFixed(2),R.w+3,liveY+4);

  // Trade markers
  trades.forEach(tr=>{
    const ti=CANDLES.findIndex(c=>c.t===tr.date);if(ti<vs||ti>=vs+visC.length)return;
    const i=ti-vs,x=R.x+(i+0.5)*candleW,y=priceToY(tr.price,minP,maxP,R),isBuy=tr.action==="BUY";
    mctx.save();mctx.fillStyle=isBuy?C.green:C.red;mctx.strokeStyle="#000";mctx.lineWidth=1;
    mctx.beginPath();mctx.arc(x,y,9,0,Math.PI*2);mctx.fill();mctx.stroke();
    mctx.fillStyle="#000";mctx.font="bold 9px 'IBM Plex Mono'";mctx.textAlign="center";
    mctx.fillText(isBuy?"B":"S",x,y+3);mctx.restore();
  });

  // USER DRAWINGS — drawn on top of everything
  drawUserShapes(R,minP,maxP,candleW,vs);

  // Sub-panels
  getSubPanels().forEach(sub=>{
    const SR=rects[sub];if(!SR)return;
    mctx.fillStyle=C.bg;mctx.fillRect(0,SR.y,W,SR.h);
    mctx.strokeStyle=C.border;mctx.lineWidth=1;mctx.beginPath();mctx.moveTo(0,SR.y);mctx.lineTo(W,SR.y);mctx.stroke();
    const subCandleW=SR.w/viewCount;
    if(sub==="vol"){
      const maxV=Math.max(...visC.map(c=>c.v));
      visC.forEach((c,i)=>{const x=SR.x+(i+0.5)*subCandleW,bh=maxV>0?(c.v/maxV)*(SR.h-8):2,by=SR.y+SR.h-bh-2;
        mctx.fillStyle=(c.c>=c.o?C.green:C.red)+"88";mctx.fillRect(x-bodyW/2,by,bodyW,bh);});
      mctx.fillStyle=C.dim;mctx.font="9px 'IBM Plex Mono'";mctx.textAlign="left";mctx.fillText("VOL",4,SR.y+11);
    }
    if(sub==="rsi"){
      const rsiS=PRE.rsi.slice(sf,st2);
      mctx.fillStyle="rgba(255,61,87,0.05)";mctx.fillRect(0,SR.y,W,(1-70/100)*SR.h);
      mctx.fillStyle="rgba(0,230,118,0.05)";mctx.fillRect(0,SR.y+(1-30/100)*SR.h,W,30/100*SR.h);
      [70,30].forEach(lvl=>{const y=SR.y+(1-lvl/100)*SR.h;mctx.strokeStyle=lvl===70?C.red+"66":C.green+"66";mctx.lineWidth=0.7;mctx.setLineDash([2,2]);mctx.beginPath();mctx.moveTo(0,y);mctx.lineTo(SR.w,y);mctx.stroke();mctx.setLineDash([]);});
      mctx.save();mctx.strokeStyle=C.yellow;mctx.lineWidth=1.4;mctx.beginPath();let sr=false;
      rsiS.forEach((v,i)=>{if(!v){sr=false;return;}const x=SR.x+(i+0.5)*subCandleW,y=SR.y+(1-v/100)*SR.h;if(!sr){mctx.moveTo(x,y);sr=true;}else mctx.lineTo(x,y);});
      mctx.stroke();mctx.restore();
      mctx.fillStyle=C.dim;mctx.font="9px 'IBM Plex Mono'";mctx.textAlign="left";mctx.fillText("RSI",4,SR.y+11);
      const lr=rsiS.filter(v=>v!=null).pop();if(lr!=null){mctx.fillStyle=C.yellow;mctx.textAlign="right";mctx.fillText(lr.toFixed(1),SR.w+XPAD_R-4,SR.y+11);}
    }
    if(sub==="macd"){
      const{line,signal:sig,hist}=PRE.macd;
      const ls=line.slice(sf,st2),ss=sig.slice(sf,st2),hs=hist.slice(sf,st2);
      const av=[...ls,...ss,...hs].filter(v=>v!=null);if(!av.length)return;
      const minM=Math.min(...av),maxM=Math.max(...av);
      const toY=(v)=>SR.y+(1-(v-minM)/(maxM-minM))*(SR.h-4)+2;
      const zero=toY(0);
      mctx.strokeStyle=C.dim;mctx.lineWidth=0.5;mctx.beginPath();mctx.moveTo(0,zero);mctx.lineTo(SR.w,zero);mctx.stroke();
      hs.forEach((v,i)=>{if(!v)return;const x=SR.x+(i+0.5)*subCandleW,y=toY(v),h2=Math.abs(y-zero);mctx.fillStyle=(v>=0?C.green:C.red)+"88";mctx.fillRect(x-bodyW/2,Math.min(y,zero),bodyW,Math.max(1,h2));});
      mctx.save();mctx.strokeStyle=C.blue;mctx.lineWidth=1.4;mctx.beginPath();let sm=false;
      ls.forEach((v,i)=>{if(!v){sm=false;return;}const x=SR.x+(i+0.5)*subCandleW,y=toY(v);if(!sm){mctx.moveTo(x,y);sm=true;}else mctx.lineTo(x,y);});
      mctx.stroke();mctx.strokeStyle=C.yellow;mctx.lineWidth=1.2;mctx.beginPath();sm=false;
      ss.forEach((v,i)=>{if(!v){sm=false;return;}const x=SR.x+(i+0.5)*subCandleW,y=toY(v);if(!sm){mctx.moveTo(x,y);sm=true;}else mctx.lineTo(x,y);});
      mctx.stroke();mctx.restore();
      mctx.fillStyle=C.dim;mctx.font="9px 'IBM Plex Mono'";mctx.textAlign="left";mctx.fillText("MACD",4,SR.y+11);
    }
  });

  mctx.strokeStyle=C.border;mctx.lineWidth=1;mctx.setLineDash([]);mctx.strokeRect(0,0,R.w,R.h);
}

// ── INTERACTION: Drawing & Pan
cc.addEventListener("mousedown",e=>{
  e.preventDefault();
  const{x,y}=relXY(e);
  const rects=getPanelRects(),R=rects.main;
  if(activeTool==="none"){isDragging=true;dragStartX=x;dragStartView=viewStart;document.body.classList.add("dragging");return;}
  // Only draw in main chart area
  if(y>R.h)return;
  const ve=Math.min(curIdx+1,CANDLES.length),vs=Math.max(0,ve-viewCount);
  const candleW=R.w/viewCount,ci=vs+Math.floor((x-R.x)/candleW);
  const{min:mn,max:mx}=getPriceRange(),price=yToPrice(y,mn,mx,R);
  drawStart={x:ci,p:price};currentDraw=null;
});

cc.addEventListener("mousemove",e=>{
  e.preventDefault();
  const{x,y}=relXY(e);
  drawCrosshair(x,y);
  if(isDragging&&activeTool==="none"){
    const rects=getPanelRects(),candleW=rects.main.w/viewCount;
    const shift=Math.round(-(x-dragStartX)/candleW);
    const ve=Math.min(curIdx+1,CANDLES.length);
    viewStart=Math.max(0,Math.min(dragStartView+shift,ve-viewCount));
    drawChart();return;
  }
  if(!drawStart)return;
  const rects=getPanelRects(),R=rects.main;
  const ve=Math.min(curIdx+1,CANDLES.length),vs=Math.max(0,ve-viewCount);
  const candleW=R.w/viewCount,ci=vs+Math.floor((x-R.x)/candleW);
  const{min:mn,max:mx}=getPriceRange(),price=yToPrice(y,mn,mx,R);
  if(activeTool==="line")       currentDraw={type:"line", x1:drawStart.x,p1:drawStart.p,x2:ci,p2:price,color:C.yellow};
  else if(activeTool==="hline") currentDraw={type:"hline",x1:drawStart.x,p1:drawStart.p,color:"#4da6ff"};
  else if(activeTool==="rect")  currentDraw={type:"rect", x1:drawStart.x,p1:drawStart.p,x2:ci,p2:price,color:C.yellow};
  drawChart();
});

cc.addEventListener("mouseup",e=>{
  document.body.classList.remove("dragging");
  isDragging=false;
  if(currentDraw&&(currentDraw.type==="hline"||(currentDraw.x1!==currentDraw.x2||currentDraw.p1!==currentDraw.p2))){
    drawings.push({...currentDraw});
  }
  currentDraw=null;drawStart=null;drawChart();
});

cc.addEventListener("mouseleave",()=>{cctx.clearRect(0,0,cc.width,cc.height);});
cc.addEventListener("wheel",e=>{e.preventDefault();viewCount=Math.max(20,Math.min(200,viewCount+Math.sign(e.deltaY)*5));drawChart();},{passive:false});

function drawCrosshair(x,y){
  cctx.clearRect(0,0,cc.width,cc.height);
  const rects=getPanelRects(),R=rects.main;
  const{min:minP,max:maxP}=getPriceRange();
  const ve=Math.min(curIdx+1,CANDLES.length),vs=Math.max(0,ve-viewCount);
  const candleW=R.w/viewCount,ci=vs+Math.floor((x-R.x)/candleW);
  const date=ci>=0&&ci<CANDLES.length?CANDLES[ci].t:"";
  cctx.save();cctx.strokeStyle="rgba(255,255,255,0.12)";cctx.lineWidth=0.8;cctx.setLineDash([3,3]);
  cctx.beginPath();cctx.moveTo(x,0);cctx.lineTo(x,cc.height);cctx.stroke();
  if(y<R.h){cctx.beginPath();cctx.moveTo(0,y);cctx.lineTo(R.w,y);cctx.stroke();
    const price=yToPrice(y,minP,maxP,R);cctx.setLineDash([]);
    cctx.fillStyle="#1a2438";cctx.fillRect(R.w,y-9,XPAD_R,18);
    cctx.fillStyle=C.white;cctx.font="9px 'IBM Plex Mono'";cctx.textAlign="left";cctx.fillText("$"+price.toFixed(2),R.w+3,y+3);}
  if(date){cctx.setLineDash([]);const tw=60;cctx.fillStyle="#1a2438";cctx.fillRect(x-tw/2,R.h-14,tw,14);cctx.fillStyle=C.white;cctx.font="9px 'IBM Plex Mono'";cctx.textAlign="center";cctx.fillText(date,x,R.h-3);}
  cctx.restore();
}

function updateHUD(){
  _priceCache=null;
  const lp=getTickPrice(curIdx),c=CANDLES[curIdx];
  const pv=cash+shares*lp,pnl=pv-INIT_CAP,pnlPct=pnl/INIT_CAP*100,unreal=avgCost>0&&shares>0?(lp-avgCost)*shares:0;
  document.getElementById("live-price-text").textContent="$"+lp.toFixed(2);
  document.getElementById("m-price").textContent="$"+lp.toFixed(2);
  document.getElementById("m-port").textContent="$"+pv.toFixed(2);
  const pnlEl=document.getElementById("m-pnl");pnlEl.textContent=(pnl>=0?"+":"")+f2(pnl);pnlEl.className="mc-val "+(pnl>=0?"g":"r");
  const retEl=document.getElementById("m-ret");retEl.textContent=(pnlPct>=0?"+":"")+pnlPct.toFixed(2)+"%";retEl.className="mc-val "+(pnlPct>=0?"g":"r");
  const urEl=document.getElementById("m-unreal");urEl.textContent=(unreal>=0?"+":"")+f2(unreal);urEl.className="mc-val "+(unreal>=0?"g":"r");
  document.getElementById("m-cash").textContent="$"+cash.toFixed(2);
  document.getElementById("m-shares").textContent=shares.toFixed(2);
  document.getElementById("m-date").textContent=c.t.slice(5);
  document.getElementById("progress-fill").style.width=((curIdx+1)/CANDLES.length*100)+"%";
  const maxQ=cash/lp;
  document.getElementById("buy-value").textContent="$"+(parseFloat(document.getElementById("buy-qty").value||1)*lp).toFixed(2);
  document.getElementById("buy-maxq").textContent=maxQ.toFixed(1)+" sh";
  const sq=parseFloat(document.getElementById("sell-qty").value||0);
  document.getElementById("sell-proc").textContent="$"+(sq*lp).toFixed(2);
  const spnl=avgCost>0?(lp-avgCost)*sq:0;
  const spEl=document.getElementById("sell-pnl");spEl.textContent=(spnl>=0?"+":"")+f2(spnl);spEl.style.color=spnl>=0?C.green:C.red;
  document.getElementById("pos-sh").textContent=shares.toFixed(2);
  document.getElementById("pos-ac").textContent=avgCost>0?"$"+avgCost.toFixed(2):"N/A";
  const urEl2=document.getElementById("pos-ur");urEl2.textContent=(unreal>=0?"+":"")+f2(unreal);urEl2.className="pos-val "+(unreal>=0?"g":"r");
  const pp=pnlPct;const retEl2=document.getElementById("pos-ret");retEl2.textContent=(pp>=0?"+":"")+pp.toFixed(2)+"%";retEl2.className="pos-val "+(pp>=0?"g":"r");
  updateTape(lp);
}
function f2(n){return"$"+Math.abs(n).toFixed(2);}
function updateTape(lp){
  const c=CANDLES[curIdx],chg=lp-c.o,pct=chg/c.o*100;
  const items=[{sym:TICKER,val:"$"+lp.toFixed(2),chg:(chg>=0?"+":"")+pct.toFixed(2)+"%",up:chg>=0},{sym:"VOL",val:c.v.toLocaleString(),chg:"",up:true},{sym:"HI",val:"$"+c.h.toFixed(2),chg:"",up:true},{sym:"LO",val:"$"+c.l.toFixed(2),chg:"",up:false},{sym:"OPEN",val:"$"+c.o.toFixed(2),chg:"",up:true},{sym:"BAR",val:(curIdx+1)+"/"+CANDLES.length,chg:"",up:true}];
  document.getElementById("tape").innerHTML=[...items,...items].map(it=>`<span class="tape-item"><span class="tape-sym">${it.sym}</span><span class="tape-val">${it.val}</span>${it.chg?`<span class="tape-chg ${it.up?"up":"down"}"> ${it.chg}</span>`:""}</span>`).join("");
}

const SPEED_MAP=[3.0,2.0,1.5,1.0,0.7,0.5,0.3,0.2,0.12,0.07];
function getSpeed(){return SPEED_MAP[document.getElementById("speed-range").value-1]||0.7;}
document.getElementById("speed-range").addEventListener("input",()=>{document.getElementById("speed-lbl").textContent=getSpeed().toFixed(2)+"s";});

function advanceBar(){if(curIdx<CANDLES.length-1){curIdx++;tickPhase=0.05;}else stopPlay();}
function startPlay(){playing=true;document.getElementById("play-btn").textContent="PAUSE";document.getElementById("play-btn").classList.add("playing");
  function tick(){tickPhase=Math.min(1,tickPhase+0.15);if(tickPhase>=1)advanceBar();updateHUD();drawChart();playTimer=setTimeout(tick,getSpeed()*1000*0.18);}tick();}
function stopPlay(){playing=false;clearTimeout(playTimer);playTimer=null;document.getElementById("play-btn").textContent="PLAY";document.getElementById("play-btn").classList.remove("playing");}
document.getElementById("play-btn").addEventListener("click",()=>playing?stopPlay():startPlay());
document.getElementById("btn-back1").addEventListener("click",()=>{if(curIdx>0){curIdx--;tickPhase=0.5;updateHUD();drawChart();}});
document.getElementById("btn-back5").addEventListener("click",()=>{curIdx=Math.max(0,curIdx-5);tickPhase=0.5;updateHUD();drawChart();});
document.getElementById("btn-fwd1").addEventListener("click",()=>{if(curIdx<CANDLES.length-1){curIdx++;tickPhase=0.5;updateHUD();drawChart();}});
document.getElementById("btn-fwd5").addEventListener("click",()=>{curIdx=Math.min(CANDLES.length-1,curIdx+5);tickPhase=0.5;updateHUD();drawChart();});

["tool-none","tool-line","tool-hline","tool-rect"].forEach(id=>{
  document.getElementById(id).addEventListener("click",()=>{
    activeTool=id.replace("tool-","");
    document.querySelectorAll(".draw-btn").forEach(b=>b.classList.remove("active"));
    document.getElementById(id).classList.add("active");
    const isDrawing=activeTool!=="none";
    document.body.classList.toggle("drawing",isDrawing);
    document.body.classList.toggle("panning",!isDrawing);
  });
});
document.getElementById("clear-draw").addEventListener("click",()=>{drawings=[];currentDraw=null;drawChart();});
document.querySelectorAll("input[type=checkbox]").forEach(cb=>cb.addEventListener("change",()=>drawChart()));

function toast(msg,type){const el=document.createElement("div");el.className="toast "+type;el.textContent=msg;document.getElementById("toast-area").appendChild(el);setTimeout(()=>el.remove(),3000);}
document.getElementById("buy-qty").addEventListener("input",()=>updateHUD());
document.getElementById("sell-qty").addEventListener("input",()=>updateHUD());
document.getElementById("buy-half").addEventListener("click",()=>{const lp=getTickPrice(curIdx);document.getElementById("buy-qty").value=Math.max(0.01,(cash/lp/2)).toFixed(2);updateHUD();});
document.getElementById("buy-max").addEventListener("click",()=>{const lp=getTickPrice(curIdx);document.getElementById("buy-qty").value=Math.max(0.01,Math.floor(cash/lp*100)/100).toFixed(2);updateHUD();});
document.getElementById("sell-half").addEventListener("click",()=>{document.getElementById("sell-qty").value=Math.max(0.01,shares/2).toFixed(2);updateHUD();});
document.getElementById("sell-all").addEventListener("click",()=>{document.getElementById("sell-qty").value=Math.max(0.01,shares).toFixed(2);updateHUD();});
document.getElementById("buy-btn").addEventListener("click",()=>{const lp=getTickPrice(curIdx),qty=parseFloat(document.getElementById("buy-qty").value)||0,cost=qty*lp;if(qty<=0)return;if(cost>cash){toast("Insufficient funds","sell");return;}const ov=avgCost*shares;shares+=qty;cash-=cost;avgCost=(ov+cost)/shares;trades.push({date:CANDLES[curIdx].t,action:"BUY",price:lp,shares:qty});toast("Bought "+qty.toFixed(2)+" "+TICKER+" @ $"+lp.toFixed(2),"buy");updateHUD();drawChart();});
document.getElementById("sell-btn").addEventListener("click",()=>{const lp=getTickPrice(curIdx),qty=parseFloat(document.getElementById("sell-qty").value)||0;if(qty<=0||qty>shares){toast("Not enough shares","sell");return;}shares-=qty;cash+=qty*lp;if(shares<=0){shares=0;avgCost=0;}trades.push({date:CANDLES[curIdx].t,action:"SELL",price:lp,shares:qty});toast("Sold "+qty.toFixed(2)+" "+TICKER+" @ $"+lp.toFixed(2),"sell");updateHUD();drawChart();});
document.getElementById("reset-btn").addEventListener("click",()=>{cash=INIT_CAP;shares=0;avgCost=0;trades=[];updateHUD();drawChart();});

// Initialize with pan mode
document.body.classList.add("panning");
resize();updateHUD();drawChart();
</script>
</body>
</html>
"""

html_out = HTML.replace("__CONFIG__", config_json)

import streamlit.components.v1 as components
components.html(html_out, height=820, scrolling=False)
