import streamlit as st
import google.generativeai as genai
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

st.set_page_config(page_title="Assistant | 11%", page_icon="💬", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""<style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=IBM+Plex+Mono:wght@300;400;600;700&family=IBM+Plex+Sans:wght@300;400;600&display=swap');
    :root {
        --bg:#07090d; --surface:#0d1117; --border:#1c2333;
        --green:#00d68f; --red:#ff4757; --text:#cdd5e0; --muted:#3a4558;
        --grid:rgba(255,255,255,0.03);
    }
    /* ── Kill ALL Streamlit chrome ── */
    header[data-testid="stHeader"] { display:none!important; }
    [data-testid="stToolbar"] { display:none!important; }
    [data-testid="stDecoration"] { display:none!important; }
    [data-testid="stSidebar"] { display:none!important; }
    [data-testid="stSidebarNav"] { display:none!important; }
    [data-testid="collapsedControl"] { display:none!important; }
    footer { display:none!important; }
    #MainMenu { display:none!important; }
    .stDeployButton { display:none!important; }
    /* ── Layout ── */
    html,body,[data-testid="stAppViewContainer"],[data-testid="stMain"],.main {
        background-color:var(--bg)!important; color:var(--text)!important;
        font-family:'IBM Plex Sans',sans-serif!important;
    }
    [data-testid="stMain"] {
        background-image:linear-gradient(var(--grid) 1px,transparent 1px),linear-gradient(90deg,var(--grid) 1px,transparent 1px)!important;
        background-size:48px 48px!important;
        padding-top:0!important;
    }
    .block-container { padding-top:0!important; padding-left:2rem!important; padding-right:2rem!important; max-width:100%!important; }
    /* ── Navbar ── */
    .nb { background:#07090d; border-bottom:1px solid #1c2333; padding:0; margin:-1rem -2rem 2rem -2rem; display:flex; align-items:stretch; position:sticky; top:0; z-index:1000; }
    .nb-brand { font-family:'Bebas Neue',sans-serif; font-size:1.7rem; letter-spacing:0.1em; color:var(--text); padding:0.6rem 1.6rem; border-right:1px solid #1c2333; display:flex; align-items:center; flex-shrink:0; }
    .nb-brand .g { color:#00d68f; }
    .nb-brand .r { color:#ff4757; }
    .nb-links { display:flex; align-items:stretch; flex:1; }
    .nb-tag { font-family:'IBM Plex Mono',monospace; font-size:0.58rem; color:#3a4558; letter-spacing:0.15em; padding:0.6rem 1.6rem; display:flex; align-items:center; border-left:1px solid #1c2333; }
    /* Style the st.page_link elements inside the navbar */
    .nb-links [data-testid="stPageLink"] { display:flex; align-items:stretch; }
    .nb-links [data-testid="stPageLink-NavLink"] {
        font-family:'IBM Plex Mono',monospace!important;
        font-size:0.69rem!important;
        font-weight:500!important;
        text-transform:uppercase!important;
        letter-spacing:0.12em!important;
        color:#3a4558!important;
        text-decoration:none!important;
        padding:0 1.1rem!important;
        border-radius:0!important;
        border:none!important;
        border-bottom:2px solid transparent!important;
        background:transparent!important;
        display:flex!important;
        align-items:center!important;
        height:100%!important;
        transition:color 0.15s, border-color 0.15s!important;
        white-space:nowrap!important;
    }
    .nb-links [data-testid="stPageLink-NavLink"]:hover {
        color:#cdd5e0!important;
        background:transparent!important;
        text-decoration:none!important;
        border-bottom:2px solid #3a4558!important;
    }
    .nb-links [data-testid="stPageLink-NavLink"][aria-current="page"] {
        color:#00d68f!important;
        border-bottom:2px solid #00d68f!important;
    }
    /* ── Typography ── */
    h1 { font-family:'Bebas Neue',sans-serif!important; letter-spacing:0.06em; color:var(--text)!important; }
    h2 { font-family:'Bebas Neue',sans-serif!important; }
    h3 { font-family:'IBM Plex Mono',monospace!important; font-size:0.75rem!important; color:var(--green)!important; text-transform:uppercase; letter-spacing:0.15em; }
    /* ── Inputs ── */
    .stTextInput input, .stNumberInput input {
        background:#0d1117!important; border:1px solid #1c2333!important;
        color:#cdd5e0!important; font-family:'IBM Plex Mono',monospace!important;
        font-size:0.85rem!important; border-radius:3px!important;
    }
    .stTextInput input:focus, .stNumberInput input:focus { border-color:#00d68f!important; box-shadow:none!important; }
    div[data-baseweb="select"]>div { background:#0d1117!important; border:1px solid #1c2333!important; color:#cdd5e0!important; font-family:'IBM Plex Mono',monospace!important; border-radius:3px!important; }
    .stDateInput input { background:#0d1117!important; border:1px solid #1c2333!important; color:#cdd5e0!important; font-family:'IBM Plex Mono',monospace!important; border-radius:3px!important; }
    label { font-family:'IBM Plex Mono',monospace!important; font-size:0.68rem!important; color:#3a4558!important; text-transform:uppercase!important; letter-spacing:0.1em!important; }
    /* ── Buttons ── */
    .stButton>button { background:transparent!important; color:#00d68f!important; border:1px solid #00d68f!important; border-radius:3px!important; font-family:'IBM Plex Mono',monospace!important; font-weight:600!important; font-size:0.78rem!important; letter-spacing:0.1em!important; padding:0.45rem 1.4rem!important; transition:all 0.15s!important; text-transform:uppercase!important; }
    .stButton>button:hover { background:#00d68f!important; color:#000!important; }
    /* ── Cards ── */
    .metric-card { background:#0d1117; border:1px solid #1c2333; padding:1rem; border-radius:4px; text-align:center; }
    .metric-val { font-family:'IBM Plex Mono',monospace; font-size:1.1rem; font-weight:700; }
    .metric-lbl { font-family:'IBM Plex Mono',monospace; font-size:0.55rem; color:#3a4558; text-transform:uppercase; margin-top:0.3rem; }
    .pos{color:#00d68f;} .neg{color:#ff4757;} .neu{color:#cdd5e0;}
    /* ── Config panel ── */
    .config-panel { background:#0d1117; border:1px solid #1c2333; border-radius:6px; padding:1.4rem 1.4rem 0.4rem 1.4rem; margin-bottom:1.5rem; }
    /* ── Dividers ── */
    .price-divider { display:flex; align-items:center; gap:1rem; margin:1.5rem 0 1rem 0; font-family:'IBM Plex Mono',monospace; font-size:0.62rem; color:#3a4558; letter-spacing:0.12em; }
    .price-divider::before,.price-divider::after { content:''; flex:1; height:1px; background:#1c2333; }
    /* ── Page header ── */
    .page-header { padding:1.5rem 0 1rem 0; border-bottom:1px solid #1c2333; margin-bottom:1.5rem; }
    .page-header h1 { font-size:2.8rem!important; margin:0!important; }
    .page-header p { color:#3a4558; font-size:0.85rem; margin:0.3rem 0 0 0; }
    /* ── Boxes ── */
    .info-box { background:#071a0f; border:1px solid #0d3320; border-radius:4px; padding:0.8rem 1rem; font-size:0.82rem; color:#00d68f; font-family:'IBM Plex Mono',monospace; }
    .warn-box { background:#1a0a08; border:1px solid #3a1008; border-radius:4px; padding:0.8rem 1rem; font-size:0.82rem; color:#ff4757; font-family:'IBM Plex Mono',monospace; }
    /* ── Chat ── */
    .chat-user { background:#0d1117; border:1px solid #1c2333; border-radius:10px 10px 3px 10px; padding:1rem 1.2rem; margin:0.6rem 0; }
    .chat-ai { background:#071a0f; border:1px solid #0d3320; border-radius:10px 10px 10px 3px; padding:1rem 1.2rem; margin:0.6rem 0; }
    .chat-lbl { font-family:'IBM Plex Mono',monospace; font-size:0.65rem; text-transform:uppercase; letter-spacing:0.12em; color:#3a4558; margin-bottom:0.4rem; }
    /* ── Ticker ── */
    .ticker-wrap { overflow:hidden; background:#0d1117; border-bottom:1px solid #1c2333; padding:0.4rem 0; margin:-2rem -2rem 2rem -2rem; }
    .ticker-tape { display:inline-flex; animation:ticker 35s linear infinite; white-space:nowrap; }
    .ticker-item { font-family:'IBM Plex Mono',monospace; font-size:0.68rem; padding:0 1.5rem; letter-spacing:0.05em; }
    .t-up{color:#00d68f;} .t-dn{color:#ff4757;} .t-sym{color:#cdd5e0;margin-right:0.4rem;}
    @keyframes ticker{0%{transform:translateX(0)}100%{transform:translateX(-50%)}}
    /* ── Misc ── */
    ::-webkit-scrollbar{width:4px;} ::-webkit-scrollbar-track{background:#07090d;} ::-webkit-scrollbar-thumb{background:#263045;border-radius:2px;}
    hr{border-color:#1c2333!important;}
    [data-testid="stExpander"]{background:#0d1117!important;border:1px solid #1c2333!important;border-radius:4px!important;}
</style>""", unsafe_allow_html=True)
st.markdown('<div class="nb"><div class="nb-brand"><span class="g">11</span><span class="r">%</span></div><div class="nb-links">', unsafe_allow_html=True)
_nav = st.columns([1,1,1,1,1,1])
with _nav[0]: st.page_link("app.py",                    label="Home")
with _nav[1]: st.page_link("pages/1_Backtest.py",       label="Backtest")
with _nav[2]: st.page_link("pages/2_Indicator_Test.py", label="Indicators")
with _nav[3]: st.page_link("pages/3_Replay.py",         label="Replay")
with _nav[4]: st.page_link("pages/4_Analysis.py",       label="Analysis")
with _nav[5]: st.page_link("pages/5_Assistant.py",      label="Assistant")
st.markdown('</div><div class="nb-tag">FREE · OPEN SOURCE</div></div>', unsafe_allow_html=True)

try:    api_key=st.secrets["GEMINI_API_KEY"]
except: api_key=os.getenv("GEMINI_API_KEY","")
if api_key: genai.configure(api_key=api_key); model=genai.GenerativeModel("gemini-2.5-flash")
else: model=None

if "messages" not in st.session_state: st.session_state.messages=[]
if "user_profile" not in st.session_state: st.session_state.user_profile={}

st.markdown('''<div class="page-header"><h1>AI Assistant</h1><p>Your personal trading coach. Ask anything — strategies, analysis, results, or concepts.</p></div>''', unsafe_allow_html=True)

if not api_key: st.markdown('<div class="warn-box">No Gemini API key. Add GEMINI_API_KEY to Streamlit Secrets.</div>', unsafe_allow_html=True); st.stop()

st.markdown('<div class="config-panel">', unsafe_allow_html=True)
pc1,pc2,pc3,pc4,pc5 = st.columns([2,2,2,2,1])
with pc1: experience = st.selectbox("Experience Level", ["Beginner","Intermediate","Advanced"])
with pc2: style      = st.selectbox("Trading Style",    ["Day Trading","Swing Trading","Long-term Investing","Not sure yet"])
with pc3: risk       = st.selectbox("Risk Tolerance",   ["Low","Medium","High"])
with pc4: goals      = st.text_input("Your goal", placeholder="e.g. Grow $10k over 2 years")
with pc5:
    st.markdown('<div style="height:1.8rem"></div>', unsafe_allow_html=True)
    if st.button("Clear Chat", use_container_width=True): st.session_state.messages=[]; st.rerun()
st.markdown('</div>', unsafe_allow_html=True)
st.session_state.user_profile={"experience":experience,"style":style,"risk":risk,"goals":goals}

last_bt=st.session_state.get("last_backtest"); last_an=st.session_state.get("last_analysis")
ctx=[]
if last_bt:
    mm=last_bt["metrics"]
    ctx.append(f"Last backtest: {last_bt['ticker']} · {last_bt['strategy']} · Return {mm['total_return']:+.2f}% · Win Rate {mm['win_rate']:.0f}%")
if last_an: ctx.append(f"Last analysis: {last_an['ticker']}")
if ctx: st.markdown(f'<div class="info-box">Context: {" &nbsp;|&nbsp; ".join(ctx)}</div>', unsafe_allow_html=True)

st.markdown('<div class="price-divider">QUICK QUESTIONS</div>', unsafe_allow_html=True)
qc=st.columns(4)
quick=[("Explain my backtest","Can you explain my most recent backtest results in simple terms?"),("Best strategy for beginners","What trading strategy is best for a beginner to start with and why?"),("What is the Sharpe ratio?","What is the Sharpe ratio and why does it matter in backtesting?"),("Recommend a strategy","Based on my trading profile, what strategy would you recommend?")]
for col,(label,prompt) in zip(qc,quick):
    with col:
        if st.button(label,use_container_width=True): st.session_state.messages.append({"role":"user","content":prompt}); st.rerun()

prof=st.session_state.user_profile
SYS=f"""You are the AI trading coach for 11%, a free trading education platform.
USER: Experience={prof.get("experience","Unknown")}, Style={prof.get("style","Unknown")}, Risk={prof.get("risk","Unknown")}, Goals={prof.get("goals","Not specified")}
CONTEXT: {chr(10).join(ctx) if ctx else "No recent activity."}
RULES: Match complexity to experience. Never give direct buy/sell stock picks. Always add disclaimers. Be concise and honest."""

st.markdown('<div class="price-divider">CHAT</div>', unsafe_allow_html=True)
for msg in st.session_state.messages:
    if msg["role"]=="user":
        st.markdown(f'<div class="chat-user"><div class="chat-lbl">You</div>{msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-ai"><div class="chat-lbl" style="color:#00d68f;">11% AI Coach</div>{msg["content"].replace(chr(10),"<br>")}</div>', unsafe_allow_html=True)

if st.session_state.messages and st.session_state.messages[-1]["role"]=="user":
    with st.spinner("Thinking..."):
        try:
            conv=[{"role":"user","parts":[SYS+"\n\nBegin."]}]
            for msg in st.session_state.messages:
                conv.append({"role":"user" if msg["role"]=="user" else "model","parts":[msg["content"]]})
            resp=model.generate_content(conv)
            st.session_state.messages.append({"role":"assistant","content":resp.text}); st.rerun()
        except Exception as e: st.error(f"Gemini error: {e}")

user_input=st.chat_input("Ask your trading coach anything...")
if user_input: st.session_state.messages.append({"role":"user","content":user_input}); st.rerun()
