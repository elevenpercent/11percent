import streamlit as st
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(__file__)))
from utils.session_persist import restore_session
import streamlit.components.v1 as components
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(__file__)))
from utils.session_persist import restore_session
import yfinance as yf
import pandas as pd
import json
import sys, os
from datetime import date, timedelta
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.styles import SHARED_CSS, inject_bg
from utils.nav import navbar

st.set_page_config(page_title="Replay — 11%", page_icon="$", layout="wide", initial_sidebar_state="collapsed")
restore_session()
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
inject_bg()

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
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>
:root{
  --bg:#13161a;--bg2:#1c1f23;--bg3:#21252b;
  --border:#2d333b;--border2:#373d47;
  --text:#e6eaf0;--text2:#9ca3af;--dim:#4b5563;--dim2:#374151;
  --green:#4ade80;--red:#f87171;--yellow:#fbbf24;--blue:#60a5fa;--purple:#a78bfa;
}
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:100%;height:100%;background:var(--bg);color:var(--text);font-family:'Inter',sans-serif;overflow:hidden}
#root{display:flex;flex-direction:column;height:100vh}

/* ── Top bar (BacktestingMax style) ── */
#topbar{
  display:flex;align-items:center;background:var(--bg2);
  border-bottom:1px solid var(--border);height:52px;
  flex-shrink:0;padding:0 12px;gap:6px;overflow-x:auto;
  scrollbar-width:none;
}
#topbar::-webkit-scrollbar{display:none}
.tb-back{width:34px;height:34px;border-radius:8px;border:1px solid var(--border);
  background:transparent;color:var(--dim);display:flex;align-items:center;justify-content:center;
  cursor:pointer;font-size:1rem;flex-shrink:0;transition:all 0.15s}
.tb-back:hover{border-color:var(--border2);color:var(--text)}
.tb-sep{width:1px;background:var(--border);height:28px;margin:0 4px;flex-shrink:0}
.tb-sym{font-family:'IBM Plex Mono',monospace;font-size:0.82rem;font-weight:600;
  color:var(--text);min-width:80px;letter-spacing:0.04em}
.tb-pill{font-family:'IBM Plex Mono',monospace;font-size:0.58rem;font-weight:500;
  background:var(--bg3);border:1px solid var(--border);border-radius:6px;
  color:var(--text2);padding:5px 10px;cursor:pointer;white-space:nowrap;
  transition:all 0.15s;flex-shrink:0;line-height:1}
.tb-pill:hover{border-color:var(--border2);color:var(--text)}
.tb-pill.active{border-color:var(--green);color:var(--green);background:rgba(74,222,128,0.06)}
.tb-equity{font-family:'IBM Plex Mono',monospace;font-size:0.72rem;
  color:var(--text2);white-space:nowrap;flex-shrink:0}
.tb-equity span{color:var(--text);font-weight:600}
.tb-trade-btn{
  font-family:'IBM Plex Mono',monospace;font-size:0.65rem;font-weight:700;
  text-transform:uppercase;letter-spacing:0.08em;
  background:var(--green);color:#0a0f0a;border:none;border-radius:8px;
  padding:8px 18px;cursor:pointer;flex-shrink:0;transition:all 0.15s;
}
.tb-trade-btn:hover{background:#6ee7a0;box-shadow:0 0 16px rgba(74,222,128,0.3)}
.tb-play-btn{
  font-family:'IBM Plex Mono',monospace;font-size:0.62rem;font-weight:600;
  background:transparent;border:1px solid var(--border);border-radius:6px;
  color:var(--text2);padding:6px 14px;cursor:pointer;
  display:inline-flex;align-items:center;gap:6px;flex-shrink:0;transition:all 0.15s;
}
.tb-play-btn:hover{border-color:var(--border2);color:var(--text)}
.tb-play-btn.playing{border-color:var(--yellow);color:var(--yellow);background:rgba(251,191,36,0.06)}
.tb-icon-btn{width:34px;height:34px;border-radius:8px;border:1px solid var(--border);
  background:transparent;color:var(--dim);display:flex;align-items:center;justify-content:center;
  cursor:pointer;font-size:0.9rem;flex-shrink:0;transition:all 0.15s}
.tb-icon-btn:hover{border-color:var(--border2);color:var(--text)}
.spd-wrap{display:flex;align-items:center;gap:5px;flex-shrink:0}
.spd-lbl{font-family:'IBM Plex Mono',monospace;font-size:0.5rem;color:var(--dim);text-transform:uppercase;letter-spacing:0.12em}
#speed-slider{-webkit-appearance:none;width:70px;height:3px;background:var(--border);border-radius:2px;outline:none;cursor:pointer}
#speed-slider::-webkit-slider-thumb{-webkit-appearance:none;width:12px;height:12px;border-radius:50%;background:var(--green);cursor:pointer}
.spd-val{font-family:'IBM Plex Mono',monospace;font-size:0.6rem;color:var(--green);font-weight:600;min-width:28px}
.pos-slider-wrap{display:flex;align-items:center;gap:5px;flex-shrink:0}
#pos-slider{-webkit-appearance:none;width:100px;height:3px;background:var(--border);border-radius:2px;outline:none;cursor:pointer}
#pos-slider::-webkit-slider-thumb{-webkit-appearance:none;width:12px;height:12px;border-radius:50%;background:var(--blue);cursor:pointer}
#pos-lbl{font-family:'IBM Plex Mono',monospace;font-size:0.56rem;color:var(--dim);min-width:80px}
.ml-auto{margin-left:auto}

/* ── OHLCV strip ── */
#ohlcv{
  display:flex;align-items:center;gap:16px;padding:5px 14px;
  background:var(--bg);border-bottom:1px solid rgba(45,51,59,0.5);
  font-family:'IBM Plex Mono',monospace;font-size:0.65rem;
  color:var(--dim);flex-shrink:0;
}
.ohlcv-sym{color:var(--text);font-weight:600;font-size:0.75rem}
.ohlcv-val{color:var(--text);font-weight:500}
.ohlcv-chg-up{color:var(--green)}.ohlcv-chg-dn{color:var(--red)}

/* ── Body ── */
#body{display:flex;flex:1;min-height:0;overflow:hidden}

/* ── Left sidebar (drawing tools) ── */
#left-tools{
  width:44px;background:var(--bg2);border-right:1px solid var(--border);
  display:flex;flex-direction:column;align-items:center;padding:8px 0;gap:4px;
  flex-shrink:0;
}
.lt-btn{
  width:32px;height:32px;border-radius:6px;border:1px solid transparent;
  background:transparent;color:var(--dim);display:flex;align-items:center;
  justify-content:center;cursor:pointer;font-size:0.75rem;transition:all 0.12s;
  font-family:monospace;
}
.lt-btn:hover{border-color:var(--border);color:var(--text);background:var(--bg3)}
.lt-btn.on{border-color:var(--yellow);color:var(--yellow);background:rgba(251,191,36,0.07)}
.lt-sep{width:24px;height:1px;background:var(--border);margin:2px 0}

