# P1 Delivery Evidence Observation — 2026-08-26

## Scope and state

- Policy: `ADR-058`
- Repository: `tare.tools.library`
- Mode: `OBSERVE`; no CI or admission gate was enabled.
- Declared/effective class: `E3_CRITICAL` / `E3_CRITICAL`
- Honest delivery state: `PREPARED`
- Classification manifest SHA-256: `3e1ac3bf08a238ac124f477b2918407206904ea1172e736728e03aae601edf40`
- Bootstrap treatment: the first manifest has no parent, so the manifest and classifier retain an intrinsic `E3_CRITICAL` floor.

## Evidence

| Evidence | Result |
|---|---|
| Pre-change repository baseline | `161 passed in 19.78s` |
| Focused policy, runner-safety, and namespace falsifiers | `20 passed in 0.34s` |
| Initial existing mutation campaign | Baseline `ERROR`: ontology absent from the shadow copy; no mutant result claimed |
| First valid mutation campaign | `13 killed / 16 evaluated`; three real model-namespace survivors |
| Strengthened mutation campaign | `16 killed / 16 evaluated`; `0 SURVIVED`, `0 ERROR`, `0 TIMEOUT` |
| Post-change repository suite | `181 passed in 20.51s` |
| Source containment | Runner emitted `ALL_SOURCES_UNCHANGED=True`; all five pre-existing dirty-file SHA-256 values also remained unchanged |
| Line coverage | `UNAVAILABLE`: the active Python environment has no `coverage` module |
| Independent E3 audit | Fable 5 `xhigh`: initial `REVISE`, follow-up `PASS` at confidence `0.92`, zero remaining findings |
| CI | Not run; therefore this observation is not `VALIDATED_CI` or `ADMITTED` |

One cross-model namespace test killed all three meaningful survivors: listing
hashes for one embedding model must exclude another model, stale-document
selection must stay inside the requested model, and deletion must preserve the
other model's rows. The runner now preserves `FAIL`, `TIMEOUT`, and `ERROR` as
distinct results and copies `catalog/ontology` to its temporary shadow.

## Ecosystem guidance and visible gaps

`specgraph ground` returned `NOT_MAPPED` for `tare.tools.library`. The receipt
records `specgraph_repository_not_mapped`; the absence of mapping did not lower
the effective class or authorize admission. This is a concrete P2 traceability
gap, not a test failure.

No false classification block was observed. The local repository suite stayed
near its baseline duration. The mutation campaign found behavior-relevant
coverage that the existing aggregate test count did not reveal.

## Independent audit receipt

The independent auditor used the exact CLI model `claude-fable-5` with effort
`xhigh`, declared bias domain `anthropic/fable`, and implementer bias domain
`openai/gpt`. The CLI reported the canonical model as `claude-fable-5`, no
permission denials, and no subagents.

- Initial session `51f4328c-eb9f-4866-b429-f6b34dde40f9`: `REVISE` at
  confidence `0.86`. It reproduced Windows drive-path acceptance and an E0
  default for unknown executable suffixes; three smaller findings covered path
  casing, a reproduction-command omission, and the unasserted bootstrap label.
- Follow-up session `20e97e93-6275-4f79-a12f-f5ad428420b3`: `PASS` at
  confidence `0.92`; all five findings resolved and no remaining findings.
- Combined reported CLI cost: `$3.707334`. The auditor was read-only and did
  not re-execute tests; the local test and mutation receipts above remain the
  executable evidence.

The accepted correction rejects Windows drive/UNC paths, matches risk paths
case-insensitively, defaults unknown or extensionless paths to E1, and reserves
E0 for a short list of known-inert prose/image artifacts. No dependency,
service, generalized framework, or new CI gate was added.

## Reproduction

```powershell
py -m pytest -q tests/test_delivery_evidence.py tests/test_mutation_tester_safety.py tests/test_vector_namespace_isolation.py
py tests/mutation_tester.py
py -m pytest -q tests tools/publisher/tests
py -m tools.delivery_evidence --declared E3_CRITICAL `
  --path docs/policies/delivery-evidence.json `
  --path tools/delivery_evidence.py `
  --path tests/mutation_tester.py `
  --path tests/test_delivery_evidence.py `
  --path tests/test_mutation_tester_safety.py `
  --path tests/test_vector_namespace_isolation.py `
  --graph-status NOT_MAPPED
```
