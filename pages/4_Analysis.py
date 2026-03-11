import streamlit as st
import google.generativeai as genai
import sys, os
from datetime import date, timedelta
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.styles import SHARED_CSS, PLOTLY_THEME
from utils.nav import navbar
from utils.data import get_stock_data, get_ticker_info, get_news

st.set_page_config(page_title="Analysis | 11%", layout="wide", initial_sidebar_state="collapsed")
st.markdown(SHARED_CSS, unsafe_allow_html=True)
navbar()

# ── API ────────────────────────────────────────────────────────────────────────
try:    api_key = st.secrets["GEMINI_API_KEY"]
except: api_key = os.getenv("GEMINI_API_KEY", "")
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")
else:
    model = None

def fmt(val, t="num"):
    if val is None: return "N/A"
    if t=="pct":   return f"{val*100:.1f}%"
    if t=="ratio": return f"{val:.2f}x"
    if t=="large":
        if val>=1e12: return f"${val/1e12:.2f}T"
        if val>=1e9:  return f"${val/1e9:.2f}B"
        if val>=1e6:  return f"${val/1e6:.2f}M"
        return f"${val:,.0f}"
    try: return f"{float(val):.2f}"
    except: return str(val)

# ── Page header ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
    <div class="page-header-eyebrow">AI-Powered Research</div>
    <h1>Stock Analysis</h1>
    <p>Fundamentals, financials, price history and AI-powered investment breakdown — for any ticker, in seconds.</p>
</div>
""", unsafe_allow_html=True)

# ── Controls ───────────────────────────────────────────────────────────────────
a1, a2, a3, a4 = st.columns([1, 2, 2, 1])
with a1: ticker = st.text_input("Ticker", value="AAPL").upper().strip()
with a2: focus_options = st.multiselect("AI Focus", ["Overall thesis","Financial health","Valuation","Growth drivers","Key risks","Recent news","Beginner-friendly"], default=["Overall thesis","Key risks"])
with a3: user_context = st.text_input("Your context", placeholder="e.g. Long-term investor, 5-year horizon, moderate risk")
with a4:
    st.markdown("<div style='height:1.75rem'></div>", unsafe_allow_html=True)
    analyze_btn = st.button("Analyse", type="primary", use_container_width=True)

if not api_key:
    st.markdown('<div class="warn-box" style="margin-bottom:1rem;">No Gemini API key — metrics and charts load, AI section skipped. Add GEMINI_API_KEY to Streamlit Secrets.</div>', unsafe_allow_html=True)

if not analyze_btn:
    st.markdown("""
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;margin-top:1rem;">
        <div class="panel-sm"><div style="font-family:'IBM Plex Mono',monospace;font-size:0.6rem;color:#00e676;text-transform:uppercase;letter-spacing:0.12em;margin-bottom:0.5rem;">What gets pulled</div><div style="font-size:0.82rem;color:#8892a4;line-height:1.65;">Market cap, P/E, forward P/E, revenue, profit margin, ROE, debt/equity, beta, dividend, 52-week range.</div></div>
        <div class="panel-sm"><div style="font-family:'IBM Plex Mono',monospace;font-size:0.6rem;color:#00e676;text-transform:uppercase;letter-spacing:0.12em;margin-bottom:0.5rem;">Price chart</div><div style="font-size:0.82rem;color:#8892a4;line-height:1.65;">1-year interactive price chart with volume overlay and recent news headlines.</div></div>
        <div class="panel-sm"><div style="font-family:'IBM Plex Mono',monospace;font-size:0.6rem;color:#00e676;text-transform:uppercase;letter-spacing:0.12em;margin-bottom:0.5rem;">AI breakdown</div><div style="font-size:0.82rem;color:#8892a4;line-height:1.65;">Gemini AI reads all the data and writes a structured verdict: bull/bear case, risks, valuation and advice for your profile.</div></div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── Load data ──────────────────────────────────────────────────────────────────
with st.spinner(f"Loading {ticker}…"):
    info = get_ticker_info(ticker)
    df   = get_stock_data(ticker, str(date.today()-timedelta(days=365)), str(date.today()))
    news = get_news(ticker)

if not info.get("name"): st.error(f"Could not find '{ticker}'. Check the symbol."); st.stop()

