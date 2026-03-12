import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sys, os
from datetime import date, timedelta

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.styles import SHARED_CSS, PLOTLY_THEME
from utils.nav import navbar
from utils.data import get_stock_data
from utils.strategies import run_backtest, STRATEGY_REGISTRY

st.set_page_config(page_title="Strategy Lab | 11%", layout="wide", initial_sidebar_state="collapsed")
st.markdown(SHARED_CSS, unsafe_allow_html=True)
navbar()

st.markdown("""
<div class="page-header">
    <div class="page-header-eyebrow">Backtesting Engine</div>
    <h1>Strategy Lab</h1>
    <p>Test prebuilt strategies on any ticker with full performance metrics, or wire up your own custom signal from multiple indicators.</p>
</div>
""", unsafe_allow_html=True)

# ── Shared inputs
c1, c2, c3, c4, c5 = st.columns([2, 1.5, 1.5, 1, 1])
with c1: ticker     = st.text_input("Ticker", value="AAPL", key="sl_ticker").upper().strip()
with c2: start_date = st.date_input("From", value=date.today()-timedelta(days=730), key="sl_start")
with c3: end_date   = st.date_input("To", value=date.today(), key="sl_end")
with c4: capital    = st.number_input("Capital ($)", value=10000, step=1000, key="sl_cap")
with c5: commission = st.number_input("Commission ($)", value=0.0, step=0.5, key="sl_com")

# ── Load data once (shared between tabs)
@st.cache_data(ttl=3600)
def load(ticker, start, end):
    return get_stock_data(ticker, str(start), str(end))

if ticker:
    df = load(ticker, start_date, end_date)
else:
    df = pd.DataFrame()

if df.empty and ticker:
    st.error(f"No data for **{ticker}**. Check the symbol and date range.")
    st.stop()

tab_pre, tab_custom = st.tabs(["Prebuilt Strategies", "Custom Signal Builder"])

# ══════════════════════════════════════════════════════════
# Shared results renderer
# ══════════════════════════════════════════════════════════
def show_results(portfolio, trades, metrics, ticker_name, strategy_name):
    m = metrics
    ret_color   = "pos" if m.get("total_return", 0) >= 0 else "neg"
    alpha_color = "pos" if m.get("alpha", 0) >= 0 else "neg"

    st.markdown(
        f'<div class="stat-strip">'
        f'<div class="stat-cell"><div class="stat-val {ret_color}">{m.get("total_return",0)*100:.1f}%</div><div class="stat-lbl">Total Return</div></div>'
        f'<div class="stat-cell"><div class="stat-val {alpha_color}">{m.get("alpha",0)*100:+.1f}%</div><div class="stat-lbl">Alpha vs B&H</div></div>'
        f'<div class="stat-cell"><div class="stat-val neg">{m.get("max_drawdown",0)*100:.1f}%</div><div class="stat-lbl">Max Drawdown</div></div>'
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
            name="Strategy", line=dict(color="#00e676", width=2),
            fill="tozeroy", fillcolor="rgba(0,230,118,0.06)"
        ))
        if "BuyHold" in portfolio.columns:
            fig.add_trace(go.Scatter(
                x=portfolio.index, y=portfolio["BuyHold"],
                name="Buy & Hold", line=dict(color="#4da6ff", width=1.5, dash="dash")
            ))
        fig.update_layout(
            **PLOTLY_THEME, height=340,
            title=f"{ticker_name} — {strategy_name}",
            legend=dict(orientation="h", y=1.02, x=0)
        )
        st.plotly_chart(fig, use_container_width=True)

    if trades is not None and not trades.empty:
        with st.expander(f"Trade log ({len(trades)} trades)"):
            st.dataframe(trades, use_container_width=True)


