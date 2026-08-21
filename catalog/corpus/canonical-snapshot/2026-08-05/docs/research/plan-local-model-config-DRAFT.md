# Plan: local-model configuration split

Status: independent plan-author draft; design only, no implementation.

## Design

### 1. Spec flow

This is covered by the existing self-hosted HTTP-executor boundary, so it should
not open a new SPEC id.

- Create the refinement artifact at
  `specs/40-features/local-model-operator-config.intake.md`, using
  `specs/templates/intake-refinement.md`.
- Amend `specs/40-features/compat-executor-routing.md` as **SPEC-165 amendment
  v3**, extending requirements 5 and 6 with numbered requirements for the
  operator overlay, precedence, setup validation, and no-overlay compatibility.
- Put the UI/CLI acceptance Gherkin in that amendment, with scenario check ids
  mapped to the proposed `lmc-*` scenario checks.
- Update `specs/MANIFEST.yaml` as required by the normal spec-pack flow.

This is the covered door because SPEC-165 R5 owns `local-llama` and its LAN
allowlist, while R6 owns keyless authorization. A records search found no
narrower governing decision; repository discovery pointed to the existing
canonical-seed/local-copy and chat-setup precedents.

### 2. Overlay location and names

Keep the operator file inside the repository:

- Canonical, tracked example and compatibility defaults:
  `.harness/runtime/local-model-config.example.json`
- Operator-local, gitignored delta:
  `.harness/runtime/local-model-config.json`

Add only the local filename to `.gitignore`; do not ignore all of
`.harness/runtime/`.

This location wins over an XDG-style file. The repo already keeps local
`chat-prefs.json` and `executor-state.json` in `.harness/runtime/`, and
`tools/bootstrap_local.py` establishes the tracked `*.example*` to gitignored
local-file vocabulary. Keeping the overlay here also lets `harness.py doctor`
inspect the exact file without searching user-global locations.

Do **not** add this overlay to `tools/bootstrap_local.py`'s `DERIVED` map. It is
optional and must tolerate absence; `models setup-local` is its intentional
creator. The example remains available for manual copying, but a fresh clone
does not acquire a fake "configured" state.

### 3. Canonical example and overlay shape

The tracked example is also the lowest-precedence compatibility default:

```json
{
  "schemaVersion": 1,
  "_notice": "baseUrl selects a destination; allowHosts and keylessHosts are separate explicit grants and are never derived from it",
  "localLlama": {
    "baseUrl": null,
    "allowHosts": ["localhost", "127.0.0.1", "::1"],
    "keylessHosts": ["localhost", "127.0.0.1", "::1"],
    "contextWindow": 65536,
    "minimumOutputTokens": null
  }
}
```

`baseUrl: null` preserves today's requirement that the operator provide
`OPENAI_BASE_URL`. The loopback lists and `contextWindow: 65536` preserve the
current no-overlay behavior; the latter is explicitly a compatibility default,
not a claim about every model.

The helper writes a local delta such as:

```json
{
  "schemaVersion": 1,
  "localLlama": {
    "baseUrl": "http://192.0.2.10:8080/v1",
    "allowHosts": ["192.0.2.10"],
    "keylessHosts": ["192.0.2.10"],
    "contextWindow": 65536,
    "minimumOutputTokens": 300,
    "detected": {
      "servedId": "local_agent_coder",
      "contextWindowTrained": 262144,
      "parameterCount": 34660610688,
      "sizeBytes": 26445203968,
      "verifiedAt": "RFC-3339 timestamp"
    }
  }
}
```

The local file is a delta over these operator fields. It is never merged into
the executor or card object wholesale. Its schema accepts only `baseUrl`,
`allowHosts`, `keylessHosts`, `contextWindow`, `minimumOutputTokens`, and the
bounded `detected` metadata object. Keys such as `commandTemplate`, `id`,
`models`, `executors`, `envKeepList`, or arbitrary unknown keys are rejected.

Lists replace the corresponding example list; they are not appended. An
explicit empty `allowHosts` is invalid. Omitting `allowHosts` retains the
canonical loopback grant, so a LAN `baseUrl` without a separate LAN grant fails
closed.

