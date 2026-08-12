# Recurrent Memory / RNN / Memory Caching — Experimental Lineage

**Document ID:** `experiment.local-llm.recurrent-memory.lineage-2026-08-12`  
**Document type:** `experiment`  
**Status:** `EXPERIMENTAL`  
**Created:** `2026-08-12`  
**Primary contexts:** Runtime / Model / Inference · Memory / Context · Validation / Assurance · Observability / Economics / Resources  
**Authority:** research/experimental evidence only; does not mint tare.tools TARGET or canonical CURRENT.

## 1. Purpose

This lineage preserves the scientific path from early recurrent/TPTT experiments through the current Mamba transportability work without converting negative experiments into disappearances or positive observations into architectural authority.

The line has progressively narrowed its question:

```text
Can recurrence / Memory Caching improve a Transformer?
        ↓
Does a historical-memory mechanism require co-adaptation?
        ↓
Can a frozen recurrent model exhibit controlled forgetting?
        ↓
Does unique recurrent-state load cause retrieval loss?
        ↓
Does an earlier recurrent state preserve information the final state lost?
        ↓
Can target-agnostic historical-state selection recover that information?
        ↓
Does the result transport across checkpoint/backend and remain useful end-to-end?
```

The latest independent audit is authoritative for the interpretation of `RNN-06T` within this research publication.

## 2. Evidence hierarchy used in this lineage

```text
experiment preregistration + executed source + raw results
        >
independent audit / reconciliation
        >
implementer handoff / narrative
        >
research synthesis
```

When the handoff and independent audit disagree, both are preserved and the downstream classification follows the audit until a fresh prospective experiment resolves the disagreement.

## 3. Compact scientific ledger

| Stage | Result | Experimental meaning |
|---|---|---|
| RNN-08/09 | tested TPTT configuration `PARKED` | after state-lifecycle correction, tested TPTT+LoRA regressed vs LoRA and cost more; not a universal TPTT falsification |
| RNN-04 | exploratory MC positive under co-training | first signal, later narrowed because the substrate/conditioning did not prove post-hoc utility |
| RNN-05A | frozen LA post-hoc MC `NEGATIVE / NO_EFFECT` | historical memory is not a free attach-on for this additive substrate |
| RNN-05B | co-adaptation interaction `SUPPORTED` | train/inference memory-mode alignment matters strongly in DN/GDN |
| RNN-05B-EXT | `BLOCKED_BY_UNSTABLE_BASE` | per-condition training conflated forgetting with training/basin instability |
| RNN-05B-EXT2 | fixed-backbone graded region `BLOCKED` | synthetic recipe stayed flat-high; no MC run; no EXT3 |
| RNN-06-P0 | Mamba graded band `PLAUSIBLE` exploratory | real recurrent LM showed a useful forgetting curve; P co-varied with length/gap |
| RNN-06A | strict lifecycle `NOT_QUALIFIED` | full-vs-segmented numerical differences and prereg deviations preserved |
| RNN-06A2 | continuation lifecycle `QUALIFIED` | exact pinned Transformers-native Mamba continuation/checkpoint contract passed |
| RNN-06B | original causal contract `BLOCKED` | same-space competition not needed; length vs general binding load unresolved |
| RNN-06B2 | fixed-length graded contract `BLOCKED` | strong state-load signal, but order churn/full-packing confounds found |
| RNN-06B3 | controlled unique-binding-load forgetting `QUALIFIED` | length, gap, binding order and full-packing confounds controlled; robust loss |
| RNN-06C | historical-state information `QUALIFIED (presence)` | same-aged repeated-sentinel branch retains access while high unique load loses it |
| RNN-06D0 | recovery ceiling `QUALIFIED` | scheduled historical pool contains large recoverable signal |
| RNN-06D1 | prereg gate `QUALIFIED_PARAMETER_FREE` | parameter-free historical recovery strongly positive on exact synthetic Mamba substrate |
| RNN-06D audit refinement | adaptive selector incremental value `OPEN` | a fixed slot already captures most of the gain in the narrow target band |
| RNN-06T | handoff claimed official Mamba transport qualification | official fast path and real in-run capture observed |
| **RNN-06T independent audit** | **`ACCEPTED_AS_EXPLORATORY_WITH_MAJOR_GATE_RECONCILIATION`** | strict T0 prereg was not satisfied; 3A/3B/economics/scout are exploratory non-load-bearing |
| RNN-06T2 | **in progress / no result published yet** | fresh prospective fixed-batch lifecycle requalification + recovery confirmation |

## 4. Results that are currently load-bearing inside the experimental lineage

### 4.1 State ownership is part of recurrent-model semantics

The original TPTT shared-state incident demonstrated that independent examples can contaminate one another when recurrent state is not explicitly sequence-owned. This later became request/branch isolation and temporal-identity testing.

### 4.2 Historical-memory mechanisms exhibit co-adaptation

RNN-05B's 2×2 train/inference comparison produced large interaction effects for non-additive recurrent substrates. The result supports the research hypothesis that a learned interface to historical state may be necessary when simple post-hoc aggregation fails.

