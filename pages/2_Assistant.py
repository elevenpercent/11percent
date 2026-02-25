import streamlit as st
import google.generativeai as genai
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

st.set_page_config(page_title="AI Assistant | BacktestFree", page_icon="🤖", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;600&display=swap');
    :root { --accent:#0066ff; --bg:#0d0f14; --surface:#161920; --border:#2a2d38; --muted:#6b7280; }
    html,body,[data-testid="stAppViewContainer"]{background:var(--bg)!important;color:#e8eaf0!important;font-family:'DM Sans',sans-serif;}
    [data-testid="stSidebar"]{background:var(--surface)!important;border-right:1px solid var(--border);}
    h1,h2,h3{font-family:'Space Mono',monospace;}
    .stButton>button{background:var(--accent);color:#fff;border:none;border-radius:4px;font-family:'Space Mono',monospace;font-weight:700;padding:.5rem 1.5rem;}
    .chat-user{background:#1e2235;border-radius:12px 12px 4px 12px;padding:1rem;margin:0.5rem 0;border:1px solid var(--border);}
    .chat-ai{background:#0d1a2e;border-radius:12px 12px 12px 4px;padding:1rem;margin:0.5rem 0;border:1px solid #0066ff44;}
    .chat-label{font-size:.7rem;text-transform:uppercase;letter-spacing:.1em;color:var(--muted);margin-bottom:.3rem;}
</style>
""", unsafe_allow_html=True)

st.markdown("# 🤖 AI Trading Assistant")
st.caption("Powered by Google Gemini — Ask anything about trading, strategies, or your backtest results.")

# ── API Key setup ─────────────────────────────────────────────────────────────
# On Streamlit Community Cloud, set GEMINI_API_KEY in your app's Secrets settings
# For local development, put it in your .env file
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    api_key = os.getenv("GEMINI_API_KEY", "")

if not api_key:
    st.error("⚠️ No Gemini API key found. Add GEMINI_API_KEY to your Streamlit secrets or .env file.")
    st.markdown("""
    **How to get a free Gemini API key:**
    1. Go to [Google AI Studio](https://aistudio.google.com)
    2. Click **Get API Key**
    3. Copy the key
    4. In Streamlit Cloud → your app → **Settings** → **Secrets** → add:
    ```
    GEMINI_API_KEY = "your-key-here"
    ```
    """)
    st.stop()

# Configure Gemini
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")  # Free tier model

# ── System prompt for the assistant ──────────────────────────────────────────
SYSTEM_PROMPT = """You are a helpful trading education assistant on a free backtesting platform called BacktestFree. 

Your role is to:
- Explain trading strategies in simple, beginner-friendly language
- Help users understand their backtest results (total return, drawdown, win rate, etc.)
- Suggest strategies based on the user's goals
- Explain trading concepts clearly with real examples
- Help users write custom strategy code in Python

Important rules:
- NEVER give specific financial advice or tell users to buy/sell specific stocks
- Always remind users that past performance doesn't guarantee future results
- Keep explanations beginner-friendly unless the user seems advanced
- Be encouraging and educational, not intimidating
- When explaining code, always add clear comments

You have access to the user's most recent backtest results if they share them."""

# ── Initialize chat history ───────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# ── Show last backtest context if available ───────────────────────────────────
last_backtest = st.session_state.get("last_backtest")

if last_backtest:
    m = last_backtest["metrics"]
    st.success(f"📊 I can see your last backtest: **{last_backtest['ticker']}** with **{last_backtest['strategy']}** — "
               f"Return: `{m['total_return']:+.2f}%` | Drawdown: `{m['max_drawdown']:.2f}%` | "
               f"Win Rate: `{m['win_rate']:.0f}%`")

    if st.button("🗣️ Ask AI to explain my results"):
        context = f"""The user just ran a backtest with these results:
- Ticker: {last_backtest['ticker']}
- Strategy: {last_backtest['strategy']}
- Parameters: {last_backtest.get('params', {})}
- Total Return: {m['total_return']:+.2f}%
- Buy & Hold Return: {m['bh_return']:+.2f}%
- Max Drawdown: {m['max_drawdown']:.2f}%
- Final Portfolio Value: ${m['final_value']:,.2f}
- Number of Trades: {m['num_trades']}
- Win Rate: {m['win_rate']:.0f}%

Please explain these results in simple terms. Tell them what went well, what the numbers mean, and suggest ways to potentially improve."""
        st.session_state.messages.append({"role": "user", "content": context})

# ── Quick suggestion buttons ──────────────────────────────────────────────────
st.markdown("**Quick questions:**")
qcol1, qcol2, qcol3 = st.columns(3)
with qcol1:
    if st.button("What is the SMA crossover strategy?"):
        st.session_state.messages.append({"role": "user", "content": "What is the SMA crossover strategy and how does it work?"})
with qcol2:
    if st.button("What does max drawdown mean?"):
        st.session_state.messages.append({"role": "user", "content": "What does max drawdown mean and why does it matter?"})
with qcol3:
    if st.button("What strategy should I start with?"):
        st.session_state.messages.append({"role": "user", "content": "I'm a beginner. What trading strategy should I start with and why?"})

st.markdown("---")

# ── Display chat history ──────────────────────────────────────────────────────
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"""
        <div class="chat-user">
            <div class="chat-label">You</div>
            {msg['content']}
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="chat-ai">
            <div class="chat-label" style="color:#0066ff;">🤖 Assistant</div>
            {msg['content']}
        </div>""", unsafe_allow_html=True)

# ── Generate AI response if the last message is from the user ─────────────────
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    with st.spinner("Thinking..."):
        try:
            # Build full conversation for Gemini
            conversation = [{"role": "user", "parts": [SYSTEM_PROMPT + "\n\nNow begin the conversation."]}]
            
            for msg in st.session_state.messages:
                role = "user" if msg["role"] == "user" else "model"
                conversation.append({"role": role, "parts": [msg["content"]]})

            response = model.generate_content(conversation)
            reply = response.text

            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.rerun()

        except Exception as e:
            st.error(f"Error connecting to Gemini: {e}")

# ── Chat input ────────────────────────────────────────────────────────────────
user_input = st.chat_input("Ask me anything about trading or your results...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.rerun()

# ── Clear chat button ─────────────────────────────────────────────────────────
if st.session_state.messages:
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()
