import streamlit as st
import yfinance, plotly, pandas, numpy  # pre-import heavy deps for faster page loads

st.set_page_config(
    page_title="11% — Trading Platform",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

from utils.styles import SHARED_CSS
st.markdown(SHARED_CSS, unsafe_allow_html=True)

# ── Sidebar branding ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding: 1rem 0 1.5rem 0; border-bottom: 1px solid #1c2333;">
        <div style="font-family:'Bebas Neue',sans-serif; font-size:2rem; letter-spacing:0.1em; color:#f0b429;">11%</div>
        <div style="font-family:'IBM Plex Mono',monospace; font-size:0.65rem; color:#4a5568; text-transform:uppercase; letter-spacing:0.15em;">Trading Platform</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div style="padding-top:1rem; font-family:'IBM Plex Mono',monospace; font-size:0.72rem; color:#4a5568;">
    NAVIGATE<br>
    </div>
    """, unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="padding: 3rem 0 2rem 0;">
    <div style="font-family:'IBM Plex Mono',monospace; font-size:0.75rem; color:#f0b429; text-transform:uppercase; letter-spacing:0.2em; margin-bottom:0.5rem;">
        Free · Open Source · No Paywalls
    </div>
    <h1 style="font-size:4.5rem !important; line-height:1 !important; margin:0;">
        BACKTEST.<br>ANALYZE.<br>MASTER.
    </h1>
    <p style="color:#4a5568; font-size:1rem; margin-top:1rem; max-width:500px;">
        A professional-grade trading platform built for everyone.
        Test strategies, study indicators, replay charts, and get AI-powered analysis — all free.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ── Feature cards ─────────────────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)

cards = [
    ("🔬", "Backtest", "1_Backtest", "Test pre-built strategies on historical data with full performance metrics."),
    ("📊", "Indicators", "2_Indicator_Test", "Test single or combo indicators with custom buy/sell conditions."),
    ("▶", "Replay", "3_Replay", "Replay any chart bar by bar. Practice your entries and exits."),
    ("🧠", "Analysis", "4_Analysis", "AI-powered stock analysis. Fundamentals, risk, and AI insights."),
    ("💬", "Assistant", "5_Assistant", "Your personal AI trading coach. Ask anything, anytime."),
]

for col, (icon, title, page, desc) in zip([c1, c2, c3, c4, c5], cards):
    with col:
        st.markdown(f"""
        <div class="metric-card" style="cursor:pointer; min-height:160px; text-align:left; padding:1.2rem;">
            <div style="font-size:1.6rem; margin-bottom:0.6rem;">{icon}</div>
            <div style="font-family:'IBM Plex Mono',monospace; font-size:0.8rem; font-weight:600;
                        color:#f0b429; text-transform:uppercase; letter-spacing:0.1em;">{title}</div>
            <div style="font-size:0.78rem; color:#4a5568; margin-top:0.5rem; line-height:1.5;">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# ── Stats row ─────────────────────────────────────────────────────────────────
s1, s2, s3, s4 = st.columns(4)
stats = [
    ("9+", "Indicators"),
    ("100%", "Free Forever"),
    ("5", "Pages / Tools"),
    ("AI", "Powered by Gemini"),
]
for col, (val, lbl) in zip([s1, s2, s3, s4], stats):
    with col:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-val neu">{val}</div>
            <div class="metric-lbl">{lbl}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("---")

# ── Quick start ───────────────────────────────────────────────────────────────
st.markdown("### QUICK START")
st.markdown("""
1. **Backtest** → Pick a stock + strategy → Run Backtest → See your returns
2. **Indicators** → Choose up to 3 indicators → Set your buy/sell conditions → Run
3. **Replay** → Pick a stock and date → Step through candles and practice trading
4. **Analysis** → Enter any ticker → Get AI-generated financial breakdown
5. **Assistant** → Ask anything — strategies, results, or general trading questions
""")

st.markdown("""
<div class="warn-box" style="margin-top:1.5rem;">
⚠️ 11% is for educational purposes only. Nothing on this platform constitutes financial advice.
Past performance does not guarantee future results.
</div>
""", unsafe_allow_html=True)
