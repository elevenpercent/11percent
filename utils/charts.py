"""
Chart rendering for 11% platform.
All charts use the shared dark theme from utils/styles.py
"""
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.styles import PLOTLY_THEME


def _base_fig(**kwargs) -> go.Figure:
    fig = go.Figure(**kwargs)
    fig.update_layout(**PLOTLY_THEME)
    return fig


# ─────────────────────────────────────────────────────────────────
# CANDLESTICK + SIGNALS
# ─────────────────────────────────────────────────────────────────

def chart_candles(df: pd.DataFrame, trades: pd.DataFrame = None,
                  overlays: dict = None, title: str = "") -> go.Figure:
    """
    Candlestick chart with optional buy/sell markers and overlay indicators.
    overlays: dict of {"Label": pd.Series} to draw on price chart
    """
    fig = _base_fig()
    fig.add_trace(go.Candlestick(
        x=df.index, open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"],
        name="Price",
        increasing_line_color="#00d68f", increasing_fillcolor="#00d68f22",
        decreasing_line_color="#ff4757", decreasing_fillcolor="#ff475722",
    ))

    COLORS = ["#4da6ff", "#f0b429", "#b388ff", "#ff9f43", "#00d68f"]
    if overlays:
        for i, (label, series) in enumerate(overlays.items()):
            fig.add_trace(go.Scatter(
                x=series.index, y=series,
                mode="lines", name=label,
                line=dict(color=COLORS[i % len(COLORS)], width=1.5),
            ))

    if trades is not None and not trades.empty:
        buys  = trades[trades["action"] == "BUY"]
        sells = trades[trades["action"].str.contains("SELL")]
        if not buys.empty:
            fig.add_trace(go.Scatter(
                x=buys["date"], y=buys["price"], mode="markers", name="Buy",
                marker=dict(symbol="triangle-up", size=12, color="#00d68f",
                            line=dict(color="#00d68f", width=1)),
            ))
        if not sells.empty:
            fig.add_trace(go.Scatter(
                x=sells["date"], y=sells["price"], mode="markers", name="Sell",
                marker=dict(symbol="triangle-down", size=12, color="#ff4757",
                            line=dict(color="#ff4757", width=1)),
            ))

    fig.update_layout(title=title, xaxis_rangeslider_visible=False, height=480,
                      xaxis_title="", yaxis_title="Price")
    return fig


# ─────────────────────────────────────────────────────────────────
# PORTFOLIO vs BUY & HOLD
# ─────────────────────────────────────────────────────────────────

def chart_portfolio(portfolio: pd.DataFrame, df: pd.DataFrame, initial_capital: float) -> go.Figure:
    bh = (df["Close"] / float(df["Close"].iloc[0])) * initial_capital
    fig = _base_fig()
    fig.add_trace(go.Scatter(
        x=portfolio.index, y=portfolio["value"],
        mode="lines", name="Strategy",
        line=dict(color="#f0b429", width=2),
        fill="tozeroy", fillcolor="rgba(240,180,41,0.05)",
    ))
    fig.add_trace(go.Scatter(
        x=bh.index, y=bh,
        mode="lines", name="Buy & Hold",
        line=dict(color="#4da6ff", width=1.5, dash="dot"),
    ))
    fig.update_layout(title="Portfolio Value vs Buy & Hold", height=320, yaxis_title="Value (USD)")
    return fig


# ─────────────────────────────────────────────────────────────────
# RSI CHART
# ─────────────────────────────────────────────────────────────────

def chart_rsi(rsi_series: pd.Series, oversold=30, overbought=70) -> go.Figure:
    fig = _base_fig()
    fig.add_trace(go.Scatter(
        x=rsi_series.index, y=rsi_series, mode="lines", name="RSI",
        line=dict(color="#f0b429", width=1.8),
    ))
    fig.add_hrect(y0=overbought, y1=100, fillcolor="rgba(255,71,87,0.07)", line_width=0)
    fig.add_hrect(y0=0, y1=oversold, fillcolor="rgba(0,214,143,0.07)", line_width=0)
    fig.add_hline(y=overbought, line_dash="dash", line_color="#ff4757", line_width=1,
                  annotation_text=f"Overbought ({overbought})", annotation_font_size=10)
    fig.add_hline(y=oversold, line_dash="dash", line_color="#00d68f", line_width=1,
                  annotation_text=f"Oversold ({oversold})", annotation_font_size=10)
    fig.update_layout(title="RSI", height=220, yaxis=dict(range=[0, 100], **PLOTLY_THEME["yaxis"]))
    return fig


# ─────────────────────────────────────────────────────────────────
# STOCH RSI CHART
# ─────────────────────────────────────────────────────────────────

def chart_stoch_rsi(k: pd.Series, d: pd.Series) -> go.Figure:
    fig = _base_fig()
    fig.add_trace(go.Scatter(x=k.index, y=k, mode="lines", name="%K", line=dict(color="#4da6ff", width=1.5)))
    fig.add_trace(go.Scatter(x=d.index, y=d, mode="lines", name="%D", line=dict(color="#f0b429", width=1.5)))
    fig.add_hline(y=80, line_dash="dash", line_color="#ff4757", line_width=1)
    fig.add_hline(y=20, line_dash="dash", line_color="#00d68f", line_width=1)
    fig.update_layout(title="Stochastic RSI", height=220, yaxis=dict(range=[0, 100], **PLOTLY_THEME["yaxis"]))
    return fig


# ─────────────────────────────────────────────────────────────────
# MACD CHART
# ─────────────────────────────────────────────────────────────────

