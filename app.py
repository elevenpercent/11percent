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
st.markdown(SHARED_CSS, unsafe_allow_html=True)

# Inject dark background INSTANTLY before anything renders — kills white flash
st.markdown("""
<style>
html,body,[data-testid="stAppViewContainer"],[data-testid="stAppViewContainer"]>.main{background:#13161a!important}
[data-testid="stSidebar"],[data-testid="stSidebarNav"],[data-testid="collapsedControl"],
section[data-testid="stSidebar"]{display:none!important;width:0!important;max-width:0!important;opacity:0!important;visibility:hidden!important}
</style>
""", unsafe_allow_html=True)

restore_session()
navbar()

# Redirect logged-in users to dashboard on home page
if st.session_state.get("user"):
    _email = st.session_state.get("user_email","")
    _uname = _email.split("@")[0].replace("."," ").replace("_"," ").title()
    st.markdown(f'''<div style="background:rgba(74,222,128,0.05);border:1px solid rgba(74,222,128,0.18);
    border-radius:10px;padding:0.8rem 1.3rem;margin-bottom:1rem;
    display:flex;align-items:center;justify-content:space-between;">
        <div style="font-family:IBM Plex Mono,monospace;font-size:0.72rem;color:#9ca3af">
            Welcome back, <strong style="color:#e6eaf0">{_uname}</strong>
        </div>
        <a href="/Dashboard" style="background:#4ade80;color:#0a0f0a;font-family:IBM Plex Mono,monospace;
        font-size:0.6rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;
        padding:0.4rem 1rem;border-radius:6px;text-decoration:none">Go to Dashboard</a>
    </div>''', unsafe_allow_html=True)

# ── Particle background (canvas) ─────────────────────────────────────────────
st.markdown("""
<canvas id="particles" style="position:fixed;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:0;opacity:0.35"></canvas>
<script>
(function(){
var c=document.getElementById('particles');
if(!c)return;
var ctx=c.getContext('2d');
var W=c.width=window.innerWidth, H=c.height=window.innerHeight;
var pts=[];
for(var i=0;i<90;i++) pts.push({x:Math.random()*W,y:Math.random()*H,vx:(Math.random()-0.5)*0.4,vy:(Math.random()-0.5)*0.4,r:Math.random()*1.5+0.5});
function draw(){
  ctx.clearRect(0,0,W,H);
  for(var i=0;i<pts.length;i++){
    var p=pts[i];
    p.x+=p.vx; p.y+=p.vy;
    if(p.x<0||p.x>W) p.vx*=-1;
    if(p.y<0||p.y>H) p.vy*=-1;
    ctx.beginPath();ctx.arc(p.x,p.y,p.r,0,Math.PI*2);
    ctx.fillStyle='rgba(74,222,128,0.5)';ctx.fill();
    for(var j=i+1;j<pts.length;j++){
      var q=pts[j],dx=p.x-q.x,dy=p.y-q.y,dist=Math.sqrt(dx*dx+dy*dy);
      if(dist<120){
        ctx.beginPath();ctx.moveTo(p.x,p.y);ctx.lineTo(q.x,q.y);
        ctx.strokeStyle='rgba(74,222,128,'+(0.12*(1-dist/120))+')';
        ctx.lineWidth=0.5;ctx.stroke();
      }
    }
  }
  requestAnimationFrame(draw);
}
draw();
window.addEventListener('resize',function(){W=c.width=window.innerWidth;H=c.height=window.innerHeight;});
})();
</script>
""", unsafe_allow_html=True)

# ── Helpers ─────────────────────────────────────────────────────────────────
def mkt_status(name):
    now = datetime.now(pytz.utc).astimezone(pytz.timezone("America/New_York"))
    if name == "Crypto": return "24/7", "#4ade80"
    if now.weekday() >= 5: return "Closed", "#f87171"
    s = now.replace(hour=9, minute=30, second=0, microsecond=0)
    e = now.replace(hour=16, minute=0,  second=0, microsecond=0)
    if s <= now <= e:  return "Open",        "#4ade80"
    elif now < s:      return "Pre-Market",  "#fbbf24"
    else:              return "After-Hours", "#fbbf24"

