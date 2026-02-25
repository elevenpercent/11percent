import streamlit as st

st.set_page_config(page_title="Learn Strategies", layout="wide")

st.title("📚 Strategy Library")
st.write("Understand the math and logic behind the indicators used in our backtester.")

tab1, tab2 = st.tabs(["Moving Averages (SMA)", "Relative Strength Index (RSI)"])

with tab1:
    st.subheader("Simple Moving Average (SMA)")
    st.write("""
    The **Simple Moving Average** is the average price of a stock over a specific number of days.
    - **Fast SMA (e.g., 20 day):** Reacts quickly to price changes.
    - **Slow SMA (e.g., 50 day):** Shows the longer-term trend.
    
    **The Strategy:**
    - **Golden Cross (Buy):** When the Fast SMA crosses *above* the Slow SMA. This suggests upward momentum.
    - **Death Cross (Sell):** When the Fast SMA crosses *below* the Slow SMA. This suggests downward momentum.
    """)
    st.info("💡 Tip: SMAs work best in trending markets, but can give 'false signals' when the market is moving sideways.")

with tab2:
    st.subheader("Relative Strength Index (RSI)")
    st.write("""
    The **RSI** is a momentum oscillator that measures the speed and change of price movements. It ranges from 0 to 100.
    
    **How to read it:**
    - **Oversold (< 30):** The stock may be undervalued or 'due' for a bounce. This is often a **Buy** signal.
    - **Overbought (> 70):** The stock may be overvalued or 'due' for a pullback. This is often a **Sell** signal.
    """)
    st.warning("⚠️ Warning: A stock can stay 'Overbought' for a long time during a strong bull run. Don't rely on RSI alone!")

st.divider()
st.subheader("🤖 How to use the AI Assistant")
st.write("""
1. Go to the **Assistant** page.
2. Type a ticker like `NVDA` or `BTC`.
3. Ask: *"What is the current RSI trend for this stock?"* or *"Explain the risk of a 50-day SMA crossover."*
""")
