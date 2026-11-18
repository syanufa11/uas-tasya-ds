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

from views import consistency, methodology, overview, patterns, quality  # noqa: E402

pages = [
    st.Page(overview.render, title="Overview", icon="🏠", url_path="overview", default=True),
    st.Page(patterns.render, title="Sleep Patterns", icon="🌙", url_path="patterns"),
    st.Page(consistency.render, title="Sleep Consistency", icon="⏱️", url_path="consistency"),
    st.Page(quality.render, title="Data Quality", icon="🧹", url_path="quality"),
    st.Page(methodology.render, title="Methodology", icon="📚", url_path="methodology"),
]
st.navigation(pages).run()
