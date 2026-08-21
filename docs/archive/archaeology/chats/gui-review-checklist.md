# GUI review checklist (GUI-X6 antipatterns)

Review guardrail for every GUI-* PR -- NOT a screen. Derived from the reference
antipatterns (ref §13). Cite this file in GUI-* reckon prompts; a reviewer walks
the seven and blocks any diff that trips one. Each line names the smell and the
one thing to look for.

- [ ] **One chat per worker** -- a per-worker chat log is diagnostic ONLY, never the
  primary surface. Look for: worker detail defaulting to a raw transcript instead of
  Outcome-first progressive disclosure (GUI-X1).

- [ ] **Graph for everything** -- a DAG/graph belongs to genuine topology, not to a
  fallback chain, a queue, or a table. Look for: a force-directed graph where a
  sorted list or a DataTable would read faster.

- [ ] **Card soup** -- every datum wrapped in its own bordered card. Look for: a wall
  of equal-weight cards with no hierarchy; prefer a dense table/list and reserve
  cards for the ONE signature moment per domain (D028).

- [ ] **Color per agent** -- a distinct hue assigned to each agent/vendor/worker.
  Look for: color used as identity rather than as status. Color is semantic
  (GUI-F4 status tones) + always paired with icon + text; never a vendor palette.

- [ ] **Real-time excess** -- everything live-polling/streaming/animating at once.
  Look for: motion or sub-second refresh where a single snapshot (or an on-demand
  refresh) is enough; live motion earns its place, it is not the default.

- [ ] **Telemetry as conclusion** -- a raw metric presented as a verdict. Look for: a
  number/chart framed as an answer with no honest "-" for gaps; evidence is marked
  technical (GUI-X5 evidence badge), never dressed up as a conclusion.

- [ ] **JSON as the only interface** -- a raw JSON blob standing in for a real view.
  Look for: `<pre>{JSON.stringify(...)}</pre>` as the actual UI; typed fields,
  honest "-" for missing data, and a proper primitive instead.

## Related patterns

- GUI-X1 progressive disclosure -- Outcome -> Plan -> Topology -> Evidence.
- GUI-X4 typed inspector -- the right panel swaps by object type.
- GUI-X5 action semantics -- command/proposal/approval/execution/receipt/evidence/promotion.
- Design law: `docs/DESIGN_SYSTEM.md` (SIGNAL, D026/D028) -- tokens only, compose F5/F4.
