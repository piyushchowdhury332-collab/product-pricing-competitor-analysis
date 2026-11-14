import streamlit as st
from portal_auth import require_login, get_stats

require_login()

st.title("Welcome to Pricing Intelligence")
st.write(
    "A central portal for exploring product pricing, "
    "competitor comparisons, and business insights."
)

users, visits, active = get_stats()

a, b, c = st.columns(3)
a.metric("Registered Users", users)
b.metric("Total Visits", visits)
c.metric("Active Sessions", active)

st.caption("Active sessions are based on activity within the last 3 minutes.")
st.divider()

st.subheader("Available Dashboards")

left, right = st.columns(2)

with left:
    st.markdown("### 📊 Streamlit Analytics")
    st.write("Explore pricing trends, competitor comparisons, filters, and dataset quality.")
    st.info("Open Streamlit Analytics from the sidebar.")

with right:
    st.markdown("### 📈 Power BI Dashboard")
    st.write("Explore the executive overview, category and brand analysis, and pricing insights.")
    st.info("Open Power BI Dashboard from the sidebar.")

st.divider()
st.caption(
    "Project data is synthetic and intended for educational analysis. "
    "Units Sold and Revenue are simulated."
)
