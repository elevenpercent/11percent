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
            '<a class="ep-signout" href="/Login">Sign Out</a>'
            '</div>'
        )
    else:
        right = (
            '<div class="ep-right">'
            '<div class="ep-beta"><span class="ep-dot"></span>Beta</div>'
            '<a class="ep-signup" href="/Login">Sign Up</a>'
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
    background: #0f1318;
    border-bottom: 1px solid #243040;
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
    color: #3d5068 !important;
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
    color: #e8edf2 !important;
    background: rgba(255,255,255,0.05) !important;
    border-color: #243040 !important;
}
.ep-tools-wrap {
    position: relative; display: inline-flex; align-items: center;
}
.ep-tools-btn {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.58rem; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.09em;
    color: #3d5068;
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
    color: #e8edf2;
    background: rgba(255,255,255,0.05);
    border-color: #243040;
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
    background: #141a1f;
    border: 1px solid #243040;
    border-top: 2px solid #26d97f;
    border-radius: 0 0 10px 10px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.9);
    z-index: 999999; padding: 0.2rem 0; overflow: hidden;
}
.ep-tools-wrap:hover .ep-dropdown { display: block; }
.ep-drop-link {
    display: flex; align-items: center; gap: 0.6rem;
    padding: 0.58rem 1rem;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.57rem; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.08em;
    color: #3d5068 !important;
    text-decoration: none !important;
    border-bottom: 1px solid #0f1318;
    transition: color 0.12s, background 0.12s, padding-left 0.12s;
}
.ep-drop-link:last-child { border-bottom: none; }
.ep-drop-link:hover {
    color: #26d97f !important;
    background: rgba(38,217,127,0.05) !important;
    padding-left: 1.4rem !important;
}
.ep-right {
    display: flex; align-items: center;
    gap: 0.65rem; flex-shrink: 0; margin-left: 0.5rem;
}
.ep-beta {
    font-family: 'IBM Plex Mono', monospace; font-size: 0.4rem;
    text-transform: uppercase; letter-spacing: 0.2em; color: #243040;
    display: flex; align-items: center; gap: 0.35rem;
}
.ep-dot {
    width: 5px; height: 5px; border-radius: 50%;
    background: #26d97f; flex-shrink: 0;
    animation: ep-pulse 2s ease-in-out infinite;
}
@keyframes ep-pulse {
    0%,100% { opacity:1; box-shadow: 0 0 5px #26d97f; }
    50%      { opacity:0.3; box-shadow: none; }
}
.ep-signup {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.55rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.07em;
    color: #000 !important;
    background: #26d97f;
    border: none; border-radius: 6px;
    padding: 0.38rem 0.85rem;
    cursor: pointer; white-space: nowrap;
    transition: background 0.15s, box-shadow 0.15s;
    text-decoration: none !important;
    display: inline-flex; align-items: center;
}
.ep-signup:hover {
    background: #30f090 !important;
    box-shadow: 0 0 12px rgba(38,217,127,0.4);
}
.ep-welcome {
    font-family: 'IBM Plex Mono', monospace; font-size: 0.58rem;
    color: #26d97f; font-weight: 600; white-space: nowrap;
}
.ep-signout {
    font-family: 'IBM Plex Mono', monospace; font-size: 0.52rem;
    color: #3d5068 !important; text-decoration: none !important;
    border: 1px solid #243040; border-radius: 6px;
    padding: 0.32rem 0.7rem;
    transition: color 0.15s, border-color 0.15s; white-space: nowrap;
}
.ep-signout:hover { color: #e84040 !important; border-color: #e84040 !important; }
.ep-spacer { height: 1.4rem; }
</style>"""

    body = (
        '<div class="ep-navbar">'
        '<a class="ep-brand" href="/">' + LOGO_IMG + '</a>'
        '<div class="ep-center">'
        '<a class="ep-pill" href="/">Home</a>'
        '<a class="ep-pill" href="/Strategy_Lab">Strategy Lab</a>'
        '<a class="ep-pill" href="/Replay">Replay</a>'
        '<a class="ep-pill" href="/Analysis">Analysis</a>'
        '<a class="ep-pill" href="/Assistant">AI Coach</a>'
        '<div class="ep-tools-wrap">'
        '<button class="ep-tools-btn">Research <span class="ep-arrow">&#9660;</span></button>'
        '<div class="ep-dropdown">'
        '<a class="ep-drop-link" href="/Earnings">Earnings</a>'
        '<a class="ep-drop-link" href="/Correlations">Correlations</a>'
        '<a class="ep-drop-link" href="/Whale_Tracker">Whale Tracker</a>'
        '<a class="ep-drop-link" href="/Monte_Carlo">Monte Carlo</a>'
        '<a class="ep-drop-link" href="/Economic_Calendar">Econ Calendar</a>'
        '<a class="ep-drop-link" href="/Market_Heatmap">Heatmap</a>'
        '<a class="ep-drop-link" href="/Sector_Rotation">Sector Rotation</a>'
        '<a class="ep-drop-link" href="/Screener">Screener</a>'
        '<a class="ep-drop-link" href="/Pattern_Recognition">Patterns</a>'
        '</div>'
        '</div>'
        '<div class="ep-tools-wrap">'
        '<button class="ep-tools-btn">Tools <span class="ep-arrow">&#9660;</span></button>'
        '<div class="ep-dropdown">'
        '<a class="ep-drop-link" href="/Risk_Calculator">Risk Calculator</a>'
        '<a class="ep-drop-link" href="/Options_Chain">Options Chain</a>'
        '<a class="ep-drop-link" href="/Portfolio_Tracker">Portfolio</a>'
        '<a class="ep-drop-link" href="/Trade_Journal">Trade Journal</a>'
        '<a class="ep-drop-link" href="/Trade_Stats">Trade Stats</a>'
        '</div>'
        '</div>'
        '</div>'
        + right +
        '</div>'
        '<div class="ep-spacer"></div>'
        # Navigation JS — routes all navbar clicks via window.top to fix URL updates
        '<script>'
        '(function(){'
        '  function nav(url){'
        '    try{ window.top.location.href=url; }'
        '    catch(e){ window.location.href=url; }'
        '  }'
        '  document.querySelectorAll(".ep-navbar a[href], .ep-drop-link[href], .ep-pill[href], .ep-brand[href], .ep-signup[href], .ep-signout[href]").forEach(function(a){'
        '    a.addEventListener("click",function(e){'
        '      e.preventDefault(); nav(a.getAttribute("href"));'
        '    });'
        '  });'
        '})();'
        '</script>'
    )

    st.markdown(css + body, unsafe_allow_html=True)
