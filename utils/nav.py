import streamlit as st
from utils.styles import LOGO_IMG


def navbar():
    user_email = st.session_state.get("user_email", "")
    user_name  = ""
    if user_email:
        raw = user_email.split("@")[0].replace(".", " ").replace("_", " ")
        user_name = raw.title()

    if user_name:
        right = (
            '<div class="ep-right">'
            '<span class="ep-welcome">Hi, ' + user_name + '</span>'
            '<a class="ep-signout" href="/Login" target="_self">Sign Out</a>'
            '</div>'
        )
    else:
        right = (
            '<div class="ep-right">'
            '<div class="ep-beta"><span class="ep-dot"></span>Beta</div>'
            '<a class="ep-signup" href="/Login" target="_self">Sign Up</a>'
            '</div>'
        )

    # CRITICAL FIXES vs previous version:
    # 1. overflow:visible on .main and .block-container so dropdown shows above page
    # 2. Links styled as plain text — no browser blue underline (text-decoration:none, color inherited)
    # 3. Dropdown uses padding bridge between button and menu so mouse doesn't "leave" the hover zone
    # 4. No iframe (components.html) — st.markdown only, so clicks work
    # 5. body overflow reset so page stays scrollable

    css = """<style>
/* Restore page scroll — previous overflow:visible broke it */
.main { overflow-y: auto !important; }
section[data-testid="stMain"] > div { overflow: visible !important; }
.block-container { overflow: visible !important; }

/* Hide Streamlit default link styling everywhere in nav */
.ep-navbar a, .ep-navbar a:visited, .ep-navbar a:hover, .ep-navbar a:active {
    text-decoration: none !important;
}

.ep-navbar {
    background: #06080c;
    border-bottom: 1px solid #1a2235;
    margin: -2.5rem -2.5rem 0 -2.5rem;
    height: 60px;
    display: flex;
    align-items: center;
    position: sticky;
    top: 0;
    z-index: 99999;
    padding: 0 1.6rem;
}
.ep-brand {
    display: flex;
    align-items: center;
    flex-shrink: 0;
    margin-right: 0.5rem;
    text-decoration: none !important;
}
.ep-brand img { height: 42px !important; width: auto !important; display: block; }

.ep-center {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 2px;
}

/* Pill — looks like button, no browser link styling */
.ep-pill {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.58rem; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.09em;
    color: #3a4a5e !important;
    background: transparent;
    border: 1px solid transparent;
    border-radius: 6px;
    padding: 0.38rem 0.85rem;
    cursor: pointer;
    display: inline-flex; align-items: center;
    white-space: nowrap;
    transition: color 0.15s, background 0.15s, border-color 0.15s;
    line-height: 1;
    text-decoration: none !important;
}
.ep-pill:hover {
    color: #eef2f7 !important;
    background: rgba(255,255,255,0.06) !important;
    border-color: #1a2235 !important;
    text-decoration: none !important;
}

/* Tools wrapper — the padding-top bridge prevents dropdown from closing
   when mouse moves from button down to the menu */
.ep-tools-wrap {
    position: relative;
    display: inline-flex;
    align-items: center;
}
.ep-tools-btn {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.58rem; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.09em;
    color: #3a4a5e;
    background: transparent;
    border: 1px solid transparent;
    border-radius: 6px;
    padding: 0.38rem 0.85rem;
    cursor: pointer;
    display: inline-flex; align-items: center; gap: 0.35rem;
    transition: color 0.15s, background 0.15s, border-color 0.15s;
    outline: none; white-space: nowrap; line-height: 1;
}
.ep-tools-btn:hover,
.ep-tools-wrap:hover .ep-tools-btn {
    color: #eef2f7;
    background: rgba(255,255,255,0.06);
    border-color: #1a2235;
}
.ep-arrow {
    font-size: 0.4rem; opacity: 0.5;
    transition: transform 0.2s; display: inline-block;
}
.ep-tools-wrap:hover .ep-arrow { transform: rotate(180deg); }

/* Invisible bridge fills gap between button and dropdown 
   so mouse doesn't leave hover zone while crossing the gap */
.ep-tools-wrap::after {
    content: '';
    position: absolute;
    top: 100%;
    left: 0; right: 0;
    height: 14px;
    display: none;
}
.ep-tools-wrap:hover::after { display: block; }

.ep-dropdown {
    display: none;
    position: absolute;
    top: calc(100% + 8px);
    left: 50%;
    transform: translateX(-50%);
    min-width: 185px;
    background: #0d1117;
    border: 1px solid #1a2235;
    border-top: 2px solid #00e676;
    border-radius: 0 0 10px 10px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.9);
    z-index: 999999;
    padding: 0.2rem 0;
    overflow: hidden;
}
.ep-tools-wrap:hover .ep-dropdown { display: block; }

.ep-drop-link {
    display: flex; align-items: center; gap: 0.6rem;
    padding: 0.58rem 1rem;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.57rem; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.08em;
    color: #3a4a5e !important;
    text-decoration: none !important;
    border-bottom: 1px solid #0d1117;
    transition: color 0.12s, background 0.12s, padding-left 0.12s;
}
.ep-drop-link:last-child { border-bottom: none; }
.ep-drop-link:hover {
    color: #00e676 !important;
    background: rgba(0,230,118,0.05) !important;
    padding-left: 1.4rem !important;
    text-decoration: none !important;
}

.ep-right {
    display: flex; align-items: center;
    gap: 0.65rem; flex-shrink: 0; margin-left: 0.5rem;
}
.ep-beta {
    font-family: 'IBM Plex Mono', monospace; font-size: 0.4rem;
    text-transform: uppercase; letter-spacing: 0.2em; color: #2a3550;
    display: flex; align-items: center; gap: 0.35rem;
}
.ep-dot {
    width: 5px; height: 5px; border-radius: 50%;
    background: #00e676; flex-shrink: 0;
    animation: ep-pulse 2s ease-in-out infinite;
}
@keyframes ep-pulse {
    0%,100% { opacity:1; box-shadow: 0 0 5px #00e676; }
    50%      { opacity:0.3; box-shadow: none; }
}
.ep-signup {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.55rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.07em;
    color: #000 !important;
    background: #00e676;
    border: none; border-radius: 6px;
    padding: 0.38rem 0.85rem;
    cursor: pointer; white-space: nowrap;
    transition: background 0.15s, box-shadow 0.15s;
    text-decoration: none !important;
    display: inline-flex; align-items: center;
}
.ep-signup:hover {
    background: #00ff88 !important;
    box-shadow: 0 0 12px rgba(0,230,118,0.4);
}
.ep-welcome {
    font-family: 'IBM Plex Mono', monospace; font-size: 0.58rem;
    color: #00e676; font-weight: 600; white-space: nowrap;
}
.ep-signout {
    font-family: 'IBM Plex Mono', monospace; font-size: 0.52rem;
    color: #3a4a5e !important; text-decoration: none !important;
    border: 1px solid #1a2235; border-radius: 6px;
    padding: 0.32rem 0.7rem;
    transition: color 0.15s, border-color 0.15s;
    white-space: nowrap;
}
.ep-signout:hover { color: #ff3d57 !important; border-color: #ff3d57 !important; }

.ep-spacer { height: 1.4rem; }

/* Remove Streamlit's default blue link color from page_link buttons */
[data-testid="stPageLink"] a {
    text-decoration: none !important;
    color: inherit !important;
}
</style>"""

    body = (
        '<div class="ep-navbar">'
        '<a class="ep-brand" href="/" target="_self">' + LOGO_IMG + '</a>'
        '<div class="ep-center">'
        '<a class="ep-pill" href="/" target="_self">Home</a>'
        '<a class="ep-pill" href="/Strategy_Lab" target="_self">Strategy Lab</a>'
        '<a class="ep-pill" href="/Replay" target="_self">Replay</a>'
        '<a class="ep-pill" href="/Analysis" target="_self">Analysis</a>'
        '<a class="ep-pill" href="/Assistant" target="_self">AI Coach</a>'
        '<div class="ep-tools-wrap">'
        '<button class="ep-tools-btn">Tools <span class="ep-arrow">&#9660;</span></button>'
        '<div class="ep-dropdown">'
        '<a class="ep-drop-link" href="/Earnings" target="_self">Earnings</a>'
        '<a class="ep-drop-link" href="/Correlations" target="_self">Correlations</a>'
        '<a class="ep-drop-link" href="/Whale_Tracker" target="_self">Whale Tracker</a>'
        '<a class="ep-drop-link" href="/Monte_Carlo" target="_self">Monte Carlo</a>'
        '</div>'
        '</div>'
        '</div>'
        + right +
        '</div>'
        '<div class="ep-spacer"></div>'
    )

    st.markdown(css + body, unsafe_allow_html=True)
