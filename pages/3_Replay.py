import streamlit as st
import sys, os
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.styles import SHARED_CSS
from utils.nav import navbar

st.set_page_config(page_title="Replay — 11%", page_icon="$", layout="wide", initial_sidebar_state="collapsed")
st.markdown(SHARED_CSS, unsafe_allow_html=True)
navbar()

st.markdown("""
<style>
@keyframes fadeUp { from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:translateY(0)} }
.rp-title { font-family:'Bebas Neue',sans-serif; font-size:2.4rem; letter-spacing:0.04em; color:#eef2f7; line-height:1; }
.rp-sub   { font-size:0.84rem; color:#3a4a5e; line-height:1.6; margin-top:0.3rem; }
.ctrl-card { background:#0c1018; border:1px solid #1a2235; border-radius:10px; padding:1rem 1.2rem; }
.ctrl-label { font-family:'IBM Plex Mono',monospace; font-size:0.52rem; text-transform:uppercase; letter-spacing:0.18em; color:#3a4a5e; margin-bottom:0.4rem; }
.chip { display:inline-flex; align-items:center; gap:0.4rem; padding:0.22rem 0.7rem; border-radius:4px;
    font-family:'IBM Plex Mono',monospace; font-size:0.58rem; font-weight:600; }
.chip-green { background:rgba(0,230,118,0.1); border:1px solid rgba(0,230,118,0.25); color:#00e676; }
.chip-red   { background:rgba(255,61,87,0.1);  border:1px solid rgba(255,61,87,0.25);  color:#ff3d57; }
.chip-blue  { background:rgba(77,166,255,0.1); border:1px solid rgba(77,166,255,0.25); color:#4da6ff; }
.chip-dim   { background:rgba(58,74,94,0.15);  border:1px solid #1a2235; color:#3a4a5e; }
.trade-row { display:grid; grid-template-columns:80px 60px 80px 80px 80px 1fr; gap:0.5rem;
    align-items:center; padding:0.55rem 0.8rem; border-bottom:1px solid #0d1117;
    font-family:'IBM Plex Mono',monospace; font-size:0.65rem; }
.trade-row:last-child { border-bottom:none; }
.trade-row:hover { background:rgba(255,255,255,0.01); }
.metric-mini { background:#0c1018; border:1px solid #1a2235; border-radius:8px; padding:0.8rem 1rem; }
.metric-val { font-family:'IBM Plex Mono',monospace; font-size:1.2rem; font-weight:700; line-height:1; }
.metric-lbl { font-family:'IBM Plex Mono',monospace; font-size:0.5rem; text-transform:uppercase; letter-spacing:0.16em; color:#3a4a5e; margin-top:0.25rem; }
.pos { color:#00e676; } .neg { color:#ff3d57; } .neu { color:#eef2f7; }
</style>
""", unsafe_allow_html=True)

# ── Session state init ────────────────────────────────────────────────────────
if "rp_trades"   not in st.session_state: st.session_state["rp_trades"]   = []
if "rp_position" not in st.session_state: st.session_state["rp_position"] = None  # {size, entry, direction}
if "rp_capital"  not in st.session_state: st.session_state["rp_capital"]  = 10000.0
if "rp_cash"     not in st.session_state: st.session_state["rp_cash"]     = 10000.0

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(
    '<div style="padding:1.5rem 0 1rem;">'
    '<div class="rp-title">Market Replay</div>'
    '<div class="rp-sub">Full TradingView chart with built-in bar replay. '
    'Use the controls below to simulate trades as you step through history.</div>'
    '</div>',
    unsafe_allow_html=True
)

# ── Controls row ──────────────────────────────────────────────────────────────
ctl1, ctl2, ctl3, ctl4 = st.columns([2, 1.2, 1.2, 1.2])

with ctl1:
    ticker = st.text_input("Ticker", value="NASDAQ:AAPL",
                           placeholder="EXCHANGE:SYMBOL e.g. NASDAQ:AAPL",
                           label_visibility="collapsed").strip().upper() or "NASDAQ:AAPL"