cp     = float(df["Close"].iloc[-1]) if not df.empty else 0
pct_1y = (cp - float(df["Close"].iloc[0])) / float(df["Close"].iloc[0]) * 100 if not df.empty and float(df["Close"].iloc[0]) > 0 else 0
pct_col = "#00e676" if pct_1y >= 0 else "#ff3d57"

# ── Stock banner ───────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="background:#0c1018;border:1px solid #1a2235;border-radius:10px;padding:1.2rem 1.5rem;margin:0.5rem 0 1.5rem 0;display:flex;align-items:center;gap:2rem;flex-wrap:wrap;">
    <div>
        <div style="font-family:'Bebas Neue',sans-serif;font-size:2.2rem;letter-spacing:0.06em;line-height:1;">{ticker}</div>
        <div style="font-family:'IBM Plex Mono',monospace;font-size:0.65rem;color:#3a4558;margin-top:2px;">{info.get('name','')} · {info.get('sector','N/A')} · {info.get('exchange','')}</div>
    </div>
    <div style="margin-left:auto;text-align:right;">
        <div style="font-family:'IBM Plex Mono',monospace;font-size:1.4rem;color:#eef2f7;">${cp:,.2f}</div>
        <div style="font-size:0.75rem;color:{pct_col};font-family:'IBM Plex Mono',monospace;">{pct_1y:+.2f}% (1Y)</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Metrics ────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-hdr"><div class="section-hdr-label">Key Metrics</div></div>', unsafe_allow_html=True)
mc1 = st.columns(8)
metrics = [
    ("Market Cap",    fmt(info.get("market_cap"),"large"), "neu"),
    ("P/E Ratio",     fmt(info.get("pe_ratio"),"ratio"),   "neu"),
    ("Fwd P/E",       fmt(info.get("fwd_pe"),"ratio"),     "neu"),
    ("Revenue",       fmt(info.get("revenue"),"large"),    "neu"),
    ("Profit Margin", fmt(info.get("profit_margin"),"pct"),"pos" if (info.get("profit_margin") or 0)>0 else "neg"),
    ("ROE",           fmt(info.get("roe"),"pct"),          "pos" if (info.get("roe") or 0)>0 else "neg"),
    ("Debt/Equity",   fmt(info.get("debt_equity"),"ratio"),"neu"),
    ("Beta",          fmt(info.get("beta")),               "neu"),
]
for col, (lbl, val, cls) in zip(mc1, metrics):
    col.markdown(f'<div class="metric-card"><div class="metric-val {cls}">{val}</div><div class="metric-lbl">{lbl}</div></div>', unsafe_allow_html=True)

mc2 = st.columns(8)
metrics2 = [
    ("52W High",  f"${info.get('52w_high',0):.2f}" if info.get("52w_high") else "N/A", "neu"),
    ("52W Low",   f"${info.get('52w_low',0):.2f}"  if info.get("52w_low")  else "N/A", "neu"),
    ("EPS",       fmt(info.get("eps")),              "neu"),
    ("Dividend",  fmt(info.get("dividend"),"pct") if info.get("dividend") else "None", "neu"),
    ("Employees", f"{info.get('employees',0):,}" if info.get("employees") else "N/A", "neu"),
    ("","","neu"),("","","neu"),("","","neu"),
]
for col, (lbl, val, cls) in zip(mc2, metrics2):
    if lbl:
        col.markdown(f'<div class="metric-card"><div class="metric-val {cls}">{val}</div><div class="metric-lbl">{lbl}</div></div>', unsafe_allow_html=True)

# ── Price chart ────────────────────────────────────────────────────────────────
if not df.empty:
    st.markdown('<div class="section-hdr"><div class="section-hdr-label">1-Year Price</div></div>', unsafe_allow_html=True)
    import plotly.graph_objects as go
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["Close"], mode="lines", name="Price",
        line=dict(color="#00e676", width=2), fill="tozeroy", fillcolor="rgba(0,230,118,0.04)"))
    fig.update_layout(**PLOTLY_THEME, height=280, xaxis_rangeslider_visible=False)
    fig.update_layout(margin=dict(l=10,r=10,t=20,b=10))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

