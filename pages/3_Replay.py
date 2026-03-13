import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf
import pandas as pd
import json
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.styles import SHARED_CSS
from utils.nav import navbar

st.set_page_config(
    page_title="Replay — 11%",
    page_icon="$",
    layout="wide",
    initial_sidebar_state="collapsed"
)
st.markdown(SHARED_CSS, unsafe_allow_html=True)
st.markdown("""
<style>
#MainMenu, footer, header { display:none!important; }
.block-container { padding:0.5rem 1rem 0!important; max-width:100%!important; }
section[data-testid="stMain"] > div { padding-top:0!important; }
[data-testid="stTextInput"] input {
    background:#0c1018!important; color:#eef2f7!important;
    border:1px solid #1a2235!important; border-radius:5px!important;
    font-family:'IBM Plex Mono',monospace!important; font-size:0.78rem!important;
    padding:5px 10px!important;
}
[data-testid="stNumberInput"] input {
    background:#0c1018!important; color:#eef2f7!important;
    border:1px solid #1a2235!important; border-radius:5px!important;
    font-family:'IBM Plex Mono',monospace!important;
}
div[data-testid="stSelectbox"] > div > div {
    background:#0c1018!important; border:1px solid #1a2235!important;
    border-radius:5px!important; color:#eef2f7!important;
    font-family:'IBM Plex Mono',monospace!important; font-size:0.75rem!important;
}
div.stButton > button {
    font-family:'IBM Plex Mono',monospace!important;
    font-size:0.58rem!important; font-weight:700!important;
    text-transform:uppercase!important; letter-spacing:0.08em!important;
    border-radius:5px!important; padding:6px 14px!important;
    transition:all 0.15s!important;
}
div.stButton > button[kind="primary"] {
    background:#00e676!important; color:#000!important;
    border:1px solid #00e676!important;
}
div.stButton > button[kind="primary"]:hover {
    background:#00ff88!important; box-shadow:0 0 16px rgba(0,230,118,0.4)!important;
}
</style>
""", unsafe_allow_html=True)

navbar()

# ── Session state init ─────────────────────────────────────────────────────────
for k, v in [
    ("rp_df", None), ("rp_ticker", "AAPL"), ("rp_loaded", False),
    ("rp_trades", []), ("rp_capital", 10000.0),
    ("rp_interval", "1d"), ("rp_period", "1y"),
]:
    if k not in st.session_state:
        st.session_state[k] = v

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="display:flex;align-items:center;justify-content:space-between;
    padding:0.6rem 0 0.8rem;border-bottom:1px solid #1a2235;margin-bottom:0.8rem;">
  <div style="display:flex;align-items:center;gap:1rem;">
    <div>
      <div style="font-family:'Bebas Neue',sans-serif;font-size:1.9rem;
          letter-spacing:0.07em;color:#eef2f7;line-height:1;display:flex;
          align-items:center;gap:0.7rem;">
        MARKET REPLAY
        <span style="font-family:'IBM Plex Mono',monospace;font-size:0.48rem;
            font-weight:700;text-transform:uppercase;letter-spacing:0.2em;
            color:#000;background:#00e676;border-radius:3px;padding:3px 9px;">
          FLAGSHIP
        </span>
      </div>
      <div style="font-family:'IBM Plex Mono',monospace;font-size:0.6rem;
          color:#2a3550;margin-top:0.15rem;letter-spacing:0.06em;">
        Animated bar-by-bar · Live trade execution · Indicators · Drawing tools · Fibonacci · Pattern tools
      </div>
    </div>
  </div>
  <div style="font-family:'IBM Plex Mono',monospace;font-size:0.52rem;color:#1a2235;
      text-align:right;line-height:2;">
    SPACE=Play/Pause &nbsp;·&nbsp; ←/→=Step &nbsp;·&nbsp; B=Buy &nbsp;·&nbsp; S=Short &nbsp;·&nbsp; C=Close
  </div>
</div>
""", unsafe_allow_html=True)

# ── Control bar ────────────────────────────────────────────────────────────────
col1, col2, col3, col4, col5, col6, col7 = st.columns([1.8, 1, 1, 1, 0.9, 0.9, 0.9])

with col1:
    ticker_in = st.text_input(
        "Ticker", value=st.session_state["rp_ticker"],
        placeholder="e.g. AAPL, TSLA, BTC-USD",
        label_visibility="collapsed"
    ).strip().upper()

with col2:
    interval_map = {"1m":"1 Min","5m":"5 Min","15m":"15 Min","30m":"30 Min",
                    "1h":"1 Hour","4h":"4 Hour","1d":"Daily","1wk":"Weekly","1mo":"Monthly"}
    interval = st.selectbox("Interval", list(interval_map.keys()),
                            index=list(interval_map.keys()).index(st.session_state["rp_interval"]),
                            format_func=lambda x: interval_map[x],
                            label_visibility="collapsed")

with col3:
    period_map = {"7d":"7 Days","1mo":"1 Month","3mo":"3 Months",
                  "6mo":"6 Months","1y":"1 Year","2y":"2 Years","5y":"5 Years"}
    period = st.selectbox("Period", list(period_map.keys()),
                          index=list(period_map.keys()).index(st.session_state["rp_period"]),
                          format_func=lambda x: period_map[x],
                          label_visibility="collapsed")

with col4:
    capital = st.number_input("Capital", value=st.session_state["rp_capital"],
                               min_value=100.0, step=1000.0, label_visibility="collapsed",
                               format="%.0f")

with col5:
    load_btn = st.button("⬛ Load", type="primary", use_container_width=True)

with col6:
    reset_btn = st.button("↺ Reset Session", use_container_width=True)

with col7:
    if st.session_state["rp_loaded"] and st.session_state["rp_trades"]:
        df_exp = pd.DataFrame(st.session_state["rp_trades"])
        st.download_button("↓ Export", df_exp.to_csv(index=False),
                           file_name="trades.csv", mime="text/csv",
                           use_container_width=True)
    else:
        st.button("↓ Export", disabled=True, use_container_width=True)

# ── Reset ─────────────────────────────────────────────────────────────────────
if reset_btn:
    st.session_state["rp_loaded"] = False
    st.session_state["rp_df"]     = None
    st.session_state["rp_trades"] = []
    st.session_state["rp_capital"] = capital
    st.rerun()

# ── Load data ─────────────────────────────────────────────────────────────────
if load_btn:
    with st.spinner(f"Loading {ticker_in} · {interval_map[interval]} · {period_map[period]}..."):
        try:
            raw = yf.Ticker(ticker_in).history(period=period, interval=interval)
            if raw.empty or len(raw) < 30:
                st.error(f"Not enough data for {ticker_in}. Try a longer period or different interval.")
            else:
                raw = raw[["Open","High","Low","Close","Volume"]].dropna().reset_index()
                raw.columns = ["Date","Open","High","Low","Close","Volume"]
                raw["Date"] = raw["Date"].astype(str).str[:16]  # keep HH:MM for intraday
                st.session_state["rp_df"]      = raw.to_dict("records")
                st.session_state["rp_ticker"]  = ticker_in
                st.session_state["rp_interval"] = interval
                st.session_state["rp_period"]   = period
                st.session_state["rp_trades"]  = []
                st.session_state["rp_capital"] = capital
                st.session_state["rp_loaded"]  = True
                st.rerun()
        except Exception as e:
            st.error(f"Error loading {ticker_in}: {e}")

# ═══════════════════════════════════════════════════════════════════════════════
#  LANDING SCREEN
# ═══════════════════════════════════════════════════════════════════════════════
if not st.session_state["rp_loaded"] or not st.session_state["rp_df"]:
    st.markdown("""
