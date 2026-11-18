"""Unit and smoke tests for the Streamlit dashboard (synthetic demo mode)."""

import sys
import tomllib
from pathlib import Path

import pandas as pd
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "dashboard") not in sys.path:
    sys.path.insert(0, str(ROOT / "dashboard"))

import common  # noqa: E402


def test_streamlit_configs_are_valid_toml() -> None:
    """Verify root and dashboard Streamlit configs parse cleanly."""
    for rel_path in (".streamlit/config.toml", "dashboard/.streamlit/config.toml"):
        cfg_path = ROOT / rel_path
        assert cfg_path.is_file(), f"Missing config: {rel_path}"
        parsed = tomllib.loads(cfg_path.read_text(encoding="utf-8"))
        assert "theme" in parsed


def test_requirements_files_include_core_dependencies() -> None:
    """Verify root and dashboard requirements include required packages."""
    for rel_path in ("requirements.txt", "dashboard/requirements.txt"):
        req_path = ROOT / rel_path
        assert req_path.is_file(), f"Missing requirements file: {rel_path}"
        content = req_path.read_text(encoding="utf-8").lower()
        for pkg in ("streamlit", "pandas", "numpy", "altair"):
            assert pkg in content, f"{pkg} missing in {rel_path}"


def test_synthetic_sleep_is_deterministic_and_labeled_demo() -> None:
    """Verify synthetic_sleep produces reproducible, bounded synthetic data."""
    assert "SINTETIS" in common.DEMO_LABEL.upper()
    assert "BUKAN" in common.DEMO_LABEL.upper()

    df1 = common.synthetic_sleep(days=30, seed=42)
    df2 = common.synthetic_sleep(days=30, seed=42)
    pd.testing.assert_frame_equal(df1, df2)

    expected_cols = {
        "date",
        "bed_hour",
        "duration_h",
        "wake_hour",
        "deep_pct",
        "rem_pct",
        "light_pct",
        "weekday",
        "is_weekend",
    }
    assert expected_cols.issubset(df1.columns)
    assert len(df1) == 30
    assert (df1["duration_h"] >= 3.5).all() and (df1["duration_h"] <= 10.0).all()
    stage_sum = df1["deep_pct"] + df1["rem_pct"] + df1["light_pct"]
    assert (stage_sum - 100.0).abs().max() < 1e-6


def test_synthetic_quality_structure() -> None:
    """Verify synthetic_quality returns expected schema."""
    df = common.synthetic_quality()
    assert list(df.columns) == ["Check", "Status", "Demo count"]
    assert len(df) == 5


def test_theme_css_supports_dark_and_light_modes() -> None:
    """Verify design tokens and responsive rules are present for both dark and light modes."""
    dark_css = common.build_theme_css("dark")
    light_css = common.build_theme_css("light")
    for css in (dark_css, light_css):
        assert "--sh-navy:" in css
        assert "--sh-indigo:" in css
        assert "--sh-cyan:" in css
        assert "@media (max-width: 768px)" in css
    assert "#0B1120" in dark_css
    # Native Streamlit themes own widget/card colors; the legacy CSS helper is retained.
    assert "#F8FAFC" in light_css
    config = tomllib.loads((ROOT / ".streamlit/config.toml").read_text(encoding="utf-8"))
    assert config["theme"]["light"]["backgroundColor"] == "#F8FAFC"
    assert config["theme"]["dark"]["backgroundColor"] == "#0B1120"


def test_tailwind_skill_structure_present() -> None:
    """Verify tailwind-4-docs skill is installed with required metadata and references."""
    skill_dir = ROOT / ".github" / "skills" / "tailwind-4-docs"
    assert (skill_dir / "SKILL.md").is_file()
    assert (skill_dir / "LICENSE.md").is_file()
    assert (skill_dir / "references" / "engineering-playbook.md").is_file()
    assert (skill_dir / "references" / "gotchas.md").is_file()
    assert (skill_dir / "scripts" / "sync_tailwind_docs.py").is_file()


def test_dashboard_app_runs_without_private_data() -> None:
    """Smoke test that dashboard/app.py renders without exceptions in demo mode."""
    app_path = ROOT / "dashboard" / "app.py"
    at = AppTest.from_file(str(app_path))
    at.run(timeout=30)
    assert not at.exception, f"App raised exception: {at.exception}"
    assert len(at.title) >= 1
