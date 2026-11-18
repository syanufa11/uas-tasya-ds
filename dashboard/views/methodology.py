import streamlit as st
from common import setup


def render():
    setup("Methodology", "Alur kerja dan batasan")
    st.markdown("""
1. **Audit data** — inspeksi struktur & kualitas ekspor Samsung Health (`data_audit/`).
2. **Cleaning** — duplikat, nilai hilang, rentang tidak wajar, zona waktu. *(belum dikerjakan)*
3. **Analisis deskriptif** — pola dan konsistensi tidur.
4. **Dashboard** — tahap ini hanya kerangka dengan data sintetis.
5. **Modeling (opsional)** — **hanya setelah cleaning selesai**.

**Privasi:** dashboard berjalan tanpa dataset pribadi; data asli tidak disertakan di repo.
""")
    st.caption("Semua grafik saat ini berasal dari generator acak (seed tetap) di `dashboard/common.py`.")
