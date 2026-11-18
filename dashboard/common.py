"""Shared UI helpers and SYNTHETIC demo data (not Samsung Health data)."""
import numpy as np
import pandas as pd
import streamlit as st

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


def setup(title: str, subtitle: str = ""):
    st.markdown(CSS, unsafe_allow_html=True)
    st.title(title)
    if subtitle:
        st.caption(subtitle)
    st.markdown(f'<div class="demo-banner">{DEMO_LABEL}</div>', unsafe_allow_html=True)


def metric_cards(items):
    """items: list of (label, placeholder value). Values are placeholders."""
    cols = st.columns(len(items))
    for c, (k, v) in zip(cols, items):
        c.markdown(
            f'<div class="card"><div class="k">{k}</div><div class="v">{v}</div>'
            f'<div class="t">PLACEHOLDER</div></div>',
            unsafe_allow_html=True,
        )


@st.cache_data
def synthetic_sleep(days: int = 60, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2000-01-01", periods=days)  # fake dates
    bed = 23 + rng.normal(0, 1.0, days)  # hour of day (can exceed 24)
    dur = np.clip(rng.normal(7, 1.1, days), 3.5, 10)
    df = pd.DataFrame({"date": dates, "bed_hour": bed, "duration_h": dur})
    df["wake_hour"] = (df.bed_hour + df.duration_h) % 24
    df["deep_pct"] = rng.normal(18, 3, days).clip(5, 30)
    df["rem_pct"] = rng.normal(22, 3, days).clip(8, 35)
    df["light_pct"] = 100 - df.deep_pct - df.rem_pct
    df["weekday"] = df.date.dt.day_name()
    df["is_weekend"] = df.date.dt.dayofweek >= 5
    return df


@st.cache_data
def synthetic_quality() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Check": ["Missing values", "Duplicate sessions", "Out-of-range duration",
                      "Timezone inconsistency", "Overlapping sessions"],
            "Status": ["Belum dihitung"] * 5,
            "Demo count": [12, 3, 5, 0, 2],
        }
    )
