"""
Chart rendering for 11% platform.
TradingView-style dark charts with full drawing tools, multi-panel sub-charts.
"""
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.styles import PLOTLY_THEME

# ── Shared config ────────────────────────────────────────────────────────────
_BG       = "#06080c"
_PANEL    = "#0c1018"
_GRID     = "#111927"
_BORDER   = "#1a2235"
_TEXT_DIM = "#3a4a5e"
_TEXT     = "#8896ab"
_GREEN    = "#00e676"
_RED      = "#ff3d57"
_BLUE     = "#4da6ff"
_YELLOW   = "#ffd166"
_PURPLE   = "#b388ff"
_ORANGE   = "#ff9f43"

OVERLAY_COLORS = [_BLUE, _YELLOW, _PURPLE, _ORANGE, "#00e5ff", "#ea80fc", "#69ff47"]

# Full drawing toolbar config — exposes every TradingView-like tool Plotly supports
TV_CONFIG = dict(
    displayModeBar=True,
    displaylogo=False,
    scrollZoom=True,
    modeBarButtonsToAdd=[
        "drawline",
        "drawopenpath",
        "drawclosedpath",
        "drawcircle",
        "drawrect",
        "eraseshape",
    ],
    modeBarButtonsToRemove=["autoScale2d", "lasso2d", "select2d"],
    toImageButtonOptions=dict(format="png", filename="11pct_chart", scale=2),
)

def _theme(fig, height=520, title="", rangeslider=False):
    """Apply shared dark theme to any figure."""
    fig.update_layout(
        paper_bgcolor=_BG,
        plot_bgcolor=_PANEL,
        font=dict(family="IBM Plex Mono", size=11, color=_TEXT),
        height=height,
        margin=dict(l=8, r=8, t=44 if title else 28, b=8),
        xaxis_rangeslider_visible=rangeslider,
        showlegend=True,
        legend=dict(
            bgcolor="rgba(12,16,24,0.9)",
            bordercolor=_BORDER,
            borderwidth=1,
            font=dict(size=10),
            orientation="h",
            y=1.02, x=0,
        ),
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor=_PANEL,
            bordercolor=_BORDER,
            font=dict(family="IBM Plex Mono", size=11),
        ),
        dragmode="pan",
        newshape=dict(
            line=dict(color=_YELLOW, width=2),
            fillcolor="rgba(255,209,102,0.08)",
        ),
    )
    if title:
        fig.update_layout(title=dict(
            text=title,
            font=dict(family="IBM Plex Mono", size=13, color=_TEXT),
            x=0.01,
        ))
    return fig


def _style_axes(fig, n_rows=1):
    axis_style = dict(
        gridcolor=_GRID,
        linecolor=_BORDER,
        tickfont=dict(size=10, color=_TEXT_DIM),
        zeroline=False,
        showgrid=True,
    )
    for i in range(1, n_rows + 1):
        fig.update_xaxes(**axis_style, row=i, col=1)
        fig.update_yaxes(**axis_style, row=i, col=1)
    return fig


def _candle_trace(df, name="Price"):
    return go.Candlestick(
        x=df.index,
        open=df["Open"], high=df["High"],
        low=df["Low"],   close=df["Close"],
        name=name,
        increasing=dict(line=dict(color=_GREEN, width=1), fillcolor=_GREEN),
        decreasing=dict(line=dict(color=_RED,   width=1), fillcolor=_RED),
        whiskerwidth=0.3,
        showlegend=False,
    )


# ── Multi-panel builder ──────────────────────────────────────────────────────

