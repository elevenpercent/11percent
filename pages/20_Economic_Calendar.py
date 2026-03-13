import streamlit as st, sys, os, pandas as pd
from datetime import date, timedelta
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.styles import SHARED_CSS; from utils.nav import navbar

st.set_page_config(page_title="Economic Calendar | 11%", layout="wide", initial_sidebar_state="collapsed")
st.markdown(SHARED_CSS, unsafe_allow_html=True)
st.markdown("""<style>
.ph{background:linear-gradient(135deg,#0c1018,#0d1420);border:1px solid #1a2235;border-radius:16px;padding:2.5rem 3rem;margin-bottom:2rem}
.ph-ey{font-family:'IBM Plex Mono',monospace;font-size:0.55rem;text-transform:uppercase;letter-spacing:0.3em;color:#3a4a5e;margin-bottom:0.5rem}
.ph h1{font-family:'Bebas Neue',sans-serif;font-size:3.5rem;letter-spacing:0.05em;line-height:1;margin:0 0 0.5rem 0}
.ph p{font-family:'IBM Plex Mono',monospace;font-size:0.75rem;color:#8896ab;line-height:1.8;margin:0}
.sec-t{font-family:'IBM Plex Mono',monospace;font-size:0.55rem;text-transform:uppercase;letter-spacing:0.25em;color:#3a4a5e;padding:1.2rem 0 0.8rem;border-top:1px solid #0d1117}
.ev-row{display:grid;grid-template-columns:110px 60px 1fr 180px;gap:12px;align-items:center;padding:1rem 1.2rem;border-bottom:1px solid #0d1117;font-family:'IBM Plex Mono',monospace;transition:background 0.12s}
.ev-row:hover{background:rgba(255,255,255,0.02)}
.ev-hdr{background:#0d1117;font-size:0.5rem;text-transform:uppercase;letter-spacing:0.15em;color:#3a4a5e;border-radius:6px 6px 0 0}
.ev-date{font-size:0.68rem;color:#8896ab}
.ev-name{font-size:0.82rem;color:#eef2f7;font-weight:600}
.ev-desc{font-size:0.65rem;color:#8896ab;margin-top:0.15rem}
.imp-high{background:#ff3d57;color:#000;font-size:0.48rem;font-weight:700;text-transform:uppercase;letter-spacing:0.12em;padding:3px 9px;border-radius:4px}
.imp-med{background:#ffd166;color:#000;font-size:0.48rem;font-weight:700;text-transform:uppercase;letter-spacing:0.12em;padding:3px 9px;border-radius:4px}
.imp-low{background:#1a2235;color:#8896ab;font-size:0.48rem;font-weight:700;text-transform:uppercase;letter-spacing:0.12em;padding:3px 9px;border-radius:4px}
.exp-val{font-size:0.72rem;color:#4da6ff;font-weight:700}
.guide-card{background:#0c1018;border:1px solid #1a2235;border-radius:12px;padding:1.5rem}
.guide-title{font-family:'Bebas Neue',sans-serif;font-size:1.6rem;letter-spacing:0.06em;margin-bottom:0.5rem}
.guide-body{font-family:'IBM Plex Mono',monospace;font-size:0.68rem;color:#8896ab;line-height:1.9}
.guide-body strong{color:#eef2f7}
</style>""", unsafe_allow_html=True)
navbar()

st.markdown("""<div class="ph"><div class="ph-ey">Macro Events</div><h1>Economic Calendar</h1><p>The biggest market moves of the year happen around scheduled macro events. Know when FOMC, CPI, NFP, and GDP print — and understand how to position around them.</p></div>""", unsafe_allow_html=True)

