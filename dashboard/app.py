"""Entry point. Run: streamlit run dashboard/app.py"""

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent))

st.set_page_config(
    page_title="Samsung Health Sleep Analytics",
    page_icon="🌙",
    layout="wide",
    initial_sidebar_state="expanded",
)

from common import sidebar_controls  # noqa: E402
from views import activity, methodology, overview, quality, relationship, sleep  # noqa: E402

sidebar_controls()

pages = [
    st.Page(overview.render, title="Overview", icon="🏠", url_path="overview", default=True),
    st.Page(sleep.render, title="Sleep Analytics", icon=":material/bedtime:", url_path="sleep"),
    st.Page(
        activity.render, title="Physical Activity", icon=":material/steps:", url_path="activity"
    ),
    st.Page(
        relationship.render,
        title="Sleep & Activity Relationship",
        icon=":material/scatter_plot:",
        url_path="relationship",
    ),
    st.Page(quality.render, title="Data Quality", icon="🧹", url_path="quality"),
    st.Page(methodology.render, title="Methodology", icon="📚", url_path="methodology"),
]
st.navigation(pages).run()