def build_tv_chart(
    df,
    title="",
    overlays=None,       # dict {label: pd.Series}  — plotted on price panel
    sub_panels=None,     # list of dicts: {label, series/dict, type, color}
    trades=None,         # pd.DataFrame with columns: date, action, price
    vline_date=None,     # highlight current bar (replay)
    height_base=520,
):
    """
    Master chart builder used by every page.
    Returns (fig, config) ready for st.plotly_chart(fig, config=config).
    """
    n_sub = len(sub_panels) if sub_panels else 0
    n_rows = 1 + n_sub

    if n_sub > 0:
        heights = [0.58] + [0.42 / n_sub] * n_sub
    else:
        heights = [1.0]

    fig = make_subplots(
        rows=n_rows, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.018,
        row_heights=heights,
    )

    # ── Price candles ──
    fig.add_trace(_candle_trace(df), row=1, col=1)

    # ── Overlays ──
    oi = 0
    if overlays:
        for label, series in overlays.items():
            if series is None or (hasattr(series, "dropna") and series.dropna().empty):
                continue
            color = OVERLAY_COLORS[oi % len(OVERLAY_COLORS)]
            fig.add_trace(go.Scatter(
                x=series.index, y=series,
                mode="lines", name=label,
                line=dict(color=color, width=1.6),
                opacity=0.9,
            ), row=1, col=1)
            oi += 1

    # ── Trade markers ──
    if trades is not None and not trades.empty:
        buys  = trades[trades["action"] == "BUY"]
        sells = trades[trades["action"].str.contains("SELL", na=False)]
        if not buys.empty:
            fig.add_trace(go.Scatter(
                x=buys["date"], y=buys["price"],
                mode="markers+text", name="Buy",
                text=["B"] * len(buys), textposition="middle center",
                textfont=dict(color="#000", size=9, family="IBM Plex Mono"),
                marker=dict(symbol="circle", size=20, color=_GREEN,
                            line=dict(color="#000", width=1)),
            ), row=1, col=1)
        if not sells.empty:
            fig.add_trace(go.Scatter(
                x=sells["date"], y=sells["price"],
                mode="markers+text", name="Sell",
                text=["S"] * len(sells), textposition="middle center",
                textfont=dict(color="#fff", size=9, family="IBM Plex Mono"),
                marker=dict(symbol="circle", size=20, color=_RED,
                            line=dict(color="#000", width=1)),
            ), row=1, col=1)

    # ── Current-bar vline (replay) ──
    if vline_date is not None:
        fig.add_vline(
            x=vline_date, line_dash="dot",
            line_color="rgba(255,255,255,0.15)", line_width=1,
        )

    # ── Sub-panels ──
    for si, panel in enumerate(sub_panels or []):
        row = 2 + si
        ptype  = panel.get("type", "line")
        label  = panel.get("label", "")
        color  = panel.get("color", _BLUE)
        data   = panel.get("data")

        if ptype == "rsi":
            fig.add_trace(go.Scatter(
                x=data.index, y=data, mode="lines", name="RSI",
                line=dict(color=_YELLOW, width=1.5),
            ), row=row, col=1)
            fig.add_hrect(y0=70, y1=100, fillcolor="rgba(255,61,87,0.05)",  line_width=0, row=row, col=1)
            fig.add_hrect(y0=0,  y1=30,  fillcolor="rgba(0,230,118,0.05)", line_width=0, row=row, col=1)
            fig.add_hline(y=70, line_dash="dot", line_color=_RED,   line_width=0.7, row=row, col=1)
            fig.add_hline(y=30, line_dash="dot", line_color=_GREEN, line_width=0.7, row=row, col=1)
            fig.update_yaxes(range=[0, 100], row=row, col=1)
            fig.update_yaxes(title_text="RSI", title_font=dict(size=9, color=_TEXT_DIM), row=row, col=1)

        elif ptype == "macd":
            md = data  # dict: macd, signal, histogram
            bar_c = [_GREEN if v >= 0 else _RED for v in md["histogram"].fillna(0)]
            fig.add_trace(go.Bar(
                x=md["histogram"].index, y=md["histogram"],
                name="Hist", marker_color=bar_c, opacity=0.6,
            ), row=row, col=1)
            fig.add_trace(go.Scatter(
                x=md["macd"].index, y=md["macd"],
                mode="lines", name="MACD", line=dict(color=_BLUE, width=1.5),
            ), row=row, col=1)
            fig.add_trace(go.Scatter(
                x=md["signal"].index, y=md["signal"],
                mode="lines", name="Signal", line=dict(color=_YELLOW, width=1.2),
            ), row=row, col=1)
            fig.update_yaxes(title_text="MACD", title_font=dict(size=9, color=_TEXT_DIM), row=row, col=1)

        elif ptype == "volume":
            vol_c = [_GREEN if c >= o else _RED
                     for c, o in zip(df["Close"], df["Open"])]
            fig.add_trace(go.Bar(
                x=df.index, y=df["Volume"],
                name="Vol", marker_color=vol_c, opacity=0.55,
            ), row=row, col=1)
            fig.update_yaxes(title_text="Vol", title_font=dict(size=9, color=_TEXT_DIM), row=row, col=1)

        elif ptype == "cci":
            fig.add_trace(go.Scatter(
                x=data.index, y=data, mode="lines", name="CCI",
                line=dict(color=_PURPLE, width=1.5),
            ), row=row, col=1)
            fig.add_hline(y=100,  line_dash="dot", line_color=_RED,   line_width=0.7, row=row, col=1)
            fig.add_hline(y=-100, line_dash="dot", line_color=_GREEN, line_width=0.7, row=row, col=1)
            fig.update_yaxes(title_text="CCI", title_font=dict(size=9, color=_TEXT_DIM), row=row, col=1)

        elif ptype == "wpr":
            fig.add_trace(go.Scatter(
                x=data.index, y=data, mode="lines", name="%R",
                line=dict(color=_ORANGE, width=1.5),
            ), row=row, col=1)
            fig.add_hline(y=-20, line_dash="dot", line_color=_RED,   line_width=0.7, row=row, col=1)
            fig.add_hline(y=-80, line_dash="dot", line_color=_GREEN, line_width=0.7, row=row, col=1)
            fig.update_yaxes(range=[-100, 0], title_text="%R",
                             title_font=dict(size=9, color=_TEXT_DIM), row=row, col=1)

        else:  # generic line
            fig.add_trace(go.Scatter(
                x=data.index, y=data, mode="lines", name=label,
                line=dict(color=color, width=1.5),
            ), row=row, col=1)
            fig.update_yaxes(title_text=label, title_font=dict(size=9, color=_TEXT_DIM), row=row, col=1)

    total_height = height_base + n_sub * 130
    _theme(fig, height=total_height, title=title)
    _style_axes(fig, n_rows=n_rows)

    return fig, TV_CONFIG