with ctl2:
    interval = st.selectbox("Interval",
        ["1","5","15","30","60","240","D","W"],
        index=6, label_visibility="collapsed",
        format_func=lambda x: {"1":"1m","5":"5m","15":"15m","30":"30m","60":"1h","240":"4h","D":"1D","W":"1W"}[x]
    )

with ctl3:
    capital_input = st.number_input("Capital $", value=st.session_state["rp_capital"],
                                    min_value=100.0, step=500.0, label_visibility="collapsed")
    if capital_input != st.session_state["rp_capital"] and not st.session_state["rp_trades"]:
        st.session_state["rp_capital"] = capital_input
        st.session_state["rp_cash"]    = capital_input

with ctl4:
    if st.button("Reset Session", use_container_width=True):
        st.session_state["rp_trades"]   = []
        st.session_state["rp_position"] = None
        st.session_state["rp_cash"]     = st.session_state["rp_capital"]
        st.rerun()

# ── TradingView chart ─────────────────────────────────────────────────────────
st.components.v1.html(f"""
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body,html {{ background:#06080c; }}
.tv-outer {{
    border:1px solid #1a2235;
    border-radius:12px;
    overflow:hidden;
    height:620px;
}}
.tv-inner {{
    height:100%;
    width:100%;
    background:#06080c;
}}
</style>
<div class="tv-outer">
  <div class="tv-inner">
    <div class="tradingview-widget-container" style="height:100%;width:100%;">
      <div id="tv_replay" style="height:100%;width:100%;"></div>
      <script src="https://s3.tradingview.com/tv.js"></script>
      <script>
      new TradingView.widget({{
        autosize: true,
        symbol: "{ticker}",
        interval: "{interval}",
        timezone: "America/New_York",
        theme: "dark",
        style: "1",
        locale: "en",
        toolbar_bg: "#06080c",
        enable_publishing: false,
        hide_side_toolbar: false,
        hide_top_toolbar: false,
        withdateranges: true,
        allow_symbol_change: true,
        save_image: true,
        container_id: "tv_replay",
        backgroundColor: "rgba(6,8,12,1)",
        gridColor: "rgba(26,34,53,0.5)",
        studies: ["Volume@tv-basicstudies"],
        overrides: {{
          "mainSeriesProperties.candleStyle.upColor":       "#00e676",
          "mainSeriesProperties.candleStyle.downColor":     "#ff3d57",
          "mainSeriesProperties.candleStyle.borderUpColor": "#00e676",
          "mainSeriesProperties.candleStyle.borderDownColor":"#ff3d57",
          "mainSeriesProperties.candleStyle.wickUpColor":   "#00e676",
          "mainSeriesProperties.candleStyle.wickDownColor": "#ff3d57",
          "paneProperties.background":                      "#06080c",
          "paneProperties.backgroundType":                  "solid",
          "paneProperties.vertGridProperties.color":        "#1a2235",
          "paneProperties.horzGridProperties.color":        "#1a2235",
          "scalesProperties.textColor":                     "#3a4a5e",
          "scalesProperties.lineColor":                     "#1a2235"
        }}
      }});
      </script>
    </div>
  </div>
</div>
""", height=640, scrolling=False)

st.markdown(
    '<div style="background:rgba(77,166,255,0.06);border:1px solid rgba(77,166,255,0.18);'
    'border-radius:8px;padding:0.6rem 1rem;margin:0.6rem 0;'
    'font-family:IBM Plex Mono,monospace;font-size:0.62rem;color:#4da6ff;line-height:1.6;">'
    '⏱ <strong>Enter Replay:</strong> Click the <strong>clock icon ⏱</strong> in the TradingView toolbar, '
    'then pick a start date on the chart. Use ▶ / ▶| to play or step bar by bar. '
    'Log your trades below as you go.'
    '</div>',
    unsafe_allow_html=True
)

# ── Trade simulator ───────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    '<div style="font-family:IBM Plex Mono,monospace;font-size:0.58rem;text-transform:uppercase;'
    'letter-spacing:0.2em;color:#3a4a5e;margin-bottom:1rem;">Trade Journal</div>',
    unsafe_allow_html=True
)

