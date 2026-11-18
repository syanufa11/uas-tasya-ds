"""Daily candidate dataset; no imputation or public dashboard integration."""

from __future__ import annotations

from zoneinfo import ZoneInfo

import pandas as pd

from samsung_health.sleep import clean_sleep_sessions, flag_overlapping_sessions

SLEEP_PREFIX = "com.samsung.health.sleep."
UNITS = {
    "date": "tanggal bangun/kalender kandidat, dd/mm/yyyy",
    "sleep_duration_minutes": "menit tersimpan; missing dipertahankan",
    "sleep_interval_minutes": "menit, turunan end-start; bukan tidur fisiologis",
    "sleep_start_local": "ISO 8601 dengan offset +07:00, Asia/Jakarta",
    "sleep_end_local": "ISO 8601 dengan offset +07:00, Asia/Jakarta",
    "bedtime_hour": "jam desimal [0,24), turunan waktu mulai",
    "wake_hour": "jam desimal [0,24), turunan waktu akhir",
    "step_count": "langkah per label hari sumber",
    "active_time_minutes": "menit, kandidat empiris active_time/60000",
    "secondary_sleep_session_count": "jumlah sesi tambahan; bukan klasifikasi nap",
    "day_of_week": "Senin=0 sampai Minggu=6, turunan kalender",
    "is_weekend": "Sabtu/Minggu=1, lainnya=0, turunan kalender",
}


