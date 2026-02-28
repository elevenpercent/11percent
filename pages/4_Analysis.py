import streamlit as st
import google.generativeai as genai
import sys, os
from datetime import date, timedelta
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.data import get_stock_data, get_ticker_info, get_news

st.set_page_config(page_title="Analysis | 11%", page_icon="🧠", layout="wide", initial_sidebar_state="collapsed")
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

try:    api_key=st.secrets["GEMINI_API_KEY"]
except: api_key=os.getenv("GEMINI_API_KEY","")
if api_key: genai.configure(api_key=api_key); model=genai.GenerativeModel("gemini-2.5-flash")
else: model=None

st.markdown('''<div class="page-header"><h1>AI Analysis</h1><p>Fundamentals, financials, and AI-powered insights for any stock.</p></div>''', unsafe_allow_html=True)

if not api_key:
    st.markdown('<div class="warn-box">No Gemini API key found. Add GEMINI_API_KEY to Streamlit Secrets.</div>', unsafe_allow_html=True)

st.markdown('<div class="config-panel">', unsafe_allow_html=True)
ac1,ac2,ac3 = st.columns([1.2,2,2])
with ac1: ticker = st.text_input("Ticker Symbol", value="AAPL").upper().strip()
with ac2: focus_options = st.multiselect("AI Focus Areas", ["Overall investment thesis","Financial health & fundamentals","Risk assessment","Growth potential","Valuation","Competitor comparison","Recent news impact"], default=["Overall investment thesis","Risk assessment"])
with ac3: user_context = st.text_input("Your situation (optional)", placeholder="e.g. Long-term investor, moderate risk")
analyze_btn = st.button("Analyse")
st.markdown('</div>', unsafe_allow_html=True)

def fmt(val,t="num"):
    if val is None: return "N/A"
    if t=="pct": return f"{val*100:.1f}%"
    if t=="ratio": return f"{val:.2f}x"
    if t=="large":
        if val>=1e12: return f"${val/1e12:.2f}T"
        if val>=1e9: return f"${val/1e9:.2f}B"
        if val>=1e6: return f"${val/1e6:.2f}M"
        return f"${val:,.0f}"
    return f"{val:.2f}"

