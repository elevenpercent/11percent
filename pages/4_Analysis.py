import streamlit as st
import google.generativeai as genai
import sys, os, json
from datetime import date, timedelta
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.data import get_stock_data, get_ticker_info, get_news
from utils.styles import SHARED_CSS

st.set_page_config(page_title="Analysis | 11%", layout="wide", initial_sidebar_state="collapsed")
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

try:    api_key = st.secrets["GEMINI_API_KEY"]
except: api_key = os.getenv("GEMINI_API_KEY", "")
if api_key: genai.configure(api_key=api_key); model = genai.GenerativeModel("gemini-2.5-flash")
else: model = None

st.markdown('''<div class="page-header"><h1>Stock Analysis</h1><p>Pull up any stock's fundamentals, financials and price history — then get an AI-generated breakdown of the investment case.</p></div>''', unsafe_allow_html=True)

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

# ── What is fundamental analysis ─────────────────────────────────────────────
with st.expander("New here? What is fundamental analysis?"):
    fa1, fa2, fa3 = st.columns(3)
    with fa1:
        st.markdown("""**Fundamental vs Technical**

Technical analysis (what the Backtest and Replay pages do) looks at price and volume patterns. Fundamental analysis looks at the actual business — revenue, profits, debt, growth prospects — to decide if the stock is fairly priced.

Both are tools. Most serious investors use both.""")
    with fa2:
        st.markdown("""**Key metrics explained**

**P/E ratio** — price divided by earnings. Lower = cheaper, but context matters. A 30x P/E for a fast-growing tech company might be fair; 30x for a slow utility would be expensive.

**Market cap** — total value of all shares. Under $2B = small cap. $2–10B = mid. Over $10B = large cap.

**ROE** — Return on Equity. How much profit per dollar of shareholder capital. Above 15% is generally good.""")
    with fa3:
        st.markdown("""**Profit margin and debt**

**Profit margin** — what % of revenue becomes profit. Software companies often hit 25-40%. Retailers might be 2-5%.

**Debt/Equity** — how much the company borrowed vs shareholder equity. Very high D/E can be risky in rising rate environments.

**Beta** — how much the stock moves vs the market. Beta 1.5 = moves 50% more than the index. Beta 0.5 = much calmer.""")

# ── Setup ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="price-divider">SETUP</div>', unsafe_allow_html=True)
st.markdown('<div class="config-panel">', unsafe_allow_html=True)
ac1,ac2,ac3 = st.columns([1,2,2])
with ac1: ticker = st.text_input("Ticker Symbol", value="AAPL").upper().strip()
with ac2: focus_options = st.multiselect("AI Focus Areas",
    ["Overall investment thesis","Financial health & fundamentals","Valuation","Growth potential","Key risks","Competitor landscape","Recent news impact","For beginners — explain simply"],
    default=["Overall investment thesis","Key risks"])
