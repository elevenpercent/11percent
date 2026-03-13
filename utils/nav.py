import streamlit as st
from utils.styles import LOGO_IMG


def render_navbar():
    """Render the top navigation bar."""

    st.markdown(
        f"""
        <div class="nb">

            <div class="nb-brand">
                {LOGO_IMG}
            </div>

            <div class="nb-links">
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.page_link("app.py", label="Home")

    with col2:
        st.page_link("pages/1_Strategy_Lab.py", label="Strategy")

    with col3:
        st.page_link("pages/4_Analysis.py", label="Analysis")

    with col4:
        st.page_link("pages/3_Replay.py", label="Replay")

    with col5:
        st.page_link("pages/5_Assistant.py", label="Assistant")

    st.markdown(
        """
            </div>

            <div class="nb-tools-wrap">
                <button class="nb-tools-btn">
                    Tools <span class="arr">▼</span>
                </button>

                <div class="nb-tools-drop">

                    <a href="/Earnings" target="_self">Earnings</a>
                    <a href="/Correlations" target="_self">Correlations</a>
                    <a href="/Whale_Tracker" target="_self">Whale Tracker</a>
                    <a href="/Monte_Carlo" target="_self">Monte Carlo</a>

                </div>
            </div>

            <div class="nb-tag">
                <span class="live-dot"></span>
                LIVE
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )
