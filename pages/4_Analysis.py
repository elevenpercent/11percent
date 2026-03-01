import streamlit as st
import google.generativeai as genai
import sys, os
from datetime import date, timedelta
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.data import get_stock_data, get_ticker_info, get_news
from utils.styles import SHARED_CSS

st.set_page_config(page_title="Analysis | 11%", page_icon="🧠", layout="wide", initial_sidebar_state="collapsed")
st.markdown(SHARED_CSS, unsafe_allow_html=True)
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
        prompt=f"""You are a financial analysis AI on 11%, a free trading education platform.
Analyse this stock and respond ONLY with valid JSON in this exact structure — no markdown, no explanation outside the JSON:

{{
  "verdict": "Bull | Bear | Neutral",
  "one_liner": "One sentence summary of the investment case.",
  "sections": [
    {{"title": "Business Overview", "body": "2-3 sentences about what the company does and its market position."}},
    {{"title": "Financial Health", "body": "Comment on revenue, margins, ROE, debt/equity and what they indicate."}},
    {{"title": "Valuation", "body": "Is the stock cheap or expensive? Reference P/E, forward P/E and compare to sector norms."}},
    {{"title": "Growth Potential", "body": "What drives future growth? Products, markets, tailwinds."}},
    {{"title": "Key Risks", "body": "Top 2-3 risks an investor must be aware of — be honest and direct."}},
    {{"title": "Recent News Impact", "body": "How does recent news affect the outlook? If no news context, say so."}},
    {{"title": "For Your Profile", "body": "Specific advice for this user based on their experience and goals."}}
  ],
  "bull_case": "One sentence on the best case scenario.",
  "bear_case": "One sentence on the worst case scenario.",
  "disclaimer": "One sentence standard disclaimer."
}}

STOCK: {ticker} — {info.get("name","")} | SECTOR: {info.get("sector","N/A")} | INDUSTRY: {info.get("industry","N/A")}
FINANCIALS: Market Cap {fmt(info.get("market_cap"),"large")} | P/E {fmt(info.get("pe_ratio"),"ratio")} | Fwd P/E {fmt(info.get("fwd_pe"),"ratio")} | Revenue {fmt(info.get("revenue"),"large")} | Profit Margin {fmt(info.get("profit_margin"),"pct")} | ROE {fmt(info.get("roe"),"pct")} | Debt/Equity {fmt(info.get("debt_equity"),"ratio")} | Beta {fmt(info.get("beta"))} | 52W High {fmt(info.get("52w_high"))} | 52W Low {fmt(info.get("52w_low"))}
{bt_ctx}
USER PROFILE: {user_context or "Not provided."} | FOCUS: {", ".join(focus_options)}
Respond with JSON only. No other text."""

        with st.spinner("Analysing..."):
            try:
                import json as _json
                r = model.generate_content(prompt)
                raw = r.text.strip()
                # Strip markdown code fences if present
                if raw.startswith("```"):
                    raw = raw.split("\n", 1)[-1]
                    raw = raw.rsplit("```", 1)[0]
                try:
                    data = _json.loads(raw)
                    # ── Render structured output ──────────────────────────────
                    verdict = data.get("verdict","Neutral")
                    vcol = "#00d68f" if verdict=="Bull" else "#ff4757" if verdict=="Bear" else "#cdd5e0"
                    st.markdown(f'''
<div style="background:#0d1117;border:1px solid #1c2333;border-radius:6px;padding:1.5rem;margin-bottom:1rem;">
  <div style="display:flex;align-items:center;gap:1.2rem;margin-bottom:0.8rem;">
    <div style="font-family:'Bebas Neue',sans-serif;font-size:1.8rem;color:{vcol};letter-spacing:0.08em;">{verdict.upper()}</div>
    <div style="font-size:0.88rem;color:#cdd5e0;line-height:1.6;">{data.get("one_liner","")}</div>
  </div>
  <div style="display:flex;gap:1rem;flex-wrap:wrap;">
    <div style="flex:1;min-width:200px;background:#071a0f;border:1px solid #0d3320;border-radius:4px;padding:0.7rem 1rem;">
      <div style="font-family:'IBM Plex Mono',monospace;font-size:0.58rem;color:#3a4558;text-transform:uppercase;letter-spacing:0.15em;margin-bottom:0.3rem;">Bull Case</div>
      <div style="font-size:0.8rem;color:#00d68f;">{data.get("bull_case","")}</div>
    </div>
    <div style="flex:1;min-width:200px;background:#1a0a08;border:1px solid #3a1008;border-radius:4px;padding:0.7rem 1rem;">
      <div style="font-family:'IBM Plex Mono',monospace;font-size:0.58rem;color:#3a4558;text-transform:uppercase;letter-spacing:0.15em;margin-bottom:0.3rem;">Bear Case</div>
      <div style="font-size:0.8rem;color:#ff4757;">{data.get("bear_case","")}</div>
    </div>
  </div>
</div>''', unsafe_allow_html=True)

                    # Sections in 2-col grid
                    sections = data.get("sections", [])
                    for i in range(0, len(sections), 2):
                        c1, c2 = st.columns(2)
                        for col, sec in zip([c1,c2], sections[i:i+2]):
                            col.markdown(f'''
<div style="background:#0d1117;border:1px solid #1c2333;border-radius:6px;padding:1.2rem;margin-bottom:0.8rem;height:100%;">
  <div style="font-family:'IBM Plex Mono',monospace;font-size:0.6rem;color:#00d68f;text-transform:uppercase;letter-spacing:0.15em;margin-bottom:0.6rem;">{sec["title"]}</div>
  <div style="font-size:0.82rem;color:#8892a4;line-height:1.72;">{sec["body"]}</div>
</div>''', unsafe_allow_html=True)

                    st.markdown(f'<div style="font-family:IBM Plex Mono,monospace;font-size:0.65rem;color:#3a4558;margin-top:0.5rem;border-top:1px solid #1c2333;padding-top:0.8rem;">⚠ {data.get("disclaimer","Not financial advice.")}</div>', unsafe_allow_html=True)

                except _json.JSONDecodeError:
                    # Fallback to plain text if JSON parse fails
                    st.markdown(f'<div class="chat-ai"><div class="chat-lbl" style="color:#00d68f;">AI Analysis — {ticker}</div>{r.text.replace(chr(10),"<br>")}</div>', unsafe_allow_html=True)

                st.session_state["last_analysis"]={"ticker":ticker,"analysis":r.text,"info":info}
            except Exception as e: st.error(f"Gemini error: {e}")
else:
    st.markdown('<div class="info-box">Enter a ticker above and click Analyse to get started.</div>', unsafe_allow_html=True)
