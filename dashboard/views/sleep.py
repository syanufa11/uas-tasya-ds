"""Preserve both existing sleep analyses in one navigation destination."""

import streamlit as st

from views import consistency, patterns


def render() -> None:
    section = st.segmented_control(
        "Analisis tidur", ["Pola tidur", "Konsistensi"], default="Pola tidur", key="sleep_section"
    )
    if section == "Konsistensi":
        consistency.render()
    else:
        patterns.render()
