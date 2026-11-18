"""Samsung Health CSV parsing, timestamp/timezone validation, cleaning, and overlap detection."""

from __future__ import annotations

import csv
import io
import re
from datetime import UTC, datetime, timedelta, timezone
from typing import Any

import pandas as pd

_DELIMITERS = (",", ";", "\t", "|")
_OFFSET_PATTERN = re.compile(r"^(?:UTC)?\s*([+-])\s*(\d{2}):?(\d{2})$", re.IGNORECASE)


def parse_samsung_csv(text: str) -> tuple[list[str], list[dict[str, str]], dict[str, Any]]:
    """Parse Samsung Health CSV text with preamble detection and strict row-width checks.

    Handles the 3-field ``com.samsung.*`` preamble row, auto-detects the delimiter
    among ``,``, ``;``, ``\\t``, and ``|``, and tolerates a single trailing empty
    field per data row without shifting headers. Malformed rows are counted rather
    than silently skipped.
    """
    if not text.strip():
        return [], [], {
            "delimiter": repr(","),
            "has_preamble": False,
            "header_row": 0,
            "metadata_rows": 0,
            "row_count": 0,
            "trailing_empty_field_rows": 0,
            "malformed_rows": 0,
            "duplicate_header_names": 0,
            "status": "empty",
        }

    candidates: list[tuple[int, str, list[list[str]]]] = []
    for delimiter in _DELIMITERS:
        parsed = list(csv.reader(io.StringIO(text), delimiter=delimiter))
        max_cols = max((len(row) for row in parsed[:3]), default=0)
        candidates.append((max_cols, delimiter, parsed))

    _, delimiter, parsed = max(candidates, key=lambda item: item[0])
    has_preamble = bool(
        parsed and len(parsed[0]) == 3 and parsed[0][0].startswith("com.samsung.")
    )
    header_idx = 1 if has_preamble else 0
    header = parsed[header_idx] if len(parsed) > header_idx else []
    data_rows = parsed[header_idx + 1 :]

    trailing = 0
    malformed = 0
    records: list[dict[str, str]] = []
    for row in data_rows:
        normalized = row
        if len(normalized) == len(header) + 1 and normalized[-1] == "":
            normalized = normalized[:-1]
            trailing += 1
        if len(normalized) != len(header):
            malformed += 1
        records.append(dict(zip(header, normalized, strict=False)))

    metadata: dict[str, Any] = {
        "delimiter": repr(delimiter),
        "has_preamble": has_preamble,
        "header_row": header_idx + 1 if header else 0,
        "metadata_rows": header_idx,
        "row_count": len(records),
        "trailing_empty_field_rows": trailing,
        "malformed_rows": malformed,
        "duplicate_header_names": len(header) - len(set(header)),
        "status": "width_mismatch" if malformed else "ok",
    }
    return header, records, metadata


