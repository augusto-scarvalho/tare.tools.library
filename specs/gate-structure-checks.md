# Gate structure/syntax checks module (gate-lines-burndown r1)

Status: Active (v3, 2026-07-12)

<!-- SPEC-116 NEW-door provenance (specs/templates/intake-refinement.md). -->
<!-- v2 amendment (COVERED door, gate-lines-burndown r2): check_release_hygiene +
LOCAL_ABSOLUTE_PATH_PATTERNS moved verbatim to harness_lib/gate_checks_release.py,
re-exported through spec_test_gate.py (stg.-attribute access unchanged); the
path_pattern_exempt set additionally names the new home. Scenarios gs-4/gs-5. -->
<!-- v3 amendment (COVERED door, gate-lines-burndown r3): check_testing_artifacts,
check_validation_policy, check_handles_lint and check_en_default_strings (with the
SPEC-122 EN-guard constants + scan_en_default) moved verbatim to
harness_lib/gate_checks_content.py, re-exported through spec_test_gate.py
(stg.-attribute access unchanged). EN_GUARD_SCOPE is a positive file list, so the
new home is out of the guard's own scan scope by construction — no allowlist
entry needed. Scenarios gs-6/gs-7. -->

## Request (verbatim)

> `scripts/spec_test_gate.py` is over the 900-line budget and every gate item
> serializes on it. Extract the six self-contained structure/syntax checks into
> a harness_lib module, following the existing
> `scripts/harness_lib/gate_checks_policy.py` precedent. Behavior-preserving:
> every check id and detail string stays byte-identical.

## Covered-check (which door?)

Lookup over existing specs (`doc-find` / spec index over "gate checks",
"structure checks", "burndown") returned no spec owning the gate's extracted
check modules: `gate_checks_policy.py` landed as an MF-series extraction
without its own feature spec. Decision: **NEW** (this spec also names the
precedent pattern the next extraction should follow).

## Goal

Shrink `scripts/spec_test_gate.py` — the largest regression surface in the
repo — by moving its six self-contained structure/syntax checks verbatim into
`scripts/harness_lib/gate_checks_structure.py`, with zero behavioral change:
same check ids, same detail strings, same call sites in `main()`.

## Applicability

The six checks run on the same gates as before (json on every gate including
product-release; yaml/directory-guides/runtime-portability on non-fast gates;
py_compile always; markdown-links on spec-pack and heavier). The module is
bound with the gate's shared `_POLICY_ENV` (`bind(env)` pattern, identical to
`gate_checks_policy`).

## Requirements / invariants

1. **Exactly six functions moved, verbatim.** `check_json_syntax`,
   `check_yaml_syntax`, `check_python_compile`, `check_directory_guides`,
   `check_runtime_portability`, `check_markdown_links` live in
   `harness_lib/gate_checks_structure.py`; their bodies are byte-identical to
   the pre-move gate source.
2. **No moved def remains.** `scripts/spec_test_gate.py` imports the six from
   the new module and defines none of them; call sites in `main()` are
   unchanged.
3. **Ids and details byte-identical.** Every emitted check id and detail
   string is unchanged (the cli-golden fixture and the before/after gate
   output diff are the net).
4. **Static-integrity block untouched.** `check_static_integrity` (including
   the `wsub\.add_parser` regex), the fixture table, the literal
   `security_baseline.evaluate` (control-liveness probe target), and the
   risk-tier / security-regression-ratchet functions all remain in
   `spec_test_gate.py`. (v2) `check_release_hygiene` and
   `LOCAL_ABSOLUTE_PATH_PATTERNS` live in
   `harness_lib/gate_checks_release.py` and are re-exported through
   `spec_test_gate.py` so `stg.`-attribute access is unchanged; its
   `path_pattern_exempt` set keeps every v1 entry and additionally names
   `scripts/harness_lib/gate_checks_release.py` (the new home quotes the
   forbidden patterns).
5. **Line count strictly dropped.** `spec_test_gate.py`'s `splitlines()` count
   is below its frozen pre-move value (1985).
6. **Bind completeness holds.** The new module's free names (`ROOT`,
   `HARNESS`, `result`, `project_config`) are all satisfied by `_POLICY_ENV`
   (`static-integrity:bind-env-completeness` stays green).
