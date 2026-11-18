"""Overview page: KPI summary, sleep duration trend, and period overview."""

import pandas as pd
import plotly.express as px
import streamlit as st
from charts import show_chart
from common import (
    analysis_data,
    empty_state,
    metric_cards,
    section_header,
    setup,
)

from src.samsung_health.metrics import compute_sleep_overview_kpis


def render() -> None:
    """Render the Overview page with synthetic demo sleep KPIs and trends."""
    setup(
        "Overview",
        "Ringkasan KPI tidur, tren durasi harian, dan cakupan periode data (mode demo sintetis).",
    )
    df = analysis_data()
    if df.empty:
        empty_state("Data demo tidur kosong.")
        return

    kpis = compute_sleep_overview_kpis(df)
    metric_cards(
        [
            ("Rata-rata Durasi", f"{kpis['avg_duration_h']:.2f} jam", "DEMO SINTETIS"),
            ("Median Durasi", f"{kpis['median_duration_h']:.2f} jam", "DEMO SINTETIS"),
            ("Rata-rata Jam Tidur", str(kpis["avg_bedtime"]), "DEMO SINTETIS"),
            ("Rata-rata Jam Bangun", str(kpis["avg_waketime"]), "DEMO SINTETIS"),
            ("Malam Dianalisis", f"{kpis['nights']} malam", "DEMO SINTETIS"),
        ]
    )

    section_header(
        "Tren Durasi Tidur Harian (Demo Sintetis)",
        "Rata-rata bergerak memakai 7 observasi terakhir setelah filter jenis hari.",
    )
    trend_df = df[["date", "duration_h"]].copy()
    trend_df["rolling_7d"] = trend_df["duration_h"].rolling(7, min_periods=1).mean()

    with st.container(border=True):
        figure = px.line(
            trend_df,
            x="date",
            y=["duration_h", "rolling_7d"],
            labels={"date": "Tanggal fiktif", "value": "Durasi (jam)", "variable": "Seri"},
        )
        figure.for_each_trace(
            lambda trace: trace.update(
                name={"duration_h": "Durasi harian", "rolling_7d": "Rata-rata 7 observasi"}[
                    trace.name
                ]
            )
        )
        show_chart(figure, "Durasi tidur sintetis dan rata-rata bergerak 7 observasi")

    section_header(
        "Ringkasan Periode Data",
        "Metadata periode dan komposisi hari pengamatan pada mode demo sintetis.",
    )
    period_table = pd.DataFrame(
        [
            {"Parameter": "Periode Mulai", "Nilai": kpis["start_date"]},
            {"Parameter": "Periode Selesai", "Nilai": kpis["end_date"]},
            {"Parameter": "Total Malam (Demo)", "Nilai": f"{kpis['nights']} malam"},
            {"Parameter": "Hari Kerja (Sen–Jum)", "Nilai": f"{kpis['weekday_nights']} malam"},
            {"Parameter": "Akhir Pekan (Sab–Min)", "Nilai": f"{kpis['weekend_nights']} malam"},
            {
                "Parameter": "Sumber Data Aktif",
                "Nilai": "Generator Sintetis Deterministik (seed=42)",
            },
        ]
    )
    st.dataframe(period_table, width="stretch", hide_index=True)
