---
name: build-admin-panel
description: Design and refine the existing Samsung Health analytics dashboard with scoped research, reusable UI, accessible states, and browser verification. Use for analytics dashboard redesign or admin-style navigation, not authentication or CRUD systems.
---

# Analytics dashboard delivery

This is an original project skill, not a copy of third-party instructions.
Read [references/project-design.md](references/project-design.md) for the UI/data
contract and [references/attribution.md](references/attribution.md) for provenance.

1. **Research:** inspect the entrypoint, requirements, views, analysis modules,
   existing skills, working tree, and privacy rules. Verify a reference's license
   before incorporating its text or code. Keep local audit records private.
2. **Scope:** retain Streamlit and the established analysis pipeline. The public
   dashboard uses deterministic synthetic data. Do not add auth, CRUD, roles,
   an API, or a new frontend unless requested. Reuse `tailwind-4-docs` if a real
   Tailwind build is in scope; never install a duplicate or use a production CDN.
3. **Design:** define navigation, period filters, units, token palette, light/dark
   appearance, mobile layout, and loading/empty/error behavior before editing.
   Preserve existing analyses when consolidating pages.
4. **Build:** keep pure analysis in `src/samsung_health/` and presentation in
   `dashboard/`. Share filters in the entrypoint so they survive navigation.
   Validate the active dataset contract; missing columns must produce a clear
   state, never fabricated values. Label demo charts and tables as synthetic.
5. **Browser verification:** run Ruff, pytest, configuration checks, and the
   privacy guard. In a real browser visit all six pages, exercise date/day/window
   and metric filters, both sleep analyses, light/dark appearance, and mobile
   sidebar. Inspect screenshots, runtime/console errors, and failed requests.
   AppTest and HTTP health checks alone do not prove responsive browser behavior.
6. **Deploy:** use the existing Actions and Streamlit hosting. Commit/push only
   within the current user's authorization; exclude pre-existing unrelated edits.
   Inspect the deployed revision and live UI separately from CI. Report any
   unavailable access or incomplete verification plainly.

For dataset eligibility, run the local-only `scripts/check_dashboard_schema.py`;
the synthetic schema does not prove eligibility of the research dataset.
Never infer causation from correlation or publish individual health observations.
