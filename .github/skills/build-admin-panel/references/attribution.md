# Provenance and reuse decision

Reviewed 2026-11-18:

- [Owais232/Admin-Panel-Skill-LLM-Models](https://github.com/Owais232/Admin-Panel-Skill-LLM-Models),
  `skill/build-admin-panel/SKILL.md`, `references/research-and-scope.md`, and
  `references/build-and-verify.md`. No explicit reuse license was established from
  the repository listing or a root LICENSE request. Public visibility alone does
  not establish permission. No upstream text, reference file, script, or asset is
  vendored. This local skill is independently written for the analytics project;
  only general research/design/build/verification principles inform its workflow.
- [Lombiq/Tailwind-Agent-Skills](https://github.com/Lombiq/Tailwind-Agent-Skills):
  existing TASK 09 installation remains the sole `tailwind-4-docs` skill. Its
  BSD-3-Clause notice is retained in the sibling skill's `LICENSE.md`.
  The Tailwind documentation snapshot has separate source terms;
  no snapshot or license acceptance is introduced by this task.

The original upstream admin references address auth, entities, writes, and APIs.
Those dependencies are outside this read-only analytics dashboard's scope. The
local skill requires no Node.js package, backend service, or paid provider.
