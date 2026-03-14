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

    css = """<style>
.main { overflow-y: auto !important; }
section[data-testid="stMain"] > div { overflow: visible !important; }
.block-container { overflow: visible !important; }

.ep-navbar a, .ep-navbar a:visited, .ep-navbar a:hover, .ep-navbar a:active {
    text-decoration: none !important;
}
.ep-navbar {
    background: #0d0f11;
    border-bottom: 1px solid #1f2530;
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
    display: flex; align-items: center; flex-shrink: 0;
    margin-right: 0.5rem; text-decoration: none !important;
    cursor: pointer;
}
.ep-brand img { height: 42px !important; width: auto !important; display: block; }
.ep-center {
    flex: 1; display: flex; align-items: center;
    justify-content: center; gap: 2px;
}
.ep-pill {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.58rem; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.09em;
    color: #374151 !important;
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
    color: #e2e8f0 !important;
    background: rgba(255,255,255,0.04) !important;
    border-color: #1f2530 !important;
}
.ep-tools-wrap {
    position: relative; display: inline-flex; align-items: center;
}
.ep-tools-btn {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.58rem; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.09em;
    color: #374151;
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
    color: #e2e8f0;
    background: rgba(255,255,255,0.04);
    border-color: #1f2530;
}
.ep-arrow { font-size:0.4rem; opacity:0.5; transition:transform 0.2s; display:inline-block; }
.ep-tools-wrap:hover .ep-arrow { transform: rotate(180deg); }
.ep-tools-wrap::after {
    content: ''; position: absolute; top: 100%; left: 0; right: 0;
    height: 14px; display: none;
}
.ep-tools-wrap:hover::after { display: block; }
.ep-dropdown {
    display: none;
    position: absolute; top: calc(100% + 8px);
    left: 50%; transform: translateX(-50%);
    min-width: 220px;
    background: #12151a;
    border: 1px solid #1f2530;
    border-top: 2px solid #4ade80;
    border-radius: 0 0 10px 10px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.95);
    z-index: 999999; padding: 0.2rem 0; overflow: hidden;
}
.ep-tools-wrap:hover .ep-dropdown { display: block; }
.ep-drop-link {
    display: flex; align-items: center; gap: 0.6rem;
    padding: 0.58rem 1rem;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.57rem; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.08em;
    color: #374151 !important;
    text-decoration: none !important;
    border-bottom: 1px solid #0d0f11;
    transition: color 0.12s, background 0.12s, padding-left 0.12s;
}
.ep-drop-link:last-child { border-bottom: none; }
.ep-drop-link:hover {
    color: #4ade80 !important;
    background: rgba(74,222,128,0.04) !important;
    padding-left: 1.4rem !important;
}
.ep-right {
    display: flex; align-items: center;
    gap: 0.65rem; flex-shrink: 0; margin-left: 0.5rem;
}
.ep-beta {
    font-family: 'IBM Plex Mono', monospace; font-size: 0.4rem;
    text-transform: uppercase; letter-spacing: 0.2em; color: #1f2530;
    display: flex; align-items: center; gap: 0.35rem;
}
.ep-dot {
    width: 5px; height: 5px; border-radius: 50%;
    background: #4ade80; flex-shrink: 0;
    animation: ep-pulse 2s ease-in-out infinite;
}
@keyframes ep-pulse {
    0%,100% { opacity:1; box-shadow: 0 0 5px #4ade80; }
    50%      { opacity:0.3; box-shadow: none; }
}
.ep-signup {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.55rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.07em;
    color: #030804 !important;
    background: #4ade80;
    border: none; border-radius: 6px;
    padding: 0.38rem 0.85rem;
    cursor: pointer; white-space: nowrap;
    transition: background 0.15s, box-shadow 0.15s;
    text-decoration: none !important;
    display: inline-flex; align-items: center;
}
.ep-signup:hover {
    background: #6ee7a0 !important;
    box-shadow: 0 0 12px rgba(74,222,128,0.3);
}
.ep-welcome {
    font-family: 'IBM Plex Mono', monospace; font-size: 0.58rem;
    color: #4ade80; font-weight: 600; white-space: nowrap;
}
.ep-signout {
    font-family: 'IBM Plex Mono', monospace; font-size: 0.52rem;
    color: #374151 !important; text-decoration: none !important;
    border: 1px solid #1f2530; border-radius: 6px;
    padding: 0.32rem 0.7rem;
    transition: color 0.15s, border-color 0.15s; white-space: nowrap;
}
.ep-signout:hover { color: #f87171 !important; border-color: #f87171 !important; }
.ep-spacer { height: 1.4rem; }
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
        '<button class="ep-tools-btn">Research <span class="ep-arrow">&#9660;</span></button>'
        '<div class="ep-dropdown">'
        '<a class="ep-drop-link" href="/Earnings" target="_self">Earnings</a>'
        '<a class="ep-drop-link" href="/Correlations" target="_self">Correlations</a>'
        '<a class="ep-drop-link" href="/Whale_Tracker" target="_self">Whale Tracker</a>'
        '<a class="ep-drop-link" href="/Monte_Carlo" target="_self">Monte Carlo</a>'
        '<a class="ep-drop-link" href="/Economic_Calendar" target="_self">Econ Calendar</a>'
        '<a class="ep-drop-link" href="/Market_Heatmap" target="_self">Heatmap</a>'
        '<a class="ep-drop-link" href="/Sector_Rotation" target="_self">Sector Rotation</a>'
        '<a class="ep-drop-link" href="/Screener" target="_self">Screener</a>'
        '<a class="ep-drop-link" href="/Pattern_Recognition" target="_self">Patterns</a>'
        '</div>'
        '</div>'
        '<div class="ep-tools-wrap">'
        '<button class="ep-tools-btn">Tools <span class="ep-arrow">&#9660;</span></button>'
        '<div class="ep-dropdown">'
        '<a class="ep-drop-link" href="/Risk_Calculator" target="_self">Risk Calculator</a>'
        '<a class="ep-drop-link" href="/Options_Chain" target="_self">Options Chain</a>'
        '<a class="ep-drop-link" href="/Portfolio_Tracker" target="_self">Portfolio</a>'
        '<a class="ep-drop-link" href="/Trade_Journal" target="_self">Trade Journal</a>'
        '<a class="ep-drop-link" href="/Trade_Stats" target="_self">Trade Stats</a>'
        '</div>'
        '</div>'
        '</div>'
        + right +
        '</div>'
        '<div class="ep-spacer"></div>'
        '<script>'
        '(function(){'
        '  function nav(url){'
        '    try{ window.top.location.href=url; }'
        '    catch(e){ window.location.href=url; }'
        '  }'
        '  document.querySelectorAll(".ep-navbar a[href]").forEach(function(a){'
        '    a.addEventListener("click",function(e){'
        '      e.preventDefault(); nav(a.getAttribute("href"));'
        '    });'
        '  });'
        '})();'
        '</script>'
    )

    st.markdown(css + body, unsafe_allow_html=True)