Move `contextWindow` out of the raw `local-llama` card in
`.harness/routing/model-cards.json`. Keep the generic `qwen36-fast` id and all
vendor cards unchanged. A resolved-card view overlays the effective
`contextWindow` and `minimumOutputTokens` for inspection without rewriting the
canonical card.

### 4. Precedence and inspectability

Resolve each field independently:

| Field | Precedence, highest first |
|---|---|
| `baseUrl` | non-empty process `OPENAI_BASE_URL` -> local overlay -> canonical `null` |
| `allowHosts` | local overlay -> canonical loopback list; no environment override exists |
| `keylessHosts` | local overlay -> canonical loopback list; no environment override exists |
| `contextWindow` | local overlay -> canonical compatibility value `65536` |
| `minimumOutputTokens` | local overlay -> canonical `null` |
| card `id` | canonical `qwen36-fast` only |
| API key | existing process environment -> OS vault behavior; never stored in this overlay |

When tiers disagree, the table above decides. A process environment can select
a different `baseUrl`, but it cannot authorize that host. If the selected host
is not present in the separately resolved `allowHosts`, local-model resolution
is invalid and spawning is refused before a request.

The brief refers to `common.load_env_file` and its `setdefault` behavior. Current
source has since replaced that function with `load_ambient_keys()` and the
process-env -> OS-vault key cascade. Do not resurrect `.env`. Instead, after
`load_ambient_keys()`, load the local overlay and apply only its non-secret
`baseUrl` with `os.environ.setdefault("OPENAI_BASE_URL", ...)`. This retains the
required real-environment-wins behavior and lets the existing
`envKeepList` carry the resolved URL into filtered worker environments.

Make the answer visible in two existing surfaces:

- `python scripts/harness.py models show qwen36-fast --resolved` prints the
  resolved local fields plus a source label for each field
  (`environment`, `local overlay`, or `canonical example`). It prints no secret.
- `python scripts/harness.py doctor` adds a static `local-model-config` check:
  absent overlay is OK/canonical-loopback; a valid overlay is OK and names the
  resolved host and source; malformed, stale, or authorization-mismatched config
  is WARN. `doctor` performs no network request.

### 5. Safe `commandTemplate` merge

Keep the security flags in the canonical
`.harness/routing/executors.json` template and replace only their value tokens:

```json
[
  "{python}",
  "tools/openai_worker.py",
  "--allow-hosts",
  "{localAllowHosts}",
  "--keyless-hosts",
  "{localKeylessHosts}",
  "--model",
  "{model}",
  "{prompt}"
]
```

The overlay cannot contain argv or a command template. A small
`scripts/harness_lib/local_model_config.py` resolver validates the overlay,
normalizes host entries, and substitutes exact argv elements equal to
`{localAllowHosts}` and `{localKeylessHosts}` with comma-separated resolved
lists. It must not perform general string or shell interpolation.

Apply that resolution in `executor_config("local-llama")`, the shared executor
read seam. Change `spawn_command()` to use `executor_config()` instead of its
current direct `load_executors()` lookup. The workflow-spawn and route-loop
paths already use `executor_config()`. This produces the same literal loopback
argv as today when no overlay exists, while ensuring every normal spawn path
receives the local delta.

Validation must reject an explicit empty `allowHosts` before rendering.
`tools/openai_worker.py` currently skips its egress check when
`args.allow_hosts` is an empty string, so allowing an empty rendered value would
turn a malformed overlay into a bypass.

### 6. Helper command

Add one action to the existing model command family:

```text
python scripts/harness.py models setup-local
python scripts/harness.py models setup-local --base-url URL --allow-host HOST [--keyless-host HOST] [--served-id ID] [--probe-tokens 300] [--update]
```

It uses the existing model-card surface rather than adding a top-level setup,
config, or validation command.

Interactive flow:

1. Ask for the base URL, defaulting only to an already resolved
   `OPENAI_BASE_URL`; otherwise require input.
2. Parse and normalize it. Accept only `http` or `https`, require a hostname,
   and reject embedded credentials, query strings, and fragments.