# ══════════════════════════════════════════════════════════
# TAB 1 — Prebuilt Strategies
# ══════════════════════════════════════════════════════════
with tab_pre:
    if df.empty:
        st.info("Enter a ticker above to get started.")
        st.stop()

    strategy_names = list(STRATEGY_REGISTRY.keys())
    chosen = st.selectbox("Strategy", strategy_names, key="sl_strat")
    strat  = STRATEGY_REGISTRY[chosen]

    # Dynamic sliders for strategy params
    params = {}
    if strat.get("params"):
        p_items = list(strat["params"].items())
        pcols = st.columns(min(len(p_items), 4))
        for i, (pname, pdef) in enumerate(p_items):
            with pcols[i % len(pcols)]:
                params[pname] = st.slider(
                    pname.replace("_", " ").title(),
                    min_value=int(pdef.get("min", 2)),
                    max_value=int(pdef.get("max", 200)),
                    value=int(pdef.get("default", 14)),
                    key=f"sl_p_{pname}"
                )

    if st.button("Run Backtest", type="primary", key="sl_run_pre"):
        with st.spinner("Running backtest…"):
            try:
                portfolio, trades, metrics = run_backtest(
                    df.copy(), chosen, params, float(capital), float(commission)
                )
                st.session_state["last_backtest"] = {
                    "ticker": ticker, "strategy": chosen,
                    "metrics": metrics, "params": params,
                }
                show_results(portfolio, trades, metrics, ticker, chosen)
            except Exception as e:
                st.error(f"Backtest error: {e}")


