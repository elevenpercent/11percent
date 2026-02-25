import streamlit as st

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="BacktestFree",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;600&display=swap');

    :root {
        --bg: #0d0f14;
        --surface: #161920;
        --border: #2a2d38;
        --accent: #00ff88;
        --accent2: #0066ff;
        --text: #e8eaf0;
        --muted: #6b7280;
    }

    html, body, [data-testid="stAppViewContainer"] {
        background-color: var(--bg) !important;
        color: var(--text) !important;
        font-family: 'DM Sans', sans-serif;
    }

    [data-testid="stSidebar"] {
        background-color: var(--surface) !important;
        border-right: 1px solid var(--border);
    }

    h1, h2, h3 { font-family: 'Space Mono', monospace; }

    .stButton > button {
        background: var(--accent);
        color: #000;
        border: none;
        border-radius: 4px;
        font-family: 'Space Mono', monospace;
        font-weight: 700;
        padding: 0.5rem 1.5rem;
        transition: opacity 0.2s;
    }
    .stButton > button:hover { opacity: 0.85; }

    .metric-card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 1.2rem;
        text-align: center;
    }
    .metric-value {
        font-family: 'Space Mono', monospace;
        font-size: 1.8rem;
        font-weight: 700;
    }
    .metric-label {
        color: var(--muted);
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }
    .positive { color: var(--accent); }
    .negative { color: #ff4d6d; }
</style>
""", unsafe_allow_html=True)

# ── Loading spinner on cold start ────────────────────────────────────────────
with st.spinner("🔄 Loading BacktestFree... (first load may take a moment)"):
    import yfinance  # noqa: F401 — pre-import heavy packages so pages load faster
    import plotly    # noqa: F401
    import pandas    # noqa: F401
    import numpy     # noqa: F401

# ── Home page content ─────────────────────────────────────────────────────────
st.markdown("# 📈 BacktestFree")
st.markdown("### A free, open-source backtesting platform for everyone.")

st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-value positive">🔬</div>
        <div style="margin-top:0.5rem; font-size:1.1rem; font-weight:600;">Backtest</div>
        <div class="metric-label" style="margin-top:0.3rem;">Test strategies on historical data</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-value" style="color:#0066ff;">🤖</div>
        <div style="margin-top:0.5rem; font-size:1.1rem; font-weight:600;">AI Assistant</div>
        <div class="metric-label" style="margin-top:0.3rem;">Get help from Gemini AI</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-value" style="color:#ffd700;">📚</div>
        <div style="margin-top:0.5rem; font-size:1.1rem; font-weight:600;">Learn</div>
        <div class="metric-label" style="margin-top:0.3rem;">Understand trading strategies</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.markdown("""
**How to use:**
1. Go to **Backtest** in the sidebar → pick a stock, strategy, and date range
2. Hit **Run Backtest** and see your results instantly
3. Ask the **AI Assistant** to explain results or suggest improvements
4. Visit **Learn** to understand how each strategy works
""")

st.markdown("""
<div style="color:#6b7280; font-size:0.8rem; margin-top:2rem;">
⚠️ This platform is for educational purposes only. Nothing here is financial advice.
</div>
""", unsafe_allow_html=True)
