import streamlit as st
import google.generativeai as genai
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from datetime import date, timedelta
from utils.data import get_stock_data, get_ticker_info, get_news

st.set_page_config(page_title="Analysis | 11%", page_icon="🧠", layout="wide")
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
        background-size:48px 48px!important;
    }
    [data-testid="stSidebar"] { background-color:var(--surface)!important; border-right:1px solid var(--border)!important; }
    [data-testid="stSidebarNav"] { display:none!important; }
    h1 { font-family:'Bebas Neue',sans-serif!important; letter-spacing:0.06em; color:var(--text)!important; }
    h2 { font-family:'Bebas Neue',sans-serif!important; letter-spacing:0.05em; color:var(--text)!important; }
    h3 { font-family:'IBM Plex Mono',monospace!important; font-size:0.75rem!important; color:var(--green)!important; text-transform:uppercase; letter-spacing:0.15em; }
    .ticker-wrap { width:100%; overflow:hidden; background:var(--surface); border-top:1px solid var(--border); border-bottom:1px solid var(--border); padding:0.45rem 0; margin-bottom:2rem; }
    .ticker-tape { display:inline-flex; animation:ticker 30s linear infinite; white-space:nowrap; }
    .ticker-item { font-family:'IBM Plex Mono',monospace; font-size:0.72rem; padding:0 2rem; letter-spacing:0.06em; }
    .ticker-up { color:var(--green); }
    .ticker-down { color:var(--red); }
    .ticker-sym { color:var(--text); margin-right:0.4rem; }
    @keyframes ticker { 0%{transform:translateX(0)} 100%{transform:translateX(-50%)} }
    .hero { padding:2.5rem 0 2rem 0; }
    .hero-eyebrow { font-family:'IBM Plex Mono',monospace; font-size:0.7rem; color:var(--green); text-transform:uppercase; letter-spacing:0.25em; margin-bottom:0.8rem; }
    .hero-title { font-family:'Bebas Neue',sans-serif; font-size:5.5rem; line-height:0.92; letter-spacing:0.04em; margin:0; }
    .hero-title .green { color:var(--green); }
    .hero-title .red   { color:var(--red); }
    .hero-subtitle { font-size:0.9rem; color:var(--muted); margin-top:1.2rem; max-width:480px; line-height:1.7; }
    .chart-deco { display:flex; align-items:flex-end; gap:4px; height:80px; margin:1.5rem 0; }
    .candle-body { width:14px; border-radius:2px; position:relative; flex-shrink:0; }
    .candle-wick { width:2px; background:inherit; position:absolute; left:50%; transform:translateX(-50%); border-radius:1px; opacity:0.6; }
    .candle-wick-top { bottom:100%; }
    .candle-wick-bottom { top:100%; }
    .ohlc-row { display:flex; gap:1px; margin:0.8rem 0; background:var(--border); border-radius:6px; overflow:hidden; }
    .ohlc-box { flex:1; background:var(--surface); padding:0.8rem; text-align:center; }
    .ohlc-label { font-family:'IBM Plex Mono',monospace; font-size:0.6rem; text-transform:uppercase; letter-spacing:0.15em; color:var(--muted); margin-bottom:0.3rem; }
    .ohlc-value { font-family:'IBM Plex Mono',monospace; font-size:1rem; font-weight:600; }
    .price-divider { display:flex; align-items:center; gap:1rem; margin:1.5rem 0; font-family:'IBM Plex Mono',monospace; font-size:0.65rem; color:var(--muted); }
    .price-divider::before,.price-divider::after { content:''; flex:1; height:1px; background:var(--border); }
    ::-webkit-scrollbar { width:4px; }
    ::-webkit-scrollbar-track { background:var(--bg); }
    ::-webkit-scrollbar-thumb { background:var(--border2); border-radius:2px; }
    .stButton>button { background:transparent!important; color:var(--green)!important; border:1px solid var(--green)!important; border-radius:3px!important; font-family:'IBM Plex Mono',monospace!important; font-weight:600!important; font-size:0.78rem!important; letter-spacing:0.1em!important; padding:0.45rem 1.4rem!important; transition:all 0.15s!important; text-transform:uppercase!important; }
    .stButton>button:hover { background:var(--green)!important; color:#000!important; }
    hr { border-color:var(--border)!important; }
    [data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"] { font-family:'IBM Plex Mono',monospace!important; font-size:0.72rem!important; text-transform:uppercase!important; letter-spacing:0.1em!important; color:#3a4558!important; padding:0.45rem 0.3rem!important; border-bottom:1px solid #1c2333!important; border-radius:0!important; display:block!important; }
    [data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"]:hover { color:#00d68f!important; background:transparent!important; }
    [data-testid="stSidebar"] a[aria-current="page"] { color:#00d68f!important; background:transparent!important; }

    .metric-card { background:#0d1117; border:1px solid #1c2333; padding:1rem; border-radius:4px; text-align:center; }
    .metric-val { font-family:'IBM Plex Mono',monospace; font-size:1.1rem; font-weight:700; }
    .metric-lbl { font-family:'IBM Plex Mono',monospace; font-size:0.55rem; color:#3a4558; text-transform:uppercase; margin-top:0.3rem; }
    .pos { color:#00d68f; } .neg { color:#ff4757; } .neu { color:#cdd5e0; }
    .page-header { border-left:3px solid #00d68f; padding-left:1rem; margin-bottom:1.5rem; }
    .page-header p { color:#3a4558; font-size:0.88rem; margin-top:0.2rem; }
    .info-box { background:#071a0f; border:1px solid #0d3320; border-radius:6px; padding:0.8rem 1rem; font-size:0.82rem; color:#00d68f; font-family:'IBM Plex Mono',monospace; }
    .warn-box { background:#1a0a08; border:1px solid #3a1008; border-radius:6px; padding:0.8rem 1rem; font-size:0.82rem; color:#ff4757; font-family:'IBM Plex Mono',monospace; }
    .chat-user { background:#0d1117; border:1px solid #1c2333; border-radius:10px 10px 3px 10px; padding:1rem 1.2rem; margin:0.6rem 0; }
    .chat-ai { background:#071a0f; border:1px solid #0d3320; border-radius:10px 10px 10px 3px; padding:1rem 1.2rem; margin:0.6rem 0; }
    .chat-lbl { font-family:'IBM Plex Mono',monospace; font-size:0.65rem; text-transform:uppercase; letter-spacing:0.12em; color:#3a4558; margin-bottom:0.4rem; }
</style>
""", unsafe_allow_html=True)

try:    api_key = st.secrets["GEMINI_API_KEY"]
except: api_key = os.getenv("GEMINI_API_KEY", "")
if api_key: genai.configure(api_key=api_key); model = genai.GenerativeModel("gemini-2.5-flash")
else:        model = None

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("assets/logo.png", width=120)
    st.markdown('<div style="padding-top:1rem;padding-bottom:0.5rem;border-top:1px solid #1c2333;"><div style="font-family:IBM Plex Mono,monospace;font-size:0.6rem;color:#3a4558;text-transform:uppercase;letter-spacing:0.18em;margin-bottom:0.5rem;">Navigation</div></div>', unsafe_allow_html=True)
    st.page_link("app.py",                       label="🏠  Home")
    st.page_link("pages/1_Backtest.py",          label="🔬  Backtest")
    st.page_link("pages/2_Indicator_Test.py",    label="📊  Indicator Test")
    st.page_link("pages/3_Replay.py",            label="▶   Replay")
    st.page_link("pages/4_Analysis.py",          label="🧠  Analysis")
    st.page_link("pages/5_Assistant.py",         label="💬  Assistant")
    st.markdown('<div style="position:absolute;bottom:1.5rem;left:1rem;right:1rem;text-align:center;font-family:IBM Plex Mono,monospace;font-size:0.6rem;color:#3a4558;text-transform:uppercase;letter-spacing:0.1em;">Free · Open Source</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown('<div style="font-family:IBM Plex Mono,monospace;font-size:0.6rem;color:#3a4558;text-transform:uppercase;letter-spacing:0.18em;margin-bottom:0.5rem;">Analysis Setup</div>', unsafe_allow_html=True)
    ticker = st.text_input("Ticker Symbol", value="AAPL").upper().strip()
    focus_options = st.multiselect("AI Focus", ["Overall investment thesis","Financial health & fundamentals","Risk assessment","Growth potential","Valuation (is it cheap or expensive?)","Competitor comparison","Recent news impact"], default=["Overall investment thesis","Risk assessment"])
    user_context  = st.text_area("Your situation (optional)", placeholder="e.g. Long-term investor, moderate risk.", height=80)
    analyze_btn   = st.button("🧠  ANALYSE", use_container_width=True)

st.markdown('''<div class="page-header"><h1>AI ANALYSIS</h1><p>Fundamentals, financials, and AI-powered insights for any stock.</p></div>''', unsafe_allow_html=True)

if not api_key:
    st.markdown('<div class="warn-box">⚠️ No Gemini API key found. Add GEMINI_API_KEY to Streamlit Secrets.</div>', unsafe_allow_html=True)

def fmt(val, t="num"):
    if val is None: return "N/A"
    if t=="pct": return f"{val*100:.1f}%"
    if t=="ratio": return f"{val:.2f}x"
    if t=="large":
        if val>=1e12: return f"${val/1e12:.2f}T"
        if val>=1e9:  return f"${val/1e9:.2f}B"
        if val>=1e6:  return f"${val/1e6:.2f}M"
        return f"${val:,.0f}"
    return f"{val:.2f}"

if analyze_btn:
    with st.spinner(f"Loading {ticker}..."):
        info = get_ticker_info(ticker)
        df   = get_stock_data(ticker, str(date.today()-timedelta(days=365)), str(date.today()))
        news = get_news(ticker)
    if not info.get("name"): st.error("Could not find data for this ticker."); st.stop()

    st.markdown(f'''<div style="margin-bottom:1.5rem;"><div style="font-family:Bebas Neue,sans-serif;font-size:2.2rem;letter-spacing:0.05em;">{info.get("name",ticker)}</div><div style="font-family:IBM Plex Mono,monospace;font-size:0.72rem;color:#3a4558;margin-top:0.2rem;">{ticker} &nbsp;·&nbsp; {info.get("sector","N/A")} &nbsp;·&nbsp; {info.get("industry","N/A")}</div></div>''', unsafe_allow_html=True)

    st.markdown('<div class="price-divider">KEY METRICS</div>', unsafe_allow_html=True)
    cols = st.columns(4)
    metrics = [
        ("Market Cap",fmt(info.get("market_cap"),"large"),"neu"),("P/E Ratio",fmt(info.get("pe_ratio"),"ratio"),"neu"),
        ("Fwd P/E",fmt(info.get("fwd_pe"),"ratio"),"neu"),("EPS",fmt(info.get("eps")),"neu"),
        ("Revenue",fmt(info.get("revenue"),"large"),"neu"),("Profit Margin",fmt(info.get("profit_margin"),"pct"),"pos" if (info.get("profit_margin") or 0)>0 else "neg"),
        ("ROE",fmt(info.get("roe"),"pct"),"pos" if (info.get("roe") or 0)>0 else "neg"),("Debt/Equity",fmt(info.get("debt_equity"),"ratio"),"pos" if (info.get("debt_equity") or 999)<100 else "neg"),
    ]
    for i,(lbl,val,cls) in enumerate(metrics):
        cols[i%4].markdown(f'<div class="metric-card" style="margin-bottom:0.8rem;"><div class="metric-val {cls}">{val}</div><div class="metric-lbl">{lbl}</div></div>', unsafe_allow_html=True)
    c5,c6,c7,c8 = st.columns(4)
    for col,lbl,val in [(c5,"52W High",f"${info.get('52w_high',0):.2f}" if info.get("52w_high") else "N/A"),(c6,"52W Low",f"${info.get('52w_low',0):.2f}" if info.get("52w_low") else "N/A"),(c7,"Beta",fmt(info.get("beta"))),(c8,"Dividend",fmt(info.get("dividend"),"pct") if info.get("dividend") else "None")]:
        col.markdown(f'<div class="metric-card"><div class="metric-val neu">{val}</div><div class="metric-lbl">{lbl}</div></div>', unsafe_allow_html=True)

    if not df.empty:
        st.markdown('<div class="price-divider">1-YEAR PRICE</div>', unsafe_allow_html=True)
        import plotly.graph_objects as go
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.index, y=df["Close"], mode="lines", name="Close", line=dict(color="#00d68f",width=2), fill="tozeroy", fillcolor="rgba(0,214,143,0.04)"))
        fig.update_layout(paper_bgcolor="#07090d", plot_bgcolor="#07090d", font=dict(family="IBM Plex Mono",color="#cdd5e0",size=11), xaxis=dict(gridcolor="#1c2333",linecolor="#1c2333"), yaxis=dict(gridcolor="#1c2333",linecolor="#1c2333"), margin=dict(l=10,r=10,t=20,b=10), height=280, xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

    if info.get("summary"):
        with st.expander("📄 BUSINESS SUMMARY"):
            st.markdown(f'<p style="font-size:0.88rem;line-height:1.7;color:#8892a4;">{info["summary"]}</p>', unsafe_allow_html=True)

    if news:
        st.markdown('<div class="price-divider">RECENT NEWS</div>', unsafe_allow_html=True)
        for item in news[:5]:
            st.markdown(f'<div style="padding:0.6rem 0;border-bottom:1px solid #1c2333;font-size:0.85rem;"><a href="{item.get("link","#")}" target="_blank" style="color:#cdd5e0;text-decoration:none;">{item.get("title","")}</a><span style="font-family:IBM Plex Mono,monospace;font-size:0.65rem;color:#3a4558;margin-left:0.8rem;">{item.get("publisher","")}</span></div>', unsafe_allow_html=True)

    st.markdown('<div class="price-divider">AI ANALYSIS</div>', unsafe_allow_html=True)
    if not model:
        st.markdown('<div class="warn-box">⚠️ Add your Gemini API key to enable AI analysis.</div>', unsafe_allow_html=True)
    else:
        last_bt = st.session_state.get("last_backtest")
        bt_ctx  = ""
        if last_bt and last_bt.get("ticker")==ticker:
            mm=last_bt["metrics"]
            bt_ctx = f"Backtest: {last_bt['strategy']} → Return {mm['total_return']:+.2f}%, Drawdown {mm['max_drawdown']:.2f}%, Win Rate {mm['win_rate']:.0f}%"
        prompt = f"""You are a financial analysis AI on 11%, a free trading education platform.
Provide sharp, honest, educational analysis. You are NOT a financial advisor — include a disclaimer.
STOCK: {ticker} — {info.get("name","")} | SECTOR: {info.get("sector","N/A")}
METRICS: Market Cap {fmt(info.get("market_cap"),"large")} | P/E {fmt(info.get("pe_ratio"),"ratio")} | Fwd P/E {fmt(info.get("fwd_pe"),"ratio")} | Revenue {fmt(info.get("revenue"),"large")} | Profit Margin {fmt(info.get("profit_margin"),"pct")} | ROE {fmt(info.get("roe"),"pct")} | Beta {fmt(info.get("beta"))}
{bt_ctx}
USER CONTEXT: {user_context or "Not provided."}
FOCUS: {", ".join(focus_options)}
Be honest about risks and valuation. Keep it educational and accessible. End with a disclaimer."""
        with st.spinner("Gemini is analysing..."):
            try:
                response = model.generate_content(prompt)
                st.markdown(f'<div class="chat-ai"><div class="chat-lbl" style="color:#00d68f;">🧠 AI ANALYSIS — {ticker}</div>{response.text.replace(chr(10),"<br>")}</div>', unsafe_allow_html=True)
                st.session_state["last_analysis"] = {"ticker":ticker,"analysis":response.text,"info":info}
            except Exception as e:
                st.error(f"Gemini error: {e}")
else:
    st.markdown('<div class="info-box">← Enter a ticker and hit ANALYSE to get started.</div>', unsafe_allow_html=True)
