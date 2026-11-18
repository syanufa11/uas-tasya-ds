"""Synthetic fixtures only: daily integration and temporal safeguards."""

import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from samsung_health.merged import (  # noqa: E402
    SLEEP_PREFIX,
    build_daily,
    daily_activity,
    daily_sleep,
    prior_activity_dates,
)


def sessions(intervals: list[tuple[str, str, object]]) -> pd.DataFrame:
    """Build explicitly synthetic UTC-text sleep records."""
    return pd.DataFrame([
        {SLEEP_PREFIX + "start_time": start, SLEEP_PREFIX + "end_time": end,
         SLEEP_PREFIX + "time_offset": "UTC+0700", "sleep_duration": duration}
        for start, end, duration in intervals
    ])


def test_daily_selection_missing_and_midnight() -> None:
    raw = sessions([
        ("2030-01-01 16:00", "2030-01-01 23:00", None),
        ("2030-01-02 06:00", "2030-01-02 07:00", 60),
    ])
    original = raw.copy(deep=True)
    result, info = daily_sleep(raw)
    assert len(result) == 1
    row = result.iloc[0]
    assert row.date == pd.Timestamp("2030-01-02")
    assert row.bedtime_hour == 23
    assert row.wake_hour == 6
    assert row.sleep_interval_minutes == 420
    assert pd.isna(row.sleep_duration_minutes)
    assert row.secondary_sleep_session_count == 1
    assert info["secondary_sessions_not_summed"] == 1
    pd.testing.assert_frame_equal(raw, original)


def test_all_overlaps_quarantined() -> None:
    raw = sessions([
        ("2030-01-01 16:00", "2030-01-01 23:00", 420),
        ("2030-01-01 16:00", "2030-01-01 23:00", 420),
        ("2030-01-02 16:00", "2030-01-02 23:00", 420),
    ])
    result, info = daily_sleep(raw)
    assert len(result) == 1
    assert info["overlap_quarantined"] == 2
    assert info["interval_duplicate_excess"] == 1


def test_join_preserves_unobserved_calendar_days() -> None:
    raw = sessions([("2030-01-01 16:00", "2030-01-01 23:00", 420)])
    activity = pd.DataFrame({"day_time": ["2030-01-01", "2030-01-04"],
                             "step_count": [0, 12], "active_time": [0, 120000]})
    result, info = build_daily(raw, activity)
    assert len(result) == 4
    assert result.date.is_unique
    assert result.iloc[0].step_count == 0
    assert pd.isna(result.iloc[1].step_count)
    assert pd.isna(result.iloc[2].secondary_sleep_session_count)
    assert result.iloc[3].active_time_minutes == 2
    assert info["coverage"]["sleep_only"] == 1
    repeated, _ = build_daily(raw, activity)
    pd.testing.assert_frame_equal(result, repeated)


@pytest.mark.parametrize("steps,active", [([-1], [0]), ([1.5], [0]), ([1], [-1])])
def test_invalid_activity_rejected(steps: list, active: list) -> None:
    with pytest.raises(ValueError):
        daily_activity(pd.DataFrame({"day_time": ["2030-01-01"],
                                     "step_count": steps, "active_time": active}))


def test_duplicate_activity_rejected() -> None:
    with pytest.raises(ValueError, match="Duplicate"):
        daily_activity(pd.DataFrame({"day_time": ["2030-01-01"] * 2,
                                     "step_count": [1, 2], "active_time": [60000, 120000]}))


def test_temporal_rule_uses_start_not_wake_date() -> None:
    starts = pd.Series(["2030-01-02T23:00:00+07:00", "2030-01-03T01:00:00+07:00"])
    dates = prior_activity_dates(starts)
    assert dates.tolist() == [pd.Timestamp("2030-01-01")] * 2
    cutoff = pd.to_datetime(dates, utc=True) + pd.Timedelta(days=1)
    assert cutoff.le(pd.to_datetime(starts, utc=True)).all()


def test_private_reports_rejected_by_privacy_guard() -> None:
    from scripts.check_privacy import find_forbidden_paths

    paths = ["reports/dataset_integration_report.md", "data_processed/samsung_health_merged.csv"]
    assert find_forbidden_paths(paths) == paths
