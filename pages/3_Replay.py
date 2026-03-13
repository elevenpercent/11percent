import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.styles import SHARED_CSS
from utils.nav import navbar

st.set_page_config(page_title="Replay — 11%", page_icon="$", layout="wide", initial_sidebar_state="collapsed")
st.markdown(SHARED_CSS, unsafe_allow_html=True)
st.markdown("""
<style>
.rp-title{font-family:'Bebas Neue',sans-serif;font-size:2.2rem;letter-spacing:0.04em;color:#eef2f7;line-height:1;}
.rp-sub{font-size:0.82rem;color:#3a4a5e;line-height:1.6;margin-top:0.25rem;}
.metric-mini{background:#0c1018;border:1px solid #1a2235;border-radius:8px;padding:0.75rem 1rem;}
.metric-val{font-family:'IBM Plex Mono',monospace;font-size:1.15rem;font-weight:700;line-height:1;}
.metric-lbl{font-family:'IBM Plex Mono',monospace;font-size:0.48rem;text-transform:uppercase;letter-spacing:0.15em;color:#3a4a5e;margin-top:0.2rem;}
.pos{color:#00e676;} .neg{color:#ff3d57;} .neu{color:#eef2f7;}
.trade-row{display:grid;grid-template-columns:70px 55px 75px 65px 75px 1fr;gap:0.4rem;
    align-items:center;padding:0.5rem 0.8rem;border-bottom:1px solid #0d1117;
    font-family:'IBM Plex Mono',monospace;font-size:0.62rem;}
.trade-row:last-child{border-bottom:none;}
.trade-hdr{background:#08100d;font-size:0.5rem;text-transform:uppercase;letter-spacing:0.14em;color:#1a2235;}
.replay-bar{background:#0c1018;border:1px solid #1a2235;border-radius:10px;padding:0.8rem 1rem;
    display:flex;align-items:center;gap:1rem;flex-wrap:wrap;margin-bottom:0.8rem;}
.bar-counter{font-family:'IBM Plex Mono',monospace;font-size:0.6rem;color:#3a4a5e;}
.bar-price{font-family:'IBM Plex Mono',monospace;font-size:1.1rem;font-weight:700;color:#eef2f7;}
.bar-chg-up{color:#00e676;font-family:'IBM Plex Mono',monospace;font-size:0.68rem;}
.bar-chg-dn{color:#ff3d57;font-family:'IBM Plex Mono',monospace;font-size:0.68rem;}
</style>
""", unsafe_allow_html=True)

navbar()

# ── Session state ──────────────────────────────────────────────────────────────
def _init():
    for k, v in [
        ("rp_df", None), ("rp_bar", 50), ("rp_ticker", "AAPL"),
        ("rp_trades", []), ("rp_position", None),
        ("rp_capital", 10000.0), ("rp_cash", 10000.0),
        ("rp_loaded", False),
    ]:
        if k not in st.session_state:
            st.session_state[k] = v
_init()

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(
    '<div style="padding:1.2rem 0 0.8rem;">'
    '<div class="rp-title">Market Replay</div>'
    '<div class="rp-sub">Load any stock, pick a start bar, then step forward one candle at a time — '
    'log trades as you go without knowing what comes next.</div>'
    '</div>',
    unsafe_allow_html=True
)

# ── Setup row ────────────────────────────────────────────────────────────────
s1, s2, s3, s4, s5 = st.columns([2, 1.2, 1.2, 1.2, 1.2])
with s1:
    ticker_in = st.text_input("Ticker", value=st.session_state["rp_ticker"],
                               placeholder="e.g. AAPL, TSLA, SPY",
                               label_visibility="collapsed").strip().upper()
with s2:
    period = st.selectbox("Period", ["6mo","1y","2y","5y"], index=1, label_visibility="collapsed")
with s3:
    start_bar = st.number_input("Start at bar", min_value=20, max_value=200, value=50, step=5,
                                 label_visibility="collapsed")
with s4:
    capital_in = st.number_input("Capital $", value=st.session_state["rp_capital"],
                                  min_value=100.0, step=500.0, label_visibility="collapsed")
with s5:
    load_btn = st.button("Load Chart", type="primary", use_container_width=True)

