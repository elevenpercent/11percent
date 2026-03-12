import streamlit as st
import pandas as pd
import sys, os
from datetime import date, timedelta

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.styles import SHARED_CSS
from utils.nav import navbar
from utils.data import get_stock_data
from utils.indicators import INDICATOR_INFO, apply_indicator
from utils.strategies import run_backtest, STRATEGY_REGISTRY

st.set_page_config(page_title="Strategy Lab | 11%", layout="wide", initial_sidebar_state="collapsed")
st.markdown(SHARED_CSS, unsafe_allow_html=True)
navbar()

st.markdown("""
<div class="page-header">
    <div class="page-header-eyebrow">Backtesting Engine</div>
    <h1>Strategy Lab</h1>
    <p>Test prebuilt strategies on any ticker with full performance metrics, or wire up your own custom signal from up to three indicators.</p>
</div>
""", unsafe_allow_html=True)

# ── Shared inputs (outside tabs so both tabs share them)
c1, c2, c3, c4, c5 = st.columns([2, 1.5, 1.5, 1, 1])
with c1: ticker     = st.text_input("Ticker", value="AAPL", key="sl_ticker").upper().strip()
with c2: start_date = st.date_input("From",   value=date.today()-timedelta(days=730), key="sl_start")
with c3: end_date   = st.date_input("To",     value=date.today(), key="sl_end")
with c4: capital    = st.number_input("Capital ($)", value=10000, step=1000, key="sl_cap")
with c5: commission = st.number_input("Commission ($)", value=0.0, step=0.5, key="sl_com")

# ── Load data (shared, cached — fires for both tabs)
@st.cache_data(ttl=3600)
def load(ticker, start, end):
    return get_stock_data(ticker, str(start), str(end))

df = load(ticker, start_date, end_date)

if df.empty:
    st.error(f"No data for **{ticker}**. Check the ticker and date range.")
    st.stop()

tab_pre, tab_custom = st.tabs(["Prebuilt Strategies", "Custom Signal Builder"])

# ══════════════════════════════════════════════════════════
# TAB 1 — Prebuilt
# ══════════════════════════════════════════════════════════
with tab_pre:
    strategy_names = list(STRATEGY_REGISTRY.keys())
    chosen = st.selectbox("Strategy", strategy_names, key="sl_strat")
    strat  = STRATEGY_REGISTRY[chosen]

    # Dynamic parameter sliders
    params = {}
    if strat.get("params"):
        pcols = st.columns(min(len(strat["params"]), 4))
        for i, (pname, pdef) in enumerate(strat["params"].items()):
            with pcols[i % len(pcols)]:
                params[pname] = st.slider(
                    pname.replace("_", " ").title(),
                    min_value=pdef.get("min", 2),
                    max_value=pdef.get("max", 200),
                    value=pdef.get("default", 14),
                    key=f"sl_p_{pname}"
                )

    run_pre = st.button("Run Backtest", type="primary", key="sl_run_pre")
    if run_pre:
        with st.spinner("Running backtest…"):
            portfolio, trades, metrics = run_backtest(
                df.copy(), chosen, params, float(capital), float(commission)
            )
        st.session_state["last_backtest"] = {
            "ticker": ticker, "strategy": chosen,
            "metrics": metrics, "params": params,
        }
        _show_results(portfolio, trades, metrics, ticker, chosen)

    elif "last_backtest" in st.session_state and st.session_state["last_backtest"].get("strategy") == chosen:
        st.info("Showing last run — hit **Run Backtest** to refresh.")


