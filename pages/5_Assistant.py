import streamlit as st
import google.generativeai as genai
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.styles import SHARED_CSS

st.set_page_config(page_title="Assistant | 11%", page_icon="💬", layout="wide", initial_sidebar_state="collapsed")
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

USER PROFILE: Experience={prof.get("experience","Unknown")} | Style={prof.get("style","Unknown")} | Risk={prof.get("risk","Unknown")} | Goals={prof.get("goals","Not specified")}
CONTEXT: {chr(10).join(ctx) if ctx else "No recent activity."}

RESPONSE RULES:
- Match depth to the user experience level
- For complex answers: use **bold headings** and short paragraphs, not one wall of text
- Use bullet points for lists of 3+ items
- Never give direct buy/sell recommendations on specific stocks
- Add a one-line disclaimer when discussing specific investment decisions
- Be direct, honest, and concise"""

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
