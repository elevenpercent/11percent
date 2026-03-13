import streamlit as st
from utils.styles import LOGO_IMG


def navbar():
    # CRITICAL: st.markdown with unsafe_allow_html works fine for links.
    # The previous components.v1.html approach created an iframe which
    # (a) blocks pointer events to parent and (b) clips the dropdown.
    # 
    # The dropdown "hidden behind page" issue is caused by Streamlit's
    # .block-container having overflow:hidden. We fix that with CSS injection.
    # 
    # The "raw HTML showing" from before was caused by f-string curly brace
    # escaping inside the CSS. We avoid f-strings entirely here.

    user_email = st.session_state.get("user_email", "")
    user_name  = ""
    if user_email:
        user_name = user_email.split("@")[0].title()

    if user_name:
        right_html = (
            '<div class="ep-right">'
            '<span class="ep-welcome">Hi, ' + user_name + '</span>'
            '<a class="ep-signout" href="/Login" target="_self">Sign Out</a>'
            '</div>'
        )
    else:
        right_html = (
            '<div class="ep-right">'
            '<div class="ep-beta"><span class="ep-dot"></span>Beta</div>'
            '<a class="ep-signup" href="/Login" target="_self">Sign Up</a>'
            '</div>'
        )

    css = """<style>
/* Fix Streamlit overflow so dropdown isn't clipped */
.main .block-container { overflow: visible !important; }
section[data-testid="stMain"] { overflow: visible !important; }
.appview-container { overflow: visible !important; }

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
    gap: 0;
}
.ep-brand {
    display: flex;
    align-items: center;
    flex-shrink: 0;
    text-decoration: none;
    margin-right: 0.5rem;
}
.ep-brand img {
    height: 42px !important;
    width: auto !important;
    display: block;
}
.ep-center {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 2px;
    position: relative;
}
.ep-pill {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.58rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.09em;
    color: #3a4a5e;
    background: transparent;
    border: 1px solid transparent;
    border-radius: 6px;
    padding: 0.38rem 0.85rem;
    cursor: pointer;
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    white-space: nowrap;
    transition: color 0.15s, background 0.15s, border-color 0.15s;
    line-height: 1;
}
.ep-pill:hover {
    color: #eef2f7;
    background: rgba(255,255,255,0.06);
    border-color: #1a2235;
    text-decoration: none;
}

/* Tools wrapper */
.ep-tools-wrap {
    position: relative;
    display: inline-flex;
    align-items: center;
}
.ep-tools-btn {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.58rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.09em;
    color: #3a4a5e;
    background: transparent;
    border: 1px solid transparent;
    border-radius: 6px;
    padding: 0.38rem 0.85rem;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    transition: color 0.15s, background 0.15s, border-color 0.15s;
    outline: none;
    white-space: nowrap;
    line-height: 1;
}
.ep-tools-btn:hover {
    color: #eef2f7;
    background: rgba(255,255,255,0.06);
    border-color: #1a2235;
}
.ep-arrow {
    font-size: 0.4rem;
    opacity: 0.5;
    transition: transform 0.2s;
    display: inline-block;
}
.ep-tools-wrap:hover .ep-arrow { transform: rotate(180deg); }

.ep-dropdown {
    display: none;
    position: absolute;
    top: calc(100% + 6px);
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
    display: flex;
    align-items: center;
    gap: 0.6rem;
    padding: 0.58rem 1rem;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.57rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #3a4a5e;
    text-decoration: none;
    border-bottom: 1px solid #0d1117;
    transition: color 0.12s, background 0.12s, padding-left 0.12s;
}
.ep-drop-link:last-child { border-bottom: none; }
.ep-drop-link:hover {
    color: #00e676;
    background: rgba(0,230,118,0.05);
    padding-left: 1.4rem;
    text-decoration: none;
}

.ep-right {
    display: flex;
    align-items: center;
    gap: 0.65rem;
    flex-shrink: 0;
    margin-left: 0.5rem;
}
.ep-beta {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.4rem;
    text-transform: uppercase;
    letter-spacing: 0.2em;
    color: #2a3550;
    display: flex;
    align-items: center;
    gap: 0.35rem;
}
.ep-dot {
    width: 5px; height: 5px;
    border-radius: 50%;
    background: #00e676;
    flex-shrink: 0;
    animation: ep-pulse 2s ease-in-out infinite;
}
@keyframes ep-pulse {
    0%,100% { opacity:1; box-shadow: 0 0 5px #00e676; }
    50%      { opacity:0.3; box-shadow: none; }
}
.ep-signup {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.55rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    color: #000 !important;
    background: #00e676;
    border: none;
    border-radius: 6px;
    padding: 0.38rem 0.85rem;
    cursor: pointer;
    white-space: nowrap;
    transition: background 0.15s, box-shadow 0.15s;
    text-decoration: none !important;
    display: inline-flex;
    align-items: center;
}
.ep-signup:hover {
    background: #00ff88;
    box-shadow: 0 0 12px rgba(0,230,118,0.4);
    text-decoration: none !important;
}
.ep-welcome {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.58rem;
    color: #00e676;
    font-weight: 600;
    white-space: nowrap;
}
.ep-signout {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.52rem;
    color: #3a4a5e;
    text-decoration: none;
    border: 1px solid #1a2235;
    border-radius: 6px;
    padding: 0.32rem 0.7rem;
    transition: color 0.15s, border-color 0.15s;
    white-space: nowrap;
}
.ep-signout:hover { color: #ff3d57; border-color: #ff3d57; text-decoration: none; }

.ep-spacer { height: 1.5rem; }
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
        + right_html +
        '</div>'
        '<div class="ep-spacer"></div>'
    )

    st.markdown(css + body, unsafe_allow_html=True)
