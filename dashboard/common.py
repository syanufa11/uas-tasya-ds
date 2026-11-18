"""Shared UI tokens, layout components, and synthetic demo helpers for Streamlit."""

from __future__ import annotations

import html
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from src.samsung_health.metrics import (  # noqa: E402
    synthetic_quality_checks,
    synthetic_sleep_data,
)

APP_NAME = "Samsung Health Sleep Analytics"
DEMO_LABEL = "🧪 DEMO SINTETIS — data acak buatan, BUKAN data Samsung Health asli"

PALETTE = {
    "navy": "#0B1120",
    "navy_surface": "#131C31",
    "indigo": "#4F46E5",
    "indigo_soft": "#818CF8",
    "cyan": "#06B6D4",
    "cyan_bright": "#22D3EE",
    "amber": "#F59E0B",
    "emerald": "#10B981",
    "rose": "#F43F5E",
}

_THEME_TOKENS = {
    "dark": {
        "bg": "#0B1120",
        "sidebar_bg": "#0F172A",
        "surface": "#131C31",
        "surface_alt": "#1A2540",
        "border": "#263354",
        "text": "#F1F5F9",
        "text_muted": "#94A3B8",
        "accent": "#6366F1",
        "accent_2": "#22D3EE",
        "banner_bg": "rgba(245, 158, 11, 0.12)",
        "banner_border": "rgba(245, 158, 11, 0.45)",
        "banner_text": "#FDE68A",
        "shadow": "0 8px 24px rgba(2, 6, 23, 0.35)",
    },
    "light": {
        "bg": "#F8FAFC",
        "sidebar_bg": "#EEF2FF",
        "surface": "#FFFFFF",
        "surface_alt": "#F1F5F9",
        "border": "#CBD5E1",
        "text": "#0F172A",
        "text_muted": "#475569",
        "accent": "#4F46E5",
        "accent_2": "#0891B2",
        "banner_bg": "#FFFBEB",
        "banner_border": "#F59E0B",
        "banner_text": "#92400E",
        "shadow": "0 4px 16px rgba(15, 23, 42, 0.08)",
    },
}


def build_theme_css(mode: str = "dark") -> str:
    """Build scoped CSS using Tailwind-inspired design tokens for light or dark mode."""
    t = _THEME_TOKENS.get(mode, _THEME_TOKENS["dark"])
    return f"""
<style>
:root {{
  --sh-navy: #0B1120;
  --sh-indigo: #4F46E5;
  --sh-cyan: #06B6D4;
  --sh-bg: {t['bg']};
  --sh-sidebar-bg: {t['sidebar_bg']};
  --sh-surface: {t['surface']};
  --sh-surface-alt: {t['surface_alt']};
  --sh-border: {t['border']};
  --sh-text: {t['text']};
  --sh-text-muted: {t['text_muted']};
  --sh-accent: {t['accent']};
  --sh-accent-2: {t['accent_2']};
  --sh-radius-md: 12px;
  --sh-radius-lg: 16px;
  --sh-shadow: {t['shadow']};
}}
.stApp {{
  background-color: var(--sh-bg);
  color: var(--sh-text);
}}
[data-testid="stSidebar"] {{
  background-color: var(--sh-sidebar-bg);
  border-right: 1px solid var(--sh-border);
}}
[data-testid="stSidebar"] * {{
  color: var(--sh-text);
}}
.block-container {{
  padding-top: 1.5rem;
  padding-bottom: 2.5rem;
  max-width: 1220px;
}}
.sh-hero {{
  background: linear-gradient(135deg, rgba(79,70,229,0.16), rgba(6,182,212,0.12));
  border: 1px solid var(--sh-border);
  border-radius: var(--sh-radius-lg);
  padding: 1.15rem 1.35rem;
  margin-bottom: 0.9rem;
  box-shadow: var(--sh-shadow);
}}
.sh-brand {{
  display: inline-block;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--sh-accent-2);
  margin-bottom: 0.25rem;
}}
.sh-hero-sub {{
  color: var(--sh-text-muted);
  font-size: 0.95rem;
  margin: 0.2rem 0 0 0;
  line-height: 1.45;
}}
.demo-banner {{
  background: {t['banner_bg']};
  border: 1px solid {t['banner_border']};
  color: {t['banner_text']};
  padding: 0.65rem 1rem;
  border-radius: var(--sh-radius-md);
  font-size: 0.88rem;
  font-weight: 600;
  margin-bottom: 1.15rem;
}}
.sh-kpi-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(195px, 1fr));
  gap: 0.85rem;
  margin: 0.5rem 0 1.25rem 0;
}}
.card {{
  background: var(--sh-surface);
  border: 1px solid var(--sh-border);
  border-top: 3px solid var(--sh-accent);
  border-radius: var(--sh-radius-md);
  padding: 1rem 1.15rem;
  box-shadow: var(--sh-shadow);
}}
.card .k {{
  color: var(--sh-text-muted);
  font-size: 0.76rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}}
.card .v {{
  font-size: 1.7rem;
  font-weight: 700;
  color: var(--sh-text);
  margin: 0.25rem 0 0.2rem 0;
  line-height: 1.2;
}}
.card .t {{
  color: var(--sh-accent-2);
  font-size: 0.72rem;
  font-weight: 600;
}}
.sh-section {{
  margin-top: 1.1rem;
  margin-bottom: 0.4rem;
}}
.sh-section h3 {{
  margin: 0;
  font-size: 1.12rem;
  font-weight: 700;
  color: var(--sh-text);
}}
.sh-section p {{
  margin: 0.15rem 0 0.5rem 0;
  font-size: 0.86rem;
  color: var(--sh-text-muted);
}}
.sh-panel {{
  background: var(--sh-surface);
  border: 1px solid var(--sh-border);
  border-radius: var(--sh-radius-md);
  padding: 1rem 1.15rem;
  margin-bottom: 0.9rem;
}}
.sh-panel h4 {{
  margin: 0 0 0.35rem 0;
  color: var(--sh-accent-2);
  font-size: 0.96rem;
}}
.sh-panel p, .sh-panel li {{
  color: var(--sh-text);
  font-size: 0.9rem;
  line-height: 1.5;
}}
@media (max-width: 768px) {{
  .block-container {{ padding-left: 1rem; padding-right: 1rem; }}
  .sh-kpi-grid {{ grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); }}
  .card .v {{ font-size: 1.4rem; }}
}}
</style>
"""


