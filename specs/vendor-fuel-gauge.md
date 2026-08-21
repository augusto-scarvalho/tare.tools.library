# SPEC-168 — Vendor fuel gauge (gasômetro, N-VENDORCREDIT v1)

Status: SPEC-168, proposed 2026-07-22; **v1.1 amended 2026-07-27** — the gauge
pulls EVERY configured vendor, not only the two CLIs (acceptance:
`testing/scenarios/vf_vendor_fuel.py`).

## Goal

Give the harness a CANONICAL, machine-readable per-vendor "fuel gauge" —
`.harness/state/vendor-fuel.json` — populated by probing the NATIVE
non-interactive usage surface of each configured vendor. The state is
the load-bearing artifact: the GUI strip is only a reader, and the future worker
load-balancer (D017 / U-scarcity) is the real consumer. The gauge reports what
each vendor actually exposes and NEVER fabricates a number.

## Applicability

- `scripts/harness_lib/vendor_fuel.py` (probes + canonical state + the `fuel`
  verb, registered thin in `harness_lib/cli_registry.py`).
- `/api/state` `fuel` field (`harness_lib/ui_panel._fuel`, read-only, mtime-cached).
- The `EnvBudgetHealth` topbar strip (`ui/src/shell/EnvBudgetHealth.tsx` +
  `envbudget.css`, tiles via `ui/src/api/state.pickFuel`).
- Cadence surfaces (schedule + overseer loop) are DOCUMENTED for the owner; this
  spec does not implement a scheduler.
- **v1.1 (2026-07-27):** HTTP-only vendors (nvidia/gemini/openai-compat) and the
  402/quota backstop are now IN scope — `vendor_fuel.http_vendor_configs` +
  `probe_http`. Still out of scope: owner-declared balance, Admin/Usage-API cost
  reconciliation, and the worker load-balance router (see Ceilings).

## Requirements / invariants (numbered, testable)

1. **Canonical state shape.** `probe` writes `{schemaVersion: 1, vendors: {<name>:
   {kind, value, summary: {label, pct, detail}, capturedAt, probeMs, status,
   error?}}, updatedAt}`. `status ∈ {fresh, unavailable}` at write time; `stale`
   is DERIVED from `capturedAt` age (>2h) by readers.
2. **Never fabricate a number.** `summary.pct` is a real percent ONLY when the
   vendor exposes a percentualizable number; otherwise `pct` is `null` and
   `detail` carries the honest text. As of the 2026-07-23 correction (rule 6):
   claude DOES expose one non-interactively (`/usage` week-all-models) → real
   `pct`; codex does not (rule 7) → `pct` stays `null`.
3. **Atomic write.** The state file is written temp+rename (`common.write_json`);
   a probe leaves no `*.tmp` and never a torn document.
4. **No PII in canonical state.** `claude auth status` returns email/orgId/orgName;
   only `loggedIn/authMethod/subscriptionType/apiProvider` are whitelisted into
   `value`. PII is never stored or surfaced.
5. **Probe failure is honest, not fatal.** An absent CLI, a timeout
   (60s/vendor), a parse failure, or a logged-out session yields
   `status: "unavailable"` with an honest `detail`/`error` — never a crash, never
   an invented reading.
