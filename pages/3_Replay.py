import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf
import pandas as pd
import json
import sys, os
from datetime import date, timedelta
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.styles import SHARED_CSS
from utils.nav import navbar

st.set_page_config(page_title="Replay — 11%", page_icon="$", layout="wide", initial_sidebar_state="collapsed")
st.markdown(SHARED_CSS, unsafe_allow_html=True)
st.markdown("""<style>
#MainMenu,footer,header{display:none!important}
.block-container{padding:0.5rem 1rem 0!important;max-width:100%!important}
[data-testid="stTextInput"] input{background:#0c1018!important;color:#eef2f7!important;border:1px solid #1a2235!important;border-radius:8px!important;font-family:'IBM Plex Mono',monospace!important;font-size:0.85rem!important;padding:0.6rem 0.8rem!important;height:44px!important}
[data-testid="stNumberInput"] input{background:#0c1018!important;color:#eef2f7!important;border:1px solid #1a2235!important;border-radius:8px!important;font-family:'IBM Plex Mono',monospace!important;font-size:0.85rem!important;height:44px!important}
div[data-testid="stSelectbox"]>div>div{background:#0c1018!important;border:1px solid #1a2235!important;border-radius:8px!important;color:#eef2f7!important;font-family:'IBM Plex Mono',monospace!important;font-size:0.82rem!important;min-height:44px!important}
[data-testid="stDateInput"] input{background:#0c1018!important;color:#eef2f7!important;border:1px solid #1a2235!important;border-radius:8px!important;font-family:'IBM Plex Mono',monospace!important;font-size:0.82rem!important;height:44px!important}
div.stButton>button{font-family:'IBM Plex Mono',monospace!important;font-size:0.72rem!important;font-weight:700!important;text-transform:uppercase!important;letter-spacing:0.1em!important;border-radius:8px!important;padding:0.6rem 1.2rem!important;height:44px!important;min-height:44px!important}
div.stButton>button[kind="primary"]{background:#00e676!important;color:#000!important;border:none!important;box-shadow:0 0 20px rgba(0,230,118,0.2)!important}
div.stButton>button[kind="primary"]:hover{background:#00ff88!important;box-shadow:0 0 28px rgba(0,230,118,0.4)!important}
div.stButton>button:hover{border-color:#00e676!important;color:#00e676!important}
[data-testid="stSlider"]{padding-top:0.3rem}
[data-testid="stSlider"] label{font-family:'IBM Plex Mono',monospace!important;font-size:0.65rem!important;color:#8896ab!important;text-transform:uppercase!important;letter-spacing:0.15em!important}
</style>""", unsafe_allow_html=True)
navbar()

for k,v in [("rp_df",None),("rp_ticker","AAPL"),("rp_loaded",False),("rp_trades",[]),("rp_capital",10000.0),("rp_interval","1d"),("rp_start",str(date.today()-timedelta(days=365))),("rp_end",str(date.today())),("rp_start_bar",60)]:
    if k not in st.session_state: st.session_state[k]=v

st.markdown("""<div style="display:flex;align-items:center;justify-content:space-between;padding:0.6rem 0 0.8rem;border-bottom:1px solid #1a2235;margin-bottom:0.8rem;">
<div><div style="font-family:'Bebas Neue',sans-serif;font-size:1.9rem;letter-spacing:0.07em;color:#eef2f7;line-height:1;display:flex;align-items:center;gap:0.7rem;">MARKET REPLAY<span style="font-family:'IBM Plex Mono',monospace;font-size:0.48rem;font-weight:700;text-transform:uppercase;letter-spacing:0.2em;color:#000;background:#00e676;border-radius:3px;padding:3px 9px;">FLAGSHIP</span></div>
<div style="font-family:'IBM Plex Mono',monospace;font-size:0.6rem;color:#2a3550;margin-top:0.15rem;">Animated bar-by-bar · Portfolio sim · Add/reduce positions · Date picker · RAF-smooth playback</div></div>
<div style="font-family:'IBM Plex Mono',monospace;font-size:0.52rem;color:#1a2235;text-align:right;line-height:2;">SPACE=Play/Pause · ←/→=Step · B=Buy · A=Add Long · S=Short · X=Close All · P=Partial</div></div>""", unsafe_allow_html=True)

col1,col2,col3,col4,col5,col6,col7,col8=st.columns([1.5,1,1.2,1.2,0.8,0.7,0.7,0.7])
with col1: ticker_in=st.text_input("Ticker",value=st.session_state["rp_ticker"],placeholder="AAPL, TSLA, BTC-USD",label_visibility="collapsed").strip().upper()
with col2:
    imap={"1m":"1 Min","5m":"5 Min","15m":"15 Min","30m":"30 Min","1h":"1 Hour","4h":"4 Hour","1d":"Daily","1wk":"Weekly","1mo":"Monthly"}
    interval=st.selectbox("Interval",list(imap.keys()),index=list(imap.keys()).index(st.session_state["rp_interval"]),format_func=lambda x:imap[x],label_visibility="collapsed")
with col3: start_date=st.date_input("Start",value=date.fromisoformat(st.session_state["rp_start"]),label_visibility="collapsed")
with col4: end_date=st.date_input("End",value=date.fromisoformat(st.session_state["rp_end"]),label_visibility="collapsed")
with col5: capital=st.number_input("Capital",value=st.session_state["rp_capital"],min_value=100.0,step=1000.0,label_visibility="collapsed",format="%.0f")
with col6: load_btn=st.button("⬛ Load",type="primary",use_container_width=True)
with col7: reset_btn=st.button("↺ Reset",use_container_width=True)
with col8:
    if st.session_state["rp_loaded"] and st.session_state["rp_trades"]:
        st.download_button("↓ Export",pd.DataFrame(st.session_state["rp_trades"]).to_csv(index=False),file_name="replay_trades.csv",mime="text/csv",use_container_width=True)
    else: st.button("↓ Export",disabled=True,use_container_width=True)

if st.session_state["rp_loaded"] and st.session_state["rp_df"]:
    n=len(st.session_state["rp_df"])
    sb_col,_=st.columns([4,6])
    with sb_col:
        start_bar=st.slider("📅 Playback start bar — drag to set the date where blind trading begins",min_value=10,max_value=max(10,n-1),value=min(st.session_state.get("rp_start_bar",60),n-1))
        if start_bar!=st.session_state.get("rp_start_bar"): st.session_state["rp_start_bar"]=start_bar

if reset_btn:
    st.session_state.update({"rp_loaded":False,"rp_df":None,"rp_trades":[],"rp_capital":capital})
    st.rerun()

if load_btn:
    with st.spinner(f"Loading {ticker_in}..."):
        try:
            raw=yf.Ticker(ticker_in).history(start=str(start_date),end=str(end_date),interval=interval)
            if raw.empty or len(raw)<20: st.error(f"Not enough data for {ticker_in}. Try a wider date range or different interval.")
            else:
                raw=raw[["Open","High","Low","Close","Volume"]].dropna().reset_index()
                raw.columns=["Date","Open","High","Low","Close","Volume"]
                raw["Date"]=raw["Date"].astype(str).str[:16]
                st.session_state.update({"rp_df":raw.to_dict("records"),"rp_ticker":ticker_in,"rp_interval":interval,"rp_start":str(start_date),"rp_end":str(end_date),"rp_trades":[],"rp_capital":capital,"rp_loaded":True,"rp_start_bar":min(60,len(raw)-1)})
                st.rerun()
        except Exception as e: st.error(f"Error: {e}")