if analyze_btn:
    with st.spinner(f"Loading {ticker}..."):
        info=get_ticker_info(ticker)
        df=get_stock_data(ticker,str(date.today()-timedelta(days=365)),str(date.today()))
        news=get_news(ticker)
    if not info.get("name"): st.error("Could not find data for this ticker."); st.stop()
    st.markdown(f'<div style="margin-bottom:1.2rem;"><div style="font-family:Bebas Neue,sans-serif;font-size:2rem;letter-spacing:0.05em;">{info.get("name",ticker)}</div><div style="font-family:IBM Plex Mono,monospace;font-size:0.7rem;color:#3a4558;">{ticker} · {info.get("sector","N/A")} · {info.get("industry","N/A")}</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="price-divider">KEY METRICS</div>', unsafe_allow_html=True)
    cols=st.columns(4)
    metrics=[("Market Cap",fmt(info.get("market_cap"),"large"),"neu"),("P/E Ratio",fmt(info.get("pe_ratio"),"ratio"),"neu"),("Fwd P/E",fmt(info.get("fwd_pe"),"ratio"),"neu"),("EPS",fmt(info.get("eps")),"neu"),("Revenue",fmt(info.get("revenue"),"large"),"neu"),("Profit Margin",fmt(info.get("profit_margin"),"pct"),"pos" if (info.get("profit_margin") or 0)>0 else "neg"),("ROE",fmt(info.get("roe"),"pct"),"pos" if (info.get("roe") or 0)>0 else "neg"),("Debt/Equity",fmt(info.get("debt_equity"),"ratio"),"pos" if (info.get("debt_equity") or 999)<100 else "neg")]
    for i,(lbl,val,cls) in enumerate(metrics):
        cols[i%4].markdown(f'<div class="metric-card" style="margin-bottom:0.8rem;"><div class="metric-val {cls}">{val}</div><div class="metric-lbl">{lbl}</div></div>', unsafe_allow_html=True)
    c5,c6,c7,c8=st.columns(4)
    for col,lbl,val in [(c5,"52W High",f"${info.get('52w_high',0):.2f}" if info.get("52w_high") else "N/A"),(c6,"52W Low",f"${info.get('52w_low',0):.2f}" if info.get("52w_low") else "N/A"),(c7,"Beta",fmt(info.get("beta"))),(c8,"Dividend",fmt(info.get("dividend"),"pct") if info.get("dividend") else "None")]:
        col.markdown(f'<div class="metric-card"><div class="metric-val neu">{val}</div><div class="metric-lbl">{lbl}</div></div>', unsafe_allow_html=True)
    if not df.empty:
        st.markdown('<div class="price-divider">1-YEAR PRICE</div>', unsafe_allow_html=True)
        import plotly.graph_objects as go
        fig=go.Figure()
        fig.add_trace(go.Scatter(x=df.index,y=df["Close"],mode="lines",line=dict(color="#00d68f",width=2),fill="tozeroy",fillcolor="rgba(0,214,143,0.04)"))
        fig.update_layout(paper_bgcolor="#07090d",plot_bgcolor="#07090d",font=dict(family="IBM Plex Mono",color="#cdd5e0",size=11),xaxis=dict(gridcolor="#1c2333",linecolor="#1c2333"),yaxis=dict(gridcolor="#1c2333",linecolor="#1c2333"),margin=dict(l=10,r=10,t=20,b=10),height=260,xaxis_rangeslider_visible=False,showlegend=False)
        st.plotly_chart(fig,use_container_width=True)
    if info.get("summary"):
        with st.expander("Business Summary"):
            st.markdown(f'<p style="font-size:0.85rem;line-height:1.75;color:#8892a4;">{info["summary"]}</p>', unsafe_allow_html=True)
    if news:
        st.markdown('<div class="price-divider">RECENT NEWS</div>', unsafe_allow_html=True)
        for item in news[:5]:
            st.markdown(f'<div style="padding:0.55rem 0;border-bottom:1px solid #1c2333;font-size:0.83rem;"><a href="{item.get('link','#')}" target="_blank" style="color:#cdd5e0;text-decoration:none;">{item.get("title","")}</a><span style="font-family:IBM Plex Mono,monospace;font-size:0.62rem;color:#3a4558;margin-left:0.8rem;">{item.get("publisher","")}</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="price-divider">AI ANALYSIS</div>', unsafe_allow_html=True)
    if not model:
        st.markdown('<div class="warn-box">Add your Gemini API key to enable AI analysis.</div>', unsafe_allow_html=True)
    else:
        last_bt=st.session_state.get("last_backtest"); bt_ctx=""
        if last_bt and last_bt.get("ticker")==ticker:
            mm=last_bt["metrics"]
            bt_ctx=f"Backtest on this stock: {last_bt['strategy']} → Return {mm['total_return']:+.2f}%, Drawdown {mm['max_drawdown']:.2f}%, Win Rate {mm['win_rate']:.0f}%"
        prompt=f"""Financial analysis AI on 11% platform. Sharp, honest, educational. NOT a financial advisor — include disclaimer.
STOCK: {ticker} — {info.get("name","")} | SECTOR: {info.get("sector","N/A")}
METRICS: Market Cap {fmt(info.get("market_cap"),"large")} | P/E {fmt(info.get("pe_ratio"),"ratio")} | Revenue {fmt(info.get("revenue"),"large")} | Margin {fmt(info.get("profit_margin"),"pct")} | ROE {fmt(info.get("roe"),"pct")} | Beta {fmt(info.get("beta"))}
{bt_ctx}
USER: {user_context or "Not provided."} | FOCUS: {", ".join(focus_options)}
Be honest about risks. End with a brief disclaimer."""
        with st.spinner("Analysing..."):
            try:
                r=model.generate_content(prompt)
                st.markdown(f'<div class="chat-ai"><div class="chat-lbl" style="color:#00d68f;">AI Analysis — {ticker}</div>{r.text.replace(chr(10),"<br>")}</div>', unsafe_allow_html=True)
                st.session_state["last_analysis"]={"ticker":ticker,"analysis":r.text,"info":info}
            except Exception as e: st.error(f"Gemini error: {e}")
else:
    st.markdown('<div class="info-box">Enter a ticker above and click Analyse to get started.</div>', unsafe_allow_html=True)
