"""Methodology page: CRISP-DM workflow, cleaning pipeline, analysis methods, and limitations."""

import streamlit as st
from common import section_header, setup


def render() -> None:
    """Render Methodology page following CRISP-DM structure."""
    setup(
        "Methodology",
        (
            "Kerangka CRISP-DM: pemahaman bisnis, akuisisi data, "
            "pembersihan, metode analisis, dan batasan."
        ),
    )

    sections = [
        (
            "1. Business Understanding",
            "Memahami pola durasi tidur, keteraturan jadwal tidur–bangun, dan perbedaan hari "
            "kerja vs akhir pekan dari data pelacakan personal Samsung Health untuk mendukung "
            "evaluasi kebiasaan tidur.",
        ),
        (
            "2. Data Acquisition",
            "Data berasal dari ekspor resmi Samsung Health (CSV & JSON) yang disimpan secara "
            "lokal dan dikecualikan dari Git melalui .gitignore. Pada deployment publik, "
            "dashboard berjalan dalam mode demo sintetis deterministik (seed=42) tanpa memuat "
            "data kesehatan pribadi.",
        ),
        (
            "3. Data Cleaning",
            "Pipeline pembersihan di src/samsung_health/sleep.py mencakup parsing header Samsung "
            "Health, validasi offset UTC tanpa pergeseran ganda, deteksi duplikasi sesi, "
            "identifikasi sesi overlap (tanpa menandai sesi yang sekadar bersentuhan batas), "
            "serta karantina durasi di luar rentang wajar.",
        ),
        (
            "4. Metode Analisis",
            "Analisis deskriptif menggunakan statistik ringkas (mean, median, IQR), pergeseran "
            "jam tidur lintas tengah malam untuk menghitung simpangan baku (SD) jam "
            "tidur/bangun, social jetlag (selisih midpoint akhir pekan vs hari kerja), serta "
            "agregasi tren mingguan dan peta panas kalender.",
        ),
        (
            "5. Batasan Penelitian",
            "Analisis bersifat observasional dan bukan alat diagnosis medis. Metrik REM, Deep "
            "Sleep, Sleep Score, dan Sleep Efficiency tidak diklaim sebagai hasil aktual karena "
            "belum didukung oleh skema dataset yang diaudit secara lengkap.",
        ),
    ]

    for title, body in sections:
        with st.container(border=True):
            st.subheader(title, anchor=False)
            st.markdown(body)

    section_header("Arsitektur UI & Integrasi Skill")
    st.caption(
        "Dashboard dibangun dengan Streamlit native + Plotly + Altair. Logika analisis ada di "
        "`src/samsung_health/metrics.py`, serta mengadopsi design tokens modern "
        "(navy, indigo, cyan) dengan dukungan mode gelap dan terang."
    )

    st.info(
        "Hubungan aktivitas-tidur bersifat eksploratif. Korelasi bukan sebab-akibat; "
        "data demo tidak menghasilkan kesimpulan penelitian atau diagnosis."
    )
    st.caption(
        "Kelayakan minimal lima kolom data asli diperiksa lokal melalui "
        "scripts/check_dashboard_schema.py. Dashboard publik memvalidasi skema "
        "demo secara terpisah dan tidak membuka data pribadi."
    )