@st.cache_data(ttl=1800)
def get_tape(tickers):
    out = []
    for s in tickers:
        try:
            h = yf.Ticker(s).history(period="2d")
            if len(h) >= 2:
                p, c = float(h["Close"].iloc[-2]), float(h["Close"].iloc[-1])
                chg = (c - p) / p * 100
                out.append((s, f"{c:,.2f}", f"{chg:+.2f}%", "▲" if chg >= 0 else "▼", chg >= 0))
        except: pass
    return out

# ── Nav link helper — replaces page_link ─────────────────────────────────────
def nav_btn(label, path, primary=False):
    color = "#0a0f0a" if primary else "#9ca3af"
    bg    = "#4ade80" if primary else "transparent"
    bdr   = "#4ade80" if primary else "#2d333b"
    hover_bg = "#6ee7a0" if primary else "rgba(74,222,128,0.06)"
    st.markdown(f"""
    <a href="{path}" style="display:inline-flex;align-items:center;justify-content:center;
    font-family:'IBM Plex Mono',monospace;font-size:0.65rem;font-weight:700;
    text-transform:uppercase;letter-spacing:0.1em;text-decoration:none;
    color:{color};background:{bg};border:1px solid {bdr};border-radius:8px;
    padding:0.55rem 1.2rem;cursor:pointer;transition:all 0.15s;width:100%;text-align:center;">
    {label}</a>""", unsafe_allow_html=True)

