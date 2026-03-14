import streamlit as st, sys, os, pandas as pd
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.styles import SHARED_CSS, inject_bg
from utils.nav import navbar
from utils.session_persist import restore_session
from utils import db

st.set_page_config(page_title="Dashboard | 11%", layout="wide", initial_sidebar_state="collapsed")

restore_session()

st.markdown(SHARED_CSS, unsafe_allow_html=True)
st.markdown("""<style>
html,body,[data-testid="stAppViewContainer"]{background:#13161a!important}
[data-testid="stSidebar"],[data-testid="stSidebarNav"],[data-testid="collapsedControl"],
section[data-testid="stSidebar"]{display:none!important;width:0!important;max-width:0!important;opacity:0!important}
.dash-hero{background:linear-gradient(135deg,#1c1f23,#1a1e24);border:1px solid #2d333b;border-radius:14px;padding:2rem 2.5rem;margin-bottom:1.5rem;position:relative;overflow:hidden}
.dash-hero::after{content:'';position:absolute;bottom:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,rgba(74,222,128,0.3),transparent)}
.dash-greeting{font-family:'Bebas Neue',sans-serif;font-size:2.8rem;letter-spacing:0.05em;line-height:1;margin-bottom:0.25rem}
.dash-sub{font-family:'IBM Plex Mono',monospace;font-size:0.7rem;color:#6b7280;line-height:1.7}
.stat-bar{display:grid;grid-template-columns:repeat(6,1fr);gap:0;background:#1c1f23;border:1px solid #2d333b;border-radius:10px;overflow:hidden;margin-bottom:1.5rem}
.stat-cell{padding:1rem 1.2rem;border-right:1px solid #2d333b;text-align:center}
.stat-cell:last-child{border-right:none}
.stat-n{font-family:'IBM Plex Mono',monospace;font-size:1.6rem;font-weight:700;line-height:1}
.stat-l{font-family:'IBM Plex Mono',monospace;font-size:0.44rem;text-transform:uppercase;letter-spacing:0.2em;color:#3d4450;margin-top:0.2rem}
.card{background:#1c1f23;border:1px solid #2d333b;border-radius:12px;padding:1.4rem;margin-bottom:1rem;transition:border-color 0.2s}
.card:hover{border-color:#373d47}
.card-title{font-family:'IBM Plex Mono',monospace;font-size:0.52rem;text-transform:uppercase;letter-spacing:0.22em;color:#4ade80;margin-bottom:0.9rem;display:flex;align-items:center;gap:0.5rem}
.next-step{background:#13161a;border:1px solid #2d333b;border-radius:10px;padding:1rem 1.2rem;display:flex;align-items:center;justify-content:space-between;cursor:pointer;transition:border-color 0.2s,background 0.2s;margin-bottom:0.5rem}
.next-step:hover{border-color:#4ade80;background:rgba(74,222,128,0.02)}
.next-step-title{font-family:'IBM Plex Mono',monospace;font-size:0.78rem;font-weight:600;color:#e6eaf0;margin-bottom:0.15rem}
.next-step-sub{font-family:'IBM Plex Mono',monospace;font-size:0.6rem;color:#6b7280}
.next-step-arr{color:#4ade80;font-size:1rem}
.action-chip{background:#13161a;border:1px solid #2d333b;border-radius:8px;padding:0.8rem;text-align:center;cursor:pointer;transition:border-color 0.2s;text-decoration:none;display:block}
.action-chip:hover{border-color:#4ade80}
.action-chip-name{font-family:'IBM Plex Mono',monospace;font-size:0.65rem;font-weight:600;color:#e6eaf0;margin-bottom:0.15rem}
.action-chip-sub{font-family:'IBM Plex Mono',monospace;font-size:0.54rem;color:#3d4450}
.session-row{display:grid;grid-template-columns:1fr 80px 80px 80px 60px;gap:8px;align-items:center;padding:0.7rem 0.9rem;border-bottom:1px solid rgba(45,51,59,0.5);font-family:'IBM Plex Mono',monospace;font-size:0.66rem;transition:background 0.1s}
.session-row:hover{background:rgba(255,255,255,0.01)}
.s-sym{font-weight:600;color:#e6eaf0}
.s-pos{color:#4ade80;font-weight:600}.s-neg{color:#f87171;font-weight:600}.s-dim{color:#6b7280}
.achievement{background:#13161a;border:1px solid #2d333b;border-radius:8px;padding:0.9rem;display:flex;align-items:center;gap:0.8rem;opacity:0.5}
.achievement.unlocked{opacity:1;border-color:#4ade80}
.ach-icon{font-size:1.4rem;width:36px;text-align:center}
.ach-name{font-family:'IBM Plex Mono',monospace;font-size:0.65rem;font-weight:600;color:#e6eaf0}
.ach-desc{font-family:'IBM Plex Mono',monospace;font-size:0.55rem;color:#6b7280;margin-top:0.1rem}
.ach-prog{font-family:'IBM Plex Mono',monospace;font-size:0.52rem;color:#4ade80;margin-top:0.2rem}
.streak-num{font-family:'Bebas Neue',sans-serif;font-size:3.5rem;color:#f87171;letter-spacing:0.04em;line-height:1}
.points-big{font-family:'Bebas Neue',sans-serif;font-size:3.5rem;color:#4ade80;letter-spacing:0.04em;line-height:1}
</style>""", unsafe_allow_html=True)

