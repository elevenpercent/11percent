import streamlit as st
import google.generativeai as genai
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.styles import SHARED_CSS

st.set_page_config(page_title="AI Assistant | 11%", layout="wide", initial_sidebar_state="collapsed")
st.markdown(SHARED_CSS, unsafe_allow_html=True)
st.markdown('<div class="nb"><div class="nb-brand"><span class="g">11</span><span class="r">%</span></div><div class="nb-links">', unsafe_allow_html=True)
_nav = st.columns([1,1,1,1,1,1])
with _nav[0]: st.page_link("app.py",                    label="Home")
with _nav[1]: st.page_link("pages/1_Backtest.py",       label="Backtest")
with _nav[2]: st.page_link("pages/2_Indicator_Test.py", label="Indicators")
with _nav[3]: st.page_link("pages/3_Replay.py",         label="Replay")
with _nav[4]: st.page_link("pages/4_Analysis.py",       label="Analysis")
with _nav[5]: st.page_link("pages/5_Assistant.py",      label="Assistant")
st.markdown('</div><div class="nb-tag">FREE · OPEN SOURCE</div></div>', unsafe_allow_html=True)

try:    api_key = st.secrets["GEMINI_API_KEY"]
except: api_key = os.getenv("GEMINI_API_KEY", "")
if api_key: genai.configure(api_key=api_key); model = genai.GenerativeModel("gemini-2.5-flash")
else: model = None

for k, v in [("messages",[]),("user_profile",{})]:
    if k not in st.session_state: st.session_state[k] = v

st.markdown('''<div class="page-header"><h1>AI Trading Coach</h1><p>Ask anything about trading, strategies, your backtest results, or concepts you don't understand. Your coach adapts to your experience level.</p></div>''', unsafe_allow_html=True)

if not api_key:
    st.markdown('<div class="warn-box">No Gemini API key found. Add GEMINI_API_KEY to Streamlit Secrets to enable the AI coach.</div>', unsafe_allow_html=True)

# ── Profile ───────────────────────────────────────────────────────────────────
st.markdown('<div class="price-divider">YOUR PROFILE</div>', unsafe_allow_html=True)
st.markdown('<div class="config-panel">', unsafe_allow_html=True)
pc1,pc2,pc3,pc4,pc5 = st.columns([2,2,2,3,1])
with pc1: experience = st.selectbox("Experience Level", ["Complete Beginner","Some Knowledge","Intermediate","Advanced"])
with pc2: style      = st.selectbox("Trading Style",    ["Not sure yet","Day Trading","Swing Trading (days–weeks)","Position Trading (weeks–months)","Long-term Investing (years)"])
with pc3: risk       = st.selectbox("Risk Tolerance",   ["Low — capital preservation first","Medium — balanced growth","High — aggressive growth"])
with pc4: goals      = st.text_input("Your goal", placeholder="e.g. Learn to trade, grow $5k over 2 years, understand RSI")
with pc5:
    st.markdown('<div style="height:1.9rem"></div>', unsafe_allow_html=True)
    if st.button("Clear Chat", use_container_width=True):
        st.session_state.messages = []; st.rerun()
st.markdown('</div>', unsafe_allow_html=True)
st.session_state.user_profile = {"experience":experience,"style":style,"risk":risk,"goals":goals}

# Context from other pages
last_bt = st.session_state.get("last_backtest")
last_an = st.session_state.get("last_analysis")
ctx = []
if last_bt:
    mm = last_bt["metrics"]
    ctx.append(f"Last backtest: {last_bt['ticker']} · {last_bt['strategy']} · Return {mm['total_return']:+.2f}% · BH {mm['bh_return']:+.2f}% · Win Rate {mm['win_rate']:.0f}% · Sharpe {mm['sharpe']} · Drawdown {mm['max_drawdown']:.2f}%")
if last_an:
    ctx.append(f"Last stock analysis: {last_an['ticker']}")
if ctx:
    st.markdown(f'<div class="info-box" style="margin-bottom:1rem;">📊 Context loaded: {" &nbsp;·&nbsp; ".join(ctx)}</div>', unsafe_allow_html=True)

# ── Quick question buttons ────────────────────────────────────────────────────
st.markdown('<div class="price-divider">QUICK QUESTIONS</div>', unsafe_allow_html=True)
quick_questions = [
    ("Explain my results",       "Can you explain my most recent backtest results in simple terms? What do the numbers mean and is this strategy worth using?"),
    ("Best strategy for me",     "Based on my trading profile, what strategy would you recommend I start with and why?"),
    ("What is alpha?",           "What is alpha in backtesting? How do I know if my strategy is actually adding value?"),
    ("Sharpe ratio explained",   "Can you explain the Sharpe ratio? What counts as a good number and why does it matter?"),
    ("Why did my strategy lose?","My backtest underperformed buy and hold. Does that mean the strategy is useless?"),
    ("SMA vs EMA",               "What is the difference between SMA and EMA? When should I use each one?"),
    ("RSI explained",            "Explain RSI to me like I've never traded before. How does it work and how do I use it?"),
    ("How to improve results",   "What are the most common ways to improve a backtesting strategy's performance?"),
]
rows = [quick_questions[:4], quick_questions[4:]]
for row in rows:
    cols = st.columns(4)
    for col, (label, prompt) in zip(cols, row):
        with col:
            if st.button(label, use_container_width=True, key=f"q_{label[:10]}"):
                st.session_state.messages.append({"role":"user","content":prompt})
                st.rerun()

