import streamlit as st
import sys, os
import pandas as pd
import numpy as np
from datetime import date, timedelta
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.styles import SHARED_CSS
from utils.nav import navbar

st.set_page_config(page_title="Monte Carlo | 11%", layout="wide", initial_sidebar_state="collapsed")
st.markdown(SHARED_CSS, unsafe_allow_html=True)
navbar()

st.markdown("""
<div class="page-header">
    <div class="page-header-eyebrow">Probabilistic Modelling <span class="beta-badge">Beta</span></div>
    <h1>Monte Carlo Projection</h1>
    <p>1,000 random simulations of where the price <em>could</em> go — based on current volatility. Not a prediction. A probability cone.</p>
</div>
""", unsafe_allow_html=True)

# ── Controls ───────────────────────────────────────────────────────────────────
m1, m2, m3, m4, m5 = st.columns([1.5, 1, 1, 1, 1])
with m1: ticker   = st.text_input("Ticker", value="AAPL", key="mc_ticker").upper().strip()
with m2: horizon  = st.selectbox("Forecast", ["30 days","60 days","90 days","180 days","1 year"], index=2, key="mc_horizon")
with m3: n_sims   = st.selectbox("Simulations", [500, 1000, 2000], index=1, key="mc_sims")
with m4: hist_per = st.selectbox("Volatility basis", ["3 months","6 months","1 year","2 years"], index=2, key="mc_hist")
with m5:
    st.markdown("<div style='height:1.75rem'></div>", unsafe_allow_html=True)
    run_btn = st.button("Run Simulation", type="primary", key="mc_run")

if not run_btn:
    st.markdown("""
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;margin-top:1.5rem;">
        <div class="panel-sm">
            <div style="font-family:'IBM Plex Mono',monospace;font-size:0.6rem;color:#4da6ff;text-transform:uppercase;letter-spacing:0.14em;margin-bottom:0.5rem;">The math</div>
            <div style="font-size:0.82rem;color:#8896ab;line-height:1.65;">Each path uses Geometric Brownian Motion: S(t+1) = S(t) × exp((μ − σ²/2)Δt + σ√Δt × Z) where Z is a random draw from a normal distribution.</div>
        </div>
        <div class="panel-sm">
            <div style="font-family:'IBM Plex Mono',monospace;font-size:0.6rem;color:#4da6ff;text-transform:uppercase;letter-spacing:0.14em;margin-bottom:0.5rem;">What the cone means</div>
            <div style="font-size:0.82rem;color:#8896ab;line-height:1.65;">The shaded bands show where 50%, 80%, and 95% of all simulated paths end up. Wide cone = high volatility = high uncertainty.</div>
        </div>
        <div class="panel-sm">
            <div style="font-family:'IBM Plex Mono',monospace;font-size:0.6rem;color:#4da6ff;text-transform:uppercase;letter-spacing:0.14em;margin-bottom:0.5rem;">Important caveat</div>
            <div style="font-size:0.82rem;color:#8896ab;line-height:1.65;">This assumes log-normal returns and constant volatility — both simplifications. Real markets have fat tails, regime changes, and black swans not captured here.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── Fetch historical data ──────────────────────────────────────────────────────
hist_days = {"3 months":90,"6 months":180,"1 year":365,"2 years":730}[hist_per]
fore_days = {"30 days":30,"60 days":60,"90 days":90,"180 days":180,"1 year":252}[horizon]

import yfinance as yf
with st.spinner(f"Fetching {ticker} history…"):
    try:
        df = yf.download(ticker, start=str(date.today()-timedelta(days=hist_days+10)),
                         end=str(date.today()), progress=False, auto_adjust=True)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df = df.dropna()
    except Exception as e:
        st.error(f"Could not fetch {ticker}: {e}"); st.stop()

if df.empty or len(df) < 20:
    st.error(f"Not enough data for {ticker}."); st.stop()

closes  = df["Close"].astype(float)
log_ret = np.log(closes / closes.shift(1)).dropna()

# Parameters
mu    = float(log_ret.mean())         # daily drift
sigma = float(log_ret.std())          # daily volatility
S0    = float(closes.iloc[-1])        # last known price
dt    = 1.0                            # 1 trading day

# ── Monte Carlo simulation ─────────────────────────────────────────────────────
np.random.seed(42)
with st.spinner(f"Running {n_sims:,} simulations…"):
    Z       = np.random.standard_normal((fore_days, n_sims))
    drift   = (mu - 0.5 * sigma**2) * dt
    diffuse = sigma * np.sqrt(dt) * Z
    daily   = np.exp(drift + diffuse)

    paths = np.zeros((fore_days + 1, n_sims))
    paths[0] = S0
    for t in range(1, fore_days + 1):
        paths[t] = paths[t-1] * daily[t-1]

# ── Statistics ─────────────────────────────────────────────────────────────────
final_prices = paths[-1]
p5   = np.percentile(final_prices, 5)
p10  = np.percentile(final_prices, 10)
p25  = np.percentile(final_prices, 25)
p50  = np.percentile(final_prices, 50)   # median
p75  = np.percentile(final_prices, 75)
p90  = np.percentile(final_prices, 90)
p95  = np.percentile(final_prices, 95)

prob_up   = float(np.mean(final_prices > S0) * 100)
prob_10up = float(np.mean(final_prices > S0 * 1.10) * 100)
prob_20up = float(np.mean(final_prices > S0 * 1.20) * 100)
prob_10dn = float(np.mean(final_prices < S0 * 0.90) * 100)
prob_20dn = float(np.mean(final_prices < S0 * 0.80) * 100)
ann_vol   = sigma * np.sqrt(252) * 100

# ── Stat strip ─────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="stat-strip" style="margin-top:1rem;">
    <div class="stat-cell"><div class="stat-val neu">${S0:,.2f}</div><div class="stat-lbl">Current Price</div></div>
    <div class="stat-cell"><div class="stat-val neu">${p50:,.2f}</div><div class="stat-lbl">Median Target ({horizon})</div></div>
    <div class="stat-cell"><div class="stat-val {'pos' if prob_up>=50 else 'neg'}">{prob_up:.1f}%</div><div class="stat-lbl">Prob Higher</div></div>
    <div class="stat-cell"><div class="stat-val neu">{ann_vol:.1f}%</div><div class="stat-lbl">Ann. Volatility</div></div>
    <div class="stat-cell"><div class="stat-val neu">{n_sims:,}</div><div class="stat-lbl">Simulations</div></div>
</div>
""", unsafe_allow_html=True)