3. Display the parsed hostname and ask for a separate, explicit egress grant:
   `Allow local-llama to contact HOST? [y/N]`. Only an affirmative answer
   creates `allowHosts`. The host may be suggested from the URL, but it is not
   authorized without this separate confirmation.
4. If no API key is present and the host is not loopback, ask separately:
   `Permit keyless requests to HOST? [y/N]`. Declining requires an API key and
   does not silently copy the egress grant into `keylessHosts`.
5. Run the health and thinking checks below.
6. Show the exact delta and its resolution sources, then write
   `.harness/runtime/local-model-config.json` only after every check passes.

Non-interactive mode requires `--base-url` and a separate `--allow-host`; the
URL alone is insufficient. A non-loopback, keyless setup additionally requires
the separate `--keyless-host`. This preserves two independent declarations
even in automation.

Existing overlay behavior:

- Without `--update`, refuse before probing or writing.
- With `--update`, require the existing file to parse and validate, retain it
  unchanged until the replacement has passed all checks, show the changed
  fields, then replace it.
- Do not provide a blind `--force` path for malformed existing configuration.

Other refusals:

- unreachable server, timeout, non-2xx response, or invalid JSON;
- `/v1/models` returns no served model;
- selected model metadata lacks a positive `n_ctx`;
- multiple served models without `--served-id`;
- the approved host differs from the URL host after normalization;
- missing API key for a non-loopback host without a separate keyless grant;
- thinking confirmation still returns no content at the chosen probe floor;
- any attempt to place canonical executor/card fields in the delta.

The helper writes no API key and does not rename the generic card id.

### 7. Health and thinking validation

Health check:

- After the egress grant is confirmed, perform `GET <baseUrl>/models` with a
  short timeout and the existing API key when present.
- Require at least one model and read the measured llama.cpp fields: served id,
  `n_ctx`, `n_ctx_train`, `n_params`, and `size`.
- Use `n_ctx` as `contextWindow`; store the remaining facts under `detected`.
- Cost: zero generated tokens. This metadata request is mandatory before any
  write.

Thinking check:

- POST a deterministic "reply exactly OK" request with `max_tokens=16`.
- If it returns non-empty content, record `minimumOutputTokens: 16`.
- If it returns empty content with `finish_reason: length`, classify it as a
  thinking model and make one confirmation request with `max_tokens` equal to
  `--probe-tokens` (default `300`).
- Record the confirmed value only if that request returns non-empty content.
  Otherwise refuse to write and tell the operator to rerun with an explicitly
  larger `--probe-tokens`.
- Cost: at most 16 completion tokens for a non-starved model; at most
  16 + 300 = 316 completion tokens by default for a thinking model. The second
  spend occurs only after the cheap probe proves it necessary. This is a
  one-time setup cost that prevents an empty worker result from being mistaken
  for a broken server.

`minimumOutputTokens` is a recorded lower bound validated by setup. It is not a
new global workflow token budget. Any future code that introduces an OpenAI
`max_tokens` cap must clamp it to at least this resolved floor.

### 8. Backward compatibility

With no local overlay:

- `OPENAI_BASE_URL` continues to come from the real process environment;
- the resolved allow/keyless argv values are exactly
  `localhost,127.0.0.1,::1`;
- the resolved card remains `qwen36-fast` with `contextWindow: 65536`;
- a missing base URL still fails as it does today;
- vendor executor/card objects are byte-for-byte untouched.

Lock this with an acceptance scenario that removes the overlay, sets a loopback
`OPENAI_BASE_URL`, and compares the rendered argv and resolved card to the
pre-change fixtures.

### 9. Pre-existing spawn-mapping gap

Do **not** fix `task-profiles.json` spawn mappings in this plan. The failure
`Profile 'review' has no spawn mapping for executor 'local-llama'` predates the
configuration split and requires a routing-policy decision: which profiles may
select the local executor, with which model and effort. Adding mappings here
would silently change model routing rather than merely make operator config
local.

Track it as a separate SPEC-165 follow-up/backlog item. `models setup-local`
validates the endpoint directly and therefore does not depend on
`spawn-command --executor local-llama`.

## Rationale table