# ── Build system prompt ───────────────────────────────────────────────────────
prof = st.session_state.user_profile
SYS = f"""You are a friendly, expert trading coach on 11%, a free trading education platform for learners.

USER PROFILE:
- Experience: {prof.get("experience","Unknown")}
- Style: {prof.get("style","Unknown")}
- Risk Tolerance: {prof.get("risk","Unknown")}
- Goals: {prof.get("goals","Not specified")}

CONTEXT FROM THE PLATFORM:
{chr(10).join(ctx) if ctx else "No recent activity on the platform."}

HOW TO RESPOND:
- Match your language complexity to the user's experience level. Beginners need plain English with analogies. Advanced users can handle technical terms.
- For any question with more than one part, use **bold headings** to separate sections. Never write one wall of text.
- Use bullet points for any list of 3 or more items.
- Be direct and honest. If a strategy has problems, say so clearly rather than being vague.
- When explaining backtest metrics, always relate them to real-world meaning (e.g. "this means you would have lost 23% before recovering").
- Never recommend specific stocks to buy or sell. Focus on education, strategy, and interpretation.
- Add a short disclaimer only when discussing specific investment decisions.
- Keep responses focused and concise — quality over length."""

# ── Chat display ──────────────────────────────────────────────────────────────
st.markdown('<div class="price-divider">CHAT</div>', unsafe_allow_html=True)

if not st.session_state.messages:
    st.markdown(f'''<div style="background:#0d1117;border:1px solid #1c2333;border-radius:8px;padding:1.5rem;text-align:center;margin:1rem 0;">
        <div style="font-family:'IBM Plex Mono',monospace;font-size:0.65rem;color:#00d68f;text-transform:uppercase;letter-spacing:0.15em;margin-bottom:0.6rem;">11% AI Coach</div>
        <div style="font-size:0.9rem;color:#8892a4;line-height:1.7;">Ready to help. Ask me about trading strategies, how to read your backtest results, what indicators mean, or anything else you want to understand.<br><br>I know about your recent activity on the platform and will use that context in my answers.</div>
    </div>''', unsafe_allow_html=True)

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="chat-user"><div class="chat-lbl">You</div>{msg["content"]}</div>', unsafe_allow_html=True)
    else:
        formatted = msg["content"].replace("\n\n","<br><br>").replace("\n","<br>")
        # Bold markdown
        import re
        formatted = re.sub(r'\*\*(.+?)\*\*', r'<strong style="color:#cdd5e0;">\1</strong>', formatted)
        formatted = re.sub(r'^• ', '&nbsp;&nbsp;• ', formatted, flags=re.MULTILINE)
        st.markdown(f'<div class="chat-ai"><div class="chat-lbl" style="color:#00d68f;">11% Coach</div><div style="font-size:0.85rem;line-height:1.75;color:#8892a4;">{formatted}</div></div>', unsafe_allow_html=True)

# ── Run AI ────────────────────────────────────────────────────────────────────
if model and st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    with st.spinner("Thinking..."):
        try:
            history = [{"role":"user","parts":[SYS + "\n\nConversation begins now."]}]
            for msg in st.session_state.messages:
                role = "user" if msg["role"] == "user" else "model"
                history.append({"role": role, "parts": [msg["content"]]})
            resp = model.generate_content(history)
            st.session_state.messages.append({"role":"assistant","content":resp.text})
            st.rerun()
        except Exception as e:
            st.error(f"Gemini error: {e}")

user_input = st.chat_input("Ask your trading coach anything...")
if user_input:
    st.session_state.messages.append({"role":"user","content":user_input})
    st.rerun()

# ── Topic guide ───────────────────────────────────────────────────────────────
if not st.session_state.messages:
    st.markdown('<div class="price-divider">WHAT YOU CAN ASK</div>', unsafe_allow_html=True)
    tg1, tg2, tg3, tg4 = st.columns(4)
    for col, title, topics in [
        (tg1, "Understanding Results",  ["What does my Sharpe ratio mean?","Why did my strategy underperform buy & hold?","Is a 60% win rate good?","What is alpha and how is it calculated?","What causes high drawdown?"]),
        (tg2, "Learning Strategies",    ["How does the RSI strategy work?","When does SMA Crossover fail?","What is mean reversion?","Explain momentum trading","What is the best strategy for beginners?"]),
        (tg3, "Indicator Concepts",     ["SMA vs EMA — what's the difference?","How do Bollinger Bands signal a squeeze?","What is MACD divergence?","Explain SuperTrend simply","How do I combine indicators?"]),
        (tg4, "General Trading",        ["What is position sizing?","How do professionals manage risk?","What is the difference between backtesting and paper trading?","Should I day trade or swing trade?","What is a drawdown and why does it matter?"]),
    ]:
        col.markdown(f'<div style="font-family:IBM Plex Mono,monospace;font-size:0.6rem;color:#3a4558;text-transform:uppercase;letter-spacing:0.15em;margin-bottom:0.8rem;">{title}</div>', unsafe_allow_html=True)
        for topic in topics:
            col.markdown(f'<div style="padding:0.4rem 0;border-bottom:1px solid #1c2333;font-size:0.77rem;color:#3a4558;"><span style="color:#1c2333;margin-right:0.4rem;">—</span>{topic}</div>', unsafe_allow_html=True)