# ── Welcome banner ─────────────────────────────────────────────────────────
user_email = st.session_state.get("user_email","")
if user_email:
    uname = user_email.split("@")[0].replace("."," ").replace("_"," ").title()
    st.markdown(f"""
    <div style="background:rgba(74,222,128,0.05);border:1px solid rgba(74,222,128,0.18);
    border-radius:10px;padding:0.8rem 1.3rem;margin-bottom:1.2rem;
    display:flex;align-items:center;justify-content:space-between;">
        <div style="display:flex;align-items:center;gap:0.75rem">
            <div style="width:34px;height:34px;border-radius:50%;background:rgba(74,222,128,0.1);
            border:1px solid rgba(74,222,128,0.25);display:flex;align-items:center;justify-content:center;
            font-family:'IBM Plex Mono',monospace;font-size:0.7rem;font-weight:700;color:#4ade80">
            {uname[0].upper()}</div>
            <div>
                <div style="font-family:'IBM Plex Mono',monospace;font-size:0.5rem;color:#3d4450;
                text-transform:uppercase;letter-spacing:0.15em;margin-bottom:0.1rem">Welcome back</div>
                <div style="font-size:0.95rem;font-weight:600;color:#e6eaf0">Hi, {uname}</div>
            </div>
        </div>
        <div style="font-family:'IBM Plex Mono',monospace;font-size:0.55rem;color:#3d4450">
            Ready to trade smarter?
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Ticker tape ──────────────────────────────────────────────────────────────
TICKERS = ["AAPL","TSLA","SPY","NVDA","MSFT","AMZN","BTC-USD","META","GOOGL","AMD",
           "NFLX","JPM","V","QQQ","GLD","PLTR","COIN","TSM","SMCI","WMT"]
tape = get_tape(tuple(TICKERS))
if tape:
    items = "".join(
        f'<span class="ticker-item">'
        f'<span class="t-sym">{s}</span>'
        f'<span class="{"t-up" if up else "t-dn"}">{p} {a} {ch}</span>'
        f'</span>'
        for s,p,ch,a,up in tape
    )
    st.markdown(f'<div class="ticker-outer"><div class="ticker-track">{items}{items}</div></div>', unsafe_allow_html=True)

# ── HERO ────────────────────────────────────────────────────────────────────
hl, hr = st.columns([6, 5])

with hl:
    # Animated candlestick bars
    bars = [(35,"#f87171"),(42,"#4ade80"),(26,"#f87171"),(50,"#4ade80"),(58,"#4ade80"),
            (32,"#f87171"),(60,"#4ade80"),(66,"#4ade80"),(36,"#f87171"),(70,"#4ade80"),
            (76,"#4ade80"),(44,"#f87171"),(78,"#4ade80"),(72,"#4ade80"),(80,"#4ade80"),
            (62,"#f87171"),(84,"#4ade80"),(75,"#f87171"),(88,"#4ade80"),(92,"#4ade80")]
    bars_html = "".join(
        f'<div style="width:11px;height:{h}px;background:{c};border-radius:2px 2px 0 0;opacity:0.9;'
        f'animation:fadeUp 0.5s ease both;animation-delay:{i*0.03}s"></div>'
        for i,(h,c) in enumerate(bars)
    )

    # Market status
    mkt_html = ""
    for label, mname in [("NYSE","NYSE"),("NASDAQ","NASDAQ"),("Crypto","Crypto")]:
        st2, col2 = mkt_status(mname)
        dot_style = "animation:pulse 2s ease-in-out infinite" if "Open" in st2 or "24" in st2 else ""
        mkt_html += f'<span style="display:inline-flex;align-items:center;gap:5px;font-family:IBM Plex Mono,monospace;font-size:0.58rem;color:{col2};background:{col2}12;border:1px solid {col2}25;border-radius:20px;padding:3px 10px;"><span style="width:6px;height:6px;border-radius:50%;background:{col2};display:inline-block;{dot_style}"></span>{label} · {st2}</span>'

    st.markdown(f"""
    <div style="padding:1.2rem 0 1.5rem;animation:fadeUp 0.4s ease both">
        <div style="display:flex;align-items:flex-end;gap:3px;height:68px;margin-bottom:1.2rem">
            {bars_html}
        </div>
        <div style="font-family:'Bebas Neue',sans-serif;font-size:5rem;line-height:0.88;
        letter-spacing:0.02em;margin-bottom:1.2rem">
            <span style="color:#4ade80">Trade</span><br>
            <span style="color:#e6eaf0">Smarter.</span>
        </div>
        <div style="font-size:0.88rem;color:#6b7280;max-width:440px;line-height:1.85;margin-bottom:1.4rem;font-family:Inter,sans-serif">
            Backtest real strategies, replay historical markets, get AI-powered analysis — 
            all in one platform. <strong style="color:#9ca3af">No cost. No fluff.</strong>
        </div>
        <div style="display:flex;gap:0.5rem;flex-wrap:wrap;margin-bottom:1.4rem">
            {mkt_html}
        </div>
    </div>
    """, unsafe_allow_html=True)

    b1, b2, b3 = st.columns(3)
    with b1: nav_btn("Strategy Lab",  "/Strategy_Lab", primary=True)
    with b2: nav_btn("Market Replay", "/Replay")
    with b3: nav_btn("AI Coach",      "/Assistant")

with hr:
    st.markdown("""
    <div style="padding:1.5rem 0 0;animation:fadeUp 0.5s ease both">
        <div style="background:#1c1f23;border:1px solid #2d333b;border-radius:10px 10px 0 0;
        border-bottom:none;padding:0.45rem 0.9rem;
        display:flex;align-items:center;gap:5px">
            <div style="width:9px;height:9px;border-radius:50%;background:#f87171"></div>
            <div style="width:9px;height:9px;border-radius:50%;background:#fbbf24"></div>
            <div style="width:9px;height:9px;border-radius:50%;background:#4ade80"></div>
            <span style="margin-left:5px;font-family:'IBM Plex Mono',monospace;font-size:0.48rem;
            color:#3d4450;text-transform:uppercase;letter-spacing:0.16em">Live Chart</span>
        </div>
    </div>""", unsafe_allow_html=True)

    st.components.v1.html("""
<style>*{margin:0;padding:0}body{background:#1c1f23}.w{height:310px;width:100%;
background:#1c1f23;border:1px solid #2d333b;border-top:none;border-radius:0 0 10px 10px;overflow:hidden}</style>
<div class="w">
<div class="tradingview-widget-container" style="height:100%;width:100%">
<div id="tv_c" style="height:100%;width:100%"></div>
<script src="https://s3.tradingview.com/tv.js"></script>
<script>new TradingView.widget({
autosize:true,symbol:"NASDAQ:AAPL",interval:"D",timezone:"America/New_York",
theme:"dark",style:"1",locale:"en",toolbar_bg:"#1c1f23",
enable_publishing:false,hide_side_toolbar:true,allow_symbol_change:true,
save_image:false,container_id:"tv_c",backgroundColor:"rgba(28,31,35,1)",
gridColor:"rgba(37,42,48,0.6)",
overrides:{
"mainSeriesProperties.candleStyle.upColor":"#4ade80",
"mainSeriesProperties.candleStyle.downColor":"#f87171",
"mainSeriesProperties.candleStyle.borderUpColor":"#4ade80",
"mainSeriesProperties.candleStyle.borderDownColor":"#f87171",
"mainSeriesProperties.candleStyle.wickUpColor":"#4ade80",
"mainSeriesProperties.candleStyle.wickDownColor":"#f87171",
"paneProperties.background":"#1c1f23","paneProperties.backgroundType":"solid",
"paneProperties.vertGridProperties.color":"#252a30",
"paneProperties.horzGridProperties.color":"#252a30",
"scalesProperties.textColor":"#3d4450","scalesProperties.lineColor":"#252a30"}});</script>
</div></div>""", height=322, scrolling=False)

    st.markdown("""
    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:6px;margin-top:0.7rem">
        <div style="background:#1c1f23;border:1px solid #2d333b;border-radius:8px;padding:0.9rem;text-align:center">
            <div style="font-family:'IBM Plex Mono',monospace;font-size:1.5rem;font-weight:700;color:#4ade80;line-height:1">15</div>
            <div style="font-family:'IBM Plex Mono',monospace;font-size:0.45rem;text-transform:uppercase;letter-spacing:0.18em;color:#3d4450;margin-top:0.2rem">Indicators</div>
        </div>
        <div style="background:#1c1f23;border:1px solid #2d333b;border-radius:8px;padding:0.9rem;text-align:center">
            <div style="font-family:'IBM Plex Mono',monospace;font-size:1.5rem;font-weight:700;color:#f87171;line-height:1">9</div>
            <div style="font-family:'IBM Plex Mono',monospace;font-size:0.45rem;text-transform:uppercase;letter-spacing:0.18em;color:#3d4450;margin-top:0.2rem">Strategies</div>
        </div>
        <div style="background:#1c1f23;border:1px solid #2d333b;border-radius:8px;padding:0.9rem;text-align:center">
            <div style="font-family:'IBM Plex Mono',monospace;font-size:1.5rem;font-weight:700;color:#60a5fa;line-height:1">20+</div>
            <div style="font-family:'IBM Plex Mono',monospace;font-size:0.45rem;text-transform:uppercase;letter-spacing:0.18em;color:#3d4450;margin-top:0.2rem">Tools</div>
        </div>
        <div style="background:#1c1f23;border:1px solid #2d333b;border-radius:8px;padding:0.9rem;text-align:center">
            <div style="font-family:'IBM Plex Mono',monospace;font-size:1.5rem;font-weight:700;color:#fbbf24;line-height:1">$0</div>
            <div style="font-family:'IBM Plex Mono',monospace;font-size:0.45rem;text-transform:uppercase;letter-spacing:0.18em;color:#3d4450;margin-top:0.2rem">Forever</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── FEATURES ────────────────────────────────────────────────────────────────
st.markdown('<div style="font-family:IBM Plex Mono,monospace;font-size:0.48rem;text-transform:uppercase;letter-spacing:0.3em;color:#3d4450;border-top:1px solid #252a30;padding-top:1.5rem;margin-top:1.8rem;margin-bottom:1rem">Platform Features</div>', unsafe_allow_html=True)

features = [
    ("Strategy Lab",     "BACKTEST",  "#4ade80", "/Strategy_Lab",
     "9 pre-built strategies + custom signal builder with 15 indicators. Real equity curves, trade logs, alpha vs buy-and-hold."),
    ("Market Replay",    "FLAGSHIP",  "#f87171", "/Replay",
     "Step through history bar by bar. Execute trades blind. Build real pattern-recognition instincts without risking capital."),
    ("AI Coach",         "AI",        "#60a5fa", "/Assistant",
     "Ask anything. Get backtest results explained, strategy feedback, risk management advice in plain English."),
    ("Options Chain",    "NEW",       "#a78bfa", "/Options_Chain",
     "Live chain, full Greeks, Black-Scholes pricer, and a Play Advisor that scores every strategy for your specific setup."),
    ("Screener",         "PRO",       "#4ade80", "/Screener",
     "Filter 70+ stocks by RSI, momentum, SMA position, volume spikes. TradingView-style sortable results."),
    ("Market Heatmap",   "LIVE",      "#fbbf24", "/Market_Heatmap",
     "Sector heatmap, custom ticker dashboard, and full-screen ticker display for trading monitors."),
]

fc = st.columns(3)
for i, (title, badge, color, path, desc) in enumerate(features):
    with fc[i%3]:
        st.markdown(f"""
        <div style="background:#1c1f23;border:1px solid #2d333b;border-radius:10px;
        padding:1.3rem;margin-bottom:10px;min-height:170px;position:relative;overflow:hidden;
        transition:border-color 0.2s,transform 0.2s;animation:fadeUp 0.4s ease both;
        animation-delay:{i*0.07}s">
            <div style="position:absolute;top:0;left:0;right:0;height:2px;
            background:linear-gradient(90deg,transparent,{color}55,transparent)"></div>
            <div style="display:inline-block;font-family:'IBM Plex Mono',monospace;font-size:0.46rem;
            text-transform:uppercase;letter-spacing:0.14em;padding:2px 8px;border-radius:3px;
            background:{color}12;color:{color};border:1px solid {color}25;margin-bottom:0.7rem">{badge}</div>
            <div style="font-family:'Bebas Neue',sans-serif;font-size:1.4rem;letter-spacing:0.04em;
            color:#e6eaf0;margin-bottom:0.35rem">{title}</div>
            <div style="font-family:'IBM Plex Mono',monospace;font-size:0.65rem;color:#6b7280;
            line-height:1.65">{desc}</div>
        </div>
        """, unsafe_allow_html=True)
        nav_btn(f"Open {title}", path)

# ── ALL TOOLS ────────────────────────────────────────────────────────────────
st.markdown('<div style="font-family:IBM Plex Mono,monospace;font-size:0.48rem;text-transform:uppercase;letter-spacing:0.3em;color:#3d4450;border-top:1px solid #252a30;padding-top:1.4rem;margin-top:1.4rem;margin-bottom:0.9rem">All Tools</div>', unsafe_allow_html=True)

tools = [
    ("Risk Calculator",   "Position sizing, Kelly, R-multiples",    "/Risk_Calculator"),
    ("Trade Journal",     "Log trades, emotions, pattern review",    "/Trade_Journal"),
    ("Portfolio Tracker", "Live P&L, allocation, sector exposure",   "/Portfolio_Tracker"),
    ("Monte Carlo",       "1,000 price path simulations",            "/Monte_Carlo"),
    ("Earnings Tracker",  "Historical earnings reactions",           "/Earnings"),
    ("Sector Rotation",   "Follow institutional money flows",        "/Sector_Rotation"),
    ("Whale Tracker",     "Unusual volume anomalies",                "/Whale_Tracker"),
    ("Correlations",      "Asset correlation heatmap",               "/Correlations"),
    ("Pattern Recognition","Auto-detect double tops, flags, S/R",   "/Pattern_Recognition"),
    ("Trade Stats",       "Upload CSV, full analytics dashboard",    "/Trade_Stats"),
    ("Econ Calendar",     "FOMC, CPI, NFP, GDP — 2026",             "/Economic_Calendar"),
    ("Analysis",          "Fundamentals + AI deep dive",             "/Analysis"),
]

tc = st.columns(4)
for i, (name, desc, path) in enumerate(tools):
    with tc[i%4]:
        st.markdown(f"""
        <a href="{path}" style="display:block;text-decoration:none;
        background:#1c1f23;border:1px solid #2d333b;border-radius:8px;
        padding:0.8rem 1rem;margin-bottom:8px;
        transition:border-color 0.18s;cursor:pointer;
        animation:fadeUp 0.4s ease both;animation-delay:{i*0.03}s">
            <div style="font-family:'IBM Plex Mono',monospace;font-weight:700;
            font-size:0.7rem;color:#e6eaf0;margin-bottom:0.15rem">{name}</div>
            <div style="font-family:'IBM Plex Mono',monospace;font-size:0.6rem;
            color:#3d4450;line-height:1.5">{desc}</div>
        </a>
        """, unsafe_allow_html=True)

# ── HOW IT WORKS ─────────────────────────────────────────────────────────────
st.markdown('<div style="font-family:IBM Plex Mono,monospace;font-size:0.48rem;text-transform:uppercase;letter-spacing:0.3em;color:#3d4450;border-top:1px solid #252a30;padding-top:1.4rem;margin-top:1.4rem;margin-bottom:0.9rem">How It Works</div>', unsafe_allow_html=True)

steps = [
    ("01", "Pick Your Stock",   "Enter any ticker — stocks, ETFs, indices, crypto. Live data from Yahoo Finance."),
    ("02", "Choose a Strategy", "Select from 9 pre-built or build your own with 15 indicators and AND/OR logic."),
    ("03", "Run the Backtest",  "Set date range and capital. Return, alpha, drawdown, Sharpe — in seconds."),
    ("04", "Replay the Chart",  "Step through the same period bar-by-bar and trade it without knowing the outcome."),
    ("05", "Ask the Coach",     "Paste results into the AI Coach. Get plain-English explanation of what worked."),
]
sc2 = st.columns(5)
for i,(num,title,desc) in enumerate(steps):
    with sc2[i]:
        st.markdown(f"""
        <div style="background:#1c1f23;border:1px solid #2d333b;border-radius:10px;
        padding:1.2rem;animation:fadeUp 0.4s ease both;animation-delay:{i*0.08}s">
            <div style="font-family:'Bebas Neue',sans-serif;font-size:3.5rem;
            color:#252a30;line-height:1;margin-bottom:0.25rem">{num}</div>
            <div style="font-family:'IBM Plex Mono',monospace;font-size:0.6rem;font-weight:700;
            text-transform:uppercase;letter-spacing:0.1em;color:#e6eaf0;margin-bottom:0.3rem">{title}</div>
            <div style="font-family:'IBM Plex Mono',monospace;font-size:0.63rem;
            color:#3d4450;line-height:1.65">{desc}</div>
        </div>""", unsafe_allow_html=True)

# ── WHY 11% ──────────────────────────────────────────────────────────────────
st.markdown('<div style="font-family:IBM Plex Mono,monospace;font-size:0.48rem;text-transform:uppercase;letter-spacing:0.3em;color:#3d4450;border-top:1px solid #252a30;padding-top:1.4rem;margin-top:1.4rem;margin-bottom:0.9rem">Why 11%?</div>', unsafe_allow_html=True)

st.markdown("""
<div style="background:#1c1f23;border:1px solid #2d333b;border-radius:12px;
padding:2rem 2.5rem;position:relative;overflow:hidden;animation:fadeUp 0.4s ease both">
    <div style="position:absolute;top:-40px;right:-40px;width:180px;height:180px;
    background:radial-gradient(circle,rgba(74,222,128,0.05),transparent 70%);pointer-events:none"></div>
    <div style="font-family:'Bebas Neue',sans-serif;font-size:3rem;letter-spacing:0.04em;
    margin-bottom:0.75rem;line-height:1">
        <span style="color:#4ade80">11</span><span style="color:#f87171">%</span>
        <span style="color:#e6eaf0;font-size:1.6rem;margin-left:0.4rem">— The edge that changes everything</span>
    </div>
    <div style="font-family:'IBM Plex Mono',monospace;font-size:0.72rem;color:#6b7280;
    line-height:2;max-width:760px">
        The S&P 500 returns roughly 10% per year. Most retail traders underperform it significantly.
        Getting to <strong style="color:#4ade80">11%</strong> — one point above the index — means your edge is real,
        your process is sound, and compounding is working for you.<br><br>
        That's the goal. Not moon shots. Not leverage. Not tips from strangers on the internet.
        <strong style="color:#e6eaf0">Consistent, process-driven, repeatable outperformance.</strong>
    </div>
</div>
""", unsafe_allow_html=True)

# ── FAQ ────────────────────────────────────────────────────────────────────
st.markdown('<div style="font-family:IBM Plex Mono,monospace;font-size:0.48rem;text-transform:uppercase;letter-spacing:0.3em;color:#3d4450;border-top:1px solid #252a30;padding-top:1.4rem;margin-top:1.4rem;margin-bottom:0.9rem">FAQ</div>', unsafe_allow_html=True)

fqa, fqb = st.columns(2)
faqs = [
    ("Is this real trading?",              "No. Fully simulated. No real money. Data from Yahoo Finance. Educational use only."),
    ("How accurate is the backtest?",      "Indicative only. Assumes close-price fills, no slippage or commission."),
    ("Do I need to code?",                 "No. Everything is point-and-click. Open-source Python/Streamlit under the hood."),
    ("How do I enable AI features?",       "Add GEMINI_API_KEY to Streamlit Secrets. Free Gemini tier is more than enough."),
    ("Is my data saved between sessions?", "Yes — create an account. Journal and portfolio sync to Supabase automatically."),
    ("Is it actually free?",               "Yes. No credit card, no trial, no premium tier. The full platform is permanently free."),
    ("What data does it use?",             "Yahoo Finance via yfinance. Years of daily OHLCV for US stocks, ETFs, and crypto."),
    ("Why can't backtests predict future?","Markets change. A strategy that worked in a bull run may fail in a bear. Understand why it works, not just that it did."),
]
for i,(q,a) in enumerate(faqs):
    with (fqa if i%2==0 else fqb).expander(q):
        st.markdown(f'<div style="font-family:IBM Plex Mono,monospace;font-size:0.72rem;color:#6b7280;line-height:1.8">{a}</div>', unsafe_allow_html=True)

# ── TICKER CHIP STRIP (like BacktestingMax bottom) ────────────────────────
if tape:
    chips = "".join(
        f'<span style="display:inline-flex;align-items:center;gap:6px;font-family:IBM Plex Mono,monospace;'
        f'font-size:0.62rem;background:#1c1f23;border:1px solid #2d333b;border-radius:6px;'
        f'padding:4px 12px;white-space:nowrap;color:{"#4ade80" if up else "#f87171"}">'
        f'<span style="color:#6b7280;font-weight:600">{s}</span>{p} {a} {ch}</span>'
        for s,p,ch,a,up in tape
    )
    st.markdown(f"""
    <div style="margin-top:2rem;border-top:1px solid #252a30;padding-top:1.2rem">
        <div style="font-family:IBM Plex Mono,monospace;font-size:0.46rem;text-transform:uppercase;
        letter-spacing:0.28em;color:#3d4450;margin-bottom:0.6rem">Market Snapshot</div>
        <div style="display:flex;flex-wrap:wrap;gap:6px">{chips}</div>
    </div>
    """, unsafe_allow_html=True)

# ── FOOTER ───────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-top:2rem;padding:1.2rem 0;border-top:1px solid #252a30;
display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:0.4rem">
    <div style="font-family:'Bebas Neue',sans-serif;font-size:1.1rem;letter-spacing:0.06em">
        <span style="color:#4ade80">11</span><span style="color:#f87171">%</span>
        <span style="font-family:'IBM Plex Mono',monospace;font-size:0.54rem;
        color:#3d4450;letter-spacing:0.1em;margin-left:0.4rem">TRADE SMARTER</span>
    </div>
    <div style="font-family:'IBM Plex Mono',monospace;font-size:0.52rem;color:#3d4450">
        Not financial advice &nbsp;·&nbsp; Educational use only &nbsp;·&nbsp; Data: Yahoo Finance
    </div>
</div>
""", unsafe_allow_html=True)
