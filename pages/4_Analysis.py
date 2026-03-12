import streamlit as st
import sys, os
import pandas as pd
import plotly.graph_objects as go
from datetime import date, timedelta

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.styles import SHARED_CSS, PLOTLY_THEME
from utils.nav import navbar
from utils.data import get_stock_data, get_ticker_info, get_news

st.set_page_config(page_title="Analysis | 11%", layout="wide", initial_sidebar_state="collapsed")
st.markdown(SHARED_CSS, unsafe_allow_html=True)
navbar()

st.markdown("""
<div class="page-header">
    <div class="page-header-eyebrow">AI-Powered Research</div>
    <h1>Stock Analysis</h1>
    <p>Fundamentals, price action, recent news, and a Gemini-powered deep-dive — all in one place.</p>
</div>
""", unsafe_allow_html=True)

# ── Input row
col_t, col_f, col_a = st.columns([2, 2, 1])
with col_t:
    ticker = st.text_input("Ticker", value="AAPL", key="an_ticker").upper().strip()
with col_f:
    focus = st.selectbox("AI Focus", [
        "Full Overview", "Bull vs Bear Case", "Technical Setup",
        "Risk Factors", "Earnings & Growth", "Competitive Moat"
    ], key="an_focus")
with col_a:
    st.markdown("<div style='height:1.75rem'></div>", unsafe_allow_html=True)
    run_btn = st.button("Analyze", type="primary", use_container_width=True)

user_ctx = st.text_area("Add context (optional)", placeholder="e.g. I'm a long-term investor considering entry...", key="an_ctx", height=60)

if not ticker:
    st.stop()

# ── Load data
with st.spinner(f"Loading {ticker}…"):
    info = get_ticker_info(ticker)
    df   = get_stock_data(ticker, str(date.today()-timedelta(days=365)), str(date.today()))
    news = get_news(ticker)

if df.empty:
    st.error(f"No price data for **{ticker}**.")
    st.stop()

price     = float(df["Close"].iloc[-1])
prev      = float(df["Close"].iloc[-2]) if len(df) > 1 else price
day_chg   = price - prev
day_pct   = day_chg / prev * 100
week_chg  = (price / float(df["Close"].iloc[-5]) - 1) * 100 if len(df) >= 5 else 0
month_chg = (price / float(df["Close"].iloc[-21]) - 1) * 100 if len(df) >= 21 else 0
ytd_chg   = (price / float(df["Close"].iloc[-252]) - 1) * 100 if len(df) >= 252 else 0
high_52   = float(df["High"].max())
low_52    = float(df["Low"].min())
from_52h  = (price / high_52 - 1) * 100
avg_vol   = float(df["Volume"].rolling(20).mean().iloc[-1])

def fmt(v, prefix="$", suffix="", decimals=2):
    if v is None: return "N/A"
    if abs(v) >= 1e12: return f"{prefix}{v/1e12:.{decimals}f}T{suffix}"
    if abs(v) >= 1e9:  return f"{prefix}{v/1e9:.{decimals}f}B{suffix}"
    if abs(v) >= 1e6:  return f"{prefix}{v/1e6:.{decimals}f}M{suffix}"
    return f"{prefix}{v:,.{decimals}f}{suffix}"

# ── Price header
pct_col = "#00e676" if day_pct >= 0 else "#ff3d57"
st.markdown(
    f'<div style="background:#0c1018;border:1px solid #1a2235;border-radius:10px;padding:1.2rem 1.5rem;margin-bottom:1.2rem;display:flex;align-items:center;gap:2rem;flex-wrap:wrap;">'
    f'<div>'
    f'  <div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.58rem;color:#3a4a5e;text-transform:uppercase;letter-spacing:0.18em;">{info.get("name",ticker)}</div>'
    f'  <div style="font-size:2.2rem;font-weight:700;color:#eef2f7;line-height:1.1;">${price:,.2f}</div>'
    f'  <div style="font-size:0.85rem;color:{pct_col};font-family:\'IBM Plex Mono\',monospace;">'
    f'    {"▲" if day_pct>=0 else "▼"} {abs(day_chg):.2f} ({abs(day_pct):.2f}%) today</div>'
    f'</div>'
    f'<div style="display:flex;gap:1.5rem;flex-wrap:wrap;">'
    f'  <div><div style="font-size:0.72rem;color:{"#00e676" if week_chg>=0 else "#ff3d57"};font-weight:600;">{week_chg:+.2f}%</div><div style="font-size:0.6rem;color:#3a4a5e;text-transform:uppercase;letter-spacing:0.12em;">1 Week</div></div>'
    f'  <div><div style="font-size:0.72rem;color:{"#00e676" if month_chg>=0 else "#ff3d57"};font-weight:600;">{month_chg:+.2f}%</div><div style="font-size:0.6rem;color:#3a4a5e;text-transform:uppercase;letter-spacing:0.12em;">1 Month</div></div>'
    f'  <div><div style="font-size:0.72rem;color:{"#00e676" if ytd_chg>=0 else "#ff3d57"};font-weight:600;">{ytd_chg:+.2f}%</div><div style="font-size:0.6rem;color:#3a4a5e;text-transform:uppercase;letter-spacing:0.12em;">1 Year</div></div>'
    f'  <div><div style="font-size:0.72rem;color:#eef2f7;font-weight:600;">${high_52:,.2f}</div><div style="font-size:0.6rem;color:#3a4a5e;text-transform:uppercase;letter-spacing:0.12em;">52W High</div></div>'
    f'  <div><div style="font-size:0.72rem;color:#eef2f7;font-weight:600;">${low_52:,.2f}</div><div style="font-size:0.6rem;color:#3a4a5e;text-transform:uppercase;letter-spacing:0.12em;">52W Low</div></div>'
    f'  <div><div style="font-size:0.72rem;color:{"#ff3d57" if from_52h<-20 else "#ffd166" if from_52h<-10 else "#8896ab"};font-weight:600;">{from_52h:+.1f}%</div><div style="font-size:0.6rem;color:#3a4a5e;text-transform:uppercase;letter-spacing:0.12em;">From 52W Hi</div></div>'
    f'</div>'
    f'</div>',
    unsafe_allow_html=True
)