pos = st.session_state["rp_position"]
cash = st.session_state["rp_cash"]

# ── Metrics strip ──────────────────────────────────────────────────────────────
trades = st.session_state["rp_trades"]
total_pnl   = sum(t["pnl"] for t in trades)
win_trades  = [t for t in trades if t["pnl"] > 0]
win_rate    = len(win_trades)/len(trades)*100 if trades else 0
portfolio   = cash + (0 if pos is None else 0)  # open position not counted until closed
ret_pct     = (portfolio - st.session_state["rp_capital"]) / st.session_state["rp_capital"] * 100

m1,m2,m3,m4,m5 = st.columns(5)
for col, val, lbl, cls in [
    (m1, f"${portfolio:,.2f}",       "Portfolio",    "neu"),
    (m2, f"${cash:,.2f}",            "Cash",         "neu"),
    (m3, f"{ret_pct:+.2f}%",         "Total Return", "pos" if ret_pct>=0 else "neg"),
    (m4, f"${total_pnl:+,.2f}",      "Realised P&L", "pos" if total_pnl>=0 else "neg"),
    (m5, f"{win_rate:.0f}%",         "Win Rate",     "pos" if win_rate>=50 else "neg" if trades else "neu"),
]:
    col.markdown(
        f'<div class="metric-mini">'
        f'<div class="metric-val {cls}">{val}</div>'
        f'<div class="metric-lbl">{lbl}</div>'
        f'</div>',
        unsafe_allow_html=True
    )

st.markdown('<div style="height:0.8rem;"></div>', unsafe_allow_html=True)

# ── Open position display ─────────────────────────────────────────────────────
if pos:
    st.markdown(
        f'<div style="background:rgba(0,230,118,0.06);border:1px solid rgba(0,230,118,0.2);'
        f'border-radius:8px;padding:0.75rem 1rem;margin-bottom:0.8rem;'
        f'font-family:IBM Plex Mono,monospace;font-size:0.68rem;color:#eef2f7;'
        f'display:flex;gap:2rem;align-items:center;">'
        f'<span style="color:#00e676;font-weight:700;">● OPEN {pos["direction"].upper()}</span>'
        f'<span>{pos["size"]} shares @ ${pos["entry"]:.2f}</span>'
        f'<span style="color:#3a4a5e;">Cost: ${pos["size"]*pos["entry"]:,.2f}</span>'
        f'</div>',
        unsafe_allow_html=True
    )