restore_session()
navbar()
inject_bg()

# Require login
if not st.session_state.get("user"):
    st.markdown("""<div style="text-align:center;padding:5rem 2rem">
        <div style="font-family:'Bebas Neue',sans-serif;font-size:3rem;color:#e6eaf0;margin-bottom:0.5rem">Your Dashboard</div>
        <div style="font-family:'IBM Plex Mono',monospace;font-size:0.75rem;color:#6b7280;margin-bottom:1.5rem">Sign in to access your personal trading dashboard, session history, and battle results.</div>
    </div>""", unsafe_allow_html=True)
    c1,c2,_ = st.columns([1,1,3])
    with c1: st.markdown('<a href="/Login" style="display:block;text-align:center;background:#4ade80;color:#0a0f0a;font-family:IBM Plex Mono,monospace;font-size:0.65rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;padding:0.6rem 1.2rem;border-radius:8px;text-decoration:none">Sign In</a>', unsafe_allow_html=True)
    with c2: st.markdown('<a href="/Signup" style="display:block;text-align:center;background:transparent;color:#9ca3af;font-family:IBM Plex Mono,monospace;font-size:0.65rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;padding:0.6rem 1.2rem;border-radius:8px;text-decoration:none;border:1px solid #2d333b">Create Account</a>', unsafe_allow_html=True)
    st.stop()

email = st.session_state.get("user_email","")
uid   = getattr(st.session_state.get("user"), "id", "") or ""
uname = email.split("@")[0].replace("."," ").replace("_"," ").title()

# Load user data
journal   = db.load("journal",   []) or []
portfolio = db.load("portfolio", []) or []
sessions  = db.load("replay_sessions_index", []) or []
profile   = db.load("profile_stats", {}) or {}

total_pts    = profile.get("points", 0)
battles_won  = profile.get("battles_won", 0)
streak       = profile.get("streak", 0)
total_trades = len(journal)
total_sessions = len(sessions)
win_rate = 0
if journal:
    wins = sum(1 for t in journal if t.get("out") == "Win")
    win_rate = round(wins/len(journal)*100)
total_pnl = sum(t.get("pnl",0) for t in journal)

# ── Hero greeting ─────────────────────────────────────────────────────────────
now_hour = datetime.now().hour
greeting = "Good morning" if now_hour < 12 else ("Good afternoon" if now_hour < 17 else "Good evening")
st.markdown(f"""
<div class="dash-hero">
    <div class="dash-greeting"><span style="color:#4ade80">{greeting},</span> {uname}!</div>
    <div class="dash-sub">Welcome to your trading dashboard. Track your progress, review sessions, and compete in battles.</div>
</div>
""", unsafe_allow_html=True)

# ── Stat bar ──────────────────────────────────────────────────────────────────
pnl_color = "#4ade80" if total_pnl >= 0 else "#f87171"
wr_color  = "#4ade80" if win_rate >= 50 else "#f87171"
st.markdown(f"""
<div class="stat-bar">
    <div class="stat-cell"><div class="stat-n" style="color:#e6eaf0">{total_sessions}</div><div class="stat-l">Sessions</div></div>
    <div class="stat-cell"><div class="stat-n" style="color:#e6eaf0">{total_trades}</div><div class="stat-l">Trades</div></div>
    <div class="stat-cell"><div class="stat-n" style="color:{wr_color}">{win_rate}%</div><div class="stat-l">Win Rate</div></div>
    <div class="stat-cell"><div class="stat-n" style="color:{pnl_color}">${total_pnl:+,.0f}</div><div class="stat-l">Total P&L</div></div>
    <div class="stat-cell"><div class="stat-n" style="color:#4ade80">{total_pts}</div><div class="stat-l">Points</div></div>
    <div class="stat-cell"><div class="stat-n" style="color:#f87171">{streak}</div><div class="stat-l">Day Streak</div></div>
</div>
""", unsafe_allow_html=True)

# ── Main grid ─────────────────────────────────────────────────────────────────
left, right = st.columns([7, 4])