<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;
    min-height:62vh;gap:2.5rem;padding:2rem 1rem;">

  <div style="text-align:center;">
    <div style="font-family:'Bebas Neue',sans-serif;font-size:5.5rem;line-height:0.88;
        letter-spacing:0.03em;margin-bottom:1.2rem;">
      <span style="color:#00e676;">TRADE</span><br>
      <span style="color:#eef2f7;">THE PAST.</span><br>
      <span style="color:#ff3d57;">WIN</span><br>
      <span style="color:#eef2f7;">THE FUTURE.</span>
    </div>
    <div style="font-family:'IBM Plex Mono',monospace;font-size:0.72rem;
        color:#3a4a5e;max-width:500px;margin:0 auto;line-height:2;">
      Enter a ticker above, pick your timeframe, hit <strong style="color:#00e676;">Load</strong>.<br>
      The chart comes alive bar by bar. You trade blind — just like real life.
    </div>
  </div>

  <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;max-width:720px;width:100%;">
    <div style="background:#0c1018;border:1px solid #1a2235;border-radius:10px;
        padding:1.2rem 1rem;text-align:center;">
      <div style="font-size:1.6rem;margin-bottom:0.5rem;">⏱</div>
      <div style="font-family:'IBM Plex Mono',monospace;font-size:0.52rem;
          text-transform:uppercase;letter-spacing:0.16em;color:#00e676;margin-bottom:0.3rem;">
        Animated
      </div>
      <div style="font-family:'IBM Plex Mono',monospace;font-size:0.6rem;color:#3a4a5e;">
        0.07× to 10× playback speed
      </div>
    </div>
    <div style="background:#0c1018;border:1px solid #1a2235;border-radius:10px;
        padding:1.2rem 1rem;text-align:center;">
      <div style="font-size:1.6rem;margin-bottom:0.5rem;">📊</div>
      <div style="font-family:'IBM Plex Mono',monospace;font-size:0.52rem;
          text-transform:uppercase;letter-spacing:0.16em;color:#00e676;margin-bottom:0.3rem;">
        Indicators
      </div>
      <div style="font-family:'IBM Plex Mono',monospace;font-size:0.6rem;color:#3a4a5e;">
        SMA · EMA · VWAP · BB · RSI · MACD
      </div>
    </div>
    <div style="background:#0c1018;border:1px solid #1a2235;border-radius:10px;
        padding:1.2rem 1rem;text-align:center;">
      <div style="font-size:1.6rem;margin-bottom:0.5rem;">✏️</div>
      <div style="font-family:'IBM Plex Mono',monospace;font-size:0.52rem;
          text-transform:uppercase;letter-spacing:0.16em;color:#00e676;margin-bottom:0.3rem;">
        Drawing Tools
      </div>
      <div style="font-family:'IBM Plex Mono',monospace;font-size:0.6rem;color:#3a4a5e;">
        Lines · Fib · Boxes · Rays · Patterns
      </div>
    </div>
    <div style="background:#0c1018;border:1px solid #1a2235;border-radius:10px;
        padding:1.2rem 1rem;text-align:center;">
      <div style="font-size:1.6rem;margin-bottom:0.5rem;">💰</div>
      <div style="font-family:'IBM Plex Mono',monospace;font-size:0.52rem;
          text-transform:uppercase;letter-spacing:0.16em;color:#00e676;margin-bottom:0.3rem;">
        Live P&L
      </div>
      <div style="font-family:'IBM Plex Mono',monospace;font-size:0.6rem;color:#3a4a5e;">
        Buy · Short · Close with real math
      </div>
    </div>
  </div>

</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN REPLAY ENGINE
# ═══════════════════════════════════════════════════════════════════════════════
else:
    bars_json    = json.dumps(st.session_state["rp_df"])
    trades_json  = json.dumps(st.session_state["rp_trades"])
    capital_val  = float(st.session_state["rp_capital"])
    ticker_label = st.session_state["rp_ticker"]
    n_bars       = len(st.session_state["rp_df"])

    HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<script src="https://cdn.jsdelivr.net/npm/lightweight-charts@4.1.3/dist/lightweight-charts.standalone.production.js"></script>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600;700&family=Bebas+Neue&display=swap" rel="stylesheet">
<style>
:root {{
  --bg:      #06080c;
  --surface: #0c1018;
  --border:  #1a2235;
  --border2: #0d1117;
  --text:    #eef2f7;
  --dim:     #3a4a5e;
  --dim2:    #1a2235;
  --green:   #00e676;
  --red:     #ff3d57;
  --gold:    #ffd166;
  --blue:    #4da6ff;
  --purple:  #b388ff;
}}
* {{ margin:0; padding:0; box-sizing:border-box; }}
html, body {{ width:100%; height:100%; background:var(--bg); color:var(--text);
  font-family:'IBM Plex Mono',monospace; overflow:hidden; }}

/* ── LAYOUT ─────────────────────────────────────────── */
#root {{ display:flex; flex-direction:column; height:100vh; }}

/* ── TOOLBAR ────────────────────────────────────────── */
#toolbar {{
  display:flex; align-items:center; gap:0;
  background:var(--bg); border-bottom:1px solid var(--border);
  flex-shrink:0; overflow-x:auto; overflow-y:hidden;
  scrollbar-width:none;
}}
#toolbar::-webkit-scrollbar {{ display:none; }}

.tb-sep {{ width:1px; background:var(--border); align-self:stretch; margin:0 2px; flex-shrink:0; }}

.tb-group {{
  display:flex; align-items:center; gap:3px;
  padding:6px 8px; flex-shrink:0;
}}
.tb-label {{
  font-size:0.4rem; text-transform:uppercase; letter-spacing:0.18em;
  color:var(--dim2); margin-right:2px; white-space:nowrap;
}}

/* pill buttons */
.tb-btn {{
  font-family:'IBM Plex Mono',monospace;
  font-size:0.5rem; font-weight:700;
  text-transform:uppercase; letter-spacing:0.07em;
  background:var(--surface); border:1px solid var(--border);
  border-radius:4px; color:var(--dim); padding:5px 9px;
  cursor:pointer; white-space:nowrap; transition:all 0.12s; line-height:1;
}}
.tb-btn:hover {{ color:var(--text); border-color:#2a3550; background:#0f1620; }}
.tb-btn.on  {{ color:var(--green); border-color:var(--green); background:rgba(0,230,118,0.08); }}
.tb-btn.ct-on {{ color:var(--text); background:#1a2235; border-color:#2a3550; }}

/* play / step */
#btn-play {{ min-width:64px; }}
#btn-play.playing {{ color:var(--gold); border-color:var(--gold); background:rgba(255,209,102,0.08); }}

/* trade buttons */
.trade-buy   {{ color:#000!important; background:var(--green)!important; border-color:var(--green)!important; min-width:52px; }}
.trade-buy:hover   {{ background:#00ff88!important; box-shadow:0 0 14px rgba(0,230,118,0.4); }}
.trade-short {{ color:#000!important; background:var(--red)!important; border-color:var(--red)!important; min-width:52px; }}
.trade-short:hover {{ background:#ff6070!important; box-shadow:0 0 14px rgba(255,61,87,0.4); }}
.trade-close {{ color:#000!important; background:var(--gold)!important; border-color:var(--gold)!important; min-width:52px; }}
.trade-close:hover {{ background:#ffe08a!important; }}

/* speed slider */
#speed-wrap {{ display:flex; align-items:center; gap:5px; }}
#speed-slider {{
  -webkit-appearance:none; width:80px; height:3px;
  background:var(--border); border-radius:2px; outline:none; cursor:pointer;
}}
#speed-slider::-webkit-slider-thumb {{
  -webkit-appearance:none; width:11px; height:11px;
  border-radius:50%; background:var(--green); cursor:pointer;
}}
#speed-val {{ font-size:0.6rem; color:var(--green); font-weight:700; min-width:34px; }}

/* scrubber */
#scrub-wrap {{ display:flex; align-items:center; gap:5px; }}
#scrubber {{
  -webkit-appearance:none; width:100px; height:3px;
  background:var(--border); border-radius:2px; outline:none; cursor:pointer;
}}
#scrubber::-webkit-slider-thumb {{
  -webkit-appearance:none; width:11px; height:11px;
  border-radius:50%; background:var(--blue); cursor:pointer;
}}
#bar-pos {{ font-size:0.52rem; color:var(--dim); min-width:70px; }}

/* qty / price mini inputs */
.mini-input {{
  background:var(--surface); border:1px solid var(--border);
  border-radius:4px; color:var(--text);
  font-family:'IBM Plex Mono',monospace; font-size:0.6rem;
  padding:4px 7px; outline:none; width:72px;
  transition:border-color 0.12s;
}}
.mini-input:focus {{ border-color:var(--dim); }}

/* ticker badge */
#ticker-badge {{
  font-family:'Bebas Neue',sans-serif; font-size:1.3rem;
  color:var(--text); letter-spacing:0.07em; line-height:1;
  padding:0 10px;
}}

/* ── BAR INFO STRIP ──────────────────────────────────── */
#bar-strip {{
  display:flex; align-items:center; gap:18px;
  padding:4px 12px; background:var(--bg);
  border-bottom:1px solid var(--border2);
  font-size:0.6rem; color:var(--dim); flex-shrink:0;
  overflow-x:auto; scrollbar-width:none;
}}
#bar-strip::-webkit-scrollbar {{ display:none; }}
.bs-price {{ color:var(--text); font-weight:700; font-size:0.72rem; }}
.bs-up {{ color:var(--green); }}
.bs-dn {{ color:var(--red); }}
.bs-dim {{ color:var(--dim); }}

/* ── METRICS ROW ─────────────────────────────────────── */
#metrics {{
  display:flex; border-bottom:1px solid var(--border);
  background:var(--bg); flex-shrink:0;
}}
.mc {{
  flex:1; padding:7px 14px; border-right:1px solid var(--border);
  min-width:0;
}}
.mc:last-child {{ border-right:none; }}
.mc-lbl {{
  font-size:0.4rem; text-transform:uppercase; letter-spacing:0.18em;
  color:var(--dim2); margin-bottom:2px; white-space:nowrap;
}}
.mc-val {{
  font-size:0.88rem; font-weight:700; color:var(--text);
  white-space:nowrap; overflow:hidden; text-overflow:ellipsis;
}}
.mc-val.pos {{ color:var(--green); }}
.mc-val.neg {{ color:var(--red); }}
.mc-val.dim {{ color:var(--dim); }}

/* ── BODY: CHART + SIDEBAR ───────────────────────────── */
#body {{ display:flex; flex:1; min-height:0; overflow:hidden; }}

/* ── CHART COLUMN ────────────────────────────────────── */
#chart-col {{
  flex:1; display:flex; flex-direction:column; min-width:0; overflow:hidden;
}}
#main-chart {{ flex:1; min-height:0; }}
#vol-chart  {{ flex-shrink:0; height:72px; }}
#rsi-chart  {{ flex-shrink:0; height:70px; display:none; border-top:1px solid var(--border2); }}
#macd-chart {{ flex-shrink:0; height:70px; display:none; border-top:1px solid var(--border2); }}

