# Agentic Async-Await Workflow Pattern

## Goal

Provide a durable async-await orchestration model for multi-agent workflow packets. The goal is to let the harness start independent workers without blocking the initiating CLI process, persist promise/task state to disk, and coordinate completion through explicit await policies.

The existing blocking path remains supported:

```bash
python scripts/harness.py workflow run WF-...
```

The async path is additive:

```bash
python scripts/harness.py workflow start WF-...
python scripts/harness.py workflow await WF-...
python scripts/harness.py workflow collect WF-...
```

## Applies to

Use this pattern for:

- large repository audits split into independent shards;
- fork-join branch reviews that can execute independently;
- scatter-gather work where partial responses are useful;
- long-running I/O-bound agent calls;
- workflows where `all`, `all-settled`, `race`, `first-success`, or `quorum` semantics matter;
- tasks that should be inspectable, awaitable, cancellable, or recoverable from a later session.

Avoid this pattern for:

- small single-file tasks;
- strictly sequential work;
- hidden dependency chains between workers;
- uncontrolled write execution;
- executors with missing auth, active rate limits, or an open circuit breaker.

## Invariants

The async-await path must preserve the same safety boundaries as blocking workflows:

1. `workflow run` remains a stable blocking/threadpool execution path.
2. `workflow start` must materialize durable state before launching work.
3. Async task state must survive terminal closure and be inspectable from a later process.
4. Reducer, reviewer, finalize, promotion, merge, and apply commands remain explicit follow-up actions.
5. Controlled writes still require approval, locks, isolation, merge planning, and explicit apply approval.
6. Placeholder executors remain blocked unless the operator explicitly allows them for testing.
7. Runtime artifacts under `.harness/workflows/active/<WF>/async/` are not release artifacts.

The durable state directory is:

```text
.harness/workflows/active/<workflowId>/async/
  async-group.json
  tasks/
    AT-001.json
    AT-002.json
  events.jsonl
  supervisor.pid
  cancellation.json
  await-result.json
  collect.result.json
```

Task lifecycle:

```text
pending -> scheduled -> running -> fulfilled|rejected|cancelled|timeout|orphaned
```

Promise lifecycle:

```text
pending | fulfilled | rejected
```

A valid `WORKER_RESULT` fulfills the orchestration task even when the worker's domain status is `partial` or `blocked`. Missing/invalid worker output, process failure, timeout, cancellation, and orphan recovery failure reject the orchestration task.

## Agent behavior

Agents operating this harness should:

- use `workflow start` only after a workflow has been planned;
- check `workflow async-status` or `workflow watch --follow` before assuming progress;
- call `workflow await` with an explicit mode when settlement semantics matter;
- call `workflow collect --recover` before reducing after an interrupted session;
- use `workflow reduce --allow-partial` only when fulfilled/partial results are acceptable;
- use `workflow cancel` for operator stops instead of deleting runtime files manually;
- run `workflow async-recover` when task state and OS process state may have diverged.

Command examples:

```bash
python scripts/harness.py workflow start WF-... --executor claude --concurrency 4 --mode all-settled
python scripts/harness.py workflow async-status WF-... --recover
python scripts/harness.py workflow watch WF-... --follow
python scripts/harness.py workflow await WF-... --mode all-settled --timeout 1800
python scripts/harness.py workflow collect WF-... --recover
python scripts/harness.py workflow cancel WF-... --reason "operator stop"
python scripts/harness.py workflow async-recover WF-...
```

Await modes:

| Mode | Settlement rule |
|---|---|
| `all` | All tasks must fulfill; a rejected-like task satisfies await as failure. |
| `all-settled` | Every task must reach a terminal state. |
| `race` | First terminal task satisfies await. |
| `first-success` | First fulfilled task satisfies await, or all terminal failures prove no success. |
| `quorum` | `minSuccess` fulfilled tasks satisfy await, or failure becomes inevitable. |

Default await policy:

```json
{
  "mode": "all-settled",
  "failFast": false,
  "cancelRestOnRace": true,
  "cancelRestOnFirstSuccess": true,
  "minSuccess": 1,
  "groupTimeoutSeconds": 1800,
  "workerTimeoutSeconds": 600,
  "allowPartialReduce": true
}
```

## Validation evidence

A compliant implementation must provide:

- `schemas/async-task.schema.json`;
- `schemas/async-group.schema.json`;
- `schemas/await-result.schema.json`;
- workflow config keys for `awaitPolicy` and `asyncScheduler`;
- profile-level `awaitPolicy` defaults;
- CLI commands: `start`, `await`, `collect`, `cancel`, `watch`, `async-status`, `async-recover`;
- an async supervisor using `asyncio.create_subprocess_exec`;
- bounded queue/backpressure using `asyncio.Queue` and concurrency limits;
- durable cancellation and orphan recovery state;
- validation fixture coverage in `scripts/spec_test_gate.py`.

Async status/collect/await should expose at least:

- `promiseResolutionRate`;
- `partialCompletionRate`;
- `timeoutRate`;
- `cancelRate`;
- `throughput`;
- `responseTimeSeconds`;
- `averageWorkerDurationSeconds`;
- `queueWaitTimeSeconds`;
- `concurrencyEfficiency`.

## Escalation triggers

Escalate to an operator or safer blocking mode when:

- a workflow has an active `.run.lock` whose PID is alive but no async heartbeat is advancing;
- `async-recover` marks tasks as `orphaned`;
- an executor circuit breaker is `open`;
- multiple tasks reject due to rate limit, auth, quota, or payment errors;
- controlled-write preparation has not been completed for a write workflow;
- await reaches timeout with pending tasks and cancellation is not clearly safe;
- reducer output would be based on too few fulfilled tasks for the decision being made.

## Reference anchors

- `.harness/workflows/WORKFLOWS.md` for operator workflow commands.
- `docs/AGENTIC_WORKFLOWS.md` for high-level pattern use.
- `docs/WORKFLOW_OPERATIONS_RUNBOOK.md` for operational commands.
- `schemas/async-task.schema.json` for durable task state.
- `schemas/async-group.schema.json` for group/settlement state.
- `schemas/await-result.schema.json` for persisted await output.
- `scripts/harness.py` for runtime implementation.
- `scripts/spec_test_gate.py` for async workflow fixture validation.
