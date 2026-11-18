"""Shared UI helpers for the Streamlit sleep dashboard."""

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from src.samsung_health.metrics import (  # noqa: E402
    synthetic_quality_checks,
    synthetic_sleep_data,
)

DEMO_LABEL = "🧪 DEMO SINTETIS — data acak buatan, BUKAN data Samsung Health asli"

CSS = """
<style>
.block-container {padding-top: 2rem; max-width: 1200px;}
.demo-banner {background:#3a2f0b; border:1px solid #f5c542; color:#ffe08a;
  padding:.6rem 1rem; border-radius:10px; font-size:.9rem; margin-bottom:1rem;}
.card {background:#181C30; border:1px solid #2a3050; border-radius:14px;
  padding:1rem 1.2rem; height:100%;}
.card .k {color:#9aa3c7; font-size:.8rem; text-transform:uppercase; letter-spacing:.05em;}
.card .v {font-size:1.8rem; font-weight:700; color:#8f84ff;}
.card .t {color:#f5c542; font-size:.7rem;}
@media (max-width: 640px){ .card .v {font-size:1.4rem;} }
</style>
"""


def setup(title: str, subtitle: str = "") -> None:
    """Render shared page styles, header, and synthetic demo banner."""
    st.markdown(CSS, unsafe_allow_html=True)
    st.title(title)
    if subtitle:
        st.caption(subtitle)
    st.markdown(f'<div class="demo-banner">{DEMO_LABEL}</div>', unsafe_allow_html=True)


def metric_cards(items: list[tuple[str, str]]) -> None:
    """Render placeholder KPI cards from a list of (label, value) pairs."""
    cols = st.columns(len(items))
    for col, (label, value) in zip(cols, items, strict=True):
        col.markdown(
            f'<div class="card"><div class="k">{label}</div><div class="v">{value}</div>'
            '<div class="t">PLACEHOLDER</div></div>',
            unsafe_allow_html=True,
        )


@st.cache_data
def synthetic_sleep(days: int = 60, seed: int = 42) -> pd.DataFrame:
    """Cached wrapper around deterministic synthetic sleep demo data."""
    return synthetic_sleep_data(days=days, seed=seed)


@st.cache_data
def synthetic_quality() -> pd.DataFrame:
    """Cached wrapper around synthetic quality check table."""
    return synthetic_quality_checks()