with ac3: user_context = st.text_input("Your context (optional)", placeholder="e.g. Long-term investor, 5-year horizon, moderate risk tolerance")
analyze_btn = st.button("Run Analysis", use_container_width=False)
if not api_key:
    st.markdown('<div class="warn-box">No Gemini API key — AI analysis will be skipped. Metrics and charts will still load. Add GEMINI_API_KEY to Streamlit Secrets to enable AI.</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

if analyze_btn:
    with st.spinner(f"Loading {ticker} data..."):
        info = get_ticker_info(ticker)
        df   = get_stock_data(ticker, str(date.today()-timedelta(days=365)), str(date.today()))
        news = get_news(ticker)

    if not info.get("name"):
        st.error(f"Could not find data for '{ticker}'. Check the symbol and try again.")
        st.stop()

    # Company header
    cp = float(df["Close"].iloc[-1]) if not df.empty else 0
    cp_1y_ago = float(df["Close"].iloc[0]) if not df.empty else 0
    pct_1y = (cp - cp_1y_ago) / cp_1y_ago * 100 if cp_1y_ago > 0 else 0
    st.markdown(f'''<div style="background:#0d1117;border:1px solid #1c2333;border-radius:6px;padding:1.2rem 1.5rem;margin:1rem 0;display:flex;align-items:flex-start;gap:2rem;flex-wrap:wrap;">
        <div>
          <div style="font-family:'Bebas Neue',sans-serif;font-size:2.2rem;letter-spacing:0.06em;">{info.get("name",ticker)}</div>
          <div style="font-family:'IBM Plex Mono',monospace;font-size:0.68rem;color:#3a4558;">{ticker} · {info.get("sector","N/A")} · {info.get("industry","N/A")}</div>
        </div>
        <div style="margin-left:auto;text-align:right;">
          <div style="font-family:'IBM Plex Mono',monospace;font-size:1.4rem;">${cp:,.2f}</div>
          <div style="font-size:0.72rem;color:{"#00d68f" if pct_1y>=0 else "#ff4757"};">{pct_1y:+.2f}% past year</div>
        </div>
    </div>''', unsafe_allow_html=True)

    # Metrics grid row 1
    st.markdown('<div class="price-divider">VALUATION</div>', unsafe_allow_html=True)
    v1,v2,v3,v4,v5,v6 = st.columns(6)
    for col,lbl,val,tip in [
        (v1,"Market Cap",   fmt(info.get("market_cap"),"large"),  "Total value of all shares outstanding"),
        (v2,"P/E Ratio",    fmt(info.get("pe_ratio"),"ratio"),    "Price divided by trailing 12-month earnings"),
        (v3,"Fwd P/E",      fmt(info.get("fwd_pe"),"ratio"),      "P/E based on expected future earnings"),
        (v4,"EPS",          fmt(info.get("eps")),                  "Earnings per share (trailing 12 months)"),
        (v5,"52W High",     f"${info.get('52w_high',0):.2f}" if info.get("52w_high") else "N/A", "Highest price in past 52 weeks"),
        (v6,"52W Low",      f"${info.get('52w_low',0):.2f}" if info.get("52w_low") else "N/A",  "Lowest price in past 52 weeks"),
    ]:
        col.markdown(f'<div class="metric-card" title="{tip}"><div class="metric-val neu">{val}</div><div class="metric-lbl">{lbl}</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="price-divider">FINANCIAL HEALTH</div>', unsafe_allow_html=True)
    f1,f2,f3,f4,f5,f6 = st.columns(6)
    pm = info.get("profit_margin") or 0
    roe = info.get("roe") or 0
    de  = info.get("debt_equity") or 0
    for col,lbl,val,cls in [
        (f1,"Revenue",      fmt(info.get("revenue"),"large"),     "neu"),
        (f2,"Profit Margin",fmt(pm,"pct"),                        "pos" if pm>0.1 else ("neu" if pm>0 else "neg")),
        (f3,"ROE",          fmt(roe,"pct"),                       "pos" if roe>0.15 else ("neu" if roe>0 else "neg")),
        (f4,"Debt/Equity",  fmt(de,"ratio"),                      "pos" if de<1 else ("neu" if de<3 else "neg")),
        (f5,"Beta",         fmt(info.get("beta")),                "neu"),
        (f6,"Dividend",     fmt(info.get("dividend"),"pct") if info.get("dividend") else "None","neu"),
    ]:
        col.markdown(f'<div class="metric-card"><div class="metric-val {cls}">{val}</div><div class="metric-lbl">{lbl}</div></div>', unsafe_allow_html=True)

    # 1-year price chart
    if not df.empty:
        st.markdown('<div class="price-divider">1-YEAR PRICE CHART</div>', unsafe_allow_html=True)
        import plotly.graph_objects as go
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.index, y=df["Close"], mode="lines", line=dict(color="#00d68f", width=2), fill="tozeroy", fillcolor="rgba(0,214,143,0.04)"))
        fig.add_trace(go.Scatter(x=df.index, y=df["Close"].rolling(50).mean(), mode="lines", line=dict(color="#4da6ff", width=1, dash="dot"), name="50-day MA"))
        fig.update_layout(paper_bgcolor="#07090d", plot_bgcolor="#07090d", font=dict(family="IBM Plex Mono", color="#cdd5e0", size=11),
            xaxis=dict(gridcolor="#1c2333", linecolor="#1c2333"), yaxis=dict(gridcolor="#1c2333", linecolor="#1c2333"),
            margin=dict(l=10,r=10,t=20,b=10), height=280, xaxis_rangeslider_visible=False,
            legend=dict(bgcolor="#0d1117", bordercolor="#1c2333", borderwidth=1), showlegend=True)
        st.plotly_chart(fig, use_container_width=True)

    # Business summary
    if info.get("summary"):
        with st.expander("Business Summary"):
            st.markdown(f'<p style="font-size:0.85rem;line-height:1.8;color:#8892a4;">{info["summary"]}</p>', unsafe_allow_html=True)

    # Recent news
    if news:
        st.markdown('<div class="price-divider">RECENT NEWS</div>', unsafe_allow_html=True)
        for item in news[:6]:
            pub = item.get("publisher",""); title = item.get("title",""); link = item.get("link","#")
            st.markdown(f'<div style="padding:0.6rem 0;border-bottom:1px solid #1c2333;display:flex;align-items:flex-start;gap:0.8rem;"><div style="flex:1;"><a href="{link}" target="_blank" style="color:#cdd5e0;text-decoration:none;font-size:0.83rem;line-height:1.5;">{title}</a></div><div style="font-family:IBM Plex Mono,monospace;font-size:0.6rem;color:#3a4558;flex-shrink:0;padding-top:2px;">{pub}</div></div>', unsafe_allow_html=True)

    # AI analysis
    st.markdown('<div class="price-divider">AI ANALYSIS</div>', unsafe_allow_html=True)
    if not model:
        st.markdown('<div class="warn-box">Add GEMINI_API_KEY to Streamlit Secrets to enable AI analysis.</div>', unsafe_allow_html=True)
    else:
        last_bt = st.session_state.get("last_backtest"); bt_ctx = ""
        if last_bt and last_bt.get("ticker") == ticker:
            mm = last_bt["metrics"]
            bt_ctx = f"Backtest context: {last_bt['strategy']} → Return {mm['total_return']:+.2f}%, Max Drawdown {mm['max_drawdown']:.2f}%, Win Rate {mm['win_rate']:.0f}%, Sharpe {mm['sharpe']}"

        prompt = f"""You are a financial educator on 11%, a free trading education platform. Analyse this stock for a learner.
Respond ONLY with valid JSON matching this exact structure. No markdown fences, no text outside the JSON:

{{
  "verdict": "Bullish",
  "confidence": "High",
  "one_liner": "One sentence summary.",
  "bull_case": "One sentence best case.",
  "bear_case": "One sentence worst case.",
  "sections": [
    {{"title": "Business Overview", "body": "What the company does, market position, competitive moat."}},
    {{"title": "Financial Health", "body": "Revenue trend, margins, ROE, debt. Is the balance sheet strong?"}},
    {{"title": "Valuation", "body": "Is the stock cheap or expensive vs peers and history? P/E context."}},
    {{"title": "Growth Drivers", "body": "What could drive the stock higher? Products, markets, tailwinds."}},
    {{"title": "Key Risks", "body": "Top 2-3 concrete risks. Be honest — don't sugarcoat."}},
    {{"title": "Technical Picture", "body": "Comment on 1-year price trend, 50-day MA position, and momentum."}},
    {{"title": "For This Investor", "body": "Specific, personalised guidance based on their profile and focus areas."}}
  ],
  "disclaimer": "One sentence disclaimer."
}}

STOCK: {ticker} | {info.get("name","")} | {info.get("sector","N/A")} | {info.get("industry","N/A")}
PRICE: ${cp:,.2f} (1Y: {pct_1y:+.2f}%)
FINANCIALS: Market Cap {fmt(info.get("market_cap"),"large")} | P/E {fmt(info.get("pe_ratio"),"ratio")} | Fwd P/E {fmt(info.get("fwd_pe"),"ratio")} | Revenue {fmt(info.get("revenue"),"large")} | Profit Margin {fmt(info.get("profit_margin"),"pct")} | ROE {fmt(info.get("roe"),"pct")} | D/E {fmt(info.get("debt_equity"),"ratio")} | Beta {fmt(info.get("beta"))} | 52W High {fmt(info.get("52w_high"))} | 52W Low {fmt(info.get("52w_low"))}
{bt_ctx}
INVESTOR: {user_context or "Not specified"} | FOCUS: {", ".join(focus_options)}
Return JSON only."""

        with st.spinner("Generating AI analysis..."):
            try:
                r = model.generate_content(prompt)
                raw = r.text.strip()
                if raw.startswith("```"):
                    raw = raw.split("\n", 1)[-1].rsplit("```", 1)[0]
                try:
                    data = json.loads(raw)
                    verdict = data.get("verdict","Neutral")
                    conf    = data.get("confidence","")
                    vcol    = "#00d68f" if "bull" in verdict.lower() else ("#ff4757" if "bear" in verdict.lower() else "#cdd5e0")
                    st.markdown(f'''<div style="background:#0d1117;border:1px solid #1c2333;border-radius:6px;padding:1.5rem;margin-bottom:1rem;">
  <div style="display:flex;align-items:center;gap:1.2rem;margin-bottom:1rem;">
    <div style="font-family:'Bebas Neue',sans-serif;font-size:2rem;color:{vcol};letter-spacing:0.06em;">{verdict}</div>
    {f'<span style="font-family:IBM Plex Mono,monospace;font-size:0.62rem;padding:3px 10px;border-radius:2px;background:{vcol}18;color:{vcol};border:1px solid {vcol}44;">{conf} Confidence</span>' if conf else ""}
    <div style="font-size:0.88rem;color:#8892a4;line-height:1.6;flex:1;">{data.get("one_liner","")}</div>
  </div>
  <div style="display:flex;gap:1rem;">
    <div style="flex:1;background:#071a0f;border:1px solid #0d3320;border-radius:4px;padding:0.8rem 1rem;">
      <div style="font-family:'IBM Plex Mono',monospace;font-size:0.58rem;color:#3a4558;text-transform:uppercase;letter-spacing:0.12em;margin-bottom:0.4rem;">Bull Case</div>
      <div style="font-size:0.82rem;color:#00d68f;line-height:1.6;">{data.get("bull_case","")}</div>
    </div>
    <div style="flex:1;background:#1a0a08;border:1px solid #3a1008;border-radius:4px;padding:0.8rem 1rem;">
      <div style="font-family:'IBM Plex Mono',monospace;font-size:0.58rem;color:#3a4558;text-transform:uppercase;letter-spacing:0.12em;margin-bottom:0.4rem;">Bear Case</div>
      <div style="font-size:0.82rem;color:#ff4757;line-height:1.6;">{data.get("bear_case","")}</div>
    </div>
  </div>
</div>''', unsafe_allow_html=True)
                    sections = data.get("sections",[])
                    for i in range(0, len(sections), 2):
                        c1, c2 = st.columns(2)
                        for col, sec in zip([c1,c2], sections[i:i+2]):
                            col.markdown(f'<div style="background:#0d1117;border:1px solid #1c2333;border-radius:6px;padding:1.2rem;margin-bottom:0.8rem;"><div style="font-family:IBM Plex Mono,monospace;font-size:0.6rem;color:#00d68f;text-transform:uppercase;letter-spacing:0.15em;margin-bottom:0.5rem;">{sec["title"]}</div><div style="font-size:0.82rem;color:#8892a4;line-height:1.72;">{sec["body"]}</div></div>', unsafe_allow_html=True)
                    st.markdown(f'<div style="font-family:IBM Plex Mono,monospace;font-size:0.65rem;color:#3a4558;margin-top:0.5rem;padding-top:0.8rem;border-top:1px solid #1c2333;">⚠ {data.get("disclaimer","Not financial advice. For educational purposes only.")}</div>', unsafe_allow_html=True)
                except json.JSONDecodeError:
                    st.markdown(f'<div class="chat-ai"><div class="chat-lbl" style="color:#00d68f;">AI Analysis — {ticker}</div>{r.text.replace(chr(10),"<br>")}</div>', unsafe_allow_html=True)
                st.session_state["last_analysis"] = {"ticker":ticker,"analysis":r.text,"info":info}
            except Exception as e: st.error(f"Gemini error: {e}")