# ── News ───────────────────────────────────────────────────────────────────────
if news:
    st.markdown('<div class="section-hdr"><div class="section-hdr-label">Recent News</div></div>', unsafe_allow_html=True)
    for item in news[:5]:
        title = item.get("title",""); link = item.get("link","#"); pub = item.get("publisher","")
        st.markdown(f"""
        <div style="padding:0.6rem 0;border-bottom:1px solid #1a2235;font-size:0.84rem;">
            <a href="{link}" target="_blank" style="color:#eef2f7;text-decoration:none;">{title}</a>
            <span style="font-family:'IBM Plex Mono',monospace;font-size:0.6rem;color:#3a4558;margin-left:0.8rem;">{pub}</span>
        </div>
        """, unsafe_allow_html=True)

# ── Business summary ───────────────────────────────────────────────────────────
if info.get("summary"):
    with st.expander("Business Summary"):
        st.markdown(f'<p style="font-size:0.87rem;line-height:1.75;color:#8896ab;">{info["summary"]}</p>', unsafe_allow_html=True)

# ── AI Analysis ────────────────────────────────────────────────────────────────
st.markdown('<div class="section-hdr"><div class="section-hdr-label">AI Analysis</div></div>', unsafe_allow_html=True)

if not model:
    st.markdown('<div class="warn-box">Add GEMINI_API_KEY to Streamlit Secrets to enable AI analysis.</div>', unsafe_allow_html=True)
else:
    last_bt = st.session_state.get("last_backtest")
    bt_ctx = ""
    if last_bt and last_bt.get("ticker") == ticker:
        m = last_bt["metrics"]
        bt_ctx = f"\nBacktest context: {last_bt['strategy']} returned {m['total_return']:+.2f}% vs {m['bh_return']:+.2f}% buy-and-hold. Drawdown: {m['max_drawdown']:.2f}%. Win rate: {m['win_rate']:.0f}%."

    prompt = f"""You are a financial analysis AI on 11%, a free trading education platform.
Provide sharp, honest, educational analysis. You are NOT a financial advisor.

STOCK: {ticker} — {info.get('name','')}
SECTOR: {info.get('sector','N/A')} | {info.get('industry','N/A')}

METRICS: Market Cap {fmt(info.get('market_cap'),'large')} · P/E {fmt(info.get('pe_ratio'),'ratio')} · Fwd P/E {fmt(info.get('fwd_pe'),'ratio')} · Revenue {fmt(info.get('revenue'),'large')} · Margin {fmt(info.get('profit_margin'),'pct')} · ROE {fmt(info.get('roe'),'pct')} · D/E {fmt(info.get('debt_equity'),'ratio')} · Beta {fmt(info.get('beta'))} · 52W {info.get('52w_low','?')}–{info.get('52w_high','?')}
{bt_ctx}
USER CONTEXT: {user_context or 'Not provided'}
FOCUS: {', '.join(focus_options)}

Write a structured analysis covering the requested focus areas. Be honest about risks and weaknesses. Use the metrics. End with a one-line disclaimer."""

    with st.spinner("Gemini is analysing…"):
        try:
            resp = model.generate_content(prompt)
            analysis_text = resp.text
            # Render as clean formatted panel
            formatted = analysis_text.replace("\n\n", "</p><p style='color:#8896ab;line-height:1.75;font-size:0.87rem;margin:0.6rem 0;'>").replace("\n", "<br>")
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#051510,#08180e);border:1px solid rgba(0,230,118,0.15);border-radius:10px;padding:1.5rem 1.5rem 1rem 1.5rem;margin-top:0.5rem;">
                <div style="font-family:'IBM Plex Mono',monospace;font-size:0.58rem;color:#00e676;text-transform:uppercase;letter-spacing:0.22em;margin-bottom:1rem;display:flex;align-items:center;gap:0.5rem;">
                    <span style="width:6px;height:6px;border-radius:50%;background:#00e676;display:inline-block;"></span>
                    Gemini Analysis — {ticker}
                </div>
                <p style="color:#8896ab;line-height:1.75;font-size:0.87rem;margin:0;">{formatted}</p>
            </div>
            """, unsafe_allow_html=True)
            st.session_state["last_analysis"] = {"ticker": ticker, "analysis": analysis_text, "info": info}
        except Exception as e:
            st.error(f"Gemini error: {e}")
