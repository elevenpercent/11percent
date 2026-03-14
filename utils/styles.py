import base64, os

# ── Logo ──────────────────────────────────────────────────────────────────────
def _logo_b64():
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "logo.png")
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return ""

_B64      = _logo_b64()
LOGO_IMG  = f'<img src="data:image/png;base64,{_B64}" alt="11%" style="height:36px;width:auto;">' if _B64 else '<span style="font-family:\'Bebas Neue\',sans-serif;font-size:1.6rem;color:#26d97f;letter-spacing:0.05em;">11%</span>'
LOGO_B64  = _B64

# ── Plotly theme ──────────────────────────────────────────────────────────────
PLOTLY_THEME = dict(
    paper_bgcolor="#141a1f",
    plot_bgcolor="#141a1f",
    font=dict(family="IBM Plex Mono", color="#8896ab", size=11),
    xaxis=dict(gridcolor="#1e2830", linecolor="#1e2830", zerolinecolor="#1e2830"),
    yaxis=dict(gridcolor="#1e2830", linecolor="#1e2830", zerolinecolor="#1e2830"),
    margin=dict(l=48, r=16, t=40, b=40),
)

# ── Shared CSS ────────────────────────────────────────────────────────────────
SHARED_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=IBM+Plex+Mono:wght@400;500;600;700&family=Space+Grotesk:wght@300;400;500;600;700&display=swap');

/* ── Variables ── */
:root {
  --green:    #26d97f;
  --green2:   #1db868;
  --red:      #e84040;
  --red2:     #c93333;
  --blue:     #4da6ff;
  --yellow:   #f0c040;
  --purple:   #a78bfa;
  --orange:   #f59e0b;
  --bg:       #0f1318;
  --bg2:      #141a1f;
  --surface:  #1a2230;
  --surface2: #1e2830;
  --border:   #243040;
  --border2:  #2e3d50;
  --text:     #e8edf2;
  --muted:    #8896ab;
  --dim:      #3d5068;
}

/* ── Kill Streamlit chrome ── */
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
[data-testid="stAppViewContainer"] > .main { background:var(--bg)!important; }
.block-container {
    padding-top:2.5rem !important;
    padding-bottom:2rem !important;
    padding-left:2.5rem !important;
    padding-right:2.5rem !important;
    max-width:100% !important;
}
* { box-sizing:border-box; }
body { color:var(--text); font-family:'Space Grotesk',sans-serif; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width:4px; height:4px; }
::-webkit-scrollbar-track { background:var(--bg); }
::-webkit-scrollbar-thumb { background:var(--surface); border-radius:2px; }
::-webkit-scrollbar-thumb:hover { background:var(--border2); }

/* ── Animations ── */
@keyframes fadeUp   { from{opacity:0;transform:translateY(16px)} to{opacity:1;transform:translateY(0)} }
@keyframes fadeIn   { from{opacity:0} to{opacity:1} }
@keyframes pulse    { 0%,100%{opacity:1;box-shadow:0 0 6px var(--green)} 50%{opacity:0.4;box-shadow:none} }
@keyframes shimmer  { 0%{background-position:-200% 0} 100%{background-position:200% 0} }
@keyframes scanline { 0%{transform:translateY(-100%)} 100%{transform:translateY(100vh)} }
@keyframes float    { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-6px)} }
@keyframes glow     { 0%,100%{text-shadow:0 0 20px rgba(38,217,127,0.4)} 50%{text-shadow:0 0 40px rgba(38,217,127,0.8),0 0 80px rgba(38,217,127,0.3)} }

