import streamlit as st
from utils.styles import SHARED_CSS, LOGO_IMG
from utils.nav import render_navbar


# -------------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------------

st.set_page_config(
    page_title="11%",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# -------------------------------------------------------
# GLOBAL STYLE LOAD
# -------------------------------------------------------

st.markdown(SHARED_CSS, unsafe_allow_html=True)


# -------------------------------------------------------
# NAVBAR
# -------------------------------------------------------

render_navbar()


# -------------------------------------------------------
# HERO SECTION
# -------------------------------------------------------

st.markdown("""
<div class="page-header">
<div class="page-header-eyebrow">
<span class="live-dot"></span>
QUANT TRADING TERMINAL
</div>

<h1>11% Trading Lab</h1>

<p>
Advanced quantitative trading research platform combining
strategy testing, market analysis, and AI-assisted insights
into a single streamlined workflow.
</p>
</div>
""", unsafe_allow_html=True)


# -------------------------------------------------------
# MAIN GRID
# -------------------------------------------------------

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
<div class="panel">
<h3 class="section-hdr">STRATEGY LAB</h3>
<p style="font-size:0.85rem;color:#8896ab;">
Build and test trading strategies with technical indicators.
</p>
</div>
""", unsafe_allow_html=True)

    st.page_link("pages/1_Strategy_Lab.py", label="Open Strategy Lab", icon="🧪")


with col2:
    st.markdown("""
<div class="panel">
<h3 class="section-hdr">MARKET ANALYSIS</h3>
<p style="font-size:0.85rem;color:#8896ab;">
Explore price action, indicators, and fundamentals.
</p>
</div>
""", unsafe_allow_html=True)

    st.page_link("pages/4_Analysis.py", label="Open Analysis", icon="📊")


with col3:
    st.markdown("""
<div class="panel">
<h3 class="section-hdr">AI ASSISTANT</h3>
<p style="font-size:0.85rem;color:#8896ab;">
Ask the AI trading coach about markets and strategies.
</p>
</div>
""", unsafe_allow_html=True)

    st.page_link("pages/5_Assistant.py", label="Open Assistant", icon="🤖")


st.markdown("<br>", unsafe_allow_html=True)


# -------------------------------------------------------
# SECOND GRID
# -------------------------------------------------------

col4, col5, col6 = st.columns(3)

with col4:
    st.markdown("""
<div class="panel">
<h3 class="section-hdr">REPLAY</h3>
<p style="font-size:0.85rem;color:#8896ab;">
Step through historical charts candle by candle.
</p>
</div>
""", unsafe_allow_html=True)

    st.page_link("pages/3_Replay.py", label="Open Replay", icon="⏪")


with col5:
    st.markdown("""
<div class="panel">
<h3 class="section-hdr">CORRELATIONS</h3>
<p style="font-size:0.85rem;color:#8896ab;">
Understand how assets move relative to each other.
</p>
</div>
""", unsafe_allow_html=True)

    st.page_link("pages/7_Correlations.py", label="Open Correlations", icon="🔗")


with col6:
    st.markdown("""
<div class="panel">
<h3 class="section-hdr">MONTE CARLO</h3>
<p style="font-size:0.85rem;color:#8896ab;">
Run probabilistic simulations on price paths.
</p>
</div>
""", unsafe_allow_html=True)

    st.page_link("pages/9_Monte_Carlo.py", label="Open Monte Carlo", icon="🎲")


st.markdown("<br>", unsafe_allow_html=True)


# -------------------------------------------------------
# THIRD GRID
# -------------------------------------------------------

col7, col8 = st.columns(2)

with col7:
    st.markdown("""
<div class="panel">
<h3 class="section-hdr">WHALE TRACKER</h3>
<p style="font-size:0.85rem;color:#8896ab;">
Detect unusual volume and institutional activity.
</p>
</div>
""", unsafe_allow_html=True)

    st.page_link("pages/8_Whale_Tracker.py", label="Open Whale Tracker", icon="🐋")


with col8:
    st.markdown("""
<div class="panel">
<h3 class="section-hdr">EARNINGS</h3>
<p style="font-size:0.85rem;color:#8896ab;">
Track earnings releases and analyze reactions.
</p>
</div>
""", unsafe_allow_html=True)

    st.page_link("pages/6_Earnings.py", label="Open Earnings", icon="💰")


# -------------------------------------------------------
# FOOTER
# -------------------------------------------------------

st.markdown("""
<hr class="divider">

<div style="font-size:0.7rem;color:#3a4a5e;text-align:center;">
11% Quant Trading Terminal • Built with Python + Streamlit
</div>
""", unsafe_allow_html=True)
