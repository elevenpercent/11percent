import streamlit as st
import sys, os
from datetime import datetime
import pytz, yfinance as yf
sys.path.insert(0, os.path.dirname(__file__))
from utils.styles import SHARED_CSS, LOGO_IMG
from utils.nav import navbar
from utils.session_persist import restore_session

st.set_page_config(
    page_title="11% · Trade Smarter",
    page_icon="$",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""<style>
html,body{background:#0d1117!important}
[data-testid="stAppViewContainer"],[data-testid="stAppViewContainer"]>.main{background:#0d1117!important}
[data-testid="stSidebar"],[data-testid="stSidebarNav"],[data-testid="collapsedControl"],
section[data-testid="stSidebar"]{display:none!important;width:0!important;max-width:0!important;
opacity:0!important;visibility:hidden!important;pointer-events:none!important}
#MainMenu,footer,header,iframe[title="streamlit_analytics"]{display:none!important}
.stDeployButton{display:none!important}
</style>""", unsafe_allow_html=True)

st.markdown(SHARED_CSS, unsafe_allow_html=True)

st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=IBM+Plex+Mono:wght@400;500;600;700&family=Inter:wght@400;500;600&display=swap');
:root{
  --bg:#0d1117;--bg2:#111827;--bg3:#161f2e;
  --border:#1c2a3a;--border2:#243447;
  --text:#e2e8f0;--text2:#8892a4;--dim:#3a4558;
  --green:#22d3a5;--red:#f87171;--gold:#f59e0b;
}
html,body,[data-testid="stAppViewContainer"],[data-testid="stAppViewContainer"]>.main,.block-container{background:var(--bg)!important}
.block-container{padding-top:1.5rem!important;padding-bottom:4rem!important;padding-left:2.5rem!important;padding-right:2.5rem!important;max-width:100%!important}

/* ANIMATED DOT GRID */
.dot-grid{position:fixed;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:0;
  background-image:radial-gradient(circle,rgba(34,211,165,0.07) 1px,transparent 1px);
  background-size:28px 28px;animation:gridDrift 60s linear infinite}
@keyframes gridDrift{0%{background-position:0 0}100%{background-position:28px 28px}}
.dot-vignette{position:fixed;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:1;
  background:radial-gradient(ellipse 90% 60% at 50% 0%,rgba(13,17,23,0) 0%,rgba(13,17,23,0.92) 100%)}
.dot-glow{position:fixed;top:-200px;left:-200px;width:700px;height:700px;pointer-events:none;z-index:0;
  background:radial-gradient(circle,rgba(34,211,165,0.04) 0%,transparent 70%)}

/* ANIMATIONS */
@keyframes fadeUp{from{opacity:0;transform:translateY(22px)}to{opacity:1;transform:translateY(0)}}
@keyframes pulseGlow{0%,100%{box-shadow:0 0 20px rgba(34,211,165,0.12),0 8px 40px rgba(0,0,0,0.4)}50%{box-shadow:0 0 40px rgba(34,211,165,0.25),0 8px 40px rgba(0,0,0,0.4)}}
.hero-wrap{animation:fadeUp 0.7s ease both}
.hero-chart-wrap{animation:fadeUp 0.7s 0.15s ease both}

.hp-section{position:relative;z-index:2;padding:4rem 0 1rem}
.hp-section-sm{position:relative;z-index:2;padding:2.5rem 0 1rem}
.section-tag{font-family:'IBM Plex Mono',monospace;font-size:0.52rem;text-transform:uppercase;letter-spacing:0.35em;color:var(--green);opacity:0.6;margin-bottom:1rem;text-align:center}

/* HERO */
.hero-eyebrow{font-family:'IBM Plex Mono',monospace;font-size:0.58rem;letter-spacing:0.35em;text-transform:uppercase;color:var(--green);margin-bottom:0.9rem;display:inline-flex;align-items:center;gap:0.5rem}
.hero-eyebrow::before{content:'';display:inline-block;width:24px;height:1px;background:var(--green);opacity:0.5}
.hero-h1{font-family:'Bebas Neue',sans-serif;font-size:5rem;letter-spacing:0.02em;line-height:0.88;color:var(--text);margin:0.3rem 0 1.2rem}
.hero-h1 .accent{color:transparent;-webkit-text-stroke:1.5px var(--green)}
.hero-sub{font-size:0.87rem;color:var(--text2);line-height:1.9;font-family:'Inter',sans-serif;max-width:450px;margin-bottom:2rem}
.hero-btns{display:flex;gap:0.75rem;align-items:center;flex-wrap:wrap}
.btn-primary{background:var(--green);color:#040d0a;font-family:'IBM Plex Mono',monospace;font-size:0.67rem;font-weight:700;text-transform:uppercase;letter-spacing:0.12em;padding:0.8rem 2.2rem;border-radius:8px;text-decoration:none;display:inline-block;transition:all 0.2s;box-shadow:0 0 28px rgba(34,211,165,0.25),0 2px 8px rgba(0,0,0,0.3);position:relative;overflow:hidden}
.btn-primary::after{content:'';position:absolute;top:0;left:-100%;width:60%;height:100%;background:linear-gradient(90deg,transparent,rgba(255,255,255,0.18),transparent);transition:left 0.4s}
.btn-primary:hover::after{left:150%}
.btn-primary:hover{background:#2eeeba;box-shadow:0 0 44px rgba(34,211,165,0.4),0 4px 16px rgba(0,0,0,0.4);transform:translateY(-1px)}
.btn-secondary{background:rgba(255,255,255,0.03);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);color:var(--text2);border:1px solid var(--border2);font-family:'IBM Plex Mono',monospace;font-size:0.67rem;font-weight:600;text-transform:uppercase;letter-spacing:0.12em;padding:0.8rem 1.8rem;border-radius:8px;text-decoration:none;display:inline-block;transition:all 0.2s}
.btn-secondary:hover{border-color:rgba(34,211,165,0.3);color:var(--text);background:rgba(34,211,165,0.05);transform:translateY(-1px)}
.hero-users{font-family:'IBM Plex Mono',monospace;font-size:0.58rem;color:var(--dim);margin-top:1.2rem;display:flex;align-items:center;gap:0.6rem;flex-wrap:wrap}
.hero-users .dot-sep{width:3px;height:3px;border-radius:50%;background:var(--dim);display:inline-block}

/* GLASS CHART */
.chart-mock{background:rgba(17,24,39,0.7);backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);border:1px solid rgba(34,211,165,0.12);border-radius:14px;overflow:hidden;animation:pulseGlow 4s ease-in-out infinite}
.chart-mock-bar{background:rgba(22,31,46,0.9);border-bottom:1px solid rgba(34,211,165,0.08);padding:0.55rem 1rem;display:flex;align-items:center;gap:6px}
.mock-dot{width:9px;height:9px;border-radius:50%}

/* CONVEYORS */
@keyframes scrollL{0%{transform:translateX(0)}100%{transform:translateX(-50%)}}
@keyframes scrollR{0%{transform:translateX(-50%)}100%{transform:translateX(0%)}}
.conv-track{display:flex;white-space:nowrap;width:max-content}
.conv-track.left{animation:scrollL 48s linear infinite}
.conv-track.right{animation:scrollR 52s linear infinite}
.conv-track:hover{animation-play-state:paused}
.conv-outer{overflow:hidden;position:relative;margin-bottom:0.5rem}
.conv-outer::before,.conv-outer::after{content:'';position:absolute;top:0;bottom:0;width:120px;z-index:2;pointer-events:none}
.conv-outer::before{left:0;background:linear-gradient(90deg,var(--bg) 0%,rgba(13,17,23,0.7) 60%,transparent 100%)}
.conv-outer::after{right:0;background:linear-gradient(-90deg,var(--bg) 0%,rgba(13,17,23,0.7) 60%,transparent 100%)}
.conv-chip{display:inline-flex;align-items:center;justify-content:center;background:rgba(17,24,39,0.6);backdrop-filter:blur(4px);-webkit-backdrop-filter:blur(4px);border:1px solid var(--border);border-radius:6px;font-family:'IBM Plex Mono',monospace;font-size:0.6rem;color:var(--text2);padding:4px 14px;margin:0 5px;white-space:nowrap;height:30px;transition:border-color 0.2s,background 0.2s}
.conv-chip:hover{border-color:rgba(34,211,165,0.25);background:rgba(34,211,165,0.04)}

/* PROOF */
.proof-wrap{background:rgba(17,24,39,0.6);backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);border:1px solid var(--border);border-radius:18px;padding:3rem 3.5rem;display:flex;gap:4rem;align-items:flex-start;flex-wrap:wrap;box-shadow:0 4px 40px rgba(0,0,0,0.3);position:relative;overflow:hidden}
.proof-wrap::before{content:'';position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,rgba(34,211,165,0.3),transparent)}
.proof-text h2{font-family:'Bebas Neue',sans-serif;font-size:3.5rem;letter-spacing:0.03em;line-height:0.92;color:var(--text);margin-bottom:0.8rem}
.proof-text h2 span{color:var(--green)}
.proof-text p{font-family:'Inter',sans-serif;font-size:0.8rem;color:var(--text2);line-height:1.85;max-width:320px}
.proof-stats{display:flex;gap:2.5rem;flex-wrap:wrap;align-items:center}
.stat-big{text-align:center}
.stat-big-n{font-family:'Bebas Neue',sans-serif;font-size:3.2rem;letter-spacing:0.04em;color:var(--green);line-height:1;text-shadow:0 0 30px rgba(34,211,165,0.3)}
.stat-big-l{font-family:'IBM Plex Mono',monospace;font-size:0.46rem;text-transform:uppercase;letter-spacing:0.2em;color:var(--dim);margin-top:0.2rem}

/* FEATURE CARDS */
.feat-section-title{font-family:'Bebas Neue',sans-serif;font-size:2.2rem;letter-spacing:0.05em;color:var(--green);text-align:center;margin-bottom:1.8rem;text-shadow:0 0 40px rgba(34,211,165,0.2)}
.feat-card{background:rgba(17,24,39,0.5);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);border:1px solid var(--border);border-radius:12px;padding:1.4rem 1.6rem;transition:border-color 0.2s,transform 0.2s,box-shadow 0.2s;position:relative;overflow:hidden}
.feat-card::before{content:'';position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,rgba(34,211,165,0.15),transparent);opacity:0;transition:opacity 0.2s}
.feat-card:hover{border-color:rgba(34,211,165,0.2);transform:translateY(-3px);box-shadow:0 8px 32px rgba(0,0,0,0.3)}
.feat-card:hover::before{opacity:1}
.feat-card-title{font-family:'IBM Plex Mono',monospace;font-size:0.68rem;font-weight:700;color:var(--green);margin-bottom:0.45rem}
.feat-card-body{font-family:'Inter',sans-serif;font-size:0.75rem;color:var(--text2);line-height:1.75}

/* PERF CARDS */
.perf-card{background:rgba(17,24,39,0.5);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);border:1px solid var(--border);border-radius:12px;padding:1.5rem;margin-bottom:1rem;transition:border-color 0.2s,transform 0.2s}
.perf-card:hover{border-color:rgba(34,211,165,0.2);transform:translateY(-2px)}
.perf-card-label{font-family:'IBM Plex Mono',monospace;font-size:0.62rem;font-weight:700;color:var(--green);margin-bottom:0.5rem}
.perf-card-body{font-family:'Inter',sans-serif;font-size:0.75rem;color:var(--text2);line-height:1.75}

/* WHY CARDS */
.why-title{font-family:'Bebas Neue',sans-serif;font-size:2.2rem;letter-spacing:0.05em;color:var(--green);text-align:center;margin-bottom:1.4rem;text-shadow:0 0 40px rgba(34,211,165,0.2)}
.why-card{background:rgba(17,24,39,0.5);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);border:1px solid var(--border);border-radius:14px;padding:1.6rem;text-align:center;transition:border-color 0.25s,transform 0.25s,box-shadow 0.25s;height:100%}
.why-card:hover{border-color:rgba(34,211,165,0.25);transform:translateY(-4px);box-shadow:0 12px 40px rgba(0,0,0,0.35)}
.why-icon{font-size:1.6rem;margin-bottom:0.8rem}
.why-name{font-family:'IBM Plex Mono',monospace;font-size:0.65rem;font-weight:700;color:var(--text);text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.6rem}
.why-body{font-family:'Inter',sans-serif;font-size:0.72rem;color:var(--text2);line-height:1.7}

/* TESTIMONIALS */
.test-title{font-family:'Bebas Neue',sans-serif;font-size:2.2rem;letter-spacing:0.05em;color:var(--green);text-align:center;margin-bottom:1.4rem;text-shadow:0 0 40px rgba(34,211,165,0.2)}
.test-card{background:rgba(17,24,39,0.5);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);border:1px solid var(--border);border-radius:14px;padding:1.6rem;height:100%;transition:border-color 0.2s,transform 0.2s}
.test-card:hover{border-color:rgba(34,211,165,0.15);transform:translateY(-2px)}
.test-stars{color:var(--gold);font-size:0.8rem;margin-bottom:0.8rem;letter-spacing:3px}
.test-quote{font-family:'Inter',sans-serif;font-size:0.78rem;color:var(--text2);line-height:1.8;font-style:italic;margin-bottom:1rem}
.test-name{font-family:'IBM Plex Mono',monospace;font-size:0.64rem;font-weight:700;color:var(--text)}
.test-role{font-family:'IBM Plex Mono',monospace;font-size:0.55rem;color:var(--dim);margin-top:3px}

/* CTA */
.cta-wrap{background:linear-gradient(135deg,rgba(17,24,39,0.8),rgba(22,31,46,0.8));backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);border:1px solid var(--border);border-radius:22px;padding:4.5rem 3rem;text-align:center;position:relative;overflow:hidden;box-shadow:0 8px 60px rgba(0,0,0,0.4)}
.cta-wrap::before{content:'';position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,var(--green),transparent)}
.cta-title{font-family:'Bebas Neue',sans-serif;font-size:3.8rem;letter-spacing:0.04em;line-height:0.92;color:var(--text);margin-bottom:0.9rem}
.cta-sub{font-family:'Inter',sans-serif;font-size:0.82rem;color:var(--text2);max-width:440px;margin:0 auto 2rem;line-height:1.85}

/* FOOTER */
.footer-wrap{border-top:1px solid var(--border);padding:2.5rem 0;margin-top:2rem;display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:1.5rem}
.footer-brand{font-family:'Bebas Neue',sans-serif;font-size:1.4rem;letter-spacing:0.06em}
.footer-col-title{font-family:'IBM Plex Mono',monospace;font-size:0.52rem;text-transform:uppercase;letter-spacing:0.2em;color:var(--dim);margin-bottom:0.7rem}
.footer-link{display:block;font-family:'IBM Plex Mono',monospace;font-size:0.62rem;color:var(--text2);text-decoration:none;margin-bottom:0.35rem;transition:color 0.15s}
.footer-link:hover{color:var(--green)}
.footer-legal{font-family:'IBM Plex Mono',monospace;font-size:0.5rem;color:var(--dim);margin-top:0.4rem}
</style>""", unsafe_allow_html=True)

restore_session()
navbar()

st.markdown('<div class="dot-grid"></div><div class="dot-vignette"></div><div class="dot-glow"></div>', unsafe_allow_html=True)

if st.session_state.get("user"):
    _uname = st.session_state.get("user_email","").split("@")[0].replace("."," ").replace("_"," ").title()
    st.markdown(f"""<div style="position:relative;z-index:2;background:rgba(34,211,165,0.04);backdrop-filter:blur(8px);border:1px solid rgba(34,211,165,0.15);border-radius:10px;padding:0.75rem 1.2rem;margin-bottom:1rem;display:flex;align-items:center;justify-content:space-between;">
        <span style="font-family:'IBM Plex Mono',monospace;font-size:0.7rem;color:#8892a4">Welcome back, <strong style="color:#e2e8f0">{_uname}</strong></span>
        <a href="/Dashboard" style="background:#22d3a5;color:#040d0a;font-family:'IBM Plex Mono',monospace;font-size:0.6rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;padding:0.38rem 1rem;border-radius:6px;text-decoration:none">Dashboard →</a>
    </div>""", unsafe_allow_html=True)

# HERO
hero_l, hero_r = st.columns([5, 4])
with hero_l:
    st.markdown("""
    <div class="hero-wrap" style="position:relative;z-index:2;padding:2rem 0 1rem">
        <div class="hero-eyebrow">The Free Trading Education Platform</div>
        <div class="hero-h1">Free Trading<br><span class="accent">Education</span><br>Platform</div>
        <div class="hero-sub">Test strategies with professional-grade backtesting tools. Replay markets bar-by-bar. Analyze performance, optimize parameters, and build real confidence in your trades.</div>
        <div class="hero-btns">
            <a class="btn-primary" href="/Strategy_Lab">Start Backtesting</a>
            <a class="btn-secondary" href="/Battles">Join Battles</a>
        </div>
        <div class="hero-users">
            <span>100% Free</span><span class="dot-sep"></span>
            <span>No Signup Required</span><span class="dot-sep"></span>
            <span>Real Market Data</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with hero_r:
    st.markdown("""
    <div class="hero-chart-wrap" style="position:relative;z-index:2;padding:2rem 0 0">
        <div class="chart-mock">
            <div class="chart-mock-bar">
                <div class="mock-dot" style="background:#f87171"></div>
                <div class="mock-dot" style="background:#fbbf24"></div>
                <div class="mock-dot" style="background:#22d3a5"></div>
                <span style="font-family:'IBM Plex Mono',monospace;font-size:0.46rem;color:#3a4558;margin-left:8px;text-transform:uppercase;letter-spacing:0.16em">Live Chart · AAPL</span>
            </div>
    """, unsafe_allow_html=True)
    st.components.v1.html("""
<style>*{margin:0;padding:0}body{background:#111827}.w{height:300px;background:#111827;border-radius:0 0 13px 13px;overflow:hidden}</style>
<div class="w"><div class="tradingview-widget-container" style="height:100%;width:100%">
<div id="tv_c" style="height:100%;width:100%"></div>
<script src="https://s3.tradingview.com/tv.js"></script>
<script>new TradingView.widget({autosize:true,symbol:"NASDAQ:AAPL",interval:"D",timezone:"America/New_York",
theme:"dark",style:"1",locale:"en",toolbar_bg:"#111827",enable_publishing:false,hide_side_toolbar:true,
hide_top_toolbar:true,allow_symbol_change:true,save_image:false,container_id:"tv_c",
backgroundColor:"rgba(17,24,39,1)",gridColor:"rgba(28,42,58,0.8)",
overrides:{"mainSeriesProperties.candleStyle.upColor":"#22d3a5","mainSeriesProperties.candleStyle.downColor":"#f87171",
"mainSeriesProperties.candleStyle.borderUpColor":"#22d3a5","mainSeriesProperties.candleStyle.borderDownColor":"#f87171",
"mainSeriesProperties.candleStyle.wickUpColor":"#22d3a5","mainSeriesProperties.candleStyle.wickDownColor":"#f87171",
"paneProperties.background":"#111827","paneProperties.backgroundType":"solid",
"paneProperties.vertGridProperties.color":"#1c2a3a","paneProperties.horzGridProperties.color":"#1c2a3a",
"scalesProperties.textColor":"#3a4558","scalesProperties.lineColor":"#1c2a3a"}});</script>
</div></div>""", height=305, scrolling=False)
    st.markdown('</div></div>', unsafe_allow_html=True)

# CONVEYORS
st.markdown('<div class="hp-section" style="padding:2rem 0 1rem">', unsafe_allow_html=True)
st.markdown('<div class="section-tag" style="position:relative;z-index:2">Trusted by traders worldwide</div>', unsafe_allow_html=True)

fx = ["EUR/USD","GBP/USD","USD/JPY","AUD/USD","USD/CAD","EUR/GBP","EUR/JPY","GBP/JPY","AUD/CAD","AUD/CHF","AUD/JPY","AUD/NZD","CAD/CHF","CAD/JPY","CHF/JPY","EUR/AUD","EUR/CAD","EUR/CHF","EUR/DKK","EUR/HUF","EUR/HKD","EUR/NZD","EUR/NOK","GBP/AUD","GBP/CAD","GBP/CHF","GBP/NZD","NZD/USD","USD/CHF","USD/DKK"]
fx_chips = "".join(f'<span class="conv-chip">{t}</span>' for t in fx)
st.markdown(f'<div class="conv-outer" style="position:relative;z-index:2"><div class="conv-track left">{fx_chips}{fx_chips}</div></div>', unsafe_allow_html=True)

crypto = ["BTC/USD","ETH/USD","BNB/USD","SOL/USD","ADA/USD","XRP/USD","DOT/USD","LTC/USD","AVAX/USD","MATIC/USD","LINK/USD","UNI/USD","ATOM/USD","NEAR/USD","FTM/USD","BCH/USD","EOS/USD","TRX/USD","XLM/USD","VET/USD","ALGO/USD","MANA/USD","SAND/USD","APE/USD","DOGE/USD","SHIB/USD","MKR/USD","COMP/USD","YFI/USD"]
cr_chips = "".join(f'<span class="conv-chip" style="color:#f59e0b">{t}</span>' for t in crypto)
st.markdown(f'<div class="conv-outer" style="position:relative;z-index:2"><div class="conv-track right">{cr_chips}{cr_chips}</div></div>', unsafe_allow_html=True)

stocks = ["AAPL","MSFT","NVDA","GOOGL","META","AMZN","TSLA","AMD","AVGO","CRM","JPM","GS","V","MA","BAC","XOM","CVX","UNH","LLY","ABBV","SPY","QQQ","IWM","DIA","VTI","GLD","TLT","USO","SLV","VXX","XAU/USD","XAG/USD","COPPER","CRUDE OIL","NAT GAS","USA500","NASDAQ","DOW30","VIX"]
st_chips = "".join(f'<span class="conv-chip" style="color:#8892a4">{t}</span>' for t in stocks)
st.markdown(f'<div class="conv-outer" style="position:relative;z-index:2"><div class="conv-track left">{st_chips}{st_chips}</div></div>', unsafe_allow_html=True)

from utils.indicators import INDICATOR_INFO
inds = list(INDICATOR_INFO.keys())
ind_chips = "".join(f'<span class="conv-chip" style="color:#22d3a5">{i}</span>' for i in inds)
st.markdown(f'<div class="conv-outer" style="position:relative;z-index:2;margin-top:0.3rem"><div class="conv-track right">{ind_chips}{ind_chips}</div></div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# PROOF
st.markdown('<div class="hp-section" style="position:relative;z-index:2">', unsafe_allow_html=True)
st.markdown("""
<div class="proof-wrap">
    <div class="proof-text">
        <h2>Proof is in the<br><span>performance</span></h2>
        <p>11% empowers traders to develop real edge with professional-grade backtesting tools. With thousands of sessions completed daily, we let the results do the talking.</p>
    </div>
    <div class="proof-stats">
        <div class="stat-big"><div class="stat-big-n">33+</div><div class="stat-big-l">Strategies<br>Available</div></div>
        <div class="stat-big"><div class="stat-big-n">56+</div><div class="stat-big-l">Technical<br>Indicators</div></div>
        <div class="stat-big"><div class="stat-big-n">20+</div><div class="stat-big-l">Trading<br>Tools</div></div>
        <div class="stat-big"><div class="stat-big-n" style="color:#f87171;text-shadow:0 0 30px rgba(248,113,113,0.3)">$0</div><div class="stat-big-l">Cost.<br>Forever.</div></div>
    </div>
</div>""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# TRADINGVIEW SECTION
st.markdown('<div class="hp-section" style="position:relative;z-index:2">', unsafe_allow_html=True)
st.markdown('<div class="feat-section-title">Using TradingView Charts</div>', unsafe_allow_html=True)
fc_l, fc_r = st.columns([5, 4])
with fc_l:
    feats = [
        ("Professional Trading Interface","Access the same TradingView charts used by millions of professional traders worldwide. Full candlestick charts with real historical data across all major markets."),
        ("Advanced Chart Analysis Tools","Utilize drawing tools, trendlines, Fibonacci, and advanced charting features for precise backtesting. Everything a professional trader needs."),
        ("20+ Years Historical Data","Access years of accurate historical price data across stocks, forex, crypto, indices, and commodities. All through Yahoo Finance — free."),
        ("No-Code Backtesting Platform","Test trading strategies visually without programming. No coding skills or complex setup required. Just pick a strategy and click run."),
    ]
    for title, body in feats:
        st.markdown(f'<div class="feat-card" style="margin-bottom:0.8rem"><div class="feat-card-title">{title}</div><div class="feat-card-body">{body}</div></div>', unsafe_allow_html=True)

with fc_r:
    st.markdown('<div class="chart-mock" style="margin-top:0.5rem"><div class="chart-mock-bar"><div class="mock-dot" style="background:#f87171"></div><div class="mock-dot" style="background:#fbbf24"></div><div class="mock-dot" style="background:#22d3a5"></div><span style="font-family:IBM Plex Mono,monospace;font-size:0.44rem;color:#3a4558;margin-left:8px;text-transform:uppercase;letter-spacing:0.16em">Replay Engine · TSLA</span></div>', unsafe_allow_html=True)
    st.components.v1.html("""
<style>*{margin:0;padding:0}body{background:#111827}.w{height:360px;background:#111827;overflow:hidden}</style>
<div class="w"><div class="tradingview-widget-container" style="height:100%;width:100%">
<div id="tv_c2" style="height:100%;width:100%"></div>
<script src="https://s3.tradingview.com/tv.js"></script>
<script>new TradingView.widget({autosize:true,symbol:"NASDAQ:TSLA",interval:"60",timezone:"America/New_York",
theme:"dark",style:"1",locale:"en",toolbar_bg:"#111827",enable_publishing:false,hide_side_toolbar:true,
hide_top_toolbar:true,allow_symbol_change:false,save_image:false,container_id:"tv_c2",
backgroundColor:"rgba(17,24,39,1)",gridColor:"rgba(28,42,58,0.8)",
overrides:{"mainSeriesProperties.candleStyle.upColor":"#22d3a5","mainSeriesProperties.candleStyle.downColor":"#f87171",
"mainSeriesProperties.candleStyle.borderUpColor":"#22d3a5","mainSeriesProperties.candleStyle.borderDownColor":"#f87171",
"mainSeriesProperties.candleStyle.wickUpColor":"#22d3a5","mainSeriesProperties.candleStyle.wickDownColor":"#f87171",
"paneProperties.background":"#111827","paneProperties.backgroundType":"solid",
"paneProperties.vertGridProperties.color":"#1c2a3a","paneProperties.horzGridProperties.color":"#1c2a3a",
"scalesProperties.textColor":"#3a4558","scalesProperties.lineColor":"#1c2a3a"}});</script>
</div></div>""", height=362, scrolling=False)
    st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# PERF ANALYSIS
st.markdown('<div class="hp-section" style="position:relative;z-index:2">', unsafe_allow_html=True)
st.markdown('<div class="feat-section-title">Backtesting Performance Analysis</div>', unsafe_allow_html=True)
perf_items = [
    ("Journal Your Trading Results","Track your trading performance with detailed balance and equity charts. Monitor account growth, drawdowns, and overall profitability over time. Visualize how your strategies perform with comprehensive equity curve analysis.",True),
    ("Trading Review & Replay Controls","Step through history bar-by-bar and trade blind. Continue unfinished sessions at any time. Our advanced replay controls let you pause, resume, and analyze at any point without losing progress.",False),
    ("Simulate Your Trading Strategy","Run Monte Carlo simulations to test strategies under thousands of different market scenarios. Analyze potential outcomes, risk profiles, and performance variations to understand your strategy statistically.",False),
    ("Battles — Compete With Traders","Enter paper trading competitions with real-time leaderboards. Set your capital, trade the same period as everyone else, and see where you rank. Win points and build your reputation.",True),
]
for i in range(0, len(perf_items), 2):
    pair = perf_items[i:i+2]
    cols = st.columns(2)
    for col, (title, body, flip) in zip(cols, pair):
        with col:
            st.markdown(f'<div class="perf-card"><div class="perf-card-label">{title}</div><div class="perf-card-body">{body}</div></div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# WHY
st.markdown('<div class="hp-section" style="position:relative;z-index:2">', unsafe_allow_html=True)
st.markdown('<div class="why-title">Why Choose 11%?</div>', unsafe_allow_html=True)
why_cols = st.columns(4)
why_items = [
    ("📊","Bar Replay & Strategy Testing","Experience advanced bar replay and test strategies in minutes. No setup, no coding, no complex configuration required."),
    ("🛡","Risk-Free Strategy Testing","Validate trading ideas with historical data before risking real money. Avoid costly mistakes and trade with confidence."),
    ("⚡","No-Code Platform","Professional-grade backtesting without programming skills. Visual strategy testing that any trader can master instantly."),
    ("$0","Always Free","Start testing profitable strategies immediately with no subscription fees, hidden costs, or trial limitations."),
]
for col, (icon, name, body) in zip(why_cols, why_items):
    with col:
        st.markdown(f'<div class="why-card"><div class="why-icon">{icon}</div><div class="why-name">{name}</div><div class="why-body">{body}</div></div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# TESTIMONIALS
st.markdown('<div class="hp-section" style="position:relative;z-index:2">', unsafe_allow_html=True)
st.markdown('<div class="test-title">What Our Users Say</div>', unsafe_allow_html=True)
test_cols = st.columns(3)
testimonials = [
    ("★★★★★",'"The replay engine is insane. I can replay any day in history and actually practice trading it. Nothing else does this for free."',"Marcus K.","Swing Trader"),
    ("★★★★★",'"Finally found a platform where I can test my EMA strategies without paying $50/month. The backtester is seriously professional grade."',"Sarah L.","Day Trader"),
    ("★★★★★",'"The AI coach actually explains WHY a strategy failed, not just the numbers. That\'s been the most educational part for me."',"Reza M.","Options Trader"),
]
for col, (stars, quote, name, role) in zip(test_cols, testimonials):
    with col:
        st.markdown(f'<div class="test-card"><div class="test-stars">{stars}</div><div class="test-quote">{quote}</div><div class="test-name">{name}</div><div class="test-role">{role}</div></div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# CTA
st.markdown('<div class="hp-section-sm" style="position:relative;z-index:2">', unsafe_allow_html=True)
st.markdown("""
<div class="cta-wrap">
    <div class="cta-title">Ready to Transform<br>Your Trading?</div>
    <div class="cta-sub">Join traders who use 11% to develop winning strategies with real historical data — completely free.</div>
    <div style="display:flex;gap:0.75rem;justify-content:center;flex-wrap:wrap">
        <a class="btn-primary" href="/Strategy_Lab">Start For Free</a>
        <a class="btn-secondary" href="/Replay">Try Replay</a>
    </div>
</div>""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# FOOTER
st.markdown("""
<div class="footer-wrap" style="position:relative;z-index:2">
    <div>
        <div class="footer-brand"><span style="color:#22d3a5">11</span><span style="color:#f87171">%</span></div>
        <div class="footer-legal">Professional trading education for serious traders.</div>
        <div class="footer-legal" style="margin-top:0.3rem">Not financial advice · Educational use only</div>
    </div>
    <div>
        <div class="footer-col-title">Product</div>
        <a class="footer-link" href="/Strategy_Lab">Strategy Lab</a>
        <a class="footer-link" href="/Replay">Market Replay</a>
        <a class="footer-link" href="/Battles">Battles</a>
        <a class="footer-link" href="/Marketplace">Marketplace</a>
    </div>
    <div>
        <div class="footer-col-title">Tools</div>
        <a class="footer-link" href="/Screener">Screener</a>
        <a class="footer-link" href="/Options_Chain">Options Chain</a>
        <a class="footer-link" href="/Trade_Journal">Trade Journal</a>
        <a class="footer-link" href="/Risk_Calculator">Risk Calculator</a>
    </div>
    <div>
        <div class="footer-col-title">Research</div>
        <a class="footer-link" href="/Market_Heatmap">Heatmap</a>
        <a class="footer-link" href="/Economic_Calendar">Econ Calendar</a>
        <a class="footer-link" href="/Sector_Rotation">Sector Rotation</a>
        <a class="footer-link" href="/Pattern_Recognition">Patterns</a>
    </div>
</div>""", unsafe_allow_html=True)
