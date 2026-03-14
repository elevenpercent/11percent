import streamlit as st
import sys, os
import re
import pandas as pd
import plotly.graph_objects as go
from datetime import date, timedelta

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.styles import SHARED_CSS, inject_bg, PLOTLY_THEME
from utils.nav import navbar
from utils.data import get_stock_data, get_ticker_info, get_news

st.set_page_config(page_title="Analysis | 11%", layout="wide", initial_sidebar_state="collapsed")
st.markdown(SHARED_CSS, unsafe_allow_html=True)
navbar()
inject_bg()

# ══════════════════════════════════════════════════════════
# Helper functions — defined FIRST before any calls
# ══════════════════════════════════════════════════════════

def _inline_md(text):
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong style="color:#eef2f7;">\1</strong>', text)
    text = re.sub(r'\*(.+?)\*',     r'<em style="color:#eef2f7;">\1</em>', text)
    text = re.sub(r'`(.+?)`',       r'<code style="background:rgba(0,0,0,0.4);border:1px solid #1a2235;border-radius:3px;padding:1px 5px;font-family:IBM Plex Mono,monospace;font-size:0.78rem;color:#4da6ff;">\1</code>', text)
    return text

def _section_body_html(text):
    lines = text.split('\n')
    out   = []
    in_ul = False
    for line in lines:
        line = line.strip()
        if not line:
            if in_ul: out.append('</ul>'); in_ul = False
            continue
        line = _inline_md(line)
        if line.startswith(('- ', '• ', '* ')):
            if not in_ul: out.append('<ul style="margin:0.3rem 0;padding-left:1.2rem;">'); in_ul = True
            out.append(f'<li style="margin-bottom:0.25rem;">{line[2:].strip()}</li>')
        else:
            if in_ul: out.append('</ul>'); in_ul = False
            out.append(f'<p style="margin:0.2rem 0;">{line}</p>')
    if in_ul: out.append('</ul>')
    return ''.join(out)

def render_analysis(text, ticker, focus):
    """Render AI analysis in organized section cards."""
    sections = re.split(r'\n##\s+', '\n' + text.strip())
    sections = [s for s in sections if s.strip()]

    # Header banner
    st.markdown(
        f'<div style="background:linear-gradient(135deg,rgba(0,230,118,0.06),rgba(77,166,255,0.04));'
        f'border:1px solid rgba(0,230,118,0.2);border-radius:12px;padding:1rem 1.4rem;margin-bottom:1rem;">'
        f'<div style="font-family:IBM Plex Mono,monospace;font-size:0.58rem;color:#00e676;'
        f'text-transform:uppercase;letter-spacing:0.18em;margin-bottom:0.2rem;">Gemini Analysis · {focus}</div>'
        f'<div style="font-size:1rem;color:#eef2f7;font-weight:600;">{ticker}</div>'
        f'</div>',
        unsafe_allow_html=True
    )

    ACCENT_MAP = {
        "snapshot": "#4da6ff", "overview": "#4da6ff",
        "bull": "#00e676", "thesis": "#00e676", "why": "#00e676",
        "bear": "#ff3d57", "risk": "#ff3d57", "concern": "#ff3d57",
        "technical": "#ffd166", "chart": "#ffd166", "price": "#ffd166",
        "bottom": "#b388ff", "takeaway": "#b388ff", "conclusion": "#b388ff",
    }

    if not sections or len(sections) <= 1:
        # No structured sections — render as plain formatted text
        st.markdown(
            '<div style="background:#0c1018;border:1px solid #1a2235;border-radius:10px;padding:1.2rem;">'
            + _section_body_html(text) +
            '</div>',
            unsafe_allow_html=True
        )
        return

    for sec in sections:
        lines  = sec.strip().split('\n', 1)
        header = lines[0].strip().lstrip('#').strip()
        body   = lines[1].strip() if len(lines) > 1 else ""

        accent = "#8896ab"
        for kw, col in ACCENT_MAP.items():
            if kw in header.lower():
                accent = col
                break

        st.markdown(
            f'<div style="background:#0c1018;border:1px solid #1a2235;border-left:3px solid {accent};'
            f'border-radius:0 10px 10px 0;padding:1rem 1.2rem;margin-bottom:0.7rem;">'
            f'<div style="font-family:IBM Plex Mono,monospace;font-size:0.58rem;color:{accent};'
            f'text-transform:uppercase;letter-spacing:0.18em;margin-bottom:0.5rem;">{header}</div>'
            f'<div style="font-size:0.84rem;color:#8896ab;line-height:1.7;">'
            + _section_body_html(body) +
            f'</div></div>',
            unsafe_allow_html=True
        )


