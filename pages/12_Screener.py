import streamlit as st, sys, os, pandas as pd, yfinance as yf, numpy as np
import plotly.graph_objects as go
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.styles import SHARED_CSS, inject_bg, PLOTLY_THEME; from utils.nav import navbar

st.set_page_config(page_title="Screener | 11%", layout="wide", initial_sidebar_state="collapsed")
st.markdown(SHARED_CSS, unsafe_allow_html=True)
st.markdown("""<style>
.ph{background:linear-gradient(135deg,#0c1018,#0d1420);border:1px solid #1a2235;border-radius:16px;padding:2.5rem 3rem;margin-bottom:1.5rem}
.ph h1{font-family:'Bebas Neue',sans-serif;font-size:3.5rem;letter-spacing:0.05em;line-height:1;margin:0 0 0.5rem 0}
.ph p{font-family:'IBM Plex Mono',monospace;font-size:0.75rem;color:#8896ab;line-height:1.8;margin:0}
.ph-ey{font-family:'IBM Plex Mono',monospace;font-size:0.55rem;text-transform:uppercase;letter-spacing:0.3em;color:#3a4a5e;margin-bottom:0.5rem}
.sec-t{font-family:'IBM Plex Mono',monospace;font-size:0.52rem;text-transform:uppercase;letter-spacing:0.25em;color:#3a4a5e;padding:1rem 0 0.6rem;border-top:1px solid #0d1117}
/* Table */
.sc-tbl{width:100%;border-collapse:collapse;font-family:'IBM Plex Mono',monospace}
.sc-hdr{background:#0d1117;font-size:0.5rem;text-transform:uppercase;letter-spacing:0.15em;color:#3a4a5e;padding:0.6rem 0.8rem;text-align:left;cursor:pointer;white-space:nowrap;user-select:none;border-bottom:2px solid #1a2235}
.sc-hdr:hover{color:#8896ab}
.sc-row{border-bottom:1px solid #0d1117;transition:background 0.1s}
.sc-row:hover{background:rgba(255,255,255,0.025)}
.sc-cell{padding:0.65rem 0.8rem;font-size:0.72rem;white-space:nowrap;vertical-align:middle}
.sc-sym{font-weight:700;font-size:0.85rem;color:#eef2f7}
.sc-name{font-size:0.6rem;color:#3a4a5e;margin-top:0.1rem}
.pos{color:#00e676;font-weight:600}.neg{color:#ff3d57;font-weight:600}.neu{color:#8896ab}
.rsi-hot{color:#ff3d57;font-weight:700}.rsi-cold{color:#00e676;font-weight:700}.rsi-mid{color:#ffd166}
.badge{font-size:0.46rem;text-transform:uppercase;letter-spacing:0.1em;padding:2px 7px;border-radius:3px;font-weight:700;white-space:nowrap}
.badge-buy{background:rgba(0,230,118,0.12);color:#00e676;border:1px solid rgba(0,230,118,0.25)}
.badge-sell{background:rgba(255,61,87,0.12);color:#ff3d57;border:1px solid rgba(255,61,87,0.25)}
.badge-neutral{background:rgba(255,209,102,0.1);color:#ffd166;border:1px solid rgba(255,209,102,0.2)}
.badge-above{background:rgba(77,166,255,0.1);color:#4da6ff;border:1px solid rgba(77,166,255,0.2)}
.badge-below{background:rgba(255,61,87,0.08);color:#ff3d57;border:1px solid rgba(255,61,87,0.15)}
/* Filter panel */
.filter-panel{background:#0c1018;border:1px solid #1a2235;border-radius:12px;padding:1.2rem 1.5rem;margin-bottom:1rem}
.filter-group-title{font-family:'IBM Plex Mono',monospace;font-size:0.5rem;text-transform:uppercase;letter-spacing:0.2em;color:#3a4a5e;margin-bottom:0.6rem}
/* Result bar */
.result-bar{background:#0d1117;border-radius:8px;padding:0.7rem 1.2rem;display:flex;align-items:center;gap:2rem;margin-bottom:0.8rem;font-family:'IBM Plex Mono',monospace;font-size:0.68rem;color:#8896ab}
.result-count{font-family:'Bebas Neue',sans-serif;font-size:1.8rem;color:#eef2f7;letter-spacing:0.05em}
</style>""", unsafe_allow_html=True)
navbar()
inject_bg()

