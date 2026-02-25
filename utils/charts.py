import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


DARK_THEME = dict(
    paper_bgcolor="#0d0f14",
    plot_bgcolor="#0d0f14",
    font_color="#e8eaf0",
    gridcolor="#2a2d38",
)


def plot_price_and_signals(df: pd.DataFrame, trades: pd.DataFrame, title: str = "Price & Trades") -> go.Figure:
    """Candlestick chart with buy/sell markers overlaid."""
    fig = go.Figure()

    # Candlestick
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df["Open"],
        high=df["High"],
        low=df["Low"],
        close=df["Close"],
        name="Price",
        increasing_line_color="#00ff88",
        decreasing_line_color="#ff4d6d",
    ))

    if not trades.empty:
        buys = trades[trades["action"] == "BUY"]
        sells = trades[trades["action"].str.contains("SELL")]

        # Buy markers
        fig.add_trace(go.Scatter(
            x=buys["date"], y=buys["price"],
            mode="markers",
            marker=dict(symbol="triangle-up", size=14, color="#00ff88"),
            name="Buy",
        ))

        # Sell markers
        fig.add_trace(go.Scatter(
            x=sells["date"], y=sells["price"],
            mode="markers",
            marker=dict(symbol="triangle-down", size=14, color="#ff4d6d"),
            name="Sell",
        ))

    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title="Price (USD)",
        xaxis_rangeslider_visible=False,
        height=450,
        **DARK_THEME,
    )
    return fig


def plot_portfolio_vs_bh(portfolio: pd.DataFrame, df: pd.DataFrame, initial_capital: float) -> go.Figure:
    """Portfolio value vs Buy & Hold benchmark."""
    # Normalise buy & hold to same starting capital
    bh_values = (df["Close"] / float(df["Close"].iloc[0])) * initial_capital

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=portfolio.index, y=portfolio["value"],
        mode="lines", name="Strategy",
        line=dict(color="#00ff88", width=2),
    ))
    fig.add_trace(go.Scatter(
        x=bh_values.index, y=bh_values,
        mode="lines", name="Buy & Hold",
        line=dict(color="#0066ff", width=2, dash="dash"),
    ))
    fig.update_layout(
        title="Portfolio Value vs Buy & Hold",
        xaxis_title="Date",
        yaxis_title="Value (USD)",
        height=350,
        **DARK_THEME,
    )
    return fig


def plot_rsi(df: pd.DataFrame, rsi: pd.Series) -> go.Figure:
    """RSI indicator chart with overbought/oversold zones."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=rsi.index, y=rsi,
        mode="lines", name="RSI",
        line=dict(color="#ffd700", width=2),
    ))
    fig.add_hline(y=70, line_dash="dash", line_color="#ff4d6d", annotation_text="Overbought (70)")
    fig.add_hline(y=30, line_dash="dash", line_color="#00ff88", annotation_text="Oversold (30)")
    fig.update_layout(
        title="RSI Indicator",
        yaxis_title="RSI",
        height=250,
        **DARK_THEME,
    )
    return fig


def plot_macd(df: pd.DataFrame, macd_line: pd.Series, signal_line: pd.Series, histogram: pd.Series) -> go.Figure:
    """MACD chart with histogram."""
    fig = make_subplots(rows=1, cols=1)
    fig.add_trace(go.Scatter(x=macd_line.index, y=macd_line, name="MACD", line=dict(color="#00ff88")))
    fig.add_trace(go.Scatter(x=signal_line.index, y=signal_line, name="Signal", line=dict(color="#ff4d6d")))
    colors = ["#00ff88" if v >= 0 else "#ff4d6d" for v in histogram]
    fig.add_trace(go.Bar(x=histogram.index, y=histogram, name="Histogram", marker_color=colors))
    fig.update_layout(title="MACD", height=250, **DARK_THEME)
    return fig