| Decision | Source |
|---|---|
| In-repo `.harness/runtime/` overlay, not XDG | Repo precedent: gitignored `chat-prefs.json`, local `executor-state.json`, and `tools/bootstrap_local.py` canonical-seed/local-copy pattern; judgement call favoring discoverability by `doctor` |
| Do not auto-materialize this optional overlay in bootstrap | Repo precedent: `bootstrap_local.py` explicitly derives only required configs and says other local files tolerate absence; backward-compatibility requirement |
| Process env wins for `baseUrl` | Brief measurement of prior `setdefault` semantics; current `load_ambient_keys()` source preserves real-env-wins for the OS-vault cascade |
| No environment tier for allow/keyless lists | Binding overseer correction and measured SPEC-165 R6 security boundary |
| Overlay is a strict field delta | Binding brief decision; research finding that full replacement can silently drop security flags |
| Canonical template retains both flags | Binding brief decision; current `tools/openai_worker.py` consumes both argv flags |
| Empty `allowHosts` is invalid | Source verification: `openai_worker.py` checks egress only when `args.allow_hosts` is truthy |
| Generic `qwen36-fast` id stays canonical | Live measurement: llama.cpp ignored the request model id and served the loaded model |
| `contextWindow` comes from `/v1/models.n_ctx` | Live measurement: `n_ctx` reflects deployment tuning while `n_ctx_train` is the trained limit |
| `models setup-local` rather than a new top-level verb | Repo precedent: `models` already owns card CRUD; brief requires sitting on existing commands |
| `models show --resolved` and `doctor` expose resolution | Repo precedent: existing show and WARN-only doctor surfaces; little-coder research finding that echoing resolved config aids diagnosis |
| Mandatory pre-write health check | Live measurement that `/v1/models` exposes the needed metadata; judgement call because little-coder has no validation precedent |
| 16-token detection plus one 300-token confirmation | Live measurements: 16 produced empty content/length, 300 produced `OK`; judgement call to bound setup cost and refuse rather than auto-escalate indefinitely |
| Separate spawn-mapping follow-up | Measured pre-existing failure plus judgement that profile mappings are routing policy, not operator configuration |

## File footprint

An implementer should touch:

- `specs/40-features/local-model-operator-config.intake.md`
- `specs/40-features/compat-executor-routing.md`
- `specs/MANIFEST.yaml`
- `.harness/runtime/local-model-config.example.json`
- `.harness/runtime/local-model-config.json` only when the operator runs the helper; never commit it
- `.gitignore`
- `.harness/routing/executors.json`
- `.harness/routing/model-cards.json`
- `scripts/harness_lib/local_model_config.py`
- `scripts/harness_lib/model_routing.py`
- `scripts/harness_lib/repo_health.py`
- `scripts/harness.py`
- `docs/OPERATOR_GUIDE.md`
- `testing/scenarios/lmc_local_model_config.py`
- Existing focused regression scenarios where their assertions cover the
  changed seams: `testing/scenarios/cer_compat_routing.py`,
  `testing/scenarios/rs_research_skill.py`, and
  `testing/scenarios/pc_post_clone.py`

Intentionally not touched:

- `.env` or `.env.example`
- `tools/bootstrap_local.py`
- vendor cards or vendor executor templates
- `.harness/routing/task-profiles.json` for the separate spawn-mapping gap

## Acceptance criteria

1. **[lmc-no-overlay-compat]** With
   `.harness/runtime/local-model-config.json` absent and a loopback
   `OPENAI_BASE_URL`, the rendered `local-llama` worker argv contains the same
   two loopback lists in the same positions as before, the card id is
   `qwen36-fast`, and the resolved context window is `65536`.
2. **[lmc-vendors-unchanged]** Adding or removing a local overlay does not alter
   any non-`local-llama` executor or card object.
3. **[lmc-env-precedence]** When process `OPENAI_BASE_URL` and overlay `baseUrl`
   disagree, the process value is resolved and reported with source
   `environment`.
4. **[lmc-env-does-not-authorize]** If that winning environment URL names a host
   absent from resolved `allowHosts`, resolution/spawn refuses before network
   access.
5. **[lmc-allowlist-structural]** An overlay cannot contain
   `commandTemplate`; every successfully resolved local command contains both
   `--allow-hosts` and `--keyless-hosts` from the canonical template.
