"""Public method status only: never import private research diagnostics."""

import streamlit as st
from common import setup


def render() -> None:
    """Present honest unavailable metrics while the data contract is unresolved."""
    setup("Model Evaluation", "Status kesiapan model dan rancangan evaluasi temporal.")
    st.warning(
        "Pelatihan penelitian belum dijalankan: batas hari aktivitas, satuan, "
        "dan definisi sesi tidur berikutnya memerlukan verifikasi."
    )
    st.table({
        "Model": ["DummyRegressor (median)", "LinearRegression", "RandomForestRegressor"],
        "Status": ["Belum dilatih"] * 3,
        "MAE (menit)": ["Belum tersedia"] * 3,
        "RMSE (menit)": ["Belum tersedia"] * 3,
        "R²": ["Belum tersedia"] * 3,
    }, alt="Model yang direncanakan; seluruh metrik belum tersedia")
    st.subheader("Grafik prediksi dan interpretasi")
    st.info(
        "Actual vs Predicted, residual, dan feature importance belum tersedia. "
        "Belum ada model terbaik; Random Forest belum dapat dinyatakan unggul. "
        "Tidak ada hasil demo yang digunakan sebagai hasil penelitian."
    )
    st.subheader("Metode dan keterbatasan")
    st.markdown(
        "Rencana: split kronologis, preprocessing di Pipeline hanya pada train, "
        "validasi temporal untuk tuning, dan pengujian semua model pada test yang sama. "
        "Data satu individu dan missing target membatasi generalisasi. Korelasi bukan "
        "sebab-akibat; K-Means ditunda sampai data layak."
    )
    st.caption("Halaman publik ini tidak memuat data, statistik, atau prediksi kesehatan pribadi.")
