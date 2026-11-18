"""Reproduce local TASK 11A diagnostics without exporting individual records."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from samsung_health.sleep import (  # noqa: E402
    clean_sleep_sessions,
    parse_samsung_csv,
)


def fingerprint(root: Path) -> dict[Path, str]:
    """Hash source files locally; never put source paths in outputs."""
    return {
        p.relative_to(root): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in root.rglob("*") if p.is_file()
    }


def read_entity(root: Path, entity: str) -> pd.DataFrame:
    """Read exactly one Samsung CSV and reject malformed widths."""
    files = list(root.glob(f"{entity}.*.csv"))
    if len(files) != 1:
        raise ValueError(f"Expected exactly one CSV for {entity}")
    _, records, meta = parse_samsung_csv(files[0].read_text(encoding="utf-8-sig"))
    if meta["status"] != "ok" or meta["duplicate_header_names"]:
        raise ValueError(f"Invalid CSV structure: {entity}")
    return pd.DataFrame(records).replace("", pd.NA)


def describe(frame: pd.DataFrame, columns: list[str]) -> dict:
    """Return only aggregate counts and numeric ranges."""
    result = {}
    for col in columns:
        values = frame[col]
        numeric = pd.to_numeric(values, errors="raise")
        result[col] = {
            "rows": len(values), "missing": int(values.isna().sum()),
            "unique": int(values.nunique()), "zero": int(numeric.eq(0).sum()),
            "min": float(numeric.min()), "max": float(numeric.max()),
        }
    return result


def prepare(sleep: pd.DataFrame, source_is_utc: bool) -> tuple[pd.DataFrame, dict]:
    """Quarantine every overlap and select one interval per conservative bucket.

    Bucket D is closed no earlier than (D+1) 00:00 UTC. This is conservative
    both if activity day labels encode UTC days and if they encode UTC+07 days.
    It intentionally does not claim to measure the entire waking day before bed.
    """
    clean, quarantine, info = clean_sleep_sessions(
        sleep, start_col="com.samsung.health.sleep.start_time",
        end_col="com.samsung.health.sleep.end_time",
        offset_col="com.samsung.health.sleep.time_offset", source_is_utc=source_is_utc,
    )
    assert quarantine.empty
    eligible = clean.loc[~clean["is_overlapping"]].copy()
    eligible["activity_date"] = (
        eligible["start_utc"].dt.tz_localize(None).dt.normalize() - pd.Timedelta(days=1)
    )
    selected = eligible.sort_values(
        ["interval_duration_minutes", "start_utc"], ascending=[False, True], kind="stable",
    ).drop_duplicates("activity_date").sort_values("start_utc")
    info.update({
        "after_overlap_quarantine": len(eligible),
        "selected": len(selected), "secondary_intervals_not_selected": len(eligible)-len(selected),
        "awake_dates_all": int(clean["awake_date_local"].nunique()),
        "awake_dates_after_overlap": int(eligible["awake_date_local"].nunique()),
        "awake_span_days": int((pd.Timestamp(clean["awake_date_local"].max())
                                - pd.Timestamp(clean["awake_date_local"].min())).days + 1),
    })
    return selected, info


def main() -> None:
    """Write aggregate local verification evidence, never raw or joined records."""
    roots = list(ROOT.glob("samsunghealth_*"))
    if len(roots) != 1:
        raise ValueError("Specify a workspace with exactly one Samsung Health export")
    raw = roots[0]
    before = fingerprint(raw)
    sleep = read_entity(raw, "com.samsung.shealth.sleep")
    activity = read_entity(raw, "com.samsung.shealth.activity.day_summary")
    activity["activity_date"] = pd.to_datetime(activity["day_time"], errors="raise")
    assert activity["activity_date"].notna().all()
    assert not activity["activity_date"].duplicated().any()
    assert activity["activity_date"].eq(activity["activity_date"].dt.normalize()).all()
    columns = ["step_count", "active_time", "walk_time", "run_time", "exercise_time",
               "distance", "calorie", "move_hourly_count"]
    for col in columns:
        activity[col] = pd.to_numeric(activity[col], errors="raise")
        assert activity[col].ge(0).all()
    result = {"pandas_version": pd.__version__, "raw_activity": describe(activity, columns)}
    result["activity_span"] = {
        "start": str(activity["activity_date"].min().date()),
        "end": str(activity["activity_date"].max().date()),
        "missing_days": len(pd.date_range(activity["activity_date"].min(),
                                          activity["activity_date"].max())
                            .difference(activity["activity_date"])),
    }
    result["raw_sleep_duration"] = describe(
        sleep.assign(sleep_duration=pd.to_numeric(sleep["sleep_duration"])), ["sleep_duration"]
    )
    for source_is_utc, name in [(True, "utc_text_candidate"), (False, "local_text_sensitivity")]:
        selected, info = prepare(sleep, source_is_utc)
        joined = selected.merge(activity[["activity_date", *columns]], on="activity_date",
                                how="left", validate="one_to_one", indicator=True)
        assert len(joined) == len(selected)
        matched = joined["_merge"].eq("both")
        cutoff = pd.to_datetime(joined["activity_date"], utc=True) + pd.Timedelta(days=1)
        assert cutoff.le(joined["start_utc"]).all()
        joined["start_clock_minutes"] = (
            pd.to_datetime(joined["start_local"]).dt.hour * 60
            + pd.to_datetime(joined["start_local"]).dt.minute
        )
        joined["end_clock_minutes"] = (
            pd.to_datetime(joined["end_local"]).dt.hour * 60
            + pd.to_datetime(joined["end_local"]).dt.minute
        )
        info.update({
            "matched": int(matched.sum()), "unmatched": int((~matched).sum()),
            "duplicate_join_keys": int(joined["activity_date"].duplicated().sum()),
            "temporal_boundary_violations": int((cutoff > joined["start_utc"]).sum()),
            "statistics": describe(joined, ["interval_duration_minutes", "sleep_duration",
                                            "start_clock_minutes", "end_clock_minutes", *columns]),
            "complete_core": int(joined[["interval_duration_minutes", "start_clock_minutes",
                                         "end_clock_minutes", "step_count", "active_time"]]
                                 .notna().all(axis=1).sum()),
            "activity_date_span": [str(joined["activity_date"].min().date()),
                                   str(joined["activity_date"].max().date())],
            "sleep_local_span": [str(min(joined["start_local"])),
                                 str(max(joined["end_local"]))],
        })
        result[name] = info

    # Reproduce the attractive but unsafe wake-date-minus-one join diagnostic.
    clean, _, _ = clean_sleep_sessions(
        sleep, start_col="com.samsung.health.sleep.start_time",
        end_col="com.samsung.health.sleep.end_time",
        offset_col="com.samsung.health.sleep.time_offset",
    )
    wake = clean.loc[~clean["is_overlapping"]].sort_values(
        ["interval_duration_minutes", "start_utc"], ascending=[False, True],
    ).drop_duplicates("awake_date_local")
    local_start = pd.to_datetime(wake["start_local"]).dt.tz_localize(None)
    previous_local_day_end = pd.to_datetime(wake["awake_date_local"])
    result["unsafe_wake_minus_one"] = {
        "rows": len(wake),
        "activity_day_overlaps_sleep": int(previous_local_day_end.gt(local_start).sum()),
    }

    paths = {}
    for path in raw.rglob("*.json"):
        paths.setdefault(path.name, []).append(path)
    differences = {col: [] for col in columns if col != "move_hourly_count"}
    units, utc_day_match, local_day_match, hourly_count, bin_count = set(), 0, 0, 0, 0
    for _, row in activity.iterrows():
        candidates = paths[str(row["extra_data"])]
        assert len(candidates) == 1
        obj = json.loads(candidates[0].read_text(encoding="utf-8-sig"))
        bins = obj.get("mUnitDataList", [])
        bin_count += len(bins)
        units.update(b["mTimeUnit"] for b in bins)
        sums = {
            "step_count": sum(b.get("walkStep", 0)+b.get("runStep", 0) for b in bins),
            "walk_time": sum(b.get("mWalkTime", 0) for b in bins),
            "run_time": sum(b.get("mRunTime", 0) for b in bins),
            "exercise_time": sum(b.get("exerciseTime", 0) for b in bins),
            "distance": sum(b.get("distance", 0) for b in bins),
            "calorie": sum(b.get("mCalorie", 0) for b in bins),
        }
        sums["active_time"] = (sums["walk_time"]+sums["run_time"]
                               + sum(b.get("mOthersTime", 0) for b in bins))
        for col, value in sums.items():
            differences[col].append(abs(float(row[col])-value))
        for hour in obj.get("hourlyDataList", []):
            dt = pd.to_datetime(hour["startTime"], unit="ms", utc=True)
            utc_day_match += int(dt.date() == row["activity_date"].date())
            local_day_match += int(dt.tz_convert("Asia/Jakarta").date()
                                   == row["activity_date"].date())
            hourly_count += 1
    result["json_crosscheck"] = {
        "files": len(activity), "bins": bin_count, "mTimeUnit_values": sorted(units),
        "hourly_entries": hourly_count, "utc_date_matches": utc_day_match,
        "local_date_matches": local_day_match,
        "max_absolute_sum_difference": {k: max(v) for k, v in differences.items()},
    }
    after = fingerprint(raw)
    assert before == after, "Source files changed during verification"
    result["raw_files_hash_verified_unchanged"] = len(before)
    target = ROOT / "data_audit" / "task11a_verification.json"
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Aggregate verification saved locally; all assertions passed.")


if __name__ == "__main__":
    main()