/* ── DRAW BAR ────────────────────────────────────────── */
#draw-bar {{
  display:flex; align-items:center; gap:4px; flex-wrap:wrap;
  padding:5px 10px; background:var(--bg);
  border-top:1px solid var(--border); flex-shrink:0;
}}
.draw-btn {{
  font-family:'IBM Plex Mono',monospace;
  font-size:0.48rem; font-weight:700; text-transform:uppercase; letter-spacing:0.07em;
  background:transparent; border:1px solid var(--border); border-radius:4px;
  color:var(--dim); padding:4px 8px; cursor:pointer; white-space:nowrap;
  transition:all 0.12s; line-height:1;
}}
.draw-btn:hover {{ color:var(--text); border-color:#2a3550; }}
.draw-btn.on {{ color:var(--gold); border-color:var(--gold); background:rgba(255,209,102,0.07); }}
.draw-btn.danger {{ color:var(--red)!important; border-color:var(--red)!important; }}
.draw-btn.danger:hover {{ background:rgba(255,61,87,0.08)!important; }}
#draw-color-pick {{
  background:var(--surface); border:1px solid var(--border); border-radius:4px;
  color:var(--text); font-family:'IBM Plex Mono',monospace; font-size:0.48rem;
  padding:3px 5px; cursor:pointer; outline:none;
}}

/* ── SIDEBAR ─────────────────────────────────────────── */
#sidebar {{
  width:250px; flex-shrink:0; background:var(--bg);
  border-left:1px solid var(--border);
  display:flex; flex-direction:column; overflow:hidden;
}}
.sb-section {{
  padding:9px 12px; border-bottom:1px solid var(--border2); flex-shrink:0;
}}
.sb-title {{
  font-size:0.42rem; text-transform:uppercase; letter-spacing:0.2em;
  color:var(--dim2); margin-bottom:7px;
}}

/* Indicator checkboxes */
.ind-row {{
  display:flex; align-items:center; justify-content:space-between;
  margin-bottom:5px;
}}
.ind-label {{
  display:flex; align-items:center; gap:6px;
  font-size:0.58rem; color:var(--dim); cursor:pointer;
  transition:color 0.12s; user-select:none;
}}
.ind-label:hover {{ color:var(--text); }}
.ind-label input {{ accent-color:var(--green); width:12px; height:12px; cursor:pointer; }}
.ind-dot {{ width:7px; height:7px; border-radius:50%; flex-shrink:0; }}
.ind-param {{
  background:var(--surface); border:1px solid var(--border); border-radius:3px;
  color:var(--dim); font-family:'IBM Plex Mono',monospace; font-size:0.52rem;
  padding:2px 5px; width:38px; outline:none; text-align:center;
}}
.ind-param:focus {{ border-color:var(--dim); color:var(--text); }}

/* Open position box */
#pos-box {{
  margin:8px 12px; padding:8px 10px; border-radius:6px;
  border:1px solid rgba(0,230,118,0.2); background:rgba(0,230,118,0.04);
  display:none; font-size:0.6rem; flex-shrink:0;
}}
#pos-box.short {{ border-color:rgba(255,61,87,0.25); background:rgba(255,61,87,0.04); }}
#pos-dir {{ font-size:0.72rem; font-weight:700; color:var(--green); margin-bottom:4px; }}
#pos-dir.short-dir {{ color:var(--red); }}
#pos-detail {{ color:var(--dim); line-height:1.8; }}
#pos-unreal {{ font-weight:700; }}

/* Trade log */
#log-wrap {{
  flex:1; overflow-y:auto; min-height:0;
}}
#log-wrap::-webkit-scrollbar {{ width:3px; }}
#log-wrap::-webkit-scrollbar-track {{ background:var(--bg); }}
#log-wrap::-webkit-scrollbar-thumb {{ background:var(--border); border-radius:2px; }}
.log-row {{
  display:grid; grid-template-columns:52px 44px 64px 1fr;
  gap:3px; padding:5px 12px; border-bottom:1px solid var(--border2);
  font-size:0.55rem; align-items:center;
}}
.log-row:hover {{ background:rgba(255,255,255,0.01); }}
.lr-time {{ color:var(--dim2); }}
.lr-buy   {{ color:var(--green); font-weight:700; }}
.lr-short {{ color:var(--red);   font-weight:700; }}
.lr-close {{ color:var(--gold);  font-weight:700; }}
.lr-price {{ color:var(--text); }}
.lr-pos {{ color:var(--green); font-weight:700; text-align:right; }}
.lr-neg {{ color:var(--red);   font-weight:700; text-align:right; }}
.lr-dim {{ color:var(--dim);   text-align:right; }}

/* ── TOAST ───────────────────────────────────────────── */
#toast {{
  position:fixed; top:12px; left:50%; transform:translateX(-50%);
  background:var(--surface); border:1px solid var(--border); border-radius:7px;
  padding:9px 20px; font-size:0.65rem; font-weight:600;
  z-index:9999; display:none; pointer-events:none;
  box-shadow:0 16px 48px rgba(0,0,0,0.85); white-space:nowrap;
}}

/* ── CROSSHAIR VALUE TOOLTIP ─────────────────────────── */
#xhair-tooltip {{
  position:absolute; top:8px; left:10px;
  background:rgba(6,8,12,0.88); border:1px solid var(--border);
  border-radius:5px; padding:5px 10px; font-size:0.58rem;
  pointer-events:none; display:none; z-index:100; line-height:1.8;
}}
</style>
</head>
<body>
<div id="root">

<div id="toast"></div>

<!-- ═══ TOOLBAR ═══ -->
<div id="toolbar">

  <!-- Playback -->
  <div class="tb-group">
    <span class="tb-label">Playback</span>
    <button class="tb-btn" id="btn-play" onclick="togglePlay()">▶ Play</button>
    <button class="tb-btn" onclick="stepBars(-10)" title="Back 10">◀◀</button>
    <button class="tb-btn" onclick="stepBars(-1)"  title="Back 1">◀</button>
    <button class="tb-btn" onclick="stepBars(1)"   title="Fwd 1">▶</button>
    <button class="tb-btn" onclick="stepBars(10)"  title="Fwd 10">▶▶</button>
  </div>

  <div class="tb-sep"></div>

  <!-- Speed -->
  <div class="tb-group">
    <span class="tb-label">Speed</span>
    <div id="speed-wrap">
      <input type="range" id="speed-slider" min="1" max="10" value="3" oninput="onSpeedChange(this.value)">
      <span id="speed-val">0.3×</span>
    </div>
  </div>

  <div class="tb-sep"></div>

  <!-- Scrubber -->
  <div class="tb-group">
    <span class="tb-label">Position</span>
    <div id="scrub-wrap">
      <input type="range" id="scrubber" min="30" max="{n_bars - 1}" value="60" oninput="scrubTo(+this.value)">
      <span id="bar-pos">60 / {n_bars}</span>
    </div>
  </div>

  <div class="tb-sep"></div>

  <!-- Chart type -->
  <div class="tb-group">
    <span class="tb-label">Chart</span>
    <button class="tb-btn ct-on" id="ct-candle"  onclick="setChartType('candle')">Candles</button>
    <button class="tb-btn" id="ct-heikin" onclick="setChartType('heikin')">Heikin</button>
    <button class="tb-btn" id="ct-bar"    onclick="setChartType('bar')">Bars</button>
    <button class="tb-btn" id="ct-line"   onclick="setChartType('line')">Line</button>
    <button class="tb-btn" id="ct-area"   onclick="setChartType('area')">Area</button>
  </div>

  <div class="tb-sep"></div>

  <!-- Trade execution -->
  <div class="tb-group">
    <span class="tb-label">Qty</span>
    <input type="number" class="mini-input" id="trade-qty" value="10" min="1" style="width:60px;">
    <span class="tb-label" style="margin-left:4px;">@ $</span>
    <input type="number" class="mini-input" id="trade-price" value="0.00" step="0.01" style="width:80px;">
    <button class="tb-btn trade-buy"   onclick="executeTrade('buy')"   title="Buy Long (B)">BUY</button>
    <button class="tb-btn trade-short" onclick="executeTrade('short')" title="Sell Short (S)">SHORT</button>
    <button class="tb-btn trade-close" onclick="executeTrade('close')" title="Close Position (C)">CLOSE</button>
  </div>

  <div class="tb-sep" style="margin-left:auto;"></div>

  <!-- Ticker -->
  <div class="tb-group">
    <span id="ticker-badge">{ticker_label}</span>
  </div>

