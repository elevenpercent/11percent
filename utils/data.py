import yfinance as yf
import pandas as pd
import streamlit as st


@st.cache_data(ttl=3600)
def get_stock_data(ticker: str, start: str, end: str, interval: str = "1d") -> pd.DataFrame:
    """Download OHLCV data from Yahoo Finance."""
    try:
        df = yf.download(ticker, start=start, end=end, interval=interval, progress=False, auto_adjust=True)
        if df.empty:
            st.error(f"No data found for '{ticker}'. Check the symbol and try again.")
            return pd.DataFrame()
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df.index = pd.to_datetime(df.index)
        df = df[["Open", "High", "Low", "Close", "Volume"]].dropna()
        return df
    except Exception as e:
        st.error(f"Data error: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=3600)
def get_ticker_info(ticker: str) -> dict:
    """Get fundamental info about a stock."""
    try:
        info = yf.Ticker(ticker).info
        return {
            "name":         info.get("longName", ticker),
            "sector":       info.get("sector", "N/A"),
            "industry":     info.get("industry", "N/A"),
            "market_cap":   info.get("marketCap"),
            "pe_ratio":     info.get("trailingPE"),
            "fwd_pe":       info.get("forwardPE"),
            "eps":          info.get("trailingEps"),
            "revenue":      info.get("totalRevenue"),
            "profit_margin":info.get("profitMargins"),
            "debt_equity":  info.get("debtToEquity"),
            "roe":          info.get("returnOnEquity"),
            "dividend":     info.get("dividendYield"),
            "52w_high":     info.get("fiftyTwoWeekHigh"),
            "52w_low":      info.get("fiftyTwoWeekLow"),
            "avg_volume":   info.get("averageVolume"),
            "beta":         info.get("beta"),
            "currency":     info.get("currency", "USD"),
            "summary":      info.get("longBusinessSummary", ""),
            "website":      info.get("website", ""),
        }
    except Exception:
        return {"name": ticker}


@st.cache_data(ttl=1800)
def get_news(ticker: str) -> list:
    """Get recent news headlines for a ticker."""
    try:
        t = yf.Ticker(ticker)
        news = t.news or []
        return news[:8]
    except Exception:
        return []
