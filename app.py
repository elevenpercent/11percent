import streamlit as st

st.set_page_config(page_title="11% — Trading Platform", page_icon="💲", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""<style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=IBM+Plex+Mono:wght@300;400;600;700&family=IBM+Plex+Sans:wght@300;400;600&display=swap');
    :root {
        --bg:#07090d; --surface:#0d1117; --border:#1c2333;
        --green:#00d68f; --red:#ff4757; --text:#cdd5e0; --muted:#3a4558;
        --grid:rgba(255,255,255,0.03);
    }
    /* ── Kill ALL Streamlit chrome ── */
    header[data-testid="stHeader"] { display:none!important; }
    [data-testid="stToolbar"] { display:none!important; }
    [data-testid="stDecoration"] { display:none!important; }
    [data-testid="stSidebar"] { display:none!important; }
    [data-testid="stSidebarNav"] { display:none!important; }
    [data-testid="collapsedControl"] { display:none!important; }
    footer { display:none!important; }
    #MainMenu { display:none!important; }
    .stDeployButton { display:none!important; }
    /* ── Layout ── */
    html,body,[data-testid="stAppViewContainer"],[data-testid="stMain"],.main {
        background-color:var(--bg)!important; color:var(--text)!important;
        font-family:'IBM Plex Sans',sans-serif!important;
    }
    [data-testid="stMain"] {
        background-image:linear-gradient(var(--grid) 1px,transparent 1px),linear-gradient(90deg,var(--grid) 1px,transparent 1px)!important;
        background-size:48px 48px!important;
        padding-top:0!important;
    }
    .block-container { padding-top:0!important; padding-left:2rem!important; padding-right:2rem!important; max-width:100%!important; }
    /* ── Navbar ── */
    .nb { background:#07090d; border-bottom:1px solid #1c2333; padding:0; margin:-1rem -2rem 2rem -2rem; display:flex; align-items:stretch; position:sticky; top:0; z-index:1000; }
    .nb-brand { font-family:'Bebas Neue',sans-serif; font-size:1.7rem; letter-spacing:0.1em; color:var(--text); padding:0.6rem 1.6rem; border-right:1px solid #1c2333; display:flex; align-items:center; flex-shrink:0; }
    .nb-brand .g { color:#00d68f; }
    .nb-brand .r { color:#ff4757; }
    .nb-links { display:flex; align-items:stretch; flex:1; }
    .nb-tag { font-family:'IBM Plex Mono',monospace; font-size:0.58rem; color:#3a4558; letter-spacing:0.15em; padding:0.6rem 1.6rem; display:flex; align-items:center; border-left:1px solid #1c2333; }
    /* Style the st.page_link elements inside the navbar */
    .nb-links [data-testid="stPageLink"] { display:flex; align-items:stretch; }
    .nb-links [data-testid="stPageLink-NavLink"] {
        font-family:'IBM Plex Mono',monospace!important;
        font-size:0.69rem!important;
        font-weight:500!important;
        text-transform:uppercase!important;
        letter-spacing:0.12em!important;
        color:#3a4558!important;
        text-decoration:none!important;
        padding:0 1.1rem!important;
        border-radius:0!important;
        border:none!important;
        border-bottom:2px solid transparent!important;
        background:transparent!important;
        display:flex!important;
        align-items:center!important;
        height:100%!important;
        transition:color 0.15s, border-color 0.15s!important;
        white-space:nowrap!important;
    }
    .nb-links [data-testid="stPageLink-NavLink"]:hover {
        color:#cdd5e0!important;
        background:transparent!important;
        text-decoration:none!important;
        border-bottom:2px solid #3a4558!important;
    }
    .nb-links [data-testid="stPageLink-NavLink"][aria-current="page"] {
        color:#00d68f!important;
        border-bottom:2px solid #00d68f!important;
    }
    /* ── Typography ── */
    h1 { font-family:'Bebas Neue',sans-serif!important; letter-spacing:0.06em; color:var(--text)!important; }
    h2 { font-family:'Bebas Neue',sans-serif!important; }
    h3 { font-family:'IBM Plex Mono',monospace!important; font-size:0.75rem!important; color:var(--green)!important; text-transform:uppercase; letter-spacing:0.15em; }
    /* ── Inputs ── */
    .stTextInput input, .stNumberInput input {
        background:#0d1117!important; border:1px solid #1c2333!important;
        color:#cdd5e0!important; font-family:'IBM Plex Mono',monospace!important;
        font-size:0.85rem!important; border-radius:3px!important;
    }
    .stTextInput input:focus, .stNumberInput input:focus { border-color:#00d68f!important; box-shadow:none!important; }
    div[data-baseweb="select"]>div { background:#0d1117!important; border:1px solid #1c2333!important; color:#cdd5e0!important; font-family:'IBM Plex Mono',monospace!important; border-radius:3px!important; }
    .stDateInput input { background:#0d1117!important; border:1px solid #1c2333!important; color:#cdd5e0!important; font-family:'IBM Plex Mono',monospace!important; border-radius:3px!important; }
    label { font-family:'IBM Plex Mono',monospace!important; font-size:0.68rem!important; color:#3a4558!important; text-transform:uppercase!important; letter-spacing:0.1em!important; }
    /* ── Buttons ── */
    .stButton>button { background:transparent!important; color:#00d68f!important; border:1px solid #00d68f!important; border-radius:3px!important; font-family:'IBM Plex Mono',monospace!important; font-weight:600!important; font-size:0.78rem!important; letter-spacing:0.1em!important; padding:0.45rem 1.4rem!important; transition:all 0.15s!important; text-transform:uppercase!important; }
    .stButton>button:hover { background:#00d68f!important; color:#000!important; }
    /* ── Cards ── */
    .metric-card { background:#0d1117; border:1px solid #1c2333; padding:1rem; border-radius:4px; text-align:center; }
    .metric-val { font-family:'IBM Plex Mono',monospace; font-size:1.1rem; font-weight:700; }
    .metric-lbl { font-family:'IBM Plex Mono',monospace; font-size:0.55rem; color:#3a4558; text-transform:uppercase; margin-top:0.3rem; }
    .pos{color:#00d68f;} .neg{color:#ff4757;} .neu{color:#cdd5e0;}
    /* ── Config panel ── */
    .config-panel { background:#0d1117; border:1px solid #1c2333; border-radius:6px; padding:1.4rem 1.4rem 0.4rem 1.4rem; margin-bottom:1.5rem; }
    /* ── Dividers ── */
    .price-divider { display:flex; align-items:center; gap:1rem; margin:1.5rem 0 1rem 0; font-family:'IBM Plex Mono',monospace; font-size:0.62rem; color:#3a4558; letter-spacing:0.12em; }
    .price-divider::before,.price-divider::after { content:''; flex:1; height:1px; background:#1c2333; }
    /* ── Page header ── */
    .page-header { padding:1.5rem 0 1rem 0; border-bottom:1px solid #1c2333; margin-bottom:1.5rem; }
    .page-header h1 { font-size:2.8rem!important; margin:0!important; }
    .page-header p { color:#3a4558; font-size:0.85rem; margin:0.3rem 0 0 0; }
    /* ── Boxes ── */
    .info-box { background:#071a0f; border:1px solid #0d3320; border-radius:4px; padding:0.8rem 1rem; font-size:0.82rem; color:#00d68f; font-family:'IBM Plex Mono',monospace; }
    .warn-box { background:#1a0a08; border:1px solid #3a1008; border-radius:4px; padding:0.8rem 1rem; font-size:0.82rem; color:#ff4757; font-family:'IBM Plex Mono',monospace; }
    /* ── Chat ── */
    .chat-user { background:#0d1117; border:1px solid #1c2333; border-radius:10px 10px 3px 10px; padding:1rem 1.2rem; margin:0.6rem 0; }
    .chat-ai { background:#071a0f; border:1px solid #0d3320; border-radius:10px 10px 10px 3px; padding:1rem 1.2rem; margin:0.6rem 0; }
    .chat-lbl { font-family:'IBM Plex Mono',monospace; font-size:0.65rem; text-transform:uppercase; letter-spacing:0.12em; color:#3a4558; margin-bottom:0.4rem; }
    /* ── Ticker ── */
    .ticker-wrap { overflow:hidden; background:#0d1117; border-bottom:1px solid #1c2333; padding:0.4rem 0; margin:-2rem -2rem 2rem -2rem; }
    .ticker-tape { display:inline-flex; animation:ticker 35s linear infinite; white-space:nowrap; }
    .ticker-item { font-family:'IBM Plex Mono',monospace; font-size:0.68rem; padding:0 1.5rem; letter-spacing:0.05em; }
    .t-up{color:#00d68f;} .t-dn{color:#ff4757;} .t-sym{color:#cdd5e0;margin-right:0.4rem;}
    @keyframes ticker{0%{transform:translateX(0)}100%{transform:translateX(-50%)}}
    /* ── Misc ── */
    ::-webkit-scrollbar{width:4px;} ::-webkit-scrollbar-track{background:#07090d;} ::-webkit-scrollbar-thumb{background:#263045;border-radius:2px;}
    hr{border-color:#1c2333!important;}
    [data-testid="stExpander"]{background:#0d1117!important;border:1px solid #1c2333!important;border-radius:4px!important;}
</style>""", unsafe_allow_html=True)
st.markdown('<div class="nb"><div class="nb-brand"><span class="g">11</span><span class="r">%</span></div><div class="nb-links">', unsafe_allow_html=True)
_nav = st.columns([1,1,1,1,1,1])
with _nav[0]: st.page_link("app.py",                    label="Home")
with _nav[1]: st.page_link("pages/1_Backtest.py",       label="Backtest")
with _nav[2]: st.page_link("pages/2_Indicator_Test.py", label="Indicators")
with _nav[3]: st.page_link("pages/3_Replay.py",         label="Replay")
with _nav[4]: st.page_link("pages/4_Analysis.py",       label="Analysis")
with _nav[5]: st.page_link("pages/5_Assistant.py",      label="Assistant")
st.markdown('</div><div class="nb-tag">FREE · OPEN SOURCE</div></div>', unsafe_allow_html=True)

TICKERS = ["AAPL","TSLA","SPY","NVDA","MSFT","AMZN","BTC-USD","META","GOOGL","AMD"]
@st.cache_data(ttl=3600)
def get_tape(tickers):
    import yfinance as yf
    out=[]
    for s in tickers:
        try:
            h=yf.Ticker(s).history(period="2d")
            if len(h)>=2:
                p=float(h["Close"].iloc[-2]); c=float(h["Close"].iloc[-1])
                chg=((c-p)/p)*100; up=chg>=0
                out.append((s,f"{c:,.2f}",f"{chg:+.2f}%","▲" if up else "▼","t-up" if up else "t-dn"))
        except: pass
    return out

tape=get_tape(tuple(TICKERS))
if tape:
    html="".join(f'<span class="ticker-item"><span class="t-sym">{s}</span><span class="{c}">{p} {a} {ch}</span></span>' for s,p,ch,a,c in tape)*2
    st.markdown(f'<div class="ticker-wrap"><div class="ticker-tape">{html}</div></div>', unsafe_allow_html=True)

left, right = st.columns([3,2])
with left:
    st.markdown("""
    <div style="padding:2.5rem 0 1.5rem 0;">
        <div style="font-family:'IBM Plex Mono',monospace;font-size:0.68rem;color:#00d68f;text-transform:uppercase;letter-spacing:0.25em;margin-bottom:1rem;">Free · Open Source · Educational</div>
        <div style="font-family:'Bebas Neue',sans-serif;font-size:5.5rem;line-height:0.9;letter-spacing:0.03em;">
            <span style="color:#00d68f;">BACK</span><br><span style="color:#ff4757;">TEST</span>
        </div>
        <p style="font-size:0.88rem;color:#3a4558;margin-top:1.2rem;max-width:460px;line-height:1.75;">A professional-grade trading platform built for everyone. Backtest strategies, study indicators, replay charts, and get AI-powered analysis — completely free.</p>
    </div>
    """, unsafe_allow_html=True)
    candles=[(28,38,"#ff4757"),(32,44,"#00d68f"),(36,28,"#ff4757"),(40,52,"#00d68f"),(44,60,"#00d68f"),(38,30,"#ff4757"),(48,62,"#00d68f"),(52,70,"#00d68f"),(46,38,"#ff4757"),(56,72,"#00d68f"),(60,78,"#00d68f"),(54,46,"#ff4757"),(62,80,"#00d68f")]
    ch='<div style="display:flex;align-items:flex-end;gap:4px;height:80px;margin:1rem 0 2rem 0;">'
    for lo,hi,col in candles:
        bh=max(8,abs(hi-lo)*0.7); wt=abs(hi-lo)*0.15
        ch+=f'<div style="width:14px;height:{bh}px;background:{col};border-radius:2px;position:relative;"><div style="width:2px;height:{wt}px;background:{col};position:absolute;left:50%;transform:translateX(-50%);bottom:100%;opacity:0.5;"></div></div>'
    st.markdown(ch+"</div>", unsafe_allow_html=True)
with right:
    st.markdown("""
    <div style="padding:2.5rem 0 1rem 0;">
        <div style="font-family:'IBM Plex Mono',monospace;font-size:0.58rem;color:#3a4558;text-transform:uppercase;letter-spacing:0.18em;margin-bottom:0.6rem;">Platform Stats</div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:1px;background:#1c2333;border-radius:4px;overflow:hidden;">
            <div style="background:#0d1117;padding:1rem;text-align:center;"><div style="font-family:'IBM Plex Mono',monospace;font-size:0.58rem;color:#3a4558;text-transform:uppercase;margin-bottom:0.4rem;">Indicators</div><div style="font-family:'IBM Plex Mono',monospace;font-size:1.4rem;font-weight:700;color:#00d68f;">9+</div></div>
            <div style="background:#0d1117;padding:1rem;text-align:center;"><div style="font-family:'IBM Plex Mono',monospace;font-size:0.58rem;color:#3a4558;text-transform:uppercase;margin-bottom:0.4rem;">Strategies</div><div style="font-family:'IBM Plex Mono',monospace;font-size:1.4rem;font-weight:700;color:#00d68f;">9</div></div>
            <div style="background:#0d1117;padding:1rem;text-align:center;"><div style="font-family:'IBM Plex Mono',monospace;font-size:0.58rem;color:#3a4558;text-transform:uppercase;margin-bottom:0.4rem;">Pages</div><div style="font-family:'IBM Plex Mono',monospace;font-size:1.4rem;font-weight:700;color:#00d68f;">5</div></div>
            <div style="background:#0d1117;padding:1rem;text-align:center;"><div style="font-family:'IBM Plex Mono',monospace;font-size:0.58rem;color:#3a4558;text-transform:uppercase;margin-bottom:0.4rem;">Cost</div><div style="font-family:'IBM Plex Mono',monospace;font-size:1.4rem;font-weight:700;color:#00d68f;">$0</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    for name, val in [("NYSE","OPEN"),("NASDAQ","OPEN"),("CRYPTO","24/7")]:
        c1,c2=st.columns(2)
        c1.markdown(f'<div style="font-family:IBM Plex Mono,monospace;font-size:0.7rem;color:#3a4558;padding:0.25rem 0;">{name}</div>', unsafe_allow_html=True)
        c2.markdown(f'<div style="font-family:IBM Plex Mono,monospace;font-size:0.7rem;color:#00d68f;padding:0.25rem 0;">● {val}</div>', unsafe_allow_html=True)

st.markdown('<div class="price-divider">QUICK START</div>', unsafe_allow_html=True)
q1,q2=st.columns([2,1])
with q1:
    steps=[("01","#00d68f","BACKTEST","Pick any stock and strategy, run the backtest, see returns, drawdown and win rate."),("02","#00d68f","INDICATORS","Choose up to 3 indicators, set your buy/sell conditions, run the test."),("03","#ff4757","REPLAY","Pick a stock and date range, step through historical candles, practice trading."),("04","#00d68f","ANALYSIS","Enter any ticker and get an AI-powered fundamental breakdown."),("05","#00d68f","ASSISTANT","Ask anything — strategies, results explained, concepts, personalised advice.")]
    for num,col,title,desc in steps:
        st.markdown(f'<div style="padding:0.8rem 0;border-bottom:1px solid #1c2333;"><span style="font-family:IBM Plex Mono,monospace;font-size:0.62rem;color:#3a4558;margin-right:0.8rem;">{num}</span><span style="font-family:IBM Plex Mono,monospace;font-size:0.72rem;font-weight:700;color:{col};letter-spacing:0.1em;">{title}</span><div style="font-size:0.8rem;color:#3a4558;margin-top:0.2rem;">{desc}</div></div>', unsafe_allow_html=True)
with q2:
    ind_names=["SMA · EMA · WMA","RSI","Stochastic RSI","MACD","Bollinger Bands","SuperTrend","Ichimoku Cloud","VWAP","OBV"]
    st.markdown('<div style="background:#0d1117;border:1px solid #1c2333;border-radius:4px;padding:1.2rem;">', unsafe_allow_html=True)
    st.markdown('<div style="font-family:IBM Plex Mono,monospace;font-size:0.58rem;color:#3a4558;text-transform:uppercase;letter-spacing:0.18em;margin-bottom:0.8rem;">Indicators</div>', unsafe_allow_html=True)
    for name in ind_names:
        st.markdown(f'<div style="padding:0.3rem 0;border-bottom:1px solid #1c2333;font-family:IBM Plex Mono,monospace;font-size:0.72rem;color:#3a4558;"><span style="color:#00d68f;margin-right:0.5rem;">—</span>{name}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div style="margin-top:2.5rem;padding-top:1rem;border-top:1px solid #1c2333;font-family:IBM Plex Mono,monospace;font-size:0.62rem;color:#3a4558;"><span style="color:#00d68f;">11</span><span style="color:#ff4757;">%</span> · Free · Open Source · Educational Use Only · Not financial advice.</div>', unsafe_allow_html=True)
