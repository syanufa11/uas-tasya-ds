"""Audit the candidate dataset without promoting provisional joins to predictions."""

from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
import pandas as pd

TARGET = "sleep_duration_minutes"
NUMERIC = [TARGET, "step_count", "active_time_minutes", "day_of_week", "is_weekend"]
REQUIRED = ["date", "sleep_start_local", "sleep_end_local", *NUMERIC]
BLOCKERS = (
    "Batas hari aktivitas UTC/Asia-Jakarta belum terkonfirmasi.",
    "Satuan active_time_minutes masih merupakan konversi empiris.",
    "Konversi timestamp tidur dari UTC belum dikonfirmasi pada histori aplikasi.",
    "CSV memilih sesi terpanjang per tanggal bangun secara retrospektif; "
    "belum mewakili sesi berikutnya yang ditetapkan sebelum pengamatan.",
)


def load_candidate(path: Path) -> pd.DataFrame:
    """Read the documented date format; reject malformed schemas and values."""
    frame = pd.read_csv(path)
    absent = set(REQUIRED) - set(frame)
    if absent:
        raise ValueError(f"Missing required columns: {sorted(absent)}")
    frame["date"] = pd.to_datetime(frame["date"], format="%d/%m/%Y", errors="raise")
    for column in NUMERIC:
        frame[column] = pd.to_numeric(frame[column], errors="raise")
        if np.isinf(frame[column].dropna()).any():
            raise ValueError(f"Infinite values: {column}")
    # Require explicit +07:00 rather than silently localizing naive timestamps.
    for column in ("sleep_start_local", "sleep_end_local"):
        values = frame[column].dropna()
        if not values.str.endswith("+07:00").all():
            raise ValueError(f"Timestamp must explicitly use +07:00: {column}")
        frame[column] = pd.to_datetime(
            frame[column], format="ISO8601", utc=True, errors="raise"
        )
    return frame.sort_values("date", kind="stable").reset_index(drop=True)


def retrospective_pairs(frame: pd.DataFrame) -> pd.DataFrame:
    """Diagnostics only: UTC day before sleep start, never wake date minus one.

    The candidate activity day D closes at D+1 00:00 UTC. Even when this
    precedes sleep start, source availability and target selection are unverified.
    Do not expose these pairs as training samples.
    """
    sleeps = frame.loc[frame.sleep_start_local.notna()].copy()
    starts = sleeps.sleep_start_local
    sleeps["activity_date"] = (
        starts.dt.tz_localize(None).dt.normalize() - pd.Timedelta(days=1)
    )
    sleeps["activity_end_candidate"] = (
        sleeps.activity_date.dt.tz_localize("UTC") + pd.Timedelta(days=1)
    )
    activities = frame[["date", "step_count", "active_time_minutes"]].rename(
        columns={"date": "activity_date"}
    )
    sleeps = sleeps.drop(columns=["step_count", "active_time_minutes"])
    return sleeps.merge(activities, on="activity_date", how="left", validate="many_to_one")


def audit_candidate(frame: pd.DataFrame) -> dict:
    """Return private aggregate diagnostics; readiness remains blocked by provenance."""
    extra = []
    if frame.date.isna().any() or frame.date.duplicated().any():
        extra.append("Tanggal hilang atau duplikat; join aktivitas tidak unik.")
    if (frame[NUMERIC[:3]] < 0).any().any() or frame[TARGET].eq(0).any():
        extra.append("Nilai negatif atau target nol memerlukan pemeriksaan.")
    starts, ends = frame.sleep_start_local, frame.sleep_end_local
    incomplete = starts.isna().ne(ends.isna()) | (frame[TARGET].notna() & starts.isna())
    if incomplete.any() or (ends <= starts).any():
        extra.append("Interval tidur tidak lengkap atau tidak positif.")
    wake_dates = ends.dt.tz_convert("Asia/Jakarta").dt.tz_localize(None).dt.normalize()
    if (ends.notna() & wake_dates.ne(frame.date)).any():
        extra.append("Tanggal bangun tidak konsisten dengan label date.")
    if not frame.day_of_week.eq(frame.date.dt.dayofweek).all():
        extra.append("day_of_week tidak konsisten.")
    if not frame.is_weekend.eq(frame.date.dt.dayofweek.ge(5).astype(int)).all():
        extra.append("is_weekend tidak konsisten.")
    if frame.date.duplicated().any():
        pairs = pd.DataFrame()
    else:
        pairs = retrospective_pairs(frame)
    numeric = frame[NUMERIC]
    q1, q3 = numeric.quantile(0.25), numeric.quantile(0.75)
    outliers = (numeric.lt(q1 - 1.5 * (q3 - q1)) | numeric.gt(q3 + 1.5 * (q3 - q1)))
    source_fields = ["sleep_start_local", "sleep_end_local", *NUMERIC[:3]]
    return {
        "status": "BLOCKED",
        "blockers": [*BLOCKERS, *extra],
        "rows": len(frame), "columns": len(frame.columns),
        "date_range": [str(frame.date.min().date()), str(frame.date.max().date())],
        "informative_columns": [c for c in frame if c != "date" and frame[c].nunique() > 1],
        "five_source_fields_complete": int(frame[source_fields].notna().all(axis=1).sum()),
        "duplicate_rows": int(frame.duplicated().sum()),
        "duplicate_dates": int(frame.date.duplicated().sum()),
        "dtypes": {c: str(t) for c, t in frame.dtypes.items()},
        "missing": frame.isna().sum().astype(int).to_dict(),
        "numeric_summary": numeric.describe().to_dict(),
        "iqr_outlier_counts": outliers.sum().astype(int).to_dict(),
        "zero_step_days": int(frame.step_count.eq(0).sum()),
        "retrospective_complete_pairs": int(
            pairs[[TARGET, "step_count", "active_time_minutes"]].notna().all(axis=1).sum()
        ) if not pairs.empty else 0,
        "candidate_boundary_violations": int(
            (pairs.activity_end_candidate > pairs.sleep_start_local).sum()
        ) if not pairs.empty else 0,
        "effective_training_samples": 0, "train_samples": 0, "test_samples": 0,
    }


def require_ready(audit: dict) -> None:
    """Fail closed: this candidate dataset is not approved for model fitting."""
    # No boolean override: resolving provenance requires revising the data contract.
    raise ValueError("Training disabled: " + "; ".join(audit["blockers"]))


def source_hash(path: Path) -> str:
    """Fingerprint a private input without publishing its contents."""
    return hashlib.sha256(path.read_bytes()).hexdigest()
