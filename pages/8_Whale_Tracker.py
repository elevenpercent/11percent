import streamlit as st
import sys, os
import pandas as pd
import numpy as np
from datetime import date, timedelta, datetime
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.styles import SHARED_CSS
from utils.nav import navbar

st.set_page_config(page_title="Whale Tracker | 11%", layout="wide", initial_sidebar_state="collapsed")
st.markdown(SHARED_CSS, unsafe_allow_html=True)
navbar()

st.markdown("""
<style>
@keyframes blinkIn { from{opacity:0;transform:translateX(-8px)} to{opacity:1;transform:translateX(0)} }
.whale-row { animation: blinkIn 0.3s ease both; }
.terminal-feed {
    background:#030508;
    border:1px solid #1a2235;
    border-radius:10px;
    padding:1rem;
    max-height:560px;
    overflow-y:auto;
    font-family:'IBM Plex Mono',monospace;
}
.terminal-hdr {
    background:#08100d;
    border-bottom:1px solid #1a2235;
    padding:0.5rem 1rem;
    display:flex;
    align-items:center;
    gap:0.4rem;
    margin:-1rem -1rem 1rem -1rem;
    border-radius:10px 10px 0 0;
    font-size:0.6rem;
    color:#3a4a5e;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="page-header">
    <div class="page-header-eyebrow">Anomaly Detection <span class="beta-badge">Beta</span></div>
    <h1>Whale Tracker</h1>
    <p>Flags unusual volume spikes — trades that are statistically far above a stock's normal activity. Large orders often precede big moves.</p>
</div>
""", unsafe_allow_html=True)

# ── Controls ───────────────────────────────────────────────────────────────────
w1, w2, w3, w4 = st.columns([2, 1, 1, 1])
with w1:
    raw_tickers = st.text_input("Watch list (comma-separated)", value="AAPL, TSLA, NVDA, MSFT, AMZN, META, GOOGL, AMD, SPY, QQQ", key="wt_tickers")
with w2:
    std_thresh = st.slider("Alert threshold (σ)", 1.0, 4.0, 2.0, step=0.5, key="wt_std",
                           help="How many standard deviations above the 30-day avg volume to flag as unusual")
with w3:
    lookback  = st.selectbox("Lookback", ["30 days","60 days","90 days"], key="wt_look")
with w4:
    st.markdown("<div style='height:1.75rem'></div>", unsafe_allow_html=True)
    scan_btn = st.button("Scan Now", type="primary", key="wt_scan")

tickers = [t.strip().upper() for t in raw_tickers.split(",") if t.strip()][:15]

