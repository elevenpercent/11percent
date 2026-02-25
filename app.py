import streamlit as st

st.set_page_config(page_title="11Percent | Free Backtesting", layout="wide")

st.title("🚀 11Percent Financial Platform")
st.markdown("### Free Backtesting, Real-time Analysis, and AI Insights")

st.info("Use the sidebar on the left to switch between the Backtester and the AI Assistant.")

col1, col2 = st.columns(2)
with col1:
    st.subheader("📈 Backtesting")
    st.write("Test SMA and RSI strategies on historical data for free.")
    
with col2:
    st.subheader("🤖 Gemini Assistant")
    st.write("Ask questions about market trends or get help with your strategy.")

st.divider()
st.caption("Disclaimer: This tool is for educational purposes only. Not financial advice.")