</div>

<!-- ═══ BAR INFO STRIP ═══ -->
<div id="bar-strip">
  <span id="bs-date" class="bs-dim">—</span>
  <span>O <span id="bs-open" class="bs-price">—</span></span>
  <span>H <span id="bs-high" class="bs-price">—</span></span>
  <span>L <span id="bs-low"  class="bs-price">—</span></span>
  <span>C <span id="bs-close" class="bs-price">—</span></span>
  <span id="bs-chg">—</span>
  <span style="margin-left:auto;" id="bs-vol" class="bs-dim">—</span>
</div>

<!-- ═══ METRICS ═══ -->
<div id="metrics">
  <div class="mc"><div class="mc-lbl">Portfolio</div><div class="mc-val" id="m-port">—</div></div>
  <div class="mc"><div class="mc-lbl">Cash</div><div class="mc-val dim" id="m-cash">—</div></div>
  <div class="mc"><div class="mc-lbl">Return</div><div class="mc-val" id="m-ret">—</div></div>
  <div class="mc"><div class="mc-lbl">Realised P&L</div><div class="mc-val" id="m-pnl">—</div></div>
  <div class="mc"><div class="mc-lbl">Open P&L</div><div class="mc-val" id="m-open">—</div></div>
  <div class="mc"><div class="mc-lbl">Win Rate</div><div class="mc-val dim" id="m-wr">—</div></div>
  <div class="mc"><div class="mc-lbl">Trades</div><div class="mc-val dim" id="m-tc">0</div></div>
</div>

<!-- ═══ BODY ═══ -->
<div id="body">

  <!-- Chart column -->
  <div id="chart-col">
    <div id="main-chart" style="position:relative;">
      <div id="xhair-tooltip"></div>
    </div>
    <div id="vol-chart"></div>
    <div id="rsi-chart"></div>
    <div id="macd-chart"></div>

    <!-- Drawing toolbar -->
    <div id="draw-bar">
      <span class="tb-label" style="margin-right:3px;">DRAW:</span>
      <button class="draw-btn" id="draw-cursor" onclick="setDraw('cursor')">↖ Select</button>
      <button class="draw-btn" id="draw-hline"  onclick="setDraw('hline')">— H-Line</button>
      <button class="draw-btn" id="draw-vline"  onclick="setDraw('vline')">| V-Line</button>
      <button class="draw-btn" id="draw-trend"  onclick="setDraw('trend')">╱ Trend</button>
      <button class="draw-btn" id="draw-ray"    onclick="setDraw('ray')">→ Ray</button>
      <button class="draw-btn" id="draw-fib"    onclick="setDraw('fib')">✦ Fibonacci</button>
      <button class="draw-btn" id="draw-rect"   onclick="setDraw('rect')">▭ Box</button>
      <button class="draw-btn" id="draw-mark"   onclick="setDraw('mark')">⬦ Marker</button>
      <span style="flex:1;"></span>
      <select id="draw-color-pick">
        <option value="#ffd166" selected>● Yellow</option>
        <option value="#00e676">● Green</option>
        <option value="#ff3d57">● Red</option>
        <option value="#4da6ff">● Blue</option>
        <option value="#b388ff">● Purple</option>
        <option value="#ffffff">● White</option>
        <option value="#ff7043">● Orange</option>
      </select>
      <button class="draw-btn danger" onclick="clearAllDrawings()">✕ Clear All</button>
    </div>
  </div>

  <!-- ═══ SIDEBAR ═══ -->
  <div id="sidebar">

    <!-- Indicators -->
    <div class="sb-section">
      <div class="sb-title">Indicators</div>

      <div class="ind-row">
        <label class="ind-label" for="i-sma20">
          <input type="checkbox" id="i-sma20" onchange="renderAll()">
          <span class="ind-dot" style="background:#4da6ff;"></span>SMA
        </label>
        <input type="number" class="ind-param" id="p-sma20" value="20" min="2" max="200" onchange="renderAll()">
      </div>

      <div class="ind-row">
        <label class="ind-label" for="i-sma50">
          <input type="checkbox" id="i-sma50" onchange="renderAll()">
          <span class="ind-dot" style="background:#b388ff;"></span>SMA
        </label>
        <input type="number" class="ind-param" id="p-sma50" value="50" min="2" max="200" onchange="renderAll()">
      </div>

      <div class="ind-row">
        <label class="ind-label" for="i-ema20">
          <input type="checkbox" id="i-ema20" onchange="renderAll()">
          <span class="ind-dot" style="background:#00e676;"></span>EMA
        </label>
        <input type="number" class="ind-param" id="p-ema20" value="20" min="2" max="200" onchange="renderAll()">
      </div>

      <div class="ind-row">
        <label class="ind-label" for="i-ema50">
          <input type="checkbox" id="i-ema50" onchange="renderAll()">
          <span class="ind-dot" style="background:#00bcd4;"></span>EMA
        </label>
        <input type="number" class="ind-param" id="p-ema50" value="50" min="2" max="200" onchange="renderAll()">
      </div>

      <div class="ind-row">
        <label class="ind-label" for="i-vwap">
          <input type="checkbox" id="i-vwap" onchange="renderAll()">
          <span class="ind-dot" style="background:#ffd166;"></span>VWAP
        </label>
      </div>

      <div class="ind-row">
        <label class="ind-label" for="i-bb">
          <input type="checkbox" id="i-bb" onchange="renderAll()">
          <span class="ind-dot" style="background:#ff7043;"></span>Bollinger
        </label>
        <input type="number" class="ind-param" id="p-bb" value="20" min="5" max="100" onchange="renderAll()">
      </div>

      <div class="ind-row">
        <label class="ind-label" for="i-rsi">
          <input type="checkbox" id="i-rsi" onchange="toggleSubChart('rsi', this.checked)">
          <span class="ind-dot" style="background:#e91e63;"></span>RSI
        </label>
        <input type="number" class="ind-param" id="p-rsi" value="14" min="2" max="50" onchange="renderAll()">
      </div>

      <div class="ind-row">
        <label class="ind-label" for="i-macd">
          <input type="checkbox" id="i-macd" onchange="toggleSubChart('macd', this.checked)">
          <span class="ind-dot" style="background:#ff9800;"></span>MACD
        </label>
      </div>

    </div>

    <!-- Open position -->
    <div id="pos-box">
      <div id="pos-dir">● LONG</div>
      <div id="pos-detail"></div>
    </div>

    <!-- Trade log -->
    <div class="sb-section" style="padding-bottom:4px;">
      <div class="sb-title">Trade Log</div>
    </div>
    <div id="log-wrap">
      <div id="trade-log"></div>
    </div>

  </div><!-- /sidebar -->
</div><!-- /body -->
</div><!-- /root -->

<script>
// ═══════════════════════════════════════════════════════════
// DATA
// ═══════════════════════════════════════════════════════════
const ALL  = {bars_json};
const CAP  = {capital_val};
const N    = ALL.length;

// ═══════════════════════════════════════════════════════════
// STATE
// ═══════════════════════════════════════════════════════════
let curBar    = Math.min(60, N - 1);
let isPlaying = false;
let playTimer = null;
let speed     = 0.3;          // bars/sec
let chartType = 'candle';
let drawMode  = 'cursor';

// Portfolio
let cash        = CAP;
let position    = null;       // {{dir, entry, qty, date}}
let trades      = {trades_json};
let realisedPnl = 0;
let wins        = 0;

// Drawing
let drawSegs  = [];           // {{series[], mode, complete}}
let tempPts   = [];           // in-progress click points
let userMarks = [];           // manual markers

// Indicator series handles
const IS = {{}};              // id -> series or [series...]

// Speed table (index 1-10)
const SPEEDS = [0.07, 0.15, 0.3, 0.5, 1, 1.5, 2, 3, 5, 10];

// ═══════════════════════════════════════════════════════════
// CHART SETUP
// ═══════════════════════════════════════════════════════════
const CHART_OPTS = {{
  layout: {{
    background: {{ type:'solid', color:'#06080c' }},
    textColor: '#3a4a5e',
    fontSize: 11,
    fontFamily: "'IBM Plex Mono', monospace",
  }},
  grid: {{
    vertLines: {{ color:'#0d1117' }},
    horzLines: {{ color:'#0d1117' }},
  }},
  crosshair: {{
    mode: LightweightCharts.CrosshairMode.Normal,
    vertLine: {{ color:'#2a3550', width:1, style:LightweightCharts.LineStyle.Dashed, labelBackgroundColor:'#1a2235' }},
    horzLine: {{ color:'#2a3550', width:1, style:LightweightCharts.LineStyle.Dashed, labelBackgroundColor:'#1a2235' }},
  }},
  rightPriceScale: {{ borderColor:'#1a2235', textColor:'#3a4a5e' }},
  timeScale: {{ borderColor:'#1a2235', textColor:'#3a4a5e', timeVisible:true, secondsVisible:false }},
  handleScroll: {{ vertTouchDrag:true, mouseWheel:true, pressedMouseMove:true }},
  handleScale: {{ axisPressedMouseMove:true, mouseWheel:true, pinch:true }},
}};

