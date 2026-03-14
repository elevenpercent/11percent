import streamlit as st, sys, os, pandas as pd, json
from datetime import datetime, date, timedelta
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.styles import SHARED_CSS, inject_bg
from utils.nav import navbar
from utils.session_persist import restore_session
from utils import db

st.set_page_config(page_title="Battles | 11%", layout="wide", initial_sidebar_state="collapsed")
st.markdown(SHARED_CSS, unsafe_allow_html=True)
st.markdown("""<style>
html,body,[data-testid="stAppViewContainer"]{background:#13161a!important}
[data-testid="stSidebar"],[data-testid="stSidebarNav"],[data-testid="collapsedControl"],
section[data-testid="stSidebar"]{display:none!important;width:0!important;max-width:0!important;opacity:0!important}
.battle-card{background:#1c1f23;border:1px solid #2d333b;border-radius:12px;padding:1.4rem 1.6rem;margin-bottom:0.8rem;transition:border-color 0.2s,transform 0.15s;position:relative;overflow:hidden}
.battle-card:hover{border-color:#373d47;transform:translateY(-2px)}
.battle-card::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,transparent,var(--accent,#4ade80),transparent)}
.battle-title{font-family:'Bebas Neue',sans-serif;font-size:1.5rem;letter-spacing:0.04em;color:#e6eaf0;margin-bottom:0.2rem}
.battle-sub{font-family:'IBM Plex Mono',monospace;font-size:0.65rem;color:#6b7280;line-height:1.6}
.battle-meta{display:flex;gap:1rem;flex-wrap:wrap;margin-top:0.7rem}
.bmeta{font-family:'IBM Plex Mono',monospace;font-size:0.58rem;color:#9ca3af}
.bmeta strong{color:#e6eaf0}
.badge-active{background:rgba(74,222,128,0.1);color:#4ade80;border:1px solid rgba(74,222,128,0.25);font-family:'IBM Plex Mono',monospace;font-size:0.45rem;text-transform:uppercase;letter-spacing:0.14em;padding:2px 8px;border-radius:3px}
.badge-pending{background:rgba(251,191,36,0.1);color:#fbbf24;border:1px solid rgba(251,191,36,0.25);font-family:'IBM Plex Mono',monospace;font-size:0.45rem;text-transform:uppercase;letter-spacing:0.14em;padding:2px 8px;border-radius:3px}
.badge-ended{background:rgba(107,114,128,0.15);color:#6b7280;border:1px solid rgba(107,114,128,0.25);font-family:'IBM Plex Mono',monospace;font-size:0.45rem;text-transform:uppercase;letter-spacing:0.14em;padding:2px 8px;border-radius:3px}
.pts-badge{background:rgba(74,222,128,0.08);border:1px solid rgba(74,222,128,0.2);border-radius:8px;padding:0.6rem 1rem;text-align:center;font-family:'IBM Plex Mono',monospace}
.pts-n{font-family:'Bebas Neue',sans-serif;font-size:2rem;color:#4ade80;line-height:1}
.pts-l{font-size:0.46rem;text-transform:uppercase;letter-spacing:0.18em;color:#3d4450;margin-top:0.15rem}
.lb-row{display:grid;grid-template-columns:30px 1fr 80px 80px 80px;gap:8px;align-items:center;padding:0.65rem 0.9rem;border-bottom:1px solid rgba(45,51,59,0.5);font-family:'IBM Plex Mono',monospace;font-size:0.65rem}
.lb-row:hover{background:rgba(255,255,255,0.01)}
.lb-rank{color:#3d4450;font-weight:700}.rank-1{color:#fbbf24}.rank-2{color:#9ca3af}.rank-3{color:#b45309}
.lb-name{color:#e6eaf0;font-weight:600}
.lb-pos{color:#4ade80;font-weight:700}.lb-neg{color:#f87171;font-weight:700}.lb-dim{color:#6b7280}
</style>""", unsafe_allow_html=True)

restore_session()
navbar()
inject_bg()

is_logged = bool(st.session_state.get("user"))
uid  = getattr(st.session_state.get("user"),"id","") or "" if is_logged else ""
uname = (st.session_state.get("user_email","").split("@")[0].replace("."," ").replace("_"," ").title()) if is_logged else ""

