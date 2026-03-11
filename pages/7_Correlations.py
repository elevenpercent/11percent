import streamlit as st
import sys, os
import pandas as pd
import numpy as np
from datetime import date, timedelta
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.styles import SHARED_CSS
from utils.nav import navbar

st.set_page_config(page_title="Correlations | 11%", layout="wide", initial_sidebar_state="collapsed")
st.markdown(SHARED_CSS, unsafe_allow_html=True)
navbar()

st.markdown("""
<div class="page-header">
    <div class="page-header-eyebrow">Statistical Analysis <span class="beta-badge">Beta</span></div>
    <h1>Correlation Matrix</h1>
    <p>See how assets move together. Bright green = move in sync. Deep red = move opposite. Diversification means low correlation.</p>
</div>
""", unsafe_allow_html=True)

# ── Presets ────────────────────────────────────────────────────────────────────
PRESETS = {
    "Tech + Macro":    ["AAPL","MSFT","NVDA","GOOGL","META","SPY","QQQ","TLT","GLD","BTC-USD"],
    "Mag 7":           ["AAPL","MSFT","NVDA","GOOGL","META","AMZN","TSLA","SPY","QQQ","VIX"],
    "Crypto":          ["BTC-USD","ETH-USD","SOL-USD","BNB-USD","XRP-USD","DOGE-USD","ADA-USD","AVAX-USD","MATIC-USD","LINK-USD"],
    "Sectors":         ["XLK","XLF","XLV","XLE","XLI","XLC","XLY","XLP","XLB","XLRE"],
    "Custom":          [],
}

p1, p2, p3 = st.columns([1.5, 1.5, 1])
with p1:
    preset = st.selectbox("Preset", list(PRESETS.keys()), key="corr_preset")
with p2:
    period = st.selectbox("Period", ["3 months","6 months","1 year","2 years","3 years"], index=2, key="corr_period")
with p3:
    st.markdown("<div style='height:1.75rem'></div>", unsafe_allow_html=True)
    run_btn = st.button("Build Matrix", type="primary", key="corr_run")

if preset == "Custom":
    raw = st.text_input("Tickers (comma-separated)", value="AAPL, TSLA, SPY, BTC-USD, GLD", key="corr_custom")
    tickers = [t.strip().upper() for t in raw.split(",") if t.strip()][:12]
else:
    tickers = PRESETS[preset]

# Preview chips
chips = "".join(f'<span style="display:inline-block;font-family:IBM Plex Mono,monospace;font-size:0.62rem;padding:3px 10px;background:#0d1117;border:1px solid #1a2235;border-radius:4px;color:#8892a4;margin:2px;">{t}</span>' for t in tickers)
st.markdown(f'<div style="margin:0.6rem 0 1rem 0;">{chips}</div>', unsafe_allow_html=True)