if load_btn or (ticker_in != st.session_state["rp_ticker"] and not st.session_state["rp_loaded"]):
    with st.spinner("Loading data..."):
        try:
            df = yf.Ticker(ticker_in).history(period=period, interval="1d")
            df = df[["Open","High","Low","Close","Volume"]].dropna().reset_index()
            df.columns = ["Date","Open","High","Low","Close","Volume"]
            if len(df) < 30:
                st.error("Not enough data for this ticker.")
            else:
                st.session_state["rp_df"]      = df
                st.session_state["rp_ticker"]  = ticker_in
                st.session_state["rp_bar"]     = min(start_bar, len(df) - 1)
                st.session_state["rp_trades"]  = []
                st.session_state["rp_position"]= None
                st.session_state["rp_capital"] = capital_in
                st.session_state["rp_cash"]    = capital_in
                st.session_state["rp_loaded"]  = True
                st.rerun()
        except Exception as e:
            st.error(f"Error loading {ticker_in}: {e}")

df = st.session_state["rp_df"]

if df is None:
    # Landing state — show the TradingView chart as a preview
    st.markdown(
        '<div style="background:rgba(0,230,118,0.04);border:1px solid rgba(0,230,118,0.15);'
        'border-radius:10px;padding:1.2rem 1.4rem;margin-bottom:1rem;'
        'font-family:IBM Plex Mono,monospace;font-size:0.68rem;color:#3a4a5e;line-height:1.8;">'
        '<span style="color:#00e676;font-weight:700;">How to use Replay</span><br>'
        '1. Enter a ticker above (e.g. AAPL, TSLA, NVDA, BTC-USD)<br>'
        '2. Choose a period and starting bar, then click <strong style="color:#eef2f7;">Load Chart</strong><br>'
        '3. Use Step Forward to reveal one candle at a time<br>'
        '4. Log your Buy / Short / Close trades as you go — P&amp;L tracked automatically'
        '</div>',
        unsafe_allow_html=True
    )

    # Show live TradingView chart as placeholder
    st.components.v1.html("""
<style>*{margin:0;padding:0;box-sizing:border-box;}body{background:#0c1018;}</style>
<div style="border:1px solid #1a2235;border-radius:12px;overflow:hidden;height:500px;">
  <div class="tradingview-widget-container" style="height:100%;width:100%;">
    <div id="tv_rp_preview" style="height:100%;width:100%;"></div>
    <script src="https://s3.tradingview.com/tv.js"></script>
    <script>
    new TradingView.widget({
      autosize:true, symbol:"NASDAQ:AAPL", interval:"D",
      timezone:"America/New_York", theme:"dark", style:"1", locale:"en",
      toolbar_bg:"#0c1018", enable_publishing:false, hide_side_toolbar:false,
      allow_symbol_change:true, save_image:true, container_id:"tv_rp_preview",
      backgroundColor:"rgba(12,16,24,1)", gridColor:"rgba(26,34,53,0.4)",
      overrides:{
        "mainSeriesProperties.candleStyle.upColor":"#00e676",
        "mainSeriesProperties.candleStyle.downColor":"#ff3d57",
        "mainSeriesProperties.candleStyle.borderUpColor":"#00e676",
        "mainSeriesProperties.candleStyle.borderDownColor":"#ff3d57",
        "mainSeriesProperties.candleStyle.wickUpColor":"#00e676",
        "mainSeriesProperties.candleStyle.wickDownColor":"#ff3d57",
        "paneProperties.background":"#0c1018","paneProperties.backgroundType":"solid",
        "paneProperties.vertGridProperties.color":"#1a2235",
        "paneProperties.horzGridProperties.color":"#1a2235",
        "scalesProperties.textColor":"#3a4a5e","scalesProperties.lineColor":"#1a2235"
      }
    });
    </script>
  </div>
</div>
""", height=510, scrolling=False)
    st.stop()

# ── Chart is loaded — replay mode ─────────────────────────────────────────────
bar_idx  = st.session_state["rp_bar"]
total    = len(df)
visible  = df.iloc[:bar_idx + 1]
cur_bar  = df.iloc[bar_idx]
cur_price = float(cur_bar["Close"])
cur_date  = pd.Timestamp(cur_bar["Date"]).strftime("%d %b %Y") if hasattr(cur_bar["Date"], "strftime") else str(cur_bar["Date"])[:10]

