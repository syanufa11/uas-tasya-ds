"""Pinned local Lucide SVGs for Streamlit; no remote assets or user-supplied SVG."""

from __future__ import annotations

import base64
import re
import xml.etree.ElementTree as ET
from functools import lru_cache
from html import escape
from pathlib import Path

import streamlit as st

ASSETS = Path(__file__).parent / "assets" / "icons"
ICONS = frozenset({
    "layout-dashboard", "moon", "footprints", "chart-no-axes-combined", "shield-check",
    "book-open", "calendar-days", "settings", "sliders-horizontal", "download", "clock",
    "sunrise", "flask-conical", "info",
})
PAGE_ICONS = {
    "Overview": "layout-dashboard", "Sleep Analytics": "moon", "Physical Activity": "footprints",
    "Sleep & Activity Relationship": "chart-no-axes-combined", "Data Quality": "shield-check",
    "Methodology": "book-open",
}
_TAGS = {"svg", "path", "rect", "circle", "ellipse", "line", "polyline", "polygon"}
_ATTRS = {
    "width", "height", "viewBox", "fill", "stroke", "stroke-width", "stroke-linecap",
    "stroke-linejoin", "d", "x", "y", "x1", "x2", "y1", "y2", "cx", "cy", "r",
    "rx", "ry", "points",
}


@lru_cache(maxsize=len(ICONS))
def _asset(name: str) -> str:
    if name not in ICONS:
        raise ValueError("Unknown local Lucide icon")
    source = (ASSETS / f"{name}.svg").read_text(encoding="utf-8")
    root = ET.fromstring(source)
    if root.tag != "{http://www.w3.org/2000/svg}svg":
        raise ValueError("Invalid SVG root")
    for element in root.iter():
        if element.tag.split("}")[-1] not in _TAGS or not set(element.attrib) <= _ATTRS:
            raise ValueError("Unsupported SVG element or attribute")
        for value in element.attrib.values():
            if re.search(r"url\s*\(|javascript:|https?:|data:", value, flags=re.I):
                raise ValueError("External or executable SVG content")
    if root.get("viewBox") != "0 0 24 24" or root.get("stroke-width") != "2":
        raise ValueError("Inconsistent Lucide geometry")
    return source


def svg(name: str, size: int = 22, label: str | None = None) -> str:
    """Return validated inline SVG; decorative unless an accessible name is supplied."""
    if size not in (16, 18, 20, 21, 22, 24):
        raise ValueError("Unsupported icon size")
    source = _asset(name).replace('width="24"', f'width="{size}"', 1)
    source = source.replace('height="24"', f'height="{size}"', 1)
    accessibility = ('aria-hidden="true"' if label is None else
                     f'role="img" aria-label="{escape(label, quote=True)}"')
    return source.replace("<svg", f'<svg focusable="false" {accessibility}', 1)


def data_uri(name: str, *, favicon: bool = False) -> str:
    """Return an embedded SVG; mask geometry uses fixed black, favicon uses indigo."""
    source = _asset(name).replace("currentColor", "#6366F1" if favicon else "#000000")
    return "data:image/svg+xml;base64," + base64.b64encode(source.encode()).decode("ascii")


def leading_icon(key: str, selector: str, name: str, size: int = 21) -> None:
    """Decorate native text via a theme-inheriting mask, scoped to a public widget key."""
    if not re.fullmatch(r"[a-z0-9_]+", key) or selector not in {"a", "h1", "h3", "p"}:
        raise ValueError("Invalid icon target")
    if size not in (18, 20, 21, 22, 24):
        raise ValueError("Unsupported icon size")
    uri = data_uri(name)
    st.html(f"""<style>
    .st-key-{key} {selector}::before {{
        content: ""; display: inline-block; width: {size}px; height: {size}px;
        flex: 0 0 {size}px; margin-right: 0.55rem; vertical-align: -0.15em;
        background-color: currentColor;
        mask: url("{uri}") center / contain no-repeat;
        -webkit-mask: url("{uri}") center / contain no-repeat;
    }}
    </style>""")


def icon_caption(text: str, name: str, key: str) -> None:
    """Add an 18px icon to native caption text, retaining its accessible label."""
    leading_icon(key, "p", name, 18)
    with st.container(key=key):
        st.caption(text)


def metric_icon(label: str) -> str:
    """Choose semantic KPI decoration without changing the metric itself."""
    text = label.casefold()
    if "langkah" in text:
        return "footprints"
    if "bangun" in text:
        return "sunrise"
    if any(word in text for word in ("durasi", "jam", "aktif")):
        return "clock"
    if any(word in text for word in ("malam", "hari", "observasi", "pasangan")):
        return "calendar-days"
    if any(word in text for word in ("kolom", "temuan")):
        return "shield-check"
    return "chart-no-axes-combined"
