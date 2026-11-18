"""Public physical activity demo."""

import plotly.express as px
import streamlit as st
from charts import show_chart
from common import analysis_data, empty_state, metric_cards, setup


def render() -> None:
    setup("Physical Activity", "Langkah dan menit aktif harian - seluruh angka sintetis.")
    frame = analysis_data()
    if frame.empty:
        empty_state()
        return
    metric_cards(
        [
            ("Rata-rata langkah", f"{frame.step_count.mean():,.0f}", "langkah / hari - demo"),
            ("Rata-rata aktif", f"{frame.active_min.mean():.1f}", "menit / hari - demo"),
            ("Hari dianalisis", str(len(frame)), "observasi sintetis"),
        ]
    )
    metric = st.selectbox("Metrik aktivitas", ["Langkah", "Menit aktif"], key="activity_metric")
    column = "step_count" if metric == "Langkah" else "active_min"
    with st.container(border=True):
        st.subheader("Tren aktivitas harian", anchor=False)
        show_chart(
            px.bar(frame, x="date", y=column, labels={"date": "Tanggal fiktif", column: metric}),
            f"Tren {metric.lower()} sintetis untuk periode aktif",
        )
    st.subheader("Tabel analisis", anchor=False)
    st.dataframe(
        frame[["date", "step_count", "active_min"]],
        hide_index=True,
        width="stretch",
        alt="Aktivitas harian sintetis",
    )
