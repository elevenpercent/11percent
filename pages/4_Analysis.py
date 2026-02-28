import streamlit as st
import google.generativeai as genai
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from datetime import date, timedelta

from utils.styles import SHARED_CSS
from utils.data import get_stock_data, get_ticker_info, get_news

st.set_page_config(page_title="Analysis | 11%", page_icon="🧠", layout="wide")
st.markdown(SHARED_CSS, unsafe_allow_html=True)

# ── API setup ─────────────────────────────────────────────────────────────────
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    api_key = os.getenv("GEMINI_API_KEY", "")

if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")
else:
    model = None

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div style="font-family:\'Bebas Neue\',sans-serif;font-size:1.8rem;color:#f0b429;letter-spacing:0.1em;">11%</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### ANALYSIS SETUP")

    ticker = st.text_input("Ticker Symbol", value="AAPL").upper().strip()

    st.markdown("### AI FOCUS")
    focus_options = st.multiselect("What should AI analyse?", [
        "Overall investment thesis",
        "Financial health & fundamentals",
        "Risk assessment",
        "Growth potential",
        "Valuation (is it cheap or expensive?)",
        "Competitor comparison",
        "Recent news impact",
    ], default=["Overall investment thesis", "Risk assessment"])

    user_context = st.text_area(
        "Your situation (optional)",
        placeholder="e.g. I'm a long-term investor looking for dividend stocks. My risk tolerance is moderate.",
        height=100,
    )

    analyze_btn = st.button("🧠  ANALYSE", use_container_width=True)

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
    <h1>AI ANALYSIS</h1>
    <p>Fundamentals, financials, and AI-powered insights for any stock.</p>
</div>
""", unsafe_allow_html=True)

if not api_key:
    st.markdown("""
    <div class="warn-box">
        ⚠️ No Gemini API key found. Add GEMINI_API_KEY to your Streamlit Secrets to enable AI analysis.<br><br>
        Get a free key at <strong>aistudio.google.com</strong> → Get API Key.
    </div>
    """, unsafe_allow_html=True)

if analyze_btn:
    with st.spinner(f"Loading data for {ticker}..."):
        info  = get_ticker_info(ticker)
        df    = get_stock_data(ticker, str(date.today() - timedelta(days=365)), str(date.today()))
        news  = get_news(ticker)

    if not info.get("name"):
        st.error("Could not find data for this ticker.")
        st.stop()

    # ── Stock header ──────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="margin-bottom:1.5rem;">
        <div style="font-family:'Bebas Neue',sans-serif; font-size:2.2rem; letter-spacing:0.05em;">{info.get('name', ticker)}</div>
        <div style="font-family:'IBM Plex Mono',monospace; font-size:0.72rem; color:#4a5568; margin-top:0.2rem;">
            {ticker} &nbsp;·&nbsp; {info.get('sector','N/A')} &nbsp;·&nbsp; {info.get('industry','N/A')}
            {f"&nbsp;·&nbsp; <a href='{info.get('website')}' style='color:#4da6ff;'>Website ↗</a>" if info.get('website') else ""}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Metrics grid ──────────────────────────────────────────────────────────
    st.markdown("### KEY METRICS")

    def fmt(val, fmt_type="num"):
        if val is None: return "N/A"
        if fmt_type == "pct": return f"{val*100:.1f}%"
        if fmt_type == "ratio": return f"{val:.2f}x"
        if fmt_type == "large":
            if val >= 1e12: return f"${val/1e12:.2f}T"
            if val >= 1e9:  return f"${val/1e9:.2f}B"
            if val >= 1e6:  return f"${val/1e6:.2f}M"
            return f"${val:,.0f}"
        return f"{val:.2f}"

    cols = st.columns(4)
    metrics = [
        ("Market Cap",     fmt(info.get("market_cap"), "large"), "neu"),
        ("P/E Ratio",      fmt(info.get("pe_ratio"),   "ratio"), "neu"),
        ("Fwd P/E",        fmt(info.get("fwd_pe"),     "ratio"), "neu"),
        ("EPS",            fmt(info.get("eps"),        "num"),   "neu"),
        ("Revenue",        fmt(info.get("revenue"),    "large"), "neu"),
        ("Profit Margin",  fmt(info.get("profit_margin"), "pct"), "pos" if (info.get("profit_margin") or 0) > 0 else "neg"),
        ("ROE",            fmt(info.get("roe"), "pct"),           "pos" if (info.get("roe") or 0) > 0 else "neg"),
        ("Debt/Equity",    fmt(info.get("debt_equity"), "ratio"), "pos" if (info.get("debt_equity") or 999) < 100 else "neg"),
    ]
    for i, (lbl, val, cls) in enumerate(metrics):
        cols[i % 4].markdown(f'<div class="metric-card" style="margin-bottom:0.8rem;"><div class="metric-val {cls}">{val}</div><div class="metric-lbl">{lbl}</div></div>', unsafe_allow_html=True)

    col5, col6, col7, col8 = st.columns(4)
    extra = [
        (col5, "52W High",    f"${info.get('52w_high',0):.2f}" if info.get("52w_high") else "N/A", "neu"),
        (col6, "52W Low",     f"${info.get('52w_low',0):.2f}"  if info.get("52w_low")  else "N/A", "neu"),
        (col7, "Beta",        fmt(info.get("beta"), "num"), "neu"),
        (col8, "Dividend",    fmt(info.get("dividend"), "pct") if info.get("dividend") else "None", "neu"),
    ]
    for col, lbl, val, cls in extra:
        col.markdown(f'<div class="metric-card"><div class="metric-val {cls}">{val}</div><div class="metric-lbl">{lbl}</div></div>', unsafe_allow_html=True)

    # ── Price chart (1 year) ──────────────────────────────────────────────────
    if not df.empty:
        st.markdown("### 1-YEAR PRICE")
        import plotly.graph_objects as go
        from utils.styles import PLOTLY_THEME
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df.index, y=df["Close"], mode="lines", name="Close",
            line=dict(color="#f0b429", width=2),
            fill="tozeroy", fillcolor="rgba(240,180,41,0.04)",
        ))
        fig.update_layout(**PLOTLY_THEME, height=300, xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

    # ── Business summary ──────────────────────────────────────────────────────
    if info.get("summary"):
        with st.expander("📄 BUSINESS SUMMARY"):
            st.markdown(f'<p style="font-size:0.88rem; line-height:1.7; color:#8892a4;">{info["summary"]}</p>', unsafe_allow_html=True)

    # ── News ──────────────────────────────────────────────────────────────────
    if news:
        st.markdown("### RECENT NEWS")
        for item in news[:5]:
            title = item.get("title", "")
            link  = item.get("link",  "#")
            publisher = item.get("publisher", "")
            st.markdown(f"""
            <div style="padding:0.6rem 0; border-bottom:1px solid #1c2333; font-size:0.85rem;">
                <a href="{link}" target="_blank" style="color:#cdd5e0; text-decoration:none;">{title}</a>
                <span style="font-family:'IBM Plex Mono',monospace; font-size:0.65rem; color:#4a5568; margin-left:0.8rem;">{publisher}</span>
            </div>
            """, unsafe_allow_html=True)

    # ── AI Analysis ───────────────────────────────────────────────────────────
    st.markdown("### 🧠 AI ANALYSIS")

    if not model:
        st.warning("Add your Gemini API key to enable AI analysis.")
    else:
        last_bt = st.session_state.get("last_backtest")
        backtest_context = ""
        if last_bt and last_bt.get("ticker") == ticker:
            m = last_bt["metrics"]
            backtest_context = f"""
