import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.styles import SHARED_CSS, LOGO_IMG

st.set_page_config(page_title="Sign Up — 11%", page_icon="$", layout="centered", initial_sidebar_state="collapsed")
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
.pw-rules {
    font-family:'IBM Plex Mono',monospace; font-size:0.58rem;
    color:#1a2235; line-height:1.8; margin-top:0.4rem; margin-bottom:1rem;
}
[data-testid="stTextInput"] label {
    font-family:'IBM Plex Mono',monospace!important;
    font-size:0.62rem!important; text-transform:uppercase!important;
    letter-spacing:0.14em!important; color:#3a4a5e!important;
}
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_supabase():
    from supabase import create_client
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_ANON_KEY"]
    return create_client(url, key)

if st.session_state.get("user"):
    st.switch_page("app.py")

st.markdown('<div class="auth-wrap">', unsafe_allow_html=True)
st.markdown(f'<div class="auth-logo">{LOGO_IMG}</div>', unsafe_allow_html=True)
st.markdown('<div class="auth-card">', unsafe_allow_html=True)
st.markdown('<div class="auth-title">Create account</div>', unsafe_allow_html=True)
st.markdown('<div class="auth-sub">Free forever. No credit card required.</div>', unsafe_allow_html=True)

msg_slot = st.empty()

name     = st.text_input("Full name", placeholder="Alex Smith", key="su_name")
email    = st.text_input("Email", placeholder="you@example.com", key="su_email")
password = st.text_input("Password", placeholder="Min. 8 characters", type="password", key="su_pass")
confirm  = st.text_input("Confirm password", placeholder="••••••••", type="password", key="su_confirm")

st.markdown(
    '<div class="pw-rules">'
    '· At least 8 characters &nbsp;·&nbsp; One uppercase &nbsp;·&nbsp; One number'
    '</div>',
    unsafe_allow_html=True
)

if st.button("Create Account", type="primary", use_container_width=True):
    if not all([name, email, password, confirm]):
        msg_slot.markdown('<div class="auth-err">All fields are required.</div>', unsafe_allow_html=True)
    elif password != confirm:
        msg_slot.markdown('<div class="auth-err">Passwords do not match.</div>', unsafe_allow_html=True)
    elif len(password) < 8:
        msg_slot.markdown('<div class="auth-err">Password must be at least 8 characters.</div>', unsafe_allow_html=True)
    else:
        try:
            sb = get_supabase()
            res = sb.auth.sign_up({
                "email": email,
                "password": password,
                "options": {"data": {"full_name": name}}
            })
            if res.user:
                # Check if email confirmation is required
                if res.session is None:
                    msg_slot.markdown(
                        '<div class="auth-ok">✓ Account created! Check your email to confirm your address, then sign in.</div>',
                        unsafe_allow_html=True
                    )
                else:
                    st.session_state["user"]         = res.user
                    st.session_state["access_token"] = res.session.access_token
                    st.session_state["user_email"]   = res.user.email
                    msg_slot.markdown('<div class="auth-ok">✓ Account created! Redirecting...</div>', unsafe_allow_html=True)
                    st.switch_page("app.py")
        except Exception as e:
            err = str(e)
            if "already registered" in err or "already been registered" in err:
                msg_slot.markdown(
                    '<div class="auth-err">An account with this email already exists. '
                    '<a href="/Login" target="_self" style="color:#ff3d57;">Sign in instead</a></div>',
                    unsafe_allow_html=True
                )
            else:
                msg_slot.markdown(f'<div class="auth-err">{err}</div>', unsafe_allow_html=True)

st.markdown(
    '<div class="auth-footer">Already have an account? '
    '<a href="/Login" target="_self">Sign in</a></div>',
    unsafe_allow_html=True
)
st.markdown('</div></div>', unsafe_allow_html=True)