def _render_sidebar_controls() -> tuple[str, int]:
    """Render shared sidebar branding, theme toggle, demo window selector, and privacy note."""
    with st.sidebar:
        st.markdown(f"### 🌙 {APP_NAME}")
        st.caption("Modern Health Analytics · UAS Data Science S2")
        theme_choice = st.radio(
            "Mode Tampilan",
            options=["Dark (Navy)", "Light (Slate)"],
            index=0,
            key="ui_theme_mode",
            horizontal=True,
        )
        demo_days = st.select_slider(
            "Rentang Demo Sintetis (hari)",
            options=[30, 60, 90],
            value=60,
            key="demo_days_window",
        )
        st.divider()
        st.caption(
            "🔒 **Privasi Terjaga:** Mode publik hanya memakai generator acak deterministik "
            "(`seed=42`) tanpa data Samsung Health pribadi."
        )
    mode = "light" if theme_choice.startswith("Light") else "dark"
    return mode, int(demo_days)


def setup(title: str, subtitle: str = "") -> None:
    """Render shared page styles, sidebar controls, hero header, and synthetic demo banner."""
    mode, _ = _render_sidebar_controls()
    st.markdown(build_theme_css(mode), unsafe_allow_html=True)
    safe_sub = html.escape(subtitle)
    st.markdown(
        f'<div class="sh-hero"><div class="sh-brand">{APP_NAME}</div>'
        f'{f"<p class=sh-hero-sub>{safe_sub}</p>" if safe_sub else ""}</div>',
        unsafe_allow_html=True,
    )
    st.title(title)
    st.markdown(f'<div class="demo-banner">{DEMO_LABEL}</div>', unsafe_allow_html=True)


def active_demo_days() -> int:
    """Return currently selected synthetic demo window length."""
    return int(st.session_state.get("demo_days_window", 60))


def metric_cards(items: list[tuple[str, str] | tuple[str, str, str]]) -> None:
    """Render responsive KPI cards from (label, value) or (label, value, note) tuples."""
    if not items:
        return
    cards_html: list[str] = ['<div class="sh-kpi-grid">']
    for item in items:
        label = html.escape(str(item[0]))
        value = html.escape(str(item[1]))
        note = html.escape(str(item[2])) if len(item) > 2 else "DEMO SINTETIS"
        cards_html.append(
            f'<div class="card"><div class="k">{label}</div>'
            f'<div class="v">{value}</div><div class="t">{note}</div></div>'
        )
    cards_html.append("</div>")
    st.markdown("".join(cards_html), unsafe_allow_html=True)


def section_header(title: str, description: str = "") -> None:
    """Render a consistent section header with optional muted description."""
    safe_t = html.escape(title)
    safe_d = html.escape(description)
    st.markdown(
        f'<div class="sh-section"><h3>{safe_t}</h3>'
        f'{f"<p>{safe_d}</p>" if safe_d else ""}</div>',
        unsafe_allow_html=True,
    )


def empty_state(message: str = "Data tidak tersedia untuk filter yang dipilih.") -> None:
    """Render a consistent empty-state notice."""
    st.info(f"ℹ️ {message}")


@st.cache_data
def synthetic_sleep(days: int = 60, seed: int = 42) -> pd.DataFrame:
    """Cached wrapper around deterministic synthetic sleep demo data."""
    return synthetic_sleep_data(days=days, seed=seed)


@st.cache_data
def synthetic_quality() -> pd.DataFrame:
    """Cached wrapper around synthetic quality check table."""
    return synthetic_quality_checks()
