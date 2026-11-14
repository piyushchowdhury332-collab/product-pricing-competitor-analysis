
import streamlit as st
import os
from portal_auth import require_login

require_login()

st.title("Power BI Dashboard")
st.caption("Product Pricing & Competitor Analysis")

st.markdown("""
Explore the interactive Power BI reports covering:
- Executive Overview
- Category & Brand Analysis
- Pricing & Customer Insights
""")

# Configure this URL after publishing the report.
report_url = os.environ.get("POWERBI_REPORT_URL", "").strip()

if report_url:
    st.success("Power BI report is connected.")

    st.link_button(
        "Open Power BI Dashboard",
        report_url,
        use_container_width=True
    )
else:
    st.info("Power BI online connection is not configured yet.")

    st.markdown("### Report publication pending")
    st.write(
        "The Power BI report is currently available as a local "
        "Power BI Desktop project. It will become accessible to "
        "portal users after it is published to Power BI Service."
    )

    st.write("Current report pages:")
    st.markdown("""
    1. Executive Overview
    2. Category & Brand
    3. Pricing & Customer
    """)

st.divider()
st.caption(
    "Access to the published report depends on Power BI permissions "
    "and licensing."
)
