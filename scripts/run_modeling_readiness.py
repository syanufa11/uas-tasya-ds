"""Run TASK 16 private EDA only; intentionally never train candidate data."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.modeling.eda import write_diagnostics  # noqa: E402

if __name__ == "__main__":
    write_diagnostics(
        ROOT / "data_processed/samsung_health_merged.csv",
        ROOT / "artifacts/task16",
        ROOT / "reports/model_evaluation.md",
    )
    print("Private EDA saved locally. BLOCKED: no model fitted; see private report.")