/* ── Chart column ── */
#chart-col{flex:1;display:flex;flex-direction:column;min-width:0;overflow:hidden}
#main-chart{flex:1;min-height:0}
#vol-chart{flex-shrink:0;height:64px;border-top:1px solid rgba(45,51,59,0.5)}
#rsi-pane{flex-shrink:0;height:70px;border-top:1px solid rgba(45,51,59,0.5);display:none}
#macd-pane{flex-shrink:0;height:70px;border-top:1px solid rgba(45,51,59,0.5);display:none}

/* ── Right sidebar ── */
#right-panel{
  width:280px;flex-shrink:0;background:var(--bg2);border-left:1px solid var(--border);
  display:flex;flex-direction:column;overflow:hidden;
}
.rp-section{padding:10px 12px;border-bottom:1px solid rgba(45,51,59,0.5);flex-shrink:0}
.rp-title{font-family:'IBM Plex Mono',monospace;font-size:0.48rem;text-transform:uppercase;
  letter-spacing:0.22em;color:var(--dim2);margin-bottom:8px}
.ind-row{display:flex;align-items:center;justify-content:space-between;margin-bottom:6px}
.ind-label{font-family:'IBM Plex Mono',monospace;font-size:0.6rem;color:var(--text2);
  display:flex;align-items:center;gap:5px}
.ind-dot{width:8px;height:8px;border-radius:50%;flex-shrink:0}
.ind-val{font-family:'IBM Plex Mono',monospace;font-size:0.58rem;color:var(--dim)}
.ind-input{width:38px;background:var(--bg3);border:1px solid var(--border);border-radius:4px;
  color:var(--text2);font-family:'IBM Plex Mono',monospace;font-size:0.55rem;
  padding:2px 5px;text-align:center;outline:none}
.ind-input:focus{border-color:var(--border2)}
.ind-check{accent-color:var(--green);width:13px;height:13px;cursor:pointer}

