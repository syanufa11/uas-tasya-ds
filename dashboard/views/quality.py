"""Data Quality page: missing values, coverage, duplicates/overlaps, and limitations."""

import altair as alt
import streamlit as st
from common import (
    PALETTE,
    empty_state,
    metric_cards,
    section_header,
    setup,
    synthetic_quality,
)


def render() -> None:
    """Render Data Quality page with synthetic audit checks and explicit limitations."""
    setup(
        "Data Quality",
        (
            "Ringkasan pemeriksaan nilai hilang, cakupan pencatatan, "
            "duplikasi, overlap, dan keterbatasan data."
        ),
    )
    qdf = synthetic_quality()
    if qdf.empty:
        empty_state("Tabel pemeriksaan kualitas data tidak tersedia.")
        return

    metric_cards(
        [
            ("Pemeriksaan Kualitas", f"{len(qdf)} item", "DEMO SINTETIS"),
            ("Temuan Demo", f"{int(qdf['Demo count'].sum())} kasus", "DEMO SINTETIS"),
            ("Status Audit Publik", "Mode Sintetis", "TANPA DATA PRIVAT"),
        ]
    )

    c1, c2 = st.columns([1.2, 1])
    with c1:
        section_header(
            "Daftar Pengecekan Kualitas Data (Demo)",
            "Cakupan: missing values, duplikasi sesi, durasi tidak wajar, zona waktu, dan overlap.",
        )
        st.dataframe(qdf, use_container_width=True, hide_index=True)

    with c2:
        section_header(
            "Distribusi Temuan Pemeriksaan (Demo)",
            "Visualisasi jumlah kasus demo per kategori pemeriksaan.",
        )
        st.altair_chart(
            alt.Chart(qdf)
            .mark_bar(color=PALETTE["indigo"], cornerRadiusTopRight=5, cornerRadiusBottomRight=5)
            .encode(
                y=alt.Y("Check:N", sort="-x", title=None),
                x=alt.X("Demo count:Q", title="Jumlah Kasus (Demo)"),
                tooltip=["Check:N", "Status:N", "Demo count:Q"],
            )
            .properties(height=240),
            use_container_width=True,
        )

    section_header(
        "Keterbatasan Data & Catatan Privasi",
        "Hal yang perlu diperhatikan saat menafsirkan hasil analisis Samsung Health.",
    )
    st.markdown(
        """
        <div class="sh-panel">
          <h4>Batasan Teknis Ekspor Samsung Health</h4>
          <ul>
            <li><strong>Cakupan pencatatan:</strong> Hari tanpa catatan tidak otomatis berarti
            tidak tidur, melainkan bisa disebabkan perangkat tidak dipakai atau sinkronisasi
            tertunda.</li>
            <li><strong>Duplikasi &amp; overlap:</strong> Penggabungan beberapa sumber pelacakan
            (ponsel dan wearable) dapat memunculkan sesi tumpang tindih yang harus dikarantina
            saat <em>data cleaning</em>.</li>
            <li><strong>Zona waktu &amp; offset UTC:</strong> Timestamp lokal dan offset UTC harus
            divalidasi agar tidak terjadi pergeseran ganda (<em>double-shift</em>).</li>
            <li><strong>Variabel tidak tersedia:</strong> Metrik REM, Deep Sleep, Sleep Score, dan
            Sleep Efficiency tidak ditampilkan sebagai hasil aktual sebelum skema dataset teraudit
            mendukungnya secara penuh.</li>
          </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )
