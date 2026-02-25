import streamlit as st
import yfinance as yf
import pandas_ta as ta
import plotly.graph_objects as go

st.title("📈 Strategy Backtester")

# Sidebar Controls
symbol = st.sidebar.text_input("Ticker (e.g., TSLA)", "AAPL").upper()
strat_type = st.sidebar.selectbox("Strategy", ["SMA Crossover", "RSI"])
period = st.sidebar.selectbox("History", ["1y", "2y", "5y"])

# Fetch Data
df = yf.download(symbol, period=period)

if not df.empty:
    # Logic
    if strat_type == "SMA Crossover":
        df['Fast'] = ta.sma(df['Close'], length=20)
        df['Slow'] = ta.sma(df['Close'], length=50)
        df['Signal'] = 0
        df.loc[df['Fast'] > df['Slow'], 'Signal'] = 1
    else:
        df['RSI'] = ta.rsi(df['Close'], length=14)
        df['Signal'] = 0
        df.loc[df['RSI'] < 30, 'Signal'] = 1  # Buy when oversold
        df.loc[df['RSI'] > 70, 'Signal'] = 0  # Sell when overbought

    df['Entry'] = df['Signal'].diff()

    # Charting
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"))
    
    # Add signals
    buys = df[df['Entry'] == 1]
    sells = df[df['Entry'] == -1]
    fig.add_trace(go.Scatter(x=buys.index, y=buys['Low']*0.97, mode='markers', marker=dict(symbol='triangle-up', size=12, color='green'), name='Buy'))
    fig.add_trace(go.Scatter(x=sells.index, y=sells['High']*1.03, mode='markers', marker=dict(symbol='triangle-down', size=12, color='red'), name='Sell'))

    fig.update_layout(height=600, template="plotly_dark", xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)
    
    # Financial Stats
    returns = (df['Close'].pct_change() * df['Signal'].shift(1)).sum()
    st.metric("Total Strategy Return", f"{returns:.2%}")
