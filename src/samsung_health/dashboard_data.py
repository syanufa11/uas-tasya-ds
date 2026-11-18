"""Public synthetic demo and pure filter/quality/association functions.

This module never opens Samsung Health exports or local audit artifacts.
"""

import numpy as np
import pandas as pd

from src.samsung_health.metrics import synthetic_sleep_data

CORE_COLUMNS = ["date", "duration_h", "bed_hour", "wake_hour", "step_count", "active_min"]


def demo_dataset() -> pd.DataFrame:
    """Stable 90-day fictional series; activity is independent of sleep by design."""
    frame = synthetic_sleep_data(days=90, seed=42)
    rng = np.random.default_rng(104)
    frame["step_count"] = rng.integers(500, 12000, len(frame))
    frame["active_min"] = rng.integers(5, 120, len(frame))
    return frame[CORE_COLUMNS + ["weekday", "is_weekend"]]


def validate_dataset(frame: pd.DataFrame) -> None:
    """Enforce the public demo contract before displaying metrics."""
    if len(frame.columns) < 5 or not set(CORE_COLUMNS).issubset(frame.columns):
        raise ValueError("Skema data tidak memenuhi kolom analisis yang diperlukan.")
    if not pd.api.types.is_datetime64_any_dtype(frame["date"]):
        raise ValueError("Kolom tanggal tidak valid.")
    for column in CORE_COLUMNS[1:]:
        if not pd.api.types.is_numeric_dtype(frame[column]):
            raise ValueError("Kolom metrik harus numerik.")


def filter_period(frame: pd.DataFrame, start, end, day_type: str = "Semua") -> pd.DataFrame:
    """Filter a fixed dataset rather than regenerating observations per window."""
    mask = frame["date"].between(pd.Timestamp(start), pd.Timestamp(end))
    if day_type == "Hari kerja":
        mask &= ~frame["is_weekend"]
    elif day_type == "Akhir pekan":
        mask &= frame["is_weekend"]
    return frame.loc[mask].copy()


def quality_checks(frame: pd.DataFrame) -> pd.DataFrame:
    """Actual checks on the active synthetic rows, never placeholder counts."""
    counts = [
        int(frame[CORE_COLUMNS].isna().sum().sum()),
        int(frame["date"].duplicated().sum()),
        int((~frame["duration_h"].between(0, 24) & frame["duration_h"].notna()).sum()),
        int((frame[["step_count", "active_min"]] < 0).sum().sum()),
    ]
    return pd.DataFrame(
        {
            "Pemeriksaan": [
                "Nilai hilang (sel)",
                "Tanggal duplikat",
                "Durasi di luar 0–24 jam",
                "Aktivitas negatif (sel)",
            ],
            "Temuan": counts,
            "Status": ["Perlu ditinjau" if count else "Lulus" for count in counts],
        }
    )


def association(frame: pd.DataFrame, activity: str) -> tuple[int, float | None]:
    """Pearson r for paired same-day demo values; no causal inference."""
    paired = frame[[activity, "duration_h"]].replace([np.inf, -np.inf], np.nan).dropna()
    if len(paired) < 3 or (paired.nunique() < 2).any():
        return len(paired), None
    return len(paired), float(paired[activity].corr(paired["duration_h"]))