if not run_btn:
    st.markdown("""
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;margin-top:1.5rem;">
        <div class="panel-sm">
            <div style="font-family:'IBM Plex Mono',monospace;font-size:0.6rem;color:#00e676;text-transform:uppercase;letter-spacing:0.14em;margin-bottom:0.5rem;">What is correlation?</div>
            <div style="font-size:0.82rem;color:#8892a4;line-height:1.65;">Pearson correlation measures how two assets move together. +1.0 = perfectly in sync. -1.0 = perfectly opposite. 0 = no relationship.</div>
        </div>
        <div class="panel-sm">
            <div style="font-family:'IBM Plex Mono',monospace;font-size:0.6rem;color:#00e676;text-transform:uppercase;letter-spacing:0.14em;margin-bottom:0.5rem;">Why it matters</div>
            <div style="font-size:0.82rem;color:#8892a4;line-height:1.65;">If your portfolio is all highly correlated assets (all tech stocks), a single market shock hits everything at once. Low correlation = true diversification.</div>
        </div>
        <div class="panel-sm">
            <div style="font-family:'IBM Plex Mono',monospace;font-size:0.6rem;color:#00e676;text-transform:uppercase;letter-spacing:0.14em;margin-bottom:0.5rem;">How to read the grid</div>
            <div style="font-size:0.82rem;color:#8892a4;line-height:1.65;">The diagonal is always 1.0 (an asset is perfectly correlated with itself). Focus on off-diagonal squares — especially surprising highs and lows.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── Fetch data ──────────────────────────────────────────────────────────────
period_days = {"3 months":90,"6 months":180,"1 year":365,"2 years":730,"3 years":1095}[period]
start = str(date.today() - timedelta(days=period_days))
end   = str(date.today())

import yfinance as yf
with st.spinner(f"Fetching {len(tickers)} assets…"):
    price_data = {}
    failed = []
    for t in tickers:
        try:
            df = yf.download(t, start=start, end=end, progress=False, auto_adjust=True)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            if not df.empty and "Close" in df.columns:
                price_data[t] = df["Close"].dropna()
            else:
                failed.append(t)
        except:
            failed.append(t)

if failed:
    st.markdown(f'<div class="warn-box">Could not load: {", ".join(failed)}</div>', unsafe_allow_html=True)

if len(price_data) < 2:
    st.error("Need at least 2 assets with data."); st.stop()

# Build returns matrix
prices_df = pd.DataFrame(price_data).dropna()
returns   = prices_df.pct_change().dropna()
corr_matrix = returns.corr()
labels = list(corr_matrix.columns)
n = len(labels)

# ── Render heat map as styled HTML ────────────────────────────────────────────
def corr_color(v):
    """Return background and text color for a correlation value."""
    if v >= 0.8:   return "#00e676", "#000"
    if v >= 0.5:   return "#00b856", "#000"
    if v >= 0.2:   return "#1a3a2a", "#8896ab"
    if v >= -0.2:  return "#101520", "#8896ab"
    if v >= -0.5:  return "#3a1a20", "#8896ab"
    if v >= -0.8:  return "#b83040", "#fff"
    return "#ff3d57", "#000"

cell_size = max(52, int(560 / n))
font_size  = max(9, int(cell_size * 0.22))
lbl_size   = max(9, int(cell_size * 0.18))

# Header row
html = '<div style="overflow-x:auto;margin:1.5rem 0;">'
html += f'<table style="border-collapse:collapse;font-family:IBM Plex Mono,monospace;">'

# Column labels
html += '<tr><td style="padding:0;"></td>'
for lbl in labels:
    html += f'<td style="padding:2px;text-align:center;font-size:{lbl_size}px;color:#8896ab;white-space:nowrap;max-width:{cell_size}px;overflow:hidden;text-overflow:ellipsis;">{lbl}</td>'
html += '</tr>'

# Data rows
for row_lbl in labels:
    html += f'<tr><td style="padding:2px;font-size:{lbl_size}px;color:#8896ab;white-space:nowrap;padding-right:6px;text-align:right;">{row_lbl}</td>'
    for col_lbl in labels:
        v = corr_matrix.loc[row_lbl, col_lbl]
        bg, fg = corr_color(v)
        is_diag = row_lbl == col_lbl
        border = "1px solid #2a3550" if is_diag else "1px solid #1a2235"
        glow = f"box-shadow:0 0 8px {bg}60;" if v >= 0.8 and not is_diag else ""
        html += (
            f'<td style="width:{cell_size}px;height:{cell_size}px;text-align:center;'
            f'background:{bg};color:{fg};font-size:{font_size}px;font-weight:600;'
            f'border:{border};border-radius:3px;{glow}">'
            f'{v:.2f}</td>'
        )
    html += '</tr>'

html += '</table></div>'
st.markdown(html, unsafe_allow_html=True)

# ── Legend ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="display:flex;gap:0.5rem;align-items:center;flex-wrap:wrap;margin:0.5rem 0 1.5rem 0;font-family:'IBM Plex Mono',monospace;font-size:0.62rem;">
    <span style="color:#8896ab;margin-right:0.5rem;">Correlation:</span>
    <span style="background:#ff3d57;color:#000;padding:2px 10px;border-radius:3px;">≤ −0.8</span>
    <span style="background:#b83040;color:#fff;padding:2px 10px;border-radius:3px;">−0.5</span>
    <span style="background:#3a1a20;color:#8896ab;padding:2px 10px;border-radius:3px;">−0.2</span>
    <span style="background:#101520;color:#8896ab;padding:2px 10px;border-radius:3px;">0</span>
    <span style="background:#1a3a2a;color:#8896ab;padding:2px 10px;border-radius:3px;">+0.2</span>
    <span style="background:#00b856;color:#000;padding:2px 10px;border-radius:3px;">+0.5</span>
    <span style="background:#00e676;color:#000;padding:2px 10px;border-radius:3px;">≥ +0.8</span>
</div>
""", unsafe_allow_html=True)

