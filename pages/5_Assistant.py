import streamlit as st
import google.generativeai as genai
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.styles import SHARED_CSS
from utils.nav import navbar

st.set_page_config(page_title="AI Coach | 11%", layout="wide", initial_sidebar_state="collapsed")
st.markdown(SHARED_CSS, unsafe_allow_html=True)
navbar()

# ── API ────────────────────────────────────────────────────────────────────────
try:    api_key = st.secrets["GEMINI_API_KEY"]
except: api_key = os.getenv("GEMINI_API_KEY", "")
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")
else:
    model = None

for k, v in [("messages",[]), ("coach_profile",{}), ("coach_done",False)]:
    if k not in st.session_state: st.session_state[k] = v

# ── Page header ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
    <div class="page-header-eyebrow">Powered by Gemini</div>
    <h1>AI Trading Coach</h1>
    <p>Overwhelmed by data? Just ask. Explains anything in plain English — from what a Sharpe ratio means to why your strategy lost money.</p>
</div>
""", unsafe_allow_html=True)

if not api_key:
    st.markdown('<div class="warn-box">Add GEMINI_API_KEY to Streamlit Secrets to enable the AI coach.</div>', unsafe_allow_html=True)

# ── Profile (collapsed by default once saved) ──────────────────────────────────
with st.expander("⚙️  Your profile — helps the coach tailor answers", expanded=not st.session_state.coach_done):
    p1, p2, p3, p4 = st.columns([1,1,1,2])
    with p1: experience = st.selectbox("Experience", ["Beginner","Some knowledge","Intermediate","Advanced"], key="exp")
    with p2: style      = st.selectbox("Style",      ["Not sure","Day trading","Swing trading","Long-term investing"], key="sty")
    with p3: risk       = st.selectbox("Risk",       ["Low","Medium","High"], key="rsk")
    with p4: goals      = st.text_input("Goal (optional)", placeholder="e.g. Understand RSI, build a strategy", key="gls")
    col_sv, col_cl = st.columns([1,5])
    with col_sv:
        if st.button("Save", type="primary", key="save_profile"):
            st.session_state.coach_profile = {"experience":experience,"style":style,"risk":risk,"goals":goals}
            st.session_state.coach_done = True
            st.rerun()
    with col_cl:
        if st.button("Clear chat", key="clear_chat"):
            st.session_state.messages = []
            st.rerun()

prof = st.session_state.coach_profile or {"experience":"Beginner","style":"Not sure","risk":"Medium","goals":""}

# ── Context pill ───────────────────────────────────────────────────────────────
ctx_parts = []
last_bt = st.session_state.get("last_backtest")
last_an = st.session_state.get("last_analysis")
if last_bt:
    m = last_bt["metrics"]
    ctx_parts.append(f"Backtest: {last_bt['ticker']} · {last_bt['strategy']} · Return {m['total_return']:+.2f}% · Sharpe {m['sharpe']}")
if last_an:
    ctx_parts.append(f"Analysis: {last_an['ticker']}")
if ctx_parts:
    st.markdown(f'<div class="info-box" style="margin-bottom:1rem;font-size:0.74rem;">📎 &nbsp;{" &nbsp;|&nbsp; ".join(ctx_parts)}</div>', unsafe_allow_html=True)

# ── Quick chips ────────────────────────────────────────────────────────────────
CHIPS = [
    ("Explain my results",   "Can you explain my most recent backtest results in plain English? What do the numbers mean?"),
    ("Best beginner strategy","What is the best strategy for a beginner to start with and why?"),
    ("What is Sharpe ratio?", "What is the Sharpe ratio, how is it calculated, and why does it matter?"),
    ("Recommend for my profile","Based on my trading profile, what strategy would you recommend and why?"),
    ("Why strategies fail",  "What are the most common reasons a backtested strategy fails in live trading?"),
    ("Explain drawdown",     "What is max drawdown and how should I think about it when evaluating a strategy?"),
]
ch_cols = st.columns(len(CHIPS))
for col, (label, prompt) in zip(ch_cols, CHIPS):
    with col:
        if st.button(label, key=f"chip_{label[:10]}", use_container_width=True):
            st.session_state.messages.append({"role":"user","content":prompt})
            st.rerun()

st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

# ── System prompt ──────────────────────────────────────────────────────────────
SYSTEM = f"""You are the AI trading coach for 11%, a free trading education platform.
You are knowledgeable, direct, honest, and encouraging. Never give direct buy/sell advice on specific stocks.

USER PROFILE: Experience={prof.get('experience')} · Style={prof.get('style')} · Risk={prof.get('risk')} · Goals={prof.get('goals') or 'not specified'}

PLATFORM CONTEXT:
{chr(10).join(ctx_parts) if ctx_parts else 'No recent backtest or analysis.'}

RULES:
- Match explanation depth to the user's experience level
- When recommending a strategy, explain WHY it suits their profile
- Be honest — name weaknesses and risks clearly
- Keep responses focused and practical
- Add a brief disclaimer when discussing specific analysis"""

# ── Chat history ───────────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"""
        <div class="chat-user">
            <div class="chat-lbl">You</div>
            {msg['content']}
        </div>""", unsafe_allow_html=True)
    else:
        formatted = msg['content'].replace('\n\n','</p><p style="margin:0.5rem 0;color:#8896ab;">').replace('\n','<br>')
        st.markdown(f"""
        <div class="chat-ai">
            <div class="chat-lbl"><span class="dot"></span>11% AI Coach</div>
            <p style="margin:0;color:#8896ab;">{formatted}</p>
        </div>""", unsafe_allow_html=True)

# ── Auto-respond if last message is user ──────────────────────────────────────
if api_key and st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    with st.spinner("Thinking…"):
        try:
            history = [{"role":"user","parts":[SYSTEM + "\n\nBegin."]}]
            for msg in st.session_state.messages:
                role = "user" if msg["role"]=="user" else "model"
                history.append({"role":role,"parts":[msg["content"]]})
            resp = model.generate_content(history)
            st.session_state.messages.append({"role":"assistant","content":resp.text})
            st.rerun()
        except Exception as e:
            st.error(f"Gemini error: {e}")

# ── Input ──────────────────────────────────────────────────────────────────────
user_input = st.chat_input("Ask your trading coach anything…")
if user_input:
    st.session_state.messages.append({"role":"user","content":user_input})
    st.rerun()