prev_price = float(df.iloc[bar_idx - 1]["Close"]) if bar_idx > 0 else cur_price
bar_chg    = cur_price - prev_price
bar_chg_pct = (bar_chg / prev_price) * 100 if prev_price else 0
chg_cls    = "bar-chg-up" if bar_chg >= 0 else "bar-chg-dn"
chg_arrow  = "▲" if bar_chg >= 0 else "▼"

# ── Current bar info strip ────────────────────────────────────────────────────
st.markdown(
    '<div class="replay-bar">'
    '<span style="font-family:IBM Plex Mono,monospace;font-size:0.7rem;color:#00e676;font-weight:700;">'
    + st.session_state["rp_ticker"] + '</span>'
    '<span class="bar-price">$' + f'{cur_price:,.2f}' + '</span>'
    '<span class="' + chg_cls + '">' + chg_arrow + f' {bar_chg:+.2f} ({bar_chg_pct:+.2f}%)' + '</span>'
    '<span class="bar-counter">' + cur_date + '</span>'
    '<span class="bar-counter">Bar ' + str(bar_idx + 1) + ' / ' + str(total) + '</span>'
    '</div>',
    unsafe_allow_html=True
)

# ── Step controls ─────────────────────────────────────────────────────────────
ctrl1, ctrl2, ctrl3, ctrl4, ctrl5 = st.columns([1, 1, 1, 1, 1])
with ctrl1:
    if st.button("◀◀ Back 10", use_container_width=True):
        st.session_state["rp_bar"] = max(20, bar_idx - 10)
        st.rerun()
with ctrl2:
    if st.button("◀ Back 1", use_container_width=True):
        st.session_state["rp_bar"] = max(20, bar_idx - 1)
        st.rerun()
with ctrl3:
    if st.button("▶ Step +1", type="primary", use_container_width=True):
        st.session_state["rp_bar"] = min(total - 1, bar_idx + 1)
        st.rerun()
with ctrl4:
    if st.button("▶▶ Skip +10", use_container_width=True):
        st.session_state["rp_bar"] = min(total - 1, bar_idx + 10)
        st.rerun()
with ctrl5:
    if st.button("Reset All", use_container_width=True):
        st.session_state["rp_bar"]      = 50
        st.session_state["rp_trades"]   = []
        st.session_state["rp_position"] = None
        st.session_state["rp_cash"]     = st.session_state["rp_capital"]
        st.session_state["rp_loaded"]   = False
        st.session_state["rp_df"]       = None
        st.rerun()

# ── Replay chart (Plotly — we control exactly what's shown) ───────────────────
fig = go.Figure()
fig.add_trace(go.Candlestick(
    x=visible["Date"],
    open=visible["Open"], high=visible["High"],
    low=visible["Low"],   close=visible["Close"],
    increasing_line_color="#00e676", decreasing_line_color="#ff3d57",
    increasing_fillcolor="#00e676",  decreasing_fillcolor="#ff3d57",
    name=st.session_state["rp_ticker"],
    whiskerwidth=0.6,
))

# Mark open position entry
pos = st.session_state["rp_position"]
if pos:
    fig.add_hline(
        y=pos["entry"],
        line_color="#ffd166", line_dash="dot", line_width=1.5,
        annotation_text=f"Entry ${pos['entry']:.2f}",
        annotation_font_color="#ffd166", annotation_font_size=10,
    )

fig.update_layout(
    paper_bgcolor="#06080c", plot_bgcolor="#06080c",
    font=dict(family="IBM Plex Mono, monospace", color="#3a4a5e", size=11),
    height=420,
    margin=dict(l=0, r=0, t=10, b=0),
    xaxis=dict(
        gridcolor="#1a2235", zeroline=False, showgrid=True,
        rangeslider=dict(visible=False),
        type="date", showspikes=True, spikecolor="#2a3550", spikethickness=1,
    ),
    yaxis=dict(
        gridcolor="#1a2235", zeroline=False, showgrid=True,
        side="right", showspikes=True, spikecolor="#2a3550", spikethickness=1,
    ),
    showlegend=False,
    xaxis_rangeselector=dict(visible=False),
)
st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# ── Volume ────────────────────────────────────────────────────────────────────
vol_colors = ["#00e676" if c >= o else "#ff3d57"
              for c, o in zip(visible["Close"], visible["Open"])]