def parse_iso_timestamp(value: object) -> datetime | None:
    """Parse an ISO-8601 timestamp string or datetime; return None if missing or invalid."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    if isinstance(value, pd.Timestamp):
        return None if pd.isna(value) else value.to_pydatetime()
    if isinstance(value, datetime):
        return value
    text = str(value).strip()
    if not text:
        return None
    normalized = text[:-1] + "+00:00" if text.endswith("Z") else text
    try:
        return datetime.fromisoformat(normalized)
    except ValueError:
        return None


def parse_utc_offset(offset_value: object) -> timezone | None:
    """Parse an offset string like 'UTC+0700' or '+07:00' into a fixed timezone."""
    if offset_value is None or (isinstance(offset_value, float) and pd.isna(offset_value)):
        return None
    match = _OFFSET_PATTERN.match(str(offset_value).strip())
    if not match:
        return None
    sign = 1 if match.group(1) == "+" else -1
    hours = int(match.group(2))
    minutes = int(match.group(3))
    if hours > 23 or minutes > 59:
        return None
    return timezone(sign * timedelta(hours=hours, minutes=minutes))


def _to_utc_and_local(
    raw_value: object,
    offset_tz: timezone | None,
    source_is_utc: bool,
) -> tuple[datetime | None, datetime | None, str | None]:
    dt = parse_iso_timestamp(raw_value)
    if dt is None:
        return None, None, "invalid_or_missing_timestamp"

    if dt.tzinfo is not None:
        dt_utc = dt.astimezone(UTC)
    elif source_is_utc:
        dt_utc = dt.replace(tzinfo=UTC)
    elif offset_tz is not None:
        dt_utc = dt.replace(tzinfo=offset_tz).astimezone(UTC)
    else:
        return None, None, "ambiguous_naive_timestamp"

    dt_local = dt_utc.astimezone(offset_tz) if offset_tz is not None else None
    return dt_utc, dt_local, None


def validate_and_normalize_timestamps(
    df: pd.DataFrame,
    start_col: str = "start_time",
    end_col: str = "end_time",
    offset_col: str | None = "time_offset",
    source_is_utc: bool = True,
) -> pd.DataFrame:
    """Validate start/end timestamps and derive explicit UTC and local datetimes.

    Preserves the original text columns without modification and avoids
    double-shifting timestamps that already carry timezone information.
    """
    if start_col not in df.columns or end_col not in df.columns:
        raise KeyError(f"Missing required timestamp columns: {start_col!r}, {end_col!r}")

    out = df.copy()
    start_utcs: list[pd.Timestamp | None] = []
    end_utcs: list[pd.Timestamp | None] = []
    start_locals: list[datetime | None] = []
    end_locals: list[datetime | None] = []
    errors: list[str | None] = []

    has_offset = offset_col is not None and offset_col in out.columns
    for idx in range(len(out)):
        offset_tz = parse_utc_offset(out[offset_col].iloc[idx]) if has_offset else None
        if has_offset and pd.notna(out[offset_col].iloc[idx]) and offset_tz is None:
            start_utcs.append(pd.NaT)
            end_utcs.append(pd.NaT)
            start_locals.append(None)
            end_locals.append(None)
            errors.append("invalid_time_offset")
            continue

        s_utc, s_loc, s_err = _to_utc_and_local(
            out[start_col].iloc[idx], offset_tz, source_is_utc
        )
        e_utc, e_loc, e_err = _to_utc_and_local(
            out[end_col].iloc[idx], offset_tz, source_is_utc
        )
        err = s_err or e_err
        if err is not None or s_utc is None or e_utc is None:
            start_utcs.append(pd.NaT)
            end_utcs.append(pd.NaT)
            start_locals.append(None)
            end_locals.append(None)
            errors.append(err or "invalid_timestamp")
        else:
            start_utcs.append(pd.Timestamp(s_utc))
            end_utcs.append(pd.Timestamp(e_utc))
            start_locals.append(s_loc)
            end_locals.append(e_loc)
            errors.append(None)

    out["start_utc"] = pd.Series(start_utcs, index=out.index, dtype="datetime64[ns, UTC]")
    out["end_utc"] = pd.Series(end_utcs, index=out.index, dtype="datetime64[ns, UTC]")
    out["start_local"] = start_locals
    out["end_local"] = end_locals
    out["timestamp_error"] = errors
    out["timestamp_valid"] = out["timestamp_error"].isna()
    out["interval_duration_minutes"] = (
        (out["end_utc"] - out["start_utc"]).dt.total_seconds() / 60.0
    )
    out["awake_date_local"] = [
        dt.date() if isinstance(dt, datetime) else None for dt in out["end_local"]
    ]
    return out


def clean_sleep_sessions(
    df: pd.DataFrame,
    start_col: str = "start_time",
    end_col: str = "end_time",
    offset_col: str | None = "time_offset",
    duration_col: str | None = "sleep_duration",
    source_is_utc: bool = True,
    max_duration_minutes: float = 1440.0,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    """Clean sleep session records deterministically while quarantining invalid rows.

    - Missing ``sleep_duration`` values remain ``NaN`` (never filled with 0).
    - Invalid timestamps or non-positive / out-of-range interval durations are
      moved to ``quarantined_df`` with an explicit ``quarantine_reason``.
    - Overlapping valid sessions are flagged via ``is_overlapping`` without
      silently dropping or summing overlapping durations.
    """
    normalized = validate_and_normalize_timestamps(
        df,
        start_col=start_col,
        end_col=end_col,
        offset_col=offset_col,
        source_is_utc=source_is_utc,
    )

    if duration_col and duration_col in normalized.columns:
        normalized[duration_col] = pd.to_numeric(normalized[duration_col], errors="coerce")

    reasons: list[str | None] = []
    for idx in range(len(normalized)):
        if not bool(normalized["timestamp_valid"].iloc[idx]):
            reasons.append(str(normalized["timestamp_error"].iloc[idx]))
            continue
        dur = float(normalized["interval_duration_minutes"].iloc[idx])
        if dur <= 0:
            reasons.append("non_positive_duration")
        elif dur > max_duration_minutes:
            reasons.append("exceeds_max_duration")
        else:
            reasons.append(None)

    normalized["quarantine_reason"] = reasons
    is_valid = normalized["quarantine_reason"].isna()
    clean_df = normalized.loc[is_valid].copy().drop(columns=["quarantine_reason"])
    quarantined_df = normalized.loc[~is_valid].copy()

    clean_df = flag_overlapping_sessions(clean_df, start_col="start_utc", end_col="end_utc")

    summary: dict[str, Any] = {
        "rows_in": len(df),
        "rows_clean": len(clean_df),
        "rows_quarantined": len(quarantined_df),
        "overlapping_rows": int(clean_df["is_overlapping"].sum()) if len(clean_df) else 0,
        "missing_sleep_duration": (
            int(clean_df[duration_col].isna().sum())
            if duration_col and duration_col in clean_df.columns
            else None
        ),
    }
    return clean_df, quarantined_df, summary


def detect_overlapping_sessions(
    df: pd.DataFrame,
    start_col: str = "start_utc",
    end_col: str = "end_utc",
) -> pd.DataFrame:
    """Detect all pairs of sleep sessions with strictly positive time overlap.

    Touching intervals where ``end_a == start_b`` have 0 overlap and are not flagged.
    """
    columns = ["index_a", "index_b", "overlap_minutes"]
    if df.empty:
        return pd.DataFrame(columns=columns)

    ordered = df[[start_col, end_col]].dropna().sort_values(by=[start_col, end_col])
    indices = list(ordered.index)
    starts = list(ordered[start_col])
    ends = list(ordered[end_col])

    overlaps: list[dict[str, Any]] = []
    for i in range(len(indices)):
        for j in range(i + 1, len(indices)):
            if starts[j] >= ends[i]:
                break
            overlap_sec = (min(ends[i], ends[j]) - max(starts[i], starts[j])).total_seconds()
            if overlap_sec > 0:
                overlaps.append(
                    {
                        "index_a": indices[i],
                        "index_b": indices[j],
                        "overlap_minutes": overlap_sec / 60.0,
                    }
                )
    return pd.DataFrame(overlaps, columns=columns)


def flag_overlapping_sessions(
    df: pd.DataFrame,
    start_col: str = "start_utc",
    end_col: str = "end_utc",
) -> pd.DataFrame:
    """Return a copy of ``df`` with a boolean ``is_overlapping`` column."""
    out = df.copy()
    pairs = detect_overlapping_sessions(out, start_col=start_col, end_col=end_col)
    if pairs.empty:
        out["is_overlapping"] = False
        return out
    flagged = set(pairs["index_a"]).union(set(pairs["index_b"]))
    out["is_overlapping"] = out.index.isin(flagged)
    return out


def integrate_sleep_with_daily_activity(
    sleep_df: pd.DataFrame,
    activity_df: pd.DataFrame,
    sleep_date_col: str = "awake_date_local",
    activity_date_col: str = "activity_date",
    lag_days: int = 1,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Left-join sleep sessions with prior-day canonical daily activity safely.

    Validates one-to-one cardinality on ``activity_df[activity_date_col]`` so
    duplicate daily records cannot silently cause a many-to-many row explosion.
    """
    if activity_df[activity_date_col].duplicated().any():
        raise ValueError(
            f"Duplicate keys in activity_df[{activity_date_col!r}]; "
            "deduplicate to one canonical row per day before joining."
        )

    left = sleep_df.copy()
    left["_join_activity_date"] = pd.to_datetime(left[sleep_date_col]) - pd.Timedelta(
        days=lag_days
    )
    right = activity_df.copy()
    right["_join_activity_date"] = pd.to_datetime(right[activity_date_col])

    merged = left.merge(
        right.drop(columns=[activity_date_col]),
        on="_join_activity_date",
        how="left",
        validate="many_to_one",
    ).drop(columns=["_join_activity_date"])

    non_key_cols = [c for c in activity_df.columns if c != activity_date_col]
    matched = int(merged[non_key_cols].notna().any(axis=1).sum()) if non_key_cols else 0
    report = {
        "sleep_rows": len(sleep_df),
        "merged_rows": len(merged),
        "matched_rows": matched,
        "unmatched_rows": len(merged) - matched,
    }
    return merged, report
