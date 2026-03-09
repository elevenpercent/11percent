import streamlit as st
import google.generativeai as genai
import sys, os, json
from datetime import date, timedelta
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.data import get_stock_data, get_ticker_info, get_news
from utils.styles import SHARED_CSS

st.set_page_config(page_title="Analysis | 11%", layout="wide", initial_sidebar_state="collapsed")
st.markdown(SHARED_CSS, unsafe_allow_html=True)

def navbar():
    st.markdown('<div class="nb"><div class="nb-brand"><span class="g">11</span><span class="r">%</span></div><div class="nb-links">', unsafe_allow_html=True)
    c = st.columns([1,1,1,1,1,1,1])
    with c[0]: st.page_link("app.py",                    label="Home")
    with c[1]: st.page_link("pages/1_Backtest.py",       label="Backtest")
    with c[2]: st.page_link("pages/2_Indicator_Test.py", label="Indicators")
    with c[3]: st.page_link("pages/3_Replay.py",         label="Replay")
    with c[4]: st.page_link("pages/4_Analysis.py",       label="Analysis")
    with c[5]: st.page_link("pages/6_Earnings.py",       label="Earnings")
    with c[6]: st.page_link("pages/5_Assistant.py",      label="Coach")
    st.markdown('</div><div class="nb-tag">FREE * OPEN SOURCE</div></div>', unsafe_allow_html=True)
navbar()

try:    api_key = st.secrets["GEMINI_API_KEY"]
except: api_key = os.getenv("GEMINI_API_KEY", "")
if api_key: genai.configure(api_key=api_key); model = genai.GenerativeModel("gemini-2.5-flash")
else: model = None

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

# -- Page header ----------------------------------------------------------------
st.markdown("""
<div class="page-header">
    <h1>Stock Analysis</h1>
    <p>Fundamentals, financials, price history and AI-powered investment breakdown for any ticker.</p>
</div>
""", unsafe_allow_html=True)

