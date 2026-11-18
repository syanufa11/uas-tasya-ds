"""Shared UI tokens, layout components, and synthetic demo helpers for Streamlit."""

from __future__ import annotations

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
  --sh-bg: {t["bg"]};
  --sh-sidebar-bg: {t["sidebar_bg"]};
  --sh-surface: {t["surface"]};
  --sh-surface-alt: {t["surface_alt"]};
  --sh-border: {t["border"]};
  --sh-text: {t["text"]};
  --sh-text-muted: {t["text_muted"]};
  --sh-accent: {t["accent"]};
  --sh-accent-2: {t["accent_2"]};
  --sh-radius-md: 12px;
  --sh-radius-lg: 16px;
  --sh-shadow: {t["shadow"]};
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
  background: var(--sh-surface);
  border: 1px solid var(--sh-border);
  color: var(--sh-text);
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
  .sh-kpi-grid {{ grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); }}
  .card .v {{ font-size: 1.4rem; }}
}}
</style>
"""


def setup(title: str, subtitle: str = "") -> None:
    """Render shared page heading and explicit public demo provenance."""
    st.caption("SAMSUNG HEALTH / ANALYTICS WORKSPACE")
    st.title(title)
    if subtitle:
        st.caption(subtitle)
    st.info(DEMO_LABEL)


def sidebar_controls() -> None:
    """Entrypoint controls persist across all pages via Streamlit's common frame."""
    with st.sidebar:
        st.caption("RESEARCH WORKSPACE · UAS DATA SCIENCE")
        st.subheader("Health insights", anchor=False)
        st.caption("Demo publik · 90 hari fiktif pada tahun 2000")
        st.select_slider(
            "Rentang Demo Sintetis (hari)", [30, 60, 90], value=60, key="demo_days_window"
        )
        st.date_input(
            "Periode analisis",
            value=(pd.Timestamp("2000-01-01").date(), pd.Timestamp("2000-03-30").date()),
            min_value=pd.Timestamp("2000-01-01").date(),
            max_value=pd.Timestamp("2000-03-30").date(),
            key="analysis_period",
        )
        st.selectbox("Jenis hari", ["Semua", "Hari kerja", "Akhir pekan"], key="day_type")
        st.caption("Jendela hari dihitung mundur dari akhir periode yang dipilih.")
        st.divider()
        st.caption("Tampilan terang/gelap: menu ⋮ → Settings → Appearance.")
        st.caption("Privasi: hanya generator sintetis. Tidak memuat ekspor pribadi.")


@st.cache_data
def public_dataset() -> pd.DataFrame:
    from src.samsung_health.dashboard_data import demo_dataset

    return demo_dataset()


def analysis_data() -> pd.DataFrame:
    """Load, validate, and filter the same public series for every analytic page."""
    from src.samsung_health.dashboard_data import filter_period, validate_dataset

    try:
        with st.spinner("Menyiapkan data demo…"):
            frame = public_dataset()
            validate_dataset(frame)
        period = st.session_state.get("analysis_period", (frame.date.min(), frame.date.max()))
        if len(period) != 2:
            st.info("Lengkapi tanggal awal dan akhir periode.")
            return frame.iloc[:0]
        start, end = map(pd.Timestamp, period)
        if start > end:
            st.error("Tanggal awal harus mendahului tanggal akhir.")
            return frame.iloc[:0]
        start = max(start, end - pd.Timedelta(days=active_demo_days() - 1))
        result = filter_period(frame, start, end, st.session_state.get("day_type", "Semua"))
        st.caption(
            f"Periode aktif: {start:%d %b %Y} – {end:%d %b %Y} · {len(result)} observasi sintetis"
        )
        return result
    except (ValueError, KeyError, TypeError, OSError):
        st.error("Data demo gagal dimuat atau skemanya tidak valid. Muat ulang halaman.")
        return pd.DataFrame()


def active_demo_days() -> int:
    """Return currently selected synthetic demo window length."""
    return int(st.session_state.get("demo_days_window", 60))


def metric_cards(items: list[tuple[str, str] | tuple[str, str, str]]) -> None:
    """Responsive native cards follow the selected theme, including on first load."""
    with st.container(horizontal=True):
        for item in items:
            with st.container(width=220, border=True):
                st.metric(str(item[0]), str(item[1]))
                st.caption(str(item[2]) if len(item) > 2 else "DEMO SINTETIS")


def section_header(title: str, description: str = "") -> None:
    """Render a consistent section header with optional muted description."""
    st.subheader(title, anchor=False)
    if description:
        st.caption(description)


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