# ══════════════════════════════════════════════════════════
# TAB 2 — Custom Signal Builder
# ══════════════════════════════════════════════════════════
with tab_custom:
    if df.empty:
        st.info("Enter a ticker above to get started.")
        st.stop()

    st.markdown("""
    <div class="info-box" style="margin-bottom:1.2rem;">
    Combine up to 3 indicators with <strong>AND logic</strong> — a BUY signal fires only when all conditions are true simultaneously.
    </div>
    """, unsafe_allow_html=True)

    # Import indicators — use what's actually available
    try:
        from utils.indicators import (
            compute_sma, compute_ema, compute_rsi, compute_macd,
            compute_bollinger, compute_supertrend
        )
        HAS_INDICATORS = True
    except ImportError:
        HAS_INDICATORS = False

    # Define available signals that work with any stock df
    def build_signal(df_work, ind_name, params, direction):
        """Returns a boolean series: True = condition met for BUY."""
        close = df_work["Close"]
        sig = pd.Series(False, index=df_work.index)

        if ind_name == "SMA Crossover":
            fast = close.rolling(params.get("fast", 10)).mean()
            slow = close.rolling(params.get("slow", 30)).mean()
            if direction == "Bullish (Fast crosses above Slow)":
                sig = (fast > slow) & (fast.shift(1) <= slow.shift(1))
            else:
                sig = (fast < slow) & (fast.shift(1) >= slow.shift(1))

        elif ind_name == "EMA Crossover":
            fast = close.ewm(span=params.get("fast", 12), adjust=False).mean()
            slow = close.ewm(span=params.get("slow", 26), adjust=False).mean()
            if direction == "Bullish (Fast crosses above Slow)":
                sig = (fast > slow) & (fast.shift(1) <= slow.shift(1))
            else:
                sig = (fast < slow) & (fast.shift(1) >= slow.shift(1))

        elif ind_name == "RSI":
            delta = close.diff()
            gain  = delta.clip(lower=0).rolling(params.get("period", 14)).mean()
            loss  = (-delta.clip(upper=0)).rolling(params.get("period", 14)).mean()
            rs    = gain / (loss + 1e-10)
            rsi   = 100 - 100 / (1 + rs)
            thresh = params.get("threshold", 30)
            if direction == "Bullish (RSI crosses above threshold)":
                sig = (rsi > thresh) & (rsi.shift(1) <= thresh)
            else:
                sig = (rsi < (100 - thresh)) & (rsi.shift(1) >= (100 - thresh))

        elif ind_name == "MACD":
            fast_ema = close.ewm(span=params.get("fast", 12), adjust=False).mean()
            slow_ema = close.ewm(span=params.get("slow", 26), adjust=False).mean()
            macd     = fast_ema - slow_ema
            signal   = macd.ewm(span=params.get("signal", 9), adjust=False).mean()
            if direction == "Bullish (MACD crosses above Signal)":
                sig = (macd > signal) & (macd.shift(1) <= signal.shift(1))
            else:
                sig = (macd < signal) & (macd.shift(1) >= signal.shift(1))

        elif ind_name == "Bollinger Bands":
            period = params.get("period", 20)
            mult   = params.get("mult", 2.0)
            mid    = close.rolling(period).mean()
            std    = close.rolling(period).std()
            upper  = mid + mult * std
            lower  = mid - mult * std
            if direction == "Bullish (Price crosses above Lower Band)":
                sig = (close > lower) & (close.shift(1) <= lower.shift(1))
            else:
                sig = (close < upper) & (close.shift(1) >= upper.shift(1))

        elif ind_name == "Price vs SMA":
            period = params.get("period", 50)
            sma    = close.rolling(period).mean()
            if direction == "Bullish (Price above SMA)":
                sig = close > sma
            else:
                sig = close < sma

        return sig.fillna(False)

    # Indicator configs
    IND_OPTIONS = {
        "SMA Crossover": {
            "params": {"fast": {"min":2,"max":50,"default":10}, "slow": {"min":10,"max":200,"default":30}},
            "directions": ["Bullish (Fast crosses above Slow)", "Bearish (Fast crosses below Slow)"]
        },
        "EMA Crossover": {
            "params": {"fast": {"min":2,"max":50,"default":12}, "slow": {"min":10,"max":200,"default":26}},
            "directions": ["Bullish (Fast crosses above Slow)", "Bearish (Fast crosses below Slow)"]
        },
        "RSI": {
            "params": {"period": {"min":2,"max":50,"default":14}, "threshold": {"min":10,"max":45,"default":30}},
            "directions": ["Bullish (RSI crosses above threshold)", "Bearish (RSI crosses below overbought)"]
        },
        "MACD": {
            "params": {"fast": {"min":2,"max":30,"default":12}, "slow": {"min":10,"max":60,"default":26}, "signal": {"min":2,"max":20,"default":9}},
            "directions": ["Bullish (MACD crosses above Signal)", "Bearish (MACD crosses below Signal)"]
        },
        "Bollinger Bands": {
            "params": {"period": {"min":5,"max":50,"default":20}, "mult": {"min":1,"max":4,"default":2}},
            "directions": ["Bullish (Price crosses above Lower Band)", "Bearish (Price crosses below Upper Band)"]
        },
        "Price vs SMA": {
            "params": {"period": {"min":5,"max":200,"default":50}},
            "directions": ["Bullish (Price above SMA)", "Bearish (Price below SMA)"]
        },
    }

    n_ind = st.radio("Number of indicators", [1, 2, 3], horizontal=True, key="sl_n_ind")

    ind_configs = []
    for i in range(n_ind):
        with st.expander(f"Indicator {i+1}", expanded=True):
            ic1, ic2 = st.columns(2)
            with ic1:
                ind_name = st.selectbox("Indicator", list(IND_OPTIONS.keys()), key=f"sl_ind_{i}")
            cfg = IND_OPTIONS[ind_name]
            with ic2:
                direction = st.selectbox("Signal", cfg["directions"], key=f"sl_dir_{i}")

            p_items = list(cfg["params"].items())
            if p_items:
                pcols = st.columns(min(len(p_items), 4))
                ind_params = {}
                for j, (pname, pdef) in enumerate(p_items):
                    with pcols[j % len(pcols)]:
                        val = st.slider(
                            pname.replace("_", " ").title(),
                            min_value=float(pdef["min"]),
                            max_value=float(pdef["max"]),
                            value=float(pdef["default"]),
                            key=f"sl_ip_{i}_{pname}"
                        )
                        ind_params[pname] = val
            else:
                ind_params = {}

            ind_configs.append({"name": ind_name, "params": ind_params, "direction": direction})

    if st.button("Run Custom Backtest", type="primary", key="sl_run_custom"):
        with st.spinner("Computing signals…"):
            try:
                df_work = df.copy()

                # Build AND-combined buy signal
                buy_signals = []
                sell_signals = []
                for cfg in ind_configs:
                    b = build_signal(df_work, cfg["name"], cfg["params"], cfg["direction"])
                    # Invert direction for sell
                    sell_dir = cfg["direction"].replace("Bullish", "Bearish").replace("above", "below").replace("Below", "Above")
                    s = build_signal(df_work, cfg["name"], cfg["params"], sell_dir)
                    buy_signals.append(b)
                    sell_signals.append(s)

                combined_buy  = buy_signals[0]
                combined_sell = sell_signals[0]
                for b, s in zip(buy_signals[1:], sell_signals[1:]):
                    combined_buy  = combined_buy  & b
                    combined_sell = combined_sell | s  # OR for sells

                df_work["Signal"] = 0
                df_work.loc[combined_buy,  "Signal"] = 1
                df_work.loc[combined_sell, "Signal"] = -1

                # Run backtest using the precomputed signals
                # We create a minimal "strategy" that uses the df_work signals directly
                portfolio, trades, metrics = _run_custom_backtest(
                    df_work, float(capital), float(commission)
                )

                st.session_state["last_backtest"] = {
                    "ticker": ticker, "strategy": "Custom Signal",
                    "metrics": metrics, "params": {c["name"]: c["params"] for c in ind_configs},
                }
                show_results(portfolio, trades, metrics, ticker, "Custom Signal")

            except Exception as e:
                st.error(f"Signal error: {e}")
                import traceback
                st.code(traceback.format_exc())


