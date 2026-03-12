import streamlit as st
import sys, os
import re

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.styles import SHARED_CSS
from utils.nav import navbar

st.set_page_config(page_title="AI Coach | 11%", layout="wide", initial_sidebar_state="collapsed")
st.markdown(SHARED_CSS, unsafe_allow_html=True)
navbar()

st.markdown("""
<style>
.coach-msg-wrap { margin-bottom:0.6rem; }
.coach-user {
    display:flex; justify-content:flex-end; margin-bottom:0.5rem;
}
.coach-user-bubble {
    background:rgba(77,166,255,0.1); border:1px solid rgba(77,166,255,0.2);
    border-radius:16px 16px 2px 16px; padding:0.75rem 1rem;
    max-width:75%; font-size:0.86rem; color:#eef2f7; line-height:1.55;
}
.coach-ai-wrap { display:flex; gap:0.75rem; align-items:flex-start; margin-bottom:0.5rem; }
.coach-ai-avatar {
    width:32px; height:32px; border-radius:8px; flex-shrink:0;
    background:linear-gradient(135deg,#007a2c,#00e676);
    display:flex; align-items:center; justify-content:center;
    font-family:'Bebas Neue',sans-serif; font-size:0.75rem; color:#000;
    margin-top:2px;
}
.coach-ai-bubble {
    background:#0c1018; border:1px solid #1a2235;
    border-radius:2px 16px 16px 16px; padding:1rem 1.2rem;
    max-width:85%; flex:1;
}
.coach-ai-bubble .ca-section {
    margin-bottom:0.8rem;
}
.coach-ai-bubble .ca-section:last-child { margin-bottom:0; }
.coach-ai-bubble .ca-hdr {
    font-family:'IBM Plex Mono',monospace; font-size:0.58rem;
    text-transform:uppercase; letter-spacing:0.18em;
    margin-bottom:0.35rem; display:flex; align-items:center; gap:0.4rem;
}
.coach-ai-bubble p { margin:0 0 0.4rem; font-size:0.85rem; color:#8896ab; line-height:1.65; }
.coach-ai-bubble p:last-child { margin-bottom:0; }
.coach-ai-bubble ul { margin:0.2rem 0; padding-left:1.2rem; }
.coach-ai-bubble li { font-size:0.84rem; color:#8896ab; margin-bottom:0.2rem; line-height:1.55; }
.coach-ai-bubble strong { color:#eef2f7; }
.coach-ai-bubble code {
    background:rgba(0,0,0,0.4); border:1px solid #1a2235;
    border-radius:3px; padding:1px 5px;
    font-family:'IBM Plex Mono',monospace; font-size:0.78rem; color:#4da6ff;
}
.coach-ai-bubble .ca-divider {
    border:none; border-top:1px solid #1a2235; margin:0.6rem 0;
}
.chip-row { display:flex; flex-wrap:wrap; gap:0.4rem; margin-bottom:0.8rem; }
.chip {
    background:#0c1018; border:1px solid #1a2235;
    border-radius:20px; padding:0.3rem 0.8rem;
    font-size:0.7rem; font-family:'IBM Plex Mono',monospace;
    color:#3a4a5e; cursor:pointer; transition:all 0.12s;
    white-space:nowrap;
}
.chip:hover { border-color:#00e676; color:#00e676; background:rgba(0,230,118,0.04); }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="page-header">
    <div class="page-header-eyebrow">Gemini-Powered</div>
    <h1>AI Trading Coach</h1>
    <p>Your personal trading mentor. Ask about strategies, chart patterns, risk management, or get feedback on specific setups.</p>
</div>
""", unsafe_allow_html=True)

# ── Profile setup
with st.expander("Your Profile", expanded="coach_profile" not in st.session_state):
    p1, p2, p3, p4 = st.columns(4)
    with p1: exp   = st.selectbox("Experience", ["Beginner","Intermediate","Advanced","Professional"], key="cp_exp")
    with p2: style = st.selectbox("Style",       ["Day Trading","Swing Trading","Position Trading","Investing"], key="cp_style")
    with p3: risk  = st.selectbox("Risk Appetite",["Conservative","Moderate","Aggressive"], key="cp_risk")
    with p4: goals = st.text_input("Goals", placeholder="e.g. Learn to read charts", key="cp_goals")
    if st.button("Save Profile", key="cp_save"):
        st.session_state["coach_profile"] = {
            "experience": exp, "style": style, "risk": risk, "goals": goals
        }
        st.success("Profile saved!")

