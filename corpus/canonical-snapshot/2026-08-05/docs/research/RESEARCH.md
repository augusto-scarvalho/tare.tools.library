# Research rounds

One evidence-driven Double Diamond study per file: `docs/research/<slug>.md`.

The method, commands, budgets, and sources are canonical in the playbook
[`.harness/prompts/research-playbook.md`](../../.harness/prompts/research-playbook.md)
— this folder only holds the per-round output.

Each `<slug>.md` follows the playbook's phase order: **question + success criteria +
declared budget** (Phase 0) → **evidence matrix** (Phase 1) → **briefs + human gate**
(Phase 2) → **divergence reduce** (Phase 3) → **concept cards + operations** (Phase 4)
→ **portfolio + decisions + traceability matrix** (Phase 5). Decisions land in
`.harness/context/DECISIONS.md`; tasks via `workflow promote`. No hand-written ledgers.
