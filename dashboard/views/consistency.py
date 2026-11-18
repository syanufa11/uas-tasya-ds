import altair as alt
import streamlit as st
from common import metric_cards, setup, synthetic_sleep

from src.samsung_health.metrics import prepare_consistency_series


def render() -> None:
    """Render sleep consistency page using separated analysis helpers."""
    setup("Sleep Consistency", "Keteraturan jam tidur dan bangun")
    metric_cards([("Bedtime SD", "– min"), ("Wake-time SD", "– min"),
                  ("Social jetlag", "– min")])
    st.write("")
    df = synthetic_sleep()
    st.subheader("Jam tidur & bangun (demo sintetis)")
    long = prepare_consistency_series(df)
    st.altair_chart(
        alt.Chart(long)
        .mark_line(point=True)
        .encode(x="date:T", y=alt.Y("hour:Q", title="Jam"), color="event:N")
        .properties(height=300),
        use_container_width=True,
    )
    st.subheader("Weekday vs weekend (demo)")
    st.altair_chart(
        alt.Chart(df)
        .mark_boxplot()
        .encode(x=alt.X("is_weekend:N", title="Weekend?"), y="duration_h:Q")
        .properties(height=240),
        use_container_width=True,
    )