profile = st.session_state.get("coach_profile", {})

# ── Session state
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# ── Context pills from other pages
ctx_pills = []
if "last_backtest" in st.session_state:
    bt = st.session_state["last_backtest"]
    ctx_pills.append(f"📊 Last backtest: {bt.get('ticker','?')} / {bt.get('strategy','?')} — {bt['metrics'].get('total_return',0)*100:+.1f}%")
if "last_analysis" in st.session_state:
    an = st.session_state["last_analysis"]
    ctx_pills.append(f"🔍 Last analysis: {an.get('ticker','?')} ({an.get('focus','')})")

if ctx_pills:
    st.markdown(
        '<div style="display:flex;gap:0.5rem;flex-wrap:wrap;margin-bottom:0.8rem;">' +
        "".join(f'<div style="background:rgba(0,230,118,0.06);border:1px solid rgba(0,230,118,0.15);border-radius:20px;padding:0.25rem 0.75rem;font-size:0.68rem;font-family:IBM Plex Mono,monospace;color:#00e676;">{p}</div>' for p in ctx_pills) +
        '</div>',
        unsafe_allow_html=True
    )

# ── Quick chips
CHIPS = [
    "Explain RSI divergence", "What is a bull flag?", "How do I size positions?",
    "Review my last backtest", "Best indicators for swing trading",
    "What is the risk/reward ratio?", "Explain support and resistance",
    "How do I manage drawdowns?",
]
st.markdown('<div class="chip-row">', unsafe_allow_html=True)
clicked_chip = None
chip_cols = st.columns(len(CHIPS))
for col, chip in zip(chip_cols, CHIPS):
    with col:
        if st.button(chip, key=f"chip_{chip}", use_container_width=True):
            clicked_chip = chip
st.markdown('</div>', unsafe_allow_html=True)

# ── Chat history
chat_container = st.container()

with chat_container:
    for msg in st.session_state["messages"]:
        if msg["role"] == "user":
            st.markdown(
                f'<div class="coach-user">'
                f'<div class="coach-user-bubble">{msg["content"]}</div>'
                f'</div>',
                unsafe_allow_html=True
            )
        else:
            formatted = _format_ai_response(msg["content"])
            st.markdown(
                f'<div class="coach-ai-wrap">'
                f'<div class="coach-ai-avatar">AI</div>'
                f'<div class="coach-ai-bubble">{formatted}</div>'
                f'</div>',
                unsafe_allow_html=True
            )

# ── Input
inp_col, btn_col = st.columns([6, 1])
with inp_col:
    user_input = st.text_input(
        "Ask your coach…", placeholder="e.g. What does a head and shoulders pattern tell me?",
        key="coach_input", label_visibility="collapsed"
    )
with btn_col:
    send = st.button("Send", type="primary", use_container_width=True, key="coach_send")

# ── Process message
query = clicked_chip or (user_input if send and user_input.strip() else None)

if query:
    st.session_state["messages"].append({"role": "user", "content": query})

    # Build system prompt
    profile_str = ""
    if profile:
        profile_str = f"""
Trader profile:
- Experience: {profile.get('experience','Unknown')}
- Style: {profile.get('style','Unknown')}
- Risk: {profile.get('risk','Unknown')}
- Goals: {profile.get('goals','')}
Tailor your response to their level and style.
"""

    context_str = ""
    if "last_backtest" in st.session_state:
        bt = st.session_state["last_backtest"]
        m  = bt.get("metrics", {})
        context_str += f"""
Recent backtest context:
- Ticker: {bt.get('ticker','')}, Strategy: {bt.get('strategy','')}
- Return: {m.get('total_return',0)*100:+.1f}%, Alpha: {m.get('alpha',0)*100:+.1f}%
- Win Rate: {m.get('win_rate',0)*100:.1f}%, Drawdown: {m.get('max_drawdown',0)*100:.1f}%
- Sharpe: {m.get('sharpe',0):.2f}, Trades: {m.get('num_trades',0)}
"""

    system_prompt = f"""You are an expert trading coach and educator on the 11% platform.
{profile_str}
{context_str}

CRITICAL FORMATTING RULES:
- Always use clear section headers with ## (e.g., ## 📖 WHAT IT IS)
- Use bullet points for lists
- Use **bold** for key terms and numbers
- Keep responses focused and well-structured
- Maximum 4-5 sections per response
- Each section should be concise — 2-4 sentences or 3-5 bullets
- End with a ## 💡 KEY TAKEAWAY section — one actionable insight

Do not write walls of text. Structure everything clearly.
"""

    history = []
    for m in st.session_state["messages"][:-1]:
        history.append({"role": m["role"], "parts": [m["content"]]})

    try:
        import google.generativeai as genai
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=system_prompt
        )
        chat = model.start_chat(history=history)

        with st.spinner("Coach is thinking…"):
            resp = chat.send_message(query)
            reply = resp.text

        st.session_state["messages"].append({"role": "assistant", "content": reply})
        st.rerun()

    except Exception as e:
        st.error(f"AI error: {e}")