# ── Chart + fundamentals
chart_col, fund_col = st.columns([3, 2])

with chart_col:
    fig = go.Figure()
    ma20 = df["Close"].rolling(20).mean()
    ma50 = df["Close"].rolling(50).mean()
    # Price area
    fig.add_trace(go.Scatter(
        x=df.index, y=df["Close"], name="Price",
        line=dict(color="#4da6ff", width=2),
        fill="tozeroy", fillcolor="rgba(77,166,255,0.04)"
    ))
    fig.add_trace(go.Scatter(x=df.index, y=ma20, name="MA 20",
                              line=dict(color="#00e676", width=1.2, dash="dot")))
    fig.add_trace(go.Scatter(x=df.index, y=ma50, name="MA 50",
                              line=dict(color="#ffd166", width=1.2, dash="dash")))
    fig.update_layout(
        **PLOTLY_THEME, height=300,
        legend=dict(orientation="h", y=1.02, x=0),
        title=f"{ticker} — 1 Year Price"
    )
    st.plotly_chart(fig, use_container_width=True)

with fund_col:
    st.markdown('<div class="section-hdr">Fundamentals</div>', unsafe_allow_html=True)
    rows = [
        ("Sector",        info.get("sector", "N/A")),
        ("Industry",      info.get("industry", "N/A")),
        ("Market Cap",    fmt(info.get("market_cap"), "$")),
        ("P/E (TTM)",     f'{info["pe_ratio"]:.1f}x' if info.get("pe_ratio") else "N/A"),
        ("Fwd P/E",       f'{info["fwd_pe"]:.1f}x'   if info.get("fwd_pe")   else "N/A"),
        ("EPS",           f'${info["eps"]:.2f}'       if info.get("eps")      else "N/A"),
        ("Revenue",       fmt(info.get("revenue"), "$")),
        ("Profit Margin", f'{info["profit_margin"]*100:.1f}%' if info.get("profit_margin") else "N/A"),
        ("Debt/Equity",   f'{info["debt_equity"]:.2f}' if info.get("debt_equity") else "N/A"),
        ("ROE",           f'{info["roe"]*100:.1f}%'   if info.get("roe")     else "N/A"),
        ("Beta",          f'{info["beta"]:.2f}'       if info.get("beta")    else "N/A"),
        ("Dividend",      f'{info["dividend"]*100:.2f}%' if info.get("dividend") else "N/A"),
        ("Avg Volume",    fmt(info.get("avg_volume"), "", suffix=" sh", decimals=1)),
    ]
    for label, val in rows:
        st.markdown(
            f'<div class="row-item"><span style="color:#3a4a5e;font-size:0.78rem;">{label}</span>'
            f'<span style="color:#eef2f7;font-size:0.8rem;font-weight:500;">{val}</span></div>',
            unsafe_allow_html=True
        )

# ── News section
st.markdown('<div class="section-hdr" style="margin-top:1.5rem;">Recent News</div>', unsafe_allow_html=True)

if not news:
    st.markdown('<div class="info-box">No recent news found for this ticker.</div>', unsafe_allow_html=True)
