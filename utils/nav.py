import streamlit as st
from utils.styles import LOGO_IMG

def navbar():
    st.markdown("""
    <style>
    .navbar {
        background:#06080c;
        border-bottom:1px solid #1a2235;
        margin:0 -2.5rem;
        height:56px;
        display:flex;
        align-items:center;
        padding:0 1.4rem;
        gap:1.4rem;
        white-space:nowrap;
    }

    .nav-logo img {
        height:36px;
    }

    .nav-buttons {
        display:flex;
        flex-direction:row;
        align-items:center;
        gap:0.6rem;
        white-space:nowrap;
    }

    .nav-btn {
        display:inline-flex;
        align-items:center;
        justify-content:center;
        font-family:'IBM Plex Mono',monospace;
        font-size:0.62rem;
        font-weight:600;
        text-transform:uppercase;
        letter-spacing:0.1em;
        padding:0.35rem 1rem;
        border-radius:6px;
        border:1px solid #1a2235;
        background:#0c1018;
        color:#8896ab;
        text-decoration:none;
        transition:all 0.15s ease;
        white-space:nowrap;
    }

    .nav-btn:hover {
        border-color:#00e676;
        color:#00e676;
        background:rgba(0,230,118,0.05);
    }
    </style>

    <div class="navbar">
        <div class="nav-logo">""" + LOGO_IMG + """</div>

        <div class="nav-buttons">
            <a class="nav-btn" href="/app.py" target="_self">Home</a>
            <a class="nav-btn" href="/pages/1_Strategy_Lab.py" target="_self">Strategy Lab</a>
            <a class="nav-btn" href="/pages/3_Replay.py" target="_self">Replay</a>
            <a class="nav-btn" href="/pages/4_Analysis.py" target="_self">Analysis</a>
            <a class="nav-btn" href="/pages/5_Assistant.py" target="_self">AI Coach</a>
        </div>
    </div>
    """, unsafe_allow_html=True)