This supports studying trained historical retrieval (for example DART-like mechanisms) **only if** simpler recovery leaves a meaningful oracle gap. It does not authorize such a mechanism yet.

### 4.3 Controlled unique-binding load causes retrieval loss on the exact frozen Mamba subject

RNN-06B3 removed the major B2 confounds:

- fixed total token length;
- fixed target→query gap;
- permanent ordinal→slot→binding mapping;
- positive sentinel reserve at every dose;
- same frozen checkpoint/backend.

Observed DS constrained accuracy:

```text
U=1     0.990
U=24    0.917
U=48    0.865
U=72    0.771
U=96    0.755
U=128   0.651
U=152   0.568
U=176   0.573
```

Paired U1→U176 loss was approximately `0.417`, with reported 95% interval `[0.349, 0.490]` and robustness across all three preregistered example strata.

Correct scope:

`GENERAL_UNIQUE_BINDING_STATE_LOAD_EFFECT = QUALIFIED`

The stronger mechanism label “literal recurrent-state capacity saturation” remains a supported hypothesis rather than a separately identified causal mechanism.

### 4.4 Historical state retains behaviorally accessible information

RNN-06C compared three branches:

- `H`: historical-direct state near target write;
- `N`: same-aged repeated-sentinel continuation;
- `L`: same-aged high unique-binding-load continuation.

Observed:

| Condition | Accuracy |
|---|---:|
| H | 163/192 = 0.849 |
| N | 192/192 = 1.000 |
| L | 105/192 = 0.547 |

Primary paired `N-L = 0.453125`, reported interval `[0.385, 0.526]`, with `87` N-correct→L-wrong transitions and `0` in the reverse direction.

Correct scope:

`HISTORICAL_STATE_INFORMATION = QUALIFIED (PRESENCE)`

The repeated-sentinel arm is a matched same-aged control, **not** a universally neutral state transformation.

### 4.5 Historical-state recovery is strongly supported on the exact synthetic Mamba-06D substrate

RNN-06D raw readouts independently reproduced:

```text
FINAL                 25/192 = 0.1302
fixed slot 38                    0.4896
fixed slot 76                    0.7708
fixed slot 115                   0.4583
fixed slot 153                   0.2865
ORACLE_BEST           174/192 = 0.9063
MAX_CONFIDENCE        160/192 = 0.8333
```

For `MAX_CONFIDENCE`:

```text
delta vs FINAL = +0.7031
recovered      = 135
harmed         = 0
```

Independent audit added the missing fixed-state control:

```text
ALWAYS_SLOT_76
accuracy       = 0.7708
delta vs FINAL = +0.6406
recovered      = 123
harmed         = 0
```

Therefore:

```text
PARAMETER_FREE_HISTORICAL_RECOVERY_EXISTS
= SUPPORTED_STRONGLY

ADAPTIVE_SELECTION_CAUSAL_ADVANTAGE_OVER_BEST_FIXED_CHECKPOINT
= NOT_YET_QUALIFIED
```

The narrow-band experiment used a known target-position distribution, so general unknown-position recovery remains open.

## 5. RNN-06T: official Mamba transportability — preserved result plus audit reconciliation

### 5.1 Strong positive observations

The train pinned the official subject:

```text
state-spaces/mamba2-1.3b
revision c5b59d00ec85d313adea86a08cad2a43c962dd3b
mamba_ssm 2.2.4
causal_conv1d 1.5.0.post8
triton 3.2.0
torch 2.6.0+cu124
bf16
RTX 3090
```

The audit accepts:

```text
OFFICIAL_MAMBA_FASTPATH
= RUNNABLE_SUPPORTED

SINGLE_PASS_HISTORICAL_CAPTURE
= SUPPORTED_STRONGLY
```

The single-pass path captured actual intermediate recurrent states from one canonical trajectory and replayed matching boundary hashes.

### 5.2 Major gate reconciliation

The frozen T0 preregistration required, among other properties:

- D: run-alone comparison under `TOL_BATCH=0.03`;
- G: row vs batch-1 equivalence.

The first executed comparison observed:

```text
batch1 vs batch6 max_abs_diff = 0.5
TOL_BATCH = 0.03
```

After this outcome, the runner changed D/G to a fixed-batch neighbor-isolation contract and later minted lifecycle `QUALIFIED`.

The audit classifies this as a post-outcome change to a load-bearing gate. It additionally found incomplete execution of preregistered branch/fork, reset/reuse and serialization-continuation checks.

Therefore:

```text
OFFICIAL_MAMBA_LIFECYCLE_STRICT_PREREG
= NOT_QUALIFIED

PROTOCOL_GATE_ORDERING
= FAILED
```

The train protocol required lifecycle qualification before 3A/3B. Downstream observations are preserved, but their evidence class is downgraded:

```text
HISTORICAL_RECOVERY_TRANSPORT_3A
= EXPLORATORY_STRONG_POSITIVE

ADAPTIVE_SELECTOR_ADVANTAGE_3A
= EXPLORATORY_DIRECTIONAL

WIDE_TARGET_RECOVERY_3B
= EXPLORATORY_STRONG_POSITIVE

ADAPTIVE_SELECTION_3B
= EXPLORATORY_STRONG_POSITIVE

END_TO_END_RECOVERY_UTILITY
= NOT_QUALIFIED_AS_APPLES_TO_APPLES

NL_NEEDLE_SCOUT
= EXPLORATORY_NO_SIGNAL
```