else:
    news_cols = st.columns(2)
    for i, article in enumerate(news[:6]):
        # yfinance news items can be dicts with varying structure
        title     = ""
        url       = "#"
        publisher = ""
        pub_time  = ""

        if isinstance(article, dict):
            # New yfinance format: article has 'content' sub-dict
            content = article.get("content", article)
            if isinstance(content, dict):
                title     = content.get("title", article.get("title", ""))
                url       = (content.get("canonicalUrl", {}) or {}).get("url", "")
                if not url:
                    url   = content.get("clickThroughUrl", {}).get("url", "#") if content.get("clickThroughUrl") else "#"
                publisher = (content.get("provider", {}) or {}).get("displayName", "")
                raw_date  = content.get("pubDate", "") or content.get("displayTime", "")
            else:
                title     = article.get("title", "")
                url       = article.get("link", article.get("url", "#"))
                publisher = article.get("publisher", "")
                raw_date  = str(article.get("providerPublishTime", ""))

        if not title:
            continue

        # Format timestamp
        try:
            import datetime as dt_lib
            if raw_date and raw_date.isdigit():
                pub_time = dt_lib.datetime.fromtimestamp(int(raw_date)).strftime("%b %d")
            elif raw_date:
                pub_time = raw_date[:10]
        except Exception:
            pub_time = ""

        with news_cols[i % 2]:
            st.markdown(
                f'<a href="{url}" target="_blank" style="text-decoration:none;">'
                f'<div style="background:#0c1018;border:1px solid #1a2235;border-radius:8px;padding:0.85rem 1rem;margin-bottom:0.6rem;transition:border-color 0.15s;" '
                f'onmouseover="this.style.borderColor=\'#2a3550\'" onmouseout="this.style.borderColor=\'#1a2235\'">'
                f'<div style="font-size:0.82rem;color:#eef2f7;font-weight:500;line-height:1.45;margin-bottom:0.4rem;">{title}</div>'
                f'<div style="display:flex;justify-content:space-between;align-items:center;">'
                f'  <span style="font-size:0.65rem;color:#3a4a5e;font-family:\'IBM Plex Mono\',monospace;">{publisher}</span>'
                f'  <span style="font-size:0.65rem;color:#3a4a5e;font-family:\'IBM Plex Mono\',monospace;">{pub_time}</span>'
                f'</div></div></a>',
                unsafe_allow_html=True
            )

# ── AI Analysis
st.markdown('<div class="section-hdr" style="margin-top:1.5rem;">AI Analysis</div>', unsafe_allow_html=True)

ANALYSIS_PROMPT = """You are a professional equity analyst. Analyze {ticker} with focus: {focus}.

Stock data:
- Price: ${price:.2f} | Day: {day_pct:+.2f}% | 1Y: {ytd_chg:+.2f}%
- 52W Range: ${low_52:.2f} – ${high_52:.2f} (currently {from_52h:+.1f}% from high)
- Market Cap: {market_cap} | P/E: {pe} | Fwd P/E: {fwd_pe}
- Revenue: {revenue} | Profit Margin: {margin}
- Beta: {beta} | Sector: {sector}

Recent headlines:
{headlines}

{user_ctx}

Respond in this EXACT structured format with clear section headers:

## 📊 SNAPSHOT
One sentence current situation.

## 🎯 KEY THESIS
2-3 bullet points of the core investment thesis.

## ✅ BULL CASE
3 specific bullish catalysts or strengths.

## ⚠️ BEAR CASE  
3 specific risks or headwinds.

## 📈 TECHNICAL PICTURE
Brief comment on price action, trend, and key levels.

## 🏁 BOTTOM LINE
One clear, direct concluding sentence with a view.

Keep each section concise. Use specific numbers. No generic filler.
"""

headlines_str = "\n".join(
    f"- {(a.get('content', a) if isinstance(a.get('content'), dict) else a).get('title', '')}"
    for a in news[:5]
    if (a.get('content', a) if isinstance(a.get('content'), dict) else a).get('title')
) or "No recent news available."

prompt = ANALYSIS_PROMPT.format(
    ticker=ticker, focus=focus,
    price=price, day_pct=day_pct, ytd_chg=ytd_chg,
    low_52=low_52, high_52=high_52, from_52h=from_52h,
    market_cap=fmt(info.get("market_cap"), "$"),
    pe=f'{info["pe_ratio"]:.1f}x' if info.get("pe_ratio") else "N/A",
    fwd_pe=f'{info["fwd_pe"]:.1f}x' if info.get("fwd_pe") else "N/A",
    revenue=fmt(info.get("revenue"), "$"),
    margin=f'{info["profit_margin"]*100:.1f}%' if info.get("profit_margin") else "N/A",
    beta=f'{info["beta"]:.2f}' if info.get("beta") else "N/A",
    sector=info.get("sector", "N/A"),
    headlines=headlines_str,
    user_ctx=f"User context: {user_ctx}" if user_ctx else ""
)