# ── Clear button
if st.session_state["messages"]:
    if st.button("Clear conversation", key="coach_clear"):
        st.session_state["messages"] = []
        st.rerun()

# ── Format AI response into structured HTML
def _format_ai_response(text):
    """Convert ## sectioned markdown into clean card-style HTML."""
    # Split by ## headers
    sections = re.split(r'\n##\s+', '\n' + text.strip())
    sections = [s for s in sections if s.strip()]

    if len(sections) <= 1 and '##' not in text:
        # No structure — render as simple formatted paragraphs
        body = _inline_md(text)
        return f'<div class="ca-section"><div style="font-size:0.85rem;color:#8896ab;line-height:1.7;">{body}</div></div>'

    ACCENT_MAP = {
        "what": "#4da6ff", "how": "#4da6ff", "explain": "#4da6ff",
        "bull": "#00e676", "why": "#00e676", "when": "#00e676", "positive": "#00e676",
        "bear": "#ff3d57", "risk": "#ff3d57", "warn": "#ff3d57", "avoid": "#ff3d57",
        "key": "#ffd166", "takeaway": "#ffd166", "bottom": "#ffd166", "example": "#ffd166",
        "technical": "#b388ff", "setup": "#b388ff", "pattern": "#b388ff",
    }

    output = []
    for sec in sections:
        lines  = sec.strip().split('\n', 1)
        header = lines[0].strip().lstrip('#').strip()
        body   = lines[1].strip() if len(lines) > 1 else ""

        # Pick accent color from header keywords
        accent = "#8896ab"
        for kw, col in ACCENT_MAP.items():
            if kw in header.lower():
                accent = col
                break

        html_body = _section_body_html(body)

        output.append(
            f'<div class="ca-section">'
            f'<div class="ca-hdr" style="color:{accent};">'
            f'<span style="display:inline-block;width:3px;height:12px;background:{accent};border-radius:2px;"></span>'
            f'{header}</div>'
            f'{html_body}'
            f'</div>'
            f'<hr class="ca-divider">'
        )

    result = "".join(output)
    # Remove trailing divider
    result = result.rstrip('<hr class="ca-divider">')
    return result


def _section_body_html(text):
    """Convert section body (bullets, paragraphs) to HTML."""
    lines = text.split('\n')
    out = []
    in_list = False

    for line in lines:
        line = line.strip()
        if not line:
            if in_list:
                out.append('</ul>')
                in_list = False
            continue

        line = _inline_md(line)

        if line.startswith(('- ', '• ', '* ', '+ ')):
            if not in_list:
                out.append('<ul style="margin:0.2rem 0 0.4rem;padding-left:1.1rem;">')
                in_list = True
            out.append(f'<li>{line[2:].strip()}</li>')
        elif re.match(r'^\d+\.\s', line):
            if not in_list:
                out.append('<ol style="margin:0.2rem 0 0.4rem;padding-left:1.1rem;">')
                in_list = True
            out.append(f'<li>{re.sub(r"^\d+\.\s", "", line)}</li>')
        else:
            if in_list:
                out.append('</ul>' if not line.startswith('<ol') else '</ol>')
                in_list = False
            out.append(f'<p style="margin:0 0 0.35rem;">{line}</p>')

    if in_list:
        out.append('</ul>')
    return ''.join(out)


def _inline_md(text):
    """Convert inline markdown (bold, code, italic) to HTML."""
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*',     r'<em style="color:#eef2f7;">\1</em>', text)
    text = re.sub(r'`(.+?)`',       r'<code>\1</code>', text)
    return text
