"""Sleep Consistency page: schedule variability, weekly trends, and activity calendar."""

import altair as alt
import streamlit as st
from common import (
    PALETTE,
    active_demo_days,
    empty_state,
    metric_cards,
    section_header,
    setup,
    synthetic_sleep,
)

from src.samsung_health.metrics import (
    compute_consistency_metrics,
    prepare_calendar_heatmap,
    prepare_consistency_series,
    prepare_weekly_trends,
)


def render() -> None:
    """Render sleep consistency page using separated analysis helpers."""
    setup(
        "Sleep Consistency",
        "Variasi jadwal tidur, tren mingguan, dan kalender aktivitas tidur (mode demo sintetis).",
    )
    df = synthetic_sleep(days=active_demo_days())
    if df.empty:
        empty_state("Data demo tidur kosong.")
        return

    metrics = compute_consistency_metrics(df)
    metric_cards(
        [
            ("Simpangan Jam Tidur", f"{metrics['bedtime_sd_min']:.1f} mnt", "DEMO SINTETIS"),
            ("Simpangan Jam Bangun", f"{metrics['waketime_sd_min']:.1f} mnt", "DEMO SINTETIS"),
            ("Simpangan Midpoint", f"{metrics['midpoint_sd_min']:.1f} mnt", "DEMO SINTETIS"),
            ("Social Jetlag", f"{metrics['social_jetlag_min']:.1f} mnt", "DEMO SINTETIS"),
        ]
    )

    section_header(
        "Variasi Jam Tidur & Jam Bangun Harian (Demo)",
        "Fluktuasi waktu mulai tidur (indigo) dan waktu bangun (cyan) sepanjang periode.",
    )
    long = prepare_consistency_series(df)
    long["event_label"] = long["event"].map(
        {"bed_hour": "Jam Tidur", "wake_hour": "Jam Bangun"}
    )
    st.altair_chart(
        alt.Chart(long)
        .mark_line(point=True, strokeWidth=2)
        .encode(
            x=alt.X("date:T", title="Tanggal"),
            y=alt.Y("hour:Q", title="Jam (0–24)"),
            color=alt.Color(
                "event_label:N",
                title="Peristiwa",
                scale=alt.Scale(
                    domain=["Jam Tidur", "Jam Bangun"],
                    range=[PALETTE["indigo_soft"], PALETTE["cyan_bright"]],
                ),
            ),
            tooltip=[
                alt.Tooltip("date:T", title="Tanggal"),
                alt.Tooltip("event_label:N", title="Peristiwa"),
                alt.Tooltip("hour:Q", title="Jam", format=".2f"),
            ],
        )
        .properties(height=280),
        use_container_width=True,
    )

    c1, c2 = st.columns(2)
    with c1:
        section_header(
            "Tren Mingguan Durasi Tidur (Demo)",
            "Rata-rata durasi tidur per minggu kalender.",
        )
        weekly = prepare_weekly_trends(df)
        st.altair_chart(
            alt.Chart(weekly)
            .mark_line(
                point=alt.OverlayMarkDef(color=PALETTE["cyan_bright"], size=60),
                color=PALETTE["indigo"],
                strokeWidth=2.5,
            )
            .encode(
                x=alt.X("week_start:T", title="Awal Minggu"),
                y=alt.Y(
                    "avg_duration_h:Q",
                    title="Rata-rata Durasi (jam)",
                    scale=alt.Scale(zero=False),
                ),
                tooltip=[
                    alt.Tooltip("week_start:T", title="Minggu"),
                    alt.Tooltip("avg_duration_h:Q", title="Rata-rata (jam)", format=".2f"),
                    alt.Tooltip("nights:Q", title="Jumlah Malam"),
                ],
            )
            .properties(height=260),
            use_container_width=True,
        )

    with c2:
        section_header(
            "Kalender Aktivitas Tidur (Demo)",
            "Peta panas durasi tidur berdasarkan minggu dan hari dalam seminggu.",
        )
        cal = prepare_calendar_heatmap(df)
        st.altair_chart(
            alt.Chart(cal)
            .mark_rect(cornerRadius=4)
            .encode(
                x=alt.X(
                    "weekday_short:N",
                    sort=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
                    title="Hari",
                ),
                y=alt.Y("week_label:O", title="Minggu"),
                color=alt.Color(
                    "duration_h:Q",
                    title="Durasi (jam)",
                    scale=alt.Scale(
                        range=[PALETTE["navy_surface"], PALETTE["indigo"], PALETTE["cyan_bright"]]
                    ),
                ),
                tooltip=[
                    alt.Tooltip("date_str:N", title="Tanggal"),
                    alt.Tooltip("weekday_short:N", title="Hari"),
                    alt.Tooltip("duration_h:Q", title="Durasi (jam)", format=".2f"),
                ],
            )
            .properties(height=260),
            use_container_width=True,
        )