7. **(v3) Content/policy checks live in `gate_checks_content`.**
   `check_testing_artifacts`, `check_validation_policy`, `check_handles_lint`
   and `check_en_default_strings` (plus `scan_en_default`,
   `_strip_embedded_comments` and the SPEC-122 EN-guard constants) live in
   `harness_lib/gate_checks_content.py`, bound with `_POLICY_ENV` (extended
   with `GATES` + `command_config`, which stay defined in the gate) and
   re-exported through `spec_test_gate.py` so `stg.`-attribute access
   (`check_handles_lint`, `check_en_default_strings`, `scan_en_default`,
   `EN_GUARD_SCOPE`) is unchanged. `EN_GUARD_SCOPE` is a positive file list,
   so the module's own PT-token literals are out of the guard's scan scope by
   construction; the guard's ids and detail strings stay byte-identical.

## Rationale & sources

Every gate item serializes on `spec_test_gate.py`; smaller files mean smaller
merge surfaces and cheaper reads (token-economy directive: fragment
monoliths). The extraction copies the proven `gate_checks_policy.py` seam —
`bind(env)` + module-level re-export — which the
`static-integrity:bind-env-completeness` check already guards against the
latent-NameError class. The six functions were chosen because they are
self-contained: no fixture state, no subprocesses, pure reads over the tree.
Source-verified at move time against `scripts/spec_test_gate.py` and
`scripts/harness_lib/gate_checks_policy.py`.

## Test strategy

The acceptance scenario imports the real gate module (which performs the real
`bind()`), calls each of the six from their harness_lib home, and asserts the
frozen name set, the unchanged check-id families, the absence of the defs from
the gate source, and the line-count drop. Full `smoke` and `spec-pack` gates
before/after the move are the behavioral net.

```gherkin
Feature: gate structure/syntax checks live in harness_lib
  Scenario: [gs-1] the six checks run from their harness_lib home with unchanged ids
    Given scripts/spec_test_gate.py has performed its module-level bind
    When each of the six moved checks is called from harness_lib.gate_checks_structure
    Then each returns rows in its pre-move check-id family
    And the module's check_* set equals the frozen 6-name list

  Scenario: [gs-2] spec_test_gate.py no longer defines the moved checks
    Given the source text of scripts/spec_test_gate.py
    Then no "def check_<moved-name>" appears in it

  Scenario: [gs-3] the gate file line count dropped below the pre-move count
    Given the frozen pre-move splitlines count of 1985
    Then len(spec_test_gate.py source splitlines) is strictly below it

  Scenario: [gs-4] release-hygiene checks run from their harness_lib home with unchanged ids
    Given scripts/spec_test_gate.py has performed its module-level bind
    When check_release_hygiene is called from harness_lib.gate_checks_release
    Then every returned check id starts with "release-hygiene:"
    And stg.check_release_hygiene and stg.LOCAL_ABSOLUTE_PATH_PATTERNS still resolve

  Scenario: [gs-5] the gate file line count dropped below the r2 pre-move count
    Given the frozen r2 pre-move splitlines count of 1822
    Then len(spec_test_gate.py source splitlines) is strictly below it

  Scenario: [gs-6] the four content/policy checks run from their harness_lib home with unchanged ids
    Given scripts/spec_test_gate.py has performed its module-level bind
    When check_testing_artifacts, check_validation_policy, check_handles_lint and check_en_default_strings are called from harness_lib.gate_checks_content
    Then each returns rows in its pre-move check-id family
    And stg.check_handles_lint, stg.check_en_default_strings, stg.scan_en_default and stg.EN_GUARD_SCOPE still resolve
    And no moved def remains in spec_test_gate.py

  Scenario: [gs-7] the gate file line count dropped below the r3 pre-move count
    Given the frozen r3 pre-move splitlines count of 1660
    Then len(spec_test_gate.py source splitlines) is strictly below it
```

## Validation

`spec-pack` runs `feature-spec-conformance:gate-structure-checks`. The Gherkin
scenarios above resolve to named checks in
`testing/scenarios/gs_gate_structure.py`. The moved checks themselves run on
every gate (`json:*`, `py_compile:*`, and gate-dependent `yaml*`,
`directory-guide:*`, `runtime-portability:*`, `markdown-links`), and
`static-integrity:bind-env-completeness` guards the bind seam.
