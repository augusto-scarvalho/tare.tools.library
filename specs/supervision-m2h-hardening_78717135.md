# SPEC-108 — M2H: Hardening & tracked technical debt

Status: **Done** (executed 2026-07-09; evidence: commits 42c7f19, 374b618 and the H5 commit;
all 7 acceptance checks ran green — see git log for the executed proofs).
Source plan: `tasks/m2h-hardening/PLAN.md`
(parked while M2W/SPEC-107 shipped). Series context: SPEC-101 (legible failures) and
SPEC-102 (CLI supervision surface) are Done; this spec pays the debt those efforts
surfaced before M3 (SPEC-103) starts.

## Grounding

Every item traces to an incident observed on 2026-07-08/09 (evidence: commits of those
dates and `tasks/m2h-hardening/PLAN.md` Context):

1. `validate_json_schema` silently returns `[]` when the optional `jsonschema` package is
   missing — true of the reference stdlib-only install, so documented runtime validation
   never runs and nothing says so (SPEC-101 violation in spirit: a silent no-op is an
   illegible failure).
2. CRLF writer class: the protected-files drift fixture had to be fixed byte-exact
   (commit 7846524) because text-mode writes on Windows rewrite LF as CRLF while
   `.gitattributes` pins `eol=lf`. Other text-mode writers of protected/hashed files
   exist (`tools/hooks/update_agent_handoff.py` writes AGENT_HANDOFF.md).
3. Test workflows left residues in `.harness/state-store/workflows/` + `events.jsonl`
   twice; manual cleanup itself failed once (red gate from an empty parent dir).
4. `escalations` (SPEC-102 surface) is absent from `testing/golden/cli-contract.json`
   and OPERATOR_GUIDE §4; `--resolve` accepts a nonexistent id silently.
5. The post-commit AST graph rebuild is a manual standard (memory
   `graph-rebuild-after-commits`) — the harness can own it.

## Items

| Id | Deliverable | Size |
|----|-------------|------|
| H1 | `schemaValidation: active\|inactive` in `status`; inactive marker on HARNESS_RESULT/REDUCE_RESULT (worker validation already reports `jsonschema\|manual-fallback`) | S |
| H2 | Newline audit: every writer of protected/hashed files uses bytes or `newline="\n"`; run-twice byte-stability proof | S–M |
| H3 | `workflow scrub WF-<id>`: removes `workflows/active/WF-*` + state-store mirror; refuses non-terminal WFs with SPEC-101 message; registered in `supportedWorkflowCommands` and the gate's hard-coded command set | S |
| H4 | Golden entry for `escalations` (requiredJsonPaths `pending`, `count`); OPERATOR_GUIDE §4 documents `escalations`, `--dry-run`, `--override-budget` | S |
| H5 | Gate check `graphify:graph-freshness` (in the always-run policy block) rebuilds a missing/stale graph before reporting — stdlib, no network; retires the manual post-commit rebuild standard. Execution note: `cleanup_test_artifacts` deletes `graphify-out/` at every gate start, so in practice every gate run rebuilds (~1s) — that cleanup was why the graph kept disappearing and the manual standard existed | S–M |
| H6 | `--resolve` unknown id → SPEC-101 error listing pending ids; `HARNESS_IMPROVEMENT_IDEAS.md` section I (platform & runtime integrity) | S |

## Acceptance (MVP)

1. Without `jsonschema` installed: `status` shows `"schemaValidation": "inactive"`;
   finalized HARNESS_RESULT carries the marker.
2. Each protected-file writer run twice → `protect_canonical_files.py check` stays green
   (byte-stable).
3. Create a test WF, `workflow scrub` it → `workflows/active/` and state-store mirror
   clean; release-hygiene green with no manual deletion.
4. Delete `graphify-out/graph.json`, touch a `.py`, run the smoke gate → graph rebuilt,
   check green.
5. `golden-cli:public-command-contract` green with the `escalations` entry.
6. `escalations --resolve nope` → 3-line what/cause/fix error listing pending ids.
7. Commit + protected-files gates green (explicit rc capture).

## Working rules (carried lessons)

- Gate exit codes captured explicitly (`; RC=$?`), never behind a pipe; commit only on rc=0.
- Any test that creates a WF cleans `workflows/active/`, `state-store/workflows/`, and events.
- Incremental commits per item; AST graph rebuilt after code commits until H5 lands.
