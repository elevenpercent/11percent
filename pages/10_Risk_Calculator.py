import streamlit as st
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(__file__)))
from utils.session_persist import restore_session
import sys, os, math, pandas as pd
import plotly.graph_objects as go
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.styles import SHARED_CSS, inject_bg, PLOTLY_THEME
from utils.nav import navbar

st.set_page_config(page_title="Risk Calculator | 11%", layout="wide", initial_sidebar_state="collapsed")
restore_session()
st.markdown(SHARED_CSS, unsafe_allow_html=True)

st.markdown("""<style>
.rc-hero{background:linear-gradient(135deg,#0c1018 0%,#0d1420 100%);border:1px solid #1a2235;border-radius:16px;padding:2.5rem 3rem;margin-bottom:2rem;position:relative;overflow:hidden}
.rc-hero::before{content:'';position:absolute;top:-60px;right:-60px;width:200px;height:200px;background:radial-gradient(circle,rgba(0,230,118,0.06) 0%,transparent 70%);pointer-events:none}
.rc-hero-eyebrow{font-family:'IBM Plex Mono',monospace;font-size:0.55rem;text-transform:uppercase;letter-spacing:0.3em;color:#3a4a5e;margin-bottom:0.5rem}
.rc-hero h1{font-family:'Bebas Neue',sans-serif;font-size:3.5rem;letter-spacing:0.05em;line-height:1;color:#eef2f7;margin:0 0 0.5rem 0}
.rc-hero p{font-family:'IBM Plex Mono',monospace;font-size:0.75rem;color:#8896ab;line-height:1.8;max-width:600px;margin:0}
.big-metric{background:#0c1018;border:1px solid #1a2235;border-radius:12px;padding:1.5rem 1.8rem;transition:border-color 0.2s,transform 0.2s}
.big-metric:hover{border-color:#2a3550;transform:translateY(-2px)}
.big-metric-val{font-family:'Bebas Neue',sans-serif;font-size:2.6rem;letter-spacing:0.05em;line-height:1}
.big-metric-lbl{font-family:'IBM Plex Mono',monospace;font-size:0.52rem;text-transform:uppercase;letter-spacing:0.22em;color:#3a4a5e;margin-top:0.4rem}
.big-metric-sub{font-family:'IBM Plex Mono',monospace;font-size:0.65rem;color:#8896ab;margin-top:0.2rem}
.verdict-card{border-radius:12px;padding:1.5rem 2rem;margin:1.5rem 0;font-family:'IBM Plex Mono',monospace}
.verdict-pass{background:rgba(0,230,118,0.06);border:1px solid rgba(0,230,118,0.25)}
.verdict-fail{background:rgba(255,61,87,0.06);border:1px solid rgba(255,61,87,0.25)}
.verdict-title{font-size:1rem;font-weight:700;margin-bottom:0.6rem}
.verdict-line{font-size:0.72rem;color:#8896ab;line-height:2.2}
.verdict-line strong{color:#eef2f7}
.section-title{font-family:'IBM Plex Mono',monospace;font-size:0.55rem;text-transform:uppercase;letter-spacing:0.25em;color:#3a4a5e;padding:1.5rem 0 0.8rem;border-top:1px solid #0d1117;margin-top:0.5rem}
</style>""", unsafe_allow_html=True)

navbar()

# ── Same-tab nav hook ─────────────────────────────────────────────────────────
import streamlit.components.v1 as _nav_cv1
_nav_cv1.html("""<script>
(function(){
  window.parent.document.addEventListener('click',function(e){
    var a=e.target.closest('a[href]');
    if(!a)return;
    var href=a.getAttribute('href');
    if(!href||href.startsWith('http')||href.startsWith('mailto')||href.startsWith('#'))return;
    e.preventDefault();e.stopPropagation();
    window.top.location.href=href;
  },true);
})();
</script>""", height=0)

inject_bg()

