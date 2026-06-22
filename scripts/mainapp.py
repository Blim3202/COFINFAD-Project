import streamlit as st

# Sidebar navigation
pg = st.navigation(
    [
        st.Page(
            "appv0.py",
            title="Dashboard",
            icon=":material/dashboard:",
            default=True,
        ),
        st.Page("chat_page.py", title="Agent Analysis", icon=":material/menu_book:")
    ]
)
pg.run()
#  Main app