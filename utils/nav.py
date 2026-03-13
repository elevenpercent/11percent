import streamlit as st
from utils.styles import LOGO_IMG


def navbar():
    # On Streamlit Cloud, pages are served at /<PageName> (underscores, no number prefix)
    # Use st.page_link for proper SPA-style navigation that updates the URL bar
    st.markdown(f"""
<style>
.nb {{ display:none!important; }}
/* Inject navbar shell */
div[data-testid="stVerticalBlock"]:has(> div > .navbar-shell) {{
    margin-top:0!important;
}}
.navbar-shell {{
    background:#06080c;
    border-bottom:1px solid #1a2235;
    margin:-2.5rem -2.5rem 0 -2.5rem;
    height:64px;
    display:flex;
    align-items:center;
    position:sticky;
    top:0;
    z-index:1000;
    padding:0 1.8rem;
    overflow:visible;
}}
.nav-brand img {{
    height:44px!important; width:auto!important; display:block;
}}
/* The center col that holds page_links */
.nav-center-wrap {{
    display:flex; align-items:center; justify-content:center;
    flex:1; gap:2px; overflow:visible;
}}
/* Override Streamlit's page_link styling to look like pills */
.nav-center-wrap [data-testid="stPageLink-NavLink"] {{
    font-family:'IBM Plex Mono',monospace!important;
    font-size:0.6rem!important; font-weight:600!important;
    text-transform:uppercase!important; letter-spacing:0.1em!important;
    color:#3a4a5e!important; text-decoration:none!important;
    padding:0.38rem 0.9rem!important;
    border-radius:6px!important;
    border:1px solid transparent!important;
    background:transparent!important;
    transition:all 0.18s ease!important;
    white-space:nowrap!important;
    display:inline-flex!important; align-items:center!important;
    height:auto!important; line-height:1!important;
}}
.nav-center-wrap [data-testid="stPageLink-NavLink"]:hover {{
    color:#eef2f7!important;
    background:rgba(255,255,255,0.05)!important;
    border-color:#1a2235!important;
}}
.nav-center-wrap [data-testid="stPageLink-NavLink"][aria-current="page"] {{
    color:#00e676!important;
    background:rgba(0,230,118,0.07)!important;
    border-color:rgba(0,230,118,0.2)!important;
}}
/* Tools dropdown (pure HTML — no routing) */
.nav-tools {{ position:relative; display:inline-flex; align-items:center; }}
.nav-tools-pill {{
    display:inline-flex; align-items:center; gap:0.4rem;
    padding:0.38rem 0.9rem;
    font-family:'IBM Plex Mono',monospace; font-size:0.6rem;
    font-weight:600; text-transform:uppercase; letter-spacing:0.1em;
    color:#3a4a5e; background:transparent;
    border:1px solid transparent; border-radius:6px;
    cursor:pointer; transition:all 0.18s ease; white-space:nowrap;
}}
.nav-tools-pill:hover {{
    color:#eef2f7; background:rgba(255,255,255,0.05); border-color:#1a2235;
}}
.nav-tools-pill .arr {{ font-size:0.4rem; transition:transform 0.2s; }}
.nav-tools:hover .arr {{ transform:rotate(180deg); }}
.nav-dropdown {{
    display:none; position:absolute; top:calc(100% + 8px); left:50%;
    transform:translateX(-50%); min-width:200px;
    background:#0c1018; border:1px solid #1a2235; border-top:2px solid #00e676;
    border-radius:8px; box-shadow:0 20px 60px rgba(0,0,0,0.8); z-index:3000; padding:0.3rem 0;
}}
.nav-tools:hover .nav-dropdown {{ display:block; }}
.nav-dropdown a {{
    display:flex; align-items:center; gap:0.7rem; padding:0.6rem 1.1rem;
    font-family:'IBM Plex Mono',monospace; font-size:0.58rem;
    font-weight:600; text-transform:uppercase; letter-spacing:0.1em;
    color:#3a4a5e; text-decoration:none;
    transition:color 0.12s, background 0.12s, padding-left 0.15s;
    border-radius:4px; margin:0 0.3rem;
}}
.nav-dropdown a:hover {{ color:#00e676; background:rgba(0,230,118,0.06); padding-left:1.4rem; }}
/* Right side */
.nav-right-html {{
    display:flex; align-items:center; gap:0.8rem; flex-shrink:0;
}}
.nav-beta {{
    font-family:'IBM Plex Mono',monospace; font-size:0.44rem;
    text-transform:uppercase; letter-spacing:0.22em; color:#2a3550;
    display:flex; align-items:center; gap:0.4rem;
}}
.nav-live-dot {{
    width:5px; height:5px; border-radius:50%; background:#00e676;
    animation:livepulse 2s ease-in-out infinite; flex-shrink:0;
}}
@keyframes livepulse {{
    0%,100%{{opacity:1;box-shadow:0 0 6px #00e676}} 50%{{opacity:0.3;box-shadow:none}}
}}
.nav-signup {{
    display:inline-flex; align-items:center;
    padding:0.38rem 1rem;
    font-family:'IBM Plex Mono',monospace; font-size:0.58rem;
    font-weight:700; text-transform:uppercase; letter-spacing:0.1em;
    color:#000!important; background:#00e676; border:none; border-radius:6px;
    cursor:pointer; text-decoration:none!important; transition:all 0.18s ease; white-space:nowrap;
}}
.nav-signup:hover {{ background:#00ff88; box-shadow:0 0 16px rgba(0,230,118,0.4); }}
/* Nuke Streamlit column padding inside navbar */
.navbar-shell [data-testid="stHorizontalBlock"] {{
    gap:0!important; align-items:center!important; flex-wrap:nowrap!important;
}}
.navbar-shell [data-testid="column"] {{ padding:0!important; }}
</style>
""", unsafe_allow_html=True)

    # Build navbar using columns so page_link works (updates URL on Streamlit Cloud)
    with st.container():
        st.markdown('<div class="navbar-shell">', unsafe_allow_html=True)

        # Logo (HTML — just an image, no routing needed)
        logo_col, center_col, right_col = st.columns([1, 5, 1.2])

        with logo_col:
            st.markdown(
                f'<div style="display:flex;align-items:center;height:64px;">'
                f'<a href="/" target="_self" style="display:flex;align-items:center;text-decoration:none;">'
                f'{LOGO_IMG}</a></div>',
                unsafe_allow_html=True
            )

        with center_col:
            st.markdown('<div class="nav-center-wrap">', unsafe_allow_html=True)
            # page_link handles Streamlit Cloud routing + URL bar updates
            link_cols = st.columns([1,1.3,1,1.2,1.1,1])
            pages = [
                ("app",                     "Home"),
                ("pages/1_Strategy_Lab",    "Strategy Lab"),
                ("pages/3_Replay",          "Replay"),
                ("pages/4_Analysis",        "Analysis"),
                ("pages/5_Assistant",       "AI Coach"),
            ]
            for col, (page, label) in zip(link_cols[:5], pages):
                with col:
                    st.page_link(f"{page}.py", label=label)
            with link_cols[5]:
                st.markdown(
                    '<div class="nav-tools">'
                    '<button class="nav-tools-pill">Tools <span class="arr">▼</span></button>'
                    '<div class="nav-dropdown">'
                    '<a href="/Earnings" target="_self">📅&nbsp; Earnings</a>'
                    '<a href="/Correlations" target="_self">⬡&nbsp; Correlations</a>'
                    '<a href="/Whale_Tracker" target="_self">🐋&nbsp; Whale Tracker</a>'
                    '<a href="/Monte_Carlo" target="_self">〰&nbsp; Monte Carlo</a>'
                    '</div></div>',
                    unsafe_allow_html=True
                )
            st.markdown('</div>', unsafe_allow_html=True)

        with right_col:
            st.markdown(
                '<div style="display:flex;align-items:center;justify-content:flex-end;height:64px;gap:0.8rem;">'
                '<div class="nav-beta"><span class="nav-live-dot"></span>Beta</div>'
                '<a class="nav-signup" href="/Login" target="_self">Sign Up</a>'
                '</div>',
                unsafe_allow_html=True
            )

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div style="margin-bottom:1.5rem;"></div>', unsafe_allow_html=True)
