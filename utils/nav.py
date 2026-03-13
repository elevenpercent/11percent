import streamlit as st
from utils.styles import LOGO_IMG


def navbar():
    """
    Pure HTML navbar — centered pills with hover effect.
    Uses window.location for navigation which DOES update the URL bar on Streamlit Cloud.
    st.page_link is NOT used here because it injects Streamlit widget chrome that
    breaks the layout. Navigation is handled via JS window.location.href instead,
    which correctly updates the browser URL bar.
    """

    # Detect current page to highlight active link
    try:
        current = st.context.headers.get("Referer", "") or ""
    except Exception:
        current = ""

    pages = [
        ("/",               "Home"),
        ("/Strategy_Lab",   "Strategy Lab"),
        ("/Replay",         "Replay"),
        ("/Analysis",       "Analysis"),
        ("/Assistant",      "AI Coach"),
    ]

    tools = [
        ("/Earnings",      "📅", "Earnings"),
        ("/Correlations",  "⬡", "Correlations"),
        ("/Whale_Tracker", "🐋", "Whale Tracker"),
        ("/Monte_Carlo",   "〰", "Monte Carlo"),
    ]

    links_html = ""
    for href, label in pages:
        active = "nav-active" if href != "/" and href.strip("/") in current else ""
        links_html += (
            f'<button class="nav-pill {active}" onclick="window.location.href=\'{href}\'">'
            f'{label}</button>'
        )

    tools_html = "".join(
        f'<div class="nav-drop-item" onclick="window.location.href=\'{href}\'">'
        f'<span>{icon}</span><span>{label}</span></div>'
        for href, icon, label in tools
    )

    html = f"""
<style>
/* ── wipe old navbar styles ── */
.nb, .navbar-shell {{ display:none!important; }}

/* ── Outer bar ── */
.ep-navbar {{
    background:#06080c;
    border-bottom:1px solid #1a2235;
    margin:-2.5rem -2.5rem 0 -2.5rem;
    height:64px;
    display:flex;
    align-items:center;
    position:sticky;
    top:0;
    z-index:9999;
    padding:0 1.8rem;
    gap:0;
}}

/* ── Logo (left, fixed width) ── */
.ep-brand {{
    display:flex;
    align-items:center;
    flex-shrink:0;
    cursor:pointer;
    width:80px;
}}
.ep-brand img {{
    height:46px!important;
    width:auto!important;
    display:block;
}}

/* ── Center pill cluster ── */
.ep-center {{
    flex:1;
    display:flex;
    align-items:center;
    justify-content:center;
    gap:2px;
    overflow:visible;
}}

/* ── Pill buttons ── */
.nav-pill {{
    font-family:'IBM Plex Mono',monospace;
    font-size:0.59rem;
    font-weight:600;
    text-transform:uppercase;
    letter-spacing:0.1em;
    color:#3a4a5e;
    background:transparent;
    border:1px solid transparent;
    border-radius:7px;
    padding:0.4rem 0.95rem;
    cursor:pointer;
    transition:color 0.15s ease, background 0.15s ease, border-color 0.15s ease;
    white-space:nowrap;
    line-height:1;
    outline:none;
}}
.nav-pill:hover {{
    color:#eef2f7;
    background:rgba(255,255,255,0.06);
    border-color:#1a2235;
}}
.nav-pill:active {{ background:rgba(255,255,255,0.04); }}
.nav-pill.nav-active {{
    color:#00e676;
    background:rgba(0,230,118,0.08);
    border-color:rgba(0,230,118,0.25);
}}

/* ── Tools dropdown ── */
.ep-tools {{
    position:relative;
    display:inline-flex;
    align-items:center;
}}
.ep-tools-btn {{
    font-family:'IBM Plex Mono',monospace;
    font-size:0.59rem; font-weight:600;
    text-transform:uppercase; letter-spacing:0.1em;
    color:#3a4a5e; background:transparent;
    border:1px solid transparent; border-radius:7px;
    padding:0.4rem 0.95rem;
    cursor:pointer;
    display:inline-flex; align-items:center; gap:0.45rem;
    transition:color 0.15s ease, background 0.15s ease, border-color 0.15s ease;
    outline:none; white-space:nowrap; line-height:1;
}}
.ep-tools-btn:hover {{
    color:#eef2f7;
    background:rgba(255,255,255,0.06);
    border-color:#1a2235;
}}
.ep-tools-btn .arr {{
    font-size:0.38rem;
    transition:transform 0.2s;
    display:inline-block;
    opacity:0.6;
}}
.ep-tools:hover .arr {{ transform:rotate(180deg); }}

.ep-dropdown {{
    display:none;
    position:absolute;
    top:calc(100% + 8px);
    left:50%;
    transform:translateX(-50%);
    min-width:196px;
    background:#0d1117;
    border:1px solid #1a2235;
    border-top:2px solid #00e676;
    border-radius:0 0 10px 10px;
    box-shadow:0 24px 64px rgba(0,0,0,0.85);
    z-index:10000;
    padding:0.25rem 0;
    overflow:hidden;
}}
.ep-tools:hover .ep-dropdown {{ display:block; }}

.nav-drop-item {{
    display:flex; align-items:center; gap:0.7rem;
    padding:0.62rem 1.1rem;
    font-family:'IBM Plex Mono',monospace; font-size:0.58rem;
    font-weight:600; text-transform:uppercase; letter-spacing:0.09em;
    color:#3a4a5e; cursor:pointer;
    transition:color 0.12s, background 0.12s, padding-left 0.14s;
}}
.nav-drop-item:hover {{
    color:#00e676;
    background:rgba(0,230,118,0.06);
    padding-left:1.5rem;
}}

/* ── Right side ── */
.ep-right {{
    display:flex;
    align-items:center;
    gap:0.75rem;
    flex-shrink:0;
    width:80px;
    justify-content:flex-end;
}}
.ep-beta {{
    font-family:'IBM Plex Mono',monospace; font-size:0.42rem;
    text-transform:uppercase; letter-spacing:0.22em; color:#2a3550;
    display:flex; align-items:center; gap:0.4rem;
}}
.ep-dot {{
    width:5px; height:5px; border-radius:50%; background:#00e676; flex-shrink:0;
    animation:ep-pulse 2s ease-in-out infinite;
}}
@keyframes ep-pulse {{
    0%,100%{{opacity:1;box-shadow:0 0 6px #00e676}} 50%{{opacity:0.3;box-shadow:none}}
}}
.ep-signup {{
    font-family:'IBM Plex Mono',monospace; font-size:0.56rem; font-weight:700;
    text-transform:uppercase; letter-spacing:0.08em;
    color:#000; background:#00e676; border:none; border-radius:6px;
    padding:0.42rem 0.9rem; cursor:pointer; white-space:nowrap;
    transition:background 0.15s, box-shadow 0.15s; outline:none;
}}
.ep-signup:hover {{ background:#00ff88; box-shadow:0 0 14px rgba(0,230,118,0.45); }}

/* ── Spacer below navbar ── */
.ep-spacer {{ height:1.8rem; }}
</style>

<div class="ep-navbar">
    <div class="ep-brand" onclick="window.location.href='/'">{LOGO_IMG}</div>

    <div class="ep-center">
        {links_html}
        <div class="ep-tools">
            <button class="ep-tools-btn">Tools <span class="arr">▼</span></button>
            <div class="ep-dropdown">
                {tools_html}
            </div>
        </div>
    </div>

    <div class="ep-right">
        <div class="ep-beta"><span class="ep-dot"></span>Beta</div>
        <button class="ep-signup" onclick="window.location.href='/Login'">Sign Up</button>
    </div>
</div>
<div class="ep-spacer"></div>
"""
    st.markdown(html, unsafe_allow_html=True)
