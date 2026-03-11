"""Shared styles for 11% platform."""
import base64, os

def _logo_b64():
    p = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "logo.png")
    if os.path.exists(p):
        with open(p, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

LOGO_B64 = _logo_b64()
LOGO_IMG = f'<img src="data:image/png;base64,{LOGO_B64}" style="height:34px;width:auto;display:block;" alt="11%">' if LOGO_B64 else '<span style="font-family:Bebas Neue,sans-serif;font-size:1.6rem;"><span style="color:#00e676;">11</span><span style="color:#ff3d57;">%</span></span>'

def navbar_html(pages):
    """
    pages: list of (path, label) tuples
    Returns the opening HTML for navbar. Must be followed by st.columns page_links then closing HTML.
    """
    return (
        '<div class="nb">'
        '<div class="nb-brand">' + LOGO_IMG + '</div>'
        '<div class="nb-links">'
    )

NAVBAR_CLOSE = '</div><div class="nb-tag"><span class="live-dot"></span>BETA</div></div>'

SHARED_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=IBM+Plex+Mono:wght@300;400;600;700&family=Space+Grotesk:wght@300;400;500;600;700&display=swap');

    :root {
        --bg:#06080c;
        --surface:#0c1018;
        --surface2:#101520;
        --border:#1a2235;
        --border2:#2a3550;
        --green:#00e676;
        --green-dim:rgba(0,230,118,0.07);
        --green-glow:rgba(0,230,118,0.18);
        --red:#ff3d57;
        --red-dim:rgba(255,61,87,0.07);
        --blue:#4da6ff;
        --purple:#b388ff;
        --yellow:#ffd166;
        --orange:#ff9f43;
        --text:#eef2f7;
        --text2:#8896ab;
        --muted:#3a4a5e;
        --grid:rgba(255,255,255,0.016);
        --radius:10px;
        --radius-sm:6px;
    }

    html, body,
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"],
    .main {
        background-color: var(--bg) !important;
        color: var(--text) !important;
        font-family: 'Space Grotesk', sans-serif !important;
    }

    [data-testid="stMain"] {
        background-image:
            linear-gradient(var(--grid) 1px, transparent 1px),
            linear-gradient(90deg, var(--grid) 1px, transparent 1px) !important;
        background-size: 48px 48px !important;
        padding-top: 0 !important;
        margin-top: 0 !important;
    }

    .block-container {
        padding-top: 0 !important;
        padding-left: 2.5rem !important;
        padding-right: 2.5rem !important;
        max-width: 1440px !important;
        margin: 0 auto !important;
        border: none !important;
        background: transparent !important;
        box-shadow: none !important;
    }

    /* Kill ALL Streamlit chrome */
    header[data-testid="stHeader"]  { display:none!important; height:0!important; min-height:0!important; }
    [data-testid="stToolbar"]        { display:none!important; }
    [data-testid="stDecoration"]     { display:none!important; }
    [data-testid="stSidebar"]        { display:none!important; }
    [data-testid="stSidebarNav"]     { display:none!important; }
    [data-testid="collapsedControl"] { display:none!important; }
    footer                           { display:none!important; }
    #MainMenu                        { display:none!important; }
    .stDeployButton                  { display:none!important; }

    /* Kill ghost boxes */
    [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlockBorderWrapper"],
    [data-testid="stVerticalBlockBorderWrapper"] {
        background:transparent!important; border:none!important;
        box-shadow:none!important; padding:0!important;
    }
    [data-testid="stElementContainer"],
    [data-testid="stHorizontalBlock"],
    [data-testid="element-container"] {
        background:transparent!important; border:none!important; box-shadow:none!important;
    }

    /* ── Typography ── */
    h1 { font-family:'Bebas Neue',sans-serif!important; letter-spacing:0.05em; color:var(--text)!important; font-size:3rem!important; margin:0!important; line-height:1!important; }
    h2 { font-family:'Bebas Neue',sans-serif!important; color:var(--text)!important; }
    p  { color:var(--text2); line-height:1.7; }

    /* ── Inputs ── */
    .stTextInput input,.stNumberInput input {
        background:var(--surface)!important; border:1px solid var(--border)!important;
        color:var(--text)!important; font-family:'IBM Plex Mono',monospace!important;
        font-size:0.875rem!important; border-radius:var(--radius-sm)!important;
        padding:0.5rem 0.75rem!important; transition:border-color 0.2s,box-shadow 0.2s!important;
    }
    .stTextInput input:focus,.stNumberInput input:focus {
        border-color:var(--green)!important; box-shadow:0 0 0 3px var(--green-glow)!important;
    }
    div[data-baseweb="select"] > div {
        background:var(--surface)!important; border:1px solid var(--border)!important;
        color:var(--text)!important; font-family:'IBM Plex Mono',monospace!important;
        border-radius:var(--radius-sm)!important;
    }
    .stDateInput input {
        background:var(--surface)!important; border:1px solid var(--border)!important;
        color:var(--text)!important; font-family:'IBM Plex Mono',monospace!important;
        border-radius:var(--radius-sm)!important;
    }
    label {
        font-family:'IBM Plex Mono',monospace!important; font-size:0.63rem!important;
        color:var(--muted)!important; text-transform:uppercase!important;
        letter-spacing:0.12em!important; margin-bottom:0.3rem!important;
    }

    /* ── Buttons ── */
    .stButton>button {
        background:transparent!important; color:var(--green)!important;
        border:1px solid var(--border)!important; border-radius:var(--radius-sm)!important;
        font-family:'IBM Plex Mono',monospace!important; font-weight:600!important;
        font-size:0.72rem!important; letter-spacing:0.1em!important;
        padding:0.5rem 1.4rem!important; transition:all 0.2s!important;
        text-transform:uppercase!important;
    }
    .stButton>button:hover { background:var(--green)!important; color:#000!important; border-color:var(--green)!important; box-shadow:0 0 16px var(--green-glow)!important; }
    .stButton>button[kind="primary"] { background:var(--green)!important; color:#000!important; border-color:var(--green)!important; font-weight:700!important; }
    .stButton>button[kind="primary"]:hover { box-shadow:0 0 20px var(--green-glow)!important; }

    /* ── Cards ── */
    .metric-card { background:var(--surface); border:1px solid var(--border); padding:1rem 1.2rem; border-radius:var(--radius); text-align:center; transition:border-color 0.2s,transform 0.2s; }
    .metric-card:hover { border-color:var(--border2); transform:translateY(-1px); }
    .metric-val { font-family:'IBM Plex Mono',monospace; font-size:1.15rem; font-weight:700; letter-spacing:-0.01em; }
    .metric-lbl { font-family:'IBM Plex Mono',monospace; font-size:0.52rem; color:var(--muted); text-transform:uppercase; letter-spacing:0.14em; margin-top:0.35rem; }
    .pos { color:var(--green); } .neg { color:var(--red); } .neu { color:var(--text); }

    .panel { background:var(--surface); border:1px solid var(--border); border-radius:var(--radius); padding:1.5rem; margin-bottom:1.5rem; }
    .panel-sm { background:var(--surface); border:1px solid var(--border); border-radius:var(--radius); padding:1rem; margin-bottom:1rem; }
    .config-panel { background:var(--surface); border:1px solid var(--border); border-radius:var(--radius); padding:1.4rem 1.4rem 1rem 1.4rem; margin-bottom:1.5rem; }

    /* ── Dividers ── */
    .divider,.price-divider { display:flex; align-items:center; gap:1rem; margin:2rem 0 1.2rem 0; font-family:'IBM Plex Mono',monospace; font-size:0.58rem; color:var(--muted); letter-spacing:0.2em; text-transform:uppercase; }
    .divider::before,.divider::after,.price-divider::before,.price-divider::after { content:''; flex:1; height:1px; background:var(--border); }

    /* ── Navbar ── */
    .nb {
        background:rgba(6,8,12,0.97);
        backdrop-filter:blur(20px); -webkit-backdrop-filter:blur(20px);
        border-bottom:1px solid var(--border);
        margin:-3.5rem -2.5rem 0 -2.5rem;
        display:flex; align-items:stretch;
        height:54px; position:sticky; top:0; z-index:1000; padding:0;
    }
    .nb-brand { padding:0 1.4rem; border-right:1px solid var(--border); display:flex; align-items:center; flex-shrink:0; height:54px; }
    .nb-links { display:flex; align-items:stretch; flex:1; height:54px; }
    .nb-tag { font-family:'IBM Plex Mono',monospace; font-size:0.48rem; color:var(--muted); letter-spacing:0.22em; padding:0 1.4rem; display:flex; align-items:center; border-left:1px solid var(--border); text-transform:uppercase; white-space:nowrap; height:54px; gap:0.4rem; }
    .live-dot { display:inline-block; width:6px; height:6px; border-radius:50%; background:var(--green); animation:livepulse 2s ease-in-out infinite; flex-shrink:0; }
    @keyframes livepulse { 0%,100%{opacity:1;box-shadow:0 0 4px var(--green)} 50%{opacity:0.4;box-shadow:none} }

    .nb-links [data-testid="stPageLink-NavLink"] {
        font-family:'IBM Plex Mono',monospace!important; font-size:0.62rem!important;
        font-weight:600!important; text-transform:uppercase!important;
        letter-spacing:0.14em!important; color:var(--muted)!important;
        text-decoration:none!important; padding:0 1rem!important;
        border-radius:0!important; border:none!important;
        border-bottom:2px solid transparent!important;
        background:transparent!important; display:flex!important;
        align-items:center!important; height:54px!important;
        transition:color 0.15s,border-color 0.15s!important; white-space:nowrap!important;
    }
    .nb-links [data-testid="stPageLink-NavLink"]:hover { color:var(--text)!important; border-bottom-color:var(--border2)!important; }
    .nb-links [data-testid="stPageLink-NavLink"][aria-current="page"] { color:var(--green)!important; border-bottom-color:var(--green)!important; }
    .nb-links [data-testid="stHorizontalBlock"] { gap:0!important; height:54px!important; align-items:stretch!important; }
    .nb-links [data-testid="column"] { display:flex!important; align-items:stretch!important; padding:0!important; }

    /* ── Page header ── */
    .page-header { padding:2.8rem 0 1.8rem 0; margin-bottom:0.5rem; position:relative; }
    .page-header-eyebrow { font-family:'IBM Plex Mono',monospace; font-size:0.56rem; color:var(--green); text-transform:uppercase; letter-spacing:0.28em; margin-bottom:0.7rem; display:flex; align-items:center; gap:0.6rem; }
    .page-header-eyebrow::before { content:''; display:inline-block; width:18px; height:1px; background:var(--green); }
    .page-header h1 { font-size:3rem!important; margin:0 0 0.55rem 0!important; line-height:1!important; }
    .page-header p { color:var(--text2); font-size:0.93rem; margin:0; max-width:560px; line-height:1.75; }
    .page-header::after { content:''; display:block; width:36px; height:3px; background:linear-gradient(90deg,var(--green),transparent); margin-top:1.1rem; border-radius:2px; }

    /* ── Beta badge ── */
    .beta-badge { display:inline-block; font-family:'IBM Plex Mono',monospace; font-size:0.48rem; padding:2px 7px; border-radius:3px; text-transform:uppercase; letter-spacing:0.18em; background:rgba(255,209,102,0.1); color:var(--yellow); border:1px solid rgba(255,209,102,0.25); vertical-align:middle; margin-left:0.6rem; }

    /* ── Status boxes ── */
    .info-box { background:var(--green-dim); border:1px solid rgba(0,230,118,0.2); border-radius:var(--radius-sm); padding:0.75rem 1rem; font-size:0.8rem; color:var(--green); font-family:'IBM Plex Mono',monospace; line-height:1.5; }
    .warn-box  { background:var(--red-dim);   border:1px solid rgba(255,61,87,0.2);  border-radius:var(--radius-sm); padding:0.75rem 1rem; font-size:0.8rem; color:var(--red);   font-family:'IBM Plex Mono',monospace; line-height:1.5; }

    /* ── Chat ── */
    .chat-user { background:var(--surface2); border:1px solid var(--border); border-radius:12px 12px 4px 12px; padding:1rem 1.25rem; margin:1rem 0 0.5rem 3rem; font-size:0.9rem; line-height:1.65; color:var(--text); }
    .chat-ai   { background:linear-gradient(135deg,#051510,#08180e); border:1px solid rgba(0,230,118,0.15); border-radius:4px 12px 12px 12px; padding:1.1rem 1.25rem; margin:0.5rem 3rem 1rem 0; font-size:0.9rem; line-height:1.75; color:var(--text2); }
    .chat-lbl  { font-family:'IBM Plex Mono',monospace; font-size:0.6rem; text-transform:uppercase; letter-spacing:0.15em; color:var(--muted); margin-bottom:0.5rem; display:flex; align-items:center; gap:0.4rem; }
    .chat-lbl .dot { width:6px; height:6px; border-radius:50%; background:var(--green); display:inline-block; }

    /* ── Feature cards ── */
    .feat-card { background:var(--surface); border:1px solid var(--border); border-radius:var(--radius); padding:1.5rem; height:100%; transition:border-color 0.2s,transform 0.2s,box-shadow 0.2s; position:relative; overflow:hidden; }
    .feat-card::before { content:''; position:absolute; top:0; left:0; right:0; height:2px; background:linear-gradient(90deg,var(--green),transparent); opacity:0; transition:opacity 0.2s; }
    .feat-card:hover { border-color:var(--border2); transform:translateY(-2px); box-shadow:0 8px 32px rgba(0,0,0,0.4); }
    .feat-card:hover::before { opacity:1; }
    .feat-icon  { font-size:1.5rem; margin-bottom:0.8rem; }
    .feat-title { font-family:'IBM Plex Mono',monospace; font-size:0.7rem; font-weight:700; text-transform:uppercase; letter-spacing:0.18em; color:var(--text); margin-bottom:0.5rem; }
    .feat-desc  { font-size:0.82rem; color:var(--text2); line-height:1.6; }

    /* ── Tags ── */
    .tag { display:inline-block; font-family:'IBM Plex Mono',monospace; font-size:0.58rem; padding:2px 8px; border-radius:4px; text-transform:uppercase; letter-spacing:0.1em; }
    .tag-green  { background:var(--green-dim);      color:var(--green);  border:1px solid rgba(0,230,118,0.2); }
    .tag-red    { background:var(--red-dim);         color:var(--red);    border:1px solid rgba(255,61,87,0.2); }
    .tag-blue   { background:rgba(77,166,255,0.1);  color:var(--blue);   border:1px solid rgba(77,166,255,0.2); }
    .tag-purple { background:rgba(179,136,255,0.1); color:var(--purple); border:1px solid rgba(179,136,255,0.2); }
    .tag-yellow { background:rgba(255,209,102,0.1); color:var(--yellow); border:1px solid rgba(255,209,102,0.2); }

    /* ── Progress bar ── */
    .progress-track { height:4px; background:var(--border); border-radius:2px; overflow:hidden; margin:0.3rem 0; }
    .progress-fill  { height:100%; background:linear-gradient(90deg,var(--green),var(--blue)); border-radius:2px; transition:width 0.3s ease; }

    /* ── Section header ── */
    .section-hdr { display:flex; align-items:center; gap:1.2rem; margin:2.5rem 0 1.4rem 0; }
    .section-hdr-label { font-family:'IBM Plex Mono',monospace; font-size:0.58rem; color:var(--muted); text-transform:uppercase; letter-spacing:0.22em; white-space:nowrap; }
    .section-hdr::after { content:''; flex:1; height:1px; background:linear-gradient(90deg,var(--border),transparent); }

    /* ── Stat strip ── */
    .stat-strip { display:flex; background:var(--surface); border:1px solid var(--border); border-radius:var(--radius); overflow:hidden; margin-bottom:1rem; }
    .stat-cell  { flex:1; padding:0.9rem 1rem; border-right:1px solid var(--border); min-width:0; }
    .stat-cell:last-child { border-right:none; }
    .stat-val { font-family:'IBM Plex Mono',monospace; font-size:1rem; font-weight:600; }
    .stat-lbl { font-family:'IBM Plex Mono',monospace; font-size:0.48rem; color:var(--muted); text-transform:uppercase; letter-spacing:0.15em; margin-top:2px; }

    /* ── Row items ── */
    .row-item { padding:0.6rem 0; border-bottom:1px solid var(--border); display:flex; align-items:flex-start; gap:0.6rem; }
    .row-item:last-child { border-bottom:none; }
    .empty-state { text-align:center; padding:3rem 1rem; color:var(--muted); font-family:'IBM Plex Mono',monospace; font-size:0.78rem; }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width:4px; height:4px; }
    ::-webkit-scrollbar-track { background:var(--bg); }
    ::-webkit-scrollbar-thumb { background:#2a3550; border-radius:2px; }

    /* ── Misc ── */
    hr { border-color:var(--border)!important; }
    [data-testid="stExpander"] { background:var(--surface)!important; border:1px solid var(--border)!important; border-radius:var(--radius)!important; }
    [data-testid="stExpander"] summary { font-family:'IBM Plex Mono',monospace!important; font-size:0.75rem!important; color:var(--text2)!important; }
    [data-testid="stSlider"] { padding:0!important; }
    .ticker-wrap { overflow:hidden; background:var(--surface); border-bottom:1px solid var(--border); padding:0.4rem 0; margin:0 -2.5rem 2rem -2.5rem; }
    .ticker-tape { display:inline-flex; animation:ticker 45s linear infinite; white-space:nowrap; }
    .ticker-item { font-family:'IBM Plex Mono',monospace; font-size:0.67rem; padding:0 2rem; letter-spacing:0.04em; }
    .t-up { color:var(--green); } .t-dn { color:var(--red); } .t-sym { color:var(--text); margin-right:0.5rem; font-weight:600; }
    @keyframes ticker { 0%{transform:translateX(0)} 100%{transform:translateX(-50%)} }
</style>
"""

PLOTLY_THEME = dict(
    paper_bgcolor="#06080c", plot_bgcolor="#06080c",
    font=dict(family="IBM Plex Mono", color="#8896ab", size=11),
    xaxis=dict(gridcolor="#1a2235", linecolor="#1a2235", tickfont=dict(size=10), zeroline=False),
    yaxis=dict(gridcolor="#1a2235", linecolor="#1a2235", tickfont=dict(size=10), zeroline=False),
    legend=dict(bgcolor="#0c1018", bordercolor="#1a2235", borderwidth=1, font=dict(size=11)),
    margin=dict(l=10, r=10, t=40, b=10),
)
