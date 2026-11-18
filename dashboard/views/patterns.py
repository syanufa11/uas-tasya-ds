import altair as alt
import streamlit as st
from common import setup, synthetic_sleep

from src.samsung_health.metrics import (
    WEEKDAY_ORDER,
    summarize_stage_composition,
    summarize_weekday_duration,
)


def render() -> None:
    """Render sleep patterns page using separated analysis helpers."""
    setup("Sleep Patterns", "Durasi, tahapan tidur, dan pola mingguan")
    df = synthetic_sleep()
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Rata-rata durasi per hari (demo)")
        weekday_summary = summarize_weekday_duration(df)
        st.altair_chart(
            alt.Chart(weekday_summary)
            .mark_bar(color="#6C5CE7")
            .encode(
                x=alt.X("weekday:N", sort=WEEKDAY_ORDER, title=None),
                y=alt.Y("duration_h:Q", title="Jam"),
            )
            .properties(height=260),
            use_container_width=True,
        )
    with c2:
        st.subheader("Komposisi tahapan tidur (demo)")
        stage_summary = summarize_stage_composition(df)
        st.altair_chart(
            alt.Chart(stage_summary)
            .mark_arc(innerRadius=60)
            .encode(theta="pct:Q", color="stage:N")
            .properties(height=260),
            use_container_width=True,
        )
    st.subheader("Distribusi durasi (demo)")
    st.altair_chart(
        alt.Chart(df)
        .mark_bar(color="#8f84ff")
        .encode(x=alt.X("duration_h:Q", bin=alt.Bin(maxbins=15), title="Jam"), y="count()")
        .properties(height=220),
        use_container_width=True,
    )
