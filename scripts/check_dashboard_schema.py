"""Read-only, local-only eligibility check; print no health records or statistics."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.samsung_health.sleep import parse_samsung_csv  # noqa: E402

ACTIVITY_COLUMNS = ["step_count", "active_time", "walk_time", "run_time", "distance"]


def main() -> None:
    roots = list(Path(__file__).resolve().parents[1].glob("samsunghealth_*"))
    if len(roots) != 1:
        raise ValueError("Diperlukan tepat satu ekspor lokal untuk verifikasi data asli.")
    files = list(roots[0].glob("com.samsung.shealth.activity.day_summary.*.csv"))
    if len(files) != 1:
        raise ValueError("Diperlukan tepat satu sumber aktivitas harian.")
    import pandas as pd

    _, records, meta = parse_samsung_csv(files[0].read_text(encoding="utf-8-sig"))
    if meta["status"] != "ok" or meta["duplicate_header_names"]:
        raise ValueError("Struktur CSV sumber tidak valid.")
    activity = pd.DataFrame(records).replace("", pd.NA)
    usable = [
        column
        for column in ACTIVITY_COLUMNS
        if column in activity and activity[column].notna().any()
    ]
    if len(usable) < 5:
        raise ValueError("Dataset asli belum memenuhi minimal lima kolom nonkosong.")
    print("PASS: lima kolom sumber aktivitas tersedia dan nonkosong pada ekspor lokal.")
    print("Hanya kelayakan skema; bukan bukti kualitas, alignment, atau hasil penelitian.")


if __name__ == "__main__":
    main()
