import streamlit as st
from utils.styles import LOGO_IMG


def navbar():
    html = f"""
<style>
.nb {{ display:none!important; }}
.navbar {{
    background:#06080c;
    border-bottom:1px solid #1a2235;
    margin:-2.5rem -2.5rem 0 -2.5rem;
    height:56px;
    display:flex;
    align-items:stretch;
    position:sticky;
    top:0;
    z-index:1000;
    overflow:visible;
}}
.nav-brand {{
    display:flex; align-items:center;
    padding:0 1.4rem; border-right:1px solid #1a2235;
    flex-shrink:0; text-decoration:none;
}}
.nav-brand img {{ height:34px; width:auto; display:block; }}
.nav-links {{
    display:flex; align-items:stretch; flex:1; overflow:visible;
}}
.nav-link {{
    display:inline-flex; align-items:center;
    padding:0 1.1rem; height:56px; box-sizing:border-box;
    font-family:'IBM Plex Mono',monospace; font-size:0.6rem;
    font-weight:600; text-transform:uppercase; letter-spacing:0.1em;
    color:#3a4a5e; text-decoration:none;
    border-bottom:2px solid transparent; border-right:1px solid #1a2235;
    transition:color 0.15s, border-color 0.15s, background 0.15s;
    white-space:nowrap;
}}
.nav-link:hover {{
    color:#eef2f7; background:rgba(255,255,255,0.02); border-bottom-color:#2a3550;
}}
.nav-tools {{
    position:relative; display:flex; align-items:stretch;
    border-right:1px solid #1a2235;
}}
.nav-tools-btn {{
    display:inline-flex; align-items:center; gap:0.5rem;
    padding:0 1.1rem; height:56px; box-sizing:border-box;
    font-family:'IBM Plex Mono',monospace; font-size:0.6rem;
    font-weight:600; text-transform:uppercase; letter-spacing:0.1em;
    color:#3a4a5e; background:transparent; border:none;
    border-bottom:2px solid transparent; cursor:pointer; white-space:nowrap;
    transition:color 0.15s, background 0.15s;
}}
.nav-tools-btn:hover {{ color:#eef2f7; background:rgba(255,255,255,0.02); }}
.nav-tools-btn .arr {{ font-size:0.45rem; transition:transform 0.2s; display:inline-block; }}
.nav-tools:hover .arr {{ transform:rotate(180deg); }}
.nav-dropdown {{
    display:none; position:absolute; top:55px; left:0; min-width:190px;
    background:#0c1018; border:1px solid #1a2235; border-top:2px solid #00e676;
    border-radius:0 0 8px 8px; box-shadow:0 16px 48px rgba(0,0,0,0.7); z-index:2000;
}}
.nav-tools:hover .nav-dropdown {{ display:block; }}
.nav-dropdown a {{
    display:flex; align-items:center; gap:0.6rem; padding:0.65rem 1.2rem;
    font-family:'IBM Plex Mono',monospace; font-size:0.58rem; font-weight:600;
    text-transform:uppercase; letter-spacing:0.1em; color:#3a4a5e;
    text-decoration:none; border-bottom:1px solid #111927;
    transition:color 0.12s, background 0.12s, padding-left 0.15s;
}}
.nav-dropdown a:last-child {{ border-bottom:none; }}
.nav-dropdown a:hover {{ color:#00e676; background:rgba(0,230,118,0.04); padding-left:1.6rem; }}
.nav-dropdown a::before {{
    content:''; display:inline-block; width:4px; height:4px;
    border-radius:50%; background:currentColor; opacity:0.5; flex-shrink:0;
}}
.nav-beta {{
    display:flex; align-items:center; padding:0 1.2rem; margin-left:auto;
    gap:0.5rem; font-family:'IBM Plex Mono',monospace; font-size:0.44rem;
    text-transform:uppercase; letter-spacing:0.22em; color:#3a4a5e;
    border-left:1px solid #1a2235; white-space:nowrap; flex-shrink:0;
}}
.nav-live-dot {{
    display:inline-block; width:5px; height:5px; border-radius:50%;
    background:#00e676; animation:livepulse 2s ease-in-out infinite; flex-shrink:0;
}}
@keyframes livepulse {{
    0%,100%{{opacity:1;box-shadow:0 0 6px #00e676}} 50%{{opacity:0.3;box-shadow:none}}
}}
</style>

<div class="navbar">
    <a class="nav-brand" href="/" target="_self">{LOGO_IMG}</a>
    <div class="nav-links">
        <a class="nav-link" href="/" target="_self">Home</a>
        <a class="nav-link" href="/Strategy_Lab" target="_self">Strategy Lab</a>
        <a class="nav-link" href="/Replay" target="_self">Replay</a>
        <a class="nav-link" href="/Analysis" target="_self">Analysis</a>
        <a class="nav-link" href="/Assistant" target="_self">AI Coach</a>
        <div class="nav-tools">
            <button class="nav-tools-btn">Tools <span class="arr">▼</span></button>
            <div class="nav-dropdown">
                <a href="/Earnings" target="_self">📅 Earnings</a>
                <a href="/Correlations" target="_self">⬡ Correlations</a>
                <a href="/Whale_Tracker" target="_self">🐋 Whale Tracker</a>
                <a href="/Monte_Carlo" target="_self">〰 Monte Carlo</a>
            </div>
        </div>
    </div>
    <div class="nav-beta"><span class="nav-live-dot"></span>Beta</div>
</div>
<div style="margin-bottom:1.5rem;"></div>
"""
    st.markdown(html, unsafe_allow_html=True)
