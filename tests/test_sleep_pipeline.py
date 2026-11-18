"""Synthetic unit tests for Samsung Health sleep pipeline and dashboard metrics."""

from datetime import date

import pandas as pd
import pytest

from src.samsung_health.metrics import (
    WEEKDAY_ORDER,
    prepare_consistency_series,
    summarize_stage_composition,
    summarize_weekday_duration,
    synthetic_quality_checks,
    synthetic_sleep_data,
)
from src.samsung_health.sleep import (
    clean_sleep_sessions,
    detect_overlapping_sessions,
    flag_overlapping_sessions,
    integrate_sleep_with_daily_activity,
    parse_samsung_csv,
    parse_utc_offset,
    validate_and_normalize_timestamps,
)


@pytest.fixture
def synthetic_sleep_rows() -> pd.DataFrame:
    """Synthetic sleep records covering cross-midnight, missing duration, overlap, and invalid."""
    return pd.DataFrame(
        [
            {
                "datauuid": "syn-1",
                "start_time": "2026-01-01 16:30:00.000",
                "end_time": "2026-01-01 23:30:00.000",
                "time_offset": "UTC+0700",
                "sleep_duration": "420",
                "sleep_score": "",
            },
            {
                "datauuid": "syn-2",
                "start_time": "2026-01-02 16:00:00.000",
                "end_time": "2026-01-02 23:00:00.000",
                "time_offset": "UTC+0700",
                "sleep_duration": "",
                "sleep_score": "",
            },
            {
                "datauuid": "syn-3-overlap",
                "start_time": "2026-01-02 22:30:00.000",
                "end_time": "2026-01-03 00:00:00.000",
                "time_offset": "UTC+0700",
                "sleep_duration": "90",
                "sleep_score": "",
            },
            {
                "datauuid": "syn-4-bad-dur",
                "start_time": "2026-01-03 18:00:00.000",
                "end_time": "2026-01-03 17:00:00.000",
                "time_offset": "UTC+0700",
                "sleep_duration": "",
                "sleep_score": "",
            },
            {
                "datauuid": "syn-5-bad-ts",
                "start_time": "not-a-timestamp",
                "end_time": "2026-01-04 00:00:00.000",
                "time_offset": "UTC+0700",
                "sleep_duration": "",
                "sleep_score": "",
            },
        ]
    )


def test_parse_samsung_csv_preamble_and_trailing_field() -> None:
    raw = (
        "com.samsung.shealth.sleep,1,2\n"
        "start_time,end_time,sleep_duration\n"
        "2026-01-01 16:00:00,2026-01-01 23:00:00,420,\n"
        "2026-01-02 16:00:00,2026-01-02 23:00:00\n"
    )
    header, records, meta = parse_samsung_csv(raw)
    assert header == ["start_time", "end_time", "sleep_duration"]
    assert len(records) == 2
    assert meta["has_preamble"] is True
    assert meta["trailing_empty_field_rows"] == 1
    assert meta["malformed_rows"] == 1
    assert meta["status"] == "width_mismatch"


def test_parse_samsung_csv_empty() -> None:
    header, records, meta = parse_samsung_csv("   \n")
    assert header == []
    assert records == []
    assert meta["status"] == "empty"


@pytest.mark.parametrize(
    ("raw_offset", "expected_hours"),
    [
        ("UTC+0700", 7.0),
        ("UTC-05:00", -5.0),
        ("+09:30", 9.5),
        ("invalid", None),
        (None, None),
    ],
)
def test_parse_utc_offset(raw_offset: object, expected_hours: float | None) -> None:
    tz = parse_utc_offset(raw_offset)
    if expected_hours is None:
        assert tz is None
    else:
        assert tz is not None
        assert tz.utcoffset(None).total_seconds() / 3600 == expected_hours


