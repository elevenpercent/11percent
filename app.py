import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="11% · Backtesting Platform",
    page_icon="$",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""<style>
html, body { background: #0b0e11 !important }
[data-testid="stAppViewContainer"] > .main { background: #0b0e11 !important; padding: 0 !important }
.block-container { padding: 0 !important; max-width: 100% !important }
[data-testid="stSidebar"], [data-testid="stSidebarNav"],
[data-testid="collapsedControl"], #MainMenu, footer, header { display: none !important }
.stDeployButton { display: none !important }
</style>""", unsafe_allow_html=True)

with open("landing.html", "r") as f:
    html_content = f.read()

components.html(html_content, height=7000, scrolling=True)
