"""Meaningful public-demo regression checks, independent of private data."""

import sys
from pathlib import Path

import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

from src.samsung_health.dashboard_data import (
    association,
    demo_dataset,
    filter_period,
    quality_checks,
    validate_dataset,
)

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "dashboard"))


def test_stable_filters_and_schema():
    frame = demo_dataset()
    validate_dataset(frame)
    selected = filter_period(frame, "2000-01-05", "2000-01-20", "Akhir pekan")
    assert not selected.empty
    assert selected.date.between("2000-01-05", "2000-01-20").all()
    assert selected.is_weekend.all()
    pd.testing.assert_frame_equal(selected, frame.loc[selected.index])
    with pytest.raises(ValueError):
        validate_dataset(frame.drop(columns="active_min"))


def test_quality_is_computed_and_correlation_handles_insufficient_data():
    frame = demo_dataset()
    assert quality_checks(frame).Temuan.sum() == 0
    frame.loc[0, "duration_h"] = float("nan")
    frame.loc[1, "step_count"] = -1
    assert quality_checks(frame).Temuan.sum() == 2
    assert association(frame.iloc[:2], "step_count")[1] is None
    constant = frame.assign(step_count=1)
    assert association(constant, "step_count")[1] is None
    linear = pd.DataFrame({"step_count": [1, 2, 3], "duration_h": [2, 4, 6]})
    assert association(linear, "step_count") == (3, 1.0)


@pytest.mark.parametrize(
    "page", ["overview", "sleep", "activity", "relationship", "quality", "methodology"]
)
def test_all_pages_and_shared_filters(page):
    source = (
        "from common import sidebar_controls\n"
        f"from views import {page}\nsidebar_controls()\n{page}.render()"
    )
    at = AppTest.from_string(source).run(timeout=30)
    assert not at.exception
    at.select_slider[0].set_value(30).run()
    at.selectbox(key="day_type").select("Akhir pekan").run()
    assert not at.exception
    if page == "sleep":
        at.segmented_control[0].set_value("Konsistensi").run()
        assert not at.exception
    if page in ("activity", "relationship"):
        at.selectbox(key=f"{page}_metric").select("Menit aktif").run()
        assert not at.exception


def test_empty_incomplete_and_error_states():
    source = "from common import sidebar_controls\nfrom views import overview\n"
    at = AppTest.from_string(source + "sidebar_controls()\noverview.render()")
    at.run()
    at.date_input[0].set_value((pd.Timestamp("2000-01-03").date(),)).run()
    assert not at.exception
    assert any("Lengkapi" in item.value for item in at.info)
    at.date_input[0].set_value((pd.Timestamp("2000-01-03").date(),) * 2)
    at.selectbox(key="day_type").select("Akhir pekan").run()
    assert not at.exception
    assert any("kosong" in item.value for item in at.info)
    broken = AppTest.from_string(
        "import common\nimport pandas as pd\n"
        "original = common.public_dataset\n"
        "try:\n"
        "    common.public_dataset = lambda: pd.DataFrame({'bad': [1]})\n"
        "    common.analysis_data()\n"
        "finally:\n"
        "    common.public_dataset = original\n"
    ).run()
    assert not broken.exception
    assert broken.error
