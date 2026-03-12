import base64, os

# ── Logo
def _logo_b64():
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "logo.png")
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return ""

_B64 = _logo_b64()
LOGO_IMG  = f'<img src="data:image/png;base64,{_B64}" alt="11%" style="height:36px;width:auto;">' if _B64 else '<span style="font-family:\'Bebas Neue\',sans-serif;font-size:1.6rem;color:#00e676;letter-spacing:0.05em;">11%</span>'
LOGO_B64  = _B64

PLOTLY_THEME = dict(
    paper_bgcolor="#06080c",
    plot_bgcolor="#06080c",
    font=dict(family="IBM Plex Mono", color="#8896ab", size=11),
    xaxis=dict(gridcolor="#0f1621", linecolor="#1a2235", zerolinecolor="#1a2235"),
    yaxis=dict(gridcolor="#0f1621", linecolor="#1a2235", zerolinecolor="#1a2235"),
    margin=dict(l=48, r=16, t=40, b=40),
)

SHARED_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=IBM+Plex+Mono:wght@400;500;600;700&family=Space+Grotesk:wght@300;400;500;600;700&display=swap');

/* ── CSS variables ── */
:root {
  --green:   #00e676;
  --red:     #ff3d57;
  --blue:    #4da6ff;
  --yellow:  #ffd166;
  --purple:  #b388ff;
  --orange:  #ff9f43;
  --bg:      #06080c;
  --surface: #0c1018;
  --border:  #1a2235;
  --border2: #2a3550;
  --text:    #eef2f7;
  --muted:   #8896ab;
  --dim:     #3a4a5e;
}

/* ── Kill Streamlit chrome & sidebar flash ── */
#MainMenu, footer, header { visibility:hidden!important; display:none!important; }
[data-testid="stSidebar"],
[data-testid="stSidebarNav"],
[data-testid="collapsedControl"],
section[data-testid="stSidebar"] {
    display:none!important; width:0!important; min-width:0!important;
    visibility:hidden!important; opacity:0!important;
}
[data-testid="stAppViewContainer"] > section:first-child { display:none!important; }
.stDeployButton { display:none!important; }

