import streamlit as st
import google.generativeai as genai
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

st.set_page_config(page_title="Assistant | 11%", page_icon="💬", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""
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
    .block-container { padding-top:0!important; padding-left:2rem!important; padding-right:2rem!important; max-width:100%!important; }
    [data-testid="stSidebar"],[data-testid="stSidebarNav"],[data-testid="collapsedControl"] { display:none!important; }
    /* Navbar */
    .navbar { background:#07090d; border-bottom:1px solid #1c2333; padding:0.7rem 2rem; display:flex; align-items:center; gap:2rem; margin-left:-2rem; margin-right:-2rem; margin-bottom:2rem; position:sticky; top:0; z-index:999; }
    .navbar-brand { font-family:'Bebas Neue',sans-serif; font-size:1.8rem; letter-spacing:0.1em; text-decoration:none; flex-shrink:0; }
    .navbar-brand .g { color:#00d68f; }
    .navbar-brand .r { color:#ff4757; }
    .nav-links { display:flex; gap:0.2rem; flex:1; }
    .nav-link { font-family:'IBM Plex Mono',monospace; font-size:0.68rem; text-transform:uppercase; letter-spacing:0.1em; color:#3a4558; text-decoration:none; padding:0.38rem 0.9rem; border-radius:3px; transition:all 0.15s; }
    .nav-link:hover { color:#00d68f; background:#0d1117; }
    .nav-link.active { color:#00d68f; background:#071a0f; border:1px solid #0d3320; }
    .nav-badge { font-family:'IBM Plex Mono',monospace; font-size:0.58rem; color:#3a4558; letter-spacing:0.12em; }
    /* Typography */
    h1 { font-family:'Bebas Neue',sans-serif!important; letter-spacing:0.06em; color:var(--text)!important; }
    h2 { font-family:'Bebas Neue',sans-serif!important; }
    h3 { font-family:'IBM Plex Mono',monospace!important; font-size:0.75rem!important; color:var(--green)!important; text-transform:uppercase; letter-spacing:0.15em; }
    /* Inputs */
    .stTextInput input, .stNumberInput input { background:#0d1117!important; border:1px solid #1c2333!important; color:#cdd5e0!important; font-family:'IBM Plex Mono',monospace!important; font-size:0.85rem!important; border-radius:3px!important; }
    .stTextInput input:focus, .stNumberInput input:focus { border-color:#00d68f!important; box-shadow:none!important; }
    div[data-baseweb="select"]>div { background:#0d1117!important; border:1px solid #1c2333!important; color:#cdd5e0!important; font-family:'IBM Plex Mono',monospace!important; border-radius:3px!important; }
    .stDateInput input { background:#0d1117!important; border:1px solid #1c2333!important; color:#cdd5e0!important; font-family:'IBM Plex Mono',monospace!important; border-radius:3px!important; }
    label { font-family:'IBM Plex Mono',monospace!important; font-size:0.68rem!important; color:#3a4558!important; text-transform:uppercase!important; letter-spacing:0.1em!important; }
    /* Buttons */
    .stButton>button { background:transparent!important; color:#00d68f!important; border:1px solid #00d68f!important; border-radius:3px!important; font-family:'IBM Plex Mono',monospace!important; font-weight:600!important; font-size:0.78rem!important; letter-spacing:0.1em!important; padding:0.45rem 1.4rem!important; transition:all 0.15s!important; text-transform:uppercase!important; }
    .stButton>button:hover { background:#00d68f!important; color:#000!important; }
    /* Metrics */
    .metric-card { background:#0d1117; border:1px solid #1c2333; padding:1rem; border-radius:4px; text-align:center; }
    .metric-val { font-family:'IBM Plex Mono',monospace; font-size:1.1rem; font-weight:700; }
    .metric-lbl { font-family:'IBM Plex Mono',monospace; font-size:0.55rem; color:#3a4558; text-transform:uppercase; margin-top:0.3rem; }
    .pos{color:#00d68f;} .neg{color:#ff4757;} .neu{color:#cdd5e0;}
    /* Config panel */
    .config-panel { background:#0d1117; border:1px solid #1c2333; border-radius:6px; padding:1.5rem 1.5rem 0.5rem 1.5rem; margin-bottom:1.5rem; }
    /* Dividers */
    .price-divider { display:flex; align-items:center; gap:1rem; margin:1.5rem 0; font-family:'IBM Plex Mono',monospace; font-size:0.65rem; color:#3a4558; }
    .price-divider::before,.price-divider::after { content:''; flex:1; height:1px; background:#1c2333; }
    /* Page header */
    .page-header { border-left:3px solid #00d68f; padding-left:1rem; margin-bottom:1.5rem; }
    .page-header p { color:#3a4558; font-size:0.88rem; margin-top:0.2rem; }
    /* Boxes */
    .info-box { background:#071a0f; border:1px solid #0d3320; border-radius:6px; padding:0.8rem 1rem; font-size:0.82rem; color:#00d68f; font-family:'IBM Plex Mono',monospace; }
    .warn-box { background:#1a0a08; border:1px solid #3a1008; border-radius:6px; padding:0.8rem 1rem; font-size:0.82rem; color:#ff4757; font-family:'IBM Plex Mono',monospace; }
    /* Chat */
    .chat-user { background:#0d1117; border:1px solid #1c2333; border-radius:10px 10px 3px 10px; padding:1rem 1.2rem; margin:0.6rem 0; }
    .chat-ai { background:#071a0f; border:1px solid #0d3320; border-radius:10px 10px 10px 3px; padding:1rem 1.2rem; margin:0.6rem 0; }
    .chat-lbl { font-family:'IBM Plex Mono',monospace; font-size:0.65rem; text-transform:uppercase; letter-spacing:0.12em; color:#3a4558; margin-bottom:0.4rem; }
    /* Ticker tape */
    .ticker-wrap { width:100%; overflow:hidden; background:#0d1117; border-bottom:1px solid #1c2333; padding:0.4rem 0; }
    .ticker-tape { display:inline-flex; animation:ticker 30s linear infinite; white-space:nowrap; }
    .ticker-item { font-family:'IBM Plex Mono',monospace; font-size:0.68rem; padding:0 1.5rem; letter-spacing:0.06em; }
    .ticker-up{color:#00d68f;} .ticker-down{color:#ff4757;}
    .ticker-sym { color:#cdd5e0; margin-right:0.4rem; }
    @keyframes ticker { 0%{transform:translateX(0)} 100%{transform:translateX(-50%)} }
    ::-webkit-scrollbar{width:4px;} ::-webkit-scrollbar-track{background:#07090d;} ::-webkit-scrollbar-thumb{background:#263045;border-radius:2px;}
    hr{border-color:#1c2333!important;}
    [data-testid="stExpander"]{background:#0d1117!important;border:1px solid #1c2333!important;border-radius:4px!important;}
</style>
""", unsafe_allow_html=True)
st.markdown('''<div class="navbar"><a class="navbar-brand" href="/app"><span class="g">11</span><span class="r">%</span></a><div class="nav-links"><a class="nav-link" href="/app">🏠 Home</a><a class="nav-link" href="/1_Backtest">🔬 Backtest</a><a class="nav-link" href="/2_Indicator_Test">📊 Indicators</a><a class="nav-link" href="/3_Replay">▶ Replay</a><a class="nav-link" href="/4_Analysis">🧠 Analysis</a><a class="nav-link active" href="/5_Assistant">💬 Assistant</a></div><span class="nav-badge">FREE · OPEN SOURCE</span></div>''', unsafe_allow_html=True)

try:    api_key = st.secrets["GEMINI_API_KEY"]
except: api_key = os.getenv("GEMINI_API_KEY", "")
if api_key: genai.configure(api_key=api_key); model = genai.GenerativeModel("gemini-2.5-flash")
else:        model = None

if "messages"     not in st.session_state: st.session_state.messages=[]
if "user_profile" not in st.session_state: st.session_state.user_profile={}

st.markdown('''<div class="page-header"><h1>AI ASSISTANT</h1><p>Your personal trading coach. Ask anything — strategies, analysis, results, or concepts.</p></div>''', unsafe_allow_html=True)

if not api_key:
    st.markdown('<div class="warn-box">⚠️ No Gemini API key. Add GEMINI_API_KEY to Streamlit Secrets.</div>', unsafe_allow_html=True)
    st.stop()

# ── Profile panel ─────────────────────────────────────────────────────────────
st.markdown('<div class="price-divider">YOUR PROFILE</div>', unsafe_allow_html=True)
st.markdown('<div class="config-panel">', unsafe_allow_html=True)
pc1,pc2,pc3,pc4 = st.columns(4)
with pc1: experience = st.selectbox("Experience Level", ["Beginner","Intermediate","Advanced"])
with pc2: style      = st.selectbox("Trading Style",    ["Day Trading","Swing Trading","Long-term Investing","Not sure yet"])
with pc3: risk       = st.selectbox("Risk Tolerance",   ["Low — capital preservation","Medium — balanced","High — aggressive growth"])
with pc4: goals      = st.text_input("Your goal", placeholder="e.g. Grow $10k over 2 years")
cc1, cc2 = st.columns([6,1])
with cc2:
    if st.button("🗑️  Clear Chat", use_container_width=True):
        st.session_state.messages=[]; st.rerun()
st.markdown('</div>', unsafe_allow_html=True)
st.session_state.user_profile={"experience":experience,"style":style,"risk":risk,"goals":goals}

last_bt=st.session_state.get("last_backtest"); last_an=st.session_state.get("last_analysis")
context_parts=[]
if last_bt:
    mm=last_bt["metrics"]
    context_parts.append(f"Last backtest: {last_bt['ticker']} with {last_bt['strategy']} — Return {mm['total_return']:+.2f}%, Drawdown {mm['max_drawdown']:.2f}%, Win Rate {mm['win_rate']:.0f}%")
if last_an: context_parts.append(f"Last analysis: {last_an['ticker']}")
if context_parts:
    st.markdown(f'<div class="info-box">📎 Context: {" &nbsp;|&nbsp; ".join(context_parts)}</div>', unsafe_allow_html=True)

st.markdown('<div class="price-divider">QUICK QUESTIONS</div>', unsafe_allow_html=True)
qcols=st.columns(4)
quick=[("Explain my results","Can you explain my most recent backtest results in simple terms?"),("Best strategy for beginners","What trading strategy is best for a beginner to start with and why?"),("What is the Sharpe ratio?","What is the Sharpe ratio and why does it matter in backtesting?"),("Recommend a strategy","Based on my trading profile, what strategy would you recommend and why?")]
for col,(label,prompt) in zip(qcols,quick):
    with col:
        if st.button(label,use_container_width=True): st.session_state.messages.append({"role":"user","content":prompt}); st.rerun()

profile=st.session_state.user_profile
SYSTEM=f"""You are the AI trading coach for 11%, a free trading education platform.
USER PROFILE: Experience: {profile.get("experience","Unknown")} | Style: {profile.get("style","Unknown")} | Risk: {profile.get("risk","Unknown")} | Goals: {profile.get("goals","Not specified")}
CONTEXT: {chr(10).join(context_parts) if context_parts else "No recent activity."}
RULES: Match complexity to experience. NEVER give direct buy/sell stock recommendations. Always add disclaimers. Be honest."""

st.markdown('<div class="price-divider">CHAT</div>', unsafe_allow_html=True)
for msg in st.session_state.messages:
    if msg["role"]=="user":
        st.markdown(f'<div class="chat-user"><div class="chat-lbl">YOU</div>{msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-ai"><div class="chat-lbl" style="color:#00d68f;">🤖 11% AI COACH</div>{msg["content"].replace(chr(10),"<br>")}</div>', unsafe_allow_html=True)

if st.session_state.messages and st.session_state.messages[-1]["role"]=="user":
    with st.spinner("Thinking..."):
        try:
            conversation=[{"role":"user","parts":[SYSTEM+"\n\nBegin."]}]
            for msg in st.session_state.messages:
                conversation.append({"role":"user" if msg["role"]=="user" else "model","parts":[msg["content"]]})
            response=model.generate_content(conversation)
            st.session_state.messages.append({"role":"assistant","content":response.text}); st.rerun()
        except Exception as e: st.error(f"Gemini error: {e}")

user_input=st.chat_input("Ask your trading coach anything...")
if user_input: st.session_state.messages.append({"role":"user","content":user_input}); st.rerun()
