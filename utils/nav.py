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
/* ── Kill sidebar flash ── */
[data-testid="stSidebar"],
[data-testid="stSidebarNav"],
[data-testid="collapsedControl"],
section[data-testid="stSidebar"] {
    display:none!important; width:0!important;
    min-width:0!important; visibility:hidden!important;
}
[data-testid="stAppViewContainer"] > section:first-child { display:none!important; }
#MainMenu, footer, header { display:none!important; }

/* ── Navbar shell ── */
.nb {
    background:rgba(6,8,12,0.98);
    backdrop-filter:blur(24px);
    border-bottom:1px solid #1a2235;
    margin:0 -2.5rem;
    display:flex; align-items:center;
    height:52px; position:sticky; top:0; z-index:1000;
}

/* Brand */
.nb-brand {
    padding:0 1.4rem;
    border-right:1px solid #1a2235;
    display:flex; align-items:center;
}
.nb-brand img { height:32px!important; width:auto!important; }

/* Flagship links */
.nb-links {
    display:flex; align-items:stretch;
    flex:1;
}
.nb-links [data-testid="stPageLink-NavLink"] {
    font-family:'IBM Plex Mono',monospace!important;
    font-size:0.6rem!important; font-weight:600!important;
    text-transform:uppercase!important; letter-spacing:0.1em!important;
    color:#3a4a5e!important; text-decoration:none!important;
    padding:0 1.1rem!important; border-radius:0!important;
    border:none!important; border-bottom:2px solid transparent!important;
    background:transparent!important; display:flex!important;
    align-items:center!important; height:52px!important;
    transition:color 0.15s, border-color 0.15s!important;
}
.nb-links [data-testid="stPageLink-NavLink"]:hover {
    color:#eef2f7!important; border-bottom-color:#2a3550!important;
    background:rgba(255,255,255,0.02)!important;
}
.nb-links [data-testid="stPageLink-NavLink"][aria-current="page"] {
    color:#00e676!important; border-bottom-color:#00e676!important;
    background:rgba(0,230,118,0.03)!important;
}

/* Tools dropdown */
.nb-tools-wrap {
    position:relative; display:flex; align-items:center;
    border-left:1px solid #1a2235;
}
.nb-tools-btn {
    font-family:'IBM Plex Mono',monospace; font-size:0.6rem;
    font-weight:600; text-transform:uppercase; letter-spacing:0.1em;
    color:#3a4a5e; background:transparent; border:none;
    padding:0 1.1rem; height:52px; cursor:pointer;
    display:flex; align-items:center; gap:0.5rem;
}
.nb-tools-btn:hover { color:#eef2f7; background:rgba(255,255,255,0.02); }
.nb-tools-drop {
    display:none; position:absolute; top:52px; left:0;
    background:#0c1018; border:1px solid #1a2235;
    border-top:2px solid #00e676;
    border-radius:0 0 8px 8px; min-width:200px; z-index:9999;
}
.nb-tools-wrap:hover .nb-tools-drop { display:block; }
.nb-tools-drop a {
    display:flex; align-items:center; gap:0.7rem; padding:0.75rem 1.2rem;
    font-family:'IBM Plex Mono',monospace; font-size:0.6rem;
    font-weight:600; text-transform:uppercase; letter-spacing:0.1em;
    color:#3a4a5e; text-decoration:none;
    border-bottom:1px solid #111927;
}
.nb-tools-drop a:hover {
    color:#00e676; background:rgba(0,230,118,0.04);
}

/* BETA tag */
.nb-tag {
    font-family:'IBM Plex Mono',monospace;
    font-size:0.44rem; color:#3a4a5e;
    letter-spacing:0.22em; padding:0 1.2rem;
    border-left:1px solid #1a2235;
    display:flex; align-items:center;
}
.live-dot {
    width:5px; height:5px; border-radius:50%;
    background:#00e676; margin-right:6px;
}

/* ── Action buttons (NEW) ── */
.nb-actions {
    display:flex;
    align-items:center;
    gap:0.6rem;
    padding:0 1.2rem;
    border-left:1px solid #1a2235;
}
.nb-btn {
    font-family:'IBM Plex Mono',monospace;
    font-size:0.6rem;
    font-weight:600;
    text-transform:uppercase;
    letter-spacing:0.1em;
    color:#eef2f7;
    padding:0.35rem 0.9rem;
    border:1px solid #1a2235;
    border-radius:6px;
    background:#0c1018;
    text-decoration:none;
    transition:all 0.15s;
}
.nb-btn:hover {
    border-color:#00e676;
    color:#00e676;
    background:rgba(0,230,118,0.05);
}

/* Spacer below navbar */
.nb-spacer { height:1.4rem; }
</style>
"""

def navbar():
    st.markdown(NAVBAR_CSS, unsafe_allow_html=True)

    st.markdown(
        '<div class="nb">'
        f'<div class="nb-brand">{LOGO_IMG}</div>'
        '<div class="nb-links">',
        unsafe_allow_html=True
    )

    cols = st.columns(len(NAV_FLAGSHIP))
    for col, (path, label) in zip(cols, NAV_FLAGSHIP):
        with col:
            st.page_link(path, label=label)

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
        '<div class="nb-actions">'
        '   <a class="nb-btn" href="/pages/1_Strategy_Lab.py">Lab</a>'
        '   <a class="nb-btn" href="/pages/3_Replay.py">Replay</a>'
        '   <a class="nb-btn" href="/pages/5_Assistant.py">AI Coach</a>'
        '</div>'
        '</div>'  # close .nb
        '<div class="nb-spacer"></div>',
        unsafe_allow_html=True
    )
