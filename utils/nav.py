"""Shared navbar for all 11% pages."""
import streamlit as st
from utils.styles import SHARED_CSS, LOGO_IMG

NAV_PAGES = [
    ("app.py",                    "Home"),
    ("pages/1_Strategy_Lab.py",   "Strategy Lab"),
    ("pages/3_Replay.py",         "Replay"),
    ("pages/4_Analysis.py",       "Analysis"),
    ("pages/6_Earnings.py",       "Earnings"),
    ("pages/7_Correlations.py",   "Correlations"),
    ("pages/8_Whale_Tracker.py",  "Whale Tracker"),
    ("pages/9_Monte_Carlo.py",    "Monte Carlo"),
    ("pages/5_Assistant.py",      "AI Coach"),
]

def inject_css():
    st.markdown(SHARED_CSS, unsafe_allow_html=True)

def navbar():
    # Brand + opening
    st.markdown(
        '<div class="nb">'
        '<div class="nb-brand">' + LOGO_IMG + '</div>'
        '<div class="nb-links">',
        unsafe_allow_html=True
    )

    # Use equal-width columns — one per nav item
    cols = st.columns(len(NAV_PAGES))
    for col, (path, label) in zip(cols, NAV_PAGES):
        with col:
            st.page_link(path, label=label)

    # Close + tag
    st.markdown(
        '</div>'
        '<div class="nb-tag"><span class="live-dot"></span>BETA</div>'
        '</div>',
        unsafe_allow_html=True
    )