# Page header
st.markdown("""
<div style="background:#1c1f23;border:1px solid #2d333b;border-radius:12px;padding:2rem 2.5rem;margin-bottom:1.5rem;position:relative;overflow:hidden">
    <div style="position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,transparent,#f87171,transparent)"></div>
    <div style="font-family:'IBM Plex Mono',monospace;font-size:0.5rem;text-transform:uppercase;letter-spacing:0.3em;color:#3d4450;margin-bottom:0.4rem">Competition</div>
    <div style="font-family:'Bebas Neue',sans-serif;font-size:2.8rem;letter-spacing:0.04em;line-height:1;margin-bottom:0.4rem"><span style="color:#f87171">Paper Trading</span> Battles</div>
    <div style="font-family:'IBM Plex Mono',monospace;font-size:0.7rem;color:#6b7280;max-width:600px;line-height:1.8">
        Compete with traders worldwide using paper money. Set your parameters, replay the same market period, 
        and see who generates the best returns. Win points. Build your ranking.
    </div>
    <div style="margin-top:0.8rem;font-family:'IBM Plex Mono',monospace;font-size:0.6rem;color:#fbbf24;background:rgba(251,191,36,0.06);border:1px solid rgba(251,191,36,0.2);border-radius:6px;padding:0.5rem 0.9rem;display:inline-block">
        All battles are reviewed and approved before going live.
    </div>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["Active Battles", "Create Battle", "My Results"])

# ── TAB 1: Active battles ─────────────────────────────────────────────────────
with tab1:
    # Load battles from Supabase
    battles_data = []
    try:
        sb = db._sb()
        if sb:
            res = sb.table("battles").select("*").eq("approved", True).neq("status","ended").order("created_at", desc=True).execute()
            battles_data = res.data or []
    except: pass

    if not battles_data:
        # Show example battles when no DB
        battles_data = [
            {"id":"demo1","title":"SPY Monthly Challenge","description":"Who can generate the best return on SPY over a volatile month?","ticker":"SPY","interval":"1d","start_date":"2022-01-01","end_date":"2022-01-31","start_capital":10000,"status":"active","points_first":100,"points_second":60,"points_third":30,"points_finish":10,"max_participants":50},
            {"id":"demo2","title":"TSLA Earnings Week","description":"Trade TSLA around the Q4 2023 earnings. High volatility, high reward.","ticker":"TSLA","interval":"1h","start_date":"2024-01-22","end_date":"2024-01-26","start_capital":10000,"status":"active","points_first":150,"points_second":80,"points_third":40,"points_finish":15,"max_participants":30},
        ]
        st.markdown('<div class="info-box" style="margin-bottom:1rem">These are example battles. Connect Supabase to see live battles.</div>', unsafe_allow_html=True)

    for b in battles_data:
        accent = "#4ade80" if b["status"]=="active" else ("#fbbf24" if b["status"]=="pending" else "#6b7280")
        badge_cls = {"active":"badge-active","pending":"badge-pending","ended":"badge-ended"}.get(b["status"],"badge-ended")
        st.markdown(f"""
        <div class="battle-card" style="--accent:{accent}">
            <div style="display:flex;align-items:flex-start;justify-content:space-between;gap:1rem">
                <div>
                    <div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:0.25rem">
                        <div class="battle-title">{b["title"]}</div>
                        <span class="{badge_cls}">{b["status"].upper()}</span>
                    </div>
                    <div class="battle-sub">{b.get("description","")}</div>
                    <div class="battle-meta">
                        <span class="bmeta">Ticker: <strong>{b["ticker"]}</strong></span>
                        <span class="bmeta">Interval: <strong>{b["interval"]}</strong></span>
                        <span class="bmeta">Period: <strong>{b["start_date"]} → {b["end_date"]}</strong></span>
                        <span class="bmeta">Capital: <strong>${b["start_capital"]:,.0f}</strong></span>
                        <span class="bmeta">Max players: <strong>{b["max_participants"]}</strong></span>
                    </div>
                </div>
                <div style="display:flex;gap:0.5rem;flex-shrink:0">
                    <div class="pts-badge"><div class="pts-n">{b["points_first"]}</div><div class="pts-l">1st pts</div></div>
                    <div class="pts-badge" style="background:rgba(156,163,175,0.06);border-color:rgba(156,163,175,0.2)"><div class="pts-n" style="color:#9ca3af">{b["points_second"]}</div><div class="pts-l">2nd</div></div>
                    <div class="pts-badge" style="background:rgba(180,83,9,0.06);border-color:rgba(180,83,9,0.2)"><div class="pts-n" style="color:#b45309">{b["points_third"]}</div><div class="pts-l">3rd</div></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if b["status"] == "active":
            ec1, ec2, _ = st.columns([1,1,4])
            with ec1:
                if is_logged:
                    if st.button(f"Enter Battle", key=f"enter_{b['id']}", type="primary"):
                        # Save battle entry
                        st.session_state[f"active_battle"] = b
                        st.markdown(f'<script>window.top.location.href="/Replay"</script>', unsafe_allow_html=True)
                else:
                    st.markdown('<a href="/Login" style="display:block;text-align:center;background:#4ade80;color:#0a0f0a;font-family:IBM Plex Mono,monospace;font-size:0.62rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;padding:0.5rem;border-radius:7px;text-decoration:none">Sign In to Enter</a>', unsafe_allow_html=True)
            with ec2:
                # Leaderboard expand
                with st.expander("Leaderboard"):
                    entries = []
                    try:
                        if sb:
                            eres = sb.table("battle_entries").select("username,return_pct,final_value,submitted").eq("battle_id",b["id"]).eq("submitted",True).order("return_pct",desc=True).execute()
                            entries = eres.data or []
                    except: pass
                    if entries:
                        st.markdown('<div class="lb-row" style="font-size:0.46rem;text-transform:uppercase;letter-spacing:0.14em;color:#3d4450"><span>#</span><span>Trader</span><span>Value</span><span>Return</span><span>Points</span></div>', unsafe_allow_html=True)
                        for i, e in enumerate(entries[:10], 1):
                            rank_cls = {1:"rank-1",2:"rank-2",3:"rank-3"}.get(i,"lb-rank")
                            ret = e.get("return_pct",0)
                            pts = b["points_first"] if i==1 else (b["points_second"] if i==2 else (b["points_third"] if i==3 else b["points_finish"]))
                            rc = "lb-pos" if ret >= 0 else "lb-neg"
                            st.markdown(f'<div class="lb-row"><span class="{rank_cls}">{i}</span><span class="lb-name">{e["username"]}</span><span class="lb-dim">${e["final_value"]:,.0f}</span><span class="{rc}">{ret:+.1f}%</span><span style="color:#4ade80">{pts}</span></div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div style="font-family:IBM Plex Mono,monospace;font-size:0.65rem;color:#3d4450;padding:0.8rem">No submissions yet. Be the first!</div>', unsafe_allow_html=True)

# ── TAB 2: Create battle ──────────────────────────────────────────────────────
with tab2:
    if not is_logged:
        st.markdown('<div class="warn-box">Sign in to create a battle.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="font-family:IBM Plex Mono,monospace;font-size:0.7rem;color:#6b7280;margin-bottom:1.2rem;line-height:1.9;max-width:600px">Propose a battle. Set the parameters below — ticker, time period, and capital. All battles require admin approval before going live so the setup is fair for everyone.</div>', unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            b_title = st.text_input("Battle Title", placeholder="e.g. SPY Earnings Week Challenge")
            b_desc  = st.text_area("Description", height=80, placeholder="What makes this battle interesting? What market event does it cover?")
            b_ticker = st.text_input("Ticker", placeholder="SPY, AAPL, BTC-USD").upper().strip()
            b_interval = st.selectbox("Timeframe", ["1d","4h","1h","30m","15m","5m"])
        with c2:
            b_start    = st.date_input("Start Date", value=date.today()-timedelta(days=30))
            b_end      = st.date_input("End Date",   value=date.today()-timedelta(days=1))
            b_capital  = st.number_input("Starting Capital ($)", value=10000, min_value=1000, step=1000)
            b_maxpart  = st.number_input("Max Participants", value=50, min_value=2, max_value=500)

        st.markdown('<div style="font-family:IBM Plex Mono,monospace;font-size:0.55rem;text-transform:uppercase;letter-spacing:0.2em;color:#3d4450;margin:0.8rem 0 0.5rem">Points Structure</div>', unsafe_allow_html=True)
        p1,p2,p3,p4 = st.columns(4)
        with p1: pts1 = st.number_input("1st Place", value=100, min_value=10, step=10)
        with p2: pts2 = st.number_input("2nd Place", value=60,  min_value=5,  step=5)
        with p3: pts3 = st.number_input("3rd Place", value=30,  min_value=5,  step=5)
        with p4: pts4 = st.number_input("Finisher",  value=10,  min_value=1,  step=1)

        if st.button("Submit Battle for Review", type="primary"):
            if not b_title or not b_ticker:
                st.error("Title and ticker are required.")
            else:
                try:
                    payload = {
                        "created_by": uid, "title": b_title, "description": b_desc,
                        "ticker": b_ticker, "interval": b_interval,
                        "start_date": str(b_start), "end_date": str(b_end),
                        "start_capital": float(b_capital), "max_participants": int(b_maxpart),
                        "status": "pending", "approved": False,
                        "points_first": int(pts1), "points_second": int(pts2),
                        "points_third": int(pts3), "points_finish": int(pts4),
                    }
                    sb2 = db._sb()
                    if sb2:
                        sb2.table("battles").insert(payload).execute()
                        st.success("Battle submitted for review. You'll be notified once it goes live.")
                    else:
                        st.info("Battle saved locally (no DB connection). In production this will be submitted.")
                except Exception as e:
                    st.error(f"Error: {e}")

# ── TAB 3: My results ─────────────────────────────────────────────────────────
with tab3:
    if not is_logged:
        st.markdown('<div class="warn-box">Sign in to see your battle results.</div>', unsafe_allow_html=True)
    else:
        my_entries = []
        try:
            sb3 = db._sb()
            if sb3:
                res3 = sb3.table("battle_entries").select("*,battles(title,ticker,start_date,end_date)").eq("user_id",uid).order("created_at",desc=True).execute()
                my_entries = res3.data or []
        except: pass

        if my_entries:
            total_pts_earned = sum(e.get("points",0) for e in my_entries)
            st.markdown(f'<div style="font-family:IBM Plex Mono,monospace;font-size:0.72rem;color:#9ca3af;margin-bottom:1rem">You have entered <strong style="color:#e6eaf0">{len(my_entries)}</strong> battles and earned <strong style="color:#4ade80">{total_pts_earned} points</strong>.</div>', unsafe_allow_html=True)
            for e in my_entries:
                battle_info = e.get("battles") or {}
                ret = e.get("return_pct",0)
                rc = "#4ade80" if ret >= 0 else "#f87171"
                st.markdown(f"""
                <div class="battle-card">
                    <div style="display:flex;align-items:center;justify-content:space-between">
                        <div>
                            <div class="battle-title">{battle_info.get("title","Battle")}</div>
                            <div class="battle-sub">{battle_info.get("ticker","—")} · {battle_info.get("start_date","")[:10]} → {battle_info.get("end_date","")[:10]}</div>
                        </div>
                        <div style="text-align:right">
                            <div style="font-family:'Bebas Neue',sans-serif;font-size:1.8rem;color:{rc}">{ret:+.1f}%</div>
                            <div style="font-family:'IBM Plex Mono',monospace;font-size:0.55rem;color:#4ade80">+{e.get("points",0)} pts</div>
                            <div style="font-family:'IBM Plex Mono',monospace;font-size:0.5rem;color:#3d4450">Rank #{e.get("rank","—")}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown('<div style="text-align:center;padding:3rem;color:#3d4450;font-family:IBM Plex Mono,monospace;font-size:0.72rem;border:1px dashed #2d333b;border-radius:10px">You haven\'t entered any battles yet. <a href="#" style="color:#4ade80">Browse active battles</a></div>', unsafe_allow_html=True)
