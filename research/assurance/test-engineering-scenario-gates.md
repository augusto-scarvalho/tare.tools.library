# Test Engineering, Scenario Gates & Regression Treasury

**Status:** RESEARCH / empirical software-engineering lineage.

## Why this survives separately

Assurance defines what evidence means; test engineering studies how to build/select/schedule a large executable evidence population. The tare.tools scenario gate became large and heavy-tailed enough to expose scheduling, validity and candidate-identity problems that deserve their own research line.

## Historical empirical baseline

The scenario suite grew into hundreds of subprocess-isolated scenarios with scorecards and long-tail runtimes. A small number of expensive scenarios dominated wall time, making a serial queue both slow and scientifically misleading when people equated “full gate” with one homogeneous test class.

## Research questions

- parallel scheduling versus isolation/resource interference;
- fail-fast versus information yield;
- deterministic shard identity and replay;
- regression-test selection without hiding changed behavior;
- candidate-tree enumeration/execution identity;
- mutation/meta-assurance to estimate discriminative power;
- hermetic evidence reuse and invalidation;
- flaky/stochastic agent evaluations versus deterministic scenarios;
- Windows/POSIX execution parity.

## Scientific principles

Test count and coverage are weak proxies. Prefer claim coverage, mutation/fault detection, protected tests, negative controls and calibrated stochastic evaluators. Scheduler optimization must not silently change the evidence population.

## Candidate identity lesson

The FSV/MXC case proved that staged candidate execution can be correct while scenario enumeration is derived from HEAD. A test system therefore needs one frozen subject identity for both **what tests exist** and **what bytes those tests execute against**.

## Economics

Optimize time-to-trust / information gained per scarce resource, not just maximum parallelism. Scheduling should account for CPU/GPU/memory, external services, serial constraints, expected duration and marginal assurance value.