// Main chart
const mainEl = document.getElementById('main-chart');
const mainChart = LightweightCharts.createChart(mainEl, {{
  ...CHART_OPTS,
  width: mainEl.offsetWidth,
  height: mainEl.offsetHeight || 400,
}});

// Volume chart
const volEl = document.getElementById('vol-chart');
const volChart = LightweightCharts.createChart(volEl, {{
  ...CHART_OPTS,
  width: volEl.offsetWidth,
  height: 72,
  timeScale: {{ ...CHART_OPTS.timeScale, visible:false }},
  rightPriceScale: {{ ...CHART_OPTS.rightPriceScale, scaleMargins:{{top:0.05,bottom:0}} }},
}});

// RSI chart
const rsiEl = document.getElementById('rsi-chart');
const rsiChart = LightweightCharts.createChart(rsiEl, {{
  ...CHART_OPTS,
  width: rsiEl.offsetWidth,
  height: 70,
  timeScale: {{ ...CHART_OPTS.timeScale, visible:false }},
}});
const rsiSeries = rsiChart.addLineSeries({{ color:'#e91e63', lineWidth:1 }});
// Overbought/oversold
const rsiOB = rsiChart.addLineSeries({{ color:'rgba(255,61,87,0.3)', lineWidth:1, lineStyle:LightweightCharts.LineStyle.Dashed }});
const rsiOS = rsiChart.addLineSeries({{ color:'rgba(0,230,118,0.3)', lineWidth:1, lineStyle:LightweightCharts.LineStyle.Dashed }});

// MACD chart
const macdEl = document.getElementById('macd-chart');
const macdChart = LightweightCharts.createChart(macdEl, {{
  ...CHART_OPTS,
  width: macdEl.offsetWidth,
  height: 70,
  timeScale: {{ ...CHART_OPTS.timeScale, visible:false }},
}});
const macdFastSeries = macdChart.addLineSeries({{ color:'#ff9800', lineWidth:1 }});
const macdSignSeries = macdChart.addLineSeries({{ color:'#4da6ff', lineWidth:1 }});
const macdHistSeries = macdChart.addHistogramSeries({{ priceScaleId:'' }});
macdChart.priceScale('').applyOptions({{ scaleMargins:{{top:0.1,bottom:0.1}} }});

// Main series (candlestick by default)
let mainSeries = null;
let volSeries  = null;

function createMainSeries(type) {{
  if (mainSeries) mainChart.removeSeries(mainSeries);
  const up = '#00e676', dn = '#ff3d57';
  switch(type) {{
    case 'bar':
      mainSeries = mainChart.addBarSeries({{ upColor:up, downColor:dn }});
      break;
    case 'line':
      mainSeries = mainChart.addLineSeries({{ color:up, lineWidth:2 }});
      break;
    case 'area':
      mainSeries = mainChart.addAreaSeries({{
        lineColor:up, topColor:'rgba(0,230,118,0.22)',
        bottomColor:'rgba(0,230,118,0)', lineWidth:2,
      }});
      break;
    default: // candle + heikin
      mainSeries = mainChart.addCandlestickSeries({{
        upColor:up, downColor:dn, borderUpColor:up,
        borderDownColor:dn, wickUpColor:up, wickDownColor:dn,
      }});
  }}
}}

function createVolSeries() {{
  if (volSeries) volChart.removeSeries(volSeries);
  volSeries = volChart.addHistogramSeries({{
    priceFormat:{{ type:'volume' }}, priceScaleId:'',
  }});
  volChart.priceScale('').applyOptions({{ scaleMargins:{{top:0.1,bottom:0}} }});
}}

createMainSeries('candle');
createVolSeries();

// Sync time scales
function syncScroll(src, targets) {{
  src.timeScale().subscribeVisibleLogicalRangeChange(r => {{
    if (!r) return;
    targets.forEach(c => c.timeScale().setVisibleLogicalRange(r));
  }});
}}
syncScroll(mainChart, [volChart, rsiChart, macdChart]);
syncScroll(volChart,  [mainChart, rsiChart, macdChart]);

// ═══════════════════════════════════════════════════════════
// BAR DATA BUILDERS
// ═══════════════════════════════════════════════════════════
function toTime(d) {{
  // d = "2023-01-15" or "2023-01-15 09:30"
  return d.length > 10 ? d.replace(' ','T') + ':00' : d;
}}

function buildBars(upTo) {{
  const out = [];
  for (let i = 0; i <= upTo; i++) {{
    const b = ALL[i];
    if (chartType === 'heikin') {{
      const hc = (b.Open + b.High + b.Low + b.Close) / 4;
      const ho = i === 0 ? (b.Open + b.Close) / 2
                         : (out[i-1].open + out[i-1].close) / 2;
      const hh = Math.max(b.High, ho, hc);
      const hl = Math.min(b.Low,  ho, hc);
      out.push({{ time:toTime(b.Date), open:ho, high:hh, low:hl, close:hc }});
    }} else {{
      out.push({{ time:toTime(b.Date), open:b.Open, high:b.High, low:b.Low, close:b.Close }});
    }}
  }}
  return out;
}}

function buildVol(upTo) {{
  const out = [];
  for (let i = 0; i <= upTo; i++) {{
    const b = ALL[i];
    const up = b.Close >= b.Open;
    out.push({{ time:toTime(b.Date), value:b.Volume,
      color: up ? 'rgba(0,230,118,0.3)' : 'rgba(255,61,87,0.25)' }});
  }}
  return out;
}}

// ═══════════════════════════════════════════════════════════
// INDICATOR MATH
// ═══════════════════════════════════════════════════════════
function calcSMA(data, p) {{
  const out = [];
  for (let i = p-1; i < data.length; i++) {{
    let s = 0;
    for (let j = 0; j < p; j++) s += ALL[i-j].Close;
    out.push({{ time:toTime(ALL[i].Date), value:s/p }});
  }}
  return out;
}}

function calcEMA(data, p) {{
  const k = 2/(p+1);
  const out = [];
  let ema = ALL[0].Close;
  for (let i = 1; i < data.length; i++) {{
    ema = ALL[i].Close * k + ema * (1-k);
    if (i >= p-1) out.push({{ time:toTime(ALL[i].Date), value:ema }});
  }}
  return out;
}}

function calcVWAP(data) {{
  const out = [];
  let cv = 0, cpv = 0;
  for (let i = 0; i < data.length; i++) {{
    cv  += ALL[i].Volume;
    cpv += ALL[i].Close * ALL[i].Volume;
    if (cv > 0) out.push({{ time:toTime(ALL[i].Date), value:cpv/cv }});
  }}
  return out;
}}

function calcBB(data, p) {{
  const upper=[], lower=[], mid=[];
  for (let i = p-1; i < data.length; i++) {{
    const closes = [];
    for (let j = 0; j < p; j++) closes.push(ALL[i-j].Close);
    const mean = closes.reduce((a,b)=>a+b,0)/p;
    const std  = Math.sqrt(closes.reduce((a,b)=>a+(b-mean)**2,0)/p);
    const t = toTime(ALL[i].Date);
    upper.push({{time:t, value:mean+2*std}});
    lower.push({{time:t, value:mean-2*std}});
    mid.push({{time:t, value:mean}});
  }}
  return {{upper, lower, mid}};
}}

function calcRSI(data, p) {{
  const out = [];
  let ag = 0, al = 0;
  for (let i = 1; i <= p; i++) {{
    const d = ALL[i].Close - ALL[i-1].Close;
    if (d > 0) ag += d; else al -= d;
  }}
  ag /= p; al /= p;
  for (let i = p; i < data.length; i++) {{
    if (i > p) {{
      const d = ALL[i].Close - ALL[i-1].Close;
      ag = (ag*(p-1) + Math.max(d,0)) / p;
      al = (al*(p-1) + Math.max(-d,0)) / p;
    }}
    const rs = al === 0 ? 100 : ag / al;
    out.push({{ time:toTime(ALL[i].Date), value:100 - 100/(1+rs) }});
  }}
  return out;
}}

function calcMACD(data) {{
  const k12=2/13, k26=2/27, k9=2/10;
  let e12=ALL[0].Close, e26=ALL[0].Close;
  const macdVals=[], signVals=[];
  for (let i=1; i<data.length; i++) {{
    e12 = ALL[i].Close*k12 + e12*(1-k12);
    e26 = ALL[i].Close*k26 + e26*(1-k26);
    if (i >= 25) macdVals.push({{ t:toTime(ALL[i].Date), v:e12-e26 }});
  }}
  let sig = macdVals[0]?.v || 0;
  macdVals.forEach(m => {{
    sig = m.v*k9 + sig*(1-k9);
    signVals.push(sig);
  }});
  return macdVals.map((m,i) => ({{
    time:m.t, macd:m.v, signal:signVals[i], hist:m.v-signVals[i]
  }}));
}}

