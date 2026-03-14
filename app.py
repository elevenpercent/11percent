import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from utils.styles import SHARED_CSS, LOGO_IMG
from utils.nav import navbar
from utils.session_persist import restore_session

st.set_page_config(
    page_title="11% · Build Real Edge",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

restore_session()
if st.session_state.get("user"):
    st.switch_page("pages/21_Dashboard.py")

st.markdown("""<style>
html,body,[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"]>.main,.block-container{background:#0a0e14!important}
[data-testid="stSidebar"],[data-testid="stSidebarNav"],[data-testid="collapsedControl"],
section[data-testid="stSidebar"]{display:none!important;width:0!important;max-width:0!important;
opacity:0!important;visibility:hidden!important;pointer-events:none!important}
#MainMenu,footer,header{display:none!important}
.stDeployButton{display:none!important}
</style>""", unsafe_allow_html=True)

st.markdown(SHARED_CSS, unsafe_allow_html=True)

st.markdown("""<style>
:root{
  --bg:    #0a0e14;
  --bg2:   #0f1420;
  --bg3:   #141926;
  --chart: #0d1117;
  --border:#1a2235;
  --border2:#1f2a3d;
  --text:  #e2e8f0;
  --text2: #64748b;
  --green: #00ff88;
  --green2:#00cc6a;
  --red:   #ff3d5a;
  --red2:  #cc2244;
  --dim:   #1e2d40;
  --dim2:  #2a3a50;
}
html,body,[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"]>.main,
.block-container{background:var(--bg)!important}
.block-container{
  padding-top:0!important;padding-bottom:4rem!important;
  padding-left:2.5rem!important;padding-right:2.5rem!important;
  max-width:100%!important;
}

/* ── Animated chart canvas background ── */
#chart-canvas{
  position:fixed;top:0;left:0;width:100vw;height:100vh;
  pointer-events:none;z-index:0;opacity:0.35;
}

/* ── Spotlight — centered, lower ── */
.spotlight{
  position:fixed;
  top:55%;left:50%;
  transform:translate(-50%,-50%);
  width:900px;height:500px;
  background:radial-gradient(ellipse at center,
    rgba(0,255,136,0.06) 0%,
    rgba(0,100,255,0.04) 40%,
    transparent 70%);
  pointer-events:none;z-index:1;
}
.spotlight-red{
  position:fixed;
  top:65%;left:30%;
  transform:translate(-50%,-50%);
  width:600px;height:400px;
  background:radial-gradient(ellipse at center,
    rgba(255,61,90,0.04) 0%,
    transparent 65%);
  pointer-events:none;z-index:1;
}

/* ── Grid lines background ── */
.grid-bg{
  position:fixed;top:0;left:0;width:100%;height:100%;
  pointer-events:none;z-index:0;
  background-image:
    linear-gradient(rgba(0,255,136,0.02) 1px,transparent 1px),
    linear-gradient(90deg,rgba(0,255,136,0.02) 1px,transparent 1px);
  background-size:60px 60px;
}

/* ── Sections ── */
.hp-wrap{position:relative;z-index:2;}
.hp-section{position:relative;z-index:2;padding:5rem 0 1rem;}
.hp-section-sm{position:relative;z-index:2;padding:2.5rem 0 1rem;}

/* ── Hero ── */
.hero-eyebrow{
  font-family:'IBM Plex Mono',monospace;font-size:0.55rem;
  text-transform:uppercase;letter-spacing:0.4em;
  color:var(--green);opacity:0.8;margin-bottom:1.2rem;
  display:flex;align-items:center;gap:0.6rem;
}
.hero-eyebrow::before{
  content:'';width:20px;height:1px;background:var(--green);opacity:0.6;
}
.hero-h1{
  font-family:'Bebas Neue',sans-serif;font-size:5.2rem;
  letter-spacing:0.02em;line-height:0.9;color:var(--text);
  margin:0 0 1.2rem;
}
.hero-h1 .green{color:var(--green);}
.hero-h1 .red{color:var(--red);}
.hero-sub{
  font-size:0.9rem;color:var(--text2);line-height:1.9;
  font-family:'Inter',sans-serif;max-width:480px;margin-bottom:2rem;
}
.hero-btns{display:flex;gap:0.8rem;align-items:center;flex-wrap:wrap;margin-bottom:1.5rem;}
.btn-primary{
  background:var(--green);color:#020a06;
  font-family:'IBM Plex Mono',monospace;font-size:0.68rem;font-weight:700;
  text-transform:uppercase;letter-spacing:0.12em;
  padding:0.8rem 2.2rem;border-radius:6px;text-decoration:none;
  display:inline-block;transition:all 0.18s;
  box-shadow:0 0 30px rgba(0,255,136,0.2);
}
.btn-primary:hover{background:#33ffaa;box-shadow:0 0 50px rgba(0,255,136,0.35);transform:translateY(-1px);}
.btn-secondary{
  background:transparent;color:var(--text2);
  border:1px solid var(--border2);
  font-family:'IBM Plex Mono',monospace;font-size:0.68rem;font-weight:600;
  text-transform:uppercase;letter-spacing:0.12em;
  padding:0.8rem 1.8rem;border-radius:6px;text-decoration:none;
  display:inline-block;transition:all 0.18s;
}
.btn-secondary:hover{border-color:var(--red);color:var(--red);}
.hero-badge{
  display:inline-flex;align-items:center;gap:0.5rem;
  font-family:'IBM Plex Mono',monospace;font-size:0.52rem;
  color:var(--dim2);text-transform:uppercase;letter-spacing:0.2em;
}
.hero-badge-dot{width:6px;height:6px;border-radius:50%;background:var(--green);
  animation:blink 2s ease-in-out infinite;}
@keyframes blink{0%,100%{opacity:1;box-shadow:0 0 6px var(--green);}50%{opacity:0.3;box-shadow:none;}}

/* ── Live chart mock ── */
.chart-wrap{
  background:var(--chart);border:1px solid var(--border);
  border-radius:12px;overflow:hidden;
  box-shadow:0 0 60px rgba(0,0,0,0.6),0 0 120px rgba(0,255,136,0.04);
}
.chart-topbar{
  background:#0d1117;border-bottom:1px solid var(--border);
  padding:0.5rem 1rem;display:flex;align-items:center;gap:8px;
}
.c-dot{width:8px;height:8px;border-radius:50%;}

/* ── Conveyor ── */
@keyframes scrollL{0%{transform:translateX(0)}100%{transform:translateX(-50%)}}
@keyframes scrollR{0%{transform:translateX(-50%)}100%{transform:translateX(0%)}}
.conv-outer{overflow:hidden;position:relative;margin-bottom:0.4rem;}
.conv-outer::before,.conv-outer::after{
  content:'';position:absolute;top:0;bottom:0;width:80px;z-index:2;pointer-events:none;
}
.conv-outer::before{left:0;background:linear-gradient(90deg,var(--bg),transparent);}
.conv-outer::after{right:0;background:linear-gradient(-90deg,var(--bg),transparent);}
.conv-track{display:flex;white-space:nowrap;width:max-content;}
.conv-track.left{animation:scrollL 50s linear infinite;}
.conv-track.right{animation:scrollR 55s linear infinite;}
.conv-track:hover{animation-play-state:paused;}
.conv-chip{
  display:inline-flex;align-items:center;
  background:var(--bg2);border:1px solid var(--border);border-radius:5px;
  font-family:'IBM Plex Mono',monospace;font-size:0.6rem;
  padding:3px 12px;margin:0 3px;white-space:nowrap;height:28px;
  transition:border-color 0.2s;
}
.conv-chip:hover{border-color:var(--border2);}

/* ── Stats bar ── */
.stats-row{
  display:grid;grid-template-columns:repeat(4,1fr);gap:0;
  background:var(--bg2);border:1px solid var(--border);border-radius:12px;
  overflow:hidden;margin:3rem 0;
}
.stats-cell{padding:1.5rem 1.8rem;border-right:1px solid var(--border);position:relative;}
.stats-cell:last-child{border-right:none;}
.stats-cell::after{
  content:'';position:absolute;top:0;left:0;right:0;height:2px;
  opacity:0;transition:opacity 0.3s;
}
.stats-cell:hover::after{opacity:1;}
.stats-cell:nth-child(1)::after,.stats-cell:nth-child(3)::after{background:linear-gradient(90deg,transparent,var(--green),transparent);}
.stats-cell:nth-child(2)::after,.stats-cell:nth-child(4)::after{background:linear-gradient(90deg,transparent,var(--red),transparent);}
.stats-n{font-family:'Bebas Neue',sans-serif;font-size:3rem;letter-spacing:0.04em;line-height:1;}
.stats-n.g{color:var(--green);text-shadow:0 0 30px rgba(0,255,136,0.3);}
.stats-n.r{color:var(--red);text-shadow:0 0 30px rgba(255,61,90,0.3);}
.stats-l{font-family:'IBM Plex Mono',monospace;font-size:0.48rem;text-transform:uppercase;
  letter-spacing:0.22em;color:var(--dim2);margin-top:0.3rem;}

/* ── Feature grid ── */
.feat-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:1px;
  background:var(--border);border:1px solid var(--border);border-radius:12px;overflow:hidden;}
.feat-cell{
  background:var(--bg2);padding:1.8rem;
  transition:background 0.2s;position:relative;
}
.feat-cell:hover{background:var(--bg3);}
.feat-cell::before{
  content:'';position:absolute;top:0;left:0;width:2px;height:100%;
  background:var(--green);opacity:0;transition:opacity 0.2s;
}
.feat-cell:hover::before{opacity:1;}
.feat-cell.red::before{background:var(--red);}
.feat-icon{font-size:1.4rem;margin-bottom:0.9rem;}
.feat-title{font-family:'IBM Plex Mono',monospace;font-size:0.65rem;font-weight:700;
  color:var(--text);text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.5rem;}
.feat-body{font-family:'Inter',sans-serif;font-size:0.74rem;color:var(--text2);line-height:1.75;}

/* ── CTA ── */
.cta-wrap{
  background:var(--bg2);
  border:1px solid var(--border);border-radius:16px;
  padding:5rem 3rem;text-align:center;position:relative;overflow:hidden;
}
.cta-wrap::before{
  content:'';position:absolute;top:0;left:0;right:0;height:1px;
  background:linear-gradient(90deg,transparent,var(--green),transparent);
}
.cta-wrap::after{
  content:'';position:absolute;bottom:0;left:0;right:0;height:1px;
  background:linear-gradient(90deg,transparent,var(--red),transparent);
}
.cta-title{font-family:'Bebas Neue',sans-serif;font-size:4rem;
  letter-spacing:0.03em;line-height:0.9;color:var(--text);margin-bottom:0.9rem;}
.cta-sub{font-family:'Inter',sans-serif;font-size:0.84rem;color:var(--text2);
  max-width:420px;margin:0 auto 2rem;line-height:1.85;}

/* ── Section label ── */
.sec-label{
  font-family:'IBM Plex Mono',monospace;font-size:0.5rem;
  text-transform:uppercase;letter-spacing:0.4em;
  color:var(--dim2);text-align:center;margin-bottom:0.6rem;
}
.sec-title{
  font-family:'Bebas Neue',sans-serif;font-size:2.6rem;
  letter-spacing:0.04em;color:var(--text);text-align:center;
  margin-bottom:2.5rem;
}
.sec-title span.g{color:var(--green);}
.sec-title span.r{color:var(--red);}

/* ── Conveyor section ── */
.conv-section{padding:3rem 0;position:relative;z-index:2;}

/* ── Footer ── */
.footer-wrap{
  border-top:1px solid var(--border);padding:3rem 0;margin-top:2rem;
  display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:2rem;
  position:relative;z-index:2;
}
.footer-brand{font-family:'Bebas Neue',sans-serif;font-size:1.4rem;letter-spacing:0.06em;margin-bottom:0.4rem;}
.footer-col-title{font-family:'IBM Plex Mono',monospace;font-size:0.5rem;
  text-transform:uppercase;letter-spacing:0.22em;color:var(--dim2);margin-bottom:0.7rem;}
.footer-link{display:block;font-family:'IBM Plex Mono',monospace;font-size:0.6rem;
  color:var(--text2);text-decoration:none;margin-bottom:0.35rem;transition:color 0.15s;}
.footer-link:hover{color:var(--green);}
.footer-legal{font-family:'IBM Plex Mono',monospace;font-size:0.48rem;color:var(--dim2);margin-top:0.5rem;}
</style>""", unsafe_allow_html=True)

# ── Background divs ───────────────────────────────────────────────────────────
st.markdown("""
<div class="grid-bg"></div>
<div class="spotlight"></div>
<div class="spotlight-red"></div>
<canvas id="chart-canvas"></canvas>
""", unsafe_allow_html=True)

# ── Animated canvas script via components (scripts work here) ─────────────────
import streamlit.components.v1 as _cv1
_cv1.html("""<script>
(function(){
  var doc = window.parent.document;
  var canvas = doc.getElementById('chart-canvas');
  if(!canvas){setTimeout(arguments.callee,200);return;}
  var ctx = canvas.getContext('2d');
  function resize(){canvas.width=window.parent.innerWidth;canvas.height=window.parent.innerHeight;}
  resize();
  window.parent.addEventListener('resize',function(){resize();initBars();});
  var bars=[],barW=14,gap=4,step=barW+gap;
  function initBars(){
    bars=[];
    var count=Math.ceil(canvas.width/step)+2;
    var price=150;
    for(var i=0;i<count;i++){
      price+=(Math.random()-0.48)*4;
      bars.push({open:price+(Math.random()-0.5)*2,close:price,high:price+Math.random()*3,low:price-Math.random()*3});
    }
  }
  initBars();
  var offset=0,scale=3;
  function draw(){
    var baseY=canvas.height*0.6;
    ctx.clearRect(0,0,canvas.width,canvas.height);
    offset+=0.15;
    if(offset>=step){
      offset-=step;bars.shift();
      var last=bars[bars.length-1];
      var price=last.close+(Math.random()-0.48)*4;
      bars.push({open:price+(Math.random()-0.5)*2,close:price,high:price+Math.random()*3,low:price-Math.random()*3});
    }
    bars.forEach(function(b,i){
      var x=i*step-offset;
      var bull=b.close>=b.open;
      var col=bull?'rgba(0,255,136,':'rgba(255,61,90,';
      var yO=baseY-b.open*scale,yC=baseY-b.close*scale;
      var yH=baseY-b.high*scale,yL=baseY-b.low*scale;
      var top=Math.min(yO,yC),h=Math.max(Math.abs(yO-yC),2);
      ctx.fillStyle=col+'0.65)';ctx.fillRect(x,top,barW,h);
      ctx.strokeStyle=col+'0.45)';ctx.lineWidth=1;
      ctx.beginPath();ctx.moveTo(x+barW/2,yH);ctx.lineTo(x+barW/2,top);
      ctx.moveTo(x+barW/2,top+h);ctx.lineTo(x+barW/2,yL);ctx.stroke();
    });
    requestAnimationFrame(draw);
  }
  draw();
  doc.addEventListener('click',function(e){
    var a=e.target.closest('a[href]');
    if(!a)return;
    var href=a.getAttribute('href');
    if(!href||href.startsWith('http')||href.startsWith('mailto')||href.startsWith('#'))return;
    e.preventDefault();
    try{window.top.location.href=href;}catch(err){window.location.href=href;}
  },true);
})();
</script>""", height=0)

navbar()

# ═══════════════════════════════════════════════════════════════
# HERO
# ═══════════════════════════════════════════════════════════════
hero_l, hero_r = st.columns([5, 4])

with hero_l:
    st.markdown("""
    <div class="hp-wrap" style="padding:3.5rem 0 1rem">
        <div class="hero-eyebrow">
            <span class="hero-badge-dot"></span>
            Professional Trading Education
        </div>
        <div class="hero-h1">
            Stop Guessing.<br>
            Start <span class="green">Winning</span><br>
            <span class="red">With Edge.</span>
        </div>
        <div class="hero-sub">
            11% gives you the tools professional traders use — bar replay, strategy backtesting, 
            performance analytics, and live market research. All free. No excuses left.
        </div>
        <div class="hero-btns">
            <a class="btn-primary" href="/Strategy_Lab" target="_self">Backtest Now</a>
            <a class="btn-secondary" href="/Replay" target="_self">Try Bar Replay</a>
        </div>
        <div class="hero-badge">
            <span class="hero-badge-dot"></span>
            Free forever &nbsp;·&nbsp; No card required &nbsp;·&nbsp; Real market data
        </div>
    </div>
    """, unsafe_allow_html=True)

with hero_r:
    st.markdown("""
    <div style="position:relative;z-index:2;padding:3rem 0 0">
        <div class="chart-wrap">
            <div class="chart-topbar">
                <div class="c-dot" style="background:#ff3d5a"></div>
                <div class="c-dot" style="background:#fbbf24"></div>
                <div class="c-dot" style="background:#00ff88"></div>
                <span style="font-family:'IBM Plex Mono',monospace;font-size:0.45rem;color:#1e2d40;
                margin-left:8px;text-transform:uppercase;letter-spacing:0.16em">Strategy Lab · NVDA · 1D</span>
                <span style="font-family:'IBM Plex Mono',monospace;font-size:0.45rem;color:#00ff88;
                margin-left:auto;letter-spacing:0.1em">+2.34%</span>
            </div>
    """, unsafe_allow_html=True)
    st.components.v1.html("""
<style>*{margin:0;padding:0}body{background:#0d1117}.w{height:300px;background:#0d1117;overflow:hidden}</style>
<div class="w">
<div class="tradingview-widget-container" style="height:100%;width:100%">
<div id="tv_c" style="height:100%;width:100%"></div>
<script src="https://s3.tradingview.com/tv.js"></script>
<script>new TradingView.widget({
autosize:true,symbol:"NASDAQ:NVDA",interval:"D",timezone:"America/New_York",
theme:"dark",style:"1",locale:"en",toolbar_bg:"#0d1117",
enable_publishing:false,hide_side_toolbar:true,hide_top_toolbar:true,
allow_symbol_change:true,save_image:false,container_id:"tv_c",
backgroundColor:"rgba(13,17,23,1)",gridColor:"rgba(26,34,53,0.8)",
overrides:{
"mainSeriesProperties.candleStyle.upColor":"#00ff88",
"mainSeriesProperties.candleStyle.downColor":"#ff3d5a",
"mainSeriesProperties.candleStyle.borderUpColor":"#00ff88",
"mainSeriesProperties.candleStyle.borderDownColor":"#ff3d5a",
"mainSeriesProperties.candleStyle.wickUpColor":"#00ff88",
"mainSeriesProperties.candleStyle.wickDownColor":"#ff3d5a",
"paneProperties.background":"#0d1117","paneProperties.backgroundType":"solid",
"paneProperties.vertGridProperties.color":"#1a2235",
"paneProperties.horzGridProperties.color":"#1a2235",
"scalesProperties.textColor":"#1e2d40","scalesProperties.lineColor":"#1a2235"}});</script>
</div></div>""", height=302, scrolling=False)
    st.markdown('</div></div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# STATS BAR
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<div style="position:relative;z-index:2;padding:2rem 0 0">
<div class="stats-row">
    <div class="stats-cell">
        <div class="stats-n g">33+</div>
        <div class="stats-l">Built-in Strategies</div>
    </div>
    <div class="stats-cell">
        <div class="stats-n r">56+</div>
        <div class="stats-l">Technical Indicators</div>
    </div>
    <div class="stats-cell">
        <div class="stats-n g">20Y+</div>
        <div class="stats-l">Historical Data</div>
    </div>
    <div class="stats-cell">
        <div class="stats-n r">$0</div>
        <div class="stats-l">Cost. Always.</div>
    </div>
</div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# CONVEYORS
# ═══════════════════════════════════════════════════════════════
st.markdown('<div class="conv-section">', unsafe_allow_html=True)
st.markdown('<div class="sec-label" style="position:relative;z-index:2">All markets. All instruments. All yours.</div>', unsafe_allow_html=True)

fx = ["EUR/USD","GBP/USD","USD/JPY","AUD/USD","USD/CAD","EUR/GBP","EUR/JPY","GBP/JPY","AUD/CAD","AUD/CHF","AUD/JPY","NZD/USD","USD/CHF","EUR/NZD","GBP/AUD","GBP/CAD","CAD/JPY","CHF/JPY","EUR/CAD","EUR/CHF"]
fx_chips = "".join(f'<span class="conv-chip" style="color:#64748b">{t}</span>' for t in fx)
st.markdown(f'<div class="conv-outer" style="position:relative;z-index:2"><div class="conv-track left">{fx_chips}{fx_chips}</div></div>', unsafe_allow_html=True)

crypto = ["BTC/USD","ETH/USD","SOL/USD","BNB/USD","ADA/USD","XRP/USD","DOGE/USD","AVAX/USD","MATIC/USD","LINK/USD","DOT/USD","UNI/USD","ATOM/USD","NEAR/USD","APE/USD","SHIB/USD","LTC/USD","BCH/USD","ALGO/USD","VET/USD"]
cr_chips = "".join(f'<span class="conv-chip" style="color:#00ff88">{t}</span>' for t in crypto)
st.markdown(f'<div class="conv-outer" style="position:relative;z-index:2"><div class="conv-track right">{cr_chips}{cr_chips}</div></div>', unsafe_allow_html=True)

stocks = ["AAPL","MSFT","NVDA","GOOGL","META","AMZN","TSLA","AMD","AVGO","CRM","JPM","GS","V","MA","BAC","XOM","UNH","LLY","SPY","QQQ","IWM","GLD","TLT","VXX","XAU/USD","CRUDE OIL","NAT GAS","USA500","NASDAQ","DOW30"]
st_chips = "".join(f'<span class="conv-chip" style="color:#ff3d5a">{t}</span>' for t in stocks)
st.markdown(f'<div class="conv-outer" style="position:relative;z-index:2"><div class="conv-track left">{st_chips}{st_chips}</div></div>', unsafe_allow_html=True)

try:
    from utils.indicators import INDICATOR_INFO
    inds = list(INDICATOR_INFO.keys())
except:
    inds = ["RSI","MACD","EMA","SMA","Bollinger Bands","ATR","Stochastic","CCI","Williams %R","OBV","VWAP","ADX","Ichimoku","Parabolic SAR","Pivot Points"]
ind_chips = "".join(f'<span class="conv-chip" style="color:#64748b">{i}</span>' for i in inds)
st.markdown(f'<div class="conv-outer" style="position:relative;z-index:2"><div class="conv-track right">{ind_chips}{ind_chips}</div></div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# FEATURES
# ═══════════════════════════════════════════════════════════════
st.markdown('<div class="hp-section" style="position:relative;z-index:2">', unsafe_allow_html=True)
st.markdown('<div class="sec-label">What you get</div>', unsafe_allow_html=True)
st.markdown('<div class="sec-title">Every tool a serious trader needs.<br><span class="g">None of the fluff.</span></div>', unsafe_allow_html=True)

features = [
    ("📊", "Strategy Backtester", "Run 33+ professional strategies on 20+ years of real data. Tweak parameters, compare results, and find what actually works before risking a dollar.", False),
    ("🔁", "Bar-by-Bar Replay", "Replay any market, any timeframe, bar by bar. Trade blind like it's happening live. The most realistic practice environment available.", False),
    ("⚔️", "Live Battles", "Compete head-to-head with other traders on the same historical period. Real leaderboards. Real bragging rights.", True),
    ("🧠", "AI Trade Coach", "Get instant analysis of your trades. Understand why your strategy succeeded or failed — not just the numbers, but the reasoning.", False),
    ("📈", "56+ Indicators", "Every major technical indicator built in. RSI, MACD, Ichimoku, Bollinger Bands, ATR and dozens more. Layer them, combine them, master them.", False),
    ("🛡", "Risk Calculator", "Calculate position size, risk/reward ratio, and max drawdown before entering any trade. Stop blowing accounts on bad sizing.", True),
    ("🔍", "Market Screener", "Scan thousands of instruments for your exact setup. Filter by technical conditions, volume, momentum, and more.", False),
    ("📰", "Earnings & Econ Calendar", "Never get caught off guard by a Fed announcement or earnings report again. Track every market-moving event.", False),
    ("📋", "Trade Journal", "Log every trade with full context. Track your patterns, biases, and improvement over time. Data-driven self-improvement.", True),
]

st.markdown('<div class="feat-grid" style="position:relative;z-index:2">', unsafe_allow_html=True)
for icon, title, body, is_red in features:
    red_class = "feat-cell red" if is_red else "feat-cell"
    st.markdown(f"""
    <div class="{red_class}">
        <div class="feat-icon">{icon}</div>
        <div class="feat-title">{title}</div>
        <div class="feat-body">{body}</div>
    </div>
    """, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# SECOND CHART SECTION
# ═══════════════════════════════════════════════════════════════
st.markdown('<div class="hp-section" style="position:relative;z-index:2">', unsafe_allow_html=True)
ch_l, ch_r = st.columns([4, 5])
with ch_l:
    st.markdown("""
    <div style="padding:2rem 0">
        <div class="hero-eyebrow"><span class="hero-badge-dot"></span>Replay Engine</div>
        <div style="font-family:'Bebas Neue',sans-serif;font-size:3.2rem;line-height:0.9;
        color:#e2e8f0;margin-bottom:1rem;letter-spacing:0.03em">
            Trade History<br>Like It's<br><span style="color:#00ff88">Happening Now</span>
        </div>
        <div style="font-family:'Inter',sans-serif;font-size:0.82rem;color:#64748b;
        line-height:1.85;max-width:360px;margin-bottom:1.5rem">
            Our bar replay engine lets you step through any market one candle at a time. 
            Practice reading price action, test your instincts, and build real pattern recognition 
            without any financial risk. Pause. Rewind. Replay until you've got it.
        </div>
        <a class="btn-primary" href="/Replay" target="_self">Launch Replay</a>
    </div>
    """, unsafe_allow_html=True)
with ch_r:
    st.markdown('<div class="chart-wrap" style="margin-top:1rem"><div class="chart-topbar"><div class="c-dot" style="background:#ff3d5a"></div><div class="c-dot" style="background:#fbbf24"></div><div class="c-dot" style="background:#00ff88"></div><span style="font-family:IBM Plex Mono,monospace;font-size:0.44rem;color:#1e2d40;margin-left:8px;text-transform:uppercase;letter-spacing:0.16em">Replay Mode · SPY · 1H</span></div>', unsafe_allow_html=True)
    st.components.v1.html("""
<style>*{margin:0;padding:0}body{background:#0d1117}.w{height:340px;background:#0d1117;overflow:hidden}</style>
<div class="w">
<div class="tradingview-widget-container" style="height:100%;width:100%">
<div id="tv_c2" style="height:100%;width:100%"></div>
<script src="https://s3.tradingview.com/tv.js"></script>
<script>new TradingView.widget({
autosize:true,symbol:"AMEX:SPY",interval:"60",timezone:"America/New_York",
theme:"dark",style:"1",locale:"en",toolbar_bg:"#0d1117",
enable_publishing:false,hide_side_toolbar:true,hide_top_toolbar:true,
allow_symbol_change:false,save_image:false,container_id:"tv_c2",
backgroundColor:"rgba(13,17,23,1)",gridColor:"rgba(26,34,53,0.8)",
overrides:{
"mainSeriesProperties.candleStyle.upColor":"#00ff88",
"mainSeriesProperties.candleStyle.downColor":"#ff3d5a",
"mainSeriesProperties.candleStyle.borderUpColor":"#00ff88",
"mainSeriesProperties.candleStyle.borderDownColor":"#ff3d5a",
"mainSeriesProperties.candleStyle.wickUpColor":"#00ff88",
"mainSeriesProperties.candleStyle.wickDownColor":"#ff3d5a",
"paneProperties.background":"#0d1117","paneProperties.backgroundType":"solid",
"paneProperties.vertGridProperties.color":"#1a2235",
"paneProperties.horzGridProperties.color":"#1a2235",
"scalesProperties.textColor":"#1e2d40","scalesProperties.lineColor":"#1a2235"}});</script>
</div></div>""", height=342, scrolling=False)
    st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# CTA
# ═══════════════════════════════════════════════════════════════
st.markdown('<div class="hp-section-sm" style="position:relative;z-index:2">', unsafe_allow_html=True)
st.markdown("""
<div class="cta-wrap">
    <div class="cta-title">Your Edge is<br>Waiting.</div>
    <div class="cta-sub">
        Every winning trader built their edge through practice, data, and honest self-review. 
        11% gives you all three — starting right now, for free.
    </div>
    <div style="display:flex;gap:0.8rem;justify-content:center;flex-wrap:wrap">
        <a class="btn-primary" href="/Strategy_Lab" target="_self">Start Backtesting Free</a>
        <a class="btn-secondary" href="/Signup" target="_self">Create Account</a>
    </div>
</div>
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<div class="footer-wrap">
    <div>
        <div class="footer-brand"><span style="color:#00ff88">11</span><span style="color:#ff3d5a">%</span></div>
        <div class="footer-legal">Professional trading education for serious traders.</div>
        <div class="footer-legal" style="margin-top:0.3rem">Not financial advice · Educational use only</div>
    </div>
    <div>
        <div class="footer-col-title">Platform</div>
        <a class="footer-link" href="/Strategy_Lab" target="_self">Strategy Lab</a>
        <a class="footer-link" href="/Replay" target="_self">Market Replay</a>
        <a class="footer-link" href="/Battles" target="_self">Battles</a>
        <a class="footer-link" href="/Marketplace" target="_self">Marketplace</a>
        <a class="footer-link" href="/Assistant" target="_self">AI Coach</a>
    </div>
    <div>
        <div class="footer-col-title">Tools</div>
        <a class="footer-link" href="/Screener" target="_self">Screener</a>
        <a class="footer-link" href="/Options_Chain" target="_self">Options Chain</a>
        <a class="footer-link" href="/Trade_Journal" target="_self">Trade Journal</a>
        <a class="footer-link" href="/Risk_Calculator" target="_self">Risk Calculator</a>
        <a class="footer-link" href="/Portfolio_Tracker" target="_self">Portfolio</a>
    </div>
    <div>
        <div class="footer-col-title">Research</div>
        <a class="footer-link" href="/Market_Heatmap" target="_self">Heatmap</a>
        <a class="footer-link" href="/Economic_Calendar" target="_self">Econ Calendar</a>
        <a class="footer-link" href="/Sector_Rotation" target="_self">Sector Rotation</a>
        <a class="footer-link" href="/Pattern_Recognition" target="_self">Patterns</a>
        <a class="footer-link" href="/Whale_Tracker" target="_self">Whale Tracker</a>
    </div>
</div>
""", unsafe_allow_html=True)
