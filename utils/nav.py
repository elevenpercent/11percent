import streamlit as st
from utils.styles import LOGO_IMG

NAV_ITEMS = [
    ("app.py",                  "Home"),
    ("pages/1_Strategy_Lab.py", "Strategy Lab"),
    ("pages/3_Replay.py",       "Replay"),
    ("pages/4_Analysis.py",     "Analysis"),
    ("pages/5_Assistant.py",    "AI Coach"),
]

NAV_CSS = """
<style>
/* Hide Streamlit chrome */
[data-testid="stSidebar"],
[data-testid="stSidebarNav"],
[data-testid="collapsedControl"],
section[data-testid="stSidebar"] {
    display:none!important;
}
#MainMenu, footer, header { display:none!important; }

/* Navbar container */
.nb {
    background:#06080c;
    border-bottom:1px solid #1a2235;
    margin:0 -2.5rem;
    height:52px;
    display:flex;
    align-items:center;
    padding:0 1.4rem;
    gap:1.2rem;
}

/* Logo */
.nb-logo img {
    height:32px!important;
}

/* Button row */
.nb-buttons {
    display:flex;
    align-items:center;
    gap:0.6rem;
}

/* Actual buttons */
.nb-btn {
    font-family:'IBM Plex Mono',monospace;
    font-size:0.62rem;
    font-weight:600;
    text-transform:uppercase;
    letter-spacing:0.1em;
    padding:0.35rem 0.9rem;
    border-radius:6px;
    border:1px solid #1a2235;
    background:#0c1018;
    color:#8896ab;
    text-decoration:none;
    transition:all 0.15s;
}

.nb-btn:hover {
    border-color:#00e676;
    color:#00e676;
    background:rgba(0,230,118,0.05);
}

.nb-btn.active {
    border-color:#00e676;
    color:#00e676;
    background:rgba(0,230,118,0.08);
}
</style>
"""

def navbar():
    st.markdown(NAV_CSS, unsafe_allow_html=True)

    st.markdown('<div class="nb">', unsafe_allow_html=True)

    # Logo
    st.markdown(f'<div class="nb-logo">{LOGO_IMG}</div>', unsafe_allow_html=True)

    # Buttons
    st.markdown('<div class="nb-buttons">', unsafe_allow_html=True)

    current = st.session_state.get("_page_", "")

    for path, label in NAV_ITEMS:
        active = "active" if current == path else ""
        st.markdown(
            f'<a class="nb-btn {active}" href="/{path}" target="_self">{label}</a>',
            unsafe_allow_html=True
        )

    st.markdown('</div></div>', unsafe_allow_html=True)
