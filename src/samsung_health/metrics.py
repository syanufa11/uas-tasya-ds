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


def format_hour_hhmm(hour: float) -> str:
    """Format fractional 24-hour clock value (can exceed 24 for post-midnight) as HH:MM."""
    if pd.isna(hour):
        return "– : –"
    wrapped = float(hour) % 24.0
    total_minutes = int(round(wrapped * 60)) % (24 * 60)
    hh, mm = divmod(total_minutes, 60)
    return f"{hh:02d}:{mm:02d}"


def _shifted_bed_hours(series: pd.Series) -> pd.Series:
    """Map post-midnight bed hours (< 12:00) to >= 24.0 for continuous sleep-onset stats."""
    return series.astype(float).where(series.astype(float) >= 12.0, series.astype(float) + 24.0)


def compute_sleep_overview_kpis(df: pd.DataFrame) -> dict[str, float | int | str]:
    """Compute overview summary KPIs and period bounds from a sleep DataFrame."""
    if df.empty:
        return {
            "nights": 0,
            "avg_duration_h": 0.0,
            "median_duration_h": 0.0,
            "avg_bedtime": "– : –",
            "avg_waketime": "– : –",
            "start_date": "–",
            "end_date": "–",
            "weekday_nights": 0,
            "weekend_nights": 0,
        }

    bed_shifted = _shifted_bed_hours(df["bed_hour"])
    dates = pd.to_datetime(df["date"])
    weekend_count = int(df["is_weekend"].sum()) if "is_weekend" in df.columns else 0
    return {
        "nights": int(len(df)),
        "avg_duration_h": round(float(df["duration_h"].mean()), 2),
        "median_duration_h": round(float(df["duration_h"].median()), 2),
        "avg_bedtime": format_hour_hhmm(float(bed_shifted.mean())),
        "avg_waketime": format_hour_hhmm(float(df["wake_hour"].mean())),
        "start_date": dates.min().strftime("%Y-%m-%d"),
        "end_date": dates.max().strftime("%Y-%m-%d"),
        "weekday_nights": int(len(df) - weekend_count),
        "weekend_nights": weekend_count,
    }


def compute_consistency_metrics(df: pd.DataFrame) -> dict[str, float]:
    """Compute bedtime/wake-time SD, midpoint SD, and social jetlag in minutes."""
    if df.empty or len(df) < 2:
        return {
            "bedtime_sd_min": 0.0,
            "waketime_sd_min": 0.0,
            "midpoint_sd_min": 0.0,
            "social_jetlag_min": 0.0,
        }

    bed_shifted = _shifted_bed_hours(df["bed_hour"])
    wake = df["wake_hour"].astype(float)
    midpoint = bed_shifted + (df["duration_h"].astype(float) / 2.0)

    is_weekend = df["is_weekend"].astype(bool)
    if is_weekend.any() and (~is_weekend).any():
        msf = float(midpoint[is_weekend].mean())
        msw = float(midpoint[~is_weekend].mean())
        social_jetlag_min = abs(msf - msw) * 60.0
    else:
        social_jetlag_min = 0.0

    return {
        "bedtime_sd_min": round(float(bed_shifted.std(ddof=1) * 60.0), 1),
        "waketime_sd_min": round(float(wake.std(ddof=1) * 60.0), 1),
        "midpoint_sd_min": round(float(midpoint.std(ddof=1) * 60.0), 1),
        "social_jetlag_min": round(social_jetlag_min, 1),
    }


def summarize_weekday_vs_weekend(df: pd.DataFrame) -> pd.DataFrame:
    """Compare sleep duration and schedule metrics between weekdays and weekends."""
    if df.empty:
        return pd.DataFrame(
            columns=[
                "Kelompok",
                "Jumlah Malam",
                "Rata-rata (jam)",
                "Median (jam)",
                "IQR (jam)",
                "Rata-rata Tidur",
                "Rata-rata Bangun",
            ]
        )

    rows = []
    for is_wknd, label in ((False, "Hari Kerja (Sen–Jum)"), (True, "Akhir Pekan (Sab–Min)")):
        sub = df[df["is_weekend"].astype(bool) == is_wknd]
        if sub.empty:
            continue
        q75 = float(sub["duration_h"].quantile(0.75))
        q25 = float(sub["duration_h"].quantile(0.25))
        bed_mean = float(_shifted_bed_hours(sub["bed_hour"]).mean())
        rows.append(
            {
                "Kelompok": label,
                "Jumlah Malam": int(len(sub)),
                "Rata-rata (jam)": round(float(sub["duration_h"].mean()), 2),
                "Median (jam)": round(float(sub["duration_h"].median()), 2),
                "IQR (jam)": round(q75 - q25, 2),
                "Rata-rata Tidur": format_hour_hhmm(bed_mean),
                "Rata-rata Bangun": format_hour_hhmm(float(sub["wake_hour"].mean())),
            }
        )
    return pd.DataFrame(rows)


def prepare_weekly_trends(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate sleep duration and schedule by ISO week start for trend charts."""
    if df.empty:
        return pd.DataFrame(
            columns=["week_start", "avg_duration_h", "avg_bed_hour", "avg_wake_hour", "nights"]
        )

    work = df.copy()
    dates = pd.to_datetime(work["date"])
    work["week_start"] = (dates - pd.to_timedelta(dates.dt.dayofweek, unit="D")).dt.normalize()
    work["bed_shifted"] = _shifted_bed_hours(work["bed_hour"])
    grouped = (
        work.groupby("week_start", as_index=False)
        .agg(
            avg_duration_h=("duration_h", "mean"),
            avg_bed_hour=("bed_shifted", "mean"),
            avg_wake_hour=("wake_hour", "mean"),
            nights=("duration_h", "count"),
        )
        .sort_values("week_start")
        .reset_index(drop=True)
    )
    return grouped


def prepare_calendar_heatmap(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare week-by-weekday grid for sleep activity calendar heatmap."""
    if df.empty:
        return pd.DataFrame(
            columns=["week_label", "weekday_short", "weekday_idx", "duration_h", "date_str"]
        )

    short_days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    work = df.copy()
    dates = pd.to_datetime(work["date"])
    week_start = (dates - pd.to_timedelta(dates.dt.dayofweek, unit="D")).dt.normalize()
    work["week_label"] = week_start.dt.strftime("%Y-%m-%d")
    work["weekday_idx"] = dates.dt.dayofweek
    work["weekday_short"] = work["weekday_idx"].map(lambda i: short_days[int(i)])
    work["date_str"] = dates.dt.strftime("%Y-%m-%d")
    return work[["week_label", "weekday_short", "weekday_idx", "duration_h", "date_str"]]
