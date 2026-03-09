import streamlit as st
import google.generativeai as genai
import sys, os, re
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.styles import SHARED_CSS

st.set_page_config(page_title="AI Coach | 11%", layout="wide", initial_sidebar_state="collapsed")
st.markdown(SHARED_CSS, unsafe_allow_html=True)

# -- Navbar ---------------------------------------------------------------------
st.markdown('<div class="nb"><div class="nb-brand"><span class="g">11</span><span class="r">%</span></div><div class="nb-links">', unsafe_allow_html=True)
_nav = st.columns([1,1,1,1,1,1,1])
with _nav[0]: st.page_link("app.py",                    label="Home")
with _nav[1]: st.page_link("pages/1_Backtest.py",       label="Backtest")
with _nav[2]: st.page_link("pages/2_Indicator_Test.py", label="Indicators")
with _nav[3]: st.page_link("pages/3_Replay.py",         label="Replay")
with _nav[4]: st.page_link("pages/4_Analysis.py",       label="Analysis")
with _nav[5]: st.page_link("pages/6_Earnings.py",       label="Earnings")
with _nav[6]: st.page_link("pages/5_Assistant.py",      label="Coach")
st.markdown('</div><div class="nb-tag">FREE * OPEN SOURCE</div></div>', unsafe_allow_html=True)

# -- API setup ------------------------------------------------------------------
try:    api_key = st.secrets["GEMINI_API_KEY"]
except: api_key = os.getenv("GEMINI_API_KEY", "")
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")
else:
    model = None

# -- Session state --------------------------------------------------------------
for k, v in [("messages", []), ("coach_profile", {}), ("coach_setup_done", False)]:
    if k not in st.session_state: st.session_state[k] = v

# -- Context from other pages ---------------------------------------------------
last_bt = st.session_state.get("last_backtest")
last_an = st.session_state.get("last_analysis")
ctx_parts = []
if last_bt:
    mm = last_bt["metrics"]
    ctx_parts.append(f"Backtest: {last_bt['ticker']} * {last_bt['strategy']} * Return {mm['total_return']:+.2f}% * Sharpe {mm['sharpe']} * Drawdown {mm['max_drawdown']:.2f}% * Win Rate {mm['win_rate']:.0f}%")
if last_an:
    ctx_parts.append(f"Analysis: {last_an['ticker']}")

# -- Page header ----------------------------------------------------------------
st.markdown("""
<div class="page-header">
    <div class="page-header-eyebrow">Powered by Gemini</div>
    <h1>AI Trading Coach</h1>
    <p>Overwhelmed by data? Just ask. Your coach explains anything in plain English — from what a Sharpe ratio means to why your strategy lost money.</p>
</div>
""", unsafe_allow_html=True)

if not api_key:
    st.markdown('<div class="warn-box">Add GEMINI_API_KEY to Streamlit Secrets to enable the AI coach.</div>', unsafe_allow_html=True)

# -- Profile setup (collapsible, not in the way) --------------------------------
with st.expander("?  Your profile - helps the coach tailor answers", expanded=not st.session_state.coach_setup_done):
    p1, p2, p3, p4 = st.columns([1,1,1,2])
    with p1: experience = st.selectbox("Experience", ["Beginner","Some knowledge","Intermediate","Advanced"], key="exp")
    with p2: style      = st.selectbox("Style", ["Not sure","Day trading","Swing trading","Long-term investing"], key="sty")
    with p3: risk       = st.selectbox("Risk", ["Low","Medium","High"], key="rsk")
    with p4: goals      = st.text_input("Goal (optional)", placeholder="e.g. Understand RSI, build a strategy", key="gls")
    if st.button("Save profile", key="save_profile"):
        st.session_state.coach_profile = {"experience": experience, "style": style, "risk": risk, "goals": goals}
        st.session_state.coach_setup_done = True
        st.rerun()

prof = st.session_state.coach_profile or {"experience": "Beginner", "style": "Not sure", "risk": "Medium", "goals": ""}

# -- Context pill ---------------------------------------------------------------
if ctx_parts:
    pills = " &nbsp;*&nbsp; ".join(ctx_parts)
    st.markdown(f'<div class="info-box" style="margin-bottom:1.5rem;font-size:0.75rem;">[bar] &nbsp;{pills}</div>', unsafe_allow_html=True)

# -- Quick-ask chips ------------------------------------------------------------
CHIPS = [
    ("Explain my results",   "Can you explain my most recent backtest results in plain English? What do the numbers mean?"),
    ("Best strategy for me", "Based on my profile, what strategy should I start with and why?"),
    ("What is the Sharpe ratio?", "What is the Sharpe ratio and what counts as a good number?"),
    ("Why did I lose to buy & hold?", "My strategy underperformed buy and hold. Does that mean it's bad?"),
    ("Explain RSI simply",   "Explain RSI like I've never traded before - what is it and how do I use it?"),
    ("SMA vs EMA",           "What's the difference between SMA and EMA and when should I use each?"),
    ("What is drawdown?",    "What is drawdown and max drawdown? How much drawdown is acceptable?"),
    ("How to improve my strategy", "What are the most effective ways to improve a backtesting strategy's results?"),
    ("What is alpha?",       "What is alpha? How do I know if my strategy is actually adding value?"),
    ("Explain MACD",         "Explain MACD in simple terms - what does it measure and how do I read it?"),
]

