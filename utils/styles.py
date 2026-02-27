"""
Shared styles for 11% platform.
Import SHARED_CSS in every page with: st.markdown(SHARED_CSS, unsafe_allow_html=True)
"""

SHARED_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=IBM+Plex+Mono:wght@300;400;600&family=IBM+Plex+Sans:wght@300;400;600&display=swap');

    :root {
        --bg:        #07090d;
        --surface:   #0d1117;
        --surface2:  #131923;
        --border:    #1c2333;
        --border2:   #263045;
        --gold:      #f0b429;
        --gold2:     #ffd166;
        --green:     #00d68f;
        --red:       #ff4757;
        --blue:      #4da6ff;
        --text:      #cdd5e0;
        --muted:     #4a5568;
        --font-display: 'Bebas Neue', sans-serif;
        --font-mono:    'IBM Plex Mono', monospace;
        --font-body:    'IBM Plex Sans', sans-serif;
    }

    html, body,
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"],
    .main { background-color: var(--bg) !important; color: var(--text) !important; font-family: var(--font-body) !important; }

    [data-testid="stSidebar"] { background-color: var(--surface) !important; border-right: 1px solid var(--border) !important; }

    h1 { font-family: var(--font-display) !important; font-size: 2.8rem !important; letter-spacing: 0.06em; color: var(--text) !important; line-height: 1.1 !important; }
    h2 { font-family: var(--font-display) !important; font-size: 1.8rem !important; letter-spacing: 0.05em; color: var(--text) !important; }
    h3 { font-family: var(--font-mono) !important; font-size: 0.78rem !important; color: var(--gold) !important; text-transform: uppercase; letter-spacing: 0.15em; margin-bottom: 0.8rem !important; }

    .stButton > button {
        background: var(--gold) !important; color: #000 !important; border: none !important;
        border-radius: 3px !important; font-family: var(--font-mono) !important;
        font-weight: 600 !important; font-size: 0.82rem !important;
        letter-spacing: 0.08em !important; padding: 0.5rem 1.6rem !important;
        transition: all 0.15s !important;
    }
    .stButton > button:hover { background: var(--gold2) !important; transform: translateY(-1px) !important; }

    .stTextInput input, .stNumberInput input {
        background: var(--surface2) !important; border: 1px solid var(--border2) !important;
        color: var(--text) !important; font-family: var(--font-mono) !important;
        font-size: 0.9rem !important; border-radius: 3px !important;
    }
    .stSelectbox > div > div {
        background: var(--surface2) !important; border: 1px solid var(--border2) !important;
        color: var(--text) !important; font-family: var(--font-mono) !important;
        border-radius: 3px !important;
    }
    [data-testid="stExpander"] {
        background: var(--surface) !important; border: 1px solid var(--border) !important; border-radius: 6px !important;
    }
    .stTabs [data-baseweb="tab-list"] { background: var(--surface) !important; border-radius: 4px; gap: 2px; }
    .stTabs [data-baseweb="tab"] {
        font-family: var(--font-mono) !important; font-size: 0.78rem !important;
        color: var(--muted) !important; letter-spacing: 0.08em; text-transform: uppercase;
    }
    .stTabs [aria-selected="true"] { color: var(--gold) !important; background: var(--surface2) !important; }

    hr { border-color: var(--border) !important; margin: 1.5rem 0 !important; }

    .metric-card {
        background: var(--surface); border: 1px solid var(--border);
        border-radius: 6px; padding: 1.1rem 0.8rem; text-align: center;
        transition: border-color 0.2s;
    }
    .metric-card:hover { border-color: var(--border2); }
    .metric-val { font-family: var(--font-mono); font-size: 1.55rem; font-weight: 600; line-height: 1.1; }
    .metric-lbl { font-family: var(--font-mono); font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.12em; color: var(--muted); margin-top: 0.3rem; }
    .pos { color: var(--green); }
    .neg { color: var(--red); }
    .neu { color: var(--gold); }

    .pill {
        display: inline-block; padding: 0.2rem 0.7rem; border-radius: 20px;
        font-family: var(--font-mono); font-size: 0.7rem; font-weight: 600;
        letter-spacing: 0.06em; margin-right: 0.4rem;
    }
    .pill-green { background: #00d68f18; color: var(--green); border: 1px solid #00d68f33; }
    .pill-gold  { background: #f0b42918; color: var(--gold);  border: 1px solid #f0b42933; }
    .pill-red   { background: #ff475718; color: var(--red);   border: 1px solid #ff475733; }
    .pill-blue  { background: #4da6ff18; color: var(--blue);  border: 1px solid #4da6ff33; }

    /* Chat bubbles */
    .chat-user {
        background: var(--surface2); border: 1px solid var(--border2);
        border-radius: 10px 10px 3px 10px; padding: 1rem 1.2rem; margin: 0.6rem 0;
    }
    .chat-ai {
        background: #0d1a2e; border: 1px solid #1a3050;
        border-radius: 10px 10px 10px 3px; padding: 1rem 1.2rem; margin: 0.6rem 0;
    }
    .chat-lbl { font-family: var(--font-mono); font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.12em; color: var(--muted); margin-bottom: 0.4rem; }

    /* Page header bar */
    .page-header {
        border-left: 3px solid var(--gold);
        padding-left: 1rem;
        margin-bottom: 1.5rem;
    }
    .page-header p { color: var(--muted); font-size: 0.88rem; margin-top: 0.2rem; }

    /* Warning / info */
    .info-box {
        background: #0d1a2e; border: 1px solid #1a3050;
        border-radius: 6px; padding: 0.8rem 1rem;
        font-size: 0.82rem; color: var(--blue);
        font-family: var(--font-mono);
    }
    .warn-box {
        background: #1a100a; border: 1px solid #3a2010;
        border-radius: 6px; padding: 0.8rem 1rem;
        font-size: 0.82rem; color: var(--gold);
        font-family: var(--font-mono);
    }
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