# ── Plotly chart ───────────────────────────────────────────────────────────────
import plotly.graph_objects as go

fig = go.Figure()

# Historical prices
hist_x = list(range(-len(closes), 0))
fig.add_trace(go.Scatter(
    x=hist_x, y=closes.values,
    mode="lines", name="Historical",
    line=dict(color="#8896ab", width=1.5),
))

# Forecast x axis
fore_x = list(range(0, fore_days + 1))

# Cone bands
pcts = [(2.5, 97.5, "rgba(77,166,255,0.06)", "95% range"),
        (10,  90,   "rgba(77,166,255,0.09)", "80% range"),
        (25,  75,   "rgba(77,166,255,0.14)", "50% range")]

for lo, hi, color, name in pcts:
    lo_band = np.percentile(paths, lo, axis=1)
    hi_band = np.percentile(paths, hi, axis=1)
    fig.add_trace(go.Scatter(
        x=fore_x + fore_x[::-1],
        y=list(hi_band) + list(lo_band[::-1]),
        fill="toself", fillcolor=color,
        line=dict(width=0), name=name, hoverinfo="skip",
    ))

# Sample paths (faint)
sample_idx = np.random.choice(n_sims, min(80, n_sims), replace=False)
for i in sample_idx:
    fig.add_trace(go.Scatter(
        x=fore_x, y=paths[:, i],
        mode="lines", line=dict(color="rgba(77,166,255,0.06)", width=0.5),
        showlegend=False, hoverinfo="skip",
    ))

# Median path
fig.add_trace(go.Scatter(
    x=fore_x, y=np.percentile(paths, 50, axis=1),
    mode="lines", name="Median path",
    line=dict(color="#4da6ff", width=2, dash="dot"),
))

# Percentile boundary lines
for pct_val, label, color in [(p5,"5th %ile","#ff3d57"),(p95,"95th %ile","#00e676")]:
    fig.add_hline(y=pct_val, line_dash="dot", line_color=color, line_width=1,
                  annotation_text=f"{label}: ${pct_val:,.2f}", annotation_position="right",
                  annotation_font_color=color, annotation_font_size=10)

# Current price line
fig.add_hline(y=S0, line_dash="dash", line_color="#ffd166", line_width=1,
              annotation_text=f"Now: ${S0:,.2f}", annotation_position="right",
              annotation_font_color="#ffd166", annotation_font_size=10)

# Divider at day 0
fig.add_vline(x=0, line_dash="solid", line_color="#2a3550", line_width=1)

