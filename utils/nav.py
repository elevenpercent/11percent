import streamlit as st
import streamlit.components.v1 as components
from utils.styles import LOGO_IMG


def navbar():
    # st.components.v1.html bypasses Streamlit's HTML sanitizer entirely
    # This is why raw HTML was showing — st.markdown sanitizes in some contexts
    
    css = """
<style>
*{box-sizing:border-box;margin:0;padding:0;}
body{background:transparent;}
.ep-navbar{background:#06080c;border-bottom:1px solid #1a2235;height:64px;display:flex;align-items:center;padding:0 1.8rem;width:100%;}
.ep-brand{display:flex;align-items:center;flex-shrink:0;text-decoration:none;}
.ep-brand img{height:46px!important;width:auto!important;display:block;}
.ep-center{flex:1;display:flex;align-items:center;justify-content:center;gap:2px;}
.nav-pill{font-family:'IBM Plex Mono',monospace;font-size:0.59rem;font-weight:600;text-transform:uppercase;letter-spacing:0.1em;color:#3a4a5e;background:transparent;border:1px solid transparent;border-radius:7px;padding:0.42rem 0.95rem;cursor:pointer;transition:color 0.15s,background 0.15s,border-color 0.15s;white-space:nowrap;outline:none;line-height:1;text-decoration:none;display:inline-flex;align-items:center;}
.nav-pill:hover{color:#eef2f7!important;background:rgba(255,255,255,0.06)!important;border-color:#1a2235!important;}
.ep-tools{position:relative;display:inline-flex;align-items:center;}
.ep-tools-btn{font-family:'IBM Plex Mono',monospace;font-size:0.59rem;font-weight:600;text-transform:uppercase;letter-spacing:0.1em;color:#3a4a5e;background:transparent;border:1px solid transparent;border-radius:7px;padding:0.42rem 0.95rem;cursor:pointer;display:inline-flex;align-items:center;gap:0.4rem;transition:color 0.15s,background 0.15s,border-color 0.15s;outline:none;white-space:nowrap;line-height:1;}
.ep-tools-btn:hover{color:#eef2f7!important;background:rgba(255,255,255,0.06)!important;border-color:#1a2235!important;}
.ep-arr{font-size:0.38rem;opacity:0.6;transition:transform 0.2s;display:inline-block;}
.ep-tools:hover .ep-arr{transform:rotate(180deg);}
.ep-dropdown{display:none;position:absolute;top:calc(100% + 4px);left:50%;transform:translateX(-50%);min-width:180px;background:#0d1117;border:1px solid #1a2235;border-top:2px solid #00e676;border-radius:0 0 10px 10px;box-shadow:0 24px 64px rgba(0,0,0,0.85);z-index:10000;padding:0.3rem 0;overflow:hidden;}
.ep-tools:hover .ep-dropdown{display:block;}
.nav-drop-item{display:flex;align-items:center;gap:0.7rem;padding:0.62rem 1.1rem;font-family:'IBM Plex Mono',monospace;font-size:0.58rem;font-weight:600;text-transform:uppercase;letter-spacing:0.09em;color:#3a4a5e;cursor:pointer;text-decoration:none;transition:color 0.12s,background 0.12s,padding-left 0.14s;}
.nav-drop-item:hover{color:#00e676!important;background:rgba(0,230,118,0.06)!important;padding-left:1.5rem!important;}
.ep-right{display:flex;align-items:center;gap:0.75rem;flex-shrink:0;}
.ep-beta{font-family:'IBM Plex Mono',monospace;font-size:0.42rem;text-transform:uppercase;letter-spacing:0.22em;color:#2a3550;display:flex;align-items:center;gap:0.4rem;}
.ep-dot{width:5px;height:5px;border-radius:50%;background:#00e676;flex-shrink:0;animation:ep-pulse 2s ease-in-out infinite;}
@keyframes ep-pulse{0%,100%{opacity:1;box-shadow:0 0 6px #00e676}50%{opacity:0.3;box-shadow:none}}
.ep-signup{font-family:'IBM Plex Mono',monospace;font-size:0.56rem;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;color:#000!important;background:#00e676;border:none;border-radius:6px;padding:0.42rem 0.9rem;cursor:pointer;white-space:nowrap;transition:background 0.15s,box-shadow 0.15s;outline:none;text-decoration:none!important;display:inline-flex;align-items:center;}
.ep-signup:hover{background:#00ff88!important;box-shadow:0 0 14px rgba(0,230,118,0.45)!important;}
</style>"""

    body = """
<div class="ep-navbar">
  <a class="ep-brand" href="/" target="_parent">{logo}</a>
  <div class="ep-center">
    <a class="nav-pill" href="/" target="_parent">Home</a>
    <a class="nav-pill" href="/Strategy_Lab" target="_parent">Strategy Lab</a>
    <a class="nav-pill" href="/Replay" target="_parent">Replay</a>
    <a class="nav-pill" href="/Analysis" target="_parent">Analysis</a>
    <a class="nav-pill" href="/Assistant" target="_parent">AI Coach</a>
    <div class="ep-tools">
      <button class="ep-tools-btn">Tools <span class="ep-arr">&#9660;</span></button>
      <div class="ep-dropdown">
        <a class="nav-drop-item" href="/Earnings" target="_parent">Earnings</a>
        <a class="nav-drop-item" href="/Correlations" target="_parent">Correlations</a>
        <a class="nav-drop-item" href="/Whale_Tracker" target="_parent">Whale Tracker</a>
        <a class="nav-drop-item" href="/Monte_Carlo" target="_parent">Monte Carlo</a>
      </div>
    </div>
  </div>
  <div class="ep-right">
    <div class="ep-beta"><span class="ep-dot"></span>Beta</div>
    <a class="ep-signup" href="/Login" target="_parent">Sign Up</a>
  </div>
</div>""".format(logo=LOGO_IMG)

    # Use components.html — immune to Streamlit's HTML sanitizer
    components.html(css + body, height=66, scrolling=False)
    
    # Add negative margin to pull content up flush
    st.markdown("""
<style>
/* Pull the iframe flush - remove gap between navbar and content */
iframe[title="st.iframe"] {
    display: block;
    margin-bottom: -1rem;
}
</style>
""", unsafe_allow_html=True)