st.markdown("""<div class="ph"><div class="ph-ey">Stock Screener</div><h1>Screener</h1>
<p>Professional multi-filter screener. Filter by RSI, momentum, SMA position, volume, market cap, and sector. Sorted and exportable.</p></div>""", unsafe_allow_html=True)

# ── Watchlist ────────────────────────────────────────────────────────────────
WATCHLIST = {
    "Mega Cap Tech":  ["AAPL","MSFT","NVDA","GOOGL","META","AMZN","TSLA","AVGO","AMD","CRM","ORCL","ADBE"],
    "Finance":        ["JPM","GS","MS","BAC","WFC","V","MA","BLK","AXP","C","SCHW","COF"],
    "Healthcare":     ["UNH","JNJ","LLY","ABBV","MRK","PFE","AMGN","BMY","GILD","MDT","CVS","CI"],
    "Energy":         ["XOM","CVX","COP","SLB","EOG","PSX","MPC","VLO","HAL","DVN"],
    "Industrials":    ["GE","HON","CAT","DE","UPS","RTX","BA","LMT","EMR","NOC"],
    "Consumer":       ["AMZN","WMT","COST","TGT","HD","LOW","NKE","MCD","SBUX","PG","KO","PEP"],
    "ETFs":           ["SPY","QQQ","IWM","GLD","TLT","XLK","XLF","XLE","XLV","XLI"],
}

# ── Filters ──────────────────────────────────────────────────────────────────
st.markdown('<div class="filter-panel">', unsafe_allow_html=True)

st.markdown('<div class="filter-group-title">Universe & Sorting</div>', unsafe_allow_html=True)
u1, u2, u3 = st.columns(3)
with u1:
    selected_sectors = st.multiselect("Sector / Group", list(WATCHLIST.keys()), default=list(WATCHLIST.keys()))
with u2:
    sort_by = st.selectbox("Sort By", ["1M Return","1W Return","RSI","Volume (Avg)","Price","Market Cap"])
with u3:
    sort_asc = st.radio("Sort Direction", ["Descending","Ascending"], horizontal=True) == "Ascending"

st.markdown('<div class="filter-group-title" style="margin-top:0.8rem">Momentum & Trend Filters</div>', unsafe_allow_html=True)
f1, f2, f3, f4 = st.columns(4)
with f1: rsi_range = st.slider("RSI Range", 0, 100, (0, 100), help="14-period RSI")
with f2: ret_1w_min = st.slider("1-Week Return Min (%)", -30, 30, -30)
with f3: ret_1m_min = st.slider("1-Month Return Min (%)", -50, 50, -50)
with f4:
    sma_filter = st.selectbox("SMA Position", ["Any","Above 20-day SMA","Below 20-day SMA","Above 50-day SMA","Below 50-day SMA","Above 200-day SMA"])

st.markdown('<div class="filter-group-title" style="margin-top:0.8rem">Volume & Size Filters</div>', unsafe_allow_html=True)
v1, v2, v3, v4 = st.columns(4)
with v1: min_avg_vol = st.number_input("Min Avg Volume (M shares)", value=0.0, step=0.5, min_value=0.0)
with v2: max_avg_vol = st.number_input("Max Avg Volume (M shares)", value=0.0, step=0.5, min_value=0.0, help="0 = no limit")
with v3: vol_spike   = st.checkbox("Volume spike (2x avg)", value=False, help="Today's volume > 2x 20-day average")
with v4: min_price   = st.number_input("Min Price ($)", value=0.0, step=1.0, min_value=0.0)

run_btn = st.button("Run Screener", type="primary")
st.markdown('</div>', unsafe_allow_html=True)