// ═══════════════════════════════════════════════════════════
// RENDER ENGINE
// ═══════════════════════════════════════════════════════════
function renderAll() {{
  const data = ALL.slice(0, curBar+1);

  // Main bars
  const bars = buildBars(curBar);
  if (chartType === 'line' || chartType === 'area') {{
    mainSeries.setData(bars.map(b => ({{ time:b.time, value:b.close }})));
  }} else {{
    mainSeries.setData(bars);
  }}

  // Volume
  volSeries.setData(buildVol(curBar));

  // Trade markers
  const markers = [];
  trades.forEach(t => {{
    const idx = ALL.findIndex(b => b.Date >= t.date);
    if (idx < 0 || idx > curBar) return;
    markers.push({{
      time: toTime(ALL[idx].Date),
      position: t.dir === 'buy' ? 'belowBar' : t.dir === 'short' ? 'aboveBar' : 'inBar',
      color:    t.dir === 'buy' ? '#00e676'  : t.dir === 'short' ? '#ff3d57'  : '#ffd166',
      shape:    t.dir === 'buy' ? 'arrowUp'  : t.dir === 'short' ? 'arrowDown': 'circle',
      text:     t.dir === 'buy'   ? `B ${{t.price.toFixed(2)}}` :
                t.dir === 'short' ? `S ${{t.price.toFixed(2)}}` :
                `✕ ${{(t.pnl>=0?'+':'')+t.pnl.toFixed(2)}}`,
      size: 1,
    }});
  }});
  // User manual markers
  userMarks.forEach(m => {{
    if (ALL.findIndex(b=>b.Date>=m.date) <= curBar) markers.push(m.marker);
  }});
  mainSeries.setMarkers(markers);

  // ── Overlaid indicators ──
  const p_sma20 = +document.getElementById('p-sma20').value || 20;
  const p_sma50 = +document.getElementById('p-sma50').value || 50;
  const p_ema20 = +document.getElementById('p-ema20').value || 20;
  const p_ema50 = +document.getElementById('p-ema50').value || 50;
  const p_bb    = +document.getElementById('p-bb').value    || 20;
  const p_rsi   = +document.getElementById('p-rsi').value   || 14;

  _updateLine('sma20', document.getElementById('i-sma20').checked,
    () => mainChart.addLineSeries({{ color:'#4da6ff', lineWidth:1, crosshairMarkerVisible:false }}),
    calcSMA(data, p_sma20));

  _updateLine('sma50', document.getElementById('i-sma50').checked,
    () => mainChart.addLineSeries({{ color:'#b388ff', lineWidth:1, crosshairMarkerVisible:false }}),
    calcSMA(data, p_sma50));

  _updateLine('ema20', document.getElementById('i-ema20').checked,
    () => mainChart.addLineSeries({{ color:'#00e676', lineWidth:1, lineStyle:LightweightCharts.LineStyle.Dashed, crosshairMarkerVisible:false }}),
    calcEMA(data, p_ema20));

  _updateLine('ema50', document.getElementById('i-ema50').checked,
    () => mainChart.addLineSeries({{ color:'#00bcd4', lineWidth:1, lineStyle:LightweightCharts.LineStyle.Dashed, crosshairMarkerVisible:false }}),
    calcEMA(data, p_ema50));

  _updateLine('vwap', document.getElementById('i-vwap').checked,
    () => mainChart.addLineSeries({{ color:'#ffd166', lineWidth:1, lineStyle:LightweightCharts.LineStyle.Dotted, crosshairMarkerVisible:false }}),
    calcVWAP(data));

  // BB (3 series)
  if (document.getElementById('i-bb').checked) {{
    const bb = calcBB(data, p_bb);
    if (!IS.bbU) {{
      IS.bbU = mainChart.addLineSeries({{ color:'rgba(255,112,67,0.55)', lineWidth:1, lineStyle:LightweightCharts.LineStyle.Dashed, crosshairMarkerVisible:false }});
      IS.bbL = mainChart.addLineSeries({{ color:'rgba(255,112,67,0.55)', lineWidth:1, lineStyle:LightweightCharts.LineStyle.Dashed, crosshairMarkerVisible:false }});
      IS.bbM = mainChart.addLineSeries({{ color:'rgba(255,112,67,0.25)', lineWidth:1, crosshairMarkerVisible:false }});
    }}
    IS.bbU.setData(bb.upper);
    IS.bbL.setData(bb.lower);
    IS.bbM.setData(bb.mid);
  }} else {{
    ['bbU','bbL','bbM'].forEach(k => {{
      if (IS[k]) {{ mainChart.removeSeries(IS[k]); delete IS[k]; }}
    }});
  }}

  // RSI
  if (document.getElementById('i-rsi').checked && data.length > p_rsi+1) {{
    const rsiData = calcRSI(data, p_rsi);
    rsiSeries.setData(rsiData);
    const refData = rsiData.map(d => ({{ time:d.time, value:70 }}));
    const refData2 = rsiData.map(d => ({{ time:d.time, value:30 }}));
    rsiOB.setData(refData);
    rsiOS.setData(refData2);
  }}

  // MACD
  if (document.getElementById('i-macd').checked && data.length > 30) {{
    const md = calcMACD(data);
    macdFastSeries.setData(md.map(d=>({{time:d.time,value:d.macd}})));
    macdSignSeries.setData(md.map(d=>({{time:d.time,value:d.signal}})));
    macdHistSeries.setData(md.map(d=>({{
      time:d.time, value:d.hist,
      color:d.hist>=0?'rgba(0,230,118,0.5)':'rgba(255,61,87,0.5)'
    }})));
  }}

  // Entry price line
  if (position) {{
    if (!IS.posLine) {{
      IS.posLine = mainChart.addLineSeries({{
        color: position.dir==='buy'?'rgba(0,230,118,0.6)':'rgba(255,61,87,0.6)',
        lineWidth:1, lineStyle:LightweightCharts.LineStyle.Dotted,
        crosshairMarkerVisible:false, lastValueVisible:true,
        priceLineVisible:false,
      }});
    }}
    const posData = ALL.slice(0, curBar+1)
      .filter(b=>b.Date>=position.date)
      .map(b=>({{time:toTime(b.Date), value:position.entry}}));
    if (posData.length) IS.posLine.setData(posData);
  }} else if (IS.posLine) {{
    mainChart.removeSeries(IS.posLine); delete IS.posLine;
  }}

  updateBarStrip();
  updateMetrics();
  updatePosBox();
  document.getElementById('bar-pos').textContent = (curBar+1)+' / '+N;
  document.getElementById('scrubber').value = curBar;
  document.getElementById('trade-price').value = ALL[curBar].Close.toFixed(2);
}}

function _updateLine(id, enabled, factory, data) {{
  if (enabled) {{
    if (!IS[id]) IS[id] = factory();
    IS[id].setData(data);
  }} else if (IS[id]) {{
    mainChart.removeSeries(IS[id]); delete IS[id];
  }}
}}

// ═══════════════════════════════════════════════════════════
// BAR INFO STRIP
// ═══════════════════════════════════════════════════════════
function updateBarStrip() {{
  const b    = ALL[curBar];
  const prev = ALL[Math.max(0, curBar-1)];
  const chg  = b.Close - prev.Close;
  const pct  = (chg/prev.Close*100);

  document.getElementById('bs-date').textContent  = b.Date;
  document.getElementById('bs-open').textContent  = '$'+b.Open.toFixed(2);
  document.getElementById('bs-high').textContent  = '$'+b.High.toFixed(2);
  document.getElementById('bs-low').textContent   = '$'+b.Low.toFixed(2);
  document.getElementById('bs-close').textContent = '$'+b.Close.toFixed(2);

  const chgEl = document.getElementById('bs-chg');
  chgEl.textContent = (chg>=0?'▲':'▼')+' '+Math.abs(chg).toFixed(2)+' ('+pct.toFixed(2)+'%)';
  chgEl.className   = chg>=0?'bs-up':'bs-dn';

  const vol = b.Volume;
  document.getElementById('bs-vol').textContent =
    vol>1e9 ? (vol/1e9).toFixed(2)+'B' :
    vol>1e6 ? (vol/1e6).toFixed(2)+'M' :
    vol>1e3 ? (vol/1e3).toFixed(1)+'K' : vol.toFixed(0);
}}

// ═══════════════════════════════════════════════════════════
// METRICS
// ═══════════════════════════════════════════════════════════
function updateMetrics() {{
  const curP = ALL[curBar].Close;
  let openVal = 0, openPnl = 0;
  if (position) {{
    openVal = position.dir==='buy' ? curP*position.qty : 0;
    openPnl = position.dir==='buy'
      ? (curP-position.entry)*position.qty
      : (position.entry-curP)*position.qty;
  }}
  const port = cash + openVal;
  const ret  = (port-CAP)/CAP*100;
  const tc   = trades.filter(t=>t.dir==='close').length;
  const wr   = tc>0 ? (wins/tc*100).toFixed(0)+'%' : '—';

  _setMc('m-port', '$'+fmt(port), ret>=0?'pos':'neg');
  _setMc('m-cash', '$'+fmt(cash), 'dim');
  _setMc('m-ret',  (ret>=0?'+':'')+ret.toFixed(2)+'%', ret>=0?'pos':'neg');
  _setMc('m-pnl',  (realisedPnl>=0?'+':'')+fmt(Math.abs(realisedPnl),true,realisedPnl), realisedPnl>0?'pos':realisedPnl<0?'neg':'dim');
  _setMc('m-open', position?((openPnl>=0?'+':'')+fmt(Math.abs(openPnl),true,openPnl)):'—', openPnl>0?'pos':openPnl<0?'neg':'dim');
  _setMc('m-wr', wr, 'dim');
  document.getElementById('m-tc').textContent = trades.length;
}}

