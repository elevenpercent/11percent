def navbar():
    st.markdown(NAVBAR_CSS, unsafe_allow_html=True)

    st.markdown(
        '<div class="nb">'
        f'<div class="nb-brand">{LOGO_IMG}</div>'
        '<div class="nb-links">',
        unsafe_allow_html=True
    )

    # Flagship links
    cols = st.columns(len(NAV_FLAGSHIP))
    for col, (path, label) in zip(cols, NAV_FLAGSHIP):
        with col:
            st.page_link(path, label=label)

    # Tools dropdown (you can ignore this if you don’t care about tools)
    tools_links = "".join(
        f'<a href="/{label.replace(" ", "_")}" target="_self">{label}</a>'
        for _, label in NAV_TOOLS
    )

    st.markdown(
        '</div>'  # close nb-links
        '<div class="nb-tools-wrap">'
        '  <button class="nb-tools-btn">Tools ▼</button>'
        f'  <div class="nb-tools-drop">{tools_links}</div>'
        '</div>'
        '<div class="nb-tag"><span class="live-dot"></span>BETA</div>'
        '</div>'  # <-- THIS closes the navbar correctly
        '<div class="nb-spacer"></div>',
        unsafe_allow_html=True
    )