# ── Convenience wrappers used by backtest + indicator pages ──────────────────

def chart_candles(df, trades=None, overlays=None, title=""):
    fig, cfg = build_tv_chart(df, title=title, overlays=overlays, trades=trades,
                               sub_panels=[{"type":"volume","label":"Volume","data":None}])
    return fig

def chart_portfolio(portfolio, df, initial_capital):
    bh = (df["Close"] / float(df["Close"].iloc[0])) * initial_capital
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=portfolio.index, y=portfolio["value"],
        mode="lines", name="Strategy",
        line=dict(color=_YELLOW, width=2),
        fill="tozeroy", fillcolor="rgba(255,209,102,0.05)",
    ))
    fig.add_trace(go.Scatter(
        x=bh.index, y=bh,
        mode="lines", name="Buy & Hold",
        line=dict(color=_BLUE, width=1.5, dash="dot"),
    ))
    _theme(fig, height=300, title="Portfolio vs Buy & Hold")
    _style_axes(fig)
    return fig

def chart_rsi(rsi_series, oversold=30, overbought=70):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=rsi_series.index, y=rsi_series,
        mode="lines", name="RSI",
        line=dict(color=_YELLOW, width=1.8),
    ))
    fig.add_hrect(y0=overbought, y1=100, fillcolor="rgba(255,61,87,0.07)",  line_width=0)
    fig.add_hrect(y0=0,          y1=oversold, fillcolor="rgba(0,230,118,0.07)", line_width=0)
    fig.add_hline(y=overbought, line_dash="dash", line_color=_RED,   line_width=1,
                  annotation_text=f"OB {overbought}", annotation_font_size=10)
    fig.add_hline(y=oversold,   line_dash="dash", line_color=_GREEN, line_width=1,
                  annotation_text=f"OS {oversold}",  annotation_font_size=10)
    _theme(fig, height=220, title="RSI")
    _style_axes(fig)
    fig.update_yaxes(range=[0, 100])
    return fig