def test_validate_timestamps_no_double_shift() -> None:
    df = pd.DataFrame(
        [
            {
                "start_time": "2026-01-01 23:30:00+07:00",
                "end_time": "2026-01-02T06:30:00+07:00",
                "time_offset": "UTC+0700",
            }
        ]
    )
    res = validate_and_normalize_timestamps(df, source_is_utc=True)
    assert bool(res["timestamp_valid"].iloc[0]) is True
    assert res["interval_duration_minutes"].iloc[0] == pytest.approx(420.0)
    assert res["awake_date_local"].iloc[0] == date(2026, 1, 2)


def test_clean_sleep_sessions_quarantine_and_missing(
    synthetic_sleep_rows: pd.DataFrame,
) -> None:
    clean_df, quarantined_df, summary = clean_sleep_sessions(synthetic_sleep_rows)
    assert summary["rows_in"] == 5
    assert summary["rows_clean"] == 3
    assert summary["rows_quarantined"] == 2
    assert summary["overlapping_rows"] == 2
    assert summary["missing_sleep_duration"] == 1

    # Missing sleep_duration must remain NaN, never filled with 0.
    syn2 = clean_df.loc[clean_df["datauuid"] == "syn-2"].iloc[0]
    assert pd.isna(syn2["sleep_duration"])
    assert syn2["awake_date_local"] == date(2026, 1, 3)

    reasons = set(quarantined_df["quarantine_reason"])
    assert reasons == {"non_positive_duration", "invalid_or_missing_timestamp"}


def test_overlap_detection_excludes_touching_intervals() -> None:
    df = pd.DataFrame(
        {
            "start_utc": pd.to_datetime(
                [
                    "2026-01-01 00:00:00Z",
                    "2026-01-01 06:00:00Z",
                    "2026-01-01 05:30:00Z",
                ]
            ),
            "end_utc": pd.to_datetime(
                [
                    "2026-01-01 06:00:00Z",
                    "2026-01-01 08:00:00Z",
                    "2026-01-01 07:00:00Z",
                ]
            ),
        }
    )
    pairs = detect_overlapping_sessions(df)
    assert len(pairs) == 2
    assert set(zip(pairs["index_a"], pairs["index_b"], strict=True)) == {(0, 2), (2, 1)}

    flagged = flag_overlapping_sessions(df)
    assert list(flagged["is_overlapping"]) == [True, True, True]

    non_overlap = df.iloc[[0, 1]]
    assert detect_overlapping_sessions(non_overlap).empty


def test_integrate_sleep_with_daily_activity_cardinality_guard() -> None:
    sleep_df = pd.DataFrame(
        {
            "datauuid": ["s1", "s2"],
            "awake_date_local": [date(2026, 1, 2), date(2026, 1, 3)],
        }
    )
    activity_df = pd.DataFrame(
        {
            "activity_date": [date(2026, 1, 1)],
            "step_count": [7500],
        }
    )
    merged, report = integrate_sleep_with_daily_activity(sleep_df, activity_df)
    assert report == {
        "sleep_rows": 2,
        "merged_rows": 2,
        "matched_rows": 1,
        "unmatched_rows": 1,
    }
    assert merged.loc[0, "step_count"] == 7500
    assert pd.isna(merged.loc[1, "step_count"])

    dup_activity = pd.concat([activity_df, activity_df], ignore_index=True)
    with pytest.raises(ValueError, match="Duplicate keys"):
        integrate_sleep_with_daily_activity(sleep_df, dup_activity)


def test_dashboard_metrics_helpers_deterministic_and_empty_safe() -> None:
    df1 = synthetic_sleep_data(days=14, seed=42)
    df2 = synthetic_sleep_data(days=14, seed=42)
    pd.testing.assert_frame_equal(df1, df2)

    weekday = summarize_weekday_duration(df1)
    assert list(weekday["weekday"]) == WEEKDAY_ORDER

    stages = summarize_stage_composition(df1)
    assert stages["pct"].sum() == pytest.approx(100.0)

    long_series = prepare_consistency_series(df1)
    assert len(long_series) == 28

    empty = df1.iloc[0:0]
    assert summarize_weekday_duration(empty).empty
    assert prepare_consistency_series(empty).empty
    assert len(synthetic_quality_checks()) == 5