else:
    st.markdown('<div class="price-divider">WHAT THIS PAGE DOES</div>', unsafe_allow_html=True)
    w1, w2, w3 = st.columns(3)
    for col, title, body in [
        (w1, "Fundamentals", "Pulls live data from Yahoo Finance: market cap, P/E ratio, revenue, profit margins, debt/equity, ROE, beta, and dividend yield. All the numbers serious investors look at."),
        (w2, "Price History", "Shows the 1-year price chart with a 50-day moving average overlay so you can quickly see the current trend and where price sits relative to recent history."),
        (w3, "AI Breakdown",  "Gemini AI reads all the numbers and writes a structured analysis: verdict, bull/bear case, financial health, valuation, risks, and advice tailored to your investor profile."),
    ]:
        col.markdown(f'<div style="background:#0d1117;border:1px solid #1c2333;border-radius:6px;padding:1.2rem;"><div style="font-family:IBM Plex Mono,monospace;font-size:0.65rem;color:#00d68f;text-transform:uppercase;letter-spacing:0.12em;margin-bottom:0.6rem;">{title}</div><div style="font-size:0.82rem;color:#3a4558;line-height:1.7;">{body}</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="info-box" style="margin-top:1rem;">Enter a ticker above and click Run Analysis to get started.</div>', unsafe_allow_html=True)