def fmt(v, prefix="$", suffix="", decimals=2):
    if v is None: return "N/A"
    try:
        v = float(v)
        if abs(v) >= 1e12: return f"{prefix}{v/1e12:.{decimals}f}T{suffix}"
        if abs(v) >= 1e9:  return f"{prefix}{v/1e9:.{decimals}f}B{suffix}"
        if abs(v) >= 1e6:  return f"{prefix}{v/1e6:.{decimals}f}M{suffix}"
        return f"{prefix}{v:,.{decimals}f}{suffix}"
    except Exception:
        return "N/A"


# ══════════════════════════════════════════════════════════
# Page UI
# ══════════════════════════════════════════════════════════

st.markdown("""
<div class="page-header">
    <div class="page-header-eyebrow">AI-Powered Research</div>
    <h1>Stock Analysis</h1>
    <p>Fundamentals, price action, recent news, and a Gemini-powered deep-dive — all in one place.</p>
</div>
""", unsafe_allow_html=True)

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

user_ctx = st.text_area(
    "Add context (optional)",
    placeholder="e.g. I'm a long-term investor considering entry around current levels...",
    key="an_ctx", height=60
)

if not ticker:
    st.stop()

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
week_chg  = (price / float(df["Close"].iloc[-5])  - 1) * 100 if len(df) >= 5  else 0
month_chg = (price / float(df["Close"].iloc[-21]) - 1) * 100 if len(df) >= 21 else 0
ytd_chg   = (price / float(df["Close"].iloc[-252])- 1) * 100 if len(df) >= 252 else 0
high_52   = float(df["High"].max())
low_52    = float(df["Low"].min())
from_52h  = (price / high_52 - 1) * 100

# ── Price header
pct_col = "#00e676" if day_pct >= 0 else "#ff3d57"
st.markdown(
    f'<div style="background:#0c1018;border:1px solid #1a2235;border-radius:10px;padding:1.2rem 1.5rem;'
    f'margin-bottom:1.2rem;display:flex;align-items:center;gap:2.5rem;flex-wrap:wrap;">'
    f'<div>'
    f'  <div style="font-family:IBM Plex Mono,monospace;font-size:0.58rem;color:#3a4a5e;text-transform:uppercase;letter-spacing:0.18em;">{info.get("name",ticker)}</div>'
    f'  <div style="font-size:2.2rem;font-weight:700;color:#eef2f7;line-height:1.15;">${price:,.2f}</div>'
    f'  <div style="font-size:0.85rem;color:{pct_col};font-family:IBM Plex Mono,monospace;">{"▲" if day_pct>=0 else "▼"} {abs(day_chg):.2f} ({abs(day_pct):.2f}%) today</div>'
    f'</div>'
    f'<div style="display:flex;gap:2rem;flex-wrap:wrap;">'
    + "".join([
        f'<div><div style="font-size:0.78rem;color:{"#00e676" if v>=0 else "#ff3d57"};font-weight:600;">{v:+.2f}%</div><div style="font-size:0.6rem;color:#3a4a5e;text-transform:uppercase;letter-spacing:0.12em;">{lbl}</div></div>'
        for v, lbl in [(week_chg,"1 Week"),(month_chg,"1 Month"),(ytd_chg,"1 Year")]
    ]) +
    f'<div><div style="font-size:0.78rem;color:#eef2f7;font-weight:600;">${high_52:,.2f}</div><div style="font-size:0.6rem;color:#3a4a5e;text-transform:uppercase;letter-spacing:0.12em;">52W High</div></div>'
    f'<div><div style="font-size:0.78rem;color:#eef2f7;font-weight:600;">${low_52:,.2f}</div><div style="font-size:0.6rem;color:#3a4a5e;text-transform:uppercase;letter-spacing:0.12em;">52W Low</div></div>'
    f'<div><div style="font-size:0.78rem;color:{"#ff3d57" if from_52h<-20 else "#ffd166" if from_52h<-10 else "#8896ab"};font-weight:600;">{from_52h:+.1f}%</div><div style="font-size:0.6rem;color:#3a4a5e;text-transform:uppercase;letter-spacing:0.12em;">From 52W Hi</div></div>'
    f'</div></div>',
    unsafe_allow_html=True
)

