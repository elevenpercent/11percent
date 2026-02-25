import streamlit as st
import pandas as pd
from datetime import date, timedelta
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils.data import get_stock_data, get_ticker_info
from utils.strategies import (
    strategy_sma_crossover, strategy_ema_crossover,
    strategy_rsi, strategy_macd, strategy_custom,
    calc_rsi, calc_macd, run_backtest,
)
from utils.charts import plot_price_and_signals, plot_portfolio_vs_bh, plot_rsi, plot_macd

st.set_page_config(page_title="Backtest | BacktestFree", page_icon="🔬", layout="wide")

# ── Styling ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;600&display=swap');
    :root { --accent:#00ff88; --bg:#0d0f14; --surface:#161920; --border:#2a2d38; --muted:#6b7280; }
    html,body,[data-testid="stAppViewContainer"]{background:var(--bg)!important;color:#e8eaf0!important;font-family:'DM Sans',sans-serif;}
    [data-testid="stSidebar"]{background:var(--surface)!important;border-right:1px solid var(--border);}
    h1,h2,h3{font-family:'Space Mono',monospace;}
    .stButton>button{background:var(--accent);color:#000;border:none;border-radius:4px;font-family:'Space Mono',monospace;font-weight:700;padding:.5rem 1.5rem;}
    .metric-card{background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:1.2rem;text-align:center;margin-bottom:1rem;}
    .metric-value{font-family:'Space Mono',monospace;font-size:1.6rem;font-weight:700;}
    .metric-label{color:var(--muted);font-size:.75rem;text-transform:uppercase;letter-spacing:.1em;}
    .positive{color:#00ff88;} .negative{color:#ff4d6d;}
</style>
""", unsafe_allow_html=True)

st.markdown("# 🔬 Backtest a Strategy")
st.caption("Test how a trading strategy would have performed historically. Not financial advice.")

# ── Sidebar Controls ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Settings")

    ticker = st.text_input("Stock Ticker", value="AAPL", help="e.g. AAPL, TSLA, MSFT, SPY").upper().strip()

    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", value=date.today() - timedelta(days=365*3))
    with col2:
        end_date = st.date_input("End Date", value=date.today())

    initial_capital = st.number_input("Starting Capital ($)", value=10000, min_value=100, step=500)

    strategy_name = st.selectbox("Strategy", [
        "SMA Crossover",
        "EMA Crossover",
        "RSI",
        "MACD",
        "Custom Code",
    ])

    # Strategy-specific parameters
    st.markdown("#### Strategy Parameters")
    params = {}

    if strategy_name == "SMA Crossover":
        params["short"] = st.slider("Short SMA window", 5, 50, 20)
        params["long"] = st.slider("Long SMA window", 20, 200, 50)
        st.caption("💡 Buy when short SMA crosses above long SMA.")

    elif strategy_name == "EMA Crossover":
        params["short"] = st.slider("Short EMA window", 5, 50, 12)
        params["long"] = st.slider("Long EMA window", 20, 200, 26)
        st.caption("💡 Like SMA but reacts faster to recent prices.")

    elif strategy_name == "RSI":
        params["window"] = st.slider("RSI Period", 5, 30, 14)
        params["oversold"] = st.slider("Oversold threshold", 10, 40, 30)
        params["overbought"] = st.slider("Overbought threshold", 60, 90, 70)
        st.caption("💡 Buy when oversold, sell when overbought.")

    elif strategy_name == "MACD":
        st.caption("💡 Buy when MACD crosses above signal line.")

    elif strategy_name == "Custom Code":
        st.caption("Write your own strategy below on the main page.")

    run_btn = st.button("▶ Run Backtest", use_container_width=True)

# ── Custom Code Editor (shown on main page) ───────────────────────────────────
custom_code = ""
if strategy_name == "Custom Code":
    st.markdown("### ✍️ Custom Strategy Code")
    st.markdown("""
    Write Python code that creates a `signals` variable.  
    You have access to: `df` (price data), `pd`, `np`, `calc_sma`, `calc_ema`, `calc_rsi`, `calc_macd`  
    - `signals = 1` → BUY  
    - `signals = -1` → SELL  
    - `signals = 0` → HOLD
    """)
    custom_code = st.text_area("Your Strategy Code", height=200, value="""# Example: Buy when RSI < 35, sell when RSI > 65
rsi = calc_rsi(df["Close"], window=14)
signals = pd.Series(0, index=df.index)
signals[rsi < 35] = 1   # Buy
signals[rsi > 65] = -1  # Sell
""")

# ── Run Backtest ──────────────────────────────────────────────────────────────
if run_btn:
    with st.spinner(f"Fetching data for {ticker}..."):
        df = get_stock_data(str(ticker), str(start_date), str(end_date))

    if df.empty:
        st.stop()

    # Get stock info
    info = get_ticker_info(ticker)
    st.markdown(f"**{info['name']}** · {info['sector']} · {ticker}")
    st.markdown("---")

    # Generate signals based on chosen strategy
    with st.spinner("Running backtest..."):
        try:
            if strategy_name == "SMA Crossover":
                signals = strategy_sma_crossover(df, params["short"], params["long"])
            elif strategy_name == "EMA Crossover":
                signals = strategy_ema_crossover(df, params["short"], params["long"])
            elif strategy_name == "RSI":
                signals = strategy_rsi(df, params["window"], params["oversold"], params["overbought"])
            elif strategy_name == "MACD":
                signals = strategy_macd(df)
            elif strategy_name == "Custom Code":
                signals = strategy_custom(df, custom_code)

            result = run_backtest(df, signals, float(initial_capital))

        except Exception as e:
            st.error(f"Error running backtest: {e}")
            st.stop()

    metrics = result["metrics"]
    portfolio = result["portfolio"]
    trades = result["trades"]

    # ── Metrics Row ───────────────────────────────────────────────────────────
    st.markdown("### 📊 Results")
    m1, m2, m3, m4, m5 = st.columns(5)

    def metric_card(label, value, is_pct=False, invert=False):
        """Helper to render a styled metric card."""
        if is_pct:
            cls = "negative" if (value < 0 if not invert else value > 0) else "positive"
            display = f"{value:+.2f}%"
        else:
            cls = ""
            display = value
        return f"""
        <div class="metric-card">
            <div class="metric-value {cls}">{display}</div>
            <div class="metric-label">{label}</div>
        </div>"""

    with m1:
        st.markdown(metric_card("Total Return", metrics["total_return"], is_pct=True), unsafe_allow_html=True)
    with m2:
        st.markdown(metric_card("Buy & Hold", metrics["bh_return"], is_pct=True), unsafe_allow_html=True)
    with m3:
        st.markdown(metric_card("Max Drawdown", metrics["max_drawdown"], is_pct=True, invert=True), unsafe_allow_html=True)
    with m4:
        final = metrics["final_value"]
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">${final:,.0f}</div>
            <div class="metric-label">Final Value</div>
        </div>""", unsafe_allow_html=True)
    with m5:
        wr = metrics["win_rate"]
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value {'positive' if wr >= 50 else 'negative'}">{wr:.0f}%</div>
            <div class="metric-label">Win Rate ({metrics['num_trades']} trades)</div>
        </div>""", unsafe_allow_html=True)

    # ── Charts ────────────────────────────────────────────────────────────────
    st.plotly_chart(plot_price_and_signals(df, trades, f"{ticker} — {strategy_name}"), use_container_width=True)
    st.plotly_chart(plot_portfolio_vs_bh(portfolio, df, float(initial_capital)), use_container_width=True)

    # Show RSI or MACD chart if relevant
    if strategy_name == "RSI":
        rsi_series = calc_rsi(df["Close"], params["window"])
        st.plotly_chart(plot_rsi(df, rsi_series), use_container_width=True)
    elif strategy_name == "MACD":
        macd_line, signal_line, histogram = calc_macd(df["Close"])
        st.plotly_chart(plot_macd(df, macd_line, signal_line, histogram), use_container_width=True)

    # ── Trade Log ─────────────────────────────────────────────────────────────
    if not trades.empty:
        with st.expander("📋 View Trade Log"):
            st.dataframe(trades.set_index("date"), use_container_width=True)

    # ── Save results to session state for AI Assistant ────────────────────────
    st.session_state["last_backtest"] = {
        "ticker": ticker,
        "strategy": strategy_name,
        "metrics": metrics,
        "params": params,
    }
    st.success("✅ Done! Head to the **AI Assistant** page to get this explained.")

else:
    st.info("👈 Configure your settings in the sidebar and hit **Run Backtest** to get started.")
