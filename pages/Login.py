import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.styles import SHARED_CSS, LOGO_IMG

st.set_page_config(page_title="Sign In — 11%", page_icon="$", layout="centered", initial_sidebar_state="collapsed")
st.markdown(SHARED_CSS, unsafe_allow_html=True)

st.markdown("""
<style>
@keyframes fadeUp { from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:translateY(0)} }
.auth-wrap {
    max-width:420px; margin:0 auto; padding:3rem 0 4rem;
    animation:fadeUp 0.5s ease both;
}
.auth-logo {
    display:flex; align-items:center; justify-content:center;
    margin-bottom:2.5rem;
}
.auth-card {
    background:#0c1018; border:1px solid #1a2235; border-radius:14px;
    padding:2.2rem 2rem;
}
.auth-title {
    font-family:'Bebas Neue',sans-serif; font-size:2.2rem;
    color:#eef2f7; letter-spacing:0.04em; margin-bottom:0.3rem; line-height:1;
}
.auth-sub {
    font-size:0.82rem; color:#3a4a5e; margin-bottom:2rem; line-height:1.5;
}
.auth-divider {
    display:flex; align-items:center; gap:0.8rem; margin:1.4rem 0;
}
.auth-divider span {
    font-family:'IBM Plex Mono',monospace; font-size:0.55rem;
    text-transform:uppercase; letter-spacing:0.15em; color:#1a2235; flex-shrink:0;
}
.auth-divider::before,.auth-divider::after {
    content:''; flex:1; height:1px; background:#1a2235;
}
.auth-footer {
    text-align:center; margin-top:1.4rem;
    font-family:'IBM Plex Mono',monospace; font-size:0.62rem; color:#3a4a5e;
}
.auth-footer a { color:#00e676; text-decoration:none; }
.auth-footer a:hover { text-decoration:underline; }
.auth-err {
    background:rgba(255,61,87,0.08); border:1px solid rgba(255,61,87,0.25);
    border-radius:8px; padding:0.7rem 1rem;
    font-size:0.78rem; color:#ff3d57; margin-bottom:1rem; line-height:1.5;
}
.auth-ok {
    background:rgba(0,230,118,0.08); border:1px solid rgba(0,230,118,0.25);
    border-radius:8px; padding:0.7rem 1rem;
    font-size:0.78rem; color:#00e676; margin-bottom:1rem; line-height:1.5;
}
/* Label styling */
[data-testid="stTextInput"] label {
    font-family:'IBM Plex Mono',monospace!important;
    font-size:0.62rem!important; text-transform:uppercase!important;
    letter-spacing:0.14em!important; color:#3a4a5e!important;
}
</style>
""", unsafe_allow_html=True)

# ── Init Supabase ─────────────────────────────────────────────────────────────
@st.cache_resource
def get_supabase():
    from supabase import create_client
    url  = st.secrets["SUPABASE_URL"]
    key  = st.secrets["SUPABASE_ANON_KEY"]
    return create_client(url, key)

# ── Redirect if already logged in ────────────────────────────────────────────
if st.session_state.get("user"):
    st.switch_page("app.py")

# ── UI ────────────────────────────────────────────────────────────────────────
st.markdown('<div class="auth-wrap">', unsafe_allow_html=True)
st.markdown(f'<div class="auth-logo">{LOGO_IMG}</div>', unsafe_allow_html=True)
st.markdown('<div class="auth-card">', unsafe_allow_html=True)
st.markdown('<div class="auth-title">Welcome back</div>', unsafe_allow_html=True)
st.markdown('<div class="auth-sub">Sign in to your 11% account</div>', unsafe_allow_html=True)

# Error/success placeholders
msg_slot = st.empty()

email    = st.text_input("Email", placeholder="you@example.com", key="login_email")
password = st.text_input("Password", placeholder="••••••••", type="password", key="login_pass")

st.markdown('<div style="margin-top:0.3rem;text-align:right;margin-bottom:1rem;">'
            '<a href="/Forgot_Password" target="_self" style="font-family:IBM Plex Mono,monospace;'
            'font-size:0.6rem;color:#3a4a5e;text-decoration:none;" '
            'onmouseover="this.style.color=\'#00e676\'" onmouseout="this.style.color=\'#3a4a5e\'">'
            'Forgot password?</a></div>', unsafe_allow_html=True)

if st.button("Sign In", type="primary", use_container_width=True):
    if not email or not password:
        msg_slot.markdown('<div class="auth-err">Please enter your email and password.</div>', unsafe_allow_html=True)
    else:
        try:
            sb = get_supabase()
            res = sb.auth.sign_in_with_password({"email": email, "password": password})
            st.session_state["user"]         = res.user
            st.session_state["access_token"] = res.session.access_token
            st.session_state["user_email"]   = res.user.email
            msg_slot.markdown('<div class="auth-ok">✓ Signed in! Redirecting...</div>', unsafe_allow_html=True)
            st.switch_page("app.py")
        except Exception as e:
            err = str(e)
            if "Invalid login" in err or "invalid_credentials" in err:
                msg_slot.markdown('<div class="auth-err">Incorrect email or password.</div>', unsafe_allow_html=True)
            elif "Email not confirmed" in err:
                msg_slot.markdown('<div class="auth-err">Please confirm your email before signing in.</div>', unsafe_allow_html=True)
            else:
                msg_slot.markdown(f'<div class="auth-err">{err}</div>', unsafe_allow_html=True)

st.markdown(
    '<div class="auth-divider"><span>or</span></div>'
    '<div class="auth-footer">Don\'t have an account? '
    '<a href="/Signup" target="_self">Create one free</a></div>',
    unsafe_allow_html=True
)
st.markdown('</div></div>', unsafe_allow_html=True)