vfig = go.Figure(go.Bar(
    x=visible["Date"], y=visible["Volume"],
    marker_color=vol_colors, marker_opacity=0.6, name="Volume"
))
vfig.update_layout(
    paper_bgcolor="#06080c", plot_bgcolor="#06080c",
    font=dict(family="IBM Plex Mono, monospace", color="#3a4a5e", size=10),
    height=100, margin=dict(l=0, r=0, t=0, b=0),
    xaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
    yaxis=dict(showticklabels=False, showgrid=False, zeroline=False, side="right"),
    showlegend=False,
)
st.plotly_chart(vfig, use_container_width=True, config={"displayModeBar": False})

# ── Metrics ───────────────────────────────────────────────────────────────────
trades   = st.session_state["rp_trades"]
cash     = st.session_state["rp_cash"]
capital  = st.session_state["rp_capital"]
open_val = (cur_price * pos["size"]) if pos and pos["direction"] == "long" else 0
portfolio = cash + open_val
total_pnl = sum(t["pnl"] for t in trades)
wins      = [t for t in trades if t["pnl"] > 0]
win_rate  = len(wins) / len(trades) * 100 if trades else 0
ret_pct   = (portfolio - capital) / capital * 100

m1, m2, m3, m4, m5 = st.columns(5)
for col, val, lbl, cls in [
    (m1, f"${portfolio:,.2f}",  "Portfolio",    "neu"),
    (m2, f"${cash:,.2f}",       "Cash",         "neu"),
    (m3, f"{ret_pct:+.2f}%",    "Return",       "pos" if ret_pct >= 0 else "neg"),
    (m4, f"${total_pnl:+,.2f}", "Realised P&L", "pos" if total_pnl >= 0 else "neg"),
    (m5, f"{win_rate:.0f}%",    "Win Rate",     "pos" if win_rate >= 50 else ("neg" if trades else "neu")),
]:
    col.markdown(
        '<div class="metric-mini">'
        '<div class="metric-val ' + cls + '">' + val + '</div>'
        '<div class="metric-lbl">' + lbl + '</div>'
        '</div>',
        unsafe_allow_html=True
    )

# ── Open position display ──────────────────────────────────────────────────────
if pos:
    unreal_pnl = (cur_price - pos["entry"]) * pos["size"] if pos["direction"] == "long" else (pos["entry"] - cur_price) * pos["size"]
    unreal_cls = "pos" if unreal_pnl >= 0 else "neg"
    st.markdown(
        '<div style="background:rgba(0,230,118,0.05);border:1px solid rgba(0,230,118,0.2);'
        'border-radius:8px;padding:0.65rem 1rem;margin:0.6rem 0;'
        'font-family:IBM Plex Mono,monospace;font-size:0.65rem;color:#eef2f7;'
        'display:flex;gap:2rem;align-items:center;flex-wrap:wrap;">'
        '<span style="color:#00e676;font-weight:700;">● OPEN ' + pos["direction"].upper() + '</span>'
        '<span>' + str(pos["size"]) + ' shares @ $' + f'{pos["entry"]:.2f}' + '</span>'
        '<span style="color:#3a4a5e;">Cost $' + f'{pos["size"] * pos["entry"]:,.2f}' + '</span>'
        '<span class="' + unreal_cls + '">Unrealised ' + f'${unreal_pnl:+,.2f}' + '</span>'
        '</div>',
        unsafe_allow_html=True
    )

# ── Trade entry ───────────────────────────────────────────────────────────────
st.markdown('<div style="margin-top:0.5rem;"></div>', unsafe_allow_html=True)
f1, f2, f3, f4, f5 = st.columns([1.6, 1.1, 0.9, 1.1, 1])
with f1: action = st.selectbox("Action", ["BUY (Long)", "SELL SHORT", "CLOSE POSITION"], label_visibility="visible")
with f2: price  = st.number_input("Price $", value=round(cur_price, 2), min_value=0.01, step=0.01, format="%.2f", label_visibility="visible")
with f3: shares = st.number_input("Shares", value=10, min_value=1, step=1, label_visibility="visible")
with f4: note   = st.text_input("Note", placeholder="e.g. breakout", label_visibility="visible")
with f5:
    st.markdown('<div style="height:28px;"></div>', unsafe_allow_html=True)
    submit = st.button("Log Trade", type="primary", use_container_width=True)