if not st.session_state.messages:
    st.markdown('<div style="margin-bottom:1rem;font-family:IBM Plex Mono,monospace;font-size:0.6rem;color:#3a4558;text-transform:uppercase;letter-spacing:0.15em;">Quick questions</div>', unsafe_allow_html=True)
    # Render chips as buttons in a flex grid
    row1 = st.columns(5)
    row2 = st.columns(5)
    for i, (label, prompt) in enumerate(CHIPS):
        col = row1[i] if i < 5 else row2[i-5]
        with col:
            if st.button(label, use_container_width=True, key=f"chip_{i}"):
                st.session_state.messages.append({"role": "user", "content": prompt})
                st.rerun()

# -- Build system prompt --------------------------------------------------------
SYS = f"""You are a friendly, knowledgeable trading coach on 11%, a free trading education platform.

ABOUT THE USER:
- Experience: {prof.get('experience','Beginner')}
- Style: {prof.get('style','Not sure')}
- Risk tolerance: {prof.get('risk','Medium')}
- Goals: {prof.get('goals','Not specified')}

CONTEXT FROM THE PLATFORM:
{chr(10).join(ctx_parts) if ctx_parts else 'No recent platform activity.'}

HOW TO RESPOND:
- Beginners: use plain English and real-world analogies. Never assume prior knowledge.
- Intermediate/Advanced: use correct terminology but stay concise.
- Structure answers with **Bold Headers** and short paragraphs. Never write a wall of text.
- Use bullet points (- item) for any list of 3 or more items.
- Always relate numbers to real-world meaning (e.g. "this means you'd have lost 25% before recovering").
- Be honest. If a strategy has problems, say so directly.
- Never recommend specific stocks. Focus on education.
- Keep responses focused - quality over length. A great answer is often 150-300 words."""

# -- Chat messages --------------------------------------------------------------
def render_ai_message(text):
    """Converts markdown-style AI response to clean HTML."""
    # Process bold
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong style="color:#e2e8f0;">\1</strong>', text)
    # Process bullet points
    lines = text.split('\n')
    out = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('- ') or stripped.startswith('? '):
            content = stripped[2:]
            # Bold within bullets too
            out.append(f'<div style="display:flex;gap:0.5rem;margin:0.25rem 0;"><span style="color:#00d68f;flex-shrink:0;margin-top:0.1rem;">-</span><span>{content}</span></div>')
        elif stripped.startswith('# '):
            out.append(f'<div style="font-family:IBM Plex Mono,monospace;font-size:0.65rem;color:#00d68f;text-transform:uppercase;letter-spacing:0.15em;margin:1rem 0 0.4rem 0;">{stripped[2:]}</div>')
        elif stripped == '':
            out.append('<div style="height:0.5rem;"></div>')
        else:
            out.append(f'<span>{line}</span><br>')
    return ''.join(out)

if st.session_state.messages:
    st.markdown('<div style="margin-bottom:0.5rem;"></div>', unsafe_allow_html=True)
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f'''<div class="chat-user">
                <div class="chat-lbl">You</div>
                {msg["content"]}
            </div>''', unsafe_allow_html=True)
        else:
            rendered = render_ai_message(msg["content"])
            st.markdown(f'''<div class="chat-ai">
                <div class="chat-lbl"><span class="dot"></span>11% Coach</div>
                <div style="margin-top:0.25rem;">{rendered}</div>
            </div>''', unsafe_allow_html=True)

    # Clear button inline, small
    if st.button("Clear conversation", key="clear_inline"):
        st.session_state.messages = []
        st.rerun()

# -- Empty state ----------------------------------------------------------------
elif not st.session_state.messages:
    st.markdown("""
    <div style="background:linear-gradient(135deg,#071a0f,#0a1a10);border:1px solid #00d68f22;border-radius:12px;padding:2.5rem;text-align:center;margin:1rem 0 1.5rem 0;">
        <div style="font-size:2rem;margin-bottom:0.8rem;">?</div>
        <div style="font-family:'IBM Plex Mono',monospace;font-size:0.72rem;color:#00d68f;text-transform:uppercase;letter-spacing:0.15em;margin-bottom:0.8rem;">Ready to help</div>
        <div style="color:#8892a4;font-size:0.9rem;line-height:1.7;max-width:480px;margin:0 auto;">
            Ask me anything - from what a Sharpe ratio means to why your strategy lost money.
            I can see your recent backtest results and will tailor my answers to your level.
        </div>
    </div>
    """, unsafe_allow_html=True)

# -- AI call --------------------------------------------------------------------
if model and st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    with st.spinner(""):
        try:
            history = [{"role": "user", "parts": [SYS + "\n\nConversation starts now."]}]
            for msg in st.session_state.messages:
                history.append({"role": "user" if msg["role"] == "user" else "model", "parts": [msg["content"]]})
            resp = model.generate_content(history)
            st.session_state.messages.append({"role": "assistant", "content": resp.text})
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")

# -- Chat input (always at bottom) ---------------------------------------------
user_input = st.chat_input("Ask anything about trading, strategies, or your results...")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.rerun()
