"""Synthetic-only safety, temporal boundaries and untrained model specifications."""

import sys
from pathlib import Path

import pandas as pd
import pytest

from src.modeling.models import model_specs
from src.modeling.readiness import audit_candidate, load_candidate, require_ready


@pytest.fixture
def candidate(tmp_path):
    """Synthetic data deliberately crossing Jakarta midnight; not research results."""
    path = tmp_path / "synthetic.csv"
    pd.DataFrame({
        "date": ["01/01/2026", "02/01/2026", "03/01/2026"],
        "sleep_start_local": [
            "2026-01-01T01:00:00+07:00", "2026-01-02T23:00:00+07:00", None,
        ],
        "sleep_end_local": [
            "2026-01-01T08:00:00+07:00", "2026-01-03T06:00:00+07:00", None,
        ],
        "sleep_duration_minutes": [420, 420, None],
        "step_count": [1000, 2000, 3000], "active_time_minutes": [10, 20, 30],
        "day_of_week": [3, 4, 5], "is_weekend": [0, 0, 1],
    }).to_csv(path, index=False)
    return path


def test_readiness_fails_closed_even_with_complete_measurements(candidate):
    audit = audit_candidate(load_candidate(candidate))
    assert audit["status"] == "BLOCKED"
    assert audit["effective_training_samples"] == 0
    assert any("Tanggal bangun" in reason for reason in audit["blockers"])
    with pytest.raises(ValueError, match="Training disabled"):
        require_ready(audit)


def test_retrospective_lookup_uses_utc_start_not_wake_date(candidate):
    from src.modeling.readiness import retrospective_pairs

    frame = load_candidate(candidate)
    pairs = retrospective_pairs(frame)
    assert pairs.activity_date.iloc[0] == pd.Timestamp("2025-12-30")
    assert pd.isna(pairs.step_count.iloc[0])  # Missing date is never shifted/backfilled.
    assert pairs.step_count.iloc[1] == 1000
    assert (pairs.activity_end_candidate <= pairs.sleep_start_local).all()


def test_naive_timestamps_rejected(candidate):
    frame = pd.read_csv(candidate)
    frame["sleep_start_local"] = frame.sleep_start_local.str.replace("+07:00", "", regex=False)
    frame.to_csv(candidate, index=False)
    with pytest.raises(ValueError, match="explicitly use"):
        load_candidate(candidate)


def test_iso_timestamp_fractional_seconds_are_supported(candidate):
    frame = pd.read_csv(candidate)
    frame.loc[1, "sleep_start_local"] = "2026-01-02T23:00:00.580000+07:00"
    frame.to_csv(candidate, index=False)
    parsed = load_candidate(candidate)
    assert parsed.sleep_start_local.iloc[1].microsecond == 580000


def test_models_have_no_fitted_state_and_preprocessing_is_in_pipeline():
    specs = model_specs()
    assert set(specs) == {"DummyRegressor", "LinearRegression", "RandomForestRegressor"}
    for pipeline in specs.values():
        assert "imputer" in pipeline.named_steps
        assert not hasattr(pipeline.named_steps["imputer"], "statistics_")
    assert "scaler" in specs["LinearRegression"].named_steps


def test_public_model_page_has_no_private_imports_or_fake_metrics():
    from streamlit.testing.v1 import AppTest

    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / "dashboard"))
    at = AppTest.from_string("from views.model_evaluation import render\nrender()")
    at.run(timeout=30)
    assert not at.exception
    assert len(at.table) == 1
    assert "Belum tersedia" in at.table[0].value.to_string()
    assert not at.get("plotly_chart")


def test_private_model_report_forbidden_in_git():
    from scripts.check_privacy import find_forbidden_paths

    assert find_forbidden_paths(["reports/model_evaluation.md"])


def test_public_notebook_has_unique_cells_and_no_outputs():
    import nbformat

    root = Path(__file__).resolve().parents[1]
    notebook = nbformat.read(root / "notebooks/16_samsung_health_modeling.ipynb", as_version=4)
    nbformat.validate(notebook)
    assert len({cell.id for cell in notebook.cells}) == len(notebook.cells)
    for cell in notebook.cells:
        if cell.cell_type == "code":
            assert cell.execution_count is None
            assert not cell.outputs
            compile(cell.source, "notebook", "exec")
