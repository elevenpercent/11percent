import streamlit as st
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(__file__)))
from utils.session_persist import restore_session
import sys, os
import re

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.styles import SHARED_CSS, inject_bg
from utils.nav import navbar

st.set_page_config(page_title="AI Coach | 11%", layout="wide", initial_sidebar_state="collapsed")
restore_session()
st.markdown(SHARED_CSS, unsafe_allow_html=True)
navbar()

# ── Same-tab nav hook ─────────────────────────────────────────────────────────
import streamlit.components.v1 as _nav_cv1
_nav_cv1.html("""<script>
(function(){
  window.parent.document.addEventListener('click',function(e){
    var a=e.target.closest('a[href]');
    if(!a)return;
    var href=a.getAttribute('href');
    if(!href||href.startsWith('http')||href.startsWith('mailto')||href.startsWith('#'))return;
    e.preventDefault();e.stopPropagation();
    window.top.location.href=href;
  },true);
})();
</script>""", height=0)

inject_bg()

st.markdown("""
<style>
.coach-user-wrap { display:flex; justify-content:flex-end; margin-bottom:0.6rem; }
.coach-user-bubble {
    background:rgba(77,166,255,0.1); border:1px solid rgba(77,166,255,0.2);
    border-radius:16px 16px 2px 16px; padding:0.75rem 1rem;
    max-width:75%; font-size:0.86rem; color:#eef2f7; line-height:1.55;
}
.coach-ai-wrap { display:flex; gap:0.75rem; align-items:flex-start; margin-bottom:0.6rem; }
.coach-avatar {
    width:32px; height:32px; border-radius:8px; flex-shrink:0;
    background:linear-gradient(135deg,#007a2c,#00e676);
    display:flex; align-items:center; justify-content:center;
    font-family:'Bebas Neue',sans-serif; font-size:0.75rem; color:#000;
    margin-top:2px; letter-spacing:0.05em;
}
.coach-ai-bubble {
    background:#0c1018; border:1px solid #1a2235;
    border-radius:2px 16px 16px 16px; padding:1rem 1.2rem;
    max-width:88%; flex:1;
    font-size:0.84rem; color:#8896ab; line-height:1.65;
}
.coach-ai-bubble .sec-hdr {
    font-family:'IBM Plex Mono',monospace; font-size:0.58rem;
    text-transform:uppercase; letter-spacing:0.18em;
    margin:0.7rem 0 0.3rem; padding-bottom:0.3rem;
    border-bottom:1px solid #1a2235;
    display:flex; align-items:center; gap:0.4rem;
}
.coach-ai-bubble .sec-hdr:first-child { margin-top:0; }
.coach-ai-bubble p   { margin:0 0 0.4rem; }
.coach-ai-bubble p:last-child { margin:0; }
.coach-ai-bubble ul  { margin:0.2rem 0 0.5rem; padding-left:1.2rem; }
.coach-ai-bubble li  { margin-bottom:0.25rem; }
.coach-ai-bubble strong { color:#eef2f7; }
.coach-ai-bubble em    { color:#eef2f7; font-style:normal; }
.coach-ai-bubble code  {
    background:rgba(0,0,0,0.4); border:1px solid #1a2235;
    border-radius:3px; padding:1px 5px;
    font-family:'IBM Plex Mono',monospace; font-size:0.78rem; color:#4da6ff;
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# Formatting helpers — DEFINED FIRST
# ══════════════════════════════════════════════════════════

def _inline_md(text):
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*',     r'<em>\1</em>', text)
    text = re.sub(r'`(.+?)`',       r'<code>\1</code>', text)
    return text

def _body_html(text):
    lines  = text.split('\n')
    out    = []
    in_ul  = False
    in_ol  = False
    for line in lines:
        line = line.strip()
        if not line:
            if in_ul: out.append('</ul>'); in_ul = False
            if in_ol: out.append('</ol>'); in_ol = False
            continue
        line = _inline_md(line)
        if re.match(r'^[-•*+]\s', line):
            if in_ol: out.append('</ol>'); in_ol = False
            if not in_ul: out.append('<ul style="margin:0.2rem 0;padding-left:1.2rem;">'); in_ul = True
            out.append(f'<li>{line[2:].strip()}</li>')
        elif re.match(r'^\d+\.\s', line):
            if in_ul: out.append('</ul>'); in_ul = False
            if not in_ol: out.append('<ol style="margin:0.2rem 0;padding-left:1.2rem;">'); in_ol = True
            out.append(f'<li>{re.sub(r"^\d+\.\s","",line)}</li>')
        else:
            if in_ul: out.append('</ul>'); in_ul = False
            if in_ol: out.append('</ol>'); in_ol = False
            out.append(f'<p style="margin:0 0 0.35rem;">{line}</p>')
    if in_ul: out.append('</ul>')
    if in_ol: out.append('</ol>')
    return ''.join(out)

def format_ai_response(text):
    """Parse ## sections into color-accented cards. Falls back to plain HTML if no structure."""
    ACCENT_MAP = {
        "what": "#4da6ff", "how": "#4da6ff", "explain": "#4da6ff", "definition": "#4da6ff",
        "bull": "#00e676", "why": "#00e676", "setup": "#00e676", "entry": "#00e676",
        "risk": "#ff3d57", "bear": "#ff3d57", "avoid": "#ff3d57", "warn": "#ff3d57",
        "key": "#ffd166", "takeaway": "#ffd166", "summary": "#ffd166", "bottom": "#ffd166",
        "technical": "#b388ff", "indicator": "#b388ff", "pattern": "#b388ff",
        "example": "#ff9f43", "practice": "#ff9f43",
    }

    # Check for ## section structure
    if '##' not in text:
        return _body_html(text)

    sections = re.split(r'\n##\s+', '\n' + text.strip())
    sections = [s for s in sections if s.strip()]

    if len(sections) <= 1:
        return _body_html(text)

    parts = []
    for i, sec in enumerate(sections):
        lines  = sec.strip().split('\n', 1)
        header = lines[0].strip().lstrip('#').strip()
        body   = lines[1].strip() if len(lines) > 1 else ""

        accent = "#8896ab"
        for kw, col in ACCENT_MAP.items():
            if kw in header.lower():
                accent = col
                break

        divider = '<hr style="border:none;border-top:1px solid #1a2235;margin:0.6rem 0;">' if i > 0 else ''
        parts.append(
            f'{divider}'
            f'<div class="sec-hdr" style="color:{accent};">'
            f'<span style="display:inline-block;width:3px;height:11px;background:{accent};border-radius:2px;"></span>'
            f'{header}</div>'
            + _body_html(body)
        )

    return ''.join(parts)


# ══════════════════════════════════════════════════════════
# Page
# ══════════════════════════════════════════════════════════

st.markdown("""
<div class="page-header">
    <div class="page-header-eyebrow">Gemini-Powered</div>
    <h1>AI Trading Coach</h1>
    <p>Your personal trading mentor. Ask about strategies, chart patterns, risk management, or get feedback on specific setups.</p>
</div>
""", unsafe_allow_html=True)

# ── Profile
with st.expander("Your Profile", expanded="coach_profile" not in st.session_state):
    p1, p2, p3, p4 = st.columns(4)
    with p1: exp   = st.selectbox("Experience",    ["Beginner","Intermediate","Advanced","Professional"], key="cp_exp")
    with p2: style = st.selectbox("Style",          ["Day Trading","Swing Trading","Position Trading","Investing"], key="cp_style")
    with p3: risk  = st.selectbox("Risk Appetite",  ["Conservative","Moderate","Aggressive"], key="cp_risk")
    with p4: goals = st.text_input("Goals",          placeholder="e.g. Learn to read charts", key="cp_goals")
    if st.button("Save Profile", key="cp_save"):
        st.session_state["coach_profile"] = {"experience":exp,"style":style,"risk":risk,"goals":goals}
        st.success("Profile saved!")

profile = st.session_state.get("coach_profile", {})

# ── Session init
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# ── Context pills
pills = []
if "last_backtest" in st.session_state:
    bt = st.session_state["last_backtest"]
    pills.append(f"📊 Backtest: {bt.get('ticker','?')} / {bt.get('strategy','?')} — {bt['metrics'].get('total_return',0)*100:+.1f}%")
if "last_analysis" in st.session_state:
    an = st.session_state["last_analysis"]
    pills.append(f"🔍 Analysis: {an.get('ticker','?')} ({an.get('focus','')})")

if pills:
    st.markdown(
        '<div style="display:flex;gap:0.5rem;flex-wrap:wrap;margin-bottom:1rem;">' +
        "".join(f'<span style="background:rgba(0,230,118,0.06);border:1px solid rgba(0,230,118,0.15);border-radius:20px;padding:0.25rem 0.8rem;font-size:0.68rem;font-family:IBM Plex Mono,monospace;color:#00e676;">{p}</span>' for p in pills) +
        '</div>',
        unsafe_allow_html=True
    )

# ── Quick chips
CHIPS = [
    "Explain RSI divergence", "What is a bull flag?", "How do I size positions?",
    "Review my last backtest", "Best indicators for swing trading",
    "What is risk/reward ratio?", "Explain support & resistance", "How to manage drawdowns?",
]
chip_cols = st.columns(len(CHIPS))
clicked_chip = None
for col, chip in zip(chip_cols, CHIPS):
    with col:
        if st.button(chip, key=f"chip_{chip[:20]}", use_container_width=True):
            clicked_chip = chip

st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)

