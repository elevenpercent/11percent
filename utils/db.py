"""
utils/db.py
─────────────────────────────────────────────────────────────
Supabase persistence layer for 11%.

Stores per-user data in a single 'user_data' table:
  user_id  TEXT  (Supabase auth UID)
  key      TEXT  (data category, e.g. 'journal', 'portfolio', 'replay_trades')
  value    JSONB (the actual payload)
  updated_at TIMESTAMPTZ

Required SQL (run once in Supabase SQL editor):
─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS user_data (
  user_id    TEXT NOT NULL,
  key        TEXT NOT NULL,
  value      JSONB,
  updated_at TIMESTAMPTZ DEFAULT now(),
  PRIMARY KEY (user_id, key)
);
ALTER TABLE user_data ENABLE ROW LEVEL SECURITY;
CREATE POLICY "users own data" ON user_data
  USING (auth.uid()::text = user_id)
  WITH CHECK (auth.uid()::text = user_id);
─────────────────────────────────────────────────────────────
"""

import streamlit as st
import json


@st.cache_resource
def _sb():
    try:
        from supabase import create_client
        return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_ANON_KEY"])
    except Exception:
        return None


def _uid():
    """Return current user's UID, or None if not logged in."""
    user = st.session_state.get("user")
    if not user:
        return None
    return getattr(user, "id", None) or (user.get("id") if isinstance(user, dict) else None)


def save(key: str, data) -> bool:
    """
    Persist data[key] for the current user.
    data can be a list, dict, or any JSON-serialisable value.
    Returns True on success, False if not logged in or error.
    """
    uid = _uid()
    if not uid:
        return False
    sb = _sb()
    if not sb:
        return False
    try:
        payload = {"user_id": uid, "key": key, "value": data, "updated_at": "now()"}
        sb.table("user_data").upsert(payload).execute()
        return True
    except Exception:
        return False


def load(key: str, default=None):
    """
    Load data[key] for the current user.
    Returns default if not logged in, not found, or error.
    """
    uid = _uid()
    if not uid:
        return default
    sb = _sb()
    if not sb:
        return default
    try:
        res = sb.table("user_data").select("value").eq("user_id", uid).eq("key", key).execute()
        if res.data:
            return res.data[0]["value"]
        return default
    except Exception:
        return default


def load_into_session(key: str, session_key: str = None, default=None):
    """
    Load key from DB and store in st.session_state[session_key].
    Only fetches from DB if session_state doesn't already have it.
    """
    sk = session_key or key
    if sk not in st.session_state or st.session_state[sk] is None:
        val = load(key, default)
        st.session_state[sk] = val if val is not None else (default if default is not None else [])


def sync(key: str, session_key: str = None):
    """
    Push current st.session_state[session_key] to DB.
    Call this after any mutation.
    """
    sk = session_key or key
    data = st.session_state.get(sk)
    if data is not None:
        save(key, data)
