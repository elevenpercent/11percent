import streamlit as st

st.set_page_config(page_title="Learn | BacktestFree", page_icon="📚", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;600&display=swap');
    :root { --accent:#ffd700; --bg:#0d0f14; --surface:#161920; --border:#2a2d38; --muted:#6b7280; }
    html,body,[data-testid="stAppViewContainer"]{background:var(--bg)!important;color:#e8eaf0!important;font-family:'DM Sans',sans-serif;}
    [data-testid="stSidebar"]{background:var(--surface)!important;border-right:1px solid var(--border);}
    h1,h2,h3,h4{font-family:'Space Mono',monospace;}
    .stButton>button{background:var(--accent);color:#000;border:none;border-radius:4px;font-family:'Space Mono',monospace;font-weight:700;}
    .learn-card{background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:1.5rem;margin-bottom:1.5rem;}
    .tag{display:inline-block;padding:.2rem .7rem;border-radius:20px;font-size:.75rem;font-weight:600;margin-right:.4rem;font-family:'Space Mono',monospace;}
    .tag-easy{background:#00ff8822;color:#00ff88;border:1px solid #00ff8844;}
    .tag-medium{background:#ffd70022;color:#ffd700;border:1px solid #ffd70044;}
    .tag-hard{background:#ff4d6d22;color:#ff4d6d;border:1px solid #ff4d6d44;}
</style>
""", unsafe_allow_html=True)

st.markdown("# 📚 Learn Trading Strategies")
st.caption("Understand how each strategy works before you backtest it.")

# ── SMA Crossover ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="learn-card">
    <h3>📈 SMA Crossover (Simple Moving Average)</h3>
    <span class="tag tag-easy">Beginner Friendly</span>
    <span class="tag tag-easy">Trend Following</span>
</div>
""", unsafe_allow_html=True)

with st.expander("Learn about SMA Crossover"):
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **What is it?**  
        A Simple Moving Average (SMA) is just the average closing price over a set number of days.
        For example, the 20-day SMA is the average price of the last 20 days.

        **How does the strategy work?**  
        You use TWO moving averages — a short one (e.g. 20 days) and a long one (e.g. 50 days).
        - When the **short SMA crosses ABOVE** the long SMA → **BUY** signal 📈
        - When the **short SMA crosses BELOW** the long SMA → **SELL** signal 📉

        This is called a "Golden Cross" (buy) and "Death Cross" (sell).
        """)
    with col2:
        st.markdown("""
        **Best used when:**
        - Markets are trending strongly (up or down)
        - You want a simple, rules-based approach

        **Limitations:**
        - Lags behind price (it's based on past data)
        - Can give many false signals in sideways/choppy markets
        - Can miss the start and end of trends

        **Good starting parameters:**
        - Short window: 20 days
        - Long window: 50 days
        """)

# ── EMA Crossover ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="learn-card">
    <h3>⚡ EMA Crossover (Exponential Moving Average)</h3>
    <span class="tag tag-easy">Beginner Friendly</span>
    <span class="tag tag-easy">Trend Following</span>
</div>
""", unsafe_allow_html=True)

with st.expander("Learn about EMA Crossover"):
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **What is it?**  
        Similar to SMA, but the EMA gives **more weight to recent prices**.
        This means it reacts faster to new price movements.

        **How does the strategy work?**  
        Same logic as SMA crossover, but faster:
        - Short EMA crosses above long EMA → **BUY** 📈  
        - Short EMA crosses below long EMA → **SELL** 📉

        The most famous version is the **MACD** (12-day EMA vs 26-day EMA).
        """)
    with col2:
        st.markdown("""
        **Best used when:**
        - You want to catch trends earlier than SMA
        - Volatile markets where speed matters

        **Limitations:**
        - More sensitive = more false signals
        - Still a lagging indicator

        **Good starting parameters:**
        - Short window: 12 days
        - Long window: 26 days
        """)

# ── RSI ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="learn-card">
    <h3>📊 RSI (Relative Strength Index)</h3>
    <span class="tag tag-medium">Intermediate</span>
    <span class="tag tag-medium">Mean Reversion</span>
</div>
""", unsafe_allow_html=True)

with st.expander("Learn about RSI"):
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **What is it?**  
        RSI measures how fast and how much a stock has moved recently.
        It produces a value between **0 and 100**.

        **How to read it:**
        - RSI **above 70** = stock is *overbought* (might drop soon) → **SELL**
        - RSI **below 30** = stock is *oversold* (might bounce back) → **BUY**

        **How does the strategy work?**  
        The idea is "mean reversion" — prices that move too far in one direction tend to snap back.
        """)
    with col2:
        st.markdown("""
        **Best used when:**
        - Markets are ranging (not strongly trending)
        - You want to buy dips and sell peaks

        **Limitations:**
        - In strong trends, RSI can stay overbought/oversold for a long time
        - Can give early signals — stock may keep falling after RSI hits 30

        **Good starting parameters:**
        - RSI Period: 14 days
        - Oversold: 30
        - Overbought: 70
        """)

# ── MACD ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="learn-card">
    <h3>🔀 MACD (Moving Average Convergence Divergence)</h3>
    <span class="tag tag-medium">Intermediate</span>
    <span class="tag tag-medium">Momentum</span>
</div>
""", unsafe_allow_html=True)

with st.expander("Learn about MACD"):
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **What is it?**  
        MACD combines two EMAs to measure momentum.
        It has three parts:
        1. **MACD Line** = 12-day EMA minus 26-day EMA
        2. **Signal Line** = 9-day EMA of the MACD Line
        3. **Histogram** = difference between MACD and Signal line

        **How does the strategy work?**
        - MACD crosses **above** signal line → **BUY** 📈
        - MACD crosses **below** signal line → **SELL** 📉
        """)
    with col2:
        st.markdown("""
        **Best used when:**
        - Identifying momentum shifts
        - Confirming trend direction

        **Limitations:**
        - Still a lagging indicator
        - Less useful in sideways markets
        - Multiple components can be confusing at first

        **Pro tip:**
        - A rising histogram = strengthening momentum
        - A shrinking histogram = momentum fading (watch for crossover)
        """)

# ── Custom Code ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="learn-card">
    <h3>🧑‍💻 Custom Strategy Code</h3>
    <span class="tag tag-hard">Advanced</span>
    <span class="tag tag-hard">Python Required</span>
</div>
""", unsafe_allow_html=True)

with st.expander("Learn how to write custom strategies"):
    st.markdown("""
    **What can you build?**  
    Anything you can express in Python! Combine multiple indicators, add filters, create complex entry/exit rules.

    **The rules:**
    - Your code must create a variable called `signals`
    - `signals` must be a `pd.Series` with values: `1` (buy), `-1` (sell), `0` (hold)
    - It must have the same index as `df`

    **Available tools in your code:**
    """)

    st.code("""
# Available variables:
# df        → price DataFrame (columns: Open, High, Low, Close, Volume)
# pd        → pandas
# np        → numpy
# calc_sma(series, window)         → Simple Moving Average
# calc_ema(series, window)         → Exponential Moving Average
# calc_rsi(series, window)         → RSI values
# calc_macd(series, fast, slow, signal) → returns (macd, signal, histogram)

# ── Example: RSI + SMA Filter ─────────────────────────────────────
# Only buy when RSI is oversold AND price is above the 50-day SMA
# (The SMA filter avoids buying in a downtrend)

rsi = calc_rsi(df["Close"], window=14)
sma_50 = calc_sma(df["Close"], window=50)

signals = pd.Series(0, index=df.index)

# Buy: RSI oversold AND price above 50-day SMA
buy_condition = (rsi < 30) & (df["Close"] > sma_50)
signals[buy_condition] = 1

# Sell: RSI overbought
signals[rsi > 70] = -1
    """, language="python")

# ── Key concepts ──────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("## 📖 Key Concepts to Understand")

c1, c2 = st.columns(2)
with c1:
    st.markdown("""
    **Total Return**  
    How much your strategy made (or lost) as a percentage of your starting capital.  
    e.g. +32% means a $10,000 investment became $13,200.

    **Buy & Hold Return**  
    What you would have made by just buying at the start and holding until the end.  
    Your strategy should ideally beat this!

    **Max Drawdown**  
    The biggest drop from a peak to a valley during your backtest.  
    e.g. -25% means at some point your portfolio dropped 25% from its highest point.
    Lower is better.
    """)

with c2:
    st.markdown("""
    **Win Rate**  
    The percentage of your trades that were profitable.  
    Note: a 40% win rate can still be profitable if your wins are much bigger than your losses.

    **Number of Trades**  
    How many times the strategy bought and sold.  
    More trades = more transaction costs in real life (not simulated here).

    **Overfitting Warning ⚠️**  
    If you tune parameters too perfectly to past data, the strategy may fail on future data.  
    Always test your strategy on data it hasn't "seen" before.
    """)

st.markdown("---")
st.info("💡 **Ready to try?** Head to the **Backtest** page and test one of these strategies on a real stock!")