# Static calendar — dates approximate for 2025
today = date.today()
EVENTS = [
    # FOMC
    {"date":"2025-01-29","event":"FOMC Rate Decision","category":"FOMC","impact":"high","prev":"4.50%","exp":"4.50%","note":"Watch for forward guidance and dot plot changes"},
    {"date":"2025-03-19","event":"FOMC Rate Decision","category":"FOMC","impact":"high","prev":"4.50%","exp":"4.25%","note":"March decision — inflation data key"},
    {"date":"2025-05-07","event":"FOMC Rate Decision","category":"FOMC","impact":"high","prev":"4.25%","exp":"4.00%","note":"May FOMC — labor market in focus"},
    {"date":"2025-06-18","event":"FOMC Rate Decision","category":"FOMC","impact":"high","prev":"4.00%","exp":"3.75%","note":"Midyear policy pivot potential"},
    {"date":"2025-07-30","event":"FOMC Rate Decision","category":"FOMC","impact":"high","prev":"3.75%","exp":"3.75%","note":"July pause likely"},
    {"date":"2025-09-17","event":"FOMC Rate Decision","category":"FOMC","impact":"high","prev":"3.75%","exp":"3.50%","note":"September — watch PCE trends"},
    {"date":"2025-11-05","event":"FOMC Rate Decision","category":"FOMC","impact":"high","prev":"3.50%","exp":"3.50%","note":"Post-election meeting"},
    {"date":"2025-12-10","event":"FOMC Rate Decision","category":"FOMC","impact":"high","prev":"3.50%","exp":"3.25%","note":"Year-end decision + projections"},
    # CPI
    {"date":"2025-01-15","event":"CPI (Dec)","category":"CPI","impact":"high","prev":"2.7%","exp":"2.9%","note":"Inflation gauge — market mover"},
    {"date":"2025-02-12","event":"CPI (Jan)","category":"CPI","impact":"high","prev":"2.9%","exp":"2.8%","note":"First CPI of 2025"},
    {"date":"2025-03-12","event":"CPI (Feb)","category":"CPI","impact":"high","prev":"2.8%","exp":"2.7%","note":"Trend vs transitory"},
    {"date":"2025-04-10","event":"CPI (Mar)","category":"CPI","impact":"high","prev":"2.7%","exp":"2.7%","note":"Q1 inflation recap"},
    {"date":"2025-05-14","event":"CPI (Apr)","category":"CPI","impact":"high","prev":"2.7%","exp":"2.6%","note":"Services inflation key"},
    {"date":"2025-06-11","event":"CPI (May)","category":"CPI","impact":"high","prev":"2.6%","exp":"2.5%","note":"Summer trend"},
    # NFP
    {"date":"2025-01-10","event":"Non-Farm Payrolls (Dec)","category":"NFP","impact":"high","prev":"256K","exp":"160K","note":"Labor market strength"},
    {"date":"2025-02-07","event":"Non-Farm Payrolls (Jan)","category":"NFP","impact":"high","prev":"143K","exp":"160K","note":"January seasonal adjustments"},
    {"date":"2025-03-07","event":"Non-Farm Payrolls (Feb)","category":"NFP","impact":"high","prev":"151K","exp":"160K","note":"Unemployment rate watch"},
    {"date":"2025-04-04","event":"Non-Farm Payrolls (Mar)","category":"NFP","impact":"high","prev":"228K","exp":"135K","note":"Q1 jobs picture"},
    {"date":"2025-05-02","event":"Non-Farm Payrolls (Apr)","category":"NFP","impact":"high","prev":"177K","exp":"130K","note":"Rate cut sensitivity high"},
    # GDP
    {"date":"2025-01-30","event":"GDP Q4 (Advance)","category":"GDP","impact":"med","prev":"3.1%","exp":"2.6%","note":"Q4 2024 advance estimate"},
    {"date":"2025-03-27","event":"GDP Q4 (Final)","category":"GDP","impact":"med","prev":"2.3%","exp":"2.4%","note":"Final Q4 revision"},
    {"date":"2025-04-30","event":"GDP Q1 (Advance)","category":"GDP","impact":"high","prev":"2.4%","exp":"1.8%","note":"Q1 2025 first look"},
    # PCE
    {"date":"2025-01-31","event":"PCE Inflation (Dec)","category":"PCE","impact":"high","prev":"2.4%","exp":"2.6%","note":"Fed's preferred inflation gauge"},
    {"date":"2025-02-28","event":"PCE Inflation (Jan)","category":"PCE","impact":"high","prev":"2.5%","exp":"2.5%","note":"Core PCE key"},
    {"date":"2025-03-28","event":"PCE Inflation (Feb)","category":"PCE","impact":"high","prev":"2.5%","exp":"2.5%","note":"Month-over-month reading"},
]