### 5.3 Why the 3B observation remains scientifically interesting

The wide-target band `[8,144]` uses schedule `[38,76,115,153]`.

A previous narrative said no fixed snapshot had observed every target. That is false: slot `153` is after every allowed target.

The better mechanistic interpretation is:

```text
NOT_YET_WRITTEN
        ↕
SEEN_AND_RETAINED
        ↕
ALREADY_FORGOTTEN
```

A confidence selector may be locating a temporal state inside the “seen and retained” window. The observation is strong enough to motivate fresh confirmation but not strong enough to bypass the failed upstream lifecycle gate.

## 6. Memory Caching status after the current evidence

Keep two separate ledger entries:

```text
SYNTHETIC_DENSE_POST_HOC_MEMORY_CACHING_RECIPE
= PARKED
```

and:

```text
HISTORICAL_RECURRENT_STATE_AS_MEMORY
= REOPENED_AT_RECOVERY_LAYER
```

The former is a specific failed/blocked recipe. The latter is a research family now supported by controlled forgetting, information presence and strong historical-recovery observations.

Do **not** publish the phrase “Memory Caching works” as a scientific conclusion.

## 7. Research alternatives

Current research-only branches:

| Branch | Status | Trigger |
|---|---|---|
| DART-like trained state-memory attention | CONDITIONAL | oracle ceiling high, simple target-agnostic selector leaves material gap |
| StateX-like current-state expansion | ALTERNATIVE | historical snapshot recovery has low ceiling or poor economics |
| Gated DeltaNet-2 | WATCH / ALTERNATIVE | erase/write dynamics become the causal target |
| Sparse Delta Memory | WATCH | explicit capacity expansion warrants higher implementation/training cost |
| INT8 recurrent archive / ReplaySSM | DEFER | semantic utility first, systems economics second |
| Qwen3.5-0.8B GDN/hybrid transfer | DEFER | requires accepted Mamba transportability and lifecycle semantics first |
| Qwen3.6-35B-A3B deployment-family target | DEFER | later validation target only |

## 8. Methodological rules retained from this program

1. Recurrent state ownership is model semantics.
2. A cache API is not checkpoint/restore qualification.
3. Complete state includes every state family required by the declared continuation contract.
4. Snapshot bytes must be bound to the exact temporal boundary they claim to represent.
5. Backend/kernel/dtype/chunk semantics are part of execution identity.
6. A feature configured but not exercised is not evidence about that feature.
7. Structural lifecycle invariants are independent of quality accuracy.
8. Calibration and qualification identities remain separate.
9. Negative evidence is append-only.
10. A failed preregistered gate cannot be made green by rewriting the test after observing the failure.
11. Downstream outcomes behind a failed hard gate may remain useful observations, but their authority is downgraded.
12. Target-aware/gold-aware selectors are diagnostic ceilings, not deployment evidence.
13. Quality utility and end-to-end systems utility are separate gates.

## 9. Current frontier

The immediate in-flight packet is `RNN-06T2`:

```text
T0R
fresh fixed-batch lifecycle requalification
        ↓ hard gate
T1R
fresh recovery confirmation
+ corrected apples-to-apples economics
```

Until independent audit accepts T0R/T1R:

```text
OFFICIAL_MAMBA_TRANSPORTABILITY
= OPEN / NOT CONFIRMATORILY CLOSED

REALISTIC_LONG_CONTEXT_OPERATING_POINT
= NOT YET AUTHORIZED

QWEN_TRANSFER
= DEFER
```

## 10. Source identities

This publication was derived from locally materialized research/audit artifacts. Exact source hashes are preserved in `DOCUMENT_MANIFEST.json`.

Key audit bundle identities:

- RNN-06D audit bundle SHA-256: `9bd4df8a1f4a63b532f923e50b28deb55b25894978912f603caa3745e26b8a75`
- RNN-06T audit bundle SHA-256: `cf4ecc0b02452dbba6e184b067f61003553139e8e06d99148b82ae85a134d370`
- RNN-06T implementer handoff SHA-256: `fed83cd4b07a6efdcc45c75a0fe8033527def614c08709429352cf3cea8c206b`
- independent RNN-06T audit SHA-256: `4c0e8fdd362bd1250dcedd2b9df50519f1cd06d682a1e5d6a74bfb89c3f4623c`

Raw ZIP bundles are **not** copied into this public research publication by default; the digests and derived audit artifacts preserve identity while avoiding accidental publication of incidental workstation evidence.

## 11. Publication boundary

This document is an `EXPERIMENTAL` research record.

It may influence later findings, research pointers, proposals and experimental design.

It does not:

- promote historical-state recovery into tare.tools architecture;
- establish a production memory subsystem;
- authorize Qwen work;
- override the local experiment repo/Git;
- replace the original preregistrations, raw results or independent audit bundles.
