import streamlit as st
import google.generativeai as genai
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils.styles import SHARED_CSS
from utils.nav import navbar

st.set_page_config(page_title="Assistant | 11%", page_icon="💬", layout="wide")
st.markdown(SHARED_CSS, unsafe_allow_html=True)

# ── API setup ─────────────────────────────────────────────────────────────────
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    api_key = os.getenv("GEMINI_API_KEY", "")

if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")
else:
    model = None

# ── Session state ─────────────────────────────────────────────────────────────
if "messages"         not in st.session_state: st.session_state.messages = []
if "user_profile"     not in st.session_state: st.session_state.user_profile = {}

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div style="font-family:\'Bebas Neue\',sans-serif;font-size:1.8rem;color:#f0b429;letter-spacing:0.1em;">11%</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### YOUR PROFILE")
    st.caption("Help the AI personalise responses for you.")

    experience = st.selectbox("Experience Level", ["Beginner", "Intermediate", "Advanced"])
    style = st.selectbox("Trading Style", ["Day Trading", "Swing Trading", "Long-term Investing", "Not sure yet"])
    risk = st.selectbox("Risk Tolerance", ["Low — capital preservation", "Medium — balanced", "High — aggressive growth"])
    goals = st.text_input("Your goal", placeholder="e.g. Grow $10k over 2 years")

    st.session_state.user_profile = {
        "experience": experience, "style": style, "risk": risk, "goals": goals
    }

    st.markdown("---")
    if st.button("🗑️  Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
    <h1>AI ASSISTANT</h1>
    <p>Your personal trading coach. Ask anything — strategies, analysis, results, or concepts.</p>
</div>
""", unsafe_allow_html=True)

if not api_key:
    st.markdown("""
    <div class="warn-box">
        ⚠️ No Gemini API key found. Add GEMINI_API_KEY to your Streamlit Secrets to enable the assistant.
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── Context from other pages ──────────────────────────────────────────────────
last_bt  = st.session_state.get("last_backtest")
last_an  = st.session_state.get("last_analysis")

context_parts = []
if last_bt:
    m = last_bt["metrics"]
    context_parts.append(
        f"Last backtest: {last_bt['ticker']} with {last_bt['strategy']} — "
        f"Return {m['total_return']:+.2f}%, Drawdown {m['max_drawdown']:.2f}%, "
        f"Win Rate {m['win_rate']:.0f}%"
    )
if last_an:
    context_parts.append(f"Last analysis: {last_an['ticker']}")

if context_parts:
    st.markdown(f"""
    <div class="info-box" style="margin-bottom:1rem;">
        📎 Context available: {' &nbsp;|&nbsp; '.join(context_parts)}
    </div>
    """, unsafe_allow_html=True)

# ── Quick prompts ─────────────────────────────────────────────────────────────
st.markdown("### QUICK QUESTIONS")
qcols = st.columns(4)
quick_prompts = [
    ("Explain my backtest results", "Can you explain my most recent backtest results in simple terms?"),
    ("Best strategy for beginners", "What trading strategy is best for a beginner to start with and why?"),
    ("What is the Sharpe ratio?", "What is the Sharpe ratio and why does it matter in backtesting?"),
    ("Recommend a strategy for me", "Based on my trading profile, what strategy would you recommend and why?"),
]
for col, (label, prompt) in zip(qcols, quick_prompts):
    with col:
        if st.button(label, use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.rerun()

st.markdown("---")

# ── Build system prompt with full context ─────────────────────────────────────
profile = st.session_state.user_profile

SYSTEM = f"""You are the AI trading coach for 11%, a free trading education platform.
You are a specialized financial and trading assistant. You are knowledgeable, direct, honest, and encouraging.

USER PROFILE:
- Experience: {profile.get('experience','Unknown')}
- Style: {profile.get('style','Unknown')}
- Risk Tolerance: {profile.get('risk','Unknown')}
- Goals: {profile.get('goals','Not specified')}

YOUR CAPABILITIES:
1. Explain backtest results in plain language
2. Recommend personalised strategies based on the user's profile, style, and risk tolerance
3. Evaluate strategies the user is considering (pros, cons, ideal conditions)
4. Teach trading concepts clearly with real examples
5. Help write custom indicator/strategy code in Python for the platform
6. Provide educational financial analysis

PLATFORM CONTEXT — if relevant, reference these:
{chr(10).join(context_parts) if context_parts else 'No recent backtest or analysis available.'}

RULES:
- Always match the explanation complexity to the user's experience level
- NEVER give direct buy/sell recommendations for specific stocks
- Always add a brief disclaimer when discussing analysis or strategies
- When recommending a strategy, explain WHY it suits their profile
- Be honest — if a strategy has weaknesses, say so
- Keep responses focused and practical, not overly long
- When writing code, always add clear comments"""

# ── Display chat history ──────────────────────────────────────────────────────
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"""
        <div class="chat-user">
            <div class="chat-lbl">YOU</div>
            {msg['content']}
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="chat-ai">
            <div class="chat-lbl" style="color:#4da6ff;">🤖 11% AI COACH</div>
            {msg['content'].replace(chr(10), '<br>')}
        </div>""", unsafe_allow_html=True)

# ── Generate response if last message is from user ────────────────────────────
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    with st.spinner("Thinking..."):
        try:
            conversation = [{"role": "user", "parts": [SYSTEM + "\n\nBegin."]}]
            for msg in st.session_state.messages:
                role = "user" if msg["role"] == "user" else "model"
                conversation.append({"role": role, "parts": [msg["content"]]})

            response = model.generate_content(conversation)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            st.rerun()
        except Exception as e:
            st.error(f"Gemini error: {e}")

# ── Chat input ────────────────────────────────────────────────────────────────
user_input = st.chat_input("Ask your trading coach anything...")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.rerun()