fig.update_layout(
    title=dict(text=f"{ticker} — Monte Carlo ({n_sims:,} paths, {horizon})", font=dict(size=13, color="#8896ab")),
    paper_bgcolor="#06080c", plot_bgcolor="#06080c",
    font=dict(family="IBM Plex Mono", color="#8896ab", size=11),
    xaxis=dict(gridcolor="#1a2235", linecolor="#1a2235", zeroline=False,
               title="Days (negative = historical, positive = simulated)"),
    yaxis=dict(gridcolor="#1a2235", linecolor="#1a2235", zeroline=False,
               title="Price ($)", tickformat="$,.0f"),
    legend=dict(bgcolor="#0c1018", bordercolor="#1a2235", borderwidth=1),
    margin=dict(l=20, r=120, t=50, b=40),
    height=520,
)

st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# ── Probability table ──────────────────────────────────────────────────────────
prob_col, dist_col = st.columns(2)

with prob_col:
    st.markdown('<div class="section-hdr"><div class="section-hdr-label">Probability Outcomes</div></div>', unsafe_allow_html=True)
    scenarios = [
        (f"Price above ${S0*1.20:,.0f} (+20%)", prob_20up, "#00e676"),
        (f"Price above ${S0*1.10:,.0f} (+10%)", prob_10up, "#00b856"),
        (f"Price above current ${S0:,.0f}",       prob_up,   "#8896ab"),
        (f"Price below ${S0*0.90:,.0f} (−10%)", prob_10dn, "#ff9f43"),
        (f"Price below ${S0*0.80:,.0f} (−20%)", prob_20dn, "#ff3d57"),
    ]
    for label, prob, color in scenarios:
        bar_w = int(prob)
        st.markdown(f"""
        <div style="margin-bottom:0.8rem;">
            <div style="display:flex;justify-content:space-between;font-family:'IBM Plex Mono',monospace;font-size:0.74rem;margin-bottom:4px;">
                <span style="color:#8896ab;">{label}</span>
                <span style="color:{color};font-weight:700;">{prob:.1f}%</span>
            </div>
            <div class="progress-track"><div class="progress-fill" style="width:{bar_w}%;background:{color};"></div></div>
        </div>
        """, unsafe_allow_html=True)

with dist_col:
    st.markdown('<div class="section-hdr"><div class="section-hdr-label">Price Distribution at End of Period</div></div>', unsafe_allow_html=True)

    buckets = [
        ("5th %ile (bear case)",  p5,  "#ff3d57"),
        ("10th %ile",             p10, "#ff9f43"),
        ("25th %ile",             p25, "#ffd166"),
        ("Median (50th %ile)",    p50, "#8896ab"),
        ("75th %ile",             p75, "#4da6ff"),
        ("90th %ile",             p90, "#00b856"),
        ("95th %ile (bull case)", p95, "#00e676"),
    ]
    for label, price, color in buckets:
        chg = (price - S0) / S0 * 100
        chg_color = "#00e676" if chg >= 0 else "#ff3d57"
        st.markdown(f"""
        <div style="display:flex;justify-content:space-between;align-items:center;padding:0.45rem 0;border-bottom:1px solid #0d1117;font-family:'IBM Plex Mono',monospace;font-size:0.74rem;">
            <span style="color:{color};">◆</span>
            <span style="color:#8896ab;flex:1;margin:0 0.8rem;">{label}</span>
            <span style="color:#eef2f7;font-weight:600;">${price:,.2f}</span>
            <span style="color:{chg_color};margin-left:0.8rem;min-width:60px;text-align:right;">{chg:+.1f}%</span>
        </div>
        """, unsafe_allow_html=True)

# ── Methodology note ──────────────────────────────────────────────────────────
st.markdown(f"""
<div style="margin-top:1.5rem;padding:1rem;background:#0a0d0f;border:1px solid #1a2235;border-radius:8px;font-family:'IBM Plex Mono',monospace;font-size:0.72rem;color:#3a4558;line-height:1.8;">
    <span style="color:#4da6ff;">Model:</span> Geometric Brownian Motion &nbsp;·&nbsp;
    <span style="color:#4da6ff;">μ (daily drift):</span> {mu*100:.4f}% &nbsp;·&nbsp;
    <span style="color:#4da6ff;">σ (daily vol):</span> {sigma*100:.3f}% ({ann_vol:.1f}% annualised) &nbsp;·&nbsp;
    <span style="color:#4da6ff;">Based on:</span> {len(log_ret)} trading days of {ticker} &nbsp;·&nbsp;
    <span style="color:#ff3d57;">Not financial advice.</span>
</div>
""", unsafe_allow_html=True)
