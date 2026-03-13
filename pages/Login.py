import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.styles import SHARED_CSS, LOGO_IMG
from utils.session_persist import save_session, restore_session

st.set_page_config(page_title="Sign In — 11%", page_icon="$", layout="centered", initial_sidebar_state="collapsed")
st.markdown(SHARED_CSS, unsafe_allow_html=True)

restore_session()  # Try to load from localStorage first

st.markdown("""
<style>
@keyframes fadeUp{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:translateY(0)}}
.auth-page{max-width:420px;margin:0 auto;padding:3.5rem 0 4rem;animation:fadeUp 0.45s ease both;}
.auth-logo{display:flex;justify-content:center;margin-bottom:2.5rem;}
.auth-card{background:#0c1018;border:1px solid #1a2235;border-radius:14px;padding:2.2rem 2rem;}
.auth-title{font-family:'Bebas Neue',sans-serif;font-size:2.4rem;color:#eef2f7;letter-spacing:0.04em;line-height:1;margin-bottom:0.25rem;}
.auth-sub{font-size:0.82rem;color:#3a4a5e;margin-bottom:1.8rem;line-height:1.5;}
.auth-err{background:rgba(255,61,87,0.08);border:1px solid rgba(255,61,87,0.25);border-radius:8px;padding:0.7rem 1rem;font-size:0.78rem;color:#ff3d57;margin-bottom:1rem;line-height:1.5;}
.auth-ok{background:rgba(0,230,118,0.08);border:1px solid rgba(0,230,118,0.25);border-radius:8px;padding:0.7rem 1rem;font-size:0.78rem;color:#00e676;margin-bottom:1rem;line-height:1.5;}
.auth-foot{text-align:center;margin-top:1.3rem;font-family:'IBM Plex Mono',monospace;font-size:0.62rem;color:#3a4a5e;}
.auth-foot a{color:#00e676;text-decoration:none;}
[data-testid="stTextInput"] label{font-family:'IBM Plex Mono',monospace!important;font-size:0.6rem!important;text-transform:uppercase!important;letter-spacing:0.14em!important;color:#3a4a5e!important;}
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def _sb():
    from supabase import create_client
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_ANON_KEY"])

if st.session_state.get("user"):
    st.switch_page("app.py")

st.markdown('<div class="auth-page">', unsafe_allow_html=True)
st.markdown('<div class="auth-logo">' + LOGO_IMG + '</div>', unsafe_allow_html=True)
st.markdown('<div class="auth-card">', unsafe_allow_html=True)
st.markdown('<div class="auth-title">Welcome back</div>', unsafe_allow_html=True)
st.markdown('<div class="auth-sub">Sign in to your 11% account</div>', unsafe_allow_html=True)

msg      = st.empty()
email    = st.text_input("Email",    placeholder="you@example.com")
password = st.text_input("Password", placeholder="••••••••", type="password")

if st.button("Sign In", type="primary", use_container_width=True):
    if not email or not password:
        msg.markdown('<div class="auth-err">Please fill in all fields.</div>', unsafe_allow_html=True)
    else:
        try:
            res = _sb().auth.sign_in_with_password({"email": email, "password": password})
            st.session_state["user"]         = res.user
            st.session_state["user_email"]   = res.user.email
            st.session_state["access_token"] = res.session.access_token
            # Persist to localStorage so refresh doesn't log out
            save_session(res.session.access_token)
            msg.markdown('<div class="auth-ok">&#10003; Signed in!</div>', unsafe_allow_html=True)
            st.switch_page("app.py")
        except Exception as e:
            err = str(e)
            if "Invalid login" in err or "invalid_credentials" in err:
                msg.markdown('<div class="auth-err">Incorrect email or password.</div>', unsafe_allow_html=True)
            elif "Email not confirmed" in err:
                msg.markdown('<div class="auth-err">Confirm your email first — check your inbox.</div>', unsafe_allow_html=True)
            else:
                msg.markdown('<div class="auth-err">' + err + '</div>', unsafe_allow_html=True)

st.markdown(
    '<div class="auth-foot" style="margin-top:1rem;">Don\'t have an account? '
    '<a href="/Signup" target="_self">Create one free &#8594;</a></div>',
    unsafe_allow_html=True
)
st.markdown('</div></div>', unsafe_allow_html=True)