The user also ran a backtest on this stock:
- Strategy: {last_bt['strategy']}
- Return: {m['total_return']:+.2f}%
- Buy & Hold: {m['bh_return']:+.2f}%
- Max Drawdown: {m['max_drawdown']:.2f}%
- Win Rate: {m['win_rate']:.0f}%
Please reference this backtest in your analysis if relevant.
"""

        prompt = f"""You are a specialized financial analysis AI assistant on a platform called 11%.
You provide sharp, honest, educational analysis. You are NOT a financial advisor and must include a disclaimer.

STOCK: {ticker} — {info.get('name', '')}
SECTOR: {info.get('sector','N/A')} | INDUSTRY: {info.get('industry','N/A')}

KEY METRICS:
- Market Cap: {fmt(info.get('market_cap'),'large')}
- P/E Ratio: {fmt(info.get('pe_ratio'),'ratio')} | Forward P/E: {fmt(info.get('fwd_pe'),'ratio')}
- EPS: {fmt(info.get('eps'))}
- Revenue: {fmt(info.get('revenue'),'large')}
- Profit Margin: {fmt(info.get('profit_margin'),'pct')}
- ROE: {fmt(info.get('roe'),'pct')}
- Debt/Equity: {fmt(info.get('debt_equity'),'ratio')}
- Beta: {fmt(info.get('beta'))}
- 52W High: ${info.get('52w_high','N/A')} | 52W Low: ${info.get('52w_low','N/A')}
- Dividend: {fmt(info.get('dividend'),'pct') if info.get('dividend') else 'None'}

{backtest_context}

USER CONTEXT: {user_context if user_context else 'Not provided.'}

ANALYSIS FOCUS AREAS REQUESTED: {', '.join(focus_options)}

Please provide a thorough analysis covering the requested focus areas. Structure your response clearly.
Be honest — if the stock looks risky or overvalued, say so. Use the metrics to support your points.
Keep it educational and accessible. End with a brief disclaimer."""

        with st.spinner("Gemini is analysing..."):
            try:
                response = model.generate_content(prompt)
                analysis = response.text
                st.markdown(f"""
                <div class="chat-ai" style="border-radius:8px; line-height:1.8; font-size:0.88rem;">
                    <div class="chat-lbl" style="color:#4da6ff; margin-bottom:0.8rem;">🧠 AI ANALYSIS — {ticker}</div>
                    {analysis.replace(chr(10), '<br>')}
                </div>
                """, unsafe_allow_html=True)

                # Save to session for assistant
                st.session_state["last_analysis"] = {"ticker": ticker, "analysis": analysis, "info": info}

            except Exception as e:
                st.error(f"Gemini error: {e}")

else:
    st.markdown('<div class="info-box">← Enter a ticker symbol and hit ANALYSE to get started.</div>', unsafe_allow_html=True)