function _setMc(id, val, cls) {{
  const el = document.getElementById(id);
  el.textContent = val;
  el.className = 'mc-val' + (cls?' '+cls:'');
}}

function fmt(v, signed=false, raw=0) {{
  const s = v>=1e6?(v/1e6).toFixed(2)+'M':v>=1e3?(v/1e3).toFixed(1)+'K':v.toFixed(0);
  return (signed&&raw<0?'-':'') + '$'+s;
}}

// ═══════════════════════════════════════════════════════════
// POSITION BOX
// ═══════════════════════════════════════════════════════════
function updatePosBox() {{
  const pb = document.getElementById('pos-box');
  if (!position) {{ pb.style.display='none'; return; }}
  pb.style.display='block';
  pb.className = position.dir==='short' ? 'short' : '';
  const dir = document.getElementById('pos-dir');
  dir.textContent = '● ' + (position.dir==='buy'?'LONG':'SHORT');
  dir.className   = position.dir==='buy'?'':'short-dir';
  const curP = ALL[curBar].Close;
  const unreal = position.dir==='buy'
    ? (curP-position.entry)*position.qty
    : (position.entry-curP)*position.qty;
  document.getElementById('pos-detail').innerHTML =
    `${{position.qty}} shares @ $${{position.entry.toFixed(2)}}<br>`+
    `Cost: $${{(position.entry*position.qty).toFixed(0)}}<br>`+
    `<span id="pos-unreal" style="color:${{unreal>=0?'#00e676':'#ff3d57'}};font-weight:700;">`+
    `P&L: ${{(unreal>=0?'+':'')+unreal.toFixed(2)}}</span>`;
}}

// ═══════════════════════════════════════════════════════════
// TRADE EXECUTION
// ═══════════════════════════════════════════════════════════
function executeTrade(dir) {{
  const qty   = Math.max(1, parseInt(document.getElementById('trade-qty').value)||10);
  const price = parseFloat(document.getElementById('trade-price').value)||ALL[curBar].Close;
  const date  = ALL[curBar].Date;
  const time  = new Date().toTimeString().slice(0,5);

  if (dir === 'buy') {{
    if (position) {{ toast('Close current position first.','#ffd166'); return; }}
    const cost = price*qty;
    if (cost > cash) {{ toast('Insufficient cash!','#ff3d57'); return; }}
    cash -= cost;
    position = {{dir:'buy', entry:price, qty, date}};
    trades.push({{dir:'buy', price, qty, date, pnl:0, time}});
    toast(`BUY ${{qty}} @ $${{price.toFixed(2)}}`,'#00e676');
  }} else if (dir === 'short') {{
    if (position) {{ toast('Close current position first.','#ffd166'); return; }}
    cash += price*qty;
    position = {{dir:'short', entry:price, qty, date}};
    trades.push({{dir:'short', price, qty, date, pnl:0, time}});
    toast(`SHORT ${{qty}} @ $${{price.toFixed(2)}}`,'#ff3d57');
  }} else if (dir === 'close') {{
    if (!position) {{ toast('No open position.','#ffd166'); return; }}
    const pnl = position.dir==='buy'
      ? (price-position.entry)*position.qty
      : (position.entry-price)*position.qty;
    if (position.dir==='buy') cash += price*position.qty;
    else cash -= price*position.qty;
    realisedPnl += pnl;
    if (pnl>0) wins++;
    trades.push({{dir:'close', price, qty:position.qty, date, pnl, time}});
    toast(`CLOSED — P&L: ${{(pnl>=0?'+':'')+pnl.toFixed(2)}}`, pnl>=0?'#00e676':'#ff3d57');
    position = null;
  }}
  renderTradeLog();
  renderAll();
}}

function renderTradeLog() {{
  document.getElementById('trade-log').innerHTML = [...trades].reverse().map(t => {{
    const cls  = t.dir==='buy'?'lr-buy':t.dir==='short'?'lr-short':'lr-close';
    const pnlS = t.dir==='close'?((t.pnl>=0?'+':'')+t.pnl.toFixed(2)):'—';
    const pnlC = t.pnl>0?'lr-pos':t.pnl<0?'lr-neg':'lr-dim';
    return `<div class="log-row">
      <span class="lr-time">${{t.time}}</span>
      <span class="${{cls}}">${{t.dir.toUpperCase()}}</span>
      <span class="lr-price">$${{t.price.toFixed(2)}}</span>
      <span class="${{pnlC}}">${{pnlS}}</span>
    </div>`;
  }}).join('');
}}

// ═══════════════════════════════════════════════════════════
// TOAST
// ═══════════════════════════════════════════════════════════
let _tt = null;
function toast(msg, color='#00e676') {{
  const el = document.getElementById('toast');
  el.textContent = msg;
  el.style.display='block';
  el.style.color = color;
  el.style.borderColor = color;
  if (_tt) clearTimeout(_tt);
  _tt = setTimeout(()=>el.style.display='none', 2200);
}}

// ═══════════════════════════════════════════════════════════
// PLAYBACK
// ═══════════════════════════════════════════════════════════
function onSpeedChange(v) {{
  speed = SPEEDS[v-1];
  document.getElementById('speed-val').textContent = speed + '×';
  if (isPlaying) {{ stopPlay(); startPlay(); }}
}}

function startPlay() {{
  if (playTimer) clearInterval(playTimer);
  const ms = Math.max(30, Math.round(1000/speed));
  playTimer = setInterval(() => {{
    if (curBar >= N-1) {{ stopPlay(); return; }}
    curBar++;
    renderAll();
    mainChart.timeScale().scrollToPosition(3, false);
  }}, ms);
}}

function stopPlay() {{
  clearInterval(playTimer); playTimer=null;
}}

function togglePlay() {{
  isPlaying = !isPlaying;
  const btn = document.getElementById('btn-play');
  if (isPlaying) {{
    startPlay();
    btn.textContent='⏸ Pause'; btn.classList.add('playing');
  }} else {{
    stopPlay();
    btn.textContent='▶ Play'; btn.classList.remove('playing');
  }}
}}

function stepBars(n) {{
  if (isPlaying) {{ stopPlay(); isPlaying=false; document.getElementById('btn-play').textContent='▶ Play'; document.getElementById('btn-play').classList.remove('playing'); }}
  curBar = Math.max(30, Math.min(N-1, curBar+n));
  renderAll();
}}

function scrubTo(n) {{
  if (isPlaying) {{ stopPlay(); isPlaying=false; document.getElementById('btn-play').textContent='▶ Play'; document.getElementById('btn-play').classList.remove('playing'); }}
  curBar = Math.max(30, Math.min(N-1, n));
  renderAll();
}}

// ═══════════════════════════════════════════════════════════
// CHART TYPE
// ═══════════════════════════════════════════════════════════
function setChartType(t) {{
  chartType = t;
  document.querySelectorAll('[id^="ct-"]').forEach(b=>b.classList.remove('ct-on'));
  document.getElementById('ct-'+t).classList.add('ct-on');
  createMainSeries(t);
  renderAll();
}}

// ═══════════════════════════════════════════════════════════
// SUBCHART TOGGLE
// ═══════════════════════════════════════════════════════════
function toggleSubChart(name, on) {{
  const el = document.getElementById(name+'-chart');
  el.style.display = on ? 'block' : 'none';
  if (on) renderAll();
  resize();
}}

// ═══════════════════════════════════════════════════════════
// DRAWING TOOLS
// ═══════════════════════════════════════════════════════════
let _drawState = {{pts:[], series:[]}};

function setDraw(mode) {{
  drawMode = mode;
  document.querySelectorAll('.draw-btn').forEach(b=>b.classList.remove('on'));
  if (mode!=='cursor') document.getElementById('draw-'+mode).classList.add('on');
  else document.getElementById('draw-cursor').classList.add('on');
  _drawState = {{pts:[], series:[]}};
  // Enable/disable chart panning
  const scroll = mode==='cursor';
  mainChart.applyOptions({{handleScroll:scroll, handleScale:scroll}});
}}

function getDrawColor() {{ return document.getElementById('draw-color-pick').value; }}