with left:
    # Next steps
    st.markdown('<div class="card"><div class="card-title">Your Next Steps</div>', unsafe_allow_html=True)
    steps = [
        ("Start a Replay Session", "Load any ticker and trade bar-by-bar", "/Replay"),
        ("Run a Backtest", "Test a strategy on historical data", "/Strategy_Lab"),
        ("Enter a Battle", "Compete with other traders, win points", "/Battles"),
        ("Log a Trade", "Track your manual trades in the journal", "/Trade_Journal"),
    ]
    for title, sub, href in steps:
        st.markdown(f"""<a href="{href}" style="text-decoration:none"><div class="next-step">
            <div><div class="next-step-title">{title}</div><div class="next-step-sub">{sub}</div></div>
            <div class="next-step-arr">&#8594;</div>
        </div></a>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Recent sessions
    st.markdown('<div class="card"><div class="card-title">Recent Replay Sessions</div>', unsafe_allow_html=True)
    if sessions:
        st.markdown('<div class="session-row" style="font-size:0.48rem;text-transform:uppercase;letter-spacing:0.15em;color:#3d4450;border-bottom:2px solid #2d333b"><span>Session</span><span>Ticker</span><span>P&L</span><span>Return</span><span>Date</span></div>', unsafe_allow_html=True)
        for s in sorted(sessions, key=lambda x: x.get("updated_at",""), reverse=True)[:8]:
            pnl   = s.get("pnl", 0)
            ret   = s.get("return_pct", 0)
            pc    = "s-pos" if pnl >= 0 else "s-neg"
            rc    = "s-pos" if ret >= 0 else "s-neg"
            date  = s.get("updated_at","")[:10] if s.get("updated_at") else "—"
            st.markdown(f"""<div class="session-row">
                <span class="s-sym">{s.get("name","Unnamed")}</span>
                <span class="s-dim">{s.get("ticker","—")}</span>
                <span class="{pc}">${pnl:+,.0f}</span>
                <span class="{rc}">{ret:+.1f}%</span>
                <span class="s-dim">{date}</span>
            </div>""", unsafe_allow_html=True)
    else:
        st.markdown('<div style="font-family:IBM Plex Mono,monospace;font-size:0.7rem;color:#3d4450;padding:1.5rem 0;text-align:center;border:1px dashed #2d333b;border-radius:8px">No sessions yet. <a href="/Replay" style="color:#4ade80">Start your first replay</a></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with right:
    # Points & streak
    st.markdown(f"""
    <div class="card">
        <div class="card-title">Battles & Points</div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;text-align:center;margin-bottom:1rem">
            <div>
                <div class="points-big">{total_pts}</div>
                <div style="font-family:'IBM Plex Mono',monospace;font-size:0.48rem;text-transform:uppercase;letter-spacing:0.18em;color:#3d4450;margin-top:0.2rem">Total Points</div>
            </div>
            <div>
                <div class="streak-num">{streak}</div>
                <div style="font-family:'IBM Plex Mono',monospace;font-size:0.48rem;text-transform:uppercase;letter-spacing:0.18em;color:#3d4450;margin-top:0.2rem">Day Streak</div>
            </div>
        </div>
        <a href="/Battles" style="display:block;text-align:center;background:#4ade80;color:#0a0f0a;font-family:IBM Plex Mono,monospace;font-size:0.62rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;padding:0.6rem;border-radius:8px;text-decoration:none">Enter a Battle</a>
    </div>
    """, unsafe_allow_html=True)

    # Quick actions
    st.markdown('<div class="card"><div class="card-title">Quick Actions</div>', unsafe_allow_html=True)
    actions = [
        ("Strategy Lab",    "Backtest strategies",   "/Strategy_Lab"),
        ("Market Replay",   "Step-by-step replay",   "/Replay"),
        ("Screener",        "Filter stocks",          "/Screener"),
        ("Options Chain",   "Live chain + advisor",   "/Options_Chain"),
        ("Heatmap",         "Sector overview",        "/Market_Heatmap"),
        ("AI Coach",        "Ask anything",           "/Assistant"),
    ]
    acols = st.columns(2)
    for i,(name,sub,href) in enumerate(actions):
        with acols[i%2]:
            st.markdown(f'<a class="action-chip" href="{href}" style="text-decoration:none"><div class="action-chip-name">{name}</div><div class="action-chip-sub">{sub}</div></a>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Achievements
    st.markdown('<div class="card"><div class="card-title">Achievements</div>', unsafe_allow_html=True)
    achievements = [
        ("First Session",   total_sessions >= 1,  f"{min(total_sessions,1)}/1",    "Complete your first replay"),
        ("Consistent",      total_sessions >= 5,  f"{min(total_sessions,5)}/5",    "Complete 5 sessions"),
        ("Active Trader",   total_trades  >= 20,  f"{min(total_trades,20)}/20",    "Log 20 trades"),
        ("Battle Ready",    battles_won   >= 1,   f"{min(battles_won,1)}/1",       "Win your first battle"),
        ("Point Collector", total_pts     >= 100, f"{min(total_pts,100)}/100",     "Earn 100 points"),
    ]
    for icon, unlocked, prog, desc in [("🎯",*achievements[0][1:]),("🔥",*achievements[1][1:]),("📈",*achievements[2][1:]),("⚔️",*achievements[3][1:]),("⭐",*achievements[4][1:])]:
        cls = "achievement unlocked" if unlocked else "achievement"
        name_list = ["First Session","Consistent","Active Trader","Battle Ready","Point Collector"]
        n = name_list[achievements.index(next(a for a in achievements if a[1]==unlocked and a[2]==prog and a[3]==desc))]
        st.markdown(f"""<div class="{cls}" style="margin-bottom:6px">
            <div class="ach-icon">{icon}</div>
            <div><div class="ach-name">{n}</div><div class="ach-desc">{desc}</div><div class="ach-prog">{prog}</div></div>
        </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
