"""
Shared styles for 11% platform.
"""

SHARED_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=IBM+Plex+Mono:wght@300;400;600;700&family=Inter:wght@300;400;500;600&display=swap');
    :root {
        --bg:#07090d; --surface:#0d1117; --surface2:#111620;
        --border:#1a2235; --border2:#263045;
        --green:#00d68f; --green-dim:#00d68f18;
        --red:#ff4757;   --red-dim:#ff475718;
        --text:#e2e8f0; --text2:#8892a4; --muted:#3a4558;
        --grid:rgba(255,255,255,0.025);
        --radius:8px; --radius-sm:4px;
    }

    /* ── Base ── */
    html,body,[data-testid="stAppViewContainer"],[data-testid="stMain"],.main {
        background-color:var(--bg)!important; color:var(--text)!important;
        font-family:'Inter',sans-serif!important;
    }
    [data-testid="stMain"] {
        background-image:linear-gradient(var(--grid) 1px,transparent 1px),
                         linear-gradient(90deg,var(--grid) 1px,transparent 1px)!important;
        background-size:56px 56px!important; padding-top:0!important;
    }
    .block-container{padding-top:0!important;padding-left:2.5rem!important;padding-right:2.5rem!important;max-width:1400px!important;margin:0 auto!important;}

    /* ── Hide Streamlit chrome ── */
    header[data-testid="stHeader"]{display:none!important;}
    [data-testid="stToolbar"]{display:none!important;}
    [data-testid="stDecoration"]{display:none!important;}
    [data-testid="stSidebar"]{display:none!important;}
    [data-testid="stSidebarNav"]{display:none!important;}
    [data-testid="collapsedControl"]{display:none!important;}
    footer{display:none!important;} #MainMenu{display:none!important;} .stDeployButton{display:none!important;}

    /* ── Typography ── */
    h1{font-family:'Bebas Neue',sans-serif!important;letter-spacing:0.05em;color:var(--text)!important;font-size:3rem!important;margin:0!important;}
    h2{font-family:'Bebas Neue',sans-serif!important;color:var(--text)!important;}
    p{color:var(--text2);line-height:1.7;}

    /* ── Inputs ── */
    .stTextInput input,.stNumberInput input {
        background:var(--surface)!important; border:1px solid var(--border)!important;
        color:var(--text)!important; font-family:'IBM Plex Mono',monospace!important;
        font-size:0.875rem!important; border-radius:var(--radius-sm)!important;
        padding:0.5rem 0.75rem!important; transition:border-color 0.15s!important;
    }
    .stTextInput input:focus,.stNumberInput input:focus{border-color:var(--green)!important;box-shadow:0 0 0 2px var(--green-dim)!important;}
    div[data-baseweb="select"]>div{background:var(--surface)!important;border:1px solid var(--border)!important;color:var(--text)!important;font-family:'IBM Plex Mono',monospace!important;border-radius:var(--radius-sm)!important;}
    .stDateInput input{background:var(--surface)!important;border:1px solid var(--border)!important;color:var(--text)!important;font-family:'IBM Plex Mono',monospace!important;border-radius:var(--radius-sm)!important;}
    label{font-family:'IBM Plex Mono',monospace!important;font-size:0.65rem!important;color:var(--muted)!important;text-transform:uppercase!important;letter-spacing:0.1em!important;margin-bottom:0.3rem!important;}

    /* ── Buttons ── */
    .stButton>button {
        background:transparent!important; color:var(--green)!important;
        border:1px solid var(--border)!important; border-radius:var(--radius-sm)!important;
        font-family:'IBM Plex Mono',monospace!important; font-weight:500!important;
        font-size:0.75rem!important; letter-spacing:0.08em!important;
        padding:0.45rem 1.2rem!important; transition:all 0.15s!important;
        text-transform:uppercase!important;
    }
    .stButton>button:hover{background:var(--green)!important;color:#000!important;border-color:var(--green)!important;}
    .stButton>button[kind="primary"]{background:var(--green)!important;color:#000!important;border-color:var(--green)!important;font-weight:600!important;}

    /* ── Metrics ── */
    .metric-card{background:var(--surface);border:1px solid var(--border);padding:1rem 1.2rem;border-radius:var(--radius);text-align:center;transition:border-color 0.15s;}
    .metric-card:hover{border-color:var(--border2);}
    .metric-val{font-family:'IBM Plex Mono',monospace;font-size:1.15rem;font-weight:700;letter-spacing:-0.01em;}
    .metric-lbl{font-family:'IBM Plex Mono',monospace;font-size:0.55rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.12em;margin-top:0.35rem;}
    .pos{color:var(--green);} .neg{color:var(--red);} .neu{color:var(--text);}

    /* ── Panels ── */
    .panel{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:1.5rem;margin-bottom:1.5rem;}
    .panel-sm{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:1rem;margin-bottom:1rem;}
    .config-panel{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:1.4rem 1.4rem 0.6rem 1.4rem;margin-bottom:1.5rem;}

    /* ── Section divider ── */
    .divider{display:flex;align-items:center;gap:1rem;margin:2rem 0 1.2rem 0;font-family:'IBM Plex Mono',monospace;font-size:0.6rem;color:var(--muted);letter-spacing:0.18em;text-transform:uppercase;}
    .divider::before,.divider::after{content:'';flex:1;height:1px;background:var(--border);}
    /* keep old class working */
    .price-divider{display:flex;align-items:center;gap:1rem;margin:2rem 0 1.2rem 0;font-family:'IBM Plex Mono',monospace;font-size:0.6rem;color:var(--muted);letter-spacing:0.18em;text-transform:uppercase;}
    .price-divider::before,.price-divider::after{content:'';flex:1;height:1px;background:var(--border);}

    /* ── Page header ── */
    .page-header{padding:2rem 0 1.5rem 0;margin-bottom:0.5rem;}
    .page-header h1{font-size:2.8rem!important;margin:0 0 0.4rem 0!important;}
    .page-header p{color:var(--text2);font-size:0.9rem;margin:0;max-width:600px;}

    /* ── Status boxes ── */
    .info-box{background:var(--green-dim);border:1px solid #00d68f30;border-radius:var(--radius-sm);padding:0.75rem 1rem;font-size:0.82rem;color:var(--green);font-family:'IBM Plex Mono',monospace;line-height:1.5;}
    .warn-box{background:var(--red-dim);border:1px solid #ff475730;border-radius:var(--radius-sm);padding:0.75rem 1rem;font-size:0.82rem;color:var(--red);font-family:'IBM Plex Mono',monospace;line-height:1.5;}

    /* ── Chat bubbles ── */
    .chat-user{
        background:var(--surface2);border:1px solid var(--border);
        border-radius:12px 12px 4px 12px;padding:1rem 1.25rem;margin:1rem 0 0.5rem 3rem;
        font-size:0.9rem;line-height:1.65;color:var(--text);
    }
    .chat-ai{
        background:linear-gradient(135deg,#071a0f 0%,#0a1a10 100%);
        border:1px solid #00d68f22;
        border-radius:4px 12px 12px 12px;padding:1.1rem 1.25rem;margin:0.5rem 3rem 1rem 0;
        font-size:0.9rem;line-height:1.75;color:var(--text2);
    }
    .chat-lbl{font-family:'IBM Plex Mono',monospace;font-size:0.6rem;text-transform:uppercase;letter-spacing:0.15em;color:var(--muted);margin-bottom:0.5rem;display:flex;align-items:center;gap:0.4rem;}
    .chat-lbl .dot{width:6px;height:6px;border-radius:50%;background:var(--green);display:inline-block;}

    /* ── Quick-ask chips ── */
    .chip-row{display:flex;flex-wrap:wrap;gap:0.5rem;margin:0.75rem 0;}
    .chip{
        background:var(--surface);border:1px solid var(--border);
        border-radius:20px;padding:0.4rem 1rem;
        font-family:'IBM Plex Mono',monospace;font-size:0.7rem;color:var(--text2);
        cursor:pointer;transition:all 0.15s;white-space:nowrap;
    }
    .chip:hover{border-color:var(--green);color:var(--green);}

    /* ── Feature cards ── */
    .feat-card{
        background:var(--surface);border:1px solid var(--border);
        border-radius:var(--radius);padding:1.5rem;height:100%;
        transition:border-color 0.2s,transform 0.2s;cursor:default;
    }
    .feat-card:hover{border-color:var(--border2);transform:translateY(-1px);}
    .feat-icon{font-size:1.4rem;margin-bottom:0.75rem;}
    .feat-title{font-family:'IBM Plex Mono',monospace;font-size:0.72rem;font-weight:600;text-transform:uppercase;letter-spacing:0.15em;color:var(--text);margin-bottom:0.5rem;}
    .feat-desc{font-size:0.82rem;color:var(--text2);line-height:1.6;}

    /* ── Navbar ── */
    .nb{
        background:rgba(7,9,13,0.95);backdrop-filter:blur(12px);
        border-bottom:1px solid var(--border);
        padding:0;margin:-1rem -2.5rem 0 -2.5rem;
        display:flex;align-items:stretch;position:sticky;top:0;z-index:1000;
    }
    .nb-brand{
        font-family:'Bebas Neue',sans-serif;font-size:1.6rem;letter-spacing:0.12em;
        padding:0.7rem 1.8rem;border-right:1px solid var(--border);
        display:flex;align-items:center;flex-shrink:0;
    }
    .nb-brand .g{color:var(--green);} .nb-brand .r{color:var(--red);}
    .nb-links{display:flex;align-items:stretch;flex:1;}
    .nb-tag{
        font-family:'IBM Plex Mono',monospace;font-size:0.55rem;color:var(--muted);
        letter-spacing:0.18em;padding:0.7rem 1.8rem;
        display:flex;align-items:center;border-left:1px solid var(--border);
        text-transform:uppercase;
    }
    .nb-links [data-testid="stPageLink-NavLink"]{
        font-family:'IBM Plex Mono',monospace!important;font-size:0.68rem!important;
        font-weight:500!important;text-transform:uppercase!important;letter-spacing:0.12em!important;
        color:var(--muted)!important;text-decoration:none!important;
        padding:0 1.2rem!important;border-radius:0!important;border:none!important;
        border-bottom:2px solid transparent!important;background:transparent!important;
        display:flex!important;align-items:center!important;height:100%!important;
        transition:color 0.15s,border-color 0.15s!important;white-space:nowrap!important;
    }
    .nb-links [data-testid="stPageLink-NavLink"]:hover{color:var(--text)!important;border-bottom:2px solid var(--border2)!important;}
    .nb-links [data-testid="stPageLink-NavLink"][aria-current="page"]{color:var(--green)!important;border-bottom:2px solid var(--green)!important;}

    /* ── Ticker tape ── */
    .ticker-wrap{overflow:hidden;background:var(--surface);border-bottom:1px solid var(--border);padding:0.45rem 0;margin:0 -2.5rem 2rem -2.5rem;}
    .ticker-tape{display:inline-flex;animation:ticker 40s linear infinite;white-space:nowrap;}
    .ticker-item{font-family:'IBM Plex Mono',monospace;font-size:0.68rem;padding:0 1.8rem;letter-spacing:0.04em;}
    .t-up{color:var(--green);} .t-dn{color:var(--red);} .t-sym{color:var(--text);margin-right:0.5rem;font-weight:500;}
    @keyframes ticker{0%{transform:translateX(0)}100%{transform:translateX(-50%)}}

    /* ── Scrollbar ── */
    ::-webkit-scrollbar{width:4px;} ::-webkit-scrollbar-track{background:var(--bg);} ::-webkit-scrollbar-thumb{background:#263045;border-radius:2px;}
    hr{border-color:var(--border)!important;}
    [data-testid="stExpander"]{background:var(--surface)!important;border:1px solid var(--border)!important;border-radius:var(--radius)!important;}
    [data-testid="stExpander"] summary{font-family:'IBM Plex Mono',monospace!important;font-size:0.78rem!important;color:var(--text2)!important;}

    /* ── Misc ── */
    .tag{display:inline-block;font-family:'IBM Plex Mono',monospace;font-size:0.6rem;padding:2px 8px;border-radius:3px;text-transform:uppercase;letter-spacing:0.1em;}
    .tag-green{background:var(--green-dim);color:var(--green);border:1px solid #00d68f30;}
    .tag-red{background:var(--red-dim);color:var(--red);border:1px solid #ff475730;}
    .tag-blue{background:#4da6ff18;color:#4da6ff;border:1px solid #4da6ff30;}
    .tag-purple{background:#b388ff18;color:#b388ff;border:1px solid #b388ff30;}
    .row-item{padding:0.6rem 0;border-bottom:1px solid var(--border);display:flex;align-items:flex-start;gap:0.5rem;}
    .row-item:last-child{border-bottom:none;}
    .empty-state{text-align:center;padding:3rem 1rem;color:var(--muted);font-family:'IBM Plex Mono',monospace;font-size:0.78rem;}
</style>
"""

# Plotly dark theme
PLOTLY_THEME = dict(
    paper_bgcolor="#07090d",
    plot_bgcolor="#07090d",
    font=dict(family="IBM Plex Mono", color="#8892a4", size=11),
    xaxis=dict(gridcolor="#1a2235", linecolor="#1a2235", tickfont=dict(size=10)),
    yaxis=dict(gridcolor="#1a2235", linecolor="#1a2235", tickfont=dict(size=10)),
    legend=dict(bgcolor="#0d1117", bordercolor="#1a2235", borderwidth=1),
    margin=dict(l=10, r=10, t=40, b=10),
)