# -- Search bar -----------------------------------------------------------------
st.markdown('<div class="config-panel">', unsafe_allow_html=True)
s1, s2, s3 = st.columns([1, 2, 2])
with s1: ticker = st.text_input("Ticker", value="AAPL", label_visibility="visible").upper().strip()
with s2: focus_options = st.multiselect("AI Focus", ["Overall thesis","Financial health","Valuation","Growth drivers","Key risks","Recent news","Beginner-friendly"], default=["Overall thesis","Key risks"])
with s3: user_context = st.text_input("Your context", placeholder="e.g. Long-term investor, 5-year horizon, moderate risk")
analyze_btn = st.button("Analyse", type="primary")
if not api_key: st.markdown('<div class="warn-box" style="margin-top:0.5rem;">No Gemini API key - metrics and charts load, AI section skipped.</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

if not analyze_btn:
    st.markdown("""
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;margin-top:1rem;">
        <div class="panel-sm"><div style="font-family:'IBM Plex Mono',monospace;font-size:0.62rem;color:#00d68f;text-transform:uppercase;letter-spacing:0.12em;margin-bottom:0.5rem;">What gets pulled</div><div style="font-size:0.82rem;color:#8892a4;line-height:1.65;">Market cap, P/E, forward P/E, revenue, profit margin, ROE, debt/equity, beta, dividend, 52-week range.</div></div>
        <div class="panel-sm"><div style="font-family:'IBM Plex Mono',monospace;font-size:0.62rem;color:#00d68f;text-transform:uppercase;letter-spacing:0.12em;margin-bottom:0.5rem;">Price chart</div><div style="font-size:0.82rem;color:#8892a4;line-height:1.65;">1-year interactive price chart with 50-day moving average overlay and recent news headlines.</div></div>
        <div class="panel-sm"><div style="font-family:'IBM Plex Mono',monospace;font-size:0.62rem;color:#00d68f;text-transform:uppercase;letter-spacing:0.12em;margin-bottom:0.5rem;">AI breakdown</div><div style="font-size:0.82rem;color:#8892a4;line-height:1.65;">Gemini AI reads all the data and writes a structured verdict: bull/bear case, risks, valuation and advice for your profile.</div></div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# -- Load data ------------------------------------------------------------------
with st.spinner(f"Loading {ticker}?"):
    info = get_ticker_info(ticker)
    df   = get_stock_data(ticker, str(date.today()-timedelta(days=365)), str(date.today()))
    news = get_news(ticker)

if not info.get("name"): st.error(f"Could not find '{ticker}'. Check the symbol."); st.stop()

cp = float(df["Close"].iloc[-1]) if not df.empty else 0
pct_1y = (cp - float(df["Close"].iloc[0])) / float(df["Close"].iloc[0]) * 100 if not df.empty and float(df["Close"].iloc[0]) > 0 else 0

# -- Company header -------------------------------------------------------------
st.markdown(f"""
<div style="background:#0d1117;border:1px solid #1a2235;border-radius:10px;padding:1.4rem 1.8rem;margin:1rem 0;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:1rem;">
    <div>
        <div style="font-family:'Bebas Neue',sans-serif;font-size:2.2rem;letter-spacing:0.05em;line-height:1;">{info.get('name',ticker)}</div>
        <div style="font-family:'IBM Plex Mono',monospace;font-size:0.65rem;color:#3a4558;margin-top:0.2rem;">{ticker} * {info.get('sector','N/A')} * {info.get('industry','N/A')}</div>
    </div>
    <div style="text-align:right;">
        <div style="font-family:'IBM Plex Mono',monospace;font-size:1.5rem;">${cp:,.2f}</div>
        <div style="font-size:0.72rem;color:{'#00d68f' if pct_1y>=0 else '#ff4757'};">{pct_1y:+.2f}% past 12 months</div>
    </div>
</div>
""", unsafe_allow_html=True)

# -- Metrics --------------------------------------------------------------------
st.markdown('<div class="divider">Fundamentals</div>', unsafe_allow_html=True)
pm = info.get("profit_margin") or 0
roe_ = info.get("roe") or 0
de_ = info.get("debt_equity") or 0

m_cols = st.columns(6)
for col, lbl, val, cls in [
    (m_cols[0], "Market Cap",    fmt(info.get("market_cap"),"large"),  "neu"),
    (m_cols[1], "P/E Ratio",     fmt(info.get("pe_ratio"),"ratio"),    "neu"),
    (m_cols[2], "Forward P/E",   fmt(info.get("fwd_pe"),"ratio"),      "neu"),
    (m_cols[3], "Revenue",       fmt(info.get("revenue"),"large"),     "neu"),
    (m_cols[4], "Profit Margin", fmt(pm,"pct"),                        "pos" if pm>0.1 else ("neu" if pm>0 else "neg")),
    (m_cols[5], "ROE",           fmt(roe_,"pct"),                      "pos" if roe_>0.15 else ("neu" if roe_>0 else "neg")),
]:
    col.markdown(f'<div class="metric-card"><div class="metric-val {cls}">{val}</div><div class="metric-lbl">{lbl}</div></div>', unsafe_allow_html=True)

m2_cols = st.columns(6)
for col, lbl, val, cls in [
    (m2_cols[0], "Debt / Equity", fmt(de_,"ratio"),                       "pos" if de_<1 else ("neu" if de_<3 else "neg")),
    (m2_cols[1], "Beta",          fmt(info.get("beta")),                   "neu"),
    (m2_cols[2], "EPS",           fmt(info.get("eps")),                    "neu"),
    (m2_cols[3], "52W High",      f"${info.get('52w_high',0):.2f}" if info.get("52w_high") else "N/A", "neu"),
    (m2_cols[4], "52W Low",       f"${info.get('52w_low',0):.2f}"  if info.get("52w_low")  else "N/A", "neu"),
    (m2_cols[5], "Dividend",      fmt(info.get("dividend"),"pct") if info.get("dividend") else "None",  "neu"),
]:
    col.markdown(f'<div class="metric-card" style="margin-top:0.6rem;"><div class="metric-val {cls}">{val}</div><div class="metric-lbl">{lbl}</div></div>', unsafe_allow_html=True)

# -- Price chart ----------------------------------------------------------------
if not df.empty:
    st.markdown('<div class="divider">1-Year Price</div>', unsafe_allow_html=True)
    import plotly.graph_objects as go
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["Close"], mode="lines", line=dict(color="#00d68f",width=2), fill="tozeroy", fillcolor="rgba(0,214,143,0.04)", name="Price"))
    fig.add_trace(go.Scatter(x=df.index, y=df["Close"].rolling(50).mean(), mode="lines", line=dict(color="#4da6ff",width=1,dash="dot"), name="50-day MA"))
    fig.update_layout(paper_bgcolor="#07090d", plot_bgcolor="#07090d",
        font=dict(family="IBM Plex Mono",color="#8892a4",size=11),
        xaxis=dict(gridcolor="#1a2235",linecolor="#1a2235"),
        yaxis=dict(gridcolor="#1a2235",linecolor="#1a2235"),
        margin=dict(l=10,r=10,t=20,b=10), height=260,
        xaxis_rangeslider_visible=False,
        legend=dict(bgcolor="#0d1117",bordercolor="#1a2235",borderwidth=1))
    st.plotly_chart(fig, use_container_width=True)

# -- News & summary side by side ------------------------------------------------
nl, nr = st.columns([1, 1])
with nl:
    if info.get("summary"):
        st.markdown('<div class="divider">About</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="font-size:0.83rem;color:#8892a4;line-height:1.75;">{info["summary"][:600]}{"?" if len(info.get("summary",""))>600 else ""}</div>', unsafe_allow_html=True)
with nr:
    if news:
        st.markdown('<div class="divider">Recent News</div>', unsafe_allow_html=True)
        for item in news[:5]:
            st.markdown(f'<div class="row-item"><div><a href="{item.get("link","#")}" target="_blank" style="color:#e2e8f0;text-decoration:none;font-size:0.82rem;line-height:1.5;">{item.get("title","")}</a><div style="font-family:IBM Plex Mono,monospace;font-size:0.6rem;color:#3a4558;margin-top:0.2rem;">{item.get("publisher","")}</div></div></div>', unsafe_allow_html=True)

# -- AI Analysis ----------------------------------------------------------------
st.markdown('<div class="divider">AI Analysis</div>', unsafe_allow_html=True)

if not model:
    st.markdown('<div class="warn-box">Add GEMINI_API_KEY to Streamlit Secrets to enable AI analysis.</div>', unsafe_allow_html=True)
else:
    last_bt = st.session_state.get("last_backtest"); bt_ctx = ""
    if last_bt and last_bt.get("ticker") == ticker:
        mm = last_bt["metrics"]
        bt_ctx = f"Backtest: {last_bt['strategy']} ? Return {mm['total_return']:+.2f}%, Drawdown {mm['max_drawdown']:.2f}%, Win Rate {mm['win_rate']:.0f}%"

    prompt = f"""You are a financial educator on 11%, a free trading education platform.
Respond ONLY with valid JSON - no markdown fences, no text outside the JSON:
{{
  "verdict": "Bullish|Bearish|Neutral",
  "confidence": "High|Medium|Low",
  "one_liner": "One sentence.",
  "bull_case": "One sentence best case.",
  "bear_case": "One sentence worst case.",
  "sections": [
    {{"title": "Business Overview", "body": "2-3 sentences."}},
    {{"title": "Financial Health", "body": "Revenue, margins, ROE, debt - what they indicate."}},
    {{"title": "Valuation", "body": "Cheap or expensive vs peers and history?"}},
    {{"title": "Growth Drivers", "body": "What could drive it higher?"}},
    {{"title": "Key Risks", "body": "Top 2-3 concrete risks. Be honest."}},
    {{"title": "Technical Picture", "body": "1-year trend, MA position, momentum."}},
    {{"title": "For This Investor", "body": "Specific guidance based on their profile."}}
  ],
  "disclaimer": "One sentence disclaimer."
}}
STOCK: {ticker} | {info.get('name','')} | {info.get('sector','N/A')}
PRICE: ${cp:,.2f} (1Y: {pct_1y:+.2f}%)
FINANCIALS: MarketCap {fmt(info.get('market_cap'),'large')} | P/E {fmt(info.get('pe_ratio'),'ratio')} | FwdP/E {fmt(info.get('fwd_pe'),'ratio')} | Revenue {fmt(info.get('revenue'),'large')} | Margin {fmt(info.get('profit_margin'),'pct')} | ROE {fmt(info.get('roe'),'pct')} | D/E {fmt(info.get('debt_equity'),'ratio')} | Beta {fmt(info.get('beta'))}
{bt_ctx}
INVESTOR: {user_context or "Not specified"} | FOCUS: {", ".join(focus_options)}
Return JSON only."""

    with st.spinner("Analysing?"):
        try:
            r = model.generate_content(prompt)
            raw = r.text.strip()
            if raw.startswith("```"): raw = raw.split("\n",1)[-1].rsplit("```",1)[0]
            try:
                data = json.loads(raw)
                verdict = data.get("verdict","Neutral")
                conf    = data.get("confidence","")
                vcol    = "#00d68f" if "bull" in verdict.lower() else ("#ff4757" if "bear" in verdict.lower() else "#e2e8f0")

                # Verdict card
                st.markdown(f"""
                <div style="background:linear-gradient(135deg,#0d1117,#111620);border:1px solid #1a2235;border-radius:12px;padding:1.8rem;margin-bottom:1.2rem;">
                    <div style="display:flex;align-items:center;gap:1rem;margin-bottom:1.2rem;">
                        <div style="font-family:'Bebas Neue',sans-serif;font-size:2.4rem;color:{vcol};letter-spacing:0.08em;line-height:1;">{verdict.upper()}</div>
                        {'<span class="tag" style="background:'+vcol+'18;color:'+vcol+';border:1px solid '+vcol+'30;">'+conf+' Confidence</span>' if conf else ""}
                        <div style="font-size:0.9rem;color:#8892a4;line-height:1.6;flex:1;">{data.get('one_liner','')}</div>
                    </div>
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;">
                        <div style="background:#071a0f;border:1px solid #00d68f1a;border-radius:8px;padding:1rem;">
                            <div style="font-family:'IBM Plex Mono',monospace;font-size:0.58rem;color:#3a4558;text-transform:uppercase;letter-spacing:0.15em;margin-bottom:0.5rem;">Bull Case</div>
                            <div style="font-size:0.84rem;color:#00d68f;line-height:1.6;">{data.get('bull_case','')}</div>
                        </div>
                        <div style="background:#1a0a08;border:1px solid #ff47571a;border-radius:8px;padding:1rem;">
                            <div style="font-family:'IBM Plex Mono',monospace;font-size:0.58rem;color:#3a4558;text-transform:uppercase;letter-spacing:0.15em;margin-bottom:0.5rem;">Bear Case</div>
                            <div style="font-size:0.84rem;color:#ff4757;line-height:1.6;">{data.get('bear_case','')}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Sections grid
                sections = data.get("sections", [])
                for i in range(0, len(sections), 2):
                    c1, c2 = st.columns(2)
                    for col, sec in zip([c1,c2], sections[i:i+2]):
                        col.markdown(f"""
                        <div style="background:#0d1117;border:1px solid #1a2235;border-radius:8px;padding:1.2rem;margin-bottom:0.8rem;">
                            <div style="font-family:'IBM Plex Mono',monospace;font-size:0.6rem;color:#00d68f;text-transform:uppercase;letter-spacing:0.15em;margin-bottom:0.5rem;">{sec['title']}</div>
                            <div style="font-size:0.84rem;color:#8892a4;line-height:1.75;">{sec['body']}</div>
                        </div>""", unsafe_allow_html=True)

                st.markdown(f'<div style="font-family:IBM Plex Mono,monospace;font-size:0.62rem;color:#3a4558;padding-top:0.8rem;border-top:1px solid #1a2235;">(!) {data.get("disclaimer","Not financial advice.")}</div>', unsafe_allow_html=True)

            except json.JSONDecodeError:
                st.markdown(f'<div class="chat-ai"><div class="chat-lbl" style="color:#00d68f;">AI Analysis</div>{r.text.replace(chr(10),"<br>")}</div>', unsafe_allow_html=True)
            st.session_state["last_analysis"] = {"ticker": ticker, "analysis": r.text, "info": info}
        except Exception as e: st.error(f"Gemini error: {e}")