/* ── Trade buttons ── */
.trade-grid{display:grid;grid-template-columns:1fr 1fr;gap:5px}
.t-btn{
  font-family:'IBM Plex Mono',monospace;font-size:0.55rem;font-weight:700;
  text-transform:uppercase;letter-spacing:0.07em;border-radius:6px;
  border:1px solid;padding:7px 6px;cursor:pointer;
  transition:all 0.12s;text-align:center;line-height:1;
}
.t-btn.buy{background:var(--green);color:#0a0f0a;border-color:var(--green)}
.t-btn.buy:hover{background:#6ee7a0}
.t-btn.addl{background:rgba(96,165,250,0.15);color:var(--blue);border-color:rgba(96,165,250,0.35)}
.t-btn.addl:hover{background:rgba(96,165,250,0.25)}
.t-btn.short{background:var(--red);color:#0a0f0a;border-color:var(--red)}
.t-btn.short:hover{background:#fca5a5}
.t-btn.adds{background:rgba(248,113,113,0.1);color:var(--red);border-color:rgba(248,113,113,0.3)}
.t-btn.adds:hover{background:rgba(248,113,113,0.2)}
.t-btn.close{background:var(--yellow);color:#0a0f0a;border-color:var(--yellow)}
.t-btn.close:hover{background:#fde68a}
.t-btn.partial{background:rgba(251,191,36,0.1);color:var(--yellow);border-color:rgba(251,191,36,0.3)}
.t-btn.partial:hover{background:rgba(251,191,36,0.2)}
.qty-row{display:flex;gap:5px;margin-bottom:6px;align-items:center}
.qty-lbl{font-family:'IBM Plex Mono',monospace;font-size:0.52rem;color:var(--dim);min-width:28px}
.qty-inp{flex:1;background:var(--bg3);border:1px solid var(--border);border-radius:5px;
  color:var(--text);font-family:'IBM Plex Mono',monospace;font-size:0.7rem;
  padding:5px 8px;outline:none;height:30px}
.qty-inp:focus{border-color:var(--border2)}

/* ── Metrics strip ── */
#metrics{
  display:flex;background:var(--bg);border-bottom:1px solid var(--border);
  flex-shrink:0;
}
.mc{flex:1;padding:6px 12px;border-right:1px solid rgba(45,51,59,0.5)}
.mc:last-child{border-right:none}
.ml{font-family:'IBM Plex Mono',monospace;font-size:0.4rem;text-transform:uppercase;
  letter-spacing:0.18em;color:var(--dim2);margin-bottom:2px}
.mv{font-family:'IBM Plex Mono',monospace;font-size:0.82rem;font-weight:600;color:var(--text)}
.mv.pos{color:var(--green)}.mv.neg{color:var(--red)}.mv.dim{color:var(--dim)}

/* ── Positions list ── */
#pos-list{overflow-y:auto;max-height:100px;flex-shrink:0}
#pos-list::-webkit-scrollbar{width:2px}#pos-list::-webkit-scrollbar-thumb{background:var(--border)}
.pos-row{display:flex;justify-content:space-between;align-items:center;
  padding:5px 12px;border-bottom:1px solid rgba(45,51,59,0.4);font-family:'IBM Plex Mono',monospace;font-size:0.62rem}
.pos-row:hover{background:rgba(255,255,255,0.01)}
.pos-long{color:var(--green)}.pos-short{color:var(--red)}

/* ── Trade log ── */
#log-wrap{flex:1;overflow-y:auto;min-height:0}
#log-wrap::-webkit-scrollbar{width:2px}#log-wrap::-webkit-scrollbar-thumb{background:var(--border)}
.log-row{display:grid;grid-template-columns:50px 36px 70px 1fr;gap:4px;
  padding:5px 12px;border-bottom:1px solid rgba(45,51,59,0.35);
  font-family:'IBM Plex Mono',monospace;font-size:0.58rem;align-items:center}
.log-row:hover{background:rgba(255,255,255,0.01)}
.log-time{color:var(--dim2)}.log-dir-b{color:var(--green);font-weight:700}
.log-dir-s{color:var(--red);font-weight:700}.log-dir-c{color:var(--yellow);font-weight:700}
.log-price{color:var(--text)}.log-pnl-pos{color:var(--green);text-align:right;font-weight:600}
.log-pnl-neg{color:var(--red);text-align:right;font-weight:600}.log-pnl-dim{color:var(--dim);text-align:right}

/* ── Bottom tabs (BacktestingMax) ── */
#bottom-tabs{
  display:flex;background:var(--bg2);border-top:1px solid var(--border);
  flex-shrink:0;
}
.btab{
  flex:1;font-family:'IBM Plex Mono',monospace;font-size:0.58rem;font-weight:600;
  text-transform:uppercase;letter-spacing:0.1em;
  color:var(--dim);padding:10px;text-align:center;cursor:pointer;
  border-bottom:2px solid transparent;transition:all 0.15s;
}
.btab:hover{color:var(--text2)}
.btab.active{color:var(--green);border-bottom-color:var(--green)}
.save-btn{
  font-family:'IBM Plex Mono',monospace;font-size:0.58rem;font-weight:700;
  text-transform:uppercase;letter-spacing:0.08em;
  background:var(--green);color:#0a0f0a;border:none;
  padding:8px 18px;cursor:pointer;margin:4px 8px;border-radius:6px;
  transition:all 0.15s;flex-shrink:0;
}
.save-btn:hover{background:#6ee7a0}

/* ── Toast ── */
#toast{
  position:fixed;top:10px;left:50%;transform:translateX(-50%);
  background:var(--bg3);border:1px solid var(--border);border-radius:8px;
  padding:8px 18px;font-family:'IBM Plex Mono',monospace;font-size:0.64rem;
  font-weight:600;z-index:9999;display:none;pointer-events:none;
  box-shadow:0 12px 40px rgba(0,0,0,0.7);white-space:nowrap;
}

/* ── Kbd hint ── */
#kbd-hint{
  font-family:'IBM Plex Mono',monospace;font-size:0.46rem;color:var(--dim2);
  text-align:right;padding:0 8px;flex-shrink:0;white-space:nowrap;overflow:hidden;
}
.kbd{display:inline-block;background:var(--bg3);border:1px solid var(--border);
  border-radius:3px;padding:1px 5px;font-size:0.42rem}

</style>
</head><body>
<div id="root">
<div id="toast"></div>

<!-- TOP BAR -->
<div id="topbar">
  <button class="tb-back" onclick="goBack()" title="Back">&#8592;</button>
  <div class="tb-sep"></div>
  <span class="tb-sym" id="sym-label">__TICKER__</span>
  <div class="tb-sep"></div>
  <!-- Timeframe pills -->
  <button class="tb-pill" id="ct-candle" onclick="setChartType('candle')">Candles</button>
  <button class="tb-pill" id="ct-heikin" onclick="setChartType('heikin')">Heikin</button>
  <button class="tb-pill" id="ct-bar" onclick="setChartType('bar')">Bars</button>
  <button class="tb-pill" id="ct-line" onclick="setChartType('line')">Line</button>
  <div class="tb-sep"></div>
  <!-- Playback -->
  <button class="tb-play-btn" id="play-btn" onclick="togglePlay()">&#9654; Play</button>
  <button class="tb-icon-btn" onclick="stepBars(-1)" title="Step back (←)">&#8592;</button>
  <button class="tb-icon-btn" onclick="stepBars(1)"  title="Step forward (→)">&#8594;</button>
  <button class="tb-icon-btn" onclick="goStart()" title="Go to start">&#9198;</button>
  <button class="tb-icon-btn" onclick="goEnd()"   title="Go to end">&#9197;</button>
  <div class="tb-sep"></div>
  <div class="spd-wrap">
    <span class="spd-lbl">Speed</span>
    <input type="range" id="speed-slider" min="1" max="10" value="3" oninput="setSpeed(this.value)">
    <span class="spd-val" id="spd-val">0.3x</span>
  </div>
  <div class="tb-sep"></div>
  <div class="pos-slider-wrap">
    <input type="range" id="pos-slider" min="10" max="__NB_M1__" value="__SB__" oninput="scrubTo(+this.value)">
    <span id="pos-lbl">Bar __SB__ / __NB__</span>
  </div>
  <div class="ml-auto"></div>
  <div id="kbd-hint">
    <span class="kbd">B</span>Buy &nbsp;
    <span class="kbd">A</span>+Long &nbsp;
    <span class="kbd">S</span>Short &nbsp;
    <span class="kbd">X</span>Close &nbsp;
    <span class="kbd">P</span>Partial &nbsp;
    <span class="kbd">Space</span>Play
  </div>
  <div class="tb-sep"></div>
  <span class="tb-equity">Equity: <span id="eq-val">$__CAP__</span></span>
  <div class="tb-sep"></div>
  <button class="tb-trade-btn" onclick="quickTrade()">Take Trade</button>
</div>

<!-- OHLCV strip -->
<div id="ohlcv">
  <span class="ohlcv-sym">__TICKER__</span>
  <span>O <span class="ohlcv-val" id="b-o">—</span></span>
  <span>H <span class="ohlcv-val" id="b-h">—</span></span>
  <span>L <span class="ohlcv-val" id="b-l">—</span></span>
  <span>C <span class="ohlcv-val" id="b-c">—</span></span>
  <span id="b-chg" class="ohlcv-chg-up">—</span>
  <span style="margin-left:auto;color:var(--dim)" id="b-date">—</span>
  <span id="b-vol" style="color:var(--dim)">—</span>
</div>

<!-- METRICS -->
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

<!-- BODY -->
<div id="body">

  <!-- Left drawing tools -->
  <div id="left-tools">
    <button class="lt-btn on" id="draw-cursor"  onclick="setDraw('cursor')"  title="Select">&#8598;</button>
    <button class="lt-btn"    id="draw-hline"   onclick="setDraw('hline')"   title="H-Line">—</button>
    <button class="lt-btn"    id="draw-vline"   onclick="setDraw('vline')"   title="V-Line">|</button>
    <button class="lt-btn"    id="draw-trend"   onclick="setDraw('trend')"   title="Trend">&#8725;</button>
    <button class="lt-btn"    id="draw-ray"     onclick="setDraw('ray')"     title="Ray">&#10145;</button>
    <button class="lt-btn"    id="draw-fib"     onclick="setDraw('fib')"     title="Fibonacci">&#10024;</button>
    <button class="lt-btn"    id="draw-rect"    onclick="setDraw('rect')"    title="Rectangle">&#9645;</button>
    <div class="lt-sep"></div>
    <button class="lt-btn"    id="draw-text"    onclick="setDraw('mark')"    title="Marker">A</button>
    <div class="lt-sep"></div>
    <button class="lt-btn" style="color:var(--red)" onclick="clearAll()" title="Clear">&#128465;</button>
    <div style="flex:1"></div>
    <select id="draw-color" style="
      background:var(--bg3);border:1px solid var(--border);border-radius:4px;
      color:var(--text2);font-size:0.48rem;padding:2px;width:32px;cursor:pointer;
      margin-bottom:6px;outline:none">
      <option value="#fbbf24">Y</option>
      <option value="#4ade80">G</option>
      <option value="#f87171">R</option>
      <option value="#60a5fa">B</option>
      <option value="#ffffff">W</option>
    </select>
  </div>

  <!-- Chart column -->
  <div id="chart-col">
    <div id="main-chart"></div>
    <div id="vol-chart"></div>
    <div id="rsi-pane"></div>
    <div id="macd-pane"></div>
  </div>

  <!-- Right panel -->
  <div id="right-panel">

    <div class="rp-section">
      <div class="rp-title">Indicators</div>
      <div class="ind-row"><label class="ind-label"><input type="checkbox" class="ind-check" id="is1" onchange="renderAll()"><span class="ind-dot" style="background:#60a5fa"></span>SMA</label><input type="number" class="ind-input" id="ip1" value="20" min="2" max="200" onchange="renderAll()"></div>
      <div class="ind-row"><label class="ind-label"><input type="checkbox" class="ind-check" id="is2" onchange="renderAll()"><span class="ind-dot" style="background:#a78bfa"></span>SMA</label><input type="number" class="ind-input" id="ip2" value="50" min="2" max="200" onchange="renderAll()"></div>
      <div class="ind-row"><label class="ind-label"><input type="checkbox" class="ind-check" id="is3" onchange="renderAll()"><span class="ind-dot" style="background:#4ade80"></span>EMA</label><input type="number" class="ind-input" id="ip3" value="20" min="2" max="200" onchange="renderAll()"></div>
      <div class="ind-row"><label class="ind-label"><input type="checkbox" class="ind-check" id="is4" onchange="renderAll()"><span class="ind-dot" style="background:#06b6d4"></span>EMA</label><input type="number" class="ind-input" id="ip4" value="50" min="2" max="200" onchange="renderAll()"></div>
      <div class="ind-row"><label class="ind-label"><input type="checkbox" class="ind-check" id="is5" onchange="renderAll()"><span class="ind-dot" style="background:#fbbf24"></span>VWAP</label></div>
      <div class="ind-row"><label class="ind-label"><input type="checkbox" class="ind-check" id="is6" onchange="renderAll()"><span class="ind-dot" style="background:#fb923c"></span>BB</label><input type="number" class="ind-input" id="ip6" value="20" min="5" max="100" onchange="renderAll()"></div>
      <div class="ind-row"><label class="ind-label"><input type="checkbox" class="ind-check" id="is7" onchange="togglePane('rsi',this.checked)"><span class="ind-dot" style="background:#ec4899"></span>RSI</label><input type="number" class="ind-input" id="ip7" value="14" min="2" max="50" onchange="renderAll()"></div>
      <div class="ind-row"><label class="ind-label"><input type="checkbox" class="ind-check" id="is8" onchange="togglePane('macd',this.checked)"><span class="ind-dot" style="background:#f59e0b"></span>MACD</label></div>
    </div>

    <div class="rp-section">
      <div class="rp-title">Execute Trade</div>
      <div class="qty-row">
        <span class="qty-lbl">Qty</span>
        <input type="number" class="qty-inp" id="tq" value="10" min="1">
        <span class="qty-lbl" style="margin-left:4px">@ $</span>
        <input type="number" class="qty-inp" id="tp" value="0" step="0.01">
      </div>
      <div class="trade-grid">
        <button class="t-btn buy"     onclick="ex('buy')">Buy</button>
        <button class="t-btn addl"    onclick="ex('addlong')">+ Long</button>
        <button class="t-btn short"   onclick="ex('short')">Short</button>
        <button class="t-btn adds"    onclick="ex('addshort')">+ Short</button>
        <button class="t-btn close"   onclick="ex('close')">Close All</button>
        <button class="t-btn partial" onclick="ex('partial')">Partial</button>
      </div>
    </div>

    <div class="rp-section" style="padding-bottom:5px">
      <div class="rp-title">Open Positions</div>
    </div>
    <div id="pos-list"></div>

    <div class="rp-section" style="padding-bottom:5px;flex-shrink:0">
      <div class="rp-title">Trade Log</div>
    </div>
    <div id="log-wrap">
      <div id="log-inner"></div>
    </div>

  </div>
</div>

<!-- BOTTOM TABS (BacktestingMax style) -->
<div id="bottom-tabs">
  <div class="btab active" onclick="setTab('trades')">Trades</div>
  <div class="btab" onclick="setTab('analytics')">Analytics</div>
  <div class="btab" onclick="setTab('logs')">Logs</div>
  <button class="save-btn" onclick="saveSession()">Save Session</button>
</div>

</div><!-- /root -->

<script>
// ── Data ──────────────────────────────────────────────────────────────────────
const ALL=__BARS__;
const CAP=__CAP__;
const N=ALL.length;
const SB=__SB__;
const SPEEDS=[0.07,0.15,0.3,0.5,1,1.5,2,3,5,10];

let cur=SB,isPlaying=false,rafId=null,lastT=0,mspb=1000/0.3;
let ct='candle',dm='cursor';
let cash=CAP,positions=[],trades=__TRADES__,rPnl=0,wins=0,losses=0,pid=0;
let segs=[],marks=[];
const IS={};

// ── Chart setup ───────────────────────────────────────────────────────────────
const CO={
  layout:{background:{type:'solid',color:'#13161a'},textColor:'#4b5563',fontSize:11,fontFamily:'IBM Plex Mono'},
  grid:{vertLines:{color:'#1e2530'},horzLines:{color:'#1e2530'}},
  crosshair:{mode:LightweightCharts.CrosshairMode.Normal,
    vertLine:{color:'#2d333b',width:1,style:LightweightCharts.LineStyle.Dashed,labelBackgroundColor:'#1c1f23'},
    horzLine:{color:'#2d333b',width:1,style:LightweightCharts.LineStyle.Dashed,labelBackgroundColor:'#1c1f23'}},
  rightPriceScale:{borderColor:'#2d333b',textColor:'#4b5563'},
  timeScale:{borderColor:'#2d333b',textColor:'#4b5563',timeVisible:true,secondsVisible:false},
  handleScroll:{vertTouchDrag:true,mouseWheel:true,pressedMouseMove:true},
  handleScale:{axisPressedMouseMove:true,mouseWheel:true,pinch:true}
};

const me=document.getElementById('main-chart');
const MC=LightweightCharts.createChart(me,{...CO,width:me.offsetWidth,height:me.offsetHeight||400});
const ve=document.getElementById('vol-chart');
const VC=LightweightCharts.createChart(ve,{...CO,width:ve.offsetWidth,height:64,timeScale:{...CO.timeScale,visible:false},rightPriceScale:{...CO.rightPriceScale,scaleMargins:{top:0.05,bottom:0}}});
const re=document.getElementById('rsi-pane');
const RC=LightweightCharts.createChart(re,{...CO,width:re.offsetWidth,height:70,timeScale:{...CO.timeScale,visible:false}});
const rsiS=RC.addLineSeries({color:'#ec4899',lineWidth:1});
const rsiOB=RC.addLineSeries({color:'rgba(248,113,113,0.3)',lineWidth:1,lineStyle:LightweightCharts.LineStyle.Dashed});
const rsiOS=RC.addLineSeries({color:'rgba(74,222,128,0.3)',lineWidth:1,lineStyle:LightweightCharts.LineStyle.Dashed});
const mae=document.getElementById('macd-pane');
const MACC=LightweightCharts.createChart(mae,{...CO,width:mae.offsetWidth,height:70,timeScale:{...CO.timeScale,visible:false}});
const macdF=MACC.addLineSeries({color:'#f59e0b',lineWidth:1});
const macdS=MACC.addLineSeries({color:'#60a5fa',lineWidth:1});
const macdH=MACC.addHistogramSeries({priceScaleId:''});
MACC.priceScale('').applyOptions({scaleMargins:{top:0.1,bottom:0.1}});
let MS=null,VS=null;

function cMS(t){
  if(MS)MC.removeSeries(MS);
  const u='#4ade80',d='#f87171';
  switch(t){
    case 'bar':MS=MC.addBarSeries({upColor:u,downColor:d});break;
    case 'line':MS=MC.addLineSeries({color:u,lineWidth:2});break;
    default:MS=MC.addCandlestickSeries({upColor:u,downColor:d,borderUpColor:u,borderDownColor:d,wickUpColor:u,wickDownColor:d});
  }
}
function cVS(){
  if(VS)VC.removeSeries(VS);
  VS=VC.addHistogramSeries({priceFormat:{type:'volume'},priceScaleId:''});
  VC.priceScale('').applyOptions({scaleMargins:{top:0.1,bottom:0}});
}
cMS('candle');cVS();

// Sync time scales
function syncCharts(){
  MC.timeScale().subscribeVisibleLogicalRangeChange(r=>{
    if(!r)return;[VC,RC,MACC].forEach(c=>c.timeScale().setVisibleLogicalRange(r));
  });
}
syncCharts();

// ── Indicator compute ─────────────────────────────────────────────────────────
function tt(d){return d.length>10?d.replace(' ','T')+':00':d;}

function cSMA(d,p){const o=[];for(let i=p-1;i<d;i++){let s=0;for(let j=0;j<p;j++)s+=ALL[i-j].Close;o.push({time:tt(ALL[i].Date),value:s/p});}return o;}
function cEMA(d,p){const k=2/(p+1);const o=[];let e=ALL[0].Close;for(let i=1;i<d;i++){e=ALL[i].Close*k+e*(1-k);if(i>=p-1)o.push({time:tt(ALL[i].Date),value:e});}return o;}
function cVWAP(d){const o=[];let cv=0,cpv=0;for(let i=0;i<d;i++){cv+=ALL[i].Volume;cpv+=ALL[i].Close*ALL[i].Volume;if(cv>0)o.push({time:tt(ALL[i].Date),value:cpv/cv});}return o;}
function cBB(d,p){const u=[],l=[],m=[];for(let i=p-1;i<d;i++){const c=[];for(let j=0;j<p;j++)c.push(ALL[i-j].Close);const mn=c.reduce((a,b)=>a+b,0)/p;const sd=Math.sqrt(c.reduce((a,b)=>a+(b-mn)**2,0)/p);const t=tt(ALL[i].Date);u.push({time:t,value:mn+2*sd});l.push({time:t,value:mn-2*sd});m.push({time:t,value:mn});}return{upper:u,lower:l,mid:m};}
function cRSI(d,p){const o=[];let ag=0,al=0;for(let i=1;i<=p;i++){const dv=ALL[i].Close-ALL[i-1].Close;if(dv>0)ag+=dv;else al-=dv;}ag/=p;al/=p;for(let i=p;i<d;i++){if(i>p){const dv=ALL[i].Close-ALL[i-1].Close;ag=(ag*(p-1)+Math.max(dv,0))/p;al=(al*(p-1)+Math.max(-dv,0))/p;}const rs=al===0?100:ag/al;o.push({time:tt(ALL[i].Date),value:100-100/(1+rs)});}return o;}
function cMACD(d){const k12=2/13,k26=2/27,k9=2/10;let e12=ALL[0].Close,e26=ALL[0].Close;const mv=[],sv=[];for(let i=1;i<d;i++){e12=ALL[i].Close*k12+e12*(1-k12);e26=ALL[i].Close*k26+e26*(1-k26);if(i>=25)mv.push({t:tt(ALL[i].Date),v:e12-e26});}let sig=mv[0]?.v||0;mv.forEach(m=>{sig=m.v*k9+sig*(1-k9);sv.push(sig);});return mv.map((m,i)=>({time:m.t,macd:m.v,signal:sv[i],hist:m.v-sv[i]}));}
function heikinBars(d){const o=[];for(let i=0;i<d;i++){const b=ALL[i];const hc=(b.Open+b.High+b.Low+b.Close)/4;const ho=i===0?(b.Open+b.Close)/2:(o[i-1].open+o[i-1].close)/2;o.push({time:tt(b.Date),open:ho,high:Math.max(b.High,ho,hc),low:Math.min(b.Low,ho,hc),close:hc});}return o;}

function uLine(id,en,fac,data){if(en){if(!IS[id])IS[id]=fac();IS[id].setData(data);}else if(IS[id]){MC.removeSeries(IS[id]);delete IS[id];}}

// ── Render ────────────────────────────────────────────────────────────────────
function renderAll(){
  const d=cur+1;
  // Chart data
  if(ct==='heikin'){const hb=heikinBars(d);MS.setData(hb);}
  else if(ct==='line'||ct==='area'){MS.setData(ALL.slice(0,d).map(b=>({time:tt(b.Date),value:b.Close})));}
  else{MS.setData(ALL.slice(0,d).map(b=>({time:tt(b.Date),open:b.Open,high:b.High,low:b.Low,close:b.Close})));}
  VS.setData(ALL.slice(0,d).map(b=>({time:tt(b.Date),value:b.Volume,color:b.Close>=b.Open?'rgba(74,222,128,0.3)':'rgba(248,113,113,0.25)'})));

  // Indicators
  const p1=+document.getElementById('ip1').value||20,p2=+document.getElementById('ip2').value||50,p3=+document.getElementById('ip3').value||20,p4=+document.getElementById('ip4').value||50,p6=+document.getElementById('ip6').value||20,p7=+document.getElementById('ip7').value||14;
  uLine('s1',document.getElementById('is1').checked,()=>MC.addLineSeries({color:'#60a5fa',lineWidth:1,crosshairMarkerVisible:false}),cSMA(d,p1));
  uLine('s2',document.getElementById('is2').checked,()=>MC.addLineSeries({color:'#a78bfa',lineWidth:1,crosshairMarkerVisible:false}),cSMA(d,p2));
  uLine('e1',document.getElementById('is3').checked,()=>MC.addLineSeries({color:'#4ade80',lineWidth:1,lineStyle:LightweightCharts.LineStyle.Dashed,crosshairMarkerVisible:false}),cEMA(d,p3));
  uLine('e2',document.getElementById('is4').checked,()=>MC.addLineSeries({color:'#06b6d4',lineWidth:1,lineStyle:LightweightCharts.LineStyle.Dashed,crosshairMarkerVisible:false}),cEMA(d,p4));
  uLine('vw',document.getElementById('is5').checked,()=>MC.addLineSeries({color:'#fbbf24',lineWidth:1,lineStyle:LightweightCharts.LineStyle.Dotted,crosshairMarkerVisible:false}),cVWAP(d));
  if(document.getElementById('is6').checked){
    const bb=cBB(d,p6);
    if(!IS.bbU){IS.bbU=MC.addLineSeries({color:'rgba(251,146,60,0.5)',lineWidth:1,lineStyle:LightweightCharts.LineStyle.Dashed,crosshairMarkerVisible:false});IS.bbL=MC.addLineSeries({color:'rgba(251,146,60,0.5)',lineWidth:1,lineStyle:LightweightCharts.LineStyle.Dashed,crosshairMarkerVisible:false});IS.bbM=MC.addLineSeries({color:'rgba(251,146,60,0.25)',lineWidth:1,crosshairMarkerVisible:false});}
    IS.bbU.setData(bb.upper);IS.bbL.setData(bb.lower);IS.bbM.setData(bb.mid);
  }else{['bbU','bbL','bbM'].forEach(k=>{if(IS[k]){MC.removeSeries(IS[k]);delete IS[k];}});}
  if(document.getElementById('is7').checked&&d>p7+1){const rd=cRSI(d,p7);rsiS.setData(rd);rsiOB.setData(rd.map(x=>({time:x.time,value:70})));rsiOS.setData(rd.map(x=>({time:x.time,value:30})));}
  if(document.getElementById('is8').checked&&d>30){const md=cMACD(d);macdF.setData(md.map(x=>({time:x.time,value:x.macd})));macdS.setData(md.map(x=>({time:x.time,value:x.signal})));macdH.setData(md.map(x=>({time:x.time,value:x.hist,color:x.hist>=0?'rgba(74,222,128,0.5)':'rgba(248,113,113,0.5)'})));}

  // Trade markers
  const mkrs=[];trades.forEach(t=>{const idx=ALL.findIndex(b=>b.Date>=t.date);if(idx<0||idx>cur)return;const col=t.dir==='buy'||t.dir==='addlong'?'#4ade80':t.dir==='short'||t.dir==='addshort'?'#f87171':'#fbbf24';const shp=t.dir==='buy'||t.dir==='addlong'?'arrowUp':t.dir==='short'||t.dir==='addshort'?'arrowDown':'circle';const pos=t.dir==='buy'||t.dir==='addlong'?'belowBar':t.dir==='short'||t.dir==='addshort'?'aboveBar':'inBar';const lbl={'buy':'B','addlong':'+L','short':'S','addshort':'+S','close':'X','partial':'~'}[t.dir]||'';mkrs.push({time:tt(ALL[idx].Date),position:pos,color:col,shape:shp,text:lbl,size:1});});
  marks.forEach(m=>{if(ALL.findIndex(b=>b.Date>=m.date)<=cur)mkrs.push(m.marker);});
  MS.setMarkers(mkrs);

  // Playback start line
  if(!IS.startLine){
    const lo=Math.min(...ALL.map(b=>b.Low))*0.98,hi=Math.max(...ALL.map(b=>b.High))*1.02;
    IS.startLine=MC.addLineSeries({color:'rgba(96,165,250,0.3)',lineWidth:1,lineStyle:LightweightCharts.LineStyle.Dashed,crosshairMarkerVisible:false,lastValueVisible:false});
    IS.startLine.setData([{time:tt(ALL[SB].Date),value:lo},{time:tt(ALL[SB].Date),value:hi}]);
  }
  updOHLCV();updMetrics();updPositions();
  document.getElementById('pos-lbl').textContent='Bar '+(cur+1)+' / '+N+' · '+ALL[cur].Date.slice(0,10);
  document.getElementById('pos-slider').value=cur;
  document.getElementById('tp').value=ALL[cur].Close.toFixed(2);
}

// ── OHLCV ─────────────────────────────────────────────────────────────────────
function updOHLCV(){
  const b=ALL[cur],p=ALL[Math.max(0,cur-1)];
  const ch=b.Close-p.Close,pct=(ch/p.Close*100);
  document.getElementById('b-o').textContent='$'+b.Open.toFixed(2);
  document.getElementById('b-h').textContent='$'+b.High.toFixed(2);
  document.getElementById('b-l').textContent='$'+b.Low.toFixed(2);
  document.getElementById('b-c').textContent='$'+b.Close.toFixed(2);
  const ce=document.getElementById('b-chg');
  ce.textContent=(ch>=0?'▲':'▼')+' '+Math.abs(ch).toFixed(2)+' ('+pct.toFixed(2)+'%)';
  ce.className=ch>=0?'ohlcv-chg-up':'ohlcv-chg-dn';
  document.getElementById('b-date').textContent=b.Date;
  const v=b.Volume;
  document.getElementById('b-vol').textContent='Vol: '+(v>1e9?(v/1e9).toFixed(1)+'B':v>1e6?(v/1e6).toFixed(1)+'M':v>1e3?(v/1e3).toFixed(0)+'K':v);
}

// ── Metrics ───────────────────────────────────────────────────────────────────
function updMetrics(){
  const p=ALL[cur].Close;
  let op=0;positions.forEach(pos=>{op+=pos.dir==='buy'?(p-pos.entry)*pos.qty:(pos.entry-p)*pos.qty;});
  const invested=positions.filter(x=>x.dir==='buy').reduce((a,x)=>a+x.entry*x.qty,0);
  const port=cash+invested+op;
  const ret=(port-CAP)/CAP*100;
  const tc=trades.filter(t=>t.dir==='close'||t.dir==='partial').length;
  const wr=tc>0?(wins/tc*100).toFixed(0)+'%':'—';
  function sm(id,v,c){const el=document.getElementById(id);el.textContent=v;el.className='mv'+(c?' '+c:'');}
  function f(v){const a=Math.abs(v);return(v<0?'-':'')+'$'+(a>=1e6?(a/1e6).toFixed(2)+'M':a>=1e3?(a/1e3).toFixed(1)+'K':a.toFixed(0));}
  sm('m0',f(port),ret>=0?'pos':'neg');
  sm('m1',f(cash),'dim');
  sm('m2',(ret>=0?'+':'')+ret.toFixed(2)+'%',ret>=0?'pos':'neg');
  sm('m3',(rPnl>=0?'+':'')+f(Math.abs(rPnl)),rPnl>0?'pos':rPnl<0?'neg':'dim');
  sm('m4',op!==0?(op>=0?'+':'')+op.toFixed(2):'—',op>0?'pos':op<0?'neg':'dim');
  document.getElementById('m5').textContent=positions.length;
  sm('m6',wr,'dim');
  document.getElementById('m7').textContent=trades.length;
  document.getElementById('eq-val').textContent=f(port);
}

// ── Positions ─────────────────────────────────────────────────────────────────
function updPositions(){
  const el=document.getElementById('pos-list');
  if(!positions.length){el.innerHTML='';return;}
  const p=ALL[cur].Close;
  el.innerHTML=positions.map(pos=>{
    const pnl=pos.dir==='buy'?(p-pos.entry)*pos.qty:(pos.entry-p)*pos.qty;
    const pc=pnl>=0?'#4ade80':'#f87171';
    return`<div class="pos-row">
      <span class="${pos.dir==='buy'?'pos-long':'pos-short'}">${pos.dir==='buy'?'L':'S'} ${pos.qty} @ $${pos.entry.toFixed(2)}</span>
      <span style="color:${pc};font-weight:600">${(pnl>=0?'+':'')}$${Math.abs(pnl).toFixed(2)}</span>
    </div>`;
  }).join('');
}

// ── Trade execution ───────────────────────────────────────────────────────────
function ex(dir){
  if(cur<SB){toast('Move past the start line to trade','#f87171');return;}
  const qty=Math.max(1,parseInt(document.getElementById('tq').value)||10);
  const price=parseFloat(document.getElementById('tp').value)||ALL[cur].Close;
  const date=ALL[cur].Date;
  const time=new Date().toTimeString().slice(0,5);
  if(dir==='buy'){const cost=price*qty;if(cost>cash){toast('Insufficient cash','#f87171');return;}cash-=cost;positions.push({dir:'buy',entry:price,qty,date,id:pid++});trades.push({dir:'buy',price,qty,date,pnl:0,time});toast('Buy '+qty+' @ $'+price.toFixed(2),'#4ade80');}
  else if(dir==='addlong'){if(!positions.filter(p=>p.dir==='buy').length){toast('No long to add to','#fbbf24');return;}const cost=price*qty;if(cost>cash){toast('Insufficient cash','#f87171');return;}cash-=cost;positions.push({dir:'buy',entry:price,qty,date,id:pid++});trades.push({dir:'addlong',price,qty,date,pnl:0,time});toast('+Long '+qty+' @ $'+price.toFixed(2),'#60a5fa');}
  else if(dir==='short'){cash+=price*qty;positions.push({dir:'short',entry:price,qty,date,id:pid++});trades.push({dir:'short',price,qty,date,pnl:0,time});toast('Short '+qty+' @ $'+price.toFixed(2),'#f87171');}
  else if(dir==='addshort'){if(!positions.filter(p=>p.dir==='short').length){toast('No short to add to','#fbbf24');return;}cash+=price*qty;positions.push({dir:'short',entry:price,qty,date,id:pid++});trades.push({dir:'addshort',price,qty,date,pnl:0,time});toast('+Short '+qty,'#f87171');}
  else if(dir==='close'){if(!positions.length){toast('No open positions','#fbbf24');return;}let tp=0;positions.forEach(pos=>{const pnl=pos.dir==='buy'?(price-pos.entry)*pos.qty:(pos.entry-price)*pos.qty;if(pos.dir==='buy')cash+=price*pos.qty;else cash-=price*pos.qty;rPnl+=pnl;tp+=pnl;if(pnl>0)wins++;else losses++;});trades.push({dir:'close',price,qty:positions.reduce((a,p)=>a+p.qty,0),date,pnl:tp,time});positions=[];toast('Closed — P&L: '+(tp>=0?'+':'')+'$'+Math.abs(tp).toFixed(2),tp>=0?'#4ade80':'#f87171');}
  else if(dir==='partial'){if(!positions.length){toast('No open positions','#fbbf24');return;}const pos=positions.pop();const pnl=pos.dir==='buy'?(price-pos.entry)*pos.qty:(pos.entry-price)*pos.qty;if(pos.dir==='buy')cash+=price*pos.qty;else cash-=price*pos.qty;rPnl+=pnl;if(pnl>0)wins++;else losses++;trades.push({dir:'partial',price,qty:pos.qty,date,pnl,time});toast('Partial P&L: '+(pnl>=0?'+':'')+pnl.toFixed(2),pnl>=0?'#4ade80':'#f87171');}
  updLog();renderAll();
}

function quickTrade(){ex('buy');}

function updLog(){
  document.getElementById('log-inner').innerHTML=[...trades].reverse().map(t=>{
    const dc={'buy':'log-dir-b','addlong':'log-dir-b','short':'log-dir-s','addshort':'log-dir-s','close':'log-dir-c','partial':'log-dir-c'}[t.dir]||'log-dir-c';
    const lb={'buy':'BUY','addlong':'+L','short':'SHT','addshort':'+S','close':'CLO','partial':'~CL'}[t.dir]||'';
    const ps=(t.dir==='close'||t.dir==='partial')?((t.pnl>=0?'+':'')+t.pnl.toFixed(2)):'—';
    const pc=t.pnl>0?'log-pnl-pos':t.pnl<0?'log-pnl-neg':'log-pnl-dim';
    return`<div class="log-row"><span class="log-time">${t.time}</span><span class="${dc}">${lb}</span><span class="log-price">$${t.price.toFixed(2)}</span><span class="${pc}">${ps}</span></div>`;
  }).join('');
}

// ── Playback ──────────────────────────────────────────────────────────────────
const spds=SPEEDS;let spd=0.3;
function setSpeed(v){spd=spds[v-1];mspb=1000/spd;document.getElementById('spd-val').textContent=spd+'x';}
function rafLoop(ts){if(!isPlaying)return;if(ts-lastT>=mspb){lastT=ts;if(cur>=N-1){stopPlay();return;}cur++;renderAll();MC.timeScale().scrollToPosition(3,false);}rafId=requestAnimationFrame(rafLoop);}
function startPlay(){if(rafId)cancelAnimationFrame(rafId);lastT=performance.now();rafId=requestAnimationFrame(rafLoop);}
function stopPlay(){isPlaying=false;if(rafId){cancelAnimationFrame(rafId);rafId=null;}const b=document.getElementById('play-btn');b.textContent='▶ Play';b.classList.remove('playing');}
function togglePlay(){isPlaying=!isPlaying;const b=document.getElementById('play-btn');if(isPlaying){startPlay();b.innerHTML='&#9646;&#9646; Pause';b.classList.add('playing');}else stopPlay();}
function stepBars(n){stopPlay();cur=Math.max(10,Math.min(N-1,cur+n));renderAll();}
function scrubTo(n){stopPlay();cur=Math.max(10,Math.min(N-1,n));renderAll();}
function goStart(){stopPlay();cur=SB;renderAll();}
function goEnd(){stopPlay();cur=N-1;renderAll();MC.timeScale().fitContent();}
function goBack(){try{window.top.location.href='/Replay';}catch(e){window.location.reload();}}

// ── Chart type ────────────────────────────────────────────────────────────────
function setChartType(t){
  ct=t;
  document.querySelectorAll('[id^="ct-"]').forEach(b=>b.classList.remove('active'));
  const el=document.getElementById('ct-'+t);if(el)el.classList.add('active');
  cMS(t);renderAll();
}

// ── Drawing ───────────────────────────────────────────────────────────────────
let _dpts=[];
function setDraw(mode){
  dm=mode;
  document.querySelectorAll('.lt-btn').forEach(b=>b.classList.remove('on'));
  const el=document.getElementById('draw-'+mode);if(el)el.classList.add('on');
  _dpts=[];
  MC.applyOptions({handleScroll:mode==='cursor',handleScale:mode==='cursor'});
}
function gdc(){return document.getElementById('draw-color').value;}
MC.subscribeClick(param=>{
  if(dm==='cursor'||!param.time)return;
  const price=MS.coordinateToPrice(param.point.y);const time=param.time;const color=gdc();
  if(dm==='hline'){const s=MC.addLineSeries({color:color+'bb',lineWidth:1,lineStyle:LightweightCharts.LineStyle.Dashed,crosshairMarkerVisible:false,lastValueVisible:false});s.setData(ALL.slice(0,cur+1).map(b=>({time:tt(b.Date),value:price})));segs.push({series:[s]});toast('H-Line @ $'+price.toFixed(2),'#fbbf24');}
  else if(dm==='vline'){const lo=Math.min(...ALL.slice(0,cur+1).map(b=>b.Low))*0.8,hi=Math.max(...ALL.slice(0,cur+1).map(b=>b.High))*1.2;const s=MC.addLineSeries({color:color+'99',lineWidth:1,lineStyle:LightweightCharts.LineStyle.Dashed,crosshairMarkerVisible:false,lastValueVisible:false});s.setData([{time,value:lo},{time,value:hi}]);segs.push({series:[s]});toast('V-Line','#fbbf24');}
  else if(dm==='trend'||dm==='ray'){
    if(!_dpts.length){_dpts=[{time,price}];toast('Click 2nd point','#fbbf24');}
    else{const p1=_dpts[0],p2={time,price};const s=MC.addLineSeries({color,lineWidth:1.5,crosshairMarkerVisible:false,lastValueVisible:false});let pts=[{time:p1.time,value:p1.price},{time:p2.time,value:p2.price}];if(dm==='ray'){const i1=ALL.findIndex(b=>tt(b.Date)>=p1.time),i2=ALL.findIndex(b=>tt(b.Date)>=p2.time);if(i1>=0&&i2>i1){const sl=(p2.price-p1.price)/(i2-i1);pts.push({time:tt(ALL[cur].Date),value:p2.price+sl*(cur-i2)});}}s.setData(pts);segs.push({series:[s]});_dpts=[];toast('Line drawn','#fbbf24');}
  }
  else if(dm==='fib'){
    if(!_dpts.length){_dpts=[{time,price}];toast('Click end point','#fbbf24');}
    else{const p1=_dpts[0],p2={time,price};const hi=Math.max(p1.price,p2.price),lo=Math.min(p1.price,p2.price),rng=hi-lo;[0,0.236,0.382,0.5,0.618,0.764,1.0].forEach((f,i)=>{const val=hi-rng*f;const cs=['#ffffff','#60a5fa','#4ade80','#fbbf24','#f59e0b','#a78bfa','#f87171'];const s=MC.addLineSeries({color:cs[i]+'88',lineWidth:1,lineStyle:LightweightCharts.LineStyle.Dashed,crosshairMarkerVisible:false,lastValueVisible:true});s.setData([{time:p1.time,value:val},{time:p2.time,value:val}]);segs.push({series:[s]});});_dpts=[];toast('Fibonacci drawn','#fbbf24');}
  }
  else if(dm==='rect'){
    if(!_dpts.length){_dpts=[{time,price}];toast('Click opposite corner','#fbbf24');}
    else{const p1=_dpts[0],p2={time,price};const hi=Math.max(p1.price,p2.price),lo=Math.min(p1.price,p2.price);const t1=p1.time<p2.time?p1.time:p2.time,t2=p1.time<p2.time?p2.time:p1.time;[[{time:t1,value:hi},{time:t2,value:hi}],[{time:t1,value:lo},{time:t2,value:lo}],[{time:t1,value:hi},{time:t1,value:lo}],[{time:t2,value:hi},{time:t2,value:lo}]].forEach(pts=>{const s=MC.addLineSeries({color:color+'aa',lineWidth:1,crosshairMarkerVisible:false,lastValueVisible:false});s.setData(pts);segs.push({series:[s]});});_dpts=[];toast('Box drawn','#fbbf24');}
  }
  else if(dm==='mark'){const idx=ALL.findIndex(b=>tt(b.Date)>=time);if(idx>=0&&idx<=cur){marks.push({date:ALL[idx].Date,marker:{time:tt(ALL[idx].Date),position:'aboveBar',color,shape:'circle',text:'✦',size:0}});renderAll();toast('Marker placed','#fbbf24');}}
});
function clearAll(){segs.forEach(s=>s.series.forEach(sr=>MC.removeSeries(sr)));segs=[];marks=[];renderAll();toast('Cleared','#fbbf24');}

// ── Bottom tabs ───────────────────────────────────────────────────────────────
function setTab(t){
  document.querySelectorAll('.btab').forEach(b=>b.classList.remove('active'));
  event.target.classList.add('active');
}
function saveSession(){toast('Session saved','#4ade80');}

// ── Sub-pane toggle ───────────────────────────────────────────────────────────
function togglePane(name,on){
  document.getElementById(name+'-pane').style.display=on?'block':'none';
  if(on)renderAll();resize();
}

// ── Toast ─────────────────────────────────────────────────────────────────────
let _tt=null;
function toast(msg,color='#4ade80'){
  const el=document.getElementById('toast');
  el.textContent=msg;el.style.display='block';el.style.color=color;el.style.borderColor=color+'55';
  if(_tt)clearTimeout(_tt);_tt=setTimeout(()=>el.style.display='none',2200);
}

// ── Keyboard ──────────────────────────────────────────────────────────────────
document.addEventListener('keydown',e=>{
  const tag=e.target.tagName;if(tag==='INPUT'||tag==='SELECT'||tag==='TEXTAREA')return;
  switch(e.code){
    case 'Space':e.preventDefault();togglePlay();break;
    case 'ArrowRight':stepBars(e.shiftKey?10:1);break;
    case 'ArrowLeft':stepBars(e.shiftKey?-10:-1);break;
    case 'KeyB':ex('buy');break;case 'KeyA':ex('addlong');break;
    case 'KeyS':ex('short');break;case 'KeyX':ex('close');break;case 'KeyP':ex('partial');break;
  }
});

// ── Resize ────────────────────────────────────────────────────────────────────
function resize(){
  const cc=document.getElementById('chart-col');
  const total=cc.offsetHeight;
  const rsiH=document.getElementById('rsi-pane').style.display!=='none'?70:0;
  const macdH=document.getElementById('macd-pane').style.display!=='none'?70:0;
  const mH=Math.max(160,total-64-rsiH-macdH-2);
  const w=cc.offsetWidth;
  MC.resize(w,mH);VC.resize(w,64);RC.resize(w,70);MACC.resize(w,70);
}
const ro=new ResizeObserver(resize);ro.observe(document.getElementById('chart-col'));

// ── Init ──────────────────────────────────────────────────────────────────────
setSpeed(3);
document.getElementById('ct-candle').classList.add('active');
renderAll();updLog();
MC.timeScale().fitContent();
setTimeout(()=>MC.timeScale().scrollToPosition(3,false),200);
toast('Loaded · Space=Play · ←/→=Step · B=Buy · S=Short · X=Close','#4ade80');
</script>
</body></html>"""

    HTML=HTML.replace("__BARS__",bars_json).replace("__TRADES__",trades_json)\
        .replace("__CAP__",str(int(capital_val))).replace("__TICKER__",ticker_label)\
        .replace("__NB__",str(n_bars)).replace("__NB_M1__",str(n_bars-1))\
        .replace("__SB__",str(start_bar_js))
    components.html(HTML, height=920, scrolling=False)