# ── Chat history display
for msg in st.session_state["messages"]:
    if msg["role"] == "user":
        st.markdown(
            f'<div class="coach-user-wrap">'
            f'<div class="coach-user-bubble">{msg["content"]}</div>'
            f'</div>',
            unsafe_allow_html=True
        )
    else:
        formatted = format_ai_response(msg["content"])
        st.markdown(
            f'<div class="coach-ai-wrap">'
            f'<div class="coach-avatar">AI</div>'
            f'<div class="coach-ai-bubble">{formatted}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

# ── Input row
inp_col, btn_col = st.columns([6, 1])
with inp_col:
    user_input = st.text_input(
        "Message", placeholder="Ask your trading coach anything…",
        key="coach_input", label_visibility="collapsed"
    )
with btn_col:
    send = st.button("Send", type="primary", use_container_width=True, key="coach_send")

# Clear button
if st.session_state["messages"]:
    if st.button("Clear conversation", key="coach_clear"):
        st.session_state["messages"] = []
        st.rerun()

# ── Process
query = clicked_chip or (user_input.strip() if send and user_input.strip() else None)

if query:
    st.session_state["messages"].append({"role": "user", "content": query})

    profile_str = ""
    if profile:
        profile_str = f"""
Trader profile:
- Experience: {profile.get('experience','Unknown')}
- Trading Style: {profile.get('style','Unknown')}
- Risk Appetite: {profile.get('risk','Unknown')}
- Goals: {profile.get('goals','')}
Tailor language, depth, and examples to their level and style.
"""

    context_str = ""
    if "last_backtest" in st.session_state:
        bt = st.session_state["last_backtest"]
        m  = bt.get("metrics", {})
        context_str += f"""
Most recent backtest context:
- Ticker: {bt.get('ticker','')}, Strategy: {bt.get('strategy','')}
- Total Return: {m.get('total_return',0)*100:+.1f}%, Alpha: {m.get('alpha',0)*100:+.1f}%
- Win Rate: {m.get('win_rate',0)*100:.1f}%, Max Drawdown: {m.get('max_drawdown',0)*100:.1f}%
- Sharpe Ratio: {m.get('sharpe',0):.2f}, Number of Trades: {m.get('num_trades',0)}
"""

    system = f"""You are an expert trading coach and educator on the 11% platform.
{profile_str}{context_str}

CRITICAL RESPONSE FORMAT — always follow this:
- Use ## section headers (e.g., ## 📖 WHAT IT IS, ## 💡 HOW TO USE IT, ## ⚠️ WATCH OUT FOR, ## 🏁 KEY TAKEAWAY)
- Use bullet points for lists, NOT walls of text
- Bold (**) key terms and important numbers
- Maximum 4-5 sections per response
- Keep each section to 2-4 sentences or 3-5 bullets
- Always end with a ## 💡 KEY TAKEAWAY containing one actionable insight
- If asked to review a backtest, give specific, constructive feedback on the numbers

Never write long unstructured paragraphs. Structure is essential for clarity.
"""

    history = [
        {"role": m["role"], "parts": [m["content"]]}
        for m in st.session_state["messages"][:-1]
    ]

    try:
        import google.generativeai as genai
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=system
        )
        chat = model.start_chat(history=history)
        with st.spinner("Coach is thinking…"):
            resp  = chat.send_message(query)
            reply = resp.text
        st.session_state["messages"].append({"role": "assistant", "content": reply})
        st.rerun()

    except Exception as e:
        st.error(f"AI error: {e}")
