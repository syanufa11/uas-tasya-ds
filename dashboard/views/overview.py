"""Overview page: KPI summary, sleep duration trend, and period overview."""

import altair as alt
import pandas as pd
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

from src.samsung_health.metrics import compute_sleep_overview_kpis


def render() -> None:
    """Render the Overview page with synthetic demo sleep KPIs and trends."""
    setup(
        "Overview",
        "Ringkasan KPI tidur, tren durasi harian, dan cakupan periode data (mode demo sintetis).",
    )
    df = synthetic_sleep(days=active_demo_days())
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
        "Garis cyan menunjukkan rata-rata bergerak 7 hari; garis putus-putus menandai acuan 7 jam.",
    )
    trend_df = df[["date", "duration_h"]].copy()
    trend_df["rolling_7d"] = trend_df["duration_h"].rolling(7, min_periods=1).mean()

    base = alt.Chart(trend_df).encode(x=alt.X("date:T", title="Tanggal"))
    area = base.mark_area(
        line={"color": PALETTE["indigo"], "strokeWidth": 2},
        color=alt.Gradient(
            gradient="linear",
            stops=[
                alt.GradientStop(color="rgba(79, 70, 229, 0.45)", offset=0),
                alt.GradientStop(color="rgba(6, 182, 212, 0.05)", offset=1),
            ],
            x1=1,
            x2=1,
            y1=0,
            y2=1,
        ),
    ).encode(
        y=alt.Y("duration_h:Q", title="Durasi (jam)", scale=alt.Scale(zero=False)),
        tooltip=[
            alt.Tooltip("date:T", title="Tanggal"),
            alt.Tooltip("duration_h:Q", title="Durasi (jam)", format=".2f"),
            alt.Tooltip("rolling_7d:Q", title="Rata-rata 7 hari", format=".2f"),
        ],
    )
    rolling_line = base.mark_line(color=PALETTE["cyan_bright"], strokeWidth=2.5).encode(
        y="rolling_7d:Q"
    )
    ref_rule = (
        alt.Chart(pd.DataFrame({"target": [7.0]}))
        .mark_rule(color=PALETTE["amber"], strokeDash=[6, 4], strokeWidth=1.5)
        .encode(y="target:Q")
    )
    st.altair_chart(
        (area + rolling_line + ref_rule).properties(height=310),
        use_container_width=True,
    )

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
    st.dataframe(period_table, use_container_width=True, hide_index=True)