if submit:
    now_str = datetime.now().strftime("%H:%M")
    cost = price * shares
    err_msg = None

    if action == "BUY (Long)":
        if cost > cash:
            err_msg = f"Not enough cash. Need ${cost:,.2f}, have ${cash:,.2f}"
        elif pos is not None:
            err_msg = "Close your open position first."
        else:
            st.session_state["rp_cash"] -= cost
            st.session_state["rp_position"] = {"direction":"long","entry":price,"size":shares}
            st.session_state["rp_trades"].append({"time":now_str,"action":"BUY","price":price,"shares":shares,"pnl":0,"note":note})

    elif action == "SELL SHORT":
        if pos is not None:
            err_msg = "Close your open position first."
        else:
            st.session_state["rp_cash"] += cost  # credit on short entry
            st.session_state["rp_position"] = {"direction":"short","entry":price,"size":shares}
            st.session_state["rp_trades"].append({"time":now_str,"action":"SHORT","price":price,"shares":shares,"pnl":0,"note":note})

    elif action == "CLOSE POSITION":
        if pos is None:
            err_msg = "No open position to close."
        else:
            if pos["direction"] == "long":
                pnl = (price - pos["entry"]) * pos["size"]
                st.session_state["rp_cash"] += price * pos["size"]
            else:
                pnl = (pos["entry"] - price) * pos["size"]
                st.session_state["rp_cash"] -= price * pos["size"]
            st.session_state["rp_position"] = None
            st.session_state["rp_trades"].append({"time":now_str,"action":"CLOSE","price":price,"shares":pos["size"],"pnl":pnl,"note":note})

    if err_msg:
        st.error(err_msg)
    else:
        st.rerun()

# ── Trade log ─────────────────────────────────────────────────────────────────
if trades:
    st.markdown(
        '<div style="font-family:IBM Plex Mono,monospace;font-size:0.5rem;text-transform:uppercase;'
        'letter-spacing:0.18em;color:#3a4a5e;margin:1rem 0 0.3rem;">'
        'Trade Log — ' + str(len(trades)) + ' entries</div>',
        unsafe_allow_html=True
    )
    header = (
        '<div class="trade-row trade-hdr">'
        '<span>Time</span><span>Action</span><span>Price</span><span>Shares</span><span>P&amp;L</span><span>Note</span>'
        '</div>'
    )
    rows_html = ""
    for t in reversed(trades):
        pnl_cls = "pos" if t["pnl"] > 0 else ("neg" if t["pnl"] < 0 else "neu")
        pnl_str = f'${t["pnl"]:+,.2f}' if t["pnl"] != 0 else "—"
        act_color = "#00e676" if t["action"] == "BUY" else ("#ff3d57" if t["action"] == "SHORT" else "#ffd166")
        rows_html += (
            '<div class="trade-row">'
            '<span style="color:#3a4a5e;">' + t["time"] + '</span>'
            '<span style="color:' + act_color + ';font-weight:700;">' + t["action"] + '</span>'
            '<span style="color:#eef2f7;">$' + f'{t["price"]:.2f}' + '</span>'
            '<span style="color:#8896ab;">' + str(t["shares"]) + '</span>'
            '<span class="' + pnl_cls + '">' + pnl_str + '</span>'
            '<span style="color:#3a4a5e;">' + t.get("note","") + '</span>'
            '</div>'
        )
    st.markdown(
        '<div style="background:#0c1018;border:1px solid #1a2235;border-radius:10px;overflow:hidden;">'
        + header + rows_html + '</div>',
        unsafe_allow_html=True
    )
    if st.button("Export CSV"):
        import pandas as pd
        st.download_button("Download", pd.DataFrame(trades).to_csv(index=False),
                           file_name="replay_trades.csv", mime="text/csv")
else:
    st.markdown(
        '<div style="background:#0c1018;border:1px solid #1a2235;border-radius:10px;'
        'padding:1.5rem;text-align:center;margin-top:0.5rem;">'
        '<div style="font-family:IBM Plex Mono,monospace;font-size:0.6rem;color:#1a2235;">'
        'No trades yet — log entries using the form above</div>'
        '</div>',
        unsafe_allow_html=True
    )
