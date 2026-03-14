"""
utils/auth.py
─────────────
Central auth helper for 11%.
All pages import: from utils.auth import require_auth, get_user, logout
"""
import streamlit as st


@st.cache_resource
def _get_supabase():
    from supabase import create_client
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_ANON_KEY"]
    return create_client(url, key)


def get_user():
    """Return current user dict or None."""
    return st.session_state.get("user")


def get_email():
    return st.session_state.get("user_email", "")


def is_logged_in():
    return st.session_state.get("user") is not None


def logout():
    """Clear session and redirect to login."""
    try:
        _get_supabase().auth.sign_out()
    except Exception:
        pass
    for key in ["user", "user_email", "access_token"]:
        st.session_state.pop(key, None)
    st.switch_page("pages/Login.py")


def require_auth():
    """
    Call at top of any page that needs auth.
    If not logged in → redirects to login page.
    Returns user dict if logged in.
    """
    if not is_logged_in():
        st.switch_page("pages/Login.py")
    return get_user()