# ── Screening function ────────────────────────────────────────────────────────
@st.cache_data(ttl=600)
def screen_stock(sym):
    try:
        t   = yf.Ticker(sym)
        h   = t.history(period="1y")
        if len(h) < 60: return None
        if isinstance(h.columns, pd.MultiIndex):
            h.columns = h.columns.get_level_values(0)

        close = h["Close"].to_numpy(dtype=float)
        vol   = h["Volume"].to_numpy(dtype=float)
        n     = len(close)

        # RSI 14
        delta = np.diff(close)
        gain  = np.where(delta > 0, delta, 0)
        loss  = np.where(delta < 0, -delta, 0)
        avg_g = np.mean(gain[-14:]) if len(gain) >= 14 else 0
        avg_l = np.mean(loss[-14:]) if len(loss) >= 14 else 0
        rsi   = 100 - (100/(1+avg_g/avg_l)) if avg_l > 0 else 100.0

        # Returns
        ret_1w = (close[-1]/close[-6]-1)*100  if n >= 6  else 0
        ret_1m = (close[-1]/close[-22]-1)*100 if n >= 22 else 0
        ret_3m = (close[-1]/close[-66]-1)*100 if n >= 66 else 0

        # SMAs
        sma20  = float(np.mean(close[-20:]))  if n >= 20  else close[-1]
        sma50  = float(np.mean(close[-50:]))  if n >= 50  else close[-1]
        sma200 = float(np.mean(close[-200:])) if n >= 200 else close[-1]

        # Volume
        avg_vol    = float(np.mean(vol[-20:])) / 1e6
        today_vol  = float(vol[-1]) / 1e6
        vol_ratio  = today_vol / avg_vol if avg_vol > 0 else 1.0

        # Market cap
        info = t.fast_info
        mc   = getattr(info, "market_cap", None) or 0
        if mc >= 1e12:   cap_str = f"${mc/1e12:.1f}T"
        elif mc >= 1e9:  cap_str = f"${mc/1e9:.0f}B"
        elif mc >= 1e6:  cap_str = f"${mc/1e6:.0f}M"
        else:            cap_str = "—"

        # Signal
        above_20  = close[-1] > sma20
        above_50  = close[-1] > sma50
        above_200 = close[-1] > sma200
        sma_score = sum([above_20, above_50, above_200])
        if rsi < 35 and sma_score >= 2:       signal = "Buy"
        elif rsi > 70 or sma_score == 0:      signal = "Sell"
        else:                                  signal = "Neutral"

        return {
            "sym":sym, "price":round(close[-1],2), "rsi":round(rsi,1),
            "ret_1w":round(ret_1w,2), "ret_1m":round(ret_1m,2), "ret_3m":round(ret_3m,2),
            "avg_vol":round(avg_vol,2), "today_vol":round(today_vol,2), "vol_ratio":round(vol_ratio,2),
            "sma20":round(sma20,2), "sma50":round(sma50,2), "sma200":round(sma200,2),
            "above_20":above_20, "above_50":above_50, "above_200":above_200,
            "cap":cap_str, "mc":mc, "signal":signal,
        }
    except: return None

if run_btn:
    tickers = []
    for sec in selected_sectors:
        tickers += WATCHLIST.get(sec, [])
    tickers = list(dict.fromkeys(tickers))  # dedupe

    progress = st.progress(0, text="Scanning...")
    results  = []
    for i, sym in enumerate(tickers):
        r = screen_stock(sym)
        if r: results.append(r)
        progress.progress((i+1)/len(tickers), text=f"Scanning {sym}... ({i+1}/{len(tickers)})")
    progress.empty()

    df = pd.DataFrame(results)
    if df.empty: st.warning("No data returned."); st.stop()

    # Apply filters
    df = df[(df["rsi"] >= rsi_range[0]) & (df["rsi"] <= rsi_range[1])]
    df = df[df["ret_1w"] >= ret_1w_min]
    df = df[df["ret_1m"] >= ret_1m_min]
    if min_avg_vol > 0:   df = df[df["avg_vol"] >= min_avg_vol]
    if max_avg_vol > 0:   df = df[df["avg_vol"] <= max_avg_vol]
    if min_price > 0:     df = df[df["price"]   >= min_price]
    if vol_spike:         df = df[df["vol_ratio"] >= 2.0]
    if sma_filter == "Above 20-day SMA":    df = df[df["above_20"] == True]
    elif sma_filter == "Below 20-day SMA":  df = df[df["above_20"] == False]
    elif sma_filter == "Above 50-day SMA":  df = df[df["above_50"] == True]
    elif sma_filter == "Below 50-day SMA":  df = df[df["above_50"] == False]
    elif sma_filter == "Above 200-day SMA": df = df[df["above_200"] == True]

    # Sort
    sort_col_map = {"1M Return":"ret_1m","1W Return":"ret_1w","RSI":"rsi",
                    "Volume (Avg)":"avg_vol","Price":"price","Market Cap":"mc"}
    sc = sort_col_map.get(sort_by, "ret_1m")
    df = df.sort_values(sc, ascending=sort_asc).reset_index(drop=True)

    st.session_state["screen_df"] = df

