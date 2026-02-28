import streamlit as st
import yfinance, pandas, numpy

st.set_page_config(page_title="11% — Trading Platform", page_icon="💲", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=IBM+Plex+Mono:wght@300;400;600;700&family=IBM+Plex+Sans:wght@300;400;600&display=swap');
    :root {
        --bg:#07090d; --surface:#0d1117; --border:#1c2333; --border2:#263045;
        --green:#00d68f; --red:#ff4757; --text:#cdd5e0; --muted:#3a4558;
        --grid:rgba(255,255,255,0.03);
    }
    html,body,[data-testid="stAppViewContainer"],[data-testid="stMain"],.main {
        background-color:var(--bg)!important; color:var(--text)!important;
        font-family:'IBM Plex Sans',sans-serif!important;
    }
    [data-testid="stMain"] {
        background-image:linear-gradient(var(--grid) 1px,transparent 1px),linear-gradient(90deg,var(--grid) 1px,transparent 1px)!important;
        background-size:48px 48px!important; padding-top:0!important;
    }
    .block-container { padding-top:0!important; padding-left:2rem!important; padding-right:2rem!important; max-width:100%!important; }
    [data-testid="stSidebar"],[data-testid="stSidebarNav"],[data-testid="collapsedControl"] { display:none!important; }
    /* Navbar */
    .navbar { background:#07090d; border-bottom:1px solid #1c2333; padding:0.7rem 2rem; display:flex; align-items:center; gap:2rem; margin-left:-2rem; margin-right:-2rem; margin-bottom:2rem; position:sticky; top:0; z-index:999; }
    .navbar-brand { font-family:'Bebas Neue',sans-serif; font-size:1.8rem; letter-spacing:0.1em; text-decoration:none; flex-shrink:0; }
    .navbar-brand .g { color:#00d68f; }
    .navbar-brand .r { color:#ff4757; }
    .nav-links { display:flex; gap:0.2rem; flex:1; }
    .nav-link { font-family:'IBM Plex Mono',monospace; font-size:0.68rem; text-transform:uppercase; letter-spacing:0.1em; color:#3a4558; text-decoration:none; padding:0.38rem 0.9rem; border-radius:3px; transition:all 0.15s; }
    .nav-link:hover { color:#00d68f; background:#0d1117; }
    .nav-link.active { color:#00d68f; background:#071a0f; border:1px solid #0d3320; }
    .nav-badge { font-family:'IBM Plex Mono',monospace; font-size:0.58rem; color:#3a4558; letter-spacing:0.12em; }
    /* Typography */
    h1 { font-family:'Bebas Neue',sans-serif!important; letter-spacing:0.06em; color:var(--text)!important; }
    h2 { font-family:'Bebas Neue',sans-serif!important; }
    h3 { font-family:'IBM Plex Mono',monospace!important; font-size:0.75rem!important; color:var(--green)!important; text-transform:uppercase; letter-spacing:0.15em; }
    /* Inputs */
    .stTextInput input, .stNumberInput input { background:#0d1117!important; border:1px solid #1c2333!important; color:#cdd5e0!important; font-family:'IBM Plex Mono',monospace!important; font-size:0.85rem!important; border-radius:3px!important; }
    .stTextInput input:focus, .stNumberInput input:focus { border-color:#00d68f!important; box-shadow:none!important; }
    div[data-baseweb="select"]>div { background:#0d1117!important; border:1px solid #1c2333!important; color:#cdd5e0!important; font-family:'IBM Plex Mono',monospace!important; border-radius:3px!important; }
    .stDateInput input { background:#0d1117!important; border:1px solid #1c2333!important; color:#cdd5e0!important; font-family:'IBM Plex Mono',monospace!important; border-radius:3px!important; }
    label { font-family:'IBM Plex Mono',monospace!important; font-size:0.68rem!important; color:#3a4558!important; text-transform:uppercase!important; letter-spacing:0.1em!important; }
    /* Buttons */
    .stButton>button { background:transparent!important; color:#00d68f!important; border:1px solid #00d68f!important; border-radius:3px!important; font-family:'IBM Plex Mono',monospace!important; font-weight:600!important; font-size:0.78rem!important; letter-spacing:0.1em!important; padding:0.45rem 1.4rem!important; transition:all 0.15s!important; text-transform:uppercase!important; }
    .stButton>button:hover { background:#00d68f!important; color:#000!important; }
    /* Metrics */
    .metric-card { background:#0d1117; border:1px solid #1c2333; padding:1rem; border-radius:4px; text-align:center; }
    .metric-val { font-family:'IBM Plex Mono',monospace; font-size:1.1rem; font-weight:700; }
    .metric-lbl { font-family:'IBM Plex Mono',monospace; font-size:0.55rem; color:#3a4558; text-transform:uppercase; margin-top:0.3rem; }
    .pos{color:#00d68f;} .neg{color:#ff4757;} .neu{color:#cdd5e0;}
    /* Config panel */
    .config-panel { background:#0d1117; border:1px solid #1c2333; border-radius:6px; padding:1.5rem 1.5rem 0.5rem 1.5rem; margin-bottom:1.5rem; }
    /* Dividers */
    .price-divider { display:flex; align-items:center; gap:1rem; margin:1.5rem 0; font-family:'IBM Plex Mono',monospace; font-size:0.65rem; color:#3a4558; }
    .price-divider::before,.price-divider::after { content:''; flex:1; height:1px; background:#1c2333; }
    /* Page header */
    .page-header { border-left:3px solid #00d68f; padding-left:1rem; margin-bottom:1.5rem; }
    .page-header p { color:#3a4558; font-size:0.88rem; margin-top:0.2rem; }
    /* Boxes */
    .info-box { background:#071a0f; border:1px solid #0d3320; border-radius:6px; padding:0.8rem 1rem; font-size:0.82rem; color:#00d68f; font-family:'IBM Plex Mono',monospace; }
    .warn-box { background:#1a0a08; border:1px solid #3a1008; border-radius:6px; padding:0.8rem 1rem; font-size:0.82rem; color:#ff4757; font-family:'IBM Plex Mono',monospace; }
    /* Chat */
    .chat-user { background:#0d1117; border:1px solid #1c2333; border-radius:10px 10px 3px 10px; padding:1rem 1.2rem; margin:0.6rem 0; }
    .chat-ai { background:#071a0f; border:1px solid #0d3320; border-radius:10px 10px 10px 3px; padding:1rem 1.2rem; margin:0.6rem 0; }
    .chat-lbl { font-family:'IBM Plex Mono',monospace; font-size:0.65rem; text-transform:uppercase; letter-spacing:0.12em; color:#3a4558; margin-bottom:0.4rem; }
    /* Ticker tape */
    .ticker-wrap { width:100%; overflow:hidden; background:#0d1117; border-bottom:1px solid #1c2333; padding:0.4rem 0; }
    .ticker-tape { display:inline-flex; animation:ticker 30s linear infinite; white-space:nowrap; }
    .ticker-item { font-family:'IBM Plex Mono',monospace; font-size:0.68rem; padding:0 1.5rem; letter-spacing:0.06em; }
    .ticker-up{color:#00d68f;} .ticker-down{color:#ff4757;}
    .ticker-sym { color:#cdd5e0; margin-right:0.4rem; }
    @keyframes ticker { 0%{transform:translateX(0)} 100%{transform:translateX(-50%)} }
    ::-webkit-scrollbar{width:4px;} ::-webkit-scrollbar-track{background:#07090d;} ::-webkit-scrollbar-thumb{background:#263045;border-radius:2px;}
    hr{border-color:#1c2333!important;}
    [data-testid="stExpander"]{background:#0d1117!important;border:1px solid #1c2333!important;border-radius:4px!important;}
</style>
""", unsafe_allow_html=True)
st.markdown('''<div class="navbar"><a class="navbar-brand" href="/app"><span class="g">11</span><span class="r">%</span></a><div class="nav-links"><a class="nav-link active" href="/app">🏠 Home</a><a class="nav-link" href="/1_Backtest">🔬 Backtest</a><a class="nav-link" href="/2_Indicator_Test">📊 Indicators</a><a class="nav-link" href="/3_Replay">▶ Replay</a><a class="nav-link" href="/4_Analysis">🧠 Analysis</a><a class="nav-link" href="/5_Assistant">💬 Assistant</a></div><span class="nav-badge">FREE · OPEN SOURCE</span></div>''', unsafe_allow_html=True)

TAPE_TICKERS = ["AAPL","TSLA","SPY","NVDA","MSFT","AMZN","BTC-USD","META","GOOGL","AMD","SOFI","HOOD","PLTR","NFLX"]
@st.cache_data(ttl=3600)
def get_tape_data(tickers):
    import yfinance as yf
    items=[]
    for sym in tickers:
        try:
            hist=yf.Ticker(sym).history(period="2d")
            if len(hist)>=2:
                prev=float(hist["Close"].iloc[-2]); close=float(hist["Close"].iloc[-1])
                chg=((close-prev)/prev)*100; up=chg>=0
                items.append((sym,f"{close:,.2f}",f"{chg:+.2f}%","▲" if up else "▼","ticker-up" if up else "ticker-down"))
        except: pass
    return items

with st.spinner("Loading market data..."): tape_items=get_tape_data(tuple(TAPE_TICKERS))
if tape_items:
    tape_html="".join(f'<span class="ticker-item"><span class="ticker-sym">{s}</span><span class="{c}">{p} {a}{ch}</span></span>' for s,p,ch,a,c in tape_items)*2
    st.markdown(f'<div class="ticker-wrap"><div class="ticker-tape">{tape_html}</div></div>', unsafe_allow_html=True)

left, right = st.columns([3,2])
with left:
    st.markdown("""
    <div style="padding:2.5rem 0 2rem 0;">
        <div style="font-family:'IBM Plex Mono',monospace;font-size:0.7rem;color:#00d68f;text-transform:uppercase;letter-spacing:0.25em;margin-bottom:0.8rem;">LIVE · FREE · OPEN SOURCE</div>
        <div style="font-family:'Bebas Neue',sans-serif;font-size:5.5rem;line-height:0.92;letter-spacing:0.04em;margin:0;">
            <span style="color:#00d68f;">BACK</span><br><span style="color:#ff4757;">TEST</span>
        </div>
        <p style="font-size:0.9rem;color:#3a4558;margin-top:1.2rem;max-width:480px;line-height:1.7;">
            A professional-grade trading platform built for everyone.
            Backtest strategies, study indicators, replay charts,
            and get AI-powered analysis — completely free.
        </p>
    </div>
    """, unsafe_allow_html=True)
    candles=[(28,38,"#ff4757"),(32,44,"#00d68f"),(36,28,"#ff4757"),(40,52,"#00d68f"),(44,60,"#00d68f"),(38,30,"#ff4757"),(48,62,"#00d68f"),(52,70,"#00d68f"),(46,38,"#ff4757"),(56,72,"#00d68f"),(60,78,"#00d68f"),(54,46,"#ff4757"),(62,80,"#00d68f")]
    ch='<div style="display:flex;align-items:flex-end;gap:4px;height:80px;margin:1.5rem 0;">'
    for lo,hi,col in candles:
        bh=max(8,abs(hi-lo)*0.7); wt=abs(hi-lo)*0.15
        ch+=f'<div style="width:14px;height:{bh}px;background:{col};border-radius:2px;position:relative;flex-shrink:0;"><div style="width:2px;height:{wt}px;background:{col};position:absolute;left:50%;transform:translateX(-50%);bottom:100%;opacity:0.6;"></div></div>'
    ch+='</div>'
    st.markdown(ch, unsafe_allow_html=True)
with right:
    st.markdown("""
    <div style="padding-top:2.5rem;">
        <div style="font-family:'IBM Plex Mono',monospace;font-size:0.6rem;color:#3a4558;text-transform:uppercase;letter-spacing:0.18em;margin-bottom:0.8rem;">Platform Stats</div>
        <div style="display:flex;gap:1px;background:#1c2333;border-radius:6px;overflow:hidden;margin-bottom:1px;">
            <div style="flex:1;background:#0d1117;padding:0.8rem;text-align:center;"><div style="font-family:'IBM Plex Mono',monospace;font-size:0.6rem;text-transform:uppercase;color:#3a4558;margin-bottom:0.3rem;">Indicators</div><div style="font-family:'IBM Plex Mono',monospace;font-size:1rem;font-weight:600;color:#00d68f;">9+</div></div>
            <div style="flex:1;background:#0d1117;padding:0.8rem;text-align:center;"><div style="font-family:'IBM Plex Mono',monospace;font-size:0.6rem;text-transform:uppercase;color:#3a4558;margin-bottom:0.3rem;">Strategies</div><div style="font-family:'IBM Plex Mono',monospace;font-size:1rem;font-weight:600;color:#00d68f;">9</div></div>
        </div>
        <div style="display:flex;gap:1px;background:#1c2333;border-radius:6px;overflow:hidden;">
            <div style="flex:1;background:#0d1117;padding:0.8rem;text-align:center;"><div style="font-family:'IBM Plex Mono',monospace;font-size:0.6rem;text-transform:uppercase;color:#3a4558;margin-bottom:0.3rem;">Pages</div><div style="font-family:'IBM Plex Mono',monospace;font-size:1rem;font-weight:600;color:#00d68f;">5</div></div>
            <div style="flex:1;background:#0d1117;padding:0.8rem;text-align:center;"><div style="font-family:'IBM Plex Mono',monospace;font-size:0.6rem;text-transform:uppercase;color:#3a4558;margin-bottom:0.3rem;">Cost</div><div style="font-family:'IBM Plex Mono',monospace;font-size:1rem;font-weight:600;color:#00d68f;">$0</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<div style="font-family:IBM Plex Mono,monospace;font-size:0.6rem;color:#3a4558;text-transform:uppercase;letter-spacing:0.18em;margin:1.2rem 0 0.5rem 0;">Market Status</div>', unsafe_allow_html=True)
    for exchange,status in {"NYSE":"OPEN","NASDAQ":"OPEN","CRYPTO":"24/7"}.items():
        c1,c2=st.columns(2)
        c1.markdown(f'<div style="font-family:IBM Plex Mono,monospace;font-size:0.7rem;color:#3a4558;padding:0.3rem 0;">{exchange}</div>', unsafe_allow_html=True)
        c2.markdown(f'<div style="font-family:IBM Plex Mono,monospace;font-size:0.7rem;color:#00d68f;padding:0.3rem 0;">● {status}</div>', unsafe_allow_html=True)

st.markdown('<div class="price-divider">QUICK START</div>', unsafe_allow_html=True)
q1,q2=st.columns([2,1])
with q1:
    for num,col,title,desc in [("01","#00d68f","BACKTEST","Pick any stock + strategy → Run Backtest → See returns, drawdown, win rate"),("02","#00d68f","INDICATORS","Choose up to 3 indicators → Set your buy/sell conditions → Run test"),("03","#ff4757","REPLAY","Pick a stock and date → Step through candles → Practice your trades"),("04","#00d68f","ANALYSIS","Enter any ticker → Get AI financial breakdown and investment insights"),("05","#00d68f","ASSISTANT","Ask anything — strategy advice, result explanations, trading concepts")]:
        st.markdown(f'<div style="padding:0.8rem 0;border-bottom:1px solid #1c2333;"><div style="font-family:IBM Plex Mono,monospace;font-size:0.72rem;font-weight:700;color:{col};letter-spacing:0.12em;margin-bottom:0.2rem;"><span style="opacity:0.3;margin-right:0.8rem;">{num}</span>{title}</div><div style="font-size:0.8rem;color:#3a4558;">{desc}</div></div>', unsafe_allow_html=True)
with q2:
    st.markdown('<div style="background:#0d1117;border:1px solid #1c2333;border-radius:6px;padding:1.2rem;"><div style="font-family:IBM Plex Mono,monospace;font-size:0.6rem;color:#3a4558;text-transform:uppercase;letter-spacing:0.18em;margin-bottom:1rem;">Indicators Available</div>', unsafe_allow_html=True)
    for name in ["SMA / EMA / WMA","RSI","Stochastic RSI","MACD","Bollinger Bands","SuperTrend","Ichimoku Cloud","VWAP","OBV"]:
        st.markdown(f'<div style="padding:0.35rem 0;border-bottom:1px solid #1c2333;font-family:IBM Plex Mono,monospace;font-size:0.7rem;color:#3a4558;"><span style="color:#00d68f;margin-right:0.6rem;">▸</span>{name}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("""
<div style="margin-top:3rem;padding:1.2rem 0;border-top:1px solid #1c2333;">
    <div style="font-family:'IBM Plex Mono',monospace;font-size:0.65rem;color:#3a4558;">
        <span style="color:#00d68f;">11</span><span style="color:#ff4757;">%</span>
        &nbsp;·&nbsp; Free · Open Source · Educational Use Only · Rishi Gopinath
    </div>
    <div style="font-family:'IBM Plex Mono',monospace;font-size:0.65rem;color:#3a4558;margin-top:0.3rem;">
        ⚠️ Not financial advice. Past performance ≠ future results.
    </div>
</div>
""", unsafe_allow_html=True)