/* ── Base ── */
html, body, [data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > .main { background:#06080c!important; }
.block-container {
    padding-top:0!important; padding-bottom:2rem!important;
    padding-left:2.5rem!important; padding-right:2.5rem!important;
    max-width:100%!important;
}
* { box-sizing:border-box; }
body { color:#eef2f7; font-family:'Space Grotesk',sans-serif; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width:4px; height:4px; }
::-webkit-scrollbar-track { background:#06080c; }
::-webkit-scrollbar-thumb { background:#1a2235; border-radius:2px; }
::-webkit-scrollbar-thumb:hover { background:#2a3550; }

/* ── Navbar ── */
.nb {
    background:rgba(6,8,12,0.98);
    backdrop-filter:blur(24px); -webkit-backdrop-filter:blur(24px);
    border-bottom:1px solid var(--border);
    margin:0 -2.5rem 0 -2.5rem;
    display:flex; align-items:stretch;
    height:56px; position:sticky; top:0; z-index:1000;
    overflow:visible;
}
.nb-brand {
    padding:0 1.5rem;
    border-right:1px solid var(--border);
    display:flex; align-items:center;
    flex-shrink:0; min-width:72px;
}
.nb-brand img { height:36px!important; width:auto!important; display:block; }
.nb-links {
    display:flex; align-items:stretch;
    flex:1; overflow:visible;
}
.nb-tag {
    font-family:'IBM Plex Mono',monospace;
    font-size:0.44rem; color:var(--dim);
    letter-spacing:0.22em; padding:0 1.2rem;
    display:flex; align-items:center;
    border-left:1px solid var(--border);
    text-transform:uppercase; white-space:nowrap;
    gap:0.4rem; flex-shrink:0;
}
.live-dot {
    display:inline-block; width:5px; height:5px;
    border-radius:50%; background:var(--green);
    animation:livepulse 2s ease-in-out infinite;
}
@keyframes livepulse {
    0%,100%{opacity:1;box-shadow:0 0 6px var(--green)}
    50%{opacity:0.3;box-shadow:none}
}

/* Streamlit page_link inside navbar */
.nb-links [data-testid="stPageLink-NavLink"] {
    font-family:'IBM Plex Mono',monospace!important;
    font-size:0.6rem!important; font-weight:600!important;
    text-transform:uppercase!important; letter-spacing:0.1em!important;
    color:var(--dim)!important; text-decoration:none!important;
    padding:0 1.1rem!important; border-radius:0!important;
    border:none!important; border-bottom:2px solid transparent!important;
    background:transparent!important; display:flex!important;
    align-items:center!important; height:56px!important;
    transition:color 0.15s, border-color 0.15s!important;
    white-space:nowrap!important;
}
.nb-links [data-testid="stPageLink-NavLink"]:hover {
    color:var(--text)!important;
    border-bottom-color:var(--border2)!important;
    background:rgba(255,255,255,0.02)!important;
}
.nb-links [data-testid="stPageLink-NavLink"][aria-current="page"] {
    color:var(--green)!important;
    border-bottom-color:var(--green)!important;
    background:rgba(0,230,118,0.03)!important;
}
.nb-links [data-testid="stHorizontalBlock"] {
    gap:0!important; height:56px!important;
    align-items:stretch!important; flex-wrap:nowrap!important;
}
.nb-links [data-testid="column"] {
    display:flex!important; align-items:stretch!important;
    padding:0!important; min-width:fit-content!important; flex-shrink:0!important;
}

/* Tools dropdown */
.nb-tools-wrap {
    position:relative; display:flex; align-items:center;
    border-left:1px solid var(--border); flex-shrink:0;
}
.nb-tools-btn {
    font-family:'IBM Plex Mono',monospace; font-size:0.6rem;
    font-weight:600; text-transform:uppercase; letter-spacing:0.1em;
    color:var(--dim); background:transparent; border:none;
    border-bottom:2px solid transparent;
    padding:0 1.1rem; height:56px; cursor:pointer;
    display:flex; align-items:center; gap:0.5rem;
    transition:color 0.15s; white-space:nowrap;
}
.nb-tools-btn:hover { color:var(--text); background:rgba(255,255,255,0.02); }
.nb-tools-btn .arr { font-size:0.45rem; transition:transform 0.2s; }
.nb-tools-wrap:hover .arr { transform:rotate(180deg); }
.nb-tools-drop {
    display:none; position:absolute; top:55px; left:0;
    background:#0c1018; border:1px solid var(--border);
    border-top:2px solid var(--green);
    border-radius:0 0 8px 8px; min-width:190px; z-index:2000;
    box-shadow:0 16px 48px rgba(0,0,0,0.7);
}
.nb-tools-wrap:hover .nb-tools-drop { display:block; }
.nb-tools-drop a {
    display:flex; align-items:center; gap:0.7rem; padding:0.7rem 1.2rem;
    font-family:'IBM Plex Mono',monospace; font-size:0.6rem;
    font-weight:600; text-transform:uppercase; letter-spacing:0.1em;
    color:var(--dim); text-decoration:none;
    border-bottom:1px solid #111927;
    transition:color 0.12s, background 0.12s, padding-left 0.15s;
}
.nb-tools-drop a:last-child { border-bottom:none; }
.nb-tools-drop a:hover {
    color:var(--green); background:rgba(0,230,118,0.04); padding-left:1.6rem;
}
.nb-tools-drop a::before {
    content:''; display:inline-block; width:4px; height:4px;
    border-radius:50%; background:currentColor; opacity:0.5; flex-shrink:0;
}

/* ── Page header ── */
.page-header {
    padding:2.2rem 0 1.8rem;
    border-bottom:1px solid var(--border);
    margin-bottom:2rem;
}
.page-header-eyebrow {
    font-family:'IBM Plex Mono',monospace;
    font-size:0.58rem; font-weight:600;
    text-transform:uppercase; letter-spacing:0.22em;
    color:var(--green); margin-bottom:0.5rem;
    display:flex; align-items:center; gap:0.6rem;
}
.page-header h1 {
    font-family:'Bebas Neue',sans-serif;
    font-size:2.8rem; letter-spacing:0.04em;
    color:var(--text); margin:0 0 0.5rem; line-height:1;
}
.page-header p {
    font-size:0.88rem; color:var(--muted);
    max-width:640px; line-height:1.65; margin:0;
}

/* ── Panels ── */
.panel {
    background:var(--surface); border:1px solid var(--border);
    border-radius:10px; padding:1.2rem 1.4rem;
}
.panel-sm {
    background:var(--surface); border:1px solid var(--border);
    border-radius:8px; padding:0.9rem 1.1rem;
}

/* ── Section header ── */
.section-hdr {
    font-family:'IBM Plex Mono',monospace;
    font-size:0.58rem; font-weight:600;
    text-transform:uppercase; letter-spacing:0.2em;
    color:var(--dim); margin:0 0 1rem;
    padding-bottom:0.6rem;
    border-bottom:1px solid var(--border);
}

/* ── Stat strip ── */
.stat-strip {
    display:flex; background:var(--surface);
    border:1px solid var(--border); border-radius:10px;
    overflow:hidden; margin-bottom:1.2rem;
}
.stat-cell {
    flex:1; padding:0.9rem 1.2rem;
    border-right:1px solid var(--border);
}
.stat-cell:last-child { border-right:none; }
.stat-val {
    font-family:'IBM Plex Mono',monospace;
    font-size:1.4rem; font-weight:700; line-height:1;
}
.stat-val.pos { color:var(--green); }
.stat-val.neg { color:var(--red); }
.stat-val.neu { color:var(--text); }
.stat-val.blue { color:var(--blue); }
.stat-lbl {
    font-family:'IBM Plex Mono',monospace;
    font-size:0.54rem; text-transform:uppercase;
    letter-spacing:0.18em; color:var(--dim); margin-top:0.3rem;
}

/* ── Metric card ── */
.metric-card {
    background:var(--surface); border:1px solid var(--border);
    border-radius:10px; padding:1rem 1.2rem;
    transition:border-color 0.15s;
}
.metric-card:hover { border-color:var(--border2); }
.metric-card .mc-val {
    font-family:'IBM Plex Mono',monospace;
    font-size:1.3rem; font-weight:700;
}
.metric-card .mc-lbl {
    font-size:0.7rem; color:var(--muted); margin-top:0.15rem;
}

/* ── Badges ── */
.beta-badge {
    background:rgba(0,230,118,0.1);
    border:1px solid rgba(0,230,118,0.25);
    color:var(--green); font-size:0.5rem;
    padding:2px 7px; border-radius:3px;
    font-family:'IBM Plex Mono',monospace;
    text-transform:uppercase; letter-spacing:0.14em;
    vertical-align:middle;
}
.tag {
    display:inline-block;
    background:rgba(77,166,255,0.1);
    border:1px solid rgba(77,166,255,0.2);
    color:var(--blue); font-size:0.56rem;
    padding:2px 8px; border-radius:3px;
    font-family:'IBM Plex Mono',monospace;
    text-transform:uppercase; letter-spacing:0.12em;
}

/* ── Info / warn boxes ── */
.info-box {
    background:rgba(77,166,255,0.06);
    border:1px solid rgba(77,166,255,0.2);
    border-radius:8px; padding:0.8rem 1rem;
    font-size:0.8rem; color:var(--muted); line-height:1.6;
}
.warn-box {
    background:rgba(255,209,102,0.06);
    border:1px solid rgba(255,209,102,0.2);
    border-radius:8px; padding:0.8rem 1rem;
    font-size:0.8rem; color:var(--muted); line-height:1.6;
}

/* ── Chat bubbles (AI Coach) ── */
.chat-user {
    background:rgba(77,166,255,0.08);
    border:1px solid rgba(77,166,255,0.15);
    border-radius:12px 12px 2px 12px;
    padding:0.8rem 1rem; margin:0.5rem 0;
    font-size:0.85rem; color:var(--text); line-height:1.6;
    max-width:85%; margin-left:auto;
}
.chat-ai {
    background:var(--surface);
    border:1px solid var(--border);
    border-radius:2px 12px 12px 12px;
    padding:0.8rem 1rem; margin:0.5rem 0;
    font-size:0.85rem; color:var(--muted); line-height:1.6;
    max-width:92%;
}
.chat-ai strong { color:var(--text); }
.chat-ai h3, .chat-ai h4 {
    font-family:'IBM Plex Mono',monospace;
    font-size:0.65rem; text-transform:uppercase;
    letter-spacing:0.15em; color:var(--green);
    margin:0.8rem 0 0.3rem;
}
.chat-ai ul, .chat-ai ol { padding-left:1.2rem; margin:0.4rem 0; }
.chat-ai li { margin-bottom:0.2rem; }
.chat-ai code {
    background:rgba(0,0,0,0.3); border:1px solid var(--border);
    border-radius:3px; padding:1px 5px;
    font-family:'IBM Plex Mono',monospace; font-size:0.78rem;
    color:var(--blue);
}

/* ── Progress track ── */
.progress-track {
    background:var(--border); border-radius:2px; height:3px; width:100%;
}
.progress-fill {
    background:linear-gradient(90deg,var(--green),var(--blue));
    height:100%; border-radius:2px; transition:width 0.3s;
}

/* ── Divider ── */
.divider {
    border:none; border-top:1px solid var(--border); margin:1.5rem 0;
}

/* ── Row item ── */
.row-item {
    display:flex; align-items:center; justify-content:space-between;
    padding:0.55rem 0; border-bottom:1px solid #0d1117;
    font-size:0.82rem;
}
.row-item:last-child { border-bottom:none; }

/* ── Ticker wrap ── */
.ticker-wrap {
    overflow:hidden; height:28px;
    background:var(--surface); border:1px solid var(--border);
    border-radius:4px; margin-bottom:0.5rem;
}

/* ── Streamlit widget overrides ── */
[data-testid="stTextInput"] > div > div > input,
[data-testid="stNumberInput"] input,
[data-testid="stSelectbox"] > div > div {
    background:#0e1420!important; border:1px solid var(--border)!important;
    color:var(--text)!important; border-radius:6px!important;
    font-family:'IBM Plex Mono',monospace!important; font-size:0.82rem!important;
}
[data-testid="stTextInput"] > div > div > input:focus,
[data-testid="stNumberInput"] input:focus {
    border-color:var(--blue)!important;
    box-shadow:0 0 0 2px rgba(77,166,255,0.12)!important;
}
[data-testid="stButton"] > button {
    font-family:'IBM Plex Mono',monospace!important;
    font-size:0.7rem!important; font-weight:700!important;
    text-transform:uppercase!important; letter-spacing:0.12em!important;
    border-radius:6px!important; border:1px solid var(--border)!important;
    background:transparent!important; color:var(--muted)!important;
    transition:all 0.15s!important; padding:0.45rem 1rem!important;
}
[data-testid="stButton"] > button:hover {
    border-color:var(--green)!important; color:var(--green)!important;
    background:rgba(0,230,118,0.05)!important;
}
[data-testid="stButton"][data-baseweb] > button[kind="primary"],
div[data-testid="stButton"] > button[kind="primary"] {
    background:linear-gradient(135deg,#007a2c,var(--green))!important;
    border-color:transparent!important; color:#000!important;
}
[data-testid="stTabs"] [role="tablist"] {
    gap:0; border-bottom:1px solid var(--border)!important; background:transparent;
}
[data-testid="stTabs"] [role="tab"] {
    font-family:'IBM Plex Mono',monospace!important;
    font-size:0.58rem!important; font-weight:600!important;
    text-transform:uppercase!important; letter-spacing:0.15em!important;
    color:var(--dim)!important; border:none!important;
    border-bottom:2px solid transparent!important;
    background:transparent!important; padding:0.6rem 1.2rem!important;
    border-radius:0!important; transition:color 0.15s!important;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    color:var(--green)!important; border-bottom-color:var(--green)!important;
    background:rgba(0,230,118,0.03)!important;
}
[data-testid="stExpander"] {
    background:var(--surface)!important; border:1px solid var(--border)!important;
    border-radius:8px!important;
}
[data-testid="stExpander"] summary {
    font-family:'IBM Plex Mono',monospace!important;
    font-size:0.68rem!important; font-weight:600!important;
    text-transform:uppercase!important; letter-spacing:0.15em!important;
    color:var(--muted)!important;
}
[data-testid="stSlider"] > div > div > div {
    background:var(--green)!important;
}
[data-testid="stCheckbox"] label { font-size:0.82rem!important; color:var(--muted)!important; }
div[data-baseweb="select"] > div { background:#0e1420!important; border-color:var(--border)!important; }
</style>
"""