# ── Trade entry form ──────────────────────────────────────────────────────────
with st.container():
    st.markdown('<div class="ctrl-card">', unsafe_allow_html=True)
    fc1, fc2, fc3, fc4, fc5 = st.columns([1.5, 1.2, 1, 1, 1])

    with fc1:
        action = st.selectbox("Action", ["BUY (Long)", "SELL SHORT", "CLOSE POSITION"],
                              label_visibility="visible")
    with fc2:
        price = st.number_input("Price $", value=100.0, min_value=0.01, step=0.01,
                                format="%.2f", label_visibility="visible")
    with fc3:
        shares = st.number_input("Shares", value=10, min_value=1, step=1,
                                 label_visibility="visible")
    with fc4:
        note = st.text_input("Note", placeholder="e.g. breakout", label_visibility="visible")
    with fc5:
        st.markdown('<div style="height:28px;"></div>', unsafe_allow_html=True)
        submit = st.button("Log Trade ▶", type="primary", use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

if submit:
    now_str = datetime.now().strftime("%H:%M:%S")
    cost = price * shares

    if action == "BUY (Long)":
        if cost > cash:
            st.error(f"Not enough cash. Need ${cost:,.2f}, have ${cash:,.2f}")
        else:
            st.session_state["rp_cash"] -= cost
            st.session_state["rp_position"] = {"direction":"long","entry":price,"size":shares}
            st.session_state["rp_trades"].append({
                "time":now_str,"action":"BUY","price":price,
                "shares":shares,"pnl":0,"note":note,"open":True
            })
            st.rerun()

    elif action == "SELL SHORT":
        # Short: credit cash, track position
        st.session_state["rp_cash"] += cost
        st.session_state["rp_position"] = {"direction":"short","entry":price,"size":shares}
        st.session_state["rp_trades"].append({
            "time":now_str,"action":"SHORT","price":price,
            "shares":shares,"pnl":0,"note":note,"open":True
        })
        st.rerun()

    elif action == "CLOSE POSITION":
        if pos is None:
            st.error("No open position to close.")
        else:
            if pos["direction"] == "long":
                pnl = (price - pos["entry"]) * pos["size"]
                st.session_state["rp_cash"] += price * pos["size"]
            else:  # short
                pnl = (pos["entry"] - price) * pos["size"]
                st.session_state["rp_cash"] -= price * pos["size"]

            st.session_state["rp_position"] = None
            st.session_state["rp_trades"].append({
                "time":now_str,"action":"CLOSE","price":price,
                "shares":pos["size"],"pnl":pnl,"note":note,"open":False
            })
            st.rerun()

# ── Trade log ────────────────────────────────────────────────────────────────
if trades:
    st.markdown(
        '<div style="font-family:IBM Plex Mono,monospace;font-size:0.52rem;text-transform:uppercase;'
        'letter-spacing:0.18em;color:#3a4a5e;margin:1rem 0 0.4rem;">'
        f'Trade Log — {len(trades)} trades</div>',
        unsafe_allow_html=True
    )
    # Header
    st.markdown(
        '<div style="display:grid;grid-template-columns:80px 60px 80px 80px 80px 1fr;gap:0.5rem;'
        'padding:0.4rem 0.8rem;font-family:IBM Plex Mono,monospace;font-size:0.5rem;'
        'text-transform:uppercase;letter-spacing:0.14em;color:#1a2235;border-bottom:1px solid #1a2235;">'
        '<span>Time</span><span>Action</span><span>Price</span><span>Shares</span><span>P&L</span><span>Note</span>'
        '</div>',
        unsafe_allow_html=True
    )
    rows_html = ""
    for t in reversed(trades):
        pnl_cls = "pos" if t["pnl"]>0 else ("neg" if t["pnl"]<0 else "neu")
        pnl_str = f"${t['pnl']:+,.2f}" if t["pnl"] != 0 else "—"
        act_color = "#00e676" if t["action"]=="BUY" else ("#ff3d57" if t["action"]=="SHORT" else "#ffd166")
        rows_html += (
            f'<div class="trade-row">'
            f'<span style="color:#3a4a5e;">{t["time"]}</span>'
            f'<span style="color:{act_color};font-weight:700;">{t["action"]}</span>'
            f'<span style="color:#eef2f7;">${t["price"]:.2f}</span>'
            f'<span style="color:#8896ab;">{t["shares"]}</span>'
            f'<span class="{pnl_cls}">{pnl_str}</span>'
            f'<span style="color:#3a4a5e;">{t.get("note","")}</span>'
            f'</div>'
        )
    st.markdown(
        '<div style="background:#0c1018;border:1px solid #1a2235;border-radius:10px;overflow:hidden;margin-top:0.2rem;">'
        + rows_html + '</div>',
        unsafe_allow_html=True
    )

    # Export
    if st.button("Export Trade Log as CSV"):
        df = pd.DataFrame(trades)
        st.download_button(
            "Download CSV", df.to_csv(index=False),
            file_name="replay_trades.csv", mime="text/csv"
        )
else:
    st.markdown(
        '<div style="background:#0c1018;border:1px solid #1a2235;border-radius:10px;'
        'padding:2rem;text-align:center;margin-top:0.5rem;">'
        '<div style="font-family:IBM Plex Mono,monospace;font-size:0.62rem;color:#1a2235;">'
        'No trades yet — use the form above to log entries as you replay the chart'
        '</div></div>',
        unsafe_allow_html=True
    )