6. **[lmc-allowlist-cannot-drop]** A LAN `baseUrl` with omitted `allowHosts`
   retains only canonical loopback and is refused; an explicitly empty
   `allowHosts` is invalid. Neither case can render an unguarded worker command.
7. **[lmc-keyless-separate]** Approving an egress host does not add it to
   `keylessHosts`; without an API key, a non-loopback host requires a second
   explicit keyless grant.
8. **[lmc-helper-unreachable]** An unreachable/timed-out server leaves an absent
   overlay absent and an existing overlay byte-identical.
9. **[lmc-helper-empty-models]** A successful `/models` response with no models
   is refused and writes nothing.
10. **[lmc-helper-existing]** An existing overlay is refused without
    `--update`; a failed update check leaves the old bytes untouched.
11. **[lmc-helper-detects]** A valid single-model response writes `n_ctx` as
    `contextWindow` and records the served id, trained context, parameters,
    size, and verification timestamp without changing the generic card id.
12. **[lmc-thinking-floor]** Empty content plus `finish_reason: length` at 16
    tokens triggers exactly one configured-floor confirmation; success records
    that floor, while another empty result refuses the write.
13. **[lmc-resolved-show]** `models show qwen36-fast --resolved` reports each
    effective local field and its source without printing an API key.
14. **[lmc-doctor-static]** `doctor` reports absent/valid/invalid overlay state
    without contacting the configured server.
15. **[lmc-post-clone]** The post-clone scenario remains green without creating
    the optional overlay, proving readers tolerate its absence.

## Open questions for the owner

1. Which task profiles, if any, should gain explicit `local-llama` spawn
   mappings, and at what effort? This is the separate pre-existing routing item;
   the configuration plan deliberately does not choose for the owner.
2. Should a future change enforce `minimumOutputTokens` immediately on every
   local request, or keep it as resolved metadata until a request-level
   `max_tokens` cap is introduced? This plan records and exposes the floor but
   does not invent a cap that the current worker does not have.

## Risks / what could break

- `spawn_command()` currently bypasses `executor_config()` and reads
  `load_executors()` directly. If it is not moved to the shared seam, direct
  spawn commands can leak unresolved host placeholders while workflow spawns
  work.
- `workflow_spawn_command_for_prompt()` and `route_loop._model_verdict()` render
  commands independently. The resolver must return the same partially resolved
  canonical template to both; do not patch each renderer separately.
- `build_worker_spawn_env()` filters process variables. Overlay `baseUrl` must
  be installed with real-env-wins semantics before filtering, and
  `OPENAI_BASE_URL` must remain in `local-llama.envKeepList`.
- `_hop_usable()` currently treats the mere presence of
  `--keyless-hosts` as usable. It must consume the resolved authorization status
  so a mismatched base URL participates in failover instead of spawning and
  failing later.
- `openai_worker.py` treats an empty allow-host string as no allowlist. Resolver
  validation of non-empty `allowHosts` is security-critical.
- Raw-card consumers such as chat model selectors will no longer see
  `contextWindow` in `model-cards.json`. Any consumer that displays or budgets
  by it must deliberately request the resolved card; vendor-card reads must
  remain raw.
- Host normalization must handle case, IPv4, bracketed IPv6, trailing dots, and
  URL ports consistently. The allowlist stores hostnames only, matching
  `urlparse(...).hostname`; it must not store schemes or paths.
- Changing `OPENAI_BASE_URL` in the process can make a previously valid overlay
  authorization-mismatched. The resolved show and doctor warning are required
  so this is visible before a worker request.
- The helper is an operator-authorized network client. It must obtain the
  explicit host grant before its first request, use bounded timeouts, reject URL
  credentials, and never echo or persist the API key.
- A mutable hostname can resolve to a different address later; the existing
  worker control is hostname-based. Changing that to IP pinning is a separate
  security design, not something to smuggle into this configuration split.
- The current source no longer has `load_env_file`. Implementing the brief
  literally against that old symbol would either fail or accidentally restore
  the retired plaintext `.env` tier.
- The implementation touches egress and keyless authorization. It requires the
  repository's security review and focused SPEC-165 regression gates before
  landing.
