import streamlit as st

# Define color palette
colors = {
    'primary_maroon': '#360829',
    'bright_pink': '#ff57bf',
    'soft_white': "#fdf7fc",
    'soft_gray':'#faf5f7',
    'gray':"#ccc9ca",
    'white': '#ffffff',
    'black': '#000000'
}

# Inject custom CSS – Streamlit needs the `unsafe_allow_html=True` flag
st.markdown(
    f"""
    <style>
        /* Your existing CSS here... */

    </style>
    """,
    unsafe_allow_html=True
)

# Sidebar navigation
pg = st.navigation(
    [
        st.Page(
            "dashboard_page.py",
            title="Dashboard",
            icon=":material/dashboard:",
            default=True,
        ),
        st.Page("chat_page.py", title="Agent Analysis", icon=":material/menu_book:")
    ]
)
pg.run()
#  Main app