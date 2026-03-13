import streamlit as st, sys, os, pandas as pd
from datetime import date, timedelta
sys.path.insert(0, os.path.dirname(os.path.dirname(**file**)))
from utils.styles import SHARED_CSS; from utils.nav import navbar

st.set_page_config(page_title=“Economic Calendar | 11%”, layout=“wide”, initial_sidebar_state=“collapsed”)
st.markdown(SHARED_CSS, unsafe_allow_html=True)
st.markdown(”””<style>
.ph{background:linear-gradient(135deg,#0c1018,#0d1420);border:1px solid #1a2235;border-radius:16px;padding:2.5rem 3rem;margin-bottom:2rem}
.ph-ey{font-family:‘IBM Plex Mono’,monospace;font-size:0.55rem;text-transform:uppercase;letter-spacing:0.3em;color:#3a4a5e;margin-bottom:0.5rem}
.ph h1{font-family:‘Bebas Neue’,sans-serif;font-size:3.5rem;letter-spacing:0.05em;line-height:1;margin:0 0 0.5rem 0}
.ph p{font-family:‘IBM Plex Mono’,monospace;font-size:0.75rem;color:#8896ab;line-height:1.8;margin:0}
.sec-t{font-family:‘IBM Plex Mono’,monospace;font-size:0.55rem;text-transform:uppercase;letter-spacing:0.25em;color:#3a4a5e;padding:1.2rem 0 0.8rem;border-top:1px solid #0d1117}
.ev-row{display:grid;grid-template-columns:120px 70px 1fr 200px;gap:12px;align-items:center;padding:1rem 1.2rem;border-bottom:1px solid #0d1117;font-family:‘IBM Plex Mono’,monospace;transition:background 0.12s}
.ev-row:hover{background:rgba(255,255,255,0.02)}
.ev-hdr{background:#0d1117;font-size:0.5rem;text-transform:uppercase;letter-spacing:0.15em;color:#3a4a5e;border-radius:6px 6px 0 0}
.ev-date{font-size:0.68rem;color:#8896ab}
.ev-name{font-size:0.82rem;color:#eef2f7;font-weight:600}
.ev-desc{font-size:0.65rem;color:#8896ab;margin-top:0.15rem}
.imp-high{background:#ff3d57;color:#000;font-size:0.48rem;font-weight:700;text-transform:uppercase;letter-spacing:0.12em;padding:4px 10px;border-radius:4px;white-space:nowrap}
.imp-med{background:#ffd166;color:#000;font-size:0.48rem;font-weight:700;text-transform:uppercase;letter-spacing:0.12em;padding:4px 10px;border-radius:4px;white-space:nowrap}
.imp-low{background:#1a2235;color:#8896ab;font-size:0.48rem;font-weight:700;text-transform:uppercase;letter-spacing:0.12em;padding:4px 10px;border-radius:4px;white-space:nowrap}
.exp-val{font-size:0.72rem;color:#4da6ff;font-weight:700}
.today-row{background:rgba(0,230,118,0.04)!important;border-left:2px solid #00e676}
.upcoming-row{background:rgba(77,166,255,0.02)!important}
.guide-card{background:#0c1018;border:1px solid #1a2235;border-radius:12px;padding:1.5rem}
.guide-title{font-family:‘Bebas Neue’,sans-serif;font-size:1.6rem;letter-spacing:0.06em;margin-bottom:0.5rem}
.guide-body{font-family:‘IBM Plex Mono’,monospace;font-size:0.68rem;color:#8896ab;line-height:1.9}
.guide-body strong{color:#eef2f7}
.countdown{font-family:‘IBM Plex Mono’,monospace;font-size:0.58rem;padding:2px 8px;border-radius:4px;white-space:nowrap}
.next-badge{background:rgba(0,230,118,0.15);color:#00e676;border:1px solid rgba(0,230,118,0.3);font-family:‘IBM Plex Mono’,monospace;font-size:0.52rem;padding:3px 10px;border-radius:4px;font-weight:700;white-space:nowrap}
</style>”””, unsafe_allow_html=True)
navbar()

st.markdown(”””<div class="ph"><div class="ph-ey">Macro Events</div><h1>Economic Calendar</h1>

<p>The biggest market moves of the year happen around scheduled macro events. Know when FOMC, CPI, NFP, and GDP print — and understand how to position around them.</p></div>""", unsafe_allow_html=True)

today = date.today()

# 2026 calendar — all major scheduled events

EVENTS = [
# ── FOMC 2026 ──────────────────────────────────────────────────────────
{“date”:“2026-01-28”,“event”:“FOMC Rate Decision”,“category”:“FOMC”,“impact”:“high”,“prev”:“4.25%”,“exp”:“4.25%”,“note”:“January 2026 — first meeting of the year. Watch for updated dot plot signals.”},
{“date”:“2026-03-18”,“event”:“FOMC Rate Decision”,“category”:“FOMC”,“impact”:“high”,“prev”:“4.25%”,“exp”:“4.00%”,“note”:“March 2026 — quarterly meeting with updated economic projections.”},
{“date”:“2026-05-06”,“event”:“FOMC Rate Decision”,“category”:“FOMC”,“impact”:“high”,“prev”:“4.00%”,“exp”:“4.00%”,“note”:“May 2026 — no projections. Market watching for cut signals.”},
{“date”:“2026-06-17”,“event”:“FOMC Rate Decision”,“category”:“FOMC”,“impact”:“high”,“prev”:“4.00%”,“exp”:“3.75%”,“note”:“June 2026 — midyear quarterly meeting. SEP and dot plot updated.”},
{“date”:“2026-07-29”,“event”:“FOMC Rate Decision”,“category”:“FOMC”,“impact”:“high”,“prev”:“3.75%”,“exp”:“3.75%”,“note”:“July 2026 — no projections. Typical summer hold.”},
{“date”:“2026-09-16”,“event”:“FOMC Rate Decision”,“category”:“FOMC”,“impact”:“high”,“prev”:“3.75%”,“exp”:“3.50%”,“note”:“September 2026 — quarterly meeting. Major policy decision potential.”},
{“date”:“2026-11-04”,“event”:“FOMC Rate Decision”,“category”:“FOMC”,“impact”:“high”,“prev”:“3.50%”,“exp”:“3.50%”,“note”:“November 2026 — no projections. Post-election follow-through.”},
{“date”:“2026-12-16”,“event”:“FOMC Rate Decision”,“category”:“FOMC”,“impact”:“high”,“prev”:“3.50%”,“exp”:“3.25%”,“note”:“December 2026 — year-end meeting with full projections.”},
# ── CPI 2026 ───────────────────────────────────────────────────────────
{“date”:“2026-01-14”,“event”:“CPI (Dec 2025)”,“category”:“CPI”,“impact”:“high”,“prev”:“2.7%”,“exp”:“2.8%”,“note”:“December inflation print — sets the tone for Q1 Fed expectations.”},
{“date”:“2026-02-11”,“event”:“CPI (Jan 2026)”,“category”:“CPI”,“impact”:“high”,“prev”:“2.8%”,“exp”:“2.7%”,“note”:“January CPI — seasonal effects often distort this print.”},
{“date”:“2026-03-11”,“event”:“CPI (Feb 2026)”,“category”:“CPI”,“impact”:“high”,“prev”:“2.7%”,“exp”:“2.6%”,“note”:“February CPI — precedes March FOMC by one week.”},
{“date”:“2026-04-10”,“event”:“CPI (Mar 2026)”,“category”:“CPI”,“impact”:“high”,“prev”:“2.6%”,“exp”:“2.5%”,“note”:“Q1 inflation summary. Tariff pass-through in focus.”},
{“date”:“2026-05-13”,“event”:“CPI (Apr 2026)”,“category”:“CPI”,“impact”:“high”,“prev”:“2.5%”,“exp”:“2.4%”,“note”:“April CPI — services inflation persistence key.”},
{“date”:“2026-06-10”,“event”:“CPI (May 2026)”,“category”:“CPI”,“impact”:“high”,“prev”:“2.4%”,“exp”:“2.3%”,“note”:“May CPI — precedes June FOMC.”},
{“date”:“2026-07-15”,“event”:“CPI (Jun 2026)”,“category”:“CPI”,“impact”:“high”,“prev”:“2.3%”,“exp”:“2.2%”,“note”:“H1 inflation picture. Housing CPI lag key watch.”},
{“date”:“2026-08-12”,“event”:“CPI (Jul 2026)”,“category”:“CPI”,“impact”:“high”,“prev”:“2.2%”,“exp”:“2.2%”,“note”:“July CPI — summer seasonal patterns.”},
{“date”:“2026-09-10”,“event”:“CPI (Aug 2026)”,“category”:“CPI”,“impact”:“high”,“prev”:“2.2%”,“exp”:“2.1%”,“note”:“Precedes September FOMC.”},
{“date”:“2026-10-14”,“event”:“CPI (Sep 2026)”,“category”:“CPI”,“impact”:“high”,“prev”:“2.1%”,“exp”:“2.1%”,“note”:“Q3 inflation close. Election proximity adds volatility.”},
{“date”:“2026-11-12”,“event”:“CPI (Oct 2026)”,“category”:“CPI”,“impact”:“high”,“prev”:“2.1%”,“exp”:“2.0%”,“note”:“October CPI — post-election market focus shifts to macro.”},
{“date”:“2026-12-09”,“event”:“CPI (Nov 2026)”,“category”:“CPI”,“impact”:“high”,“prev”:“2.0%”,“exp”:“2.0%”,“note”:“Penultimate CPI before year-end FOMC.”},
# ── NFP 2026 ───────────────────────────────────────────────────────────
{“date”:“2026-01-09”,“event”:“Non-Farm Payrolls (Dec 2025)”,“category”:“NFP”,“impact”:“high”,“prev”:“256K”,“exp”:“170K”,“note”:“December jobs — holiday hiring seasonal distortions.”},
{“date”:“2026-02-06”,“event”:“Non-Farm Payrolls (Jan 2026)”,“category”:“NFP”,“impact”:“high”,“prev”:“170K”,“exp”:“150K”,“note”:“January NFP — large seasonal adjustment. Often revised heavily.”},
{“date”:“2026-03-06”,“event”:“Non-Farm Payrolls (Feb 2026)”,“category”:“NFP”,“impact”:“high”,“prev”:“150K”,“exp”:“160K”,“note”:“February jobs — unemployment rate trajectory key.”},
{“date”:“2026-04-03”,“event”:“Non-Farm Payrolls (Mar 2026)”,“category”:“NFP”,“impact”:“high”,“prev”:“160K”,“exp”:“155K”,“note”:“Q1 jobs total picture. AHE (wages) watched for inflation.”},
{“date”:“2026-05-08”,“event”:“Non-Farm Payrolls (Apr 2026)”,“category”:“NFP”,“impact”:“high”,“prev”:“155K”,“exp”:“150K”,“note”:“April NFP — post-tax-season clarity.”},
{“date”:“2026-06-05”,“event”:“Non-Farm Payrolls (May 2026)”,“category”:“NFP”,“impact”:“high”,“prev”:“150K”,“exp”:“145K”,“note”:“May NFP — precedes June FOMC by 12 days.”},
{“date”:“2026-07-10”,“event”:“Non-Farm Payrolls (Jun 2026)”,“category”:“NFP”,“impact”:“high”,“prev”:“145K”,“exp”:“140K”,“note”:“June jobs — H1 labor market summary.”},
{“date”:“2026-08-07”,“event”:“Non-Farm Payrolls (Jul 2026)”,“category”:“NFP”,“impact”:“high”,“prev”:“140K”,“exp”:“140K”,“note”:“July NFP — summer hiring trends.”},
{“date”:“2026-09-04”,“event”:“Non-Farm Payrolls (Aug 2026)”,“category”:“NFP”,“impact”:“high”,“prev”:“140K”,“exp”:“138K”,“note”:“Precedes September FOMC by 12 days.”},
{“date”:“2026-10-02”,“event”:“Non-Farm Payrolls (Sep 2026)”,“category”:“NFP”,“impact”:“high”,“prev”:“138K”,“exp”:“135K”,“note”:“September NFP — pre-election jobs focus.”},
{“date”:“2026-11-06”,“event”:“Non-Farm Payrolls (Oct 2026)”,“category”:“NFP”,“impact”:“high”,“prev”:“135K”,“exp”:“130K”,“note”:“October NFP — released 2 days after midterm elections.”},
{“date”:“2026-12-04”,“event”:“Non-Farm Payrolls (Nov 2026)”,“category”:“NFP”,“impact”:“high”,“prev”:“130K”,“exp”:“130K”,“note”:“November jobs — holiday hiring early read.”},
# ── GDP 2026 ───────────────────────────────────────────────────────────
{“date”:“2026-01-29”,“event”:“GDP Q4 2025 (Advance)”,“category”:“GDP”,“impact”:“high”,“prev”:“3.1%”,“exp”:“2.4%”,“note”:“First look at Q4 2025. Consumption and trade balance key.”},
{“date”:“2026-04-29”,“event”:“GDP Q1 2026 (Advance)”,“category”:“GDP”,“impact”:“high”,“prev”:“2.4%”,“exp”:“2.0%”,“note”:“First look at Q1 2026 growth.”},
{“date”:“2026-07-29”,“event”:“GDP Q2 2026 (Advance)”,“category”:“GDP”,“impact”:“high”,“prev”:“2.0%”,“exp”:“1.8%”,“note”:“Q2 2026 advance — recession watch if below 1%.”},
{“date”:“2026-10-28”,“event”:“GDP Q3 2026 (Advance)”,“category”:“GDP”,“impact”:“high”,“prev”:“1.8%”,“exp”:“2.0%”,“note”:“Q3 2026 first estimate. Election year context.”},
# ── PCE 2026 ───────────────────────────────────────────────────────────
{“date”:“2026-01-30”,“event”:“PCE Inflation (Dec 2025)”,“category”:“PCE”,“impact”:“high”,“prev”:“2.4%”,“exp”:“2.5%”,“note”:“Fed’s preferred inflation measure. Released day after FOMC.”},
{“date”:“2026-02-28”,“event”:“PCE Inflation (Jan 2026)”,“category”:“PCE”,“impact”:“high”,“prev”:“2.5%”,“exp”:“2.4%”,“note”:“January PCE — core PCE most important for Fed.”},
{“date”:“2026-03-27”,“event”:“PCE Inflation (Feb 2026)”,“category”:“PCE”,“impact”:“high”,“prev”:“2.4%”,“exp”:“2.4%”,“note”:“February PCE — watch core services ex-housing.”},
{“date”:“2026-04-30”,“event”:“PCE Inflation (Mar 2026)”,“category”:“PCE”,“impact”:“high”,“prev”:“2.4%”,“exp”:“2.3%”,“note”:“Q1 PCE — alongside Q1 GDP advance.”},
{“date”:“2026-05-29”,“event”:“PCE Inflation (Apr 2026)”,“category”:“PCE”,“impact”:“high”,“prev”:“2.3%”,“exp”:“2.2%”,“note”:“April PCE — tariff pass-through being watched.”},
{“date”:“2026-06-26”,“event”:“PCE Inflation (May 2026)”,“category”:“PCE”,“impact”:“high”,“prev”:“2.2%”,“exp”:“2.2%”,“note”:“May PCE — precedes July FOMC.”},
# ── Major Earnings 2026 ────────────────────────────────────────────────
{“date”:“2026-01-22”,“event”:“NFLX Earnings Q4”,“category”:“Earnings”,“impact”:“med”,“prev”:”$4.27 EPS”,“exp”:”$4.20 EPS”,“note”:“Ad-supported tier growth key metric.”},
{“date”:“2026-01-29”,“event”:“META Earnings Q4”,“category”:“Earnings”,“impact”:“high”,“prev”:”$8.02 EPS”,“exp”:”$7.80 EPS”,“note”:“AI capex guidance and ad revenue outlook.”},
{“date”:“2026-01-30”,“event”:“MSFT Earnings Q2”,“category”:“Earnings”,“impact”:“high”,“prev”:”$3.30 EPS”,“exp”:”$3.15 EPS”,“note”:“Azure cloud growth rate pivotal.”},
{“date”:“2026-02-05”,“event”:“AMZN Earnings Q4”,“category”:“Earnings”,“impact”:“high”,“prev”:”$1.43 EPS”,“exp”:”$1.50 EPS”,“note”:“AWS growth and retail margin expansion.”},
{“date”:“2026-02-06”,“event”:“GOOGL Earnings Q4”,“category”:“Earnings”,“impact”:“high”,“prev”:”$2.15 EPS”,“exp”:”$2.10 EPS”,“note”:“Search market share and AI monetization.”},
{“date”:“2026-04-23”,“event”:“TSLA Earnings Q1”,“category”:“Earnings”,“impact”:“high”,“prev”:”$0.72 EPS”,“exp”:”$0.65 EPS”,“note”:“Delivery numbers and energy storage growth.”},
{“date”:“2026-04-30”,“event”:“AAPL Earnings Q2”,“category”:“Earnings”,“impact”:“high”,“prev”:”$2.40 EPS”,“exp”:”$2.35 EPS”,“note”:“Services revenue and India expansion.”},
{“date”:“2026-05-22”,“event”:“NVDA Earnings Q1”,“category”:“Earnings”,“impact”:“high”,“prev”:”$0.89 EPS”,“exp”:”$0.85 EPS”,“note”:“Data center demand and H100/B100 supply.”},
]

df_ev = pd.DataFrame(EVENTS)
df_ev[“date_obj”] = pd.to_datetime(df_ev[“date”]).dt.date
df_ev = df_ev.sort_values(“date_obj”)

# Controls

c1, c2, c3 = st.columns([2, 2, 2])
with c1: cat_filter = st.multiselect(“Categories”, [“FOMC”,“CPI”,“NFP”,“GDP”,“PCE”,“Earnings”],
default=[“FOMC”,“CPI”,“NFP”,“GDP”,“PCE”,“Earnings”])
with c2: show_past = st.checkbox(“Include past events”, value=False)
with c3:
days_ahead = st.slider(“Show events in next N days”, 7, 365, 90)

# Apply filters

if show_past:
display_df = df_ev.copy()
else:
cutoff = today + timedelta(days=days_ahead)
display_df = df_ev[(df_ev[“date_obj”] >= today) & (df_ev[“date_obj”] <= cutoff)]

if cat_filter:
display_df = display_df[display_df[“category”].isin(cat_filter)]

# Next event highlight

upcoming_all = df_ev[df_ev[“date_obj”] >= today].sort_values(“date_obj”)
if not upcoming_all.empty:
next_ev = upcoming_all.iloc[0]
days_to_next = (next_ev[“date_obj”] - today).days
imp_cls = {“high”:“imp-high”,“med”:“imp-med”,“low”:“imp-low”}[next_ev[“impact”]]
st.markdown(f”””
<div style="background:rgba(0,230,118,0.05);border:1px solid rgba(0,230,118,0.2);border-radius:12px;padding:1.2rem 1.8rem;margin-bottom:1.5rem;display:flex;align-items:center;gap:2rem;flex-wrap:wrap;">
<div style="font-family:'IBM Plex Mono',monospace;font-size:0.52rem;text-transform:uppercase;letter-spacing:0.2em;color:#00e676;">Next Major Event</div>
<div style="font-family:'Bebas Neue',sans-serif;font-size:1.6rem;color:#eef2f7;letter-spacing:0.05em;">{next_ev[“event”]}</div>
<div style="font-family:'IBM Plex Mono',monospace;font-size:0.72rem;color:#8896ab;">{next_ev[“date”]}  ·  <strong style="color:#ffd166;">{“Today” if days_to_next==0 else f”In {days_to_next} day{‘s’ if days_to_next!=1 else ‘’}”}</strong></div>
<div style="margin-left:auto"><span class="{imp_cls}">{next_ev[“category”]}</span></div>
</div>
“””, unsafe_allow_html=True)

st.markdown(f’<div class="sec-t">Showing {len(display_df)} events{”” if show_past else f” in next {days_ahead} days”}</div>’, unsafe_allow_html=True)

if display_df.empty:
st.markdown(’<div style="text-align:center;padding:3rem;color:#3a4a5e;font-family:IBM Plex Mono,monospace;font-size:0.75rem;border:1px dashed #1a2235;border-radius:12px;">No events match your filters. Try expanding the date range or adding more categories.</div>’, unsafe_allow_html=True)
else:
st.markdown(’<div class="ev-row ev-hdr"><span>Date</span><span>Category</span><span>Event</span><span>Prev / Expected</span></div>’, unsafe_allow_html=True)
for _, row in display_df.iterrows():
days_away = (row[“date_obj”] - today).days
if days_away == 0:   time_str = “TODAY”; row_extra = “ today-row”
elif days_away < 0:  time_str = f”{abs(days_away)}d ago”; row_extra = “”
elif days_away <= 7: time_str = f”In {days_away}d”; row_extra = “ upcoming-row”
else:                time_str = f”In {days_away}d”; row_extra = “”
imp_cls = {“high”:“imp-high”,“med”:“imp-med”,“low”:“imp-low”}[row[“impact”]]
st.markdown(f”””
<div class="ev-row{row_extra}">
<div>
<div class="ev-date">{row[“date”]}</div>
<div style="font-family:IBM Plex Mono,monospace;font-size:0.58rem;color:{'#00e676' if days_away==0 else '#ffd166' if 0<days_away<=7 else '#3a4a5e'};">{time_str}</div>
</div>
<span class="{imp_cls}">{row[“category”]}</span>
<div>
<div class="ev-name">{row[“event”]}</div>
<div class="ev-desc">{row[“note”]}</div>
</div>
<div style="font-family:IBM Plex Mono,monospace;font-size:0.68rem;color:#8896ab;">
Prev: <strong style="color:#eef2f7">{row[“prev”]}</strong>   Exp: <span class="exp-val">{row[“exp”]}</span>
</div>
</div>
“””, unsafe_allow_html=True)

# Event trading guide

st.markdown(’<div class="sec-t">How to Trade Around Macro Events</div>’, unsafe_allow_html=True)
g1, g2, g3, g4 = st.columns(4)
for col, (title, color, body) in zip([g1,g2,g3,g4], [
(“FOMC Days”,”#ff3d57”,”<strong>Biggest vol events of the year.</strong> Market moves 2-3x normal range. Fade the initial spike or wait for the second candle after Powell starts speaking. Never hold short-dated options into the decision — IV crush destroys premium.”),
(“CPI Prints”,”#ffd166”,”<strong>Hot CPI</strong> (above estimate) = dollar up, rates up, stocks down immediately. <strong>Cool CPI</strong> = risk on. The 30 minutes post-print are the most liquid of the month. Spreads widen into the print — use limit orders not market orders.”),
(“NFP Fridays”,”#00e676”,“Jobs report drops 8:30am ET. Spread widens massively in the 5 mins before. Strong jobs = hawkish Fed = stocks down short-term. Wait for the 9:31 open candle before any directional trade. Initial move is often faded within 30 minutes.”),
(“GDP Reports”,”#4da6ff”,”<strong>Advance estimate</strong> is the biggest mover — later revisions rarely matter. Watch the Q/Q annualised rate vs consensus. Below 1.5% raises recession concern. Above 3% is strongly risk-on. Personal consumption component is the quality indicator.”),
]):
col.markdown(f’<div class="guide-card"><div class="guide-title" style="color:{color}">{title}</div><div class="guide-body">{body}</div></div>’, unsafe_allow_html=True)