if not st.session_state["rp_loaded"] or not st.session_state["rp_df"]:
    items="".join(f'<div style="background:#0c1018;border:1px solid #1a2235;border-radius:10px;padding:1.2rem 1rem;text-align:center;"><div style="font-size:1.6rem;margin-bottom:0.5rem;">{ic}</div><div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.52rem;text-transform:uppercase;letter-spacing:0.16em;color:#00e676;margin-bottom:0.3rem;">{tl}</div><div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.6rem;color:#3a4a5e;">{de}</div></div>' for ic,tl,de in [("📅","Date Control","Pick exact start/end dates. Scrub to any point in history"),("📈","Portfolio Sim","Add to longs, scale shorts, partial closes — real math"),("⚡","RAF Smooth","requestAnimationFrame. Zero dropped frames at any speed"),("✏️","Full Toolkit","SMA · BB · RSI · MACD · Fib · Trend lines · Boxes")])
    st.markdown(f'<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:62vh;gap:2.5rem;padding:2rem 1rem;"><div style="text-align:center;"><div style="font-family:\'Bebas Neue\',sans-serif;font-size:5.5rem;line-height:0.88;letter-spacing:0.03em;margin-bottom:1.2rem;"><span style="color:#00e676;">TRADE</span><br><span style="color:#eef2f7;">THE PAST.</span><br><span style="color:#ff3d57;">WIN</span><br><span style="color:#eef2f7;">THE FUTURE.</span></div><div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.72rem;color:#3a4a5e;max-width:520px;margin:0 auto;line-height:2;">Set a <strong style="color:#00e676;">date range</strong> above, load any ticker, drag the <strong style="color:#4da6ff;">playback start slider</strong>.<br>Build a real portfolio — add to winners, scale out, short the dips.</div></div><div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;max-width:820px;width:100%;">{items}</div></div>',unsafe_allow_html=True)
