import yfinance as yf
import pandas as pd
import streamlit as st


@st.cache_data(ttl=3600)  # Cache data for 1 hour so we don't hammer the API
def get_stock_data(ticker: str, start: str, end: str) -> pd.DataFrame:
    """
    Download historical stock data from Yahoo Finance.
    
    Args:
        ticker: Stock symbol e.g. "AAPL"
        start:  Start date string e.g. "2020-01-01"
        end:    End date string e.g. "2024-01-01"
    
    Returns:
        DataFrame with columns: Open, High, Low, Close, Volume
    """
    try:
        df = yf.download(ticker, start=start, end=end, progress=False)

        if df.empty:
            st.error(f"No data found for ticker '{ticker}'. Please check the symbol.")
            return pd.DataFrame()

        # Flatten multi-level columns if present (yfinance sometimes returns them)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df.index = pd.to_datetime(df.index)
        df = df[["Open", "High", "Low", "Close", "Volume"]].dropna()
        return df

    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()


def get_ticker_info(ticker: str) -> dict:
    """Get basic info about a stock (name, sector, etc.)"""
    try:
        info = yf.Ticker(ticker).info
        return {
            "name": info.get("longName", ticker),
            "sector": info.get("sector", "N/A"),
            "market_cap": info.get("marketCap", "N/A"),
            "currency": info.get("currency", "USD"),
        }
    except Exception:
        return {"name": ticker, "sector": "N/A", "market_cap": "N/A", "currency": "USD"}