if not scan_btn:
    st.markdown("""
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;margin-top:1.5rem;">
        <div class="panel-sm">
            <div style="font-family:'IBM Plex Mono',monospace;font-size:0.6rem;color:#b388ff;text-transform:uppercase;letter-spacing:0.14em;margin-bottom:0.5rem;">How it works</div>
            <div style="font-size:0.82rem;color:#8896ab;line-height:1.65;">Calculates each stock's 30-day average volume and standard deviation. Flags any recent day where volume exceeds average + N×σ.</div>
        </div>
        <div class="panel-sm">
            <div style="font-family:'IBM Plex Mono',monospace;font-size:0.6rem;color:#b388ff;text-transform:uppercase;letter-spacing:0.14em;margin-bottom:0.5rem;">Why it matters</div>
            <div style="font-size:0.82rem;color:#8896ab;line-height:1.65;">Unusually large volume often signals institutional activity — earnings speculation, major news, or a large fund building or exiting a position.</div>
        </div>
        <div class="panel-sm">
            <div style="font-family:'IBM Plex Mono',monospace;font-size:0.6rem;color:#b388ff;text-transform:uppercase;letter-spacing:0.14em;margin-bottom:0.5rem;">Data source</div>
            <div style="font-size:0.82rem;color:#8896ab;line-height:1.65;">Daily OHLCV from Yahoo Finance. This shows historical volume anomalies, not real-time intraday order flow. Add your own tickers to the watch list.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── Fetch and scan ─────────────────────────────────────────────────────────────
lb_days = {"30 days":30,"60 days":60,"90 days":90}[lookback]
start   = str(date.today() - timedelta(days=lb_days + 40))
end     = str(date.today())

import yfinance as yf

alerts = []
summaries = {}

with st.spinner(f"Scanning {len(tickers)} symbols…"):
    for ticker in tickers:
        try:
            df = yf.download(ticker, start=start, end=end, progress=False, auto_adjust=True)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            if df.empty or "Volume" not in df.columns or len(df) < 20:
                continue
            df = df.dropna(subset=["Volume","Close"])

            vol = df["Volume"].astype(float)
            closes = df["Close"].astype(float)

            # Rolling 30-day stats for baseline
            roll_mean = vol.rolling(30).mean()
            roll_std  = vol.rolling(30).std()

            # Look at last lb_days rows for anomalies
            scan_df = df.iloc[-lb_days:].copy()
            scan_vol  = vol.iloc[-lb_days:]
            scan_mean = roll_mean.iloc[-lb_days:]
            scan_std  = roll_std.iloc[-lb_days:]

            z_scores = (scan_vol - scan_mean) / (scan_std + 1)

            # Daily price change
            pct_chg = closes.pct_change() * 100

            avg_vol = vol.rolling(30).mean().iloc[-1]
            summaries[ticker] = {
                "avg_vol": avg_vol,
                "last_vol": float(vol.iloc[-1]),
                "last_price": float(closes.iloc[-1]),
                "last_pct": float(pct_chg.iloc[-1]),
            }

            for idx in scan_df.index:
                z = float(z_scores.loc[idx]) if idx in z_scores.index else 0
                if z >= std_thresh:
                    day_vol  = float(vol.loc[idx])
                    day_cls  = float(closes.loc[idx])
                    day_pct  = float(pct_chg.loc[idx]) if idx in pct_chg.index else 0
                    base_avg = float(scan_mean.loc[idx]) if idx in scan_mean.index else avg_vol
                    mult     = day_vol / base_avg if base_avg > 0 else 0
                    alerts.append({
                        "date":    idx,
                        "ticker":  ticker,
                        "volume":  day_vol,
                        "avg_vol": base_avg,
                        "mult":    mult,
                        "z":       z,
                        "price":   day_cls,
                        "pct":     day_pct,
                    })
        except Exception:
            continue

alerts.sort(key=lambda x: (x["date"], x["z"]), reverse=True)

# ── Summary stat strip ────────────────────────────────────────────────────────
st.markdown(f"""
<div class="stat-strip">
    <div class="stat-cell"><div class="stat-val {'pos' if len(alerts)>0 else 'neu'}">{len(alerts)}</div><div class="stat-lbl">Alerts Found</div></div>
    <div class="stat-cell"><div class="stat-val neu">{len(tickers)}</div><div class="stat-lbl">Symbols Scanned</div></div>
    <div class="stat-cell"><div class="stat-val neu">{std_thresh:.1f}σ</div><div class="stat-lbl">Threshold</div></div>
    <div class="stat-cell"><div class="stat-val neu">{lookback}</div><div class="stat-lbl">Window</div></div>
</div>
""", unsafe_allow_html=True)

feed_col, info_col = st.columns([2, 1])

with feed_col:
    # Terminal feed
    if not alerts:
        st.markdown(f"""
        <div style="background:#030508;border:1px solid #1a2235;border-radius:10px;overflow:hidden;">
            <div style="background:#08100d;border-bottom:1px solid #1a2235;padding:0.5rem 1rem;display:flex;align-items:center;gap:0.5rem;font-family:'IBM Plex Mono',monospace;font-size:0.6rem;color:#3a4a5e;">
                <div style="width:8px;height:8px;border-radius:50%;background:#ff3d57;flex-shrink:0;"></div>
                <div style="width:8px;height:8px;border-radius:50%;background:#ffd166;flex-shrink:0;"></div>
                <div style="width:8px;height:8px;border-radius:50%;background:#00e676;flex-shrink:0;"></div>
                <span style="margin-left:0.5rem;">WHALE ALERT FEED</span>
            </div>
            <div style="text-align:center;padding:3rem 1rem;color:#3a4558;font-size:0.8rem;font-family:'IBM Plex Mono',monospace;">
                No anomalies detected above {std_thresh:.1f}σ in the last {lookback}.<br>
                Try lowering the threshold or extending the lookback period.
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        rows_html = ""
        for a in alerts[:40]:
            pct_color = "#00e676" if a["pct"] >= 0 else "#ff3d57"
            pct_arrow = "▲" if a["pct"] >= 0 else "▼"
            z_color   = "#b388ff" if a["z"] >= 3 else ("#ffd166" if a["z"] >= 2 else "#8896ab")
            alert_tag = ""
            if a["z"] >= 3.5:
                alert_tag = '<span style="background:rgba(179,136,255,0.2);color:#b388ff;border:1px solid rgba(179,136,255,0.3);padding:1px 6px;border-radius:3px;font-size:0.52rem;margin-left:5px;">WHALE</span>'
            elif a["z"] >= 2.5:
                alert_tag = '<span style="background:rgba(255,209,102,0.1);color:#ffd166;border:1px solid rgba(255,209,102,0.25);padding:1px 6px;border-radius:3px;font-size:0.52rem;margin-left:5px;">LARGE</span>'

            vol_fmt  = f"{a['volume']/1e6:.1f}M" if a["volume"] >= 1e6 else f"{a['volume']/1e3:.0f}K"
            avg_fmt  = f"{a['avg_vol']/1e6:.1f}M" if a["avg_vol"] >= 1e6 else f"{a['avg_vol']/1e3:.0f}K"
            date_str = a["date"].strftime("%Y-%m-%d") if hasattr(a["date"], "strftime") else str(a["date"])[:10]

            rows_html += f"""
            <div style="border-bottom:1px solid #0d1117;padding:0.55rem 0.2rem;display:flex;align-items:center;gap:1rem;flex-wrap:wrap;font-family:'IBM Plex Mono',monospace;">
                <span style="color:#3a4558;font-size:0.6rem;flex-shrink:0;width:80px;">{date_str}</span>
                <span style="color:#eef2f7;font-weight:700;font-size:0.82rem;flex-shrink:0;width:70px;">{a['ticker']}{alert_tag}</span>
                <span style="flex:1;min-width:120px;font-size:0.75rem;">
                    <span style="color:{z_color};font-weight:700;">{a['mult']:.1f}×</span>
                    <span style="color:#3a4558;"> avg vol &nbsp;</span>
                    <span style="color:#8896ab;">{vol_fmt} vs {avg_fmt}</span>
                </span>
                <span style="color:{pct_color};font-size:0.8rem;flex-shrink:0;min-width:64px;text-align:right;">{pct_arrow} {abs(a['pct']):.2f}%</span>
                <span style="color:#8896ab;flex-shrink:0;font-size:0.72rem;min-width:64px;text-align:right;">${a['price']:,.2f}</span>
                <span style="color:{z_color};flex-shrink:0;font-size:0.65rem;min-width:36px;text-align:right;">{a['z']:.1f}σ</span>
            </div>"""

        st.markdown(f"""
        <div style="background:#030508;border:1px solid #1a2235;border-radius:10px;overflow:hidden;max-height:560px;overflow-y:auto;">
            <div style="background:#08100d;border-bottom:1px solid #1a2235;padding:0.5rem 1rem;display:flex;align-items:center;gap:0.5rem;font-family:'IBM Plex Mono',monospace;font-size:0.6rem;color:#3a4a5e;position:sticky;top:0;z-index:10;">
                <div style="width:8px;height:8px;border-radius:50%;background:#ff3d57;flex-shrink:0;"></div>
                <div style="width:8px;height:8px;border-radius:50%;background:#ffd166;flex-shrink:0;"></div>
                <div style="width:8px;height:8px;border-radius:50%;background:#00e676;flex-shrink:0;"></div>
                <span style="margin-left:0.5rem;">WHALE ALERT FEED — {len(alerts)} events detected</span>
                <span style="margin-left:auto;color:#3a4558;">DATE &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; TICKER &nbsp;&nbsp; VOLUME SPIKE &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; CHANGE &nbsp;&nbsp;&nbsp; PRICE &nbsp;&nbsp;&nbsp;&nbsp; Z</span>
            </div>
            <div style="padding:0 0.8rem;">
            {rows_html}
            </div>
        </div>
        """, unsafe_allow_html=True)

with info_col:
    st.markdown('<div style="font-family:IBM Plex Mono,monospace;font-size:0.58rem;color:#3a4558;text-transform:uppercase;letter-spacing:0.18em;margin-bottom:0.8rem;">Watch List Status</div>', unsafe_allow_html=True)
    for t, s in summaries.items():
        alert_count = sum(1 for a in alerts if a["ticker"] == t)
        pct_color   = "#00e676" if s["last_pct"] >= 0 else "#ff3d57"
        vol_mult    = s["last_vol"] / s["avg_vol"] if s["avg_vol"] > 0 else 0
        has_alert   = alert_count > 0
        border_col  = "#b388ff" if has_alert else "#1a2235"
        st.markdown(f"""
        <div style="background:#0c1018;border:1px solid {border_col};border-radius:8px;padding:0.8rem;margin-bottom:0.5rem;">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.3rem;">
                <span style="font-size:0.82rem;color:#eef2f7;font-weight:700;">{t}</span>
                <span style="color:{pct_color};font-size:0.72rem;">{s['last_pct']:+.2f}%</span>
            </div>
            <div style="display:flex;justify-content:space-between;font-size:0.65rem;color:#3a4558;">
                <span>Vol {vol_mult:.1f}× avg</span>
                <span style="color:{'#b388ff' if has_alert else '#3a4558'};">{alert_count} alert{'s' if alert_count!=1 else ''}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div style="margin-top:1rem;padding:0.8rem;background:#0a080f;border:1px solid rgba(179,136,255,0.15);border-radius:8px;font-size:0.74rem;color:#8896ab;line-height:1.65;">
        <div style="color:#b388ff;font-family:'IBM Plex Mono',monospace;font-size:0.56rem;text-transform:uppercase;letter-spacing:0.15em;margin-bottom:0.4rem;">Legend</div>
        <span style="background:rgba(179,136,255,0.2);color:#b388ff;padding:1px 6px;border-radius:2px;font-size:0.6rem;">WHALE</span> ≥ 3.5σ<br>
        <span style="background:rgba(255,209,102,0.1);color:#ffd166;padding:1px 6px;border-radius:2px;font-size:0.6rem;margin-top:3px;display:inline-block;">LARGE</span> ≥ 2.5σ
    </div>
    """, unsafe_allow_html=True)
