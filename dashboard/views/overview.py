import altair as alt
import streamlit as st
from common import metric_cards, setup, synthetic_sleep


def render():
    setup("Overview", "Ringkasan pola tidur — kerangka dashboard (Task 04)")
    metric_cards([("Avg duration", "– h"), ("Avg bedtime", "– : –"),
                  ("Consistency score", "–"), ("Nights analysed", "–")])
    st.write("")
    df = synthetic_sleep()
    st.subheader("Durasi tidur harian (demo sintetis)")
    st.altair_chart(
        alt.Chart(df).mark_area(opacity=.4, line=True, color="#8f84ff")
        .encode(x="date:T", y=alt.Y("duration_h:Q", title="Jam"))
        .properties(height=280), use_container_width=True)
    st.info("Angka kartu masih placeholder. Akan terisi setelah cleaning data selesai.")
