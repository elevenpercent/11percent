import streamlit as st
from utils.styles import LOGO_IMG

NAV_CSS = """
<style>

/* NAVBAR CONTAINER */
.navbar {
    background:#06080c;
    border-bottom:1px solid #1a2235;
    margin:0 -2.5rem;
    height:56px;
    display:flex;
    align-items:center;
    padding:0 1.4rem;
    gap:1.4rem;
}

/* LOGO */
.nav-logo img {
    height:32px;
}

/* BUTTON ROW — THIS IS THE FIX */
.nav-buttons {
    display:flex !important;
    flex-direction:row !important;
    align-items:center;
    gap:0.6rem;
    white-space:nowrap;
}

/* BUTTON STYLE */
.nav-btn {
    display:inline-block !important;
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

.nav-btn.active {
    border-color:#00e676;
    color:#00e676;
    background:rgba(0,230,118,0.1);
}
/* FORCE NAVBAR BUTTONS INLINE — OVERRIDES GLOBAL CSS */
.nav-buttons a,
.nav-btn,
.navbar a {
    display:inline-flex !important;
    flex-direction:row !important;
    align-items:center !important;
    justify-content:center !important;
    width:auto !important;
    max-width:none !important;
    white-space:nowrap !important;
}

</style>
"""

def navbar():
    st.markdown(NAV_CSS, unsafe_allow_html=True)

    st.markdown('<div class="navbar">', unsafe_allow_html=True)

    # LOGO
    st.markdown(f'<div class="nav-logo">{LOGO_IMG}</div>', unsafe_allow_html=True)

    # BUTTONS (INLINE)
    st.markdown('<div class="nav-buttons">', unsafe_allow_html=True)

    pages = [
        ("app.py", "Home"),
        ("pages/1_Strategy_Lab.py", "Strategy Lab"),
        ("pages/3_Replay.py", "Replay"),
        ("pages/4_Analysis.py", "Analysis"),
        ("pages/5_Assistant.py", "AI Coach"),
    ]

    current = st.session_state.get("_page_", "")

    for path, label in pages:
        active = "active" if current == path else ""
        st.markdown(
            f'<a class="nav-btn {active}" href="/{path}" target="_self">{label}</a>',
            unsafe_allow_html=True
        )

    st.markdown('</div></div>', unsafe_allow_html=True)
    
