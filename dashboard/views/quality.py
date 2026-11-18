import streamlit as st
from common import metric_cards, setup, synthetic_quality


def render():
    setup("Data Quality", "Hasil audit & cleaning data")
    metric_cards([("Rows raw", "–"), ("Rows clean", "–"), ("Completeness", "– %")])
    st.write("")
    st.subheader("Daftar pengecekan (jumlah = demo)")
    st.dataframe(synthetic_quality(), use_container_width=True, hide_index=True)
    st.warning("Cleaning belum dilakukan. Tidak ada model ML sebelum cleaning selesai.")