def chart_stoch_rsi(k, d):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=k.index, y=k, mode="lines", name="%K", line=dict(color=_BLUE,   width=1.5)))
    fig.add_trace(go.Scatter(x=d.index, y=d, mode="lines", name="%D", line=dict(color=_YELLOW, width=1.5)))
    fig.add_hline(y=80, line_dash="dash", line_color=_RED,   line_width=1)
    fig.add_hline(y=20, line_dash="dash", line_color=_GREEN, line_width=1)
    _theme(fig, height=220, title="Stoch RSI")
    _style_axes(fig)
    fig.update_yaxes(range=[0, 100])
    return fig

def chart_macd(macd_line, signal_line, histogram):
    fig = go.Figure()
    colors = [_GREEN if v >= 0 else _RED for v in histogram.fillna(0)]
    fig.add_trace(go.Bar(x=histogram.index, y=histogram, name="Hist", marker_color=colors, opacity=0.7))
    fig.add_trace(go.Scatter(x=macd_line.index,   y=macd_line,   mode="lines", name="MACD",   line=dict(color=_BLUE,   width=1.8)))
    fig.add_trace(go.Scatter(x=signal_line.index, y=signal_line, mode="lines", name="Signal", line=dict(color=_YELLOW, width=1.5)))
    _theme(fig, height=220, title="MACD")
    _style_axes(fig)
    fig.update_layout(barmode="relative")
    return fig

def chart_bollinger(df, bb):
    fig = go.Figure()
    fig.add_trace(_candle_trace(df))
    fig.add_trace(go.Scatter(x=bb["upper"].index,  y=bb["upper"],  mode="lines", name="Upper",  line=dict(color=_BLUE, width=1, dash="dot")))
    fig.add_trace(go.Scatter(x=bb["middle"].index, y=bb["middle"], mode="lines", name="Middle", line=dict(color=_YELLOW, width=1.5)))
    fig.add_trace(go.Scatter(x=bb["lower"].index,  y=bb["lower"],  mode="lines", name="Lower",  line=dict(color=_BLUE, width=1, dash="dot"),
                             fill="tonexty", fillcolor="rgba(77,166,255,0.05)"))
    _theme(fig, height=420, title="Bollinger Bands")
    _style_axes(fig)
    fig.update_layout(xaxis_rangeslider_visible=False)
    return fig

def chart_supertrend(df, st_data):
    fig = go.Figure()
    fig.add_trace(_candle_trace(df))
    bull = st_data["supertrend"].where(st_data["direction"] == 1)
    bear = st_data["supertrend"].where(st_data["direction"] == -1)
    fig.add_trace(go.Scatter(x=bull.index, y=bull, mode="lines", name="Bull ST", line=dict(color=_GREEN, width=2)))
    fig.add_trace(go.Scatter(x=bear.index, y=bear, mode="lines", name="Bear ST", line=dict(color=_RED,   width=2)))
    _theme(fig, height=420, title="SuperTrend")
    _style_axes(fig)
    fig.update_layout(xaxis_rangeslider_visible=False)
    return fig

def chart_ichimoku(df, ichi):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ichi["senkou_span_a"].index, y=ichi["senkou_span_a"],
                             mode="lines", name="Span A", line=dict(color=_GREEN, width=0)))
    fig.add_trace(go.Scatter(x=ichi["senkou_span_b"].index, y=ichi["senkou_span_b"],
                             mode="lines", name="Span B", line=dict(color=_RED, width=0),
                             fill="tonexty", fillcolor="rgba(77,166,255,0.08)"))
    fig.add_trace(go.Scatter(x=ichi["tenkan_sen"].index, y=ichi["tenkan_sen"],
                             mode="lines", name="Tenkan", line=dict(color=_YELLOW, width=1.5)))
    fig.add_trace(go.Scatter(x=ichi["kijun_sen"].index, y=ichi["kijun_sen"],
                             mode="lines", name="Kijun",  line=dict(color=_BLUE,   width=1.5)))
    fig.add_trace(_candle_trace(df))
    _theme(fig, height=440, title="Ichimoku Cloud")
    _style_axes(fig)
    fig.update_layout(xaxis_rangeslider_visible=False)
    return fig
