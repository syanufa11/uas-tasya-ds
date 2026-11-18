"""Synthetic temporal-boundary checks; these are not research observations."""

import pandas as pd
import pytest

from scripts.verify_dataset_feasibility import prepare


@pytest.mark.parametrize("source_is_utc", [True, False])
def test_conservative_bucket_and_overlap_quarantine(source_is_utc: bool) -> None:
    intervals = [
        ("2026-01-02 01:00", "2026-01-02 03:00"),
        ("2026-01-02 17:00", "2026-01-02 23:00"),
        ("2026-01-04 16:00", "2026-01-04 22:00"),
        ("2026-01-04 16:00", "2026-01-04 22:00"),
    ]
    frame = pd.DataFrame({
        "com.samsung.health.sleep.start_time": [s for s, _ in intervals],
        "com.samsung.health.sleep.end_time": [e for _, e in intervals],
        "com.samsung.health.sleep.time_offset": ["UTC+0700"] * 4,
        "sleep_duration": [pd.NA] * 4,
    })
    selected, info = prepare(frame, source_is_utc)
    assert info["overlapping_rows"] == 2
    assert info["after_overlap_quarantine"] == 2
    assert not selected["activity_date"].duplicated().any()
    cutoff = pd.to_datetime(selected["activity_date"], utc=True) + pd.Timedelta(days=1)
    assert cutoff.le(selected["start_utc"]).all()
    assert selected["sleep_duration"].isna().all()
    if source_is_utc:
        assert len(selected) == 1
        assert selected["interval_duration_minutes"].iloc[0] == 360
    else:
        assert len(selected) == 2
