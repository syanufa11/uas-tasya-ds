"""Verify no sensitive data, exports, or credentials are tracked in Git."""

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FORBIDDEN_PATH_PATTERNS = (
    re.compile(r"(^|/)samsunghealth_"),
    re.compile(r"(^|/)com\.samsung\.(s?health)\."),
    re.compile(r"(^|/)data_audit/"),
    re.compile(r"(^|/)audit_report\.md$"),
    re.compile(r"(^|/)reports/(dataset_integration_report|uas_dataset_feasibility|model_evaluation)\.md$"),
    re.compile(r"(^|/)(data|data_raw|data_clean|data_cleaned|data_processed)/"),
    re.compile(r"(^|/)(raw|cleaned|processed|outputs|artifacts)/"),
    re.compile(r"(^|/)\.env($|\.(?!example$))"),
    re.compile(r"(^|/)secrets\.toml$"),
    re.compile(r"\.(pem|key|secret|parquet|feather|pkl|pickle|xlsx|xls|zip|tar\.gz|7z)$", re.I),
)

SECRET_CONTENT_PATTERNS = (
    re.compile(r"ghp_[A-Za-z0-9]{20,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----"),
)

TEXT_EXTENSIONS = {
    ".py",
    ".md",
    ".txt",
    ".toml",
    ".yml",
    ".yaml",
    ".json",
    ".csv",
    ".ipynb",
    ".sh",
}


def get_tracked_files(repo_root: Path = ROOT) -> list[str]:
    """Return tracked file paths relative to repo_root."""
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=True,
    )
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def find_forbidden_paths(paths: list[str]) -> list[str]:
    """Return any tracked paths matching forbidden sensitive patterns."""
    flagged: list[str] = []
    for path in paths:
        norm = path.replace("\\", "/")
        if any(pattern.search(norm) for pattern in FORBIDDEN_PATH_PATTERNS):
            flagged.append(norm)
    return flagged


def find_secret_leaks(paths: list[str], repo_root: Path = ROOT) -> list[str]:
    """Scan tracked text files for common credential patterns."""
    findings: list[str] = []
    for rel in paths:
        file_path = repo_root / rel
        if not file_path.is_file() or file_path.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for pattern in SECRET_CONTENT_PATTERNS:
            if pattern.search(content):
                findings.append(f"{rel}: matched {pattern.pattern}")
    return findings


def main() -> int:
    """Run privacy and secret checks on Git-tracked files."""
    tracked = get_tracked_files()
    bad_paths = find_forbidden_paths(tracked)
    secret_leaks = find_secret_leaks(tracked)

    if bad_paths:
        print("ERROR: Forbidden sensitive paths tracked in Git:", file=sys.stderr)
        for p in bad_paths:
            print(f"  - {p}", file=sys.stderr)
    if secret_leaks:
        print("ERROR: Potential secret/credential patterns found:", file=sys.stderr)
        for leak in secret_leaks:
            print(f"  - {leak}", file=sys.stderr)

    if bad_paths or secret_leaks:
        return 1

    print(f"Privacy check passed: {len(tracked)} tracked files verified clean.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