mainChart.subscribeClick(param => {{
  if (drawMode==='cursor'||!param.time) return;
  const price = mainSeries.coordinateToPrice(param.point.y);
  const time  = param.time;
  const color = getDrawColor();

  if (drawMode==='hline') {{
    const s = mainChart.addLineSeries({{
      color:color+'bb', lineWidth:1,
      lineStyle:LightweightCharts.LineStyle.Dashed,
      crosshairMarkerVisible:false, lastValueVisible:false,
    }});
    // Extend to all visible bars
    const pts = ALL.slice(0, curBar+1).map(b=>({{time:toTime(b.Date), value:price}}));
    s.setData(pts);
    drawSegs.push({{series:[s]}});
    toast('H-Line @ $'+price.toFixed(2),'#ffd166');

  }} else if (drawMode==='vline') {{
    // V-line: use a histogram column at that time
    // Actually draw a very tall/short range series spanning price axis
    const lo = Math.min(...ALL.slice(0,curBar+1).map(b=>b.Low))*0.8;
    const hi = Math.max(...ALL.slice(0,curBar+1).map(b=>b.High))*1.2;
    const s = mainChart.addLineSeries({{
      color:color+'99', lineWidth:1,
      lineStyle:LightweightCharts.LineStyle.Dashed,
      crosshairMarkerVisible:false, lastValueVisible:false,
    }});
    s.setData([{{time, value:lo}},{{time, value:hi}}]);
    drawSegs.push({{series:[s]}});
    toast('V-Line drawn','#ffd166');

  }} else if (drawMode==='trend'||drawMode==='ray') {{
    if (_drawState.pts.length===0) {{
      _drawState.pts=[{{time,price}}];
      toast('Click second point…','#ffd166');
    }} else {{
      const p1=_drawState.pts[0], p2={{time,price}};
      const s = mainChart.addLineSeries({{
        color, lineWidth:1.5,
        crosshairMarkerVisible:false, lastValueVisible:false,
      }});
      let pts=[{{time:p1.time,value:p1.price}},{{time:p2.time,value:p2.price}}];
      if (drawMode==='ray') {{
        // Extend to last bar
        const i1=ALL.findIndex(b=>toTime(b.Date)>=p1.time);
        const i2=ALL.findIndex(b=>toTime(b.Date)>=p2.time);
        const iLast=curBar;
        if (i1>=0&&i2>i1) {{
          const slope=(p2.price-p1.price)/(i2-i1);
          pts.push({{time:toTime(ALL[iLast].Date), value:p2.price+slope*(iLast-i2)}});
        }}
      }}
      s.setData(pts);
      drawSegs.push({{series:[s]}});
      _drawState={{pts:[],series:[]}};
      toast('Line drawn','#ffd166');
    }}

  }} else if (drawMode==='fib') {{
    if (_drawState.pts.length===0) {{
      _drawState.pts=[{{time,price}}];
      toast('Click end of Fibonacci range…','#ffd166');
    }} else {{
      const p1=_drawState.pts[0], p2={{time,price}};
      const hi=Math.max(p1.price,p2.price), lo=Math.min(p1.price,p2.price);
      const rng=hi-lo;
      const fibs=[0,0.236,0.382,0.5,0.618,0.764,1.0];
      const fibColors=['#ffffff','#4da6ff','#00e676','#ffd166','#ff9800','#b388ff','#ff3d57'];
      const newSeries=[];
      fibs.forEach((f,i)=>{{
        const val=hi-rng*f;
        const s=mainChart.addLineSeries({{
          color:fibColors[i]+'88', lineWidth:1,
          lineStyle:LightweightCharts.LineStyle.Dashed,
          crosshairMarkerVisible:false,
          lastValueVisible:true,
          priceFormat:{{type:'custom',formatter:()=>(f*100)+'%'}},
        }});
        s.setData([{{time:p1.time,value:val}},{{time:p2.time,value:val}}]);
        newSeries.push(s);
      }});
      drawSegs.push({{series:newSeries}});
      _drawState={{pts:[],series:[]}};
      toast('Fibonacci levels drawn','#ffd166');
    }}

  }} else if (drawMode==='rect') {{
    if (_drawState.pts.length===0) {{
      _drawState.pts=[{{time,price}}];
      toast('Click opposite corner…','#ffd166');
    }} else {{
      const p1=_drawState.pts[0], p2={{time,price}};
      const hi=Math.max(p1.price,p2.price), lo=Math.min(p1.price,p2.price);
      const t1=p1.time<p2.time?p1.time:p2.time;
      const t2=p1.time<p2.time?p2.time:p1.time;
      const sides=[
        [{{time:t1,value:hi}},{{time:t2,value:hi}}],
        [{{time:t1,value:lo}},{{time:t2,value:lo}}],
        [{{time:t1,value:hi}},{{time:t1,value:lo}}],
        [{{time:t2,value:hi}},{{time:t2,value:lo}}],
      ];
      const newSeries=sides.map(pts=>{{
        const s=mainChart.addLineSeries({{
          color:color+'aa', lineWidth:1,
          crosshairMarkerVisible:false, lastValueVisible:false,
        }});
        s.setData(pts); return s;
      }});
      // Filled area between top and bottom
      const areaS=mainChart.addAreaSeries({{
        lineColor:'transparent',
        topColor:color+'15', bottomColor:color+'05',
        crosshairMarkerVisible:false, lastValueVisible:false,
      }});
      areaS.setData([{{time:t1,value:hi}},{{time:t2,value:hi}}]);
      const areaL=mainChart.addAreaSeries({{
        lineColor:'transparent',
        topColor:color+'00', bottomColor:color+'00',
        crosshairMarkerVisible:false, lastValueVisible:false,
      }});
      areaL.setData([{{time:t1,value:lo}},{{time:t2,value:lo}}]);
      drawSegs.push({{series:[...newSeries,areaS,areaL]}});
      _drawState={{pts:[],series:[]}};
      toast('Box drawn','#ffd166');
    }}

  }} else if (drawMode==='mark') {{
    const idx=ALL.findIndex(b=>toTime(b.Date)>=time);
    if (idx>=0&&idx<=curBar) {{
      userMarks.push({{
        date:ALL[idx].Date,
        marker:{{
          time:toTime(ALL[idx].Date),
          position:'aboveBar',
          color,
          shape:'circle',
          text:'✦',
          size:0,
        }}
      }});
      renderAll();
      toast('Marker placed','#ffd166');
    }}
  }}
}});

function clearAllDrawings() {{
  drawSegs.forEach(seg=>seg.series.forEach(s=>mainChart.removeSeries(s)));
  drawSegs=[]; userMarks=[];
  renderAll();
  toast('Drawings cleared','#ffd166');
}}

// ═══════════════════════════════════════════════════════════
// KEYBOARD SHORTCUTS
// ═══════════════════════════════════════════════════════════
document.addEventListener('keydown', e => {{
  const tag=e.target.tagName;
  if (tag==='INPUT'||tag==='SELECT'||tag==='TEXTAREA') return;
  switch(e.code) {{
    case 'Space':      e.preventDefault(); togglePlay(); break;
    case 'ArrowRight': stepBars(e.shiftKey?10:1);  break;
    case 'ArrowLeft':  stepBars(e.shiftKey?-10:-1); break;
    case 'KeyB':       executeTrade('buy');   break;
    case 'KeyS':       executeTrade('short'); break;
    case 'KeyC':       executeTrade('close'); break;
    case 'KeyR':       renderAll();           break;
  }}
}});

// ═══════════════════════════════════════════════════════════
// RESIZE
// ═══════════════════════════════════════════════════════════
function resize() {{
  const chartCol  = document.getElementById('chart-col');
  const totalH    = chartCol.offsetHeight;
  const subH      = (document.getElementById('rsi-chart').style.display!=='none'?70:0)+
                    (document.getElementById('macd-chart').style.display!=='none'?70:0);
  const drawBarH  = document.getElementById('draw-bar').offsetHeight;
  const mainH     = Math.max(200, totalH - 72 - subH - drawBarH - 2);

  const w = chartCol.offsetWidth;
  mainChart.resize(w, mainH);
  volChart.resize(w, 72);
  rsiChart.resize(w, 70);
  macdChart.resize(w, 70);
}}

const ro = new ResizeObserver(resize);
ro.observe(document.getElementById('chart-col'));

// ═══════════════════════════════════════════════════════════
// INIT
// ═══════════════════════════════════════════════════════════
// Restore trades from Python session
trades.forEach(t => {{
  if (t.dir==='close') {{ realisedPnl+=t.pnl; if(t.pnl>0) wins++; }}
}});
// Recompute cash + position
cash=CAP; position=null;
let openTrade=null;
trades.forEach(t => {{
  if (t.dir==='buy')   {{ cash-=t.price*t.qty; openTrade=t; }}
  if (t.dir==='short') {{ cash+=t.price*t.qty; openTrade=t; }}
  if (t.dir==='close'&&openTrade) {{
    if (openTrade.dir==='buy') cash+=t.price*openTrade.qty;
    else cash-=t.price*openTrade.qty;
    openTrade=null; position=null;
  }}
}});
if (openTrade) position={{dir:openTrade.dir,entry:openTrade.price,qty:openTrade.qty,date:openTrade.date}};

onSpeedChange(3); // init speed display
renderAll();
renderTradeLog();
mainChart.timeScale().fitContent();
setTimeout(()=>mainChart.timeScale().scrollToRealTime(),200);

toast('Chart loaded · SPACE=Play · B=Buy · S=Short · C=Close · ←/→=Step','#00e676');
</script>
</body>
</html>"""

    components.html(HTML, height=900, scrolling=False)