def daily_sleep(sleep: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Quarantine overlaps; retain longest session per candidate Jakarta wake date."""
    clean, quarantine, info = clean_sleep_sessions(
        sleep, start_col=SLEEP_PREFIX + "start_time", end_col=SLEEP_PREFIX + "end_time",
        offset_col=SLEEP_PREFIX + "time_offset", source_is_utc=True,
    )
    if not clean[SLEEP_PREFIX + "time_offset"].eq("UTC+0700").all():
        raise ValueError("Unexpected offset: review Jakarta attribution before building")
    # Conflicting overlapping records are both quarantined, including identical intervals.
    eligible = clean.loc[~clean["is_overlapping"]].copy()
    eligible["start_local"] = eligible["start_utc"].dt.tz_convert(ZoneInfo("Asia/Jakarta"))
    eligible["end_local"] = eligible["end_utc"].dt.tz_convert(ZoneInfo("Asia/Jakarta"))
    eligible["date"] = eligible["end_local"].dt.tz_localize(None).dt.normalize()
    counts = eligible.groupby("date").size()
    selected = eligible.sort_values(
        ["interval_duration_minutes", "start_utc"], ascending=[False, True], kind="stable",
    ).drop_duplicates("date").copy()
    result = pd.DataFrame({
        "date": selected["date"],
        "sleep_duration_minutes": selected["sleep_duration"],
        "sleep_interval_minutes": selected["interval_duration_minutes"],
        "sleep_start_local": selected["start_local"].map(lambda v: v.isoformat()),
        "sleep_end_local": selected["end_local"].map(lambda v: v.isoformat()),
        "bedtime_hour": (selected["start_local"] - selected["start_local"].dt.normalize())
        .dt.total_seconds() / 3600,
        "wake_hour": (selected["end_local"] - selected["end_local"].dt.normalize())
        .dt.total_seconds() / 3600,
        "secondary_sleep_session_count": selected["date"].map(counts) - 1,
    })
    info.update({
        "basic_quarantine": len(quarantine),
        "interval_duplicate_excess": int(clean.duplicated(["start_utc", "end_utc"]).sum()),
        "overlap_quarantined": int(clean["is_overlapping"].sum()),
        "secondary_sessions_not_summed": len(eligible) - len(result),
        "daily_sleep_rows": len(result),
        "remaining_overlap_pairs": int(flag_overlapping_sessions(eligible)["is_overlapping"].sum()),
    })
    # Fail rather than publish corrupt stored duration or mislabel its unit.
    stored = result["sleep_duration_minutes"]
    mismatch = (stored - result["sleep_interval_minutes"]).abs()
    if ((stored <= 0) | (stored > 1440) | (mismatch >= 1)).any():
        raise ValueError("Stored sleep duration is inconsistent with minute intervals")
    info["stored_duration_max_difference_minutes"] = float(mismatch.max())
    return result, info


def daily_activity(activity: pd.DataFrame) -> pd.DataFrame:
    """Keep one canonical summary, rejecting duplicates instead of summing sources."""
    dates = pd.to_datetime(activity["day_time"], errors="raise")
    if dates.isna().any() or not dates.eq(dates.dt.normalize()).all():
        raise ValueError("Missing or non-midnight activity day label")
    if dates.duplicated().any():
        raise ValueError("Duplicate activity date; ambiguous canonical daily source")
    values = activity[["step_count", "active_time"]].apply(pd.to_numeric, errors="raise")
    if (values < 0).any().any() or (values["active_time"] > 86_400_000).any():
        raise ValueError("Negative activity or implausible candidate millisecond duration")
    if values["step_count"].dropna().mod(1).ne(0).any():
        raise ValueError("Non-integer steps")
    return pd.DataFrame({
        "date": dates, "step_count": values["step_count"],
        "active_time_minutes": values["active_time"] / 60_000,
    })


def build_daily(sleep: pd.DataFrame, activity: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Outer calendar join; date labels in activity remain provisional local labels."""
    sleeps, info = daily_sleep(sleep)
    acts = daily_activity(activity)
    if sleeps.empty and acts.empty:
        raise ValueError("No eligible daily records")
    joined = sleeps.merge(acts, on="date", how="outer", validate="one_to_one")
    calendar = pd.DataFrame({"date": pd.date_range(joined.date.min(), joined.date.max())})
    joined = calendar.merge(joined, on="date", how="left", validate="one_to_one")
    joined["day_of_week"] = joined.date.dt.dayofweek
    joined["is_weekend"] = joined.day_of_week.ge(5).astype(int)
    joined = joined[list(UNITS)]
    info["coverage"] = {
        "sleep_dates": len(sleeps), "activity_dates": len(acts),
        "both": len(set(sleeps.date) & set(acts.date)),
        "sleep_only": len(set(sleeps.date) - set(acts.date)),
        "activity_only": len(set(acts.date) - set(sleeps.date)),
    }
    return joined, info


def validate_daily(frame: pd.DataFrame) -> dict:
    """Return aggregate validation evidence, including missingness and feature variability."""
    informative = [c for c in frame if c != "date" and frame[c].nunique() > 1]
    complete = ["sleep_start_local", "sleep_end_local", "sleep_duration_minutes",
                "step_count", "active_time_minutes"]
    return {
        "rows": len(frame), "columns": len(frame.columns),
        "informative_non_key_columns": informative,
        "date_range": [v.strftime("%d/%m/%Y") for v in [frame.date.min(), frame.date.max()]],
        "duplicate_dates": int(frame.date.duplicated().sum()),
        "missing": {c: {"count": int(frame[c].isna().sum()),
                        "percent": round(float(frame[c].isna().mean() * 100), 4)} for c in frame},
        "complete_five_source_columns": int(frame[complete].notna().all(axis=1).sum()),
        "negative_steps": int(frame.step_count.lt(0).sum()),
        "nonpositive_or_over_24h_intervals": int(
            (frame.sleep_interval_minutes.le(0) | frame.sleep_interval_minutes.gt(1440)).sum()),
        "short_under_3h_or_over_12h_intervals_review": int(
            (frame.sleep_interval_minutes.lt(180) | frame.sleep_interval_minutes.gt(720)).sum()),
        "recorded_zero_step_days": int(frame.step_count.eq(0).sum()),
    }


def prior_activity_dates(sleep_starts: pd.Series) -> pd.Series:
    """Conservative retrospective exposure D: UTC date(start)-1, closed before sleep.

    Never substitute wake date minus one. A predictive task also needs availability
    verification, chronological splits, and a target definition fixed in advance.
    """
    starts = pd.to_datetime(sleep_starts, utc=True, errors="raise")
    return starts.dt.tz_localize(None).dt.normalize() - pd.Timedelta(days=1)
