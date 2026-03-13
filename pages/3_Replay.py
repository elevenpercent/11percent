import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.styles import SHARED_CSS
from utils.nav import navbar

st.set_page_config(page_title="Replay — 11%", page_icon="$", layout="wide", initial_sidebar_state="collapsed")
st.markdown(SHARED_CSS, unsafe_allow_html=True)
navbar()

st.markdown("""
<style>
@keyframes fadeUp { from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:translateY(0)} }
.replay-header { animation:fadeUp 0.5s ease both; padding:1.5rem 0 1.2rem; }
.replay-title {
    font-family:'Bebas Neue',sans-serif; font-size:2.4rem; letter-spacing:0.04em;
    color:#eef2f7; line-height:1; margin-bottom:0.3rem;
}
.replay-sub { font-size:0.85rem; color:#3a4a5e; line-height:1.6; }
.tv-wrap {
    border:1px solid #1a2235; border-radius:12px; overflow:hidden;
    animation:fadeUp 0.5s 0.1s ease both; opacity:0;
}
.control-card {
    background:#0c1018; border:1px solid #1a2235; border-radius:10px;
    padding:1.1rem 1.2rem; margin-top:1rem;
}
.control-label {
    font-family:'IBM Plex Mono',monospace; font-size:0.54rem;
    text-transform:uppercase; letter-spacing:0.18em; color:#3a4a5e; margin-bottom:0.5rem;
}
.info-chip {
    display:inline-flex; align-items:center; gap:0.4rem;
    padding:0.25rem 0.7rem; border-radius:4px;
    background:rgba(77,166,255,0.08); border:1px solid rgba(77,166,255,0.2);
    font-family:'IBM Plex Mono',monospace; font-size:0.58rem; color:#4da6ff;
    margin-bottom:1rem;
}
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="replay-header">'
    '<div class="replay-title">Market Replay</div>'
    '<div class="replay-sub">Real TradingView charts. Use the built-in replay button '
    '(▶ in the toolbar) to step through bars. Add indicators, draw levels, practice entries.</div>'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="info-chip">💡 Click the clock icon in the TradingView toolbar to enter Replay mode</div>',
    unsafe_allow_html=True
)

# ── Ticker input ──────────────────────────────────────────────────────────────
ctrl_l, ctrl_r = st.columns([2, 5])
with ctrl_l:
    ticker = st.text_input("Ticker", value="NASDAQ:AAPL", placeholder="e.g. NASDAQ:AAPL",
                           label_visibility="collapsed",
                           help="Use TradingView format: EXCHANGE:TICKER e.g. NASDAQ:AAPL, BINANCE:BTCUSDT")

with ctrl_r:
    interval_map = {
        "1m":"1", "5m":"5", "15m":"15", "30m":"30",
        "1h":"60", "4h":"240", "1D":"D", "1W":"W"
    }
    interval_label = st.selectbox(
        "Interval", list(interval_map.keys()), index=6,
        label_visibility="collapsed"
    )
    interval = interval_map[interval_label]

# Sanitise ticker — strip spaces
ticker = ticker.strip().upper() or "NASDAQ:AAPL"

# ── TradingView Advanced Chart Widget ─────────────────────────────────────────
tv_html = f"""
<div class="tv-wrap">
<div class="tradingview-widget-container" style="height:700px;width:100%;">
  <div id="tradingview_chart" style="height:100%;width:100%;"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
  <script type="text/javascript">
  new TradingView.widget({{
    "autosize": true,
    "symbol": "{ticker}",
    "interval": "{interval}",
    "timezone": "America/New_York",
    "theme": "dark",
    "style": "1",
    "locale": "en",
    "toolbar_bg": "#06080c",
    "enable_publishing": false,
    "hide_side_toolbar": false,
    "allow_symbol_change": true,
    "save_image": true,
    "container_id": "tradingview_chart",
    "backgroundColor": "rgba(6,8,12,1)",
    "gridColor": "rgba(26,34,53,0.5)",
    "hide_top_toolbar": false,
    "withdateranges": true,
    "studies": [
      "Volume@tv-basicstudies",
      "MASimple@tv-basicstudies"
    ],
    "overrides": {{
      "mainSeriesProperties.candleStyle.upColor": "#00e676",
      "mainSeriesProperties.candleStyle.downColor": "#ff3d57",
      "mainSeriesProperties.candleStyle.borderUpColor": "#00e676",
      "mainSeriesProperties.candleStyle.borderDownColor": "#ff3d57",
      "mainSeriesProperties.candleStyle.wickUpColor": "#00e676",
      "mainSeriesProperties.candleStyle.wickDownColor": "#ff3d57",
      "paneProperties.background": "#06080c",
      "paneProperties.backgroundType": "solid",
      "paneProperties.vertGridProperties.color": "#1a2235",
      "paneProperties.horzGridProperties.color": "#1a2235",
      "scalesProperties.textColor": "#3a4a5e",
      "scalesProperties.lineColor": "#1a2235"
    }}
  }});
  </script>
</div>
</div>
"""

st.components.v1.html(tv_html, height=720, scrolling=False)

# ── How to use replay ─────────────────────────────────────────────────────────
st.markdown('<div style="margin-top:1.2rem;"></div>', unsafe_allow_html=True)
tip_l, tip_m, tip_r = st.columns(3)

for col, icon, title, body in [
    (tip_l, "⏱", "Enter Replay Mode",
     "Click the clock icon in the top toolbar. Pick your start date on the chart."),
    (tip_m, "▶", "Step Through Bars",
     "Use the play/pause and step controls that appear. Go bar by bar or play in real-time."),
    (tip_r, "✏️", "Draw & Analyse",
     "Use TradingView's full drawing toolkit — trendlines, Fibonacci, horizontal levels, and more."),
]:
    col.markdown(
        f'<div style="background:#0c1018;border:1px solid #1a2235;border-radius:10px;padding:1.1rem 1.2rem;">'
        f'<div style="font-size:1.3rem;margin-bottom:0.5rem;">{icon}</div>'
        f'<div style="font-family:IBM Plex Mono,monospace;font-size:0.62rem;font-weight:600;'
        f'text-transform:uppercase;letter-spacing:0.1em;color:#eef2f7;margin-bottom:0.4rem;">{title}</div>'
        f'<div style="font-size:0.78rem;color:#3a4a5e;line-height:1.6;">{body}</div>'
        f'</div>',
        unsafe_allow_html=True
    )