if "screen_df" in st.session_state:
    df = st.session_state["screen_df"]

    st.markdown(f"""
    <div class="result-bar">
        <span class="result-count">{len(df)}</span>
        <span>stocks passed your filters</span>
        <span style="margin-left:auto;font-size:0.62rem;color:#3a4a5e">Sorted by {sort_by if "sort_by" in dir() else "1M Return"}</span>
    </div>
    """, unsafe_allow_html=True)

    if not df.empty:
        # Return bar chart
        top20 = df.head(20)
        fig = go.Figure(go.Bar(
            x=top20["sym"], y=top20["ret_1m"],
            marker_color=["#00e676" if v >= 0 else "#ff3d57" for v in top20["ret_1m"]],
            text=[f"{v:+.1f}%" for v in top20["ret_1m"]], textposition="outside",
            textfont=dict(family="IBM Plex Mono", size=10)
        ))
        fig.update_layout(**PLOTLY_THEME, height=240, showlegend=False,
                          title="1-Month Return — Top Results", yaxis_title="Return (%)")
        st.plotly_chart(fig, use_container_width=True)

        # Table
        st.markdown('<table class="sc-tbl"><thead><tr>', unsafe_allow_html=True)
        headers = ["Ticker","Price","Signal","RSI","1W","1M","3M","Avg Vol","Vol Ratio","20 SMA","50 SMA","200 SMA","Mkt Cap"]
        for h in headers:
            st.markdown(f'<th class="sc-hdr">{h}</th>', unsafe_allow_html=True)
        st.markdown('</tr></thead><tbody>', unsafe_allow_html=True)

        for _, r in df.iterrows():
            rsi_cls = "rsi-hot" if r["rsi"]>70 else ("rsi-cold" if r["rsi"]<35 else "rsi-mid")
            sig_cls = {"Buy":"badge-buy","Sell":"badge-sell","Neutral":"badge-neutral"}[r["signal"]]
            w_cls   = "pos" if r["ret_1w"]>=0 else "neg"
            m_cls   = "pos" if r["ret_1m"]>=0 else "neg"
            q_cls   = "pos" if r["ret_3m"]>=0 else "neg"
            sma20_cls  = "badge-above" if r["above_20"]  else "badge-below"
            sma50_cls  = "badge-above" if r["above_50"]  else "badge-below"
            sma200_cls = "badge-above" if r["above_200"] else "badge-below"
            sma20_txt  = "Above" if r["above_20"]  else "Below"
            sma50_txt  = "Above" if r["above_50"]  else "Below"
            sma200_txt = "Above" if r["above_200"] else "Below"
            vr_cls  = "pos" if r["vol_ratio"]>=2 else "neu"
            st.markdown(f"""<tr class="sc-row">
                <td class="sc-cell"><div class="sc-sym">{r["sym"]}</div></td>
                <td class="sc-cell neu">${r["price"]:,.2f}</td>
                <td class="sc-cell"><span class="badge {sig_cls}">{r["signal"]}</span></td>
                <td class="sc-cell {rsi_cls}">{r["rsi"]:.0f}</td>
                <td class="sc-cell {w_cls}">{r["ret_1w"]:+.1f}%</td>
                <td class="sc-cell {m_cls}">{r["ret_1m"]:+.1f}%</td>
                <td class="sc-cell {q_cls}">{r["ret_3m"]:+.1f}%</td>
                <td class="sc-cell neu">{r["avg_vol"]:.1f}M</td>
                <td class="sc-cell {vr_cls}">{r["vol_ratio"]:.1f}x</td>
                <td class="sc-cell"><span class="badge {sma20_cls}">{sma20_txt}</span></td>
                <td class="sc-cell"><span class="badge {sma50_cls}">{sma50_txt}</span></td>
                <td class="sc-cell"><span class="badge {sma200_cls}">{sma200_txt}</span></td>
                <td class="sc-cell neu">{r["cap"]}</td>
            </tr>""", unsafe_allow_html=True)

        st.markdown('</tbody></table>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.download_button("Download Results CSV", df.to_csv(index=False),
                          file_name="screen_results.csv", mime="text/csv")
    else:
        st.markdown('<div style="text-align:center;padding:3rem;color:#3a4a5e;font-family:IBM Plex Mono,monospace;font-size:0.75rem;border:1px dashed #1a2235;border-radius:12px;">No stocks matched your filters. Try wider ranges.</div>', unsafe_allow_html=True)
else:
    st.markdown('<div style="text-align:center;padding:4rem;color:#3a4a5e;font-family:IBM Plex Mono,monospace;font-size:0.75rem;border:1px dashed #1a2235;border-radius:12px;margin-top:0.5rem;">Set your filters above and click Run Screener.</div>', unsafe_allow_html=True)
