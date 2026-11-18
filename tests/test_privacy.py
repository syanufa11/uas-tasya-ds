"""Tests for repository privacy and secret-leak guards."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_privacy  # noqa: E402


def test_find_forbidden_paths_flags_sensitive_exports() -> None:
    """Ensure Samsung Health exports, audit outputs, and secrets are flagged."""
    sample = [
        "dashboard/app.py",
        "samsunghealth_user_123/sleep.csv",
        "data_audit/summary.csv",
        "data_clean/sleep.parquet",
        ".env",
        ".env.example",
        "dashboard/.streamlit/secrets.toml",
    ]
    flagged = check_privacy.find_forbidden_paths(sample)
    assert "samsunghealth_user_123/sleep.csv" in flagged
    assert "data_audit/summary.csv" in flagged
    assert "data_clean/sleep.parquet" in flagged
    assert ".env" in flagged
    assert "dashboard/.streamlit/secrets.toml" in flagged
    assert "dashboard/app.py" not in flagged
    assert ".env.example" not in flagged


def test_tracked_repository_has_no_sensitive_files_or_secrets() -> None:
    """Verify current Git-tracked files pass all privacy checks."""
    assert check_privacy.main() == 0
