import altair as alt
import streamlit as st
from common import setup, synthetic_sleep

ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def render():
    setup("Sleep Patterns", "Durasi, tahapan tidur, dan pola mingguan")
    df = synthetic_sleep()
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Rata-rata durasi per hari (demo)")
        st.altair_chart(alt.Chart(df).mark_bar(color="#6C5CE7")
            .encode(x=alt.X("weekday:N", sort=ORDER, title=None),
                    y=alt.Y("mean(duration_h):Q", title="Jam")).properties(height=260),
            use_container_width=True)
    with c2:
        st.subheader("Komposisi tahapan tidur (demo)")
        m = df[["deep_pct", "rem_pct", "light_pct"]].mean().reset_index()
        m.columns = ["stage", "pct"]
        st.altair_chart(alt.Chart(m).mark_arc(innerRadius=60)
            .encode(theta="pct:Q", color="stage:N").properties(height=260),
            use_container_width=True)
    st.subheader("Distribusi durasi (demo)")
    st.altair_chart(alt.Chart(df).mark_bar(color="#8f84ff")
        .encode(x=alt.X("duration_h:Q", bin=alt.Bin(maxbins=15), title="Jam"), y="count()")
        .properties(height=220), use_container_width=True)
