# FSV/MXC Validation — staged candidate enumeration case study

[← Kimi/Antigravity case](../vendor-runtime/kimi-antigravity-capability-parity.md) · [Case Studies](../README.md) · [Navigation](../../NAVIGATION.md)

**Status:** EMPIRICAL VALIDATION ARCHAEOLOGY.

A precise validation bug was established: `validate --staged` executed staged candidate content via a frozen/dangling candidate commit, but scenario enumeration came from the HEAD scenario set. A newly added staged-only scenario therefore could be omitted, while modifications to an existing scenario executed staged bytes.

## Finding

Enumeration identity and execution identity must refer to the **same frozen candidate**. Required parity cases include ADD, MODIFY, DELETE, RENAME, unchanged HEAD parity and TOCTOU/freeze.

## Boundaries deliberately not collapsed

The finding does not solve `TRUSTED_INVOCATION_SEAM_MISSING`, candidate-independent provenance versus effect isolation, filesystem confinement, strict-proof eligibility, Genesis or Windows deep-path hardening.

This case is preserved because it demonstrates a general assurance hazard: a verifier can execute the right bytes while selecting the wrong test universe.

---

**Research supported:** [Test Engineering](../../research/assurance/test-engineering-scenario-gates.md) · [Canonical Lineage](../../research/context/canonical-lineage-identity.md)  
**Next case:** [Agent Relay Q0 →](../evidence-exchange/agent-relay-q0.md)
