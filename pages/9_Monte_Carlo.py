import streamlit as st
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(__file__)))
from utils.session_persist import restore_session
import sys, os, pandas as pd, numpy as np
from datetime import date, timedelta
import yfinance as yf, plotly.graph_objects as go
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.styles import SHARED_CSS, inject_bg, PLOTLY_THEME; from utils.nav import navbar

st.set_page_config(page_title="Monte Carlo | 11%", layout="wide", initial_sidebar_state="collapsed")
restore_session()
st.markdown(SHARED_CSS, unsafe_allow_html=True)
st.markdown("""<style>
.ph{background:linear-gradient(135deg,#0c1018,#0d1420);border:1px solid #1a2235;border-radius:16px;padding:2.5rem 3rem;margin-bottom:2rem;position:relative;overflow:hidden}
.ph::before{content:'';position:absolute;bottom:-40px;right:-60px;width:200px;height:200px;background:radial-gradient(circle,rgba(77,166,255,0.07),transparent 70%);pointer-events:none}
.ph h1{font-family:'Bebas Neue',sans-serif;font-size:3.5rem;letter-spacing:0.05em;line-height:1;margin:0 0 0.5rem 0}
.ph p{font-family:'IBM Plex Mono',monospace;font-size:0.75rem;color:#8896ab;line-height:1.8;margin:0}
.ph-ey{font-family:'IBM Plex Mono',monospace;font-size:0.55rem;text-transform:uppercase;letter-spacing:0.3em;color:#3a4a5e;margin-bottom:0.5rem}
.sec-t{font-family:'IBM Plex Mono',monospace;font-size:0.55rem;text-transform:uppercase;letter-spacing:0.25em;color:#3a4a5e;padding:1.2rem 0 0.8rem;border-top:1px solid #0d1117}
.bm{background:#0c1018;border:1px solid #1a2235;border-radius:12px;padding:1.5rem 1.8rem;transition:border-color 0.2s}
.bm:hover{border-color:#2a3550}
.bm-v{font-family:'Bebas Neue',sans-serif;font-size:2.4rem;letter-spacing:0.04em;line-height:1}
.bm-l{font-family:'IBM Plex Mono',monospace;font-size:0.5rem;text-transform:uppercase;letter-spacing:0.22em;color:#3a4a5e;margin-top:0.35rem}
.bm-s{font-family:'IBM Plex Mono',monospace;font-size:0.62rem;color:#8896ab;margin-top:0.15rem}
.explain-card{background:#0c1018;border:1px solid #1a2235;border-radius:12px;padding:1.4rem 1.6rem}
.explain-title{font-family:'IBM Plex Mono',monospace;font-size:0.55rem;text-transform:uppercase;letter-spacing:0.2em;color:#4da6ff;margin-bottom:0.6rem}
.explain-body{font-family:'IBM Plex Mono',monospace;font-size:0.7rem;color:#8896ab;line-height:1.8}
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

st.markdown("""<div class="ph"><div class="ph-ey">Probabilistic Modelling</div><h1>Monte Carlo Simulation</h1>
<p>Run 1,000 random paths of where the price could go — based on real historical volatility. Not a prediction. A probability cone. Understand the range of outcomes before you hold through a move.</p></div>""", unsafe_allow_html=True)

m1, m2, m3, m4 = st.columns([2, 1.5, 1.5, 1.5])
with m1: ticker   = st.text_input("Ticker", value="AAPL", placeholder="AAPL, TSLA, BTC-USD").upper().strip()
with m2: horizon  = st.selectbox("Forecast Horizon", ["30 days","60 days","90 days","180 days","1 year"], index=2)
with m3: n_sims   = st.selectbox("Simulations", [500, 1000, 2000], index=1)
with m4: hist_per = st.selectbox("Volatility Basis", ["3 months","6 months","1 year","2 years"], index=2)

run_btn = st.button("Run Simulation", type="primary")

if not run_btn:
    st.markdown('<div class="sec-t">How This Works</div>', unsafe_allow_html=True)
    e1, e2, e3 = st.columns(3)
    for col, (title, color, body) in zip([e1,e2,e3], [
        ("The Math", "#4da6ff", "Each path uses Geometric Brownian Motion: S(t+1) = S(t) x exp((mu - sigma^2/2) x dt + sigma x sqrt(dt) x Z) where Z is a standard normal random draw. 1,000 independent paths are simulated from today's price."),
        ("Reading the Cone", "#00e676", "The dark band = 50% of paths. Medium band = 80%. Outer band = 95%. If the cone is very wide, volatility is high and outcomes are uncertain. If narrow, the stock is stable and moves are predictable."),
        ("Important Caveat", "#ffd166", "This assumes constant volatility and log-normal returns — both simplifications. Real markets have fat tails, regime shifts, and black swan events not captured here. Use this to understand the range of outcomes, not as a forecast."),
    ]):
        col.markdown(f'<div class="explain-card"><div class="explain-title" style="color:{color}">{title}</div><div class="explain-body">{body}</div></div>', unsafe_allow_html=True)
    st.stop()

hist_days = {"3 months":90,"6 months":180,"1 year":365,"2 years":730}[hist_per]
fore_days = {"30 days":30,"60 days":60,"90 days":90,"180 days":180,"1 year":252}[horizon]

with st.spinner(f"Fetching {ticker} data and running {n_sims:,} simulations..."):
    try:
        df = yf.download(ticker, start=str(date.today()-timedelta(days=hist_days+10)),
                         end=str(date.today()), progress=False, auto_adjust=True)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        if df.empty or len(df) < 20: st.error("Not enough data."); st.stop()

        close = df["Close"].squeeze()
        log_returns = np.log(close/close.shift(1)).dropna()
        mu    = log_returns.mean()
        sigma = log_returns.std()
        S0    = float(close.iloc[-1])

        np.random.seed(42)
        dt = 1
        paths = np.zeros((fore_days, n_sims))
        paths[0] = S0
        for t in range(1, fore_days):
            Z = np.random.standard_normal(n_sims)
            paths[t] = paths[t-1] * np.exp((mu - 0.5*sigma**2)*dt + sigma*np.sqrt(dt)*Z)

        pct_5  = np.percentile(paths, 5,  axis=1)
        pct_10 = np.percentile(paths, 10, axis=1)
        pct_25 = np.percentile(paths, 25, axis=1)
        pct_50 = np.percentile(paths, 50, axis=1)
        pct_75 = np.percentile(paths, 75, axis=1)
        pct_90 = np.percentile(paths, 90, axis=1)
        pct_95 = np.percentile(paths, 95, axis=1)

        final_prices  = paths[-1]
        prob_up       = (final_prices > S0).mean() * 100
        prob_up_10    = (final_prices > S0*1.1).mean() * 100
        prob_down_10  = (final_prices < S0*0.9).mean() * 100
        expected_ret  = (pct_50[-1]/S0 - 1) * 100
        annualized_vol = sigma * np.sqrt(252) * 100

    except Exception as e: st.error(f"Error: {e}"); st.stop()

# Metrics
st.markdown('<div class="sec-t">Simulation Summary</div>', unsafe_allow_html=True)
r1 = st.columns(4)
r2 = st.columns(4)
for col,(v,l,s,c) in zip(r1,[
    (f"${S0:.2f}", "Current Price", ticker, "#eef2f7"),
    (f"{annualized_vol:.1f}%", "Annualised Vol", f"based on {hist_per}", "#ffd166"),
    (f"{prob_up:.0f}%", "Prob Price Up", f"at {fore_days} days", "#00e676"),
    (f"{expected_ret:+.1f}%", "Median Return", f"in {fore_days} days", "#00e676" if expected_ret>=0 else "#ff3d57"),
]): col.markdown(f'<div class="bm"><div class="bm-v" style="color:{c}">{v}</div><div class="bm-l">{l}</div><div class="bm-s">{s}</div></div>', unsafe_allow_html=True)
for col,(v,l,s,c) in zip(r2,[
    (f"${pct_5[-1]:.2f}", "5th Percentile", "worst 5% of paths", "#ff3d57"),
    (f"${pct_25[-1]:.2f}", "25th Percentile", "lower quartile", "#ff9f43"),
    (f"${pct_75[-1]:.2f}", "75th Percentile", "upper quartile", "#4da6ff"),
    (f"${pct_95[-1]:.2f}", "95th Percentile", "best 5% of paths", "#00e676"),
]): col.markdown(f'<div class="bm"><div class="bm-v" style="color:{c}">{v}</div><div class="bm-l">{l}</div><div class="bm-s">{s}</div></div>', unsafe_allow_html=True)

# Monte Carlo cone chart
x_days = list(range(fore_days))
fig = go.Figure()

# Sample 80 individual paths for visual texture
sample_n = min(80, n_sims)
for i in range(sample_n):
    fig.add_scatter(x=x_days, y=paths[:,i],
                   mode="lines", line=dict(color="rgba(77,166,255,0.04)", width=0.8),
                   showlegend=False, hoverinfo="skip")

# Cone bands
fig.add_scatter(x=x_days+x_days[::-1], y=list(pct_5)+list(pct_95)[::-1],
               fill="toself", fillcolor="rgba(0,230,118,0.04)",
               line=dict(color="rgba(0,0,0,0)"), name="5–95%", showlegend=True)
fig.add_scatter(x=x_days+x_days[::-1], y=list(pct_10)+list(pct_90)[::-1],
               fill="toself", fillcolor="rgba(0,230,118,0.07)",
               line=dict(color="rgba(0,0,0,0)"), name="10–90%", showlegend=True)
fig.add_scatter(x=x_days+x_days[::-1], y=list(pct_25)+list(pct_75)[::-1],
               fill="toself", fillcolor="rgba(0,230,118,0.12)",
               line=dict(color="rgba(0,0,0,0)"), name="25–75%", showlegend=True)

# Median path
fig.add_scatter(x=x_days, y=pct_50, line=dict(color="#00e676", width=2.5),
               name="Median (50th pct)", showlegend=True)

# Current price line
fig.add_hline(y=S0, line_dash="dash", line_color="#ffd166",
              annotation_text=f"Today ${S0:.2f}", annotation_font_size=11)

fig.update_layout(**PLOTLY_THEME, height=460,
                  title=f"{ticker} — {n_sims:,} Simulations over {fore_days} Days",
                  xaxis_title="Days from Today", yaxis_title="Price ($)",
                  legend=dict(font=dict(family="IBM Plex Mono", size=10)))
st.plotly_chart(fig, use_container_width=True)

# Final price distribution
st.markdown('<div class="sec-t">Final Price Distribution</div>', unsafe_allow_html=True)
fig2 = go.Figure()
fig2.add_histogram(x=final_prices, nbinsx=60,
                   marker_color="#4da6ff", marker_line=dict(width=0.3, color="#06080c"),
                   name="Final Price")
fig2.add_vline(x=S0,         line_dash="dash", line_color="#ffd166", annotation_text=f"Today ${S0:.2f}")
fig2.add_vline(x=pct_50[-1], line_dash="dash", line_color="#00e676", annotation_text=f"Median ${pct_50[-1]:.2f}")
fig2.update_layout(**PLOTLY_THEME, height=280,
                   title=f"Distribution of {ticker} Price After {fore_days} Days",
                   xaxis_title="Final Price ($)", yaxis_title="Path Count", showlegend=False)
st.plotly_chart(fig2, use_container_width=True)
