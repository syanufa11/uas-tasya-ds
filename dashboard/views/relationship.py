"""Exploratory same-day demo associations, never causal conclusions."""

import plotly.express as px
import streamlit as st
from charts import show_chart
from common import analysis_data, empty_state, metric_cards, setup

from src.samsung_health.dashboard_data import association


def render() -> None:
    setup("Sleep & Activity Relationship", "Hubungan pada pasangan data demo sintetis.")
    frame = analysis_data()
    if frame.empty:
        empty_state()
        return
    label = st.selectbox(
        "Variabel aktivitas", ["Langkah", "Menit aktif"], key="relationship_metric"
    )
    column = "step_count" if label == "Langkah" else "active_min"
    n, correlation = association(frame, column)
    metric_cards(
        [
            ("Pasangan lengkap", str(n), "tanggal demo yang sama"),
            (
                "Pearson r",
                "Tidak tersedia" if correlation is None else f"{correlation:.3f}",
                "korelasi demo - bukan sebab-akibat",
            ),
        ]
    )
    st.info(
        "Korelasi tidak menunjukkan sebab-akibat. Aktivitas dibuat independen dari "
        "tidur; nilai r hanya mendemonstrasikan metode, bukan hasil penelitian."
    )
    if correlation is None:
        empty_state("Minimal 3 pasangan dan variasi kedua variabel diperlukan.")
    with st.container(border=True):
        st.subheader("Aktivitas dan durasi tidur", anchor=False)
        show_chart(
            px.scatter(
                frame,
                x=column,
                y="duration_h",
                hover_data=["date"],
                labels={column: label, "duration_h": "Durasi tidur (jam)"},
            ),
            "Sebaran aktivitas dan durasi tidur sintetis; tanpa interpretasi kausal",
        )
    st.caption(
        "Pasangan demo memakai tanggal yang sama, bukan alignment temporal "
        "penelitian. Data nyata memerlukan validasi UTC, overlap, dan urutan aktivitas "
        "sebelum onset tidur seperti prosedur TASK 11A."
    )
    st.dataframe(
        frame[["date", column, "duration_h"]],
        hide_index=True,
        width="stretch",
        alt="Pasangan data sintetis untuk korelasi",
    )
