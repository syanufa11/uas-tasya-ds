# Project design contract

- Framework: Streamlit, Python 3.11+, Plotly for interactive overview/activity/
  relationship charts; existing Altair sleep charts remain intact.
- Destinations: Overview; Sleep Analytics (patterns and consistency);
  Physical Activity; Sleep & Activity Relationship; Data Quality; Methodology.
- Navigation: native collapsible sidebar, visible active page, descriptive labels.
- Common controls: selected date interval, trailing 30/60/90-day window ending at
  its upper bound, then weekday/weekend selection. Use one fixed 90-day demo.
- Appearance: native dual themes synchronize widgets, tables, and chart colors.
  Navy surfaces, indigo accents, cyan secondary series, neutral text. Reuse small
  native metric cards and containers; avoid styling Streamlit's private selectors.
- Content hierarchy: workspace caption, page title, context, synthetic provenance,
  active period, KPIs, chart panels, analysis tables, limitations.
- Chart interaction: hover, zoom, legend selection; readable axis units, wrapped
  horizontal legends, responsive width, and accessible descriptions.
- States: spinner during preparation, informative empty/incomplete date selection,
  safe error message for schema/load failure; suppress derived metrics when empty.
- Demo columns: date, duration_h, bed_hour, wake_hour, step_count, active_min.
  No score, stage, or efficiency claims. Same-day demo correlations illustrate
  an interface, not the temporal alignment or conclusions of the research.
- Actual research data: verify at least five nonempty usable source columns locally;
  use the prior UTC/overlap verification before interpreting activity-sleep pairs.