if run_btn:
    try:
        import google.generativeai as genai
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel("gemini-2.5-flash")

        with st.spinner("Gemini is analyzing…"):
            response = model.generate_content(prompt)
            analysis_text = response.text

        st.session_state["last_analysis"] = {
            "ticker": ticker, "text": analysis_text, "focus": focus
        }
        _render_analysis(analysis_text, ticker, focus)

    except Exception as e:
        st.error(f"AI analysis error: {e}")

elif "last_analysis" in st.session_state and st.session_state["last_analysis"].get("ticker") == ticker:
    st.caption("Showing cached analysis — click Analyze to refresh.")
    _render_analysis(st.session_state["last_analysis"]["text"], ticker,
                     st.session_state["last_analysis"].get("focus", ""))
else:
    st.markdown(
        '<div style="background:#0c1018;border:1px dashed #1a2235;border-radius:10px;'
        'padding:2.5rem;text-align:center;color:#3a4a5e;font-size:0.82rem;">'
        'Click <strong style="color:#8896ab;">Analyze</strong> to generate an AI-powered deep-dive on this stock.'
        '</div>',
        unsafe_allow_html=True
    )


def _render_analysis(text, ticker, focus):
    """Render AI analysis in a clean, organized card layout."""
    import re

    # Parse sections by ## headers
    sections = re.split(r'\n##\s+', text.strip())
    parsed = {}
    for s in sections:
        if not s.strip():
            continue
        lines = s.strip().split('\n', 1)
        header = lines[0].strip().lstrip('#').strip()
        body   = lines[1].strip() if len(lines) > 1 else ""
        parsed[header] = body

    # Header card
    st.markdown(
        f'<div style="background:linear-gradient(135deg,rgba(0,230,118,0.06),rgba(77,166,255,0.04));'
        f'border:1px solid rgba(0,230,118,0.2);border-radius:12px;padding:1.2rem 1.5rem;margin-bottom:1rem;">'
        f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.58rem;color:#00e676;'
        f'text-transform:uppercase;letter-spacing:0.18em;margin-bottom:0.3rem;">'
        f'Gemini Analysis · {focus}</div>'
        f'<div style="font-size:1rem;color:#eef2f7;font-weight:600;">{ticker}</div>'
        f'</div>',
        unsafe_allow_html=True
    )

    # Section cards in a grid
    section_order = [
        ("📊 SNAPSHOT",        "#4da6ff", 1),
        ("🎯 KEY THESIS",      "#b388ff", 2),
        ("✅ BULL CASE",       "#00e676", 2),
        ("⚠️ BEAR CASE",       "#ff3d57", 2),
        ("📈 TECHNICAL PICTURE","#ffd166", 2),
        ("🏁 BOTTOM LINE",     "#00e676", 1),
    ]

    # Snapshot — full width
    for sec_name, accent, _ in section_order:
        body = None
        # Try exact match, then partial match
        for k in parsed:
            if sec_name.upper() in k.upper() or k.upper() in sec_name.upper():
                body = parsed[k]
                break
        if body is None:
            continue

        # Convert markdown-ish bullets to HTML
        html_body = _md_to_html(body, accent)

        st.markdown(
            f'<div style="background:#0c1018;border:1px solid #1a2235;border-left:3px solid {accent};'
            f'border-radius:0 10px 10px 0;padding:1rem 1.2rem;margin-bottom:0.7rem;">'
            f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.58rem;color:{accent};'
            f'text-transform:uppercase;letter-spacing:0.18em;margin-bottom:0.6rem;">{sec_name}</div>'
            f'<div style="font-size:0.84rem;color:#8896ab;line-height:1.7;">{html_body}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    # If no sections parsed, fallback to raw markdown
    if not parsed:
        st.markdown(text)


def _md_to_html(text, accent):
    """Convert basic markdown bullets/bold to clean HTML."""
    import re
    lines = text.split('\n')
    out = []
    in_list = False
    for line in lines:
        line = line.strip()
        if not line:
            if in_list:
                out.append('</ul>')
                in_list = False
            continue
        # Bold
        line = re.sub(r'\*\*(.+?)\*\*', r'<strong style="color:#eef2f7;">\1</strong>', line)
        # Bullet
        if line.startswith(('- ', '• ', '* ')):
            if not in_list:
                out.append(f'<ul style="margin:0.3rem 0;padding-left:1.2rem;">')
                in_list = True
            item = line[2:].strip()
            out.append(f'<li style="margin-bottom:0.25rem;">{item}</li>')
        else:
            if in_list:
                out.append('</ul>')
                in_list = False
            out.append(f'<p style="margin:0.2rem 0;">{line}</p>')
    if in_list:
        out.append('</ul>')
    return ''.join(out)