# ══════════════════════════════════════════════════════════
# TAB 2 — Custom Signal Builder
# ══════════════════════════════════════════════════════════
with tab_custom:
    st.markdown('<div class="section-hdr">Build Your Signal</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="info-box" style="margin-bottom:1.2rem;">
    Combine up to 3 indicators. <strong>BUY</strong> triggers when all selected conditions are true simultaneously.
    <strong>SELL</strong> triggers on the opposite crossover. Uses AND logic between indicators.
    </div>
    """, unsafe_allow_html=True)

    n_indicators = st.radio("Number of indicators", [1, 2, 3], horizontal=True, key="sl_n_ind")

    indicator_list = list(INDICATOR_INFO.keys())

    # ── Collect indicator configs
    ind_configs = []
    for i in range(n_indicators):
        with st.expander(f"Indicator {i+1}", expanded=True):
            ic1, ic2 = st.columns([2, 3])
            with ic1:
                ind_name = st.selectbox(
                    "Indicator", indicator_list, key=f"sl_ind_{i}",
                    help=INDICATOR_INFO.get(indicator_list[0], {}).get("desc", "")
                )
            info = INDICATOR_INFO.get(ind_name, {})
            with ic2:
                condition = st.selectbox(
                    "Condition",
                    options=info.get("conditions", ["crosses_above", "crosses_below", "above", "below"]),
                    key=f"sl_cond_{i}",
                    format_func=lambda x: x.replace("_", " ").title()
                )

            # Indicator params
            ind_params = {}
            ipc = st.columns(min(len(info.get("params", {})), 4) or 1)
            for j, (pname, pdef) in enumerate(info.get("params", {}).items()):
                with ipc[j % len(ipc)]:
                    ind_params[pname] = st.slider(
                        pname.replace("_", " ").title(),
                        min_value=pdef.get("min", 2),
                        max_value=pdef.get("max", 200),
                        value=pdef.get("default", 14),
                        key=f"sl_ip_{i}_{pname}"
                    )

            ind_configs.append({"name": ind_name, "condition": condition, "params": ind_params})

    run_custom = st.button("Run Custom Backtest", type="primary", key="sl_run_custom")

    if run_custom:
        with st.spinner("Computing signals and running backtest…"):
            try:
                # Build combined signal
                df_work = df.copy()
                signal_series_list = []

                for cfg in ind_configs:
                    sig = apply_indicator(df_work, cfg["name"], cfg["params"], cfg["condition"])
                    signal_series_list.append(sig)

                # AND logic: buy only when all say buy
                if len(signal_series_list) == 1:
                    combined = signal_series_list[0]
                else:
                    combined = signal_series_list[0]
                    for s in signal_series_list[1:]:
                        combined = combined & s

                df_work["Signal"] = 0
                df_work.loc[combined, "Signal"] = 1
                # Sell = any indicator reverses
                for cfg in ind_configs:
                    sell_sig = apply_indicator(df_work, cfg["name"], cfg["params"],
                                               cfg["condition"].replace("above", "below").replace("below", "above")
                                               if "above" in cfg["condition"] or "below" in cfg["condition"]
                                               else cfg["condition"])
                    df_work.loc[sell_sig, "Signal"] = -1

                portfolio, trades, metrics = run_backtest(
                    df_work, "__custom__", {}, float(capital), float(commission),
                    precomputed_signals=True
                )
                st.session_state["last_backtest"] = {
                    "ticker": ticker, "strategy": "Custom",
                    "metrics": metrics, "params": {c["name"]: c["params"] for c in ind_configs},
                }
                _show_results(portfolio, trades, metrics, ticker, "Custom Signal")
            except Exception as e:
                st.error(f"Signal build error: {e}")
                st.info("Check that your selected indicators are compatible. Some indicators require minimum data length.")


# ══════════════════════════════════════════════════════════
# Shared results renderer
# ══════════════════════════════════════════════════════════
def _show_results(portfolio, trades, metrics, ticker, strategy_name):
    import plotly.graph_objects as go
    from utils.styles import PLOTLY_THEME

    m = metrics
    ret_color    = "pos" if m.get("total_return", 0) >= 0 else "neg"
    alpha_color  = "pos" if m.get("alpha", 0) >= 0 else "neg"
    dd_color     = "neg"

    st.markdown(
        f'<div class="stat-strip">'
        f'<div class="stat-cell"><div class="stat-val {ret_color}">{m.get("total_return",0)*100:.1f}%</div><div class="stat-lbl">Total Return</div></div>'
        f'<div class="stat-cell"><div class="stat-val {alpha_color}">{m.get("alpha",0)*100:+.1f}%</div><div class="stat-lbl">Alpha vs B&H</div></div>'
        f'<div class="stat-cell"><div class="stat-val {dd_color}">{m.get("max_drawdown",0)*100:.1f}%</div><div class="stat-lbl">Max Drawdown</div></div>'
        f'<div class="stat-cell"><div class="stat-val neu">{m.get("sharpe",0):.2f}</div><div class="stat-lbl">Sharpe</div></div>'
        f'<div class="stat-cell"><div class="stat-val neu">{m.get("win_rate",0)*100:.1f}%</div><div class="stat-lbl">Win Rate</div></div>'
        f'<div class="stat-cell"><div class="stat-val neu">{m.get("num_trades",0)}</div><div class="stat-lbl">Trades</div></div>'
        f'<div class="stat-cell"><div class="stat-val neu">${m.get("final_value",0):,.0f}</div><div class="stat-lbl">Final Value</div></div>'
        f'</div>',
        unsafe_allow_html=True
    )

    if portfolio is not None and not portfolio.empty and "Portfolio" in portfolio.columns:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=portfolio.index, y=portfolio["Portfolio"],
            name="Strategy", line=dict(color="#00e676", width=2), fill="tozeroy",
            fillcolor="rgba(0,230,118,0.06)"
        ))
        if "BuyHold" in portfolio.columns:
            fig.add_trace(go.Scatter(
                x=portfolio.index, y=portfolio["BuyHold"],
                name="Buy & Hold", line=dict(color="#4da6ff", width=1.5, dash="dash")
            ))
        fig.update_layout(**PLOTLY_THEME, title=f"{ticker} — {strategy_name}", height=340,
                          legend=dict(orientation="h", y=1.02, x=0))
        st.plotly_chart(fig, use_container_width=True)

    if trades is not None and not trades.empty:
        with st.expander(f"Trade log ({len(trades)} trades)"):
            st.dataframe(trades, use_container_width=True)
