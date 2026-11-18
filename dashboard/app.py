"""Entry point. Run: streamlit run dashboard/app.py"""

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent))

from icons import PAGE_ICONS, data_uri, leading_icon  # noqa: E402

st.set_page_config(
    page_title="Samsung Health Sleep Analytics",
    page_icon=data_uri("moon", favicon=True),
    layout="wide",
    initial_sidebar_state="expanded",
)

from common import sidebar_controls  # noqa: E402
from views import (  # noqa: E402
    activity,
    methodology,
    model_evaluation,
    overview,
    quality,
    relationship,
    sleep,
)

pages = [
    st.Page(overview.render, title="Overview", url_path="overview", default=True),
    st.Page(sleep.render, title="Sleep Analytics", url_path="sleep"),
    st.Page(
        activity.render, title="Physical Activity", url_path="activity"
    ),
    st.Page(
        relationship.render,
        title="Sleep & Activity Relationship",
        url_path="relationship",
    ),
    st.Page(quality.render, title="Data Quality", url_path="quality"),
    st.Page(model_evaluation.render, title="Model Evaluation", url_path="model-evaluation"),
    st.Page(methodology.render, title="Methodology", url_path="methodology"),
]
selected = st.navigation(pages, position="hidden")
with st.sidebar:
    st.caption("NAVIGATION")
    for page in pages:
        key = "nav_" + PAGE_ICONS[page.title].replace("-", "_")
        leading_icon(key, "a", PAGE_ICONS[page.title], 21)
        with st.container(key=key):
            st.page_link(page, label=page.title, icon="", width="stretch")
    st.divider()
sidebar_controls()
selected.run()
