"""Pure analysis and synthetic demo data helpers separated from Streamlit UI."""

from __future__ import annotations

import numpy as np
import pandas as pd

WEEKDAY_ORDER = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]


def synthetic_sleep_data(days: int = 60, seed: int = 42) -> pd.DataFrame:
    """Generate deterministic SYNTHETIC sleep demo data (not real Samsung Health data)."""
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2000-01-01", periods=days)
    bed = 23 + rng.normal(0, 1.0, days)
    dur = np.clip(rng.normal(7, 1.1, days), 3.5, 10)
    df = pd.DataFrame({"date": dates, "bed_hour": bed, "duration_h": dur})
    df["wake_hour"] = (df.bed_hour + df.duration_h) % 24
    df["deep_pct"] = rng.normal(18, 3, days).clip(5, 30)
    df["rem_pct"] = rng.normal(22, 3, days).clip(8, 35)
    df["light_pct"] = 100 - df.deep_pct - df.rem_pct
    df["weekday"] = df.date.dt.day_name()
    df["is_weekend"] = df.date.dt.dayofweek >= 5
    return df


def synthetic_quality_checks() -> pd.DataFrame:
    """Return placeholder data-quality check table for dashboard demo mode."""
    return pd.DataFrame(
        {
            "Check": [
                "Missing values",
                "Duplicate sessions",
                "Out-of-range duration",
                "Timezone inconsistency",
                "Overlapping sessions",
            ],
            "Status": ["Belum dihitung"] * 5,
            "Demo count": [12, 3, 5, 0, 2],
        }
    )


def summarize_weekday_duration(df: pd.DataFrame) -> pd.DataFrame:
    """Compute mean sleep duration per weekday in canonical Monday-Sunday order."""
    if df.empty:
        return pd.DataFrame({"weekday": pd.Series(dtype=str), "duration_h": pd.Series(dtype=float)})
    grouped = (
        df.groupby("weekday", as_index=False)["duration_h"]
        .mean()
        .assign(_order=lambda d: d["weekday"].map({day: i for i, day in enumerate(WEEKDAY_ORDER)}))
        .sort_values("_order")
        .drop(columns=["_order"])
        .reset_index(drop=True)
    )
    return grouped


def summarize_stage_composition(df: pd.DataFrame) -> pd.DataFrame:
    """Compute mean sleep stage composition percentages for demo visualization."""
    stage_cols = ["deep_pct", "rem_pct", "light_pct"]
    if df.empty:
        return pd.DataFrame({"stage": stage_cols, "pct": [0.0, 0.0, 0.0]})
    means = df[stage_cols].mean().reset_index()
    means.columns = ["stage", "pct"]
    return means


def prepare_consistency_series(df: pd.DataFrame) -> pd.DataFrame:
    """Reshape sleep schedule columns into long format for consistency charts."""
    if df.empty:
        return pd.DataFrame(columns=["date", "event", "hour"])
    return df.melt("date", ["bed_hour", "wake_hour"], "event", "hour")
