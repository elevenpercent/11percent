"""Shared navbar for all 11% pages."""
import streamlit as st
from utils.styles import LOGO_IMG

NAV_FLAGSHIP = [
    ("app.py",                   "Home"),
    ("pages/1_Strategy_Lab.py",  "Strategy Lab"),
    ("pages/3_Replay.py",        "Replay"),
    ("pages/4_Analysis.py",      "Analysis"),
    ("pages/5_Assistant.py",     "AI Coach"),
]

NAV_TOOLS = [
    ("pages/6_Earnings.py",       "Earnings"),
    ("pages/7_Correlations.py",   "Correlations"),
    ("pages/8_Whale_Tracker.py",  "Whale Tracker"),
    ("pages/9_Monte_Carlo.py",    "Monte Carlo"),
]

NAVBAR_CSS = """
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
    display:flex;
    align-items:center;
    height:52px;
    position:sticky;
    top:0;
    z-index:1000;
}

/* Brand */
.nb-brand {
    padding:0 1.4rem;
    border-right:1px solid #1a2235;
    display:flex;
    align-items:center;
}
.nb-brand img { height:32px!important; }

/* Flagship links */
.nb-links {
    display:flex;
    align-items:stretch;
    flex:1;
}
.nb-links [data-testid="stPageLink-NavLink"] {
    font-family:'IBM Plex Mono',monospace!important;
    font-size:0.6rem!important;
    font-weight:600!important;
    text-transform:uppercase!important;
    letter-spacing:0.1em!important;
    color:#3a4a5e!important;
    padding:0 1.1rem!important;
    border-bottom:2px solid transparent!important;
    display:flex!important;
    align-items:center!important;
    height:52px!important;
}
.nb-links [data-testid="stPageLink-NavLink"]:hover {
    color:#eef2f7!important;
    border-bottom-color:#2a3550!important;
}
.nb-links [data-testid="stPageLink-NavLink"][aria-current="page"] {
    color:#00e676!important;
    border-bottom-color:#00e676!important;
}

/* Tools dropdown (CLICK, not hover) */
.nb-tools-wrap {
    position:relative;
    display:flex;
    align-items:center;
    border-left:1px solid #1a2235;
}

.nb-tools-btn {
    font-family:'IBM Plex Mono',monospace;
    font-size:0.6rem;
    font-weight:600;
    text-transform:uppercase;
    letter-spacing:0.1em;
    color:#3a4a5e;
    background:transparent;
    border:none;
    padding:0 1.1rem;
    height:52px;
    cursor:pointer;
    display:flex;
    align-items:center;
    gap:0.5rem;
}

.nb-tools-btn:hover {
    color:#eef2f7;
    background:rgba(255,255,255,0.02);
}

.nb-tools-drop {
    display:none;
    position:absolute;
    top:52px;
    left:0;
    background:#0c1018;
    border:1px solid #1a2235;
    border-top:2px solid #00e676;
    border-radius:0 0 8px 8px;
    min-width:200px;
    z-index:9999;
}

.nb-tools-wrap.open .nb-tools-drop {
    display:block;
}

.nb-tools-drop a {
    display:block;
    padding:0.55rem 1rem;
    font-family:'IBM Plex Mono',monospace;
    font-size:0.6rem;
    color:#8896ab;
    text-decoration:none;
    border-bottom:1px solid #111927;
}
.nb-tools-drop a:hover {
    background:#111927;
    color:#00e676;
}

/* Beta tag */
.nb-tag {
    font-family:'IBM Plex Mono',monospace;
    font-size:0.44rem;
    color:#3a4a5e;
    letter-spacing:0.22em;
    padding:0 1.2rem;
    border-left:1px solid #1a2235;
    display:flex;
    align-items:center;
}
.live-dot {
    width:5px;
    height:5px;
    border-radius:50%;
    background:#00e676;
    margin-right:6px;
}

/* Spacer */
.nb-spacer { height:1.4rem; }
</style>
"""

def navbar():
    st.markdown(NAVBAR_CSS, unsafe_allow_html=True)

    # Navbar HTML
    st.markdown(
        '<div class="nb">'
        f'<div class="nb-brand">{LOGO_IMG}</div>'
        '<div class="nb-links">',
        unsafe_allow_html=True
    )

    # Flagship links
    cols = st.columns(len(NAV_FLAGSHIP))
    for col, (path, label) in zip(cols, NAV_FLAGSHIP):
        with col:
            st.page_link(path, label=label)

    # Tools dropdown
    tools_links = "".join(
        f'<a href="/{label.replace(" ", "_")}" target="_self">{label}</a>'
        for _, label in NAV_TOOLS
    )

    st.markdown(
        '</div>'  # close nb-links
        '<div class="nb-tools-wrap">'
        '  <button class="nb-tools-btn">Tools ▼</button>'
        f'  <div class="nb-tools-drop">{tools_links}</div>'
        '</div>'
        '<div class="nb-tag"><span class="live-dot"></span>BETA</div>'
        '</div>'  # close navbar
        '<div class="nb-spacer"></div>',
        unsafe_allow_html=True
    )

    # JS for click dropdown
    st.markdown("""
    <script>
    document.addEventListener("DOMContentLoaded", function() {
        const wrap = document.querySelector('.nb-tools-wrap');
        const btn = document.querySelector('.nb-tools-btn');
        if (wrap && btn) {
            btn.addEventListener('click', function(e) {
                e.stopPropagation();
                wrap.classList.toggle('open');
            });
            document.addEventListener('click', function() {
                wrap.classList.remove('open');
            });
        }
    });
    </script>
    """, unsafe_allow_html=True)