# ── Insights ──────────────────────────────────────────────────────────────────
st.markdown('<div class="section-hdr"><div class="section-hdr-label">Key Insights</div></div>', unsafe_allow_html=True)

pairs = []
for i, a in enumerate(labels):
    for j, b in enumerate(labels):
        if j > i:
            pairs.append((a, b, corr_matrix.loc[a, b]))

pairs.sort(key=lambda x: abs(x[2]), reverse=True)

ins1, ins2 = st.columns(2)
with ins1:
    st.markdown('<div style="font-family:IBM Plex Mono,monospace;font-size:0.58rem;color:#3a4558;text-transform:uppercase;letter-spacing:0.18em;margin-bottom:0.8rem;">Highest Correlation (move together)</div>', unsafe_allow_html=True)
    for a, b, v in [(p for p in pairs if p[2] > 0)][:5] if any(p[2] > 0 for p in pairs) else []:
        bar_w = int(abs(v) * 100)
        color = "#00e676" if v > 0 else "#ff3d57"
        st.markdown(f"""
        <div style="margin-bottom:0.6rem;">
            <div style="display:flex;justify-content:space-between;font-size:0.78rem;margin-bottom:3px;">
                <span style="color:#eef2f7;">{a} <span style="color:#3a4558;">vs</span> {b}</span>
                <span style="color:{color};font-weight:600;">{v:+.3f}</span>
            </div>
            <div class="progress-track"><div class="progress-fill" style="width:{bar_w}%;background:{color};"></div></div>
        </div>
        """, unsafe_allow_html=True)

with ins2:
    st.markdown('<div style="font-family:IBM Plex Mono,monospace;font-size:0.58rem;color:#3a4558;text-transform:uppercase;letter-spacing:0.18em;margin-bottom:0.8rem;">Lowest Correlation (best diversifiers)</div>', unsafe_allow_html=True)
    low_pairs = sorted(pairs, key=lambda x: x[2])[:5]
    for a, b, v in low_pairs:
        bar_w = int(abs(v) * 100)
        color = "#00e676" if v > 0 else "#ff3d57"
        st.markdown(f"""
        <div style="margin-bottom:0.6rem;">
            <div style="display:flex;justify-content:space-between;font-size:0.78rem;margin-bottom:3px;">
                <span style="color:#eef2f7;">{a} <span style="color:#3a4558;">vs</span> {b}</span>
                <span style="color:{color};font-weight:600;">{v:+.3f}</span>
            </div>
            <div class="progress-track"><div class="progress-fill" style="width:{bar_w}%;background:{color};"></div></div>
        </div>
        """, unsafe_allow_html=True)

# Summary stats
avg_corr = np.mean([p[2] for p in pairs])
st.markdown(f"""
<div class="stat-strip" style="margin-top:1rem;">
    <div class="stat-cell"><div class="stat-val {'pos' if avg_corr < 0.4 else 'neg'}">{avg_corr:.3f}</div><div class="stat-lbl">Avg Correlation</div></div>
    <div class="stat-cell"><div class="stat-val neu">{len(labels)}</div><div class="stat-lbl">Assets</div></div>
    <div class="stat-cell"><div class="stat-val neu">{len(prices_df)}</div><div class="stat-lbl">Trading Days</div></div>
    <div class="stat-cell"><div class="stat-val {'pos' if avg_corr < 0.4 else 'neg'}">{"Well diversified" if avg_corr < 0.4 else ("Moderate" if avg_corr < 0.65 else "Highly correlated")}</div><div class="stat-lbl">Portfolio Assessment</div></div>
</div>
""", unsafe_allow_html=True)
