"""Sleep Patterns page: duration distribution, sleep/wake timing, weekday vs weekend."""

import altair as alt
import pandas as pd
import streamlit as st
from common import (
    PALETTE,
    analysis_data,
    empty_state,
    section_header,
    setup,
)

from src.samsung_health.metrics import (
    WEEKDAY_ORDER,
    summarize_weekday_duration,
    summarize_weekday_vs_weekend,
)


def render() -> None:
    """Render sleep patterns page using separated analysis helpers."""
    setup(
        "Sleep Analytics",
        (
            "Distribusi durasi tidur, pola jam tidur–bangun, "
            "serta perbandingan hari kerja dan akhir pekan."
        ),
    )
    df = analysis_data()
    if df.empty:
        empty_state("Data demo tidur kosong.")
        return

    c1, c2 = st.columns(2)
    with c1:
        section_header(
            "Distribusi Durasi Tidur (Demo)",
            "Histogram durasi tidur dengan garis rata-rata.",
        )
        mean_val = float(df["duration_h"].mean())
        hist = (
            alt.Chart(df)
            .mark_bar(color=PALETTE["indigo"], cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
            .encode(
                x=alt.X("duration_h:Q", bin=alt.Bin(maxbins=14), title="Durasi Tidur (jam)"),
                y=alt.Y("count()", title="Jumlah Malam"),
                tooltip=[alt.Tooltip("count()", title="Jumlah Malam")],
            )
        )
        mean_rule = (
            alt.Chart(pd.DataFrame({"mean_h": [mean_val]}))
            .mark_rule(color=PALETTE["cyan_bright"], strokeDash=[5, 4], strokeWidth=2)
            .encode(x="mean_h:Q")
        )
        st.altair_chart((hist + mean_rule).properties(height=270), width="stretch")

    with c2:
        section_header(
            "Rata-rata Durasi per Hari (Demo)",
            "Perbandingan rata-rata durasi tidur Senin hingga Minggu.",
        )
        weekday_summary = summarize_weekday_duration(df)
        st.altair_chart(
            alt.Chart(weekday_summary)
            .mark_bar(color=PALETTE["cyan"], cornerRadiusTopLeft=5, cornerRadiusTopRight=5)
            .encode(
                x=alt.X("weekday:N", sort=WEEKDAY_ORDER, title="Hari"),
                y=alt.Y("duration_h:Q", title="Rata-rata (jam)"),
                tooltip=[
                    alt.Tooltip("weekday:N", title="Hari"),
                    alt.Tooltip("duration_h:Q", title="Rata-rata (jam)", format=".2f"),
                ],
            )
            .properties(height=270),
            width="stretch",
        )

    c3, c4 = st.columns(2)
    with c3:
        section_header(
            "Pola Jam Tidur dan Jam Bangun (Demo)",
            "Sebaran jam mulai tidur vs jam bangun (warna membedakan hari kerja dan akhir pekan).",
        )
        scatter_df = df.copy()
        scatter_df["kelompok"] = scatter_df["is_weekend"].map(
            {True: "Akhir Pekan", False: "Hari Kerja"}
        )
        st.altair_chart(
            alt.Chart(scatter_df)
            .mark_circle(size=70, opacity=0.8)
            .encode(
                x=alt.X(
                    "bed_hour:Q",
                    title="Jam Tidur (jam desimal)",
                    scale=alt.Scale(zero=False),
                ),
                y=alt.Y(
                    "wake_hour:Q",
                    title="Jam Bangun (jam desimal)",
                    scale=alt.Scale(zero=False),
                ),
                color=alt.Color(
                    "kelompok:N",
                    title="Kelompok",
                    scale=alt.Scale(
                        domain=["Hari Kerja", "Akhir Pekan"],
                        range=[PALETTE["indigo_soft"], PALETTE["cyan_bright"]],
                    ),
                ),
                tooltip=[
                    alt.Tooltip("date:T", title="Tanggal"),
                    alt.Tooltip("kelompok:N", title="Kelompok"),
                    alt.Tooltip("bed_hour:Q", title="Jam Tidur", format=".2f"),
                    alt.Tooltip("wake_hour:Q", title="Jam Bangun", format=".2f"),
                    alt.Tooltip("duration_h:Q", title="Durasi (jam)", format=".2f"),
                ],
            )
            .properties(height=270),
            width="stretch",
        )

    with c4:
        section_header(
            "Perbandingan Hari Kerja vs Akhir Pekan (Demo)",
            "Distribusi durasi tidur pada hari kerja dibandingkan akhir pekan.",
        )
        box_df = df.copy()
        box_df["kelompok"] = box_df["is_weekend"].map({True: "Akhir Pekan", False: "Hari Kerja"})
        st.altair_chart(
            alt.Chart(box_df)
            .mark_boxplot(extent="min-max", size=42)
            .encode(
                x=alt.X("kelompok:N", title=None),
                y=alt.Y("duration_h:Q", title="Durasi Tidur (jam)", scale=alt.Scale(zero=False)),
                color=alt.Color(
                    "kelompok:N",
                    legend=None,
                    scale=alt.Scale(
                        domain=["Hari Kerja", "Akhir Pekan"],
                        range=[PALETTE["indigo"], PALETTE["cyan"]],
                    ),
                ),
            )
            .properties(height=270),
            width="stretch",
        )

    section_header("Ringkasan Statistik Hari Kerja vs Akhir Pekan (Demo)")
    st.dataframe(summarize_weekday_vs_weekend(df), width="stretch", hide_index=True)
    st.caption(
        "Catatan: Tahapan tidur (REM/Deep), Sleep Score, dan Sleep Efficiency tidak ditampilkan "
        "karena belum didukung oleh skema dataset Samsung Health yang diaudit."
    )