def _run_custom_backtest(df, capital, commission):
    """Simple backtest engine using a pre-computed Signal column (1=buy,-1=sell,0=hold)."""
    cash = capital
    shares = 0
    portfolio_vals = []
    trades_list = []
    buy_price = 0

    signals = df["Signal"].values
    closes  = df["Close"].values
    dates   = df.index

    for i in range(len(df)):
        price = float(closes[i])
        sig   = int(signals[i])

        if sig == 1 and shares == 0 and cash > 0:
            # Buy
            qty = (cash - commission) / price
            if qty > 0:
                shares = qty
                cash = 0 - commission
                buy_price = price
                trades_list.append({"Date": dates[i], "Action": "BUY", "Price": price, "Shares": qty})

        elif sig == -1 and shares > 0:
            # Sell
            proceeds = shares * price - commission
            pnl = (price - buy_price) * shares - commission
            trades_list.append({"Date": dates[i], "Action": "SELL", "Price": price, "Shares": shares, "PnL": pnl})
            cash = max(0, proceeds)
            shares = 0
            buy_price = 0

        portfolio_vals.append(cash + shares * price)

    final_value = portfolio_vals[-1] if portfolio_vals else capital
    total_return = (final_value - capital) / capital

    # Buy & hold
    bh_start = float(closes[0])
    bh_vals  = [capital * (c / bh_start) for c in closes]
    bh_ret   = (bh_vals[-1] - capital) / capital
    alpha    = total_return - bh_ret

    # Drawdown
    peak = capital
    max_dd = 0
    for v in portfolio_vals:
        if v > peak: peak = v
        dd = (peak - v) / peak
        if dd > max_dd: max_dd = dd

    # Win rate
    closed = [t for t in trades_list if t.get("Action") == "SELL"]
    wins   = [t for t in closed if t.get("PnL", 0) > 0]
    win_rate = len(wins) / len(closed) if closed else 0

    # Sharpe (simplified)
    import numpy as np
    rets = pd.Series(portfolio_vals).pct_change().dropna()
    sharpe = (rets.mean() / rets.std() * (252**0.5)) if rets.std() > 0 else 0

    portfolio_df = pd.DataFrame({
        "Portfolio": portfolio_vals,
        "BuyHold":   bh_vals,
    }, index=df.index)

    trades_df = pd.DataFrame(trades_list) if trades_list else pd.DataFrame()

    metrics = {
        "total_return": total_return,
        "bh_return":    bh_ret,
        "alpha":        alpha,
        "max_drawdown": max_dd,
        "win_rate":     win_rate,
        "sharpe":       float(sharpe),
        "num_trades":   len(closed),
        "final_value":  final_value,
    }

    return portfolio_df, trades_df, metrics
