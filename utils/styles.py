"""
Shared styles for 11% platform — green/red only, no gold.
"""

SHARED_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=IBM+Plex+Mono:wght@300;400;600;700&family=IBM+Plex+Sans:wght@300;400;600&display=swap');
    :root {
        --bg:#07090d; --surface:#0d1117; --border:#1c2333; --border2:#263045;
        --green:#00d68f; --red:#ff4757; --text:#cdd5e0; --muted:#3a4558;
        --grid:rgba(255,255,255,0.03);
    }
    html,body,[data-testid="stAppViewContainer"],[data-testid="stMain"],.main {
        background-color:var(--bg)!important; color:var(--text)!important;
        font-family:'IBM Plex Sans',sans-serif!important;
    }
    [data-testid="stMain"] {
        background-image:linear-gradient(var(--grid) 1px,transparent 1px),linear-gradient(90deg,var(--grid) 1px,transparent 1px)!important;
        background-size:48px 48px!important; padding-top:0!important;
    }
    .block-container{padding-top:0!important;padding-left:2rem!important;padding-right:2rem!important;max-width:100%!important;}
    header[data-testid="stHeader"]{display:none!important;}
    [data-testid="stToolbar"]{display:none!important;}
    [data-testid="stDecoration"]{display:none!important;}
    [data-testid="stSidebar"]{display:none!important;}
    [data-testid="stSidebarNav"]{display:none!important;}
    [data-testid="collapsedControl"]{display:none!important;}
    footer{display:none!important;} #MainMenu{display:none!important;} .stDeployButton{display:none!important;}
    h1{font-family:'Bebas Neue',sans-serif!important;letter-spacing:0.06em;color:var(--text)!important;}
    h2{font-family:'Bebas Neue',sans-serif!important;}
    h3{font-family:'IBM Plex Mono',monospace!important;font-size:0.75rem!important;color:var(--green)!important;text-transform:uppercase;letter-spacing:0.15em;}
    .stTextInput input,.stNumberInput input{background:#0d1117!important;border:1px solid #1c2333!important;color:#cdd5e0!important;font-family:'IBM Plex Mono',monospace!important;font-size:0.85rem!important;border-radius:3px!important;}
    .stTextInput input:focus,.stNumberInput input:focus{border-color:#00d68f!important;box-shadow:none!important;}
    div[data-baseweb="select"]>div{background:#0d1117!important;border:1px solid #1c2333!important;color:#cdd5e0!important;font-family:'IBM Plex Mono',monospace!important;border-radius:3px!important;}
    .stDateInput input{background:#0d1117!important;border:1px solid #1c2333!important;color:#cdd5e0!important;font-family:'IBM Plex Mono',monospace!important;border-radius:3px!important;}
    label{font-family:'IBM Plex Mono',monospace!important;font-size:0.68rem!important;color:#3a4558!important;text-transform:uppercase!important;letter-spacing:0.1em!important;}
    .stButton>button{background:transparent!important;color:#00d68f!important;border:1px solid #00d68f!important;border-radius:3px!important;font-family:'IBM Plex Mono',monospace!important;font-weight:600!important;font-size:0.78rem!important;letter-spacing:0.1em!important;padding:0.45rem 1.4rem!important;transition:all 0.15s!important;text-transform:uppercase!important;}
    .stButton>button:hover{background:#00d68f!important;color:#000!important;}
    .metric-card{background:#0d1117;border:1px solid #1c2333;padding:1rem;border-radius:4px;text-align:center;}
    .metric-val{font-family:'IBM Plex Mono',monospace;font-size:1.1rem;font-weight:700;}
    .metric-lbl{font-family:'IBM Plex Mono',monospace;font-size:0.55rem;color:#3a4558;text-transform:uppercase;margin-top:0.3rem;}
    .pos{color:#00d68f;} .neg{color:#ff4757;} .neu{color:#cdd5e0;}
    .config-panel{background:#0d1117;border:1px solid #1c2333;border-radius:6px;padding:1.4rem 1.4rem 0.4rem 1.4rem;margin-bottom:1.5rem;}
    .price-divider{display:flex;align-items:center;gap:1rem;margin:1.5rem 0 1rem 0;font-family:'IBM Plex Mono',monospace;font-size:0.62rem;color:#3a4558;letter-spacing:0.12em;}
    .price-divider::before,.price-divider::after{content:'';flex:1;height:1px;background:#1c2333;}
    .page-header{padding:1.5rem 0 1rem 0;border-bottom:1px solid #1c2333;margin-bottom:1.5rem;}
    .page-header h1{font-size:2.8rem!important;margin:0!important;}
    .page-header p{color:#3a4558;font-size:0.85rem;margin:0.3rem 0 0 0;}
    .info-box{background:#071a0f;border:1px solid #0d3320;border-radius:4px;padding:0.8rem 1rem;font-size:0.82rem;color:#00d68f;font-family:'IBM Plex Mono',monospace;}
    .warn-box{background:#1a0a08;border:1px solid #3a1008;border-radius:4px;padding:0.8rem 1rem;font-size:0.82rem;color:#ff4757;font-family:'IBM Plex Mono',monospace;}
    .chat-user{background:#0d1117;border:1px solid #1c2333;border-radius:10px 10px 3px 10px;padding:1rem 1.2rem;margin:0.6rem 0;}
    .chat-ai{background:#071a0f;border:1px solid #0d3320;border-radius:10px 10px 10px 3px;padding:1rem 1.2rem;margin:0.6rem 0;}
    .chat-lbl{font-family:'IBM Plex Mono',monospace;font-size:0.65rem;text-transform:uppercase;letter-spacing:0.12em;color:#3a4558;margin-bottom:0.4rem;}
    .nb{background:#07090d;border-bottom:1px solid #1c2333;padding:0;margin:-1rem -2rem 2rem -2rem;display:flex;align-items:stretch;position:sticky;top:0;z-index:1000;}
    .nb-brand{font-family:'Bebas Neue',sans-serif;font-size:1.7rem;letter-spacing:0.1em;color:var(--text);padding:0.6rem 1.6rem;border-right:1px solid #1c2333;display:flex;align-items:center;flex-shrink:0;}
    .nb-brand .g{color:#00d68f;} .nb-brand .r{color:#ff4757;}
    .nb-links{display:flex;align-items:stretch;flex:1;}
    .nb-tag{font-family:'IBM Plex Mono',monospace;font-size:0.58rem;color:#3a4558;letter-spacing:0.15em;padding:0.6rem 1.6rem;display:flex;align-items:center;border-left:1px solid #1c2333;}
    .nb-links [data-testid="stPageLink-NavLink"]{font-family:'IBM Plex Mono',monospace!important;font-size:0.69rem!important;font-weight:500!important;text-transform:uppercase!important;letter-spacing:0.12em!important;color:#3a4558!important;text-decoration:none!important;padding:0 1.1rem!important;border-radius:0!important;border:none!important;border-bottom:2px solid transparent!important;background:transparent!important;display:flex!important;align-items:center!important;height:100%!important;transition:color 0.15s,border-color 0.15s!important;white-space:nowrap!important;}
    .nb-links [data-testid="stPageLink-NavLink"]:hover{color:#cdd5e0!important;background:transparent!important;text-decoration:none!important;border-bottom:2px solid #3a4558!important;}
    .nb-links [data-testid="stPageLink-NavLink"][aria-current="page"]{color:#00d68f!important;border-bottom:2px solid #00d68f!important;}
    .ticker-wrap{overflow:hidden;background:#0d1117;border-bottom:1px solid #1c2333;padding:0.4rem 0;margin:-2rem -2rem 2rem -2rem;}
    .ticker-tape{display:inline-flex;animation:ticker 35s linear infinite;white-space:nowrap;}
    .ticker-item{font-family:'IBM Plex Mono',monospace;font-size:0.68rem;padding:0 1.5rem;letter-spacing:0.05em;}
    .t-up{color:#00d68f;} .t-dn{color:#ff4757;} .t-sym{color:#cdd5e0;margin-right:0.4rem;}
    @keyframes ticker{0%{transform:translateX(0)}100%{transform:translateX(-50%)}}
    ::-webkit-scrollbar{width:4px;} ::-webkit-scrollbar-track{background:#07090d;} ::-webkit-scrollbar-thumb{background:#263045;border-radius:2px;}
    hr{border-color:#1c2333!important;}
    [data-testid="stExpander"]{background:#0d1117!important;border:1px solid #1c2333!important;border-radius:4px!important;}
</style>
"""

# Plotly dark theme shared across all charts
PLOTLY_THEME = dict(
    paper_bgcolor="#07090d",
    plot_bgcolor="#07090d",
    font=dict(family="IBM Plex Mono", color="#cdd5e0", size=11),
    xaxis=dict(gridcolor="#1c2333", linecolor="#1c2333", tickfont=dict(size=10)),
    yaxis=dict(gridcolor="#1c2333", linecolor="#1c2333", tickfont=dict(size=10)),
    legend=dict(bgcolor="#0d1117", bordercolor="#1c2333", borderwidth=1),
    margin=dict(l=10, r=10, t=40, b=10),
)