# ── Chart + fundamentals
chart_col, fund_col = st.columns([3, 2])

with chart_col:
    ma20 = df["Close"].rolling(20).mean()
    ma50 = df["Close"].rolling(50).mean()
    fig  = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["Close"], name="Price",
                              line=dict(color="#4da6ff", width=2),
                              fill="tozeroy", fillcolor="rgba(77,166,255,0.04)"))
    fig.add_trace(go.Scatter(x=df.index, y=ma20, name="MA 20",
                              line=dict(color="#00e676", width=1.2, dash="dot")))
    fig.add_trace(go.Scatter(x=df.index, y=ma50, name="MA 50",
                              line=dict(color="#ffd166", width=1.2, dash="dash")))
    fig.update_layout(**PLOTLY_THEME, height=300,
                      legend=dict(orientation="h", y=1.02, x=0),
                      title=f"{ticker} — 1 Year Price")
    st.plotly_chart(fig, use_container_width=True)

with fund_col:
    st.markdown('<div class="section-hdr">Fundamentals</div>', unsafe_allow_html=True)
    rows = [
        ("Sector",        info.get("sector", "N/A")),
        ("Industry",      info.get("industry", "N/A")),
        ("Market Cap",    fmt(info.get("market_cap"))),
        ("P/E (TTM)",     f'{info["pe_ratio"]:.1f}×' if info.get("pe_ratio") else "N/A"),
        ("Fwd P/E",       f'{info["fwd_pe"]:.1f}×'   if info.get("fwd_pe")   else "N/A"),
        ("EPS",           f'${info["eps"]:.2f}'       if info.get("eps")      else "N/A"),
        ("Revenue",       fmt(info.get("revenue"))),
        ("Profit Margin", f'{info["profit_margin"]*100:.1f}%' if info.get("profit_margin") else "N/A"),
        ("ROE",           f'{info["roe"]*100:.1f}%'   if info.get("roe")     else "N/A"),
        ("Beta",          f'{info["beta"]:.2f}'       if info.get("beta")    else "N/A"),
        ("Dividend",      f'{info["dividend"]*100:.2f}%' if info.get("dividend") else "N/A"),
        ("52W Range",     f'${low_52:,.2f} – ${high_52:,.2f}'),
    ]
    for label, val in rows:
        st.markdown(
            f'<div class="row-item">'
            f'<span style="color:#3a4a5e;font-size:0.78rem;">{label}</span>'
            f'<span style="color:#eef2f7;font-size:0.8rem;font-weight:500;">{val}</span>'
            f'</div>',
            unsafe_allow_html=True
        )

# ── News
st.markdown('<div class="section-hdr" style="margin-top:1.5rem;">Recent News</div>', unsafe_allow_html=True)

def extract_article(raw):
    """Handle both old and new yfinance news formats."""
    if not isinstance(raw, dict):
        return None
    # New format: raw = { "content": { "title":..., "canonicalUrl":..., ... } }
    content = raw.get("content", raw)
    if isinstance(content, dict):
        title = content.get("title", raw.get("title", ""))
        # URL: try canonicalUrl, then clickThroughUrl, then link
        url = ""
        if isinstance(content.get("canonicalUrl"), dict):
            url = content["canonicalUrl"].get("url", "")
        if not url and isinstance(content.get("clickThroughUrl"), dict):
            url = content["clickThroughUrl"].get("url", "")
        if not url:
            url = raw.get("link", raw.get("url", "#"))
        publisher = ""
        if isinstance(content.get("provider"), dict):
            publisher = content["provider"].get("displayName", "")
        if not publisher:
            publisher = raw.get("publisher", "")
        pub_date = content.get("pubDate", content.get("displayTime", ""))
        if not pub_date:
            pub_date = str(raw.get("providerPublishTime", ""))
    else:
        title     = raw.get("title", "")
        url       = raw.get("link", raw.get("url", "#"))
        publisher = raw.get("publisher", "")
        pub_date  = str(raw.get("providerPublishTime", ""))

    if not title:
        return None

    # Format date
    pub_str = ""
    try:
        import datetime as dt_lib
        if pub_date and str(pub_date).isdigit():
            pub_str = dt_lib.datetime.fromtimestamp(int(pub_date)).strftime("%b %d")
        elif pub_date:
            pub_str = str(pub_date)[:10]
    except Exception:
        pass

    return {"title": title, "url": url or "#", "publisher": publisher, "date": pub_str}