def chart_macd(macd_line: pd.Series, signal_line: pd.Series, histogram: pd.Series) -> go.Figure:
    fig = _base_fig()
    colors = ["#00d68f" if v >= 0 else "#ff4757" for v in histogram.fillna(0)]
    fig.add_trace(go.Bar(x=histogram.index, y=histogram, name="Histogram", marker_color=colors, opacity=0.7))
    fig.add_trace(go.Scatter(x=macd_line.index, y=macd_line, mode="lines", name="MACD",
                             line=dict(color="#4da6ff", width=1.8)))
    fig.add_trace(go.Scatter(x=signal_line.index, y=signal_line, mode="lines", name="Signal",
                             line=dict(color="#f0b429", width=1.5)))
    fig.update_layout(title="MACD", height=220, barmode="relative")
    return fig


# ─────────────────────────────────────────────────────────────────
# BOLLINGER BANDS (overlay on price)
# ─────────────────────────────────────────────────────────────────

def chart_bollinger(df: pd.DataFrame, bb: dict) -> go.Figure:
    fig = _base_fig()
    fig.add_trace(go.Candlestick(
        x=df.index, open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"],
        name="Price",
        increasing_line_color="#00d68f", decreasing_line_color="#ff4757",
    ))
    fig.add_trace(go.Scatter(x=bb["upper"].index, y=bb["upper"], mode="lines", name="Upper",
                             line=dict(color="#4da6ff", width=1, dash="dot")))
    fig.add_trace(go.Scatter(x=bb["middle"].index, y=bb["middle"], mode="lines", name="Middle",
                             line=dict(color="#f0b429", width=1.5)))
    fig.add_trace(go.Scatter(x=bb["lower"].index, y=bb["lower"], mode="lines", name="Lower",
                             line=dict(color="#4da6ff", width=1, dash="dot"),
                             fill="tonexty", fillcolor="rgba(77,166,255,0.05)"))
    fig.update_layout(title="Bollinger Bands", xaxis_rangeslider_visible=False, height=400)
    return fig


# ─────────────────────────────────────────────────────────────────
# SUPERTREND (overlay on price)
# ─────────────────────────────────────────────────────────────────

def chart_supertrend(df: pd.DataFrame, st_data: dict) -> go.Figure:
    fig = _base_fig()
    fig.add_trace(go.Candlestick(
        x=df.index, open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"],
        name="Price",
        increasing_line_color="#00d68f", decreasing_line_color="#ff4757",
    ))
    st_line = st_data["supertrend"]
    direction = st_data["direction"]
    bull = st_line.where(direction == 1)
    bear = st_line.where(direction == -1)
    fig.add_trace(go.Scatter(x=bull.index, y=bull, mode="lines", name="Bullish",
                             line=dict(color="#00d68f", width=2)))
    fig.add_trace(go.Scatter(x=bear.index, y=bear, mode="lines", name="Bearish",
                             line=dict(color="#ff4757", width=2)))
    fig.update_layout(title="SuperTrend", xaxis_rangeslider_visible=False, height=400)
    return fig


# ─────────────────────────────────────────────────────────────────
# ICHIMOKU
# ─────────────────────────────────────────────────────────────────

def chart_ichimoku(df: pd.DataFrame, ichi: dict) -> go.Figure:
    fig = _base_fig()
    fig.add_trace(go.Candlestick(
        x=df.index, open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"],
        name="Price",
        increasing_line_color="#00d68f", decreasing_line_color="#ff4757",
    ))
    # Cloud fill
    fig.add_trace(go.Scatter(x=ichi["senkou_span_a"].index, y=ichi["senkou_span_a"],
                             mode="lines", name="Span A", line=dict(color="#00d68f", width=0),
                             fill=None))
    fig.add_trace(go.Scatter(x=ichi["senkou_span_b"].index, y=ichi["senkou_span_b"],
                             mode="lines", name="Span B", line=dict(color="#ff4757", width=0),
                             fill="tonexty", fillcolor="rgba(77,166,255,0.08)"))
    fig.add_trace(go.Scatter(x=ichi["tenkan_sen"].index, y=ichi["tenkan_sen"],
                             mode="lines", name="Tenkan", line=dict(color="#f0b429", width=1.5)))
    fig.add_trace(go.Scatter(x=ichi["kijun_sen"].index, y=ichi["kijun_sen"],
                             mode="lines", name="Kijun", line=dict(color="#4da6ff", width=1.5)))
    fig.update_layout(title="Ichimoku Cloud", xaxis_rangeslider_visible=False, height=420)
    return fig


# ─────────────────────────────────────────────────────────────────
# REPLAY CHART (single candle reveal)
# ─────────────────────────────────────────────────────────────────

def chart_replay(df_visible: pd.DataFrame, user_trades: list = None,
                 overlays: dict = None) -> go.Figure:
    """Chart for the replay page — only shows candles up to current index."""
    fig = chart_candles(df_visible, overlays=overlays, title="Chart Replay")

    if user_trades:
        buy_dates  = [t["date"] for t in user_trades if t["action"] == "BUY"]
        buy_prices = [t["price"] for t in user_trades if t["action"] == "BUY"]
        sell_dates  = [t["date"] for t in user_trades if t["action"] == "SELL"]
        sell_prices = [t["price"] for t in user_trades if t["action"] == "SELL"]

        if buy_dates:
            fig.add_trace(go.Scatter(
                x=buy_dates, y=buy_prices, mode="markers", name="Your Buy",
                marker=dict(symbol="star", size=14, color="#f0b429",
                            line=dict(color="#f0b429", width=1)),
            ))
        if sell_dates:
            fig.add_trace(go.Scatter(
                x=sell_dates, y=sell_prices, mode="markers", name="Your Sell",
                marker=dict(symbol="x", size=14, color="#ff4757",
                            line=dict(color="#ff4757", width=2)),
            ))

    fig.update_layout(height=520)
    return fig
