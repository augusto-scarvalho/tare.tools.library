# IMPLEMENTATION EVIDENCE — TRAIN-18-INTAKE-GEMINI-QUOTA-01

- **Train:** `TRAIN-18-INTAKE-GEMINI-QUOTA-01` — Resume bounded backlog topology grooming after Gemini quota interruption
- **Task disposed:** `INTAKE-OS-CR-DITOS-DO-GOOGLE-GE-2a34cc3db9`
- **Implementer:** `claude_opus` (role: implementer)
- **Trigger:** Initial implementation (prior attempt was `operator_reset` back to `PLAN_APPROVED`; this run re-verified from a clean read-only preflight).
- **Result:** ✅ Intake node marked `DONE` (grade `B`) via the single authorized CLI seam. Zero topology change. All 9 falsifiers pass.

---

## 1. Outcome summary

The intake recorded historical claims (76 NOT_DONE tasks, 14 disconnected roots, "15 causal edges to add"). Current canonical evidence proves **all 15 concrete links already exist** and the graph structurally validates. The smallest correct action — proving that fact and completing only the intake node — was executed. No edge was added; the 2 quarantined prose associations remain absent.

## 2. Command transcript (all captured under `evidence/`)

| Step | Command | Evidence artifact |
|---|---|---|
| PRE hash | `sha256sum work-graph.json` | `PRE_work-graph.sha256` (`b0f712…`) |
| Source hash | `sha256sum INTAKE…md/.json` | `PRE_intake_source.sha256` |
| Preflight validate | `graph_ops … validate` → PASS, 160/209 | `preflight_validate.txt` |
| Preflight diagnostics | `graph_ops … diagnostics` | `preflight_diagnostics.json` |
| Triple matrix | `verify_topology.py … triples` → all present, quarantine absent | `triple_matrix.json` |
| FAL-01 falsifier | `verify_topology.py … triples --wrong-type` → detects MISSING | `FAL01_wrong_type.json` |
| PRE snapshot | `verify_topology.py … snapshot` | `pre_snapshot.json` |
| Export mtimes (before) | `stat` on html/mermaid/log | `export_mtimes_before.txt` |
| **MUTATION** | `graph_ops … complete-node … --grade B --evidence "…" --save` | `complete_node_output.txt` |
| POST hash | `sha256sum work-graph.json` | `POST_work-graph.sha256` (`8ff006…`) |
| POST validate | `graph_ops … validate` → PASS, 160/209 | `postflight_validate.txt` |
| POST diagnostics | `graph_ops … diagnostics` (== pre) | `postflight_diagnostics.json` |
| POST snapshot | `verify_topology.py … snapshot` | `post_snapshot.json` |
| Structural diff | parsed pre/post comparison | `structural_diff.json` |
| Export mtimes (after) | `stat` on html/mermaid/log (== before) | `export_mtimes_after.txt` |
| FAL-09 idempotency | `complete-node …` **no** `--save` → `saved:false`, hash unchanged | `FAL09_second_attempt_nosave.txt` |
| Regression | `pytest tests/` → 90 passed, 1 skipped; canonical hash unchanged | `pytest_regression.txt` |

Full narrative + falsifier matrix: **`evidence/RECOVERY_RECEIPT.md`**.

## 3. Canonical delta (the only mutation)

`work-graph.json` `b0f712…` → `8ff006…`. Parsed structural diff (`evidence/structural_diff.json`):
`INVARIANT_only_target_changed = true` — edges byte-equivalent (209), no nodes added/removed, exactly one node changed (`INTAKE-OS-CR-DITOS-DO-GOOGLE-GE-2a34cc3db9`), only its `completion` field:
`NOT_DONE/grade null → DONE/grade B` (+`dod_satisfied:true`, `completed_at`, `dod_evidence`). No other node/edge/priority/horizon/admission field changed.

## 4. Autonomous engineering decisions (documented per CLAUDE.md ZERO-QUESTIONS invariant)

1. **State-drift 156 → 160 nodes.** The PACKET/plan-audit snapshot expected 156 nodes; live state is 160 (four unrelated later intake proposals admitted after audit time). The governing DoD (PACKET §2 #5) is the *relative* invariant "no node other than the intake changes" — which holds exactly. The plan-audit's literal `==156` is a stale audit-time count, not a live contract. **Decision:** record actual live totals (160/209), enforce the relative invariant, and document the drift as historical evidence. No unrelated node was touched.
2. **No new files under `tests/`.** The generic execution workflow mentions writing falsifier unit tests in `tests/`, but PACKET §3 bounded write footprint authorizes writes **only** to `work-graph.json` (CLI) and `relay/trains/TRAIN-18-INTAKE-GEMINI-QUOTA-01/**`. Writing to `tests/` would breach the footprint (FAL-06). **Decision:** realize falsifier logic as **train-local** evidence scripts (`verify_topology.py`'s `--wrong-type` FAL-01 hook; the FAL-09 no-save probe) which are authorized and were exercised green. The existing `tests/` suite was run read-only as a regression check (90 passed / 1 skipped) with the canonical hash verified unchanged afterward, proving no side effects.
3. **No `git diff HEAD` / DIFF.patch.** This tree is not a git repository, and PACKET §3 forbids any Git operation. **Decision:** substitute a parsed structural diff (`structural_diff.json`) and a changed-paths manifest (`CHANGED_PATHS.md`) as the tamper-evident change record instead of a Git patch.
4. **Stale prior-run artifacts removed.** The reverted prior attempt left `live_after_collision_snapshot.json`, `live_diagnostics.json`, `node_edge_diff.json` describing a scenario that did not occur this run. **Decision:** removed them (train-local evidence dir is authorized) to keep the evidence set internally consistent; all current artifacts are regenerated fresh this run.
5. **UTF-8 enforced (`PYTHONUTF8=1`).** The graph contains a `→` character that the Windows cp1252 console cannot encode. **Decision:** force UTF-8 I/O to read/emit bytes faithfully (FAL-05); source/graph bytes were not normalized or repaired.

## 5. Falsifier ledger

FAL-01 … FAL-09: **all PASS.** See `evidence/RECOVERY_RECEIPT.md` §7 for per-ID outcomes and artifact links.

## 6. Deferred (out of scope — do not land as part of this train)

Residual diagnostics preserved verbatim and unmodified: 6 orphan islands (incl. owner-cockpit), 7 horizon inversions, 2 transitive redundancies. Plus the 2 quarantined prose associations (`RELAY-INTAKE-DOGFOODING-CONSENSUS-01 → p11`, `assurance-topology → p20`) which require a separate admitted task. Bookkeeper exports (`work-graph.html/.mermaid`, `BACKLOG_BOOKKEEPING_LOG.md`) deferred to the normal post-landing workflow.