articles = [a for raw in (news or []) if (a := extract_article(raw)) is not None][:6]

if not articles:
    st.markdown('<div class="info-box">No recent news articles found for this ticker.</div>', unsafe_allow_html=True)
else:
    nc1, nc2 = st.columns(2)
    for i, a in enumerate(articles):
        with (nc1 if i % 2 == 0 else nc2):
            st.markdown(
                f'<a href="{a["url"]}" target="_blank" style="text-decoration:none;">'
                f'<div style="background:#0c1018;border:1px solid #1a2235;border-radius:8px;'
                f'padding:0.85rem 1rem;margin-bottom:0.6rem;transition:border-color 0.15s;"'
                f' onmouseover="this.style.borderColor=\'#2a3550\'" onmouseout="this.style.borderColor=\'#1a2235\'">'
                f'<div style="font-size:0.82rem;color:#eef2f7;font-weight:500;line-height:1.45;margin-bottom:0.4rem;">{a["title"]}</div>'
                f'<div style="display:flex;justify-content:space-between;">'
                f'  <span style="font-size:0.65rem;color:#3a4a5e;font-family:IBM Plex Mono,monospace;">{a["publisher"]}</span>'
                f'  <span style="font-size:0.65rem;color:#3a4a5e;font-family:IBM Plex Mono,monospace;">{a["date"]}</span>'
                f'</div></div></a>',
                unsafe_allow_html=True
            )

# ── AI Analysis
st.markdown('<div class="section-hdr" style="margin-top:1.5rem;">AI Analysis</div>', unsafe_allow_html=True)

headlines_str = "\n".join(f"- {a['title']}" for a in articles[:5]) or "No recent news."

PROMPT = f"""You are a professional equity analyst. Analyze {ticker} with focus: {focus}.

Stock data:
- Price: ${price:.2f} | Day: {day_pct:+.2f}% | 1Y: {ytd_chg:+.2f}%
- 52W Range: ${low_52:.2f} – ${high_52:.2f} (currently {from_52h:+.1f}% from high)
- Market Cap: {fmt(info.get('market_cap'))} | P/E: {f'{info["pe_ratio"]:.1f}×' if info.get('pe_ratio') else 'N/A'} | Fwd P/E: {f'{info["fwd_pe"]:.1f}×' if info.get('fwd_pe') else 'N/A'}
- Revenue: {fmt(info.get('revenue'))} | Margin: {f'{info["profit_margin"]*100:.1f}%' if info.get('profit_margin') else 'N/A'}
- Beta: {f'{info["beta"]:.2f}' if info.get('beta') else 'N/A'} | Sector: {info.get('sector','N/A')}

Recent headlines:
{headlines_str}

{"User context: " + user_ctx if user_ctx else ""}

Respond using this EXACT structure with ## headers:

## 📊 SNAPSHOT
One sentence on the current situation.

## 🎯 KEY THESIS
2-3 bullets on the core investment thesis.

## ✅ BULL CASE
3 specific bullish catalysts with data points.

## ⚠️ BEAR CASE
3 specific risks or headwinds with data points.

## 📈 TECHNICAL PICTURE
Comment on trend, key levels, and price action.

## 🏁 BOTTOM LINE
One direct concluding sentence with a clear view.

Be specific with numbers. No generic filler. Keep each section tight.
"""

if run_btn:
    try:
        import google.generativeai as genai
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel("gemini-2.5-flash")
        with st.spinner("Gemini is analyzing…"):
            resp = model.generate_content(PROMPT)
            analysis_text = resp.text
        st.session_state["last_analysis"] = {
            "ticker": ticker, "text": analysis_text, "focus": focus
        }
        render_analysis(analysis_text, ticker, focus)

    except Exception as e:
        st.error(f"AI analysis error: {e}")

elif "last_analysis" in st.session_state and st.session_state["last_analysis"].get("ticker") == ticker:
    st.caption("Showing cached analysis — click Analyze to refresh.")
    render_analysis(
        st.session_state["last_analysis"]["text"],
        ticker,
        st.session_state["last_analysis"].get("focus", "")
    )
else:
    st.markdown(
        '<div style="background:#0c1018;border:1px dashed #1a2235;border-radius:10px;'
        'padding:3rem;text-align:center;color:#3a4a5e;font-size:0.82rem;">'
        'Click <strong style="color:#8896ab;">Analyze</strong> to generate an AI-powered deep-dive on this stock.'
        '</div>',
        unsafe_allow_html=True
    )