st.markdown("""
<div class="rc-hero">
  <div class="rc-hero-eyebrow">Position Sizing</div>
  <h1>Risk Calculator</h1>
  <p>Calculate exactly how many shares to buy, how much you are risking, and whether the trade is worth taking — before you enter a single position.</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["Position Sizer", "R-Multiple Tracker", "Kelly Criterion"])

with tab1:
    st.markdown('<div class="section-title">Trade Inputs</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        account = st.number_input("Account Size ($)", value=25000, min_value=100, step=1000)
        entry   = st.number_input("Entry Price ($)", value=150.00, min_value=0.01, step=0.50, format="%.2f")
        target  = st.number_input("Target Price ($)", value=162.00, min_value=0.01, step=0.50, format="%.2f")
    with c2:
        risk_pct = st.slider("Risk per Trade (%)", min_value=0.25, max_value=5.0, value=1.0, step=0.25)
        stop     = st.number_input("Stop Loss ($)", value=145.00, min_value=0.01, step=0.50, format="%.2f")

    risk_amt     = account * risk_pct / 100
    stop_dist    = abs(entry - stop)
    shares       = int(risk_amt / stop_dist) if stop_dist > 0 else 0
    position_val = shares * entry
    reward       = abs(target - entry) * shares
    rr           = abs(target - entry) / stop_dist if stop_dist > 0 else 0
    pct_port     = position_val / account * 100

    st.markdown('<div class="section-title">Results</div>', unsafe_allow_html=True)
    cols = st.columns(5)
    for col, (val, lbl, sub, color) in zip(cols, [
        (f"${risk_amt:,.0f}", "At Risk", f"{risk_pct}% of account", "#ff3d57"),
        (str(shares), "Shares", f"${position_val:,.0f} position", "#00e676"),
        (f"{pct_port:.1f}%", "Portfolio %", "position size", "#4da6ff"),
        (f"${reward:,.0f}", "Potential Reward", "if target is hit", "#00e676"),
        (f"{rr:.2f}:1", "Risk / Reward", "reward per $1 risked", "#ffd166"),
    ]):
        col.markdown(f'<div class="big-metric"><div class="big-metric-val" style="color:{color}">{val}</div><div class="big-metric-lbl">{lbl}</div><div class="big-metric-sub">{sub}</div></div>', unsafe_allow_html=True)

    is_good = rr >= 2.0
    vc = "verdict-pass" if is_good else "verdict-fail"
    vt_color = "#00e676" if is_good else "#ff3d57"
    st.markdown(f"""
    <div class="verdict-card {vc}">
        <div class="verdict-title" style="color:{vt_color}">{"Trade Setup Looks Good" if is_good else "Trade Setup Needs Work"}</div>
        <div class="verdict-line">
            Risk: <strong>${risk_amt:,.0f}</strong> &nbsp;·&nbsp; Shares: <strong>{shares}</strong> &nbsp;·&nbsp; Position: <strong>${position_val:,.2f}</strong> ({pct_port:.1f}% of portfolio)<br>
            Stop distance: <strong>${stop_dist:.2f}</strong> &nbsp;·&nbsp; Reward potential: <strong>${reward:,.0f}</strong><br>
            R/R: <strong>{rr:.2f}:1</strong> — {"Good. Above the 2:1 minimum threshold." if rr >= 2 else "Below the 2:1 minimum. Move target up or tighten stop."}
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">Shares You Can Buy at Different Stop Levels</div>', unsafe_allow_html=True)
    stop_pcts  = [0.5, 1, 2, 3, 5, 8, 10]
    shares_lst = [int(risk_amt / (entry * p/100)) if entry * p/100 > 0 else 0 for p in stop_pcts]
    fig = go.Figure()
    fig.add_bar(x=[f"{p}% stop" for p in stop_pcts], y=shares_lst,
                marker_color=["#00e676" if s > 0 else "#1a2235" for s in shares_lst],
                text=[str(s) for s in shares_lst], textposition="outside",
                textfont=dict(family="IBM Plex Mono", size=12, color="#eef2f7"))
    fig.update_layout(**PLOTLY_THEME, height=280, showlegend=False,
                      xaxis_title="Stop Distance from Entry", yaxis_title="Max Shares")
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.markdown('<div class="section-title">Log Trades — Track R-Multiples Over Time</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-family:IBM Plex Mono,monospace;font-size:0.72rem;color:#8896ab;margin-bottom:1.2rem;line-height:1.8;">An R-multiple measures gain/loss relative to initial risk. +2R = made 2x your risk. -1R = lost your full risk. Track this across 20+ trades to find your edge.</div>', unsafe_allow_html=True)

    if "r_trades" not in st.session_state:
        st.session_state["r_trades"] = []

    ra, rb, rc = st.columns(3)
    with ra: r_entry = st.number_input("Entry Price", value=100.00, format="%.2f", key="re")
    with rb: r_stop  = st.number_input("Stop Price",  value=97.00,  format="%.2f", key="rs")
    with rc: r_exit  = st.number_input("Exit Price",  value=106.00, format="%.2f", key="rex")

    if st.button("Add Trade", type="primary"):
        risk_r = abs(r_entry - r_stop)
        r_mult = (r_exit - r_entry) / risk_r if risk_r > 0 else 0
        st.session_state["r_trades"].append({"Entry": r_entry, "Stop": r_stop, "Exit": r_exit, "R": round(r_mult, 2)})
        st.rerun()

    if st.session_state["r_trades"]:
        df_r = pd.DataFrame(st.session_state["r_trades"])
        avg_r = df_r["R"].mean(); total_r = df_r["R"].sum()
        wins_r = (df_r["R"] > 0).sum()

        m1, m2, m3, m4 = st.columns(4)
        for col, (val, lbl, color) in zip([m1,m2,m3,m4], [
            (f"{avg_r:+.2f}R", "Avg R / Trade", "#00e676" if avg_r >= 0 else "#ff3d57"),
            (f"{total_r:+.2f}R", "Total R", "#00e676" if total_r >= 0 else "#ff3d57"),
            (f"{wins_r}/{len(df_r)}", "Wins / Total", "#4da6ff"),
            (f"{wins_r/len(df_r)*100:.0f}%", "Win Rate", "#ffd166"),
        ]):
            col.markdown(f'<div class="big-metric"><div class="big-metric-val" style="color:{color}">{val}</div><div class="big-metric-lbl">{lbl}</div></div>', unsafe_allow_html=True)

        fig2 = go.Figure()
        cum_r = df_r["R"].cumsum()
        fig2.add_bar(name="R / Trade", x=list(range(1,len(df_r)+1)), y=df_r["R"],
                     marker_color=["#00e676" if r >= 0 else "#ff3d57" for r in df_r["R"]])
        fig2.add_scatter(name="Cumulative R", x=list(range(1,len(df_r)+1)), y=cum_r,
                         line=dict(color="#4da6ff", width=2), yaxis="y2")
        fig2.update_layout(**PLOTLY_THEME, height=300, title="R-Multiple Distribution",
                           yaxis2=dict(overlaying="y", side="right", color="#4da6ff", title="Cumulative R"))
        st.plotly_chart(fig2, use_container_width=True)

        with st.expander(f"View all {len(df_r)} trades"):
            st.dataframe(df_r, use_container_width=True, hide_index=True)
        if st.button("Clear Log"):
            st.session_state["r_trades"] = []; st.rerun()
    else:
        st.markdown('<div style="text-align:center;padding:3rem;color:#3a4a5e;font-family:IBM Plex Mono,monospace;font-size:0.75rem;border:1px dashed #1a2235;border-radius:12px;margin-top:1.5rem;">Log your first trade above to start tracking R-multiples.</div>', unsafe_allow_html=True)

with tab3:
    st.markdown('<div class="section-title">Kelly Criterion — Optimal Position Sizing</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-family:IBM Plex Mono,monospace;font-size:0.72rem;color:#8896ab;margin-bottom:1.5rem;line-height:1.9;max-width:700px;">The Kelly Criterion calculates the optimal fraction of capital to risk per trade to maximize long-term growth. Full Kelly causes big drawdowns — most professionals use Half Kelly for smoother compounding.</div>', unsafe_allow_html=True)

    ka, kb = st.columns(2)
    with ka: k_wr = st.slider("Your Win Rate (%)", 10, 90, 55) / 100
    with kb: k_rr = st.slider("Average Win / Average Loss", 0.5, 5.0, 2.0, 0.1)

    kelly = k_wr - (1 - k_wr) / k_rr
    half_kelly = kelly / 2; quarter_kelly = kelly / 4

    k1, k2, k3 = st.columns(3)
    for col, (val, lbl, desc, color) in zip([k1,k2,k3], [
        (f"{kelly*100:.1f}%", "Full Kelly", "Theoretical max — volatile", "#ffd166"),
        (f"{half_kelly*100:.1f}%", "Half Kelly", "Recommended", "#00e676"),
        (f"{quarter_kelly*100:.1f}%", "Quarter Kelly", "Conservative", "#4da6ff"),
    ]):
        col.markdown(f'<div class="big-metric"><div class="big-metric-val" style="color:{color}">{val}</div><div class="big-metric-lbl">{lbl}</div><div class="big-metric-sub">{desc}</div></div>', unsafe_allow_html=True)

    if kelly <= 0:
        st.markdown(f'<div class="verdict-card verdict-fail"><div class="verdict-title" style="color:#ff3d57">Negative Edge — Do Not Trade This Setup</div><div class="verdict-line">With {k_wr*100:.0f}% win rate and {k_rr:.1f}:1 payoff the expected value is negative. Improve win rate, increase average wins, or cut average losses.</div></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="verdict-card verdict-pass"><div class="verdict-title" style="color:#00e676">Positive Edge Confirmed</div><div class="verdict-line">With {k_wr*100:.0f}% win rate and {k_rr:.1f}:1 payoff, risk <strong>{half_kelly*100:.1f}% per trade</strong> (Half Kelly). On a $25,000 account that is <strong>${25000*half_kelly:,.0f} per trade</strong>.</div></div>', unsafe_allow_html=True)

    wr_range    = [x/100 for x in range(10, 91)]
    kelly_vals  = [max(0, w - (1-w)/k_rr) * 100 for w in wr_range]
    half_k_vals = [v/2 for v in kelly_vals]
    fig3 = go.Figure()
    fig3.add_scatter(x=[w*100 for w in wr_range], y=kelly_vals, name="Full Kelly", line=dict(color="#ffd166", width=2))
    fig3.add_scatter(x=[w*100 for w in wr_range], y=half_k_vals, name="Half Kelly", line=dict(color="#00e676", width=2))
    fig3.add_vline(x=k_wr*100, line_dash="dash", line_color="#4da6ff", annotation_text=f"You: {k_wr*100:.0f}%")
    fig3.update_layout(**PLOTLY_THEME, title=f"Kelly % vs Win Rate (payoff {k_rr:.1f}:1)",
                       height=300, xaxis_title="Win Rate (%)", yaxis_title="Bet Size (%)")
    st.plotly_chart(fig3, use_container_width=True)