6. **claude surface (CORRECTED 2026-07-23, owner-caught).** The probe is
   `claude -p "/usage" --output-format json`: the `result` text renders the real
   subscription panel (session / week-all-models / per-model % USED + reset times),
   parsed to `pct = 100 - week-all-models-used` (the binding window; e.g. "week 23%
   left"). The v1 `pct=null` claim ("/usage is interactive-only") was WRONG — it was
   Git-Bash MSYS mangling `/usage`→a Windows path; via subprocess LIST args (no shell)
   `/usage` passes intact. COST: the probe pins the CHEAPEST model (`_PROBE_MODEL`, haiku
   — owner 2026-07-23) since `/usage` is CLI-rendered and the model does no work; measured
   cost_usd ≈ 0 (the default Fable turn had billed ~$0.37), so the cadence is no longer
   cost-constrained (per-heartbeat refresh is fine). Falls back to `auth status` liveness
   (`pct=null` + " (no usage panel)" detail) when `/usage` yields no panel. No PII: the
   parsed panel carries none.
7. **codex surface (pinned truth-gate).** The probe is `codex login status`
   (free, ~0.2s, written to STDERR). `codex exec --json` carries per-turn token
   usage but NO account rate_limits; the rate-limit footer is interactive ONLY, so
   `pct` stays `null` and `detail` carries the auth method.
8. **GUI is a pure reader.** The strip reads the `fuel` field of the SAME
   `/api/state` fetch it already makes; it NEVER triggers a probe. An
   `unavailable` vendor renders NO tile; a `pct` number renders a 4-segment meter;
   a `null` pct renders the text detail; a >2h-stale tile is muted with a
   "last probe HH:MM" title.

## Rationale & sources

| Decisão | Fontes |
|---|---|
| CLI-native `/usage`-style probe over an estimated tank | docs/research/vendor-credit-tracking-log.md incr.2 (owner idea); N-VENDORCREDIT/D017 |
| `pct` null when no real number exists (measure-honesty) | Codex half still holds (re-verified 2026-07-23: login status/doctor/exec all lack account usage). The claude half of the 2026-07-22 truth-gate was RETRACTED — see next row |
| `claude -p "/usage"` as the claude surface (SUPERSEDES the 2026-07-22 auth-status pin) | Owner-caught 2026-07-23: the "interactive-only" verdict was a Git-Bash MSYS path-mangle artifact; via subprocess list args the panel renders, and pinned to the cheapest model it costs ~$0. auth-status remains only the liveness fallback |
| `codex login status` as the codex surface | In-lane probe: free/~0.2s auth line on STDERR |
| Drop email/orgId from state | claude auth JSON carries PII; SPEC-130 secrets/config hygiene |
| Canonical machine-readable state, GUI as reader | Owner refinement 2026-07-22 (values feed future worker load-balance) |

## Gherkin scenarios (UI surfaces only)

```gherkin
Feature: Vendor fuel gauge on the environment strip

  Scenario: [vf-1] each vendor shows its honest reading — real gas or plain text
    Given the last probe captured a logged-in claude and codex
    When the supervisor looks at the environment strip
    Then the CLAUDE tile shows the real remaining-week percentage from /usage
    And the CODEX tile shows its tier text with no invented percentage bar

  Scenario: [vf-7] the heartbeat context carries the gas block
    Given a fresh vendor-fuel state exists
    When the overseer renders the reinjected checkpoint context
    Then a compact per-vendor gas block names each available vendor
    And an empty state yields no block at all (never a fabricated line)

  Scenario: [vf-4] an unavailable vendor shows no tile at all
    Given the last probe found a vendor logged out or absent
    When the supervisor looks at the environment strip
    Then that vendor contributes no tile (honest absence, no visual noise)

  Scenario: [vf-5] a gauge older than two hours reads stale
    Given the last successful probe is more than two hours old
    When the supervisor looks at that vendor's tile
    Then the tile is muted and its title names the last probe time

  Scenario: [vf-9] configuring a vendor is what puts it on the gauge
    Given an http executor declared in executors.json
    When the probe runs without being told which vendors exist
    Then that vendor appears in the canonical state beside the CLI vendors
    And only its allowlisted base-url host is dialled
    And its API key never reaches the stored state

  Scenario: [vf-10] an http vendor reports the one number it really has
    Given an openai-compatible provider with no balance endpoint
    When the probe reaches it
    Then the gauge shows reachability with no invented percentage
    And a provider answering 402 reads as a real zero, not as absence

  Scenario: [vf-11] the transport that runs in production is exercised
    Given a probe whose only live path is its own HTTP fetch
    When the acceptance run reaches a loopback provider
    Then the real fetch is what answers, not an injected stand-in

  Scenario: [vf-12] an expired usage window is never shown as a percentage
    Given the newest codex rollout is older than the staleness threshold
    When the supervisor reads the gauge before routing a lane
    Then no percentage is shown for that vendor
    And the reading says how old the underlying measurement is
```

## Ceilings (upgrade paths)

- **Numeric gauge: claude YES (since 2026-07-23), codex NOT YET.** Claude's real
  week-% ships via `/usage` (rule 6). The codex v1.1 door stays open: owner-declared
  per-vendor balance decremented by the delegation ledger, plus the 402/quota error
  as the vendor-truth backstop (docs/research/vendor-credit-tracking-log.md incr.1);
  or a codex non-interactive quota endpoint if one ever ships (re-verified absent
  2026-07-23). The GUI's meter path renders claude's real `pct` today.
- **A cache read is not a probe (v1.1, 2026-07-27).** The codex gauge reads the
  newest session rollout; when that rollout is older than `STALE_SECONDS` its
  percentage is from a window that may no longer exist, so the gauge reports
  `pct: null` with the measurement's real age instead. Measured that day: a 54h-old
  rollout reported `week 1% left · resets Jul 28` as `fresh` while the true value
  was 100%, and the wrong number had already cost a deferred day of work. `resets_at`
  cannot detect this — `now` was still before the dead window's advertised reset —
  so the rollout's AGE is the signal. `measuredAt` carries the underlying
  measurement time; `capturedAt` remains when the file was read, and the two are no
  longer conflated. Minting a fresh rollout costs one `codex exec` turn and stays an
  explicit escalation: `fuel probe` is documented as ~$0 and does not silently spend.
  (**Revised for kimi by v7, 2026-08-07:** the default probe now auto-mints a stale
  *kimi* — a bounded, self-throttled spend of ~1/100 request units — because its 1h
  token keeps that lane dark otherwise. Dollar cost stays ~$0; codex stays opt-in.)
- **HTTP vendors: reachability, not a tank (v1.1, 2026-07-27).** NVIDIA Build and
  Gemini publish no balance endpoint, so `probe_http` reports `pct: null` with an
  honest detail; the ONE real number is the provider's own 402, which lands as
  `pct: 0.0`. The vendor list is derived from `executors.json` — a vendor enters
  the gauge by being configured, never by editing a tuple in the module. The
  executor's own `--allow-hosts` / `--keyless-hosts` flags are re-applied by the
  probe: a gauge that dials a host the worker may not reach (SPEC-165 R6) would be
  measuring a lane that cannot run. Owner-declared balance decremented by the
  delegation ledger stays the v1.2 door.
- **The load-balance door.** The worker router reads `vendor-fuel.json` when
  D017 / U-scarcity lands; v1 only guarantees the canonical shape it will consume.

## Test strategy

- Behaviors to verify: fresh parse — claude real pct from the /usage panel, codex
  null pct + honest detail (vf-1); atomic write, schemaVersion, no tmp leftover
  (vf-2); cli-not-found → unavailable (vf-3); logged-out → unavailable with honest
  detail (vf-4); >2h → stale (vf-5); the CLI verb dispatches read-only (vf-6); the
  heartbeat gas block via `fuel_summary` — names fresh vendors, '' on empty state
  (vf-7). GUI render across pct-bar / text / stale / absent via the pw-smoke
  `fuel-gauge` check + `state.fuelSelfCheck`.
- Edge cases: PII stripped (vf-1); codex line on STDERR (vf-1 mock); empty/absent
  state file → empty scaffold (module self-check).
- Regression risks: the scenario MOCKS both CLIs via a PATH shim — no real vendor
  call in the gate; the ONE real-root call is read-only `fuel show`.
- Coverage impact: enforced via `vf_vendor_fuel.py` (+ `vendor_fuel._self_check`,
  `ui_panel._self_check` fuel assertion).

## Validation

- `python testing/scenarios/vf_vendor_fuel.py` — checks `vf-1`..`vf-7` (the Gherkin
  ids resolve here).
- `python scripts/harness_lib/vendor_fuel.py` — module self-check (parsers, PII
  strip, stale, atomic write; no real vendor call).
- GUI render: the `fuel-gauge` check in `ui/tests/pw-smoke.mjs` (driven by
  `testing/scenarios/pw_ui_smoke.py`) over the `?debug=envstrip` kitchen-sink;
  `npx tsc -b --noEmit` green.
- `spec-pack` gate green (this file's template conformance + Gherkin mapping).

## Amendments

### v2 (2026-07-23) — codex session-rollout gauge (owner-corrected)

The v1 "codex exposes no non-interactive usage surface; pct stays null"
finding is OVERTURNED (third overturned codex claim of 2026-07-23). New
rules:

- **R-v2.1 rollout surface.** `probe_codex` reads the newest
  `~/.codex/sessions/Y/M/D/rollout-*.jsonl` LAST `rate_limits` event
  (depth-tolerant key walk): `pct = 100 - primary.used_percent`;
  detail carries the window label (10080min = week), reset time, rollout
  age, and auth method. Zero model cost — a file read.
- **R-v2.2 honesty unchanged.** No rollout on disk -> pct null with
  "(no session rollout yet)"; nothing fabricated. The cheap refresh
  escalation is ONE `codex exec --model gpt-5.6-luna -c
  model_reasoning_effort=low` turn (mints a fresh rollout), never the
  sol default.
- **R-v2.3 hermeticity.** `HARNESS_CODEX_HOME` overrides the home for
  scenarios (vf-8: fixture rollout 84% used -> pct 16, last event wins).

| Decisão | Fontes |
|---|---|
| Rollout como superfície do gauge | owner challenge 2026-07-23 + rollout inspection: rate_limits used_percent 84-85/window 10080 nos lanes reais do dia |
| luna-low como refresh, não default | cost lesson v1 (bare codex exec = sol high, turno cheio) |

### v3 (2026-07-28) — kimi /usages gauge + all-or-nothing probe (owner rule)

Two same-day changes as the kimi vendor landed (SPEC-165 v3/v4):

- **R-v3.1 kimi surface.** `probe_kimi` reads `GET /coding/v1/usages` with the
  CLI's local OAuth token (endpoint surfaced by the community tracker
  Golden0Voyager/kimi-code-usage; MoonshotAI/kimi-cli#2169 confirms the CLI
  itself is TUI-only). pct = weekly remaining% (binding window); detail adds
  the 5h window, reset and membership. 401 stale-token stays FRESH/pct-null
  with a refresh hint (any kimi turn re-mints); no token -> `--version`
  liveness; userId/businessId PII-stripped. Hermeticity: `HARNESS_KIMI_HOME`
  plus injected getter (vf-13).
- **R-v3.2 all-or-nothing probe.** Owner rule 2026-07-28: gas updates happen
  for EVERY vendor in one synchronized pass — one sequential probe, one atomic
  write, one `updatedAt`. The `--vendor` partial probe is REMOVED: it wrote a
  fresh state containing only the filtered vendor (clobbering every other row)
  and let readings age hours apart, which skews the R13 gas balancer's
  cross-vendor comparison. Cross-vendor skew is now bounded by the pass
  duration (seconds); staleness ages all rows together.

| Decisão | Fontes |
|---|---|
| /usages como superfície kimi | medição 2026-07-28 (200 com janelas weekly/5h/parallel) + kimi-code-usage + kimi-cli#2169 |
| probe all-or-nothing | dono 2026-07-28 ("sempre em sincronia"); clobber medido no code-read de probe_all(vendors=...) |

### v4 — atividade local do codex + metadados de conta (2026-07-31)

O dono reportou que o codex nao mostra a janela de 5h e supos que ela chegava
sob outro nome. **Medido antes de responder**: nos 6 rollouts mais recentes,
199 eventos `rate_limits`, TODO `secondary` e null e o unico `window_minutes`
que existe e 10080 (`plan_type: "plus"`). O codex desta versao/plano nao publica
janela curta. O `gas %` da gaveta e a MESMA semanal com nome generico, nao a de
5h renomeada — o contraste esta na mesma tela: claude mostra `5h`/`wk`/`fable`
porque o probe dele escreve tres janelas reais.

O que muda, entao, e o que se mostra no lugar do vazio:

1. `value.activity` traz ATIVIDADE LOCAL MEDIDA por janela rolante (300/1440/
   10080 min): `{windowMinutes, totalTokens, turns}` somados dos rollouts desta
   maquina. Nao e cota, nao e consumo da conta, nao e custo. A alegacao e
   exatamente "tokens vistos nos rollouts locais nesta janela".
2. Soma `last_token_usage`, NUNCA `total_token_usage` — o segundo e cumulativo
   por sessao e dobraria a contagem de todo turno. Eventos sao deduplicados por
   timestamp.
3. NENHUM percentual e derivado. Da para inferir um orcamento semanal a partir
   de `used_percent` e dividir, e isso imprimiria uma porcentagem que o vendor
   nunca disse — proibido pela lei desta spec e pelo comentario que abre
   `FuelCarousel.tsx`.
4. COTA REAL VENCE POR DURACAO: a semanal real suprime a linha de 7d de
   atividade; no dia em que o codex voltar a emitir a de 5h, a linha de 5h de
   atividade some sozinha. Atividade nunca substitui, sombreia ou alimenta
   `summary.pct`.
5. Atividade vive so na GAVETA, com rotulo `local activity — not quota`, sem
   `%`, sem barra, sem reset. O tipo `FuelActivity` nao tem campo `pct`, entao
   e estruturalmente incapaz de chegar ao medidor. A faixa fixa (347px) e o
   breakpoint (1364px) ficam intocados.
6. CUSTO LIMITADO: so arquivos com mtime >= o corte mais antigo sao ABERTOS, e
   cada um e lido uma vez alimentando os tres acumuladores. Medido no corpus
   local: 179 rollouts, 74 elegiveis para 7d, ~78ms de varredura contra ~8ms da
   leitura de cota. O `fuel probe` roda no topo de toda rodada de loop, entao o
   limite e a feature.
7. Numero formatado em idioma FIXO (`19.0M`), nao `Intl` compact: este ultimo
   formata na locale de quem olha e a mesma leitura saia `19 mi` em pt-BR
   (pego pelo dente). Leitura de maquina nao muda de forma com o observador.
8. Tambem passam a ser preservados, verbatim e sem interpretacao: `planType` e
   `credits {has_credits, unlimited, balance}`. `balance: "0"` e o que o vendor
   disse sobre creditos, que sao pote separado — nao significa assinatura
   esgotada. `model_context_window` fica de fora (nao e combustivel).
9. Escopo CODEX-ONLY, por disponibilidade de dado e nao por simetria: claude
   expoe janelas agregadas via /usage e kimi via /usages, nenhum dos dois retem
   log de evento por turno como o rollout do codex.

CORRECAO DE REGISTRO: o comentario em `_codex_rollout_limits` afirmava que o par
5h/semanal fora "MEASURED locally". Nao foi — `secondary` e caminho de
compatibilidade (versoes antigas do codex emitiam o par, e la os slots invertem).
O texto foi corrigido junto.

Validation: `vf-21` (matematica da atividade: dedup, `last_token_usage`, fora
da janela descartado) e `vf-22` (custo: arquivo fora do corte NAO e aberto) em
`testing/scenarios/vf_vendor_fuel.py`; `fuel-codex-activity` em
`ui/tests/pw-smoke.mjs` (rotulo, supressao pela cota real, zero medidores);
`fuelSelfCheck` em `ui/src/api/state.ts` (precedencia nas tres formas e descarte
de linha malformada). `vf-19`/`vf-20` seguem como dentes de compatibilidade para
o dia em que o par real voltar.

### v5 — slots padronizados + percentual DERIVADO marcado (2026-07-31)

Supersede as regras de v4 que proibiam qualquer percentual derivado. O dono pediu
padronizacao COM barra e aceitou explicitamente a premissa da derivada ("ja entendi
as implicacoes"). O que muda:

1. TODO vendor renderiza os MESMOS slots na MESMA ordem — `5h`, `wk`, e depois as
   janelas extras que aquele vendor realmente publica (a per-modelo do claude
   mantem seu lugar depois das duas). O olho compara por POSICAO.
2. Quatro estados, distinguidos por FORMA e nunca por cor sozinha:
   `published` (celula solida), `derived` (celula oca/tracejada, texto italico e
   `*`), `not-published` (celula pontilhada, `n/p`), `stale` (hachurada, `stale`).
   Um `0%` PUBLICADO e um medidor solido vazio — estruturalmente diferente da
   lacuna pontilhada, porque "esgotado" e "o vendor nao diz" sao fatos opostos.
3. DERIVADA (so codex 5h, so quando a semanal e publicada, a atividade tem os dois
   totais e NAO existe janela de 5h real):
   `orcamento_semanal_implicito = tokens_locais_7d / (uso_semanal_publicado/100)`
   `pace_5h = 100 * tokens_locais_5h / orcamento_semanal_implicito`
   O rotulo visivel diz DE QUE ela e fatia — `pace ~17% of wk` — e NUNCA "left"
   ou "quota": o vendor jamais declarou cota de 5h, entao "5h 93% left" seria
   mentira e nao aproximacao.
4. A ARITMETICA COMPLETA e a premissa ("vale so se todo o consumo da conta passar
   por esta maquina") vivem no TOOLTIP do `*`, nunca inline ao lado do numero
   (dono 2026-07-31: "não coloca textão gigante inline com os dados"). No terminal,
   que nao tem hover, ela vira NOTA DE RODAPE depois da tabela.
5. REAL VENCE DERIVADA por duracao: publicada a janela verdadeira, a derivada some
   naquela duracao. Nao existe caminho de codigo onde as duas coexistem.
6. Vendor stale mantem os slots em estado stale com a frase do PROPRIO probe no
   tooltip — nunca a faixa careca (dono: "kimi também padronizado, não mostra barra
   careca").
7. `harness.py fuel show` renderiza os mesmos slots em ASCII, com a forma carregando
   o estado (`#` publicado, `o` derivado, `.` nao publicado, `x` stale) — sem
   depender de cor. Modo compact emite TSV por SLOT (`vendor/slot/state/bar/reading`).

Base no DESIGN_SYSTEM: a emenda §6 v2 ("derivado != fabricado") define as quatro
condicoes que tornam um numero calculado legal; esta spec e a primeira consumidora.

Validation: `vf-23` (slots iguais e ordenados; lacuna e stale desenhados), `vf-24`
(derivada: formula, rotulo sem "left/quota", real vence, sem denominador vira lacuna)
e `vf-25` (formas ASCII distintas, `0%` publicado != lacuna) em
`testing/scenarios/vf_vendor_fuel.py`; `fuel-slot-standard` (ordem, italico, `*`,
aritmetica no TOOLTIP e nao inline), `fuel-kimi-stale-notice` (slots stale, nao
carequice), `fuel-codex-pair` (ordem padrao) e `fuel-topbar-fit` em
`ui/tests/pw-smoke.mjs`; `fuelSelfCheck` em `ui/src/api/state.ts`.

### v5.1 - a padronizacao vale para vendor METERED, nao para API de inferencia (2026-07-31)

Correcao de ESCOPO do v5, no mesmo dia. O item 1 dizia "TODO vendor renderiza os
MESMOS slots" sobre a lista que `all_vendors` devolve - e ela inclui os executores
`type: http` (gemini-compat, nvidia-compat, local-llama). O terminal passou a imprimir
`5h [..........] not published   wk [..........] not published` para provedores que NAO
tem janela de cota e nunca terao. Isso e o oposto da lei que o proprio v5 defende: a
lacuna pontilhada AFIRMA "o vendor ainda nao disse", quando o fato e "nao existe o que
dizer". O v1.1 ja tinha a regra certa ("HTTP vendors: reachability, not a tank") e o v5
a atropelou ao generalizar sobre uma lista de duas classes diferentes.

1. Slots padronizados = vendors com assinatura MEDIDA (claude, codex, kimi). Um endpoint
   de inferencia nao recebe slot nenhum - `vendor_slots` devolve `[]` para ele.
2. A classe vem do TRANSPORTE, nunca do nome: `probe_http` carimba `baseUrl` em toda
   linha que escreve (fresh ou unavailable, podendo ser ""), e nenhum vendor CLI carrega
   a chave. `vendor_fuel.is_api_vendor` e o mesmo discriminador que a GUI ja usava desde
   v1.1. Um provedor renomeado amanha continua classificado certo, e a API LOCAL entra na
   regra de graca por ser `type: http` - nao ha lista a manter.
3. Linha de API no terminal: registro proprio `api`, o status quando nao e `fresh`, e a
   FRASE DO PROPRIO PROBE ("reachable - 59 models - quota not exposed"). Sem barra e sem
   percentual inventado. O unico numero real que essas APIs produzem continua sendo o 402
   do provedor (creditos zerados), que vira `pct: 0.0` desde v1.1. Modo compact mantem as
   cinco colunas do TSV com slot `api` e bar `n/a`.
4. GUI: aparencia inalterada (as APIs sempre viveram no grupo `ApiSlide`, ponto + nome +
   detalhe no tooltip), mas `pickFuel` deixa de CALCULAR slots para elas - dado morto que
   um render futuro poderia ressuscitar como barra.

Base no DESIGN_SYSTEM: a emenda "a lacuna tambem e uma afirmacao" (secao 6) generaliza a
licao - padronizar forma so vale dentro da mesma classe de coisa medida.

Validation: `vf-27` em `testing/scenarios/vf_vendor_fuel.py` (api sem slots nos dois
modos do CLI, vendor CLI mantendo os seus, discriminador por transporte e nao por
sufixo de nome); `fuel-carousel` em `ui/tests/pw-smoke.mjs` (a slide de API nao contem
`.ebh-win` nem `.ebh-meter`, checado no ciclo que ja exige alcancar essa slide);
`fuelSelfCheck` em `ui/src/api/state.ts` (tile api com zero slots, metered com os seus).

### v5.2 - a tira de APIs vira celulas delimitadas, e corre quando nao cabe (2026-07-31)

Dono, olhando a slide de API: "nao gosto muito de como as bolinhas de status e os nomes
estao espacados, da pra confundir se o status ta relacionado ao item da esquerda ou
direita". Era ambiguidade real: com gap uniforme entre bolinha e nome e entre um servico
e o proximo, a proximidade nao dizia a quem a bolinha pertencia.

1. Cada servico e uma CELULA delimitada - `| * GEMINI | * NVIDIA 0% | * LOCAL-LLAMA |`.
   O espaco saiu do meio (gap) e foi pra DENTRO da celula (padding), e uma regra de 1px
   em `--border` fecha cada uma. Proximidade e traco passam a dizer a mesma coisa; a tag
   `API` tambem ganha sua divisoria e vira a parede esquerda da primeira celula.
2. Quando as celulas ultrapassam a caixa FIXA (347px), a tira CORRE em laco continuo em
   vez de cortar um provedor pra fora da vista: a lista e renderizada duas vezes e o
   trilho anda exatamente a largura de UMA lista, entao a emenda ultimo->primeiro e
   invisivel. Cabendo, nao existe animacao nem copia no DOM.
3. As quatro condicoes da lei de marquee do DESIGN_SYSTEM (secao 5) valem aqui: corre so
   por MEDICAO (`scrollWidth` da primeira lista vs `clientWidth` do viewport, medido num
   layout-effect que le so a lista original - medir o trilho realimentaria o proprio
   resultado); a copia e `aria-hidden`; hover pausa (o mesmo gesto que ja pausa a
   rotacao); e `prefers-reduced-motion` desliga o laco - ali a gaveta continua sendo a
   lista completa e parada. Duracao = largura medida / 24px por segundo, inline, nunca
   um numero escolhido.
4. Enquanto corre, um fade de 6px nas duas bordas (mascara alpha com `currentColor`, sem
   literal de cor no arquivo) faz a celula que entra/sai ler como viagem, e nao como
   glifo cortado por uma borda dura.

Validation: `fuel-api-strip` em `ui/tests/pw-smoke.mjs` sobre dois fixtures api-ONLY do
kitchen-sink (3 servicos = cabe: uma lista, `animation-name: none`; 6 servicos = corre:
duas listas, `ebh-api-marquee`, duracao > 0, copia `aria-hidden`), com a divisoria de
cada celula checada por `borderRightWidth` em ambos. O nome do dente esta na lista que
`testing/scenarios/pw_ui_smoke.py` exige presente, entao apaga-lo falha em vez de
encolher a contagem em silencio.

### v6 (2026-08-06) — antigravity (agy) gauge via o painel `/usage` do TUI, headless

O dono pediu um gasometro pro agy. **Investigado antes de responder** (as tres vias que
usamos pros outros vendors, da mais barata pra mais cara): (a) NAO ha subcomando de usage
no CLI (`agy --help`, v1.1.10: só agent/models/plugin/update/...); (b) `agy -p "/usage"`
NAO executa o slash em print mode — trata como PROMPT e o modelo ALUCINA a resposta,
gastando um turno real; (c) NAO ha arquivo de cota persistido — o `quota_manager` do agy
busca da Google Code Assist API (OAuth) e cacheia so em memoria. O `/usage` REAL existe,
mas roda unicamente no TUI interativo (o dono corrigiu a rota, com print — o comando
mostra "View model quota usage"). Regras:

- **R-v6.1 superficie = o painel `/usage` do TUI, dirigido HEADLESS.** `_drive_agy_usage`
  sobe o agy num pseudo-console (pywinpty/ConPTY, ja no venv), ACEITA o prompt de
  folder-trust do cwd descartavel (dir temp vazio — regra do mint-turn, sem capsula de
  projeto), executa `/usage` e raspa o painel "Models & Quota". Signal-driven (espera por
  sinais no buffer, nao relogios fixos). BOUNDED de tres formas pra nunca pendurar o
  `fuel probe`: timeouts por-espera, uma thread WATCHDOG de deadline ABSOLUTO
  (`_AGY_HARD_CAP_S`) que mata o filho mesmo se o fluxo (ou o proprio PtyProcess) travar,
  e `terminate(force=True)` no finally. `_strip_ansi` drena escapes de 2 bytes (ESC 7/8/c…)
  ANTES do passe de C0, senao o ESC solto e removido e o parceiro (`\x1b7`->`7`) corromperia
  um digito de cota adjacente. Nunca levanta.
- **R-v6.2 modelo da SONDA x janela vinculante.** A SONDA usa o modelo mais barato
  (`gemini-3.6-flash-low`) — o painel `/usage` renderiza igual em qualquer modelo e NAO
  custa turno (e painel do CLI, nao inferencia). A janela VINCULANTE, porem, e o GRUPO
  inteiro "GEMINI MODELS" (Flash + Pro dividem uma cota), que e tambem de onde o seat de
  PRODUCAO do R9 (`gemini-3.6-flash-high`) puxa — logo a leitura vale pra ambos. 5h +
  semanal REMAINING% do grupo entram nos slots padrao (forma do codex, `rateLimits.windows`),
  `pct = min(5h, semanal)` (regra do kimi). "Quota available" sem numero -> 100%.
- **R-v6.3 ilegivel -> UNAVAILABLE, nunca fabrica.** Painel ilegivel (pywinpty ausente /
  nao logado / timeout / layout mudou / grupo GEMINI ausente) -> linha `unavailable` com
  detalhe honesto e `error: usage-unreadable`; NADA de leitura fabricada. A linha some das
  superficies que a leem por vendor: a GUI pula `unavailable && !api` (`pickFuel`) e o
  heartbeat (`fuel_summary`) descarta `unavailable` — nenhuma delas desenha gaps 5h/wk pra
  ela. (O `fuel show` do CLI, como pra QUALQUER vendor CLI unavailable, ainda imprime a
  linha com slots `not-published`; e comportamento pre-existente do carrossel, nao
  especifico do agy.) Sem estado `reading-only` novo: o gauge ou le numeros reais ou se
  declara indisponivel — mais simples que a reachability-de-consolo que um rascunho tinha
  (removida junto com
  `is_reading_only`, apos o audit apontar que a GUI classificava reading-only so por
  `baseUrl` e desenharia gaps pra uma linha `noQuota`).
- **R-v6.4 sem PII, TUI-scrape e fragil.** So os `windows` parseados chegam ao estado
  canonico — nunca o texto do painel nem o email da conta (regra 4 / disciplina de PII).
  O scrape e inerentemente sensivel a versao do agy, entao o PARSER e fixado num fixture
  capturado (`testing/fixtures/agy_usage_panel.txt`, email redigido) pra um drift de
  layout falhar ALTO, nao em silencio.

| Decisão | Fontes |
|---|---|
| `/usage` do TUI como superficie (nao CLI/arquivo/print) | investigacao 2026-08-06: `agy --help` sem usage; `-p /usage` mede turno alucinado; cli.log `quota_manager`/`cache.go loadCodeAssistResponse` = cache em memoria via OAuth; dono corrigiu com print do menu `/usage View model quota usage` |
| sonda em `-low`, mas grupo GEMINI vincula | painel renderiza igual em qualquer modelo (nao custa turno); o grupo (Flash+Pro) e cota compartilhada, e o seat de producao R9 spawna `gemini-3.6-flash-high` do MESMO grupo |
| ConPTY headless via pywinpty | agy slash so executa em TTY real; `winpty` CLI recusa stdin nao-tty; pywinpty 3.0.5 ja no venv |
| ilegivel -> unavailable (nao reachability) | audit 2026-08-06: a GUI (`state.ts`) classifica reading-only so por `baseUrl`, entao uma linha `noQuota` fresh desenharia gaps 5h/wk — `unavailable` degrada honesto SEM tocar a GUI |
| cadencia = espelha o claude | probe caro fica no `fuel probe` (round-open, sparse); heartbeat le o cache |

Validation: `vf-28` (parser fixado no fixture real — grupo GEMINI 99.2/99.21 + refresh,
grupo CLAUDE/GPT "Quota available"->100 pelo branch sem-`%`; `_strip_ansi` drenando um escape
de 2 bytes `9\x1b79.2%`->`99.2%`; probe com driver injetado -> pct 99.2, slots 5h/wk
`published` com os %) e `vf-29` (ilegivel: driver None e painel sem grupo GEMINI ambos ->
unavailable/`usage-unreadable`, value vazio, sem crash) em `testing/scenarios/vf_vendor_fuel.py`;
`_self_check` do modulo cobre o gauge (driver mockado) e o degrade unavailable. CEILING:
substituir o TUI-scrape por um endpoint real no dia em que agy ou o Google Code Assist
expuser cota nao-interativa (o `quota_manager` ja a busca por OAuth).

### v7 (2026-08-07) — the default probe auto-mints a stale kimi (owner-caught)

Revises the v1.1 invariant "`fuel probe` does not silently spend" and the 2026-07-30
"round-open stays mint-free" call, for **kimi only**. Owner-caught: the fuel system
kept routing off a rotten kimi token to economize and never refreshed it, so the kimi
lane read `401`-stale on nearly every probe and was never routed to — the "economy" was
costing the entire lane. kimi's oauth token is a 1h token (R-v3.1 / `_kimi_expired_for`,
measured), so a passive gauge is stale far more often than not.

- **R-v7.1 default path auto-mints a stale kimi.** When a pass leaves kimi with a
  `401` token-stale row (`_needs_mint`), the DEFAULT probe runs one bare kimi mint
  turn, then ONE clean re-pass that reads the fresh token. Blast radius = every
  default `probe_all`: the CLI `fuel probe`, the GUI `fuel-probe` (same verb), AND
  the audit-leg re-probe seam (`audit_leg` seats executors off the default probe when
  the fleet reads dark). BOUNDED: a kimi mint costs ~1/100 request units and
  SELF-THROTTLES to ~1x/h ON SUCCESS — the minted token stays valid 1h, so probes
  inside that window read it and skip the mint. Dollar cost stays ~$0 (kimi quota
  units, not dollars); `~$0` in the heartbeat block still holds. The mint notice
  prints to STDERR, never stdout — the payload stream (`--json`, compact TSV, the
  audit-leg JSON) stays clean (the TSV/JSON boundary contract).
  **Failure ceiling:** the self-throttle holds only on mint SUCCESS; a FAILED mint
  has no cooldown, so a present-but-wedged kimi CLI is retried on every default probe
  (each attempt hard-capped at `MINT_TIMEOUT_S`; the common dead-token case fails
  fast, rc!=0). Add a `lastMintAttempt` cooldown in the kimi row if that measurably
  hurts round-open cadence.
- **R-v7.2 kimi ONLY; codex stays --mint opt-in.** `_mint_targets(stale, mint, auto)`
  is the pure selector: `--mint` mints every `_needs_mint` vendor (unchanged);
  the default path mints kimi only. codex is excluded — its mint burns a ChatGPT turn
  and its staleness is rollout AGE, not a clock, so it has no 1h self-throttle and would
  mint on every round. The re-pass carries `_auto=False` so a refreshed kimi is never
  minted twice (no loop).
- **R-v7.3 honesty unchanged.** A failed/hung mint keeps the honest stale row with no
  re-pass; a logged-out kimi (no token at all) is never minted — it would hang on a
  login prompt, and `_needs_mint` already excludes it.

Validation: `vf-17` updated — the default path mints kimi ONCE and never codex, forced
hermetically via a stale-token home + mocked `_http_get` (probe_all calls
`probe_kimi(path)` without the getter); `_mint_targets` branches pinned in the module
`_self_check`.

| Decisão | Fontes |
|---|---|
| default auto-minta kimi, codex fica opt-in | dono 2026-08-07: token de 1h deixa a lane do kimi sempre podre; mint ~1/100 unidades e auto-limitado a ~1x/h; codex queima turno ChatGPT sem esse throttle |
