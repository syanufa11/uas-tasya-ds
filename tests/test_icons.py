"""Local SVG safety and semantic navigation checks; no private datasets."""

import base64
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "dashboard"))

import icons  # noqa: E402


@pytest.mark.parametrize("name", sorted(icons.ICONS))
def test_local_svg_geometry_and_accessibility(name):
    root = ET.fromstring(icons.svg(name, 21))
    assert root.get("viewBox") == "0 0 24 24"
    assert root.get("stroke-width") == "2"
    assert root.get("width") == root.get("height") == "21"
    assert root.get("stroke") == "currentColor"
    assert root.get("aria-hidden") == "true"
    assert root.get("focusable") == "false"


def test_escaped_accessible_label_and_embedded_favicon():
    label = '<img onerror="test">'
    root = ET.fromstring(icons.svg("moon", label=label))
    assert root.get("aria-label") == label
    assert root.get("role") == "img"
    assert "<img" not in icons.svg("moon", label=label)
    encoded = icons.data_uri("moon", favicon=True).split(",", 1)[1]
    root = ET.fromstring(base64.b64decode(encoded))
    assert root.get("stroke") == "#6366F1"


@pytest.mark.parametrize("name", ["../moon", "https://example.com/icon.svg", "<script>"])
def test_unknown_or_external_assets_rejected(name):
    with pytest.raises(ValueError, match="Unknown"):
        icons.svg(name)


def test_bad_size_and_css_target_rejected():
    with pytest.raises(ValueError):
        icons.svg("moon", 100)
    with pytest.raises(ValueError):
        icons.leading_icon("key}script", "a", "moon")


def test_no_decorative_emoji_or_external_icon_dependencies():
    emoji = re.compile("[\U0001f000-\U0001faff\u2600-\u27bf\u2139\ufe0f]")
    for path in (ROOT / "dashboard").rglob("*.py"):
        assert not emoji.search(path.read_text(encoding="utf-8")), path.name
    assert set(icons.PAGE_ICONS.values()) <= icons.ICONS
    assert len(icons.PAGE_ICONS) == 6


def test_native_navigation_keeps_text_and_disables_emoji_icons():
    from streamlit.testing.v1 import AppTest

    at = AppTest.from_file(str(ROOT / "dashboard" / "app.py")).run(timeout=30)
    assert not at.exception
    links = at.get("page_link")
    assert [link.proto.label for link in links] == list(icons.PAGE_ICONS)
    assert all(not link.proto.icon for link in links)
