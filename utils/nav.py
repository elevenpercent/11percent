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
    background:rgba(6,8,12,0.98);
    backdrop-filter:blur(24px);
    border-bottom:1px solid #1a2235;
    margin:0 -2.5rem;
    height:52px;
    display:flex;
    align-items:center;
    gap:1rem;
    padding:0 1.4rem;
    position:sticky;
    top:0;
    z-index:1000;
}

/* Logo */
.nb-logo img {
    height:32px!important;
}

/* Links */
.nb-links {
    display:flex;
    align-items:center;
    gap:1.2rem;
}

.nb-link {
    font-family:'IBM Plex Mono',monospace;
    font-size:0.62rem;
    font-weight:600;
    text-transform:uppercase;
    letter-spacing:0.1em;
    color:#3a4a5e;
    padding-bottom:2px;
    border-bottom:2px solid transparent;
    text-decoration:none;
}

.nb-link:hover {
    color:#eef2f7;
    border-bottom-color:#2a3550;
}

.nb-link.active {
    color:#00e676;
    border-bottom-color:#00e676;
}
</style>
"""

def navbar():
    st.markdown(NAV_CSS, unsafe_allow_html=True)

    # Start navbar
    st.markdown('<div class="nb">', unsafe_allow_html=True)

    # Logo
    st.markdown(f'<div class="nb-logo">{LOGO_IMG}</div>', unsafe_allow_html=True)

    # Links
    st.markdown('<div class="nb-links">', unsafe_allow_html=True)

    for path, label in NAV_ITEMS:
        current = st.session_state.get("_page_", "")
        active = "active" if current == path else ""
        st.markdown(
            f'<a class="nb-link {active}" href="/{path}" target="_self">{label}</a>',
            unsafe_allow_html=True
        )

    st.markdown('</div></div>', unsafe_allow_html=True)  # close links + navbar