df_ev = pd.DataFrame(EVENTS)
df_ev["date_obj"] = pd.to_datetime(df_ev["date"]).dt.date
df_ev = df_ev.sort_values("date_obj")
upcoming = df_ev[df_ev["date_obj"] >= today]

# Filter controls
c1, c2 = st.columns([2,4])
with c1:
    cat_filter = st.multiselect("Filter by category", ["FOMC","CPI","NFP","GDP","PCE"], default=["FOMC","CPI","NFP","GDP","PCE"])
with c2:
    show_past = st.checkbox("Show past events", value=False)

display_df = df_ev if show_past else upcoming
if cat_filter: display_df = display_df[display_df["category"].isin(cat_filter)]

st.markdown('<div class="sec-t">Upcoming Macro Events</div>', unsafe_allow_html=True)
st.markdown('<div class="ev-row ev-hdr"><span>Date</span><span>Category</span><span>Event</span><span>Expected / Prev</span></div>', unsafe_allow_html=True)

for _, row in display_df.iterrows():
    days_away = (row["date_obj"] - today).days
    time_str = f"in {days_away}d" if days_away > 0 else ("Today" if days_away == 0 else f"{abs(days_away)}d ago")
    imp_cls = {"high":"imp-high","med":"imp-med","low":"imp-low"}[row["impact"]]
    st.markdown(f"""
    <div class="ev-row">
        <div>
            <div class="ev-date">{row["date"]}</div>
            <div style="font-family:IBM Plex Mono,monospace;font-size:0.58rem;color:#3a4a5e;">{time_str}</div>
        </div>
        <span class="{imp_cls}">{row["category"]}</span>
        <div>
            <div class="ev-name">{row["event"]}</div>
            <div class="ev-desc">{row["note"]}</div>
        </div>
        <div style="font-family:IBM Plex Mono,monospace;font-size:0.68rem;color:#8896ab;">
            Prev: <strong style="color:#eef2f7">{row["prev"]}</strong> &nbsp; Exp: <span class="exp-val">{row["exp"]}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Event trading guide
st.markdown('<div class="sec-t">How to Trade Around Macro Events</div>', unsafe_allow_html=True)
g1, g2, g3, g4 = st.columns(4)
for col, (title, color, body) in zip([g1,g2,g3,g4], [
    ("FOMC Days","#ff3d57","<strong>Biggest vol events of the year.</strong> Market moves 2–3x normal range. Fade the initial spike or wait for the second candle after the press conference. Never hold short-dated options into the decision."),
    ("CPI Prints","#ffd166","<strong>Hot CPI</strong> (above estimate) = dollar up, rates up, stocks down. <strong>Cool CPI</strong> = risk on. The 30 minutes post-print are the most liquid of the month. Use limit orders."),
    ("NFP Fridays","#00e676","Jobs report drops at 8:30am ET. Spread widens massively before. Strong jobs = hawkish Fed = stocks down short term. Wait for the 9:31 candle before entering directional trades."),
    ("GDP Reports","#4da6ff","<strong>Advance estimate</strong> is the biggest mover. Revisions matter less. Watch for Q/Q annualised rate vs expectations. Below 1.5% raises recession concern; above 3% is strongly bullish."),
]):
    col.markdown(f'<div class="guide-card"><div class="guide-title" style="color:{color}">{title}</div><div class="guide-body">{body}</div></div>', unsafe_allow_html=True)
