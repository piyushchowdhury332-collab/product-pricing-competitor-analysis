import streamlit as st
from portal_auth import init_db, is_authenticated, logout, touch_session

st.set_page_config(
    page_title="Pricing Intelligence Portal",
    page_icon="📊",
    layout="wide"
)

init_db()

if is_authenticated():
    @st.fragment(run_every="60s")
    def heartbeat():
        touch_session(st.session_state.get("session_id"))

    heartbeat()

    with st.sidebar:
        st.title("Pricing Intelligence")
        st.caption("Analytics Portal")
        st.write("Logged in as:", st.session_state.get("username", "User"))
        if st.button("Logout", use_container_width=True):
            logout()
            st.rerun()

    pages = [
        st.Page("pages/home.py", title="Portal Home", icon="🏠", default=True),
        st.Page("pages/analytics.py", title="Streamlit Analytics", icon="📊"),
        st.Page("pages/power_bi.py", title="Power BI Dashboard", icon="📈"),
    ]
else:
    pages = [
        st.Page("pages/login.py", title="Login / Signup", icon="🔐", default=True)
    ]

navigation = st.navigation(pages, position="sidebar")
navigation.run()
