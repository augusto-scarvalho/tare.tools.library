# Research — a standard structured format for experiment results (owner-ratified)

Round 2026-07-21. Question: experiment results are saved as ONE FREE-TEXT `value` string
(e.g. `"divergenceFraction=0.054 (24/444 cross-tier refs); ... Residual ~2-3%"`) — which
can't be tabulated, compared, or plotted (the numeric compare view was literally blocked).
What STRUCTURED format do we adopt, backward-compatible, minimal, fitting the
measure-before-control archetype (a shadow probe measuring an effect vs a noise floor,
evidence-graded, verdict ship/shelve)?

Ideators: 2× Sonnet 5 high (schema + display) + 4× external (GLM-5.2 ×2, Gemini ×2), each
in SCHEMA and SURVEY perspectives. Discover: MLflow / W&B are key-value+step; the exact
field schemas live in each tool's API docs (web).

## Convergence (6 ideadores, 3 vendors — near-total)

1. **Additive structured field beside the untouched free-text `value`.** Old record =
   no structured field = still valid → **zero forced migration** (optional lazy backfill,
   marked `source: backfilled`, never chase 100%).
2. **Borrow FIELD NAMES, reject the CONTAINERS.** OTel metrics (`metric`/`value`/`unit`/
   attributes) for the base shape + MLflow (`step`/`timestamp`) + tidy-data (one row per
   observation). REJECT the machinery: wandb live server/dict, OTel SDK/exporters, MLflow
   tracking-server/run-hierarchy, Frictionless data-package descriptor, Braintrust/LangSmith
   per-example eval rows (wrong grain — ours is one aggregate stat with a verdict).
3. **Archetype fields no standard carries:** `n`, `ci` (+ `ciMethod`), `noiseFloor`,
   `verdict`, `grade`, `artifact`, `variant` (baseline|candidate).
4. **Measure-honesty:** an absent field renders `—`; NEVER regex-parse a number out of the
   prose into a numeric cell (a post-hoc extracted number is a fabrication by another name).
   The raw `value` string always stays as the human-readable note.
5. **stdlib JSON, no validator file** — `json.loads` + a duck-typed `"metric" in m and
   "value" in m` check is enough; a schema nobody else writes is scaffolding.

## The one divergence — tidy OBJECT vs ARRAY (owner decided: ARRAY)

- Object (`measurement: {...}`, one metric/record): the archetype grades ONE effect; a 2nd
  independent metric is another EXP. More minimal.
- **Array (`metrics: [...]`): owner-ratified 2026-07-21.** A record often has sub-metrics
  (EXP-22: divergenceFraction + doc→code + code→doc); the array holds them without forcing
  another EXP. 4/6 ideadores chose it.
- UNANIMOUS reject: the nested map-by-name (`{divergenceFraction: {...}}`) — breaks tidy-data
  cross-record comparison.

## Ratified schema (SHIPPED — additive `metrics[]` on each measurement)

```json
{ "at": "…", "value": "<free text, authoritative note>", "note": "…",
  "metrics": [ { "metric": "divergenceFraction", "value": 0.054, "unit": "fraction",
                 "n": 444, "ci": [lo, hi], "ciMethod": "anytime-valid",
                 "noiseFloor": 0.03, "step": null, "artifact": "…json",
                 "variant": "baseline|candidate", "source": "authored|backfilled" } ] }
```
`metric` + `value` (finite number) required; everything else optional; a valueless entry is
DROPPED (`_clean_metric` in experiment_registry.py). CLI: `experiment record EXP-N "text"
--measure NAME --value N [--unit --n --ci-lo --ci-hi --ci-method --noise-floor --artifact
--variant]`.

## Display (what structure UNLOCKS that prose can't)

- **Results TABLE** (shipped): Metric | Value | Unit | n | CI | Noise floor. Legacy
  free-text-only records contribute no rows.
- **Sparkline + CI-vs-noise-floor** (deferred until data lands): x=step/order, y=value,
  shaded band = noiseFloor, CI whiskers per point; ship moment = the CI fully clears the
  band. Honest gap for records without structure.
- **baseline↔candidate delta** (the blocked compare, deferred): pick `variant:baseline`
  vs `variant:candidate`, `delta = cand − base`, propagate CI, color by clearing the floor.
- Honest ceiling: the fancy viz needs `ci`+`noiseFloor`+a series — which experiments don't
  carry yet. Built the TABLE now; the viz activates as structured records accumulate. Never
  fabricate a series (measure-honesty).

## Flagged for revisit (schema Sonnet)

`ci: [lo,hi]` without `ciMethod` — anytime-valid vs bootstrap intervals aren't comparable;
someone will plot two under different stopping rules as if equal. `ciMethod` is IN the
schema (optional); enforce/surface it once a 2nd CI method coexists.