else:
    bars_json=json.dumps(st.session_state["rp_df"])
    trades_json=json.dumps(st.session_state["rp_trades"])
    capital_val=float(st.session_state["rp_capital"])
    ticker_label=st.session_state["rp_ticker"]
    n_bars=len(st.session_state["rp_df"])
    start_bar_js=st.session_state.get("rp_start_bar",min(60,n_bars-1))

    # Inline the full engine
    HTML="""<!DOCTYPE html><html><head><meta charset="utf-8">
<script src="https://cdn.jsdelivr.net/npm/lightweight-charts@4.1.3/dist/lightweight-charts.standalone.production.js"></script>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600;700&family=Bebas+Neue&display=swap" rel="stylesheet">
<style>
:root{--bg:#06080c;--s:#0c1018;--b:#1a2235;--b2:#0d1117;--t:#eef2f7;--d:#3a4a5e;--d2:#1a2235;--g:#00e676;--r:#ff3d57;--y:#ffd166;--bl:#4da6ff;--p:#b388ff}
*{margin:0;padding:0;box-sizing:border-box}html,body{width:100%;height:100%;background:var(--bg);color:var(--t);font-family:'IBM Plex Mono',monospace;overflow:hidden}
#root{display:flex;flex-direction:column;height:100vh}
#toolbar{display:flex;align-items:center;background:var(--bg);border-bottom:2px solid var(--b);flex-shrink:0;overflow-x:auto;overflow-y:hidden;scrollbar-width:none;min-height:58px}
#toolbar::-webkit-scrollbar{display:none}
.tsep{width:1px;background:var(--b);align-self:stretch;margin:0 2px;flex-shrink:0}
.tg{display:flex;align-items:center;gap:3px;padding:6px 8px;flex-shrink:0}
.tl{font-size:0.4rem;text-transform:uppercase;letter-spacing:0.18em;color:var(--d2);margin-right:2px;white-space:nowrap}
.tb{font-family:'IBM Plex Mono',monospace;font-size:0.6rem;font-weight:700;text-transform:uppercase;letter-spacing:0.07em;background:var(--s);border:1px solid var(--b);border-radius:6px;color:var(--d);padding:8px 14px;cursor:pointer;white-space:nowrap;transition:all 0.12s;line-height:1;min-height:36px}
.tb:hover{color:var(--t);border-color:#2a3550;background:#0f1620}.tb.on{color:var(--g);border-color:var(--g);background:rgba(0,230,118,0.08)}.tb.ct-on{color:var(--t);background:#1a2235;border-color:#2a3550}
#bp{min-width:64px}.#bp.pl{color:var(--y);border-color:var(--y);background:rgba(255,209,102,0.08)}
.buy-btn{color:#000!important;background:var(--g)!important;border-color:var(--g)!important;font-size:0.68rem!important;padding:10px 18px!important;min-height:38px!important}
.buy-btn:hover{background:#00ff88!important;box-shadow:0 0 14px rgba(0,230,118,0.4)}
.addl-btn{color:#000!important;background:var(--bl)!important;border-color:var(--bl)!important}
.short-btn{color:#fff!important;background:var(--r)!important;border-color:var(--r)!important;font-size:0.68rem!important;padding:10px 16px!important;min-height:38px!important}
.short-btn:hover{background:#ff6070!important}
.adds-btn{color:var(--r)!important;background:rgba(255,61,87,0.12)!important;border-color:var(--r)!important}
.close-btn{color:#000!important;background:var(--y)!important;border-color:var(--y)!important;font-size:0.68rem!important;padding:10px 16px!important;min-height:38px!important}
#ss{-webkit-appearance:none;width:80px;height:3px;background:var(--b);border-radius:2px;outline:none;cursor:pointer}
#ss::-webkit-slider-thumb{-webkit-appearance:none;width:11px;height:11px;border-radius:50%;background:var(--g);cursor:pointer}
#sv{font-size:0.6rem;color:var(--g);font-weight:700;min-width:34px}
#scrubber{-webkit-appearance:none;width:120px;height:3px;background:var(--b);border-radius:2px;outline:none;cursor:pointer}
#scrubber::-webkit-slider-thumb{-webkit-appearance:none;width:11px;height:11px;border-radius:50%;background:var(--bl);cursor:pointer}
#bp2{font-size:0.52rem;color:var(--d);min-width:90px}
.mi{background:var(--s);border:1px solid var(--b);border-radius:6px;color:var(--t);font-family:'IBM Plex Mono',monospace;font-size:0.7rem;padding:7px 10px;outline:none;width:80px;height:36px}
.mi:focus{border-color:var(--d)}
#tbd{font-family:'Bebas Neue',sans-serif;font-size:1.3rem;color:var(--t);letter-spacing:0.07em;line-height:1;padding:0 10px}
#bar-strip{display:flex;align-items:center;gap:22px;padding:6px 14px;background:var(--bg);border-bottom:1px solid var(--b2);font-size:0.7rem;color:var(--d);flex-shrink:0;overflow-x:auto;scrollbar-width:none}
#bar-strip::-webkit-scrollbar{display:none}
.bsp{color:var(--t);font-weight:700;font-size:0.85rem}.bup{color:var(--g)}.bdn{color:var(--r)}.bdm{color:var(--d)}
#metrics{display:flex;border-bottom:1px solid var(--b);background:var(--bg);flex-shrink:0}
.mc{flex:1;padding:7px 14px;border-right:1px solid var(--b);min-width:0}.mc:last-child{border-right:none}
.ml{font-size:0.46rem;text-transform:uppercase;letter-spacing:0.18em;color:var(--d2);margin-bottom:2px;white-space:nowrap}
.mv{font-size:1rem;font-weight:700;color:var(--t);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.mv.pos{color:var(--g)}.mv.neg{color:var(--r)}.mv.dim{color:var(--d)}
#body{display:flex;flex:1;min-height:0;overflow:hidden}
#chart-col{flex:1;display:flex;flex-direction:column;min-width:0;overflow:hidden}
#main-chart{flex:1;min-height:0}#vol-chart{flex-shrink:0;height:72px}
#rsi-chart{flex-shrink:0;height:70px;display:none;border-top:1px solid var(--b2)}
#macd-chart{flex-shrink:0;height:70px;display:none;border-top:1px solid var(--b2)}
#draw-bar{display:flex;align-items:center;gap:4px;flex-wrap:wrap;padding:5px 10px;background:var(--bg);border-top:1px solid var(--b);flex-shrink:0}
.db{font-family:'IBM Plex Mono',monospace;font-size:0.48rem;font-weight:700;text-transform:uppercase;letter-spacing:0.07em;background:transparent;border:1px solid var(--b);border-radius:4px;color:var(--d);padding:4px 8px;cursor:pointer;white-space:nowrap;transition:all 0.12s;line-height:1}
.db:hover{color:var(--t);border-color:#2a3550}.db.on{color:var(--y);border-color:var(--y);background:rgba(255,209,102,0.07)}
.db.dng{color:var(--r)!important;border-color:var(--r)!important}
#dcp{background:var(--s);border:1px solid var(--b);border-radius:4px;color:var(--t);font-family:'IBM Plex Mono',monospace;font-size:0.48rem;padding:3px 5px;cursor:pointer;outline:none}
#sidebar{width:260px;flex-shrink:0;background:var(--bg);border-left:1px solid var(--b);display:flex;flex-direction:column;overflow:hidden}
.ss2{padding:9px 12px;border-bottom:1px solid var(--b2);flex-shrink:0}
.st2{font-size:0.42rem;text-transform:uppercase;letter-spacing:0.2em;color:var(--d2);margin-bottom:7px}
.ir{display:flex;align-items:center;justify-content:space-between;margin-bottom:5px}
.il{display:flex;align-items:center;gap:6px;font-size:0.58rem;color:var(--d);cursor:pointer;transition:color 0.12s;user-select:none}
.il:hover{color:var(--t)}.il input{accent-color:var(--g);width:12px;height:12px;cursor:pointer}
.id2{width:7px;height:7px;border-radius:50%;flex-shrink:0}
.ip{background:var(--s);border:1px solid var(--b);border-radius:3px;color:var(--d);font-family:'IBM Plex Mono',monospace;font-size:0.52rem;padding:2px 5px;width:38px;outline:none;text-align:center}
.ip:focus{border-color:var(--d);color:var(--t)}
#ps{overflow-y:auto;max-height:130px;flex-shrink:0}#ps::-webkit-scrollbar{width:2px}#ps::-webkit-scrollbar-thumb{background:var(--b)}
.pl2{display:flex;justify-content:space-between;align-items:center;margin:5px 12px;padding:6px 10px;border-radius:6px;border:1px solid rgba(0,230,118,0.2);background:rgba(0,230,118,0.04);font-size:0.58rem}
.pl2.sl{border-color:rgba(255,61,87,0.25);background:rgba(255,61,87,0.04)}
#lw{flex:1;overflow-y:auto;min-height:0}#lw::-webkit-scrollbar{width:3px}#lw::-webkit-scrollbar-track{background:var(--bg)}#lw::-webkit-scrollbar-thumb{background:var(--b);border-radius:2px}
.lr{display:grid;grid-template-columns:50px 44px 64px 1fr;gap:3px;padding:5px 12px;border-bottom:1px solid var(--b2);font-size:0.55rem;align-items:center}
.lr:hover{background:rgba(255,255,255,0.01)}
.lt{color:var(--d2)}.lbu{color:var(--g);font-weight:700}.lsh{color:var(--r);font-weight:700}.lcl{color:var(--y);font-weight:700}.lpr{color:var(--t)}.lpos{color:var(--g);font-weight:700;text-align:right}.lneg{color:var(--r);font-weight:700;text-align:right}.ldm{color:var(--d);text-align:right}
#toast{position:fixed;top:12px;left:50%;transform:translateX(-50%);background:var(--s);border:1px solid var(--b);border-radius:7px;padding:9px 20px;font-size:0.65rem;font-weight:600;z-index:9999;display:none;pointer-events:none;box-shadow:0 16px 48px rgba(0,0,0,0.85);white-space:nowrap}
#sml{font-size:0.52rem;color:var(--bl);padding:2px 6px;background:rgba(77,166,255,0.1);border:1px solid rgba(77,166,255,0.2);border-radius:3px;display:none}
</style></head><body>
<div id="root">
<div id="toast"></div>
<div id="toolbar">
  <div class="tg"><span class="tl">Playback</span>
    <button class="tb" id="bp" onclick="togglePlay()">▶ Play</button>
    <button class="tb" onclick="stepBars(-10)">◀◀</button>
    <button class="tb" onclick="stepBars(-1)">◀</button>
    <button class="tb" onclick="stepBars(1)">▶</button>
    <button class="tb" onclick="stepBars(10)">▶▶</button>
    <button class="tb" onclick="goToStart()" title="Go to playback start">⏮ Start</button>
    <button class="tb" onclick="goToEnd()" title="Jump to end">⏭ End</button>
  </div>
  <div class="tsep"></div>
  <div class="tg"><span class="tl">Speed</span>
    <input type="range" id="ss" min="1" max="10" value="3" oninput="onSpeedChange(this.value)">
    <span id="sv">0.3×</span>
  </div>
  <div class="tsep"></div>
  <div class="tg"><span class="tl">Position</span>
    <input type="range" id="scrubber" min="10" max="__NBARS_M1__" value="__SB__" oninput="scrubTo(+this.value)">
    <span id="bp2">__SB__ / __NBARS__</span>
  </div>
  <div class="tsep"></div>
  <div class="tg"><span class="tl">Chart</span>
    <button class="tb ct-on" id="ct-candle" onclick="setChartType('candle')">Candles</button>
    <button class="tb" id="ct-heikin" onclick="setChartType('heikin')">Heikin</button>
    <button class="tb" id="ct-bar" onclick="setChartType('bar')">Bars</button>
    <button class="tb" id="ct-line" onclick="setChartType('line')">Line</button>
  </div>
  <div class="tsep"></div>
  <div class="tg"><span class="tl">Qty</span>
    <input type="number" class="mi" id="tq" value="10" min="1" style="width:60px">
    <span class="tl" style="margin-left:4px">@ $</span>
    <input type="number" class="mi" id="tp" value="0.00" step="0.01" style="width:80px">
    <button class="tb buy-btn" onclick="ex('buy')">BUY</button>
    <button class="tb addl-btn" onclick="ex('addlong')">+LONG</button>
    <button class="tb short-btn" onclick="ex('short')">SHORT</button>
    <button class="tb adds-btn" onclick="ex('addshort')">+SHORT</button>
    <button class="tb close-btn" onclick="ex('close')">CLOSE ALL</button>
    <button class="tb" style="color:var(--y);border-color:var(--y)" onclick="ex('partial')">PARTIAL</button>
  </div>
  <div class="tsep" style="margin-left:auto"></div>
  <div class="tg"><span id="tbd">__TICKER__</span></div>
</div>
<div id="bar-strip">
  <span id="bd" class="bdm">—</span>
  <span>O <span id="bo" class="bsp">—</span></span>
  <span>H <span id="bh" class="bsp">—</span></span>
  <span>L <span id="bl" class="bsp">—</span></span>
  <span>C <span id="bc" class="bsp">—</span></span>
  <span id="bchg">—</span>
  <span id="sml">📅 Playback Start</span>
  <span style="margin-left:auto" id="bv" class="bdm">—</span>
</div>
<div id="metrics">
  <div class="mc"><div class="ml">Portfolio</div><div class="mv" id="m0">—</div></div>
  <div class="mc"><div class="ml">Cash</div><div class="mv dim" id="m1">—</div></div>
  <div class="mc"><div class="ml">Return</div><div class="mv" id="m2">—</div></div>
  <div class="mc"><div class="ml">Realised P&L</div><div class="mv" id="m3">—</div></div>
  <div class="mc"><div class="ml">Open P&L</div><div class="mv" id="m4">—</div></div>
  <div class="mc"><div class="ml">Positions</div><div class="mv dim" id="m5">0</div></div>
  <div class="mc"><div class="ml">Win Rate</div><div class="mv dim" id="m6">—</div></div>
  <div class="mc"><div class="ml">Trades</div><div class="mv dim" id="m7">0</div></div>
</div>
<div id="body">
  <div id="chart-col">
    <div id="main-chart"></div>
    <div id="vol-chart"></div>
    <div id="rsi-chart"></div>
    <div id="macd-chart"></div>
    <div id="draw-bar">
      <span class="tl" style="margin-right:3px">DRAW:</span>
      <button class="db" id="draw-cursor" onclick="setDraw('cursor')">↖ Select</button>
      <button class="db" id="draw-hline" onclick="setDraw('hline')">— H-Line</button>
      <button class="db" id="draw-vline" onclick="setDraw('vline')">| V-Line</button>
      <button class="db" id="draw-trend" onclick="setDraw('trend')">╱ Trend</button>
      <button class="db" id="draw-ray" onclick="setDraw('ray')">→ Ray</button>
      <button class="db" id="draw-fib" onclick="setDraw('fib')">✦ Fibonacci</button>
      <button class="db" id="draw-rect" onclick="setDraw('rect')">▭ Box</button>
      <button class="db" id="draw-mark" onclick="setDraw('mark')">⬦ Marker</button>
      <span style="flex:1"></span>
      <select id="dcp"><option value="#ffd166" selected>● Yellow</option><option value="#00e676">● Green</option><option value="#ff3d57">● Red</option><option value="#4da6ff">● Blue</option><option value="#b388ff">● Purple</option><option value="#ffffff">● White</option></select>
      <button class="db dng" onclick="clearDrawings()">✕ Clear</button>
    </div>
  </div>
  <div id="sidebar">
    <div class="ss2">
      <div class="st2">Indicators</div>
      <div class="ir"><label class="il" for="is1"><input type="checkbox" id="is1" onchange="renderAll()"><span class="id2" style="background:#4da6ff"></span>SMA</label><input type="number" class="ip" id="ip1" value="20" min="2" max="200" onchange="renderAll()"></div>
      <div class="ir"><label class="il" for="is2"><input type="checkbox" id="is2" onchange="renderAll()"><span class="id2" style="background:#b388ff"></span>SMA</label><input type="number" class="ip" id="ip2" value="50" min="2" max="200" onchange="renderAll()"></div>
      <div class="ir"><label class="il" for="is3"><input type="checkbox" id="is3" onchange="renderAll()"><span class="id2" style="background:#00e676"></span>EMA</label><input type="number" class="ip" id="ip3" value="20" min="2" max="200" onchange="renderAll()"></div>
      <div class="ir"><label class="il" for="is4"><input type="checkbox" id="is4" onchange="renderAll()"><span class="id2" style="background:#00bcd4"></span>EMA</label><input type="number" class="ip" id="ip4" value="50" min="2" max="200" onchange="renderAll()"></div>
      <div class="ir"><label class="il" for="is5"><input type="checkbox" id="is5" onchange="renderAll()"><span class="id2" style="background:#ffd166"></span>VWAP</label></div>
      <div class="ir"><label class="il" for="is6"><input type="checkbox" id="is6" onchange="renderAll()"><span class="id2" style="background:#ff7043"></span>Bollinger</label><input type="number" class="ip" id="ip6" value="20" min="5" max="100" onchange="renderAll()"></div>
      <div class="ir"><label class="il" for="is7"><input type="checkbox" id="is7" onchange="tsc('rsi',this.checked)"><span class="id2" style="background:#e91e63"></span>RSI</label><input type="number" class="ip" id="ip7" value="14" min="2" max="50" onchange="renderAll()"></div>
      <div class="ir"><label class="il" for="is8"><input type="checkbox" id="is8" onchange="tsc('macd',this.checked)"><span class="id2" style="background:#ff9800"></span>MACD</label></div>
    </div>
    <div class="ss2" style="padding-bottom:4px"><div class="st2">Open Positions</div></div>
    <div id="ps"></div>
    <div class="ss2" style="padding-bottom:4px"><div class="st2">Trade Log</div></div>
    <div id="lw"><div id="tl2"></div></div>
  </div>
</div>
</div>
<script>
const ALL=__BARS__;const CAP=__CAP__;const N=ALL.length;const SB=__SB__;
let cur=SB,isP=false,rafId=null,lastT=0,mspb=1000/0.3,ct='candle',dm='cursor';
let cash=CAP,positions=[],trades=__TRADES__,rPnl=0,wins=0,losses=0,pid=0;
let segs=[],dstate={pts:[],s:[]},marks=[];
const IS={};
const SPEEDS=[0.07,0.15,0.3,0.5,1,1.5,2,3,5,10];
const CO={layout:{background:{type:'solid',color:'#06080c'},textColor:'#3a4a5e',fontSize:11,fontFamily:"'IBM Plex Mono',monospace"},grid:{vertLines:{color:'#0d1117'},horzLines:{color:'#0d1117'}},crosshair:{mode:LightweightCharts.CrosshairMode.Normal,vertLine:{color:'#2a3550',width:1,style:LightweightCharts.LineStyle.Dashed,labelBackgroundColor:'#1a2235'},horzLine:{color:'#2a3550',width:1,style:LightweightCharts.LineStyle.Dashed,labelBackgroundColor:'#1a2235'}},rightPriceScale:{borderColor:'#1a2235',textColor:'#3a4a5e'},timeScale:{borderColor:'#1a2235',textColor:'#3a4a5e',timeVisible:true,secondsVisible:false},handleScroll:{vertTouchDrag:true,mouseWheel:true,pressedMouseMove:true},handleScale:{axisPressedMouseMove:true,mouseWheel:true,pinch:true}};
const me=document.getElementById('main-chart');
const MC=LightweightCharts.createChart(me,{...CO,width:me.offsetWidth,height:me.offsetHeight||400});
const ve=document.getElementById('vol-chart');
const VC=LightweightCharts.createChart(ve,{...CO,width:ve.offsetWidth,height:72,timeScale:{...CO.timeScale,visible:false},rightPriceScale:{...CO.rightPriceScale,scaleMargins:{top:0.05,bottom:0}}});
const re=document.getElementById('rsi-chart');
const RC=LightweightCharts.createChart(re,{...CO,width:re.offsetWidth,height:70,timeScale:{...CO.timeScale,visible:false}});
const rsi_s=RC.addLineSeries({color:'#e91e63',lineWidth:1});
const rsi_ob=RC.addLineSeries({color:'rgba(255,61,87,0.3)',lineWidth:1,lineStyle:LightweightCharts.LineStyle.Dashed});
const rsi_os=RC.addLineSeries({color:'rgba(0,230,118,0.3)',lineWidth:1,lineStyle:LightweightCharts.LineStyle.Dashed});
const mce=document.getElementById('macd-chart');
const MCC=LightweightCharts.createChart(mce,{...CO,width:mce.offsetWidth,height:70,timeScale:{...CO.timeScale,visible:false}});
const mf=MCC.addLineSeries({color:'#ff9800',lineWidth:1});
const ms2=MCC.addLineSeries({color:'#4da6ff',lineWidth:1});
const mh=MCC.addHistogramSeries({priceScaleId:''});
MCC.priceScale('').applyOptions({scaleMargins:{top:0.1,bottom:0.1}});
let MS=null,VS=null;
function cMS(t){if(MS)MC.removeSeries(MS);const u='#00e676',d='#ff3d57';switch(t){case 'bar':MS=MC.addBarSeries({upColor:u,downColor:d});break;case 'line':MS=MC.addLineSeries({color:u,lineWidth:2});break;case 'area':MS=MC.addAreaSeries({lineColor:u,topColor:'rgba(0,230,118,0.22)',bottomColor:'rgba(0,230,118,0)',lineWidth:2});break;default:MS=MC.addCandlestickSeries({upColor:u,downColor:d,borderUpColor:u,borderDownColor:d,wickUpColor:u,wickDownColor:d});}}
function cVS(){if(VS)VC.removeSeries(VS);VS=VC.addHistogramSeries({priceFormat:{type:'volume'},priceScaleId:''});VC.priceScale('').applyOptions({scaleMargins:{top:0.1,bottom:0}});}
cMS('candle');cVS();
function ss(src,tgts){src.timeScale().subscribeVisibleLogicalRangeChange(r=>{if(!r)return;tgts.forEach(c=>c.timeScale().setVisibleLogicalRange(r));});}
ss(MC,[VC,RC,MCC]);ss(VC,[MC,RC,MCC]);
function tt(d){return d.length>10?d.replace(' ','T')+':00':d;}
function bBars(u){const o=[];for(let i=0;i<=u;i++){const b=ALL[i];if(ct==='heikin'){const hc=(b.Open+b.High+b.Low+b.Close)/4;const ho=i===0?(b.Open+b.Close)/2:(o[i-1].open+o[i-1].close)/2;const hh=Math.max(b.High,ho,hc);const hl=Math.min(b.Low,ho,hc);o.push({time:tt(b.Date),open:ho,high:hh,low:hl,close:hc});}else o.push({time:tt(b.Date),open:b.Open,high:b.High,low:b.Low,close:b.Close});}return o;}
function bVol(u){return Array.from({length:u+1},(_,i)=>({time:tt(ALL[i].Date),value:ALL[i].Volume,color:ALL[i].Close>=ALL[i].Open?'rgba(0,230,118,0.3)':'rgba(255,61,87,0.25)'}));}
function cSMA(d,p){const o=[];for(let i=p-1;i<d.length;i++){let s=0;for(let j=0;j<p;j++)s+=ALL[i-j].Close;o.push({time:tt(ALL[i].Date),value:s/p});}return o;}
function cEMA(d,p){const k=2/(p+1);const o=[];let e=ALL[0].Close;for(let i=1;i<d.length;i++){e=ALL[i].Close*k+e*(1-k);if(i>=p-1)o.push({time:tt(ALL[i].Date),value:e});}return o;}
function cVWAP(d){const o=[];let cv=0,cpv=0;for(let i=0;i<d.length;i++){cv+=ALL[i].Volume;cpv+=ALL[i].Close*ALL[i].Volume;if(cv>0)o.push({time:tt(ALL[i].Date),value:cpv/cv});}return o;}
function cBB(d,p){const u=[],l=[],m=[];for(let i=p-1;i<d.length;i++){const c=[];for(let j=0;j<p;j++)c.push(ALL[i-j].Close);const mn=c.reduce((a,b)=>a+b,0)/p;const sd=Math.sqrt(c.reduce((a,b)=>a+(b-mn)**2,0)/p);const t=tt(ALL[i].Date);u.push({time:t,value:mn+2*sd});l.push({time:t,value:mn-2*sd});m.push({time:t,value:mn});}return{upper:u,lower:l,mid:m};}
function cRSI(d,p){const o=[];let ag=0,al=0;for(let i=1;i<=p;i++){const dv=ALL[i].Close-ALL[i-1].Close;if(dv>0)ag+=dv;else al-=dv;}ag/=p;al/=p;for(let i=p;i<d.length;i++){if(i>p){const dv=ALL[i].Close-ALL[i-1].Close;ag=(ag*(p-1)+Math.max(dv,0))/p;al=(al*(p-1)+Math.max(-dv,0))/p;}const rs=al===0?100:ag/al;o.push({time:tt(ALL[i].Date),value:100-100/(1+rs)});}return o;}
function cMACD(d){const k12=2/13,k26=2/27,k9=2/10;let e12=ALL[0].Close,e26=ALL[0].Close;const mv=[],sv=[];for(let i=1;i<d.length;i++){e12=ALL[i].Close*k12+e12*(1-k12);e26=ALL[i].Close*k26+e26*(1-k26);if(i>=25)mv.push({t:tt(ALL[i].Date),v:e12-e26});}let sig=mv[0]?.v||0;mv.forEach(m=>{sig=m.v*k9+sig*(1-k9);sv.push(sig);});return mv.map((m,i)=>({time:m.t,macd:m.v,signal:sv[i],hist:m.v-sv[i]}));}
function uLine(id,en,fac,data){if(en){if(!IS[id])IS[id]=fac();IS[id].setData(data);}else if(IS[id]){MC.removeSeries(IS[id]);delete IS[id];}}
function renderAll(){
  const data=ALL.slice(0,cur+1);const bars=bBars(cur);
  if(ct==='line'||ct==='area')MS.setData(bars.map(b=>({time:b.time,value:b.close})));else MS.setData(bars);
  VS.setData(bVol(cur));
  const mkrs=[];trades.forEach(t=>{const idx=ALL.findIndex(b=>b.Date>=t.date);if(idx<0||idx>cur)return;const col=t.dir==='buy'||t.dir==='addlong'?'#00e676':t.dir==='short'||t.dir==='addshort'?'#ff3d57':'#ffd166';const shp=t.dir==='buy'||t.dir==='addlong'?'arrowUp':t.dir==='short'||t.dir==='addshort'?'arrowDown':'circle';const pos2=t.dir==='buy'||t.dir==='addlong'?'belowBar':t.dir==='short'||t.dir==='addshort'?'aboveBar':'inBar';const lbl={'buy':'B','addlong':'+L','short':'S','addshort':'+S','close':'✕','partial':'~'}[t.dir]||t.dir;mkrs.push({time:tt(ALL[idx].Date),position:pos2,color:col,shape:shp,text:lbl+' $'+t.price.toFixed(2),size:1});});marks.forEach(m=>{if(ALL.findIndex(b=>b.Date>=m.date)<=cur)mkrs.push(m.marker);});MS.setMarkers(mkrs);
  const p1=+document.getElementById('ip1').value||20,p2=+document.getElementById('ip2').value||50,p3=+document.getElementById('ip3').value||20,p4=+document.getElementById('ip4').value||50,p6=+document.getElementById('ip6').value||20,p7=+document.getElementById('ip7').value||14;
  uLine('s1',document.getElementById('is1').checked,()=>MC.addLineSeries({color:'#4da6ff',lineWidth:1,crosshairMarkerVisible:false}),cSMA(data,p1));
  uLine('s2',document.getElementById('is2').checked,()=>MC.addLineSeries({color:'#b388ff',lineWidth:1,crosshairMarkerVisible:false}),cSMA(data,p2));
  uLine('e1',document.getElementById('is3').checked,()=>MC.addLineSeries({color:'#00e676',lineWidth:1,lineStyle:LightweightCharts.LineStyle.Dashed,crosshairMarkerVisible:false}),cEMA(data,p3));
  uLine('e2',document.getElementById('is4').checked,()=>MC.addLineSeries({color:'#00bcd4',lineWidth:1,lineStyle:LightweightCharts.LineStyle.Dashed,crosshairMarkerVisible:false}),cEMA(data,p4));
  uLine('vw',document.getElementById('is5').checked,()=>MC.addLineSeries({color:'#ffd166',lineWidth:1,lineStyle:LightweightCharts.LineStyle.Dotted,crosshairMarkerVisible:false}),cVWAP(data));
  if(document.getElementById('is6').checked){const bb=cBB(data,p6);if(!IS.bbU){IS.bbU=MC.addLineSeries({color:'rgba(255,112,67,0.55)',lineWidth:1,lineStyle:LightweightCharts.LineStyle.Dashed,crosshairMarkerVisible:false});IS.bbL=MC.addLineSeries({color:'rgba(255,112,67,0.55)',lineWidth:1,lineStyle:LightweightCharts.LineStyle.Dashed,crosshairMarkerVisible:false});IS.bbM=MC.addLineSeries({color:'rgba(255,112,67,0.25)',lineWidth:1,crosshairMarkerVisible:false});}IS.bbU.setData(bb.upper);IS.bbL.setData(bb.lower);IS.bbM.setData(bb.mid);}else{['bbU','bbL','bbM'].forEach(k=>{if(IS[k]){MC.removeSeries(IS[k]);delete IS[k];}});}
  if(document.getElementById('is7').checked&&data.length>p7+1){const rd=cRSI(data,p7);rsi_s.setData(rd);rsi_ob.setData(rd.map(d=>({time:d.time,value:70})));rsi_os.setData(rd.map(d=>({time:d.time,value:30})));}
  if(document.getElementById('is8').checked&&data.length>30){const md=cMACD(data);mf.setData(md.map(d=>({time:d.time,value:d.macd})));ms2.setData(md.map(d=>({time:d.time,value:d.signal})));mh.setData(md.map(d=>({time:d.time,value:d.hist,color:d.hist>=0?'rgba(0,230,118,0.5)':'rgba(255,61,87,0.5)'})));}
  Object.keys(IS).filter(k=>k.startsWith('pl_')).forEach(k=>{MC.removeSeries(IS[k]);delete IS[k];});
  positions.forEach(pos=>{const key='pl_'+pos.id;IS[key]=MC.addLineSeries({color:pos.dir==='buy'?'rgba(0,230,118,0.5)':'rgba(255,61,87,0.5)',lineWidth:1,lineStyle:LightweightCharts.LineStyle.Dotted,crosshairMarkerVisible:false,lastValueVisible:true,priceLineVisible:false});const pd=ALL.slice(0,cur+1).filter(b=>b.Date>=pos.date).map(b=>({time:tt(b.Date),value:pos.entry}));if(pd.length)IS[key].setData(pd);});
  if(!IS.sl){const lo=Math.min(...ALL.map(b=>b.Low))*0.99;const hi=Math.max(...ALL.map(b=>b.High))*1.01;IS.sl=MC.addLineSeries({color:'rgba(77,166,255,0.35)',lineWidth:1,lineStyle:LightweightCharts.LineStyle.Dashed,crosshairMarkerVisible:false,lastValueVisible:false});IS.sl.setData([{time:tt(ALL[SB].Date),value:lo},{time:tt(ALL[SB].Date),value:hi}]);}
  updStrip();updMetrics();updPos();
  document.getElementById('bp2').textContent=(cur+1)+' / '+N+' · '+ALL[cur].Date.slice(0,10);
  document.getElementById('scrubber').value=cur;
  document.getElementById('tp').value=ALL[cur].Close.toFixed(2);
  document.getElementById('sml').style.display=(cur===SB)?'inline':'none';
}
function updStrip(){const b=ALL[cur];const prev=ALL[Math.max(0,cur-1)];const ch=b.Close-prev.Close;const pct=(ch/prev.Close*100);document.getElementById('bd').textContent=b.Date;document.getElementById('bo').textContent='$'+b.Open.toFixed(2);document.getElementById('bh').textContent='$'+b.High.toFixed(2);document.getElementById('bl').textContent='$'+b.Low.toFixed(2);document.getElementById('bc').textContent='$'+b.Close.toFixed(2);const ce=document.getElementById('bchg');ce.textContent=(ch>=0?'▲':'▼')+' '+Math.abs(ch).toFixed(2)+' ('+pct.toFixed(2)+'%)';ce.className=ch>=0?'bup':'bdn';const v=b.Volume;document.getElementById('bv').textContent=v>1e9?(v/1e9).toFixed(2)+'B':v>1e6?(v/1e6).toFixed(2)+'M':v>1e3?(v/1e3).toFixed(1)+'K':v.toFixed(0);}
function updMetrics(){const p=ALL[cur].Close;let op=0;positions.forEach(pos=>{op+=pos.dir==='buy'?(p-pos.entry)*pos.qty:(pos.entry-p)*pos.qty;});const invested=positions.filter(x=>x.dir==='buy').reduce((a,x)=>a+x.entry*x.qty,0);const port=cash+invested+op;const ret=(port-CAP)/CAP*100;const tc=trades.filter(t=>t.dir==='close'||t.dir==='partial').length;const wr=tc>0?(wins/tc*100).toFixed(0)+'%':'—';function sm(id,v,c){const el=document.getElementById(id);el.textContent=v;el.className='mv'+(c?' '+c:'');}function fmt2(v){const a=Math.abs(v);return(v<0?'-':'')+'$'+(a>=1e6?(a/1e6).toFixed(2)+'M':a>=1e3?(a/1e3).toFixed(1)+'K':a.toFixed(0));}sm('m0',fmt2(port),ret>=0?'pos':'neg');sm('m1',fmt2(cash),'dim');sm('m2',(ret>=0?'+':'')+ret.toFixed(2)+'%',ret>=0?'pos':'neg');sm('m3',(rPnl>=0?'+':'')+fmt2(Math.abs(rPnl)),rPnl>0?'pos':rPnl<0?'neg':'dim');sm('m4',op!==0?(op>=0?'+':'')+op.toFixed(2):'—',op>0?'pos':op<0?'neg':'dim');document.getElementById('m5').textContent=positions.length;sm('m6',wr,'dim');document.getElementById('m7').textContent=trades.length;}
function updPos(){const el=document.getElementById('ps');if(!positions.length){el.innerHTML='';return;}const p=ALL[cur].Close;el.innerHTML=positions.map(pos=>{const pnl=pos.dir==='buy'?(p-pos.entry)*pos.qty:(pos.entry-p)*pos.qty;const cls=pos.dir==='short'?'pl2 sl':'pl2';const pc=pnl>=0?'#00e676':'#ff3d57';return`<div class="${cls}"><div><span style="color:${pos.dir==='buy'?'#00e676':'#ff3d57'};font-weight:700;font-size:0.68rem">${pos.dir==='buy'?'●L':'●S'}</span> <span style="color:#8896ab;font-size:0.58rem">${pos.qty} @ $${pos.entry.toFixed(2)}</span></div><div style="color:${pc};font-weight:700;font-size:0.62rem">${(pnl>=0?'+':'')+pnl.toFixed(2)}</div></div>`;}).join('');}
function ex(dir){if(cur<SB){toast('Move past playback start to trade!','#ff3d57');return;}const qty=Math.max(1,parseInt(document.getElementById('tq').value)||10);const price=parseFloat(document.getElementById('tp').value)||ALL[cur].Close;const date=ALL[cur].Date;const time=new Date().toTimeString().slice(0,5);
if(dir==='buy'){const cost=price*qty;if(cost>cash){toast('Insufficient cash!','#ff3d57');return;}cash-=cost;positions.push({dir:'buy',entry:price,qty,date,id:pid++});trades.push({dir:'buy',price,qty,date,pnl:0,time});toast(`BUY ${qty} @ $${price.toFixed(2)}`,'#00e676');}
else if(dir==='addlong'){if(!positions.filter(p=>p.dir==='buy').length){toast('No long to add to — use BUY first','#ffd166');return;}const cost=price*qty;if(cost>cash){toast('Insufficient cash!','#ff3d57');return;}cash-=cost;positions.push({dir:'buy',entry:price,qty,date,id:pid++});trades.push({dir:'addlong',price,qty,date,pnl:0,time});toast(`+LONG ${qty} @ $${price.toFixed(2)} · ${positions.filter(p=>p.dir==='buy').length} legs`,'#4da6ff');}
else if(dir==='short'){cash+=price*qty;positions.push({dir:'short',entry:price,qty,date,id:pid++});trades.push({dir:'short',price,qty,date,pnl:0,time});toast(`SHORT ${qty} @ $${price.toFixed(2)}`,'#ff3d57');}
else if(dir==='addshort'){if(!positions.filter(p=>p.dir==='short').length){toast('No short to add to — use SHORT first','#ffd166');return;}cash+=price*qty;positions.push({dir:'short',entry:price,qty,date,id:pid++});trades.push({dir:'addshort',price,qty,date,pnl:0,time});toast(`+SHORT ${qty} @ $${price.toFixed(2)}`,'#ff3d57');}
else if(dir==='close'){if(!positions.length){toast('No open positions','#ffd166');return;}let tp=0;positions.forEach(pos=>{const pnl=pos.dir==='buy'?(price-pos.entry)*pos.qty:(pos.entry-price)*pos.qty;if(pos.dir==='buy')cash+=price*pos.qty;else cash-=price*pos.qty;rPnl+=pnl;tp+=pnl;if(pnl>0)wins++;else losses++;});trades.push({dir:'close',price,qty:positions.reduce((a,p)=>a+p.qty,0),date,pnl:tp,time});positions=[];toast(`CLOSED ALL — P&L: ${(tp>=0?'+':'')+tp.toFixed(2)}`,tp>=0?'#00e676':'#ff3d57');}
else if(dir==='partial'){if(!positions.length){toast('No open positions','#ffd166');return;}const pos=positions.pop();const pnl=pos.dir==='buy'?(price-pos.entry)*pos.qty:(pos.entry-price)*pos.qty;if(pos.dir==='buy')cash+=price*pos.qty;else cash-=price*pos.qty;rPnl+=pnl;if(pnl>0)wins++;else losses++;trades.push({dir:'partial',price,qty:pos.qty,date,pnl,time});toast(`PARTIAL ${pos.qty} @ $${price.toFixed(2)} P&L: ${(pnl>=0?'+':'')+pnl.toFixed(2)}`,pnl>=0?'#00e676':'#ff3d57');}
updLog();renderAll();}
function updLog(){document.getElementById('tl2').innerHTML=[...trades].reverse().map(t=>{const cls=t.dir==='buy'||t.dir==='addlong'?'lbu':t.dir==='short'||t.dir==='addshort'?'lsh':'lcl';const lbl={'buy':'BUY','addlong':'+L','short':'SHT','addshort':'+S','close':'CLO','partial':'~CL'}[t.dir]||t.dir.toUpperCase().slice(0,4);const ps=(t.dir==='close'||t.dir==='partial')?((t.pnl>=0?'+':'')+t.pnl.toFixed(2)):'—';const pc=t.pnl>0?'lpos':t.pnl<0?'lneg':'ldm';return`<div class="lr"><span class="lt">${t.time}</span><span class="${cls}">${lbl}</span><span class="lpr">$${t.price.toFixed(2)}</span><span class="${pc}">${ps}</span></div>`;}).join('');}
let _tt2=null;
function toast(msg,color='#00e676'){const el=document.getElementById('toast');el.textContent=msg;el.style.display='block';el.style.color=color;el.style.borderColor=color;if(_tt2)clearTimeout(_tt2);_tt2=setTimeout(()=>el.style.display='none',2400);}
let speed=0.3;
function onSpeedChange(v){speed=SPEEDS[v-1];mspb=1000/speed;document.getElementById('sv').textContent=speed+'×';}
function rafLoop(ts){if(!isP)return;if(ts-lastT>=mspb){lastT=ts;if(cur>=N-1){stopPlay();return;}cur++;renderAll();MC.timeScale().scrollToPosition(4,false);}rafId=requestAnimationFrame(rafLoop);}
function startPlay(){if(rafId)cancelAnimationFrame(rafId);lastT=performance.now();rafId=requestAnimationFrame(rafLoop);}
function stopPlay(){isP=false;if(rafId){cancelAnimationFrame(rafId);rafId=null;}const b=document.getElementById('bp');b.textContent='▶ Play';b.style.color='';b.style.borderColor='';b.style.background='';}
function togglePlay(){isP=!isP;const b=document.getElementById('bp');if(isP){startPlay();b.textContent='⏸ Pause';b.style.color='#ffd166';b.style.borderColor='#ffd166';b.style.background='rgba(255,209,102,0.08)';}else stopPlay();}
function stepBars(n){stopPlay();cur=Math.max(10,Math.min(N-1,cur+n));renderAll();}
function scrubTo(n){stopPlay();cur=Math.max(10,Math.min(N-1,n));renderAll();}
function goToStart(){stopPlay();cur=SB;renderAll();}
function goToEnd(){stopPlay();cur=N-1;renderAll();MC.timeScale().fitContent();}
function setChartType(t){ct=t;document.querySelectorAll('[id^="ct-"]').forEach(b=>b.classList.remove('ct-on'));document.getElementById('ct-'+t).classList.add('ct-on');cMS(t);renderAll();}
function tsc(name,on){document.getElementById(name+'-chart').style.display=on?'block':'none';if(on)renderAll();resize();}
let _dstate={pts:[],s:[]};
function setDraw(mode){dm=mode;document.querySelectorAll('.db').forEach(b=>b.classList.remove('on'));document.getElementById('draw-'+mode)?.classList.add('on');_dstate={pts:[],s:[]};const sc=mode==='cursor';MC.applyOptions({handleScroll:sc,handleScale:sc});}
function gdc(){return document.getElementById('dcp').value;}
MC.subscribeClick(param=>{if(dm==='cursor'||!param.time)return;const price=MS.coordinateToPrice(param.point.y);const time=param.time;const color=gdc();
if(dm==='hline'){const s=MC.addLineSeries({color:color+'bb',lineWidth:1,lineStyle:LightweightCharts.LineStyle.Dashed,crosshairMarkerVisible:false,lastValueVisible:false});s.setData(ALL.slice(0,cur+1).map(b=>({time:tt(b.Date),value:price})));segs.push({series:[s]});toast('H-Line @ $'+price.toFixed(2),'#ffd166');}
else if(dm==='vline'){const lo=Math.min(...ALL.slice(0,cur+1).map(b=>b.Low))*0.8;const hi=Math.max(...ALL.slice(0,cur+1).map(b=>b.High))*1.2;const s=MC.addLineSeries({color:color+'99',lineWidth:1,lineStyle:LightweightCharts.LineStyle.Dashed,crosshairMarkerVisible:false,lastValueVisible:false});s.setData([{time,value:lo},{time,value:hi}]);segs.push({series:[s]});toast('V-Line','#ffd166');}
else if(dm==='trend'||dm==='ray'){if(!_dstate.pts.length){_dstate.pts=[{time,price}];toast('Click 2nd point…','#ffd166');}else{const p1=_dstate.pts[0],p2={time,price};const s=MC.addLineSeries({color,lineWidth:1.5,crosshairMarkerVisible:false,lastValueVisible:false});let pts=[{time:p1.time,value:p1.price},{time:p2.time,value:p2.price}];if(dm==='ray'){const i1=ALL.findIndex(b=>tt(b.Date)>=p1.time);const i2=ALL.findIndex(b=>tt(b.Date)>=p2.time);if(i1>=0&&i2>i1){const sl=(p2.price-p1.price)/(i2-i1);pts.push({time:tt(ALL[cur].Date),value:p2.price+sl*(cur-i2)});}}s.setData(pts);segs.push({series:[s]});_dstate={pts:[],s:[]};toast('Line drawn','#ffd166');}}
else if(dm==='fib'){if(!_dstate.pts.length){_dstate.pts=[{time,price}];toast('Click end…','#ffd166');}else{const p1=_dstate.pts[0],p2={time,price};const hi=Math.max(p1.price,p2.price),lo=Math.min(p1.price,p2.price),rng=hi-lo;[0,0.236,0.382,0.5,0.618,0.764,1.0].forEach((f,i)=>{const val=hi-rng*f;const cols=['#ffffff','#4da6ff','#00e676','#ffd166','#ff9800','#b388ff','#ff3d57'];const s=MC.addLineSeries({color:cols[i]+'88',lineWidth:1,lineStyle:LightweightCharts.LineStyle.Dashed,crosshairMarkerVisible:false,lastValueVisible:true,priceFormat:{type:'custom',formatter:()=>(f*100)+'%'}});s.setData([{time:p1.time,value:val},{time:p2.time,value:val}]);segs.push({series:[s]});});_dstate={pts:[],s:[]};toast('Fibonacci drawn','#ffd166');}}
else if(dm==='rect'){if(!_dstate.pts.length){_dstate.pts=[{time,price}];toast('Click corner…','#ffd166');}else{const p1=_dstate.pts[0],p2={time,price};const hi=Math.max(p1.price,p2.price),lo=Math.min(p1.price,p2.price);const t1=p1.time<p2.time?p1.time:p2.time,t2=p1.time<p2.time?p2.time:p1.time;[[{time:t1,value:hi},{time:t2,value:hi}],[{time:t1,value:lo},{time:t2,value:lo}],[{time:t1,value:hi},{time:t1,value:lo}],[{time:t2,value:hi},{time:t2,value:lo}]].forEach(pts=>{const s=MC.addLineSeries({color:color+'aa',lineWidth:1,crosshairMarkerVisible:false,lastValueVisible:false});s.setData(pts);segs.push({series:[s]});});_dstate={pts:[],s:[]};toast('Box drawn','#ffd166');}}
else if(dm==='mark'){const idx=ALL.findIndex(b=>tt(b.Date)>=time);if(idx>=0&&idx<=cur){marks.push({date:ALL[idx].Date,marker:{time:tt(ALL[idx].Date),position:'aboveBar',color,shape:'circle',text:'✦',size:0}});renderAll();toast('Marker placed','#ffd166');}}});
function clearDrawings(){segs.forEach(seg=>seg.series.forEach(s=>MC.removeSeries(s)));segs=[];marks=[];renderAll();toast('Cleared','#ffd166');}
document.addEventListener('keydown',e=>{const tag=e.target.tagName;if(tag==='INPUT'||tag==='SELECT'||tag==='TEXTAREA')return;switch(e.code){case 'Space':e.preventDefault();togglePlay();break;case 'ArrowRight':stepBars(e.shiftKey?10:1);break;case 'ArrowLeft':stepBars(e.shiftKey?-10:-1);break;case 'KeyB':ex('buy');break;case 'KeyA':ex('addlong');break;case 'KeyS':ex('short');break;case 'KeyX':ex('close');break;case 'KeyP':ex('partial');break;}});
function resize(){const cc=document.getElementById('chart-col');const total=cc.offsetHeight;const subH=(document.getElementById('rsi-chart').style.display!=='none'?70:0)+(document.getElementById('macd-chart').style.display!=='none'?70:0);const dbH=document.getElementById('draw-bar').offsetHeight;const mH=Math.max(200,total-72-subH-dbH-2);const w=cc.offsetWidth;MC.resize(w,mH);VC.resize(w,72);RC.resize(w,70);MCC.resize(w,70);}
const ro=new ResizeObserver(resize);ro.observe(document.getElementById('chart-col'));
// Init from trades
trades.forEach(t=>{if(t.dir==='close'||t.dir==='partial'){rPnl+=t.pnl;if(t.pnl>0)wins++;else losses++;}});
cash=CAP;positions=[];let legs=[];trades.forEach(t=>{if(t.dir==='buy'||t.dir==='addlong'){cash-=t.price*t.qty;legs.push({dir:'buy',entry:t.price,qty:t.qty,date:t.date,id:pid++});}if(t.dir==='short'||t.dir==='addshort'){cash+=t.price*t.qty;legs.push({dir:'short',entry:t.price,qty:t.qty,date:t.date,id:pid++});}if(t.dir==='close'){legs.forEach(l=>{if(l.dir==='buy')cash+=t.price*l.qty;else cash-=t.price*l.qty;});legs=[];}if(t.dir==='partial'&&legs.length){const l=legs.pop();if(l.dir==='buy')cash+=t.price*l.qty;else cash-=t.price*l.qty;}});positions=legs;
onSpeedChange(3);renderAll();updLog();MC.timeScale().fitContent();
setTimeout(()=>MC.timeScale().scrollToPosition(3,false),200);
toast('Loaded · SPACE=Play · B=Buy · A=+Long · S=Short · X=Close All · P=Partial','#00e676');
</script></body></html>"""

    HTML=HTML.replace("__BARS__",bars_json).replace("__TRADES__",trades_json).replace("__CAP__",str(capital_val)).replace("__TICKER__",ticker_label).replace("__NBARS__",str(n_bars)).replace("__NBARS_M1__",str(n_bars-1)).replace("__SB__",str(start_bar_js))
    components.html(HTML, height=900, scrolling=False)