/* ── Page hero headers ── */
.page-hero {
    background:linear-gradient(135deg,var(--bg2) 0%,#111820 100%);
    border:1px solid var(--border);
    border-radius:16px;
    padding:2.5rem 3rem;
    margin-bottom:2rem;
    position:relative;
    overflow:hidden;
    animation:fadeUp 0.4s ease both;
}
.page-hero::before {
    content:'';
    position:absolute;
    top:-80px; right:-80px;
    width:260px; height:260px;
    background:radial-gradient(circle,rgba(38,217,127,0.07) 0%,transparent 70%);
    pointer-events:none;
}
.page-hero::after {
    content:'';
    position:absolute;
    bottom:0; left:0; right:0;
    height:1px;
    background:linear-gradient(90deg,transparent,rgba(38,217,127,0.3),transparent);
}
.page-hero-eyebrow {
    font-family:'IBM Plex Mono',monospace;
    font-size:0.52rem; text-transform:uppercase;
    letter-spacing:0.3em; color:var(--dim);
    margin-bottom:0.5rem;
}
.page-hero h1 {
    font-family:'Bebas Neue',sans-serif;
    font-size:3.2rem; letter-spacing:0.05em;
    line-height:1; color:var(--text);
    margin:0 0 0.5rem 0;
}
.page-hero p {
    font-family:'IBM Plex Mono',monospace;
    font-size:0.72rem; color:var(--muted);
    line-height:1.8; max-width:600px; margin:0;
}

/* ── Section title ── */
.sec-t {
    font-family:'IBM Plex Mono',monospace;
    font-size:0.52rem; text-transform:uppercase;
    letter-spacing:0.25em; color:var(--dim);
    padding:1.2rem 0 0.7rem;
    border-top:1px solid var(--surface2);
    margin-top:0.5rem;
}

/* ── Metric cards ── */
.metric-card {
    background:var(--bg2);
    border:1px solid var(--border);
    border-radius:12px;
    padding:1.4rem 1.6rem;
    transition:border-color 0.2s, transform 0.2s;
    animation:fadeUp 0.4s ease both;
}
.metric-card:hover { border-color:var(--border2); transform:translateY(-2px); }
.metric-val {
    font-family:'Bebas Neue',sans-serif;
    font-size:2.2rem; letter-spacing:0.04em; line-height:1;
}
.metric-val.pos { color:var(--green); }
.metric-val.neg { color:var(--red); }
.metric-val.neu { color:var(--text); }
.metric-val.blue { color:var(--blue); }
.metric-lbl {
    font-family:'IBM Plex Mono',monospace;
    font-size:0.5rem; text-transform:uppercase;
    letter-spacing:0.2em; color:var(--dim);
    margin-top:0.35rem;
}
.metric-sub {
    font-family:'IBM Plex Mono',monospace;
    font-size:0.62rem; color:var(--muted);
    margin-top:0.2rem;
}

/* ── Info/warn boxes ── */
.info-box {
    background:rgba(77,166,255,0.05);
    border:1px solid rgba(77,166,255,0.2);
    border-radius:8px; padding:0.8rem 1rem;
    font-size:0.78rem; color:var(--muted); line-height:1.6;
}
.warn-box {
    background:rgba(240,192,64,0.05);
    border:1px solid rgba(240,192,64,0.2);
    border-radius:8px; padding:0.8rem 1rem;
    font-size:0.78rem; color:var(--muted); line-height:1.6;
}
.success-box {
    background:rgba(38,217,127,0.05);
    border:1px solid rgba(38,217,127,0.2);
    border-radius:8px; padding:0.8rem 1rem;
    font-size:0.78rem; color:var(--muted); line-height:1.6;
}

/* ── Tags / badges ── */
.tag {
    display:inline-block;
    font-family:'IBM Plex Mono',monospace;
    font-size:0.5rem; text-transform:uppercase;
    letter-spacing:0.1em; padding:2px 8px;
    border-radius:3px;
}
.tag-green { background:rgba(38,217,127,0.1); color:var(--green); border:1px solid rgba(38,217,127,0.25); }
.tag-red   { background:rgba(232,64,64,0.1);  color:var(--red);   border:1px solid rgba(232,64,64,0.25); }
.tag-blue  { background:rgba(77,166,255,0.1); color:var(--blue);  border:1px solid rgba(77,166,255,0.25); }
.tag-yellow{ background:rgba(240,192,64,0.1); color:var(--yellow);border:1px solid rgba(240,192,64,0.25); }

/* ── Dividers ── */
.divider { border:none; border-top:1px solid var(--border); margin:1.5rem 0; }

/* ── Section header (legacy) ── */
.section-hdr {
    display:flex; align-items:center; gap:0.7rem;
    padding:1rem 0 0.5rem;
    border-top:1px solid var(--surface2);
    margin-top:0.5rem;
}
.section-hdr-label {
    font-family:'IBM Plex Mono',monospace;
    font-size:0.52rem; text-transform:uppercase;
    letter-spacing:0.22em; color:var(--dim);
}

/* ── Row items ── */
.row-item {
    display:flex; align-items:center; justify-content:space-between;
    padding:0.5rem 0; border-bottom:1px solid var(--surface2);
    font-size:0.82rem;
}
.row-item:last-child { border-bottom:none; }

/* ── Chat bubbles ── */
.chat-user {
    background:rgba(77,166,255,0.07);
    border:1px solid rgba(77,166,255,0.15);
    border-radius:12px 12px 2px 12px;
    padding:0.8rem 1rem; margin:0.5rem 0;
    font-size:0.83rem; color:var(--text); line-height:1.6;
    max-width:85%; margin-left:auto;
}
.chat-ai {
    background:var(--bg2);
    border:1px solid var(--border);
    border-radius:2px 12px 12px 12px;
    padding:0.8rem 1rem; margin:0.5rem 0;
    font-size:0.83rem; color:var(--muted); line-height:1.6;
    max-width:92%;
}
.chat-ai strong { color:var(--text); }
.chat-ai code {
    background:rgba(0,0,0,0.3); border:1px solid var(--border);
    border-radius:3px; padding:1px 5px;
    font-family:'IBM Plex Mono',monospace; font-size:0.78rem;
    color:var(--blue);
}

/* ── Streamlit widget overrides ── */
[data-testid="stTextInput"] > div > div > input,
[data-testid="stNumberInput"] input,
[data-testid="stSelectbox"] > div > div {
    background:var(--bg2)!important;
    border:1px solid var(--border)!important;
    color:var(--text)!important; border-radius:8px!important;
    font-family:'IBM Plex Mono',monospace!important; font-size:0.82rem!important;
}
[data-testid="stTextInput"] > div > div > input:focus,
[data-testid="stNumberInput"] input:focus {
    border-color:var(--green)!important;
    box-shadow:0 0 0 2px rgba(38,217,127,0.12)!important;
}
[data-testid="stButton"] > button {
    font-family:'IBM Plex Mono',monospace!important;
    font-size:0.7rem!important; font-weight:700!important;
    text-transform:uppercase!important; letter-spacing:0.12em!important;
    border-radius:8px!important; border:1px solid var(--border)!important;
    background:transparent!important; color:var(--muted)!important;
    transition:all 0.15s!important; padding:0.5rem 1.1rem!important;
}
[data-testid="stButton"] > button:hover {
    border-color:var(--green)!important;
    color:var(--green)!important;
    background:rgba(38,217,127,0.05)!important;
}
div[data-testid="stButton"] > button[kind="primary"] {
    background:var(--green)!important;
    border-color:transparent!important; color:#000!important;
    font-weight:700!important;
    box-shadow:0 0 20px rgba(38,217,127,0.2)!important;
}
div[data-testid="stButton"] > button[kind="primary"]:hover {
    background:#30f090!important;
    box-shadow:0 0 30px rgba(38,217,127,0.4)!important;
}
[data-testid="stTabs"] [role="tablist"] {
    gap:0; border-bottom:1px solid var(--border)!important;
    background:transparent;
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
    color:var(--green)!important;
    border-bottom-color:var(--green)!important;
    background:rgba(38,217,127,0.03)!important;
}
[data-testid="stExpander"] {
    background:var(--bg2)!important;
    border:1px solid var(--border)!important;
    border-radius:8px!important;
}
[data-testid="stSlider"] > div > div > div { background:var(--green)!important; }
[data-testid="stCheckbox"] label { font-size:0.82rem!important; color:var(--muted)!important; }
div[data-baseweb="select"] > div { background:var(--bg2)!important; border-color:var(--border)!important; }
[data-testid="stRadio"] label { font-size:0.82rem!important; color:var(--muted)!important; }
[data-testid="stTextArea"] textarea {
    background:var(--bg2)!important; border:1px solid var(--border)!important;
    color:var(--text)!important; border-radius:8px!important;
    font-family:'IBM Plex Mono',monospace!important; font-size:0.8rem!important;
}
[data-testid="stDateInput"] input {
    background:var(--bg2)!important; border:1px solid var(--border)!important;
    color:var(--text)!important; border-radius:8px!important;
    font-family:'IBM Plex Mono',monospace!important;
}

/* ── Animated background grid (applied via JS) ── */
.animated-bg {
    position:fixed; top:0; left:0; width:100%; height:100%;
    pointer-events:none; z-index:0; opacity:0.015;
    background-image:
        linear-gradient(var(--border2) 1px, transparent 1px),
        linear-gradient(90deg, var(--border2) 1px, transparent 1px);
    background-size:60px 60px;
}

/* ── Page header (legacy compat) ── */
.page-header {
    margin-bottom:2rem;
    animation:fadeUp 0.4s ease both;
}
.page-header-eyebrow {
    font-family:'IBM Plex Mono',monospace;
    font-size:0.52rem; text-transform:uppercase;
    letter-spacing:0.3em; color:var(--dim);
    margin-bottom:0.4rem;
}
.page-header h1 {
    font-family:'Bebas Neue',sans-serif;
    font-size:3rem; letter-spacing:0.05em;
    line-height:1; color:var(--text);
    margin:0 0 0.4rem 0;
}
.page-header p {
    font-family:'IBM Plex Mono',monospace;
    font-size:0.72rem; color:var(--muted);
    line-height:1.8; max-width:600px;
}

/* ── Stat strip ── */
.stat-strip {
    display:flex; background:var(--bg2);
    border:1px solid var(--border); border-radius:10px;
    overflow:hidden; margin-bottom:1.2rem;
    animation:fadeUp 0.5s ease both;
}
.stat-cell {
    flex:1; padding:0.9rem 1.2rem;
    border-right:1px solid var(--border);
}
.stat-cell:last-child { border-right:none; }
.stat-val {
    font-family:'IBM Plex Mono',monospace;
    font-size:1.3rem; font-weight:700; line-height:1;
}
.stat-val.pos { color:var(--green); }
.stat-val.neg { color:var(--red); }
.stat-val.neu { color:var(--text); }
.stat-lbl {
    font-family:'IBM Plex Mono',monospace;
    font-size:0.5rem; text-transform:uppercase;
    letter-spacing:0.18em; color:var(--dim); margin-top:0.3rem;
}

/* ── Glow accents ── */
.glow-green { text-shadow:0 0 20px rgba(38,217,127,0.5); color:var(--green); }
.glow-red   { text-shadow:0 0 20px rgba(232,64,64,0.5);  color:var(--red); }

/* ── Ticker tape ── */
@keyframes tickerScroll { 0%{transform:translateX(0)} 100%{transform:translateX(-50%)} }
.ticker-outer {
    width:100%; overflow:hidden; background:var(--bg2);
    border:1px solid var(--border); border-radius:6px; height:32px;
    display:flex; align-items:center;
    margin-bottom:1.6rem; position:relative;
}
.ticker-outer::before,.ticker-outer::after {
    content:''; position:absolute; top:0; bottom:0; width:60px; z-index:2; pointer-events:none;
}
.ticker-outer::before { left:0;  background:linear-gradient(90deg,var(--bg2),transparent); }
.ticker-outer::after  { right:0; background:linear-gradient(-90deg,var(--bg2),transparent); }
.ticker-track { display:flex; white-space:nowrap; animation:tickerScroll 38s linear infinite; }
.ticker-item  {
    display:inline-flex; align-items:center; gap:6px; padding:0 20px;
    border-right:1px solid var(--border);
    font-family:'IBM Plex Mono',monospace; font-size:0.67rem; flex-shrink:0;
}
.t-sym{color:var(--dim);font-weight:700}
.t-up{color:var(--green)}
.t-dn{color:var(--red)}
</style>
"""
