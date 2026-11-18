"""Shared Plotly presentation; calculations remain in src/."""

import streamlit as st


def show_chart(figure, label: str) -> None:
    figure.update_layout(
        height=340,
        margin=dict(l=12, r=12, t=24, b=24),
        legend=dict(orientation="h", y=-0.25, x=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(
        figure, width="stretch", alt=label, config={"displaylogo": False, "scrollZoom": False}
    )
