# FSV/MXC Validation — staged candidate enumeration case study

**Status:** EMPIRICAL VALIDATION ARCHAEOLOGY.

A precise validation bug was established: `validate --staged` executed staged candidate content via a frozen/dangling candidate commit, but scenario enumeration came from the HEAD scenario set. A newly added staged-only scenario therefore could be omitted, while modifications to an existing scenario executed staged bytes.

## Finding

Enumeration identity and execution identity must refer to the **same frozen candidate**. Required parity cases include ADD, MODIFY, DELETE, RENAME, unchanged HEAD parity and TOCTOU/freeze.

## Boundaries deliberately not collapsed

The finding does not solve `TRUSTED_INVOCATION_SEAM_MISSING`, candidate-independent provenance versus effect isolation, filesystem confinement, strict-proof eligibility, Genesis or Windows deep-path hardening.

This case is preserved because it demonstrates a general assurance hazard: a verifier can execute the right bytes while selecting the wrong test universe.
