"""Computed quality checks on the active synthetic sample."""

import streamlit as st
from common import analysis_data, empty_state, metric_cards, setup

from src.samsung_health.dashboard_data import CORE_COLUMNS, quality_checks


def render() -> None:
    setup("Data Quality", "Pemeriksaan aktual pada data sintetis yang sedang difilter.")
    frame = analysis_data()
    if frame.empty:
        empty_state()
        return
    checks = quality_checks(frame)
    metric_cards(
        [
            ("Kolom inti", str(len(CORE_COLUMNS)), "skema demo tervalidasi - minimal 5"),
            ("Observasi", str(len(frame)), "sesuai filter aktif"),
            ("Temuan pemeriksaan", str(checks.Temuan.sum()), "dihitung dari data demo"),
        ]
    )
    st.dataframe(
        checks,
        hide_index=True,
        width="stretch",
        alt="Hasil pemeriksaan kualitas data sintetis aktif",
    )
    st.caption(
        "Jumlah temuan dapat mencakup beberapa masalah pada satu baris. "
        "Pemeriksaan ini tidak membuktikan kualitas ekspor pribadi."
    )
    st.subheader("Kamus data demo", anchor=False)
    st.dataframe(
        {
            "Kolom": CORE_COLUMNS,
            "Definisi": [
                "Tanggal fiktif",
                "Durasi interval tidur (jam)",
                "Jam mulai tidur, dapat melewati 24",
                "Jam bangun (0-24)",
                "Langkah harian sintetis",
                "Menit aktif harian sintetis",
            ],
        },
        hide_index=True,
        alt="Definisi enam kolom inti sintetis",
    )
    st.warning(
        "Zona waktu, overlap sesi, dan kelayakan dataset asli memerlukan audit lokal. "
        "Hari tanpa catatan tidak otomatis berarti tidak tidur atau tidak aktif."
    )
