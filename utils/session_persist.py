# utils/session_persist.py
# Saves login token to browser localStorage and restores on page load.
# Call restore_session() at the TOP of every page (before navbar).

import streamlit as st
import streamlit.components.v1 as components


def restore_session():
    """
    On every page load:
    1. Reads access_token from localStorage
    2. If found and session_state has no user, re-authenticates with Supabase
    3. Writes token to localStorage after login
    """
    # If already logged in this session, nothing to do
    if st.session_state.get("user"):
        return

    # Inject JS that reads localStorage and sends token back via query param
    # We use a hidden form trick: JS sets ?_token=xxx then Streamlit re-runs
    token_from_url = st.query_params.get("_token", "")

    if token_from_url:
        # Try to restore session from this token
        try:
            from supabase import create_client
            sb = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_ANON_KEY"])
            # Use the refresh token to get a fresh session
            res = sb.auth.get_user(token_from_url)
            if res and res.user:
                st.session_state["user"]         = res.user
                st.session_state["user_email"]   = res.user.email
                st.session_state["access_token"] = token_from_url
                # Clear the token from URL
                st.query_params.clear()
                st.rerun()
        except Exception:
            # Token expired or invalid — clear it
            st.query_params.clear()
            components.html("""
<script>
try { localStorage.removeItem('ep_token'); } catch(e) {}
window.location.href = window.location.pathname;
</script>
""", height=0)
        return

    # No token in URL — check localStorage via JS
    # This component reads localStorage and redirects with token if found
    components.html("""
<script>
(function() {
    try {
        var token = localStorage.getItem('ep_token');
        if (token) {
            var url = new URL(window.parent.location.href);
            if (!url.searchParams.get('_token')) {
                url.searchParams.set('_token', token);
                window.parent.location.href = url.toString();
            }
        }
    } catch(e) {}
})();
</script>
""", height=0, scrolling=False)


def save_session(token):
    """Call after successful login to persist token in browser localStorage."""
    safe = token.replace("'", "\\'")
    components.html(
        "<script>try{localStorage.setItem('ep_token','" + safe + "');}catch(e){}</script>",
        height=0, scrolling=False
    )


def clear_session():
    """Call on logout."""
    components.html(
        "<script>try{localStorage.removeItem('ep_token');}catch(e){}</script>",
        height=0, scrolling=False
    )
    for k in ["user", "user_email", "access_token"]:
        st.session_state.pop(k, None)
