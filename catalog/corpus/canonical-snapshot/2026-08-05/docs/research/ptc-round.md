# Rodada de pesquisa — Programmatic Tool Calling (PTC) + fronteira de tool-calling

Owner 2026-07-19: pesquisa ampla (NVIDIA + Sonnet 5 HIGH) sobre PTC — como o harness e os repos se
beneficiam (foco em LATÊNCIA, EFICIÊNCIA, CONSUMO DE TOKENS); como implementar em vendors diferentes
+ OpenAI-compatible (open-weights) + a PARIDADE; e varrer a FRONTEIRA do conhecimento de tool-calling
e encaixar no PTC + no tool-calling tradicional que já temos. Orquestrador = esta sessão.

## O que é PTC (o enquadramento)
Tool-calling TRADICIONAL: o modelo emite UMA chamada por vez → round-trip ao modelo por chamada; o
resultado (mesmo enorme) volta pro contexto do modelo a cada passo. **PTC:** o modelo escreve CÓDIGO
que ORQUESTRA várias tools programaticamente (loop/filtro/composição) num sandbox; os resultados
intermediários ficam no sandbox, não re-alimentam o modelo. Ganho: menos round-trips (latência),
menos tokens (o output grande não volta ao contexto), mais eficiência (o modelo filtra/agrega em
código antes de decidir). Anthropic (code execution / tool-as-code), OpenAI (code interpreter +
function calling) já shippam; open-weights (glm/llama) geralmente NÃO têm nativo → o harness provê.

## O que o harness JÁ tem (o substrato)
- **Sandbox SPEC-151** (`sandbox_spawn.py`: fs-confine + Job Object + tier) — o substrato de execução
  pra rodar o código que o modelo emite. É a peça-chave da paridade (open-weights sem code-exec nativo).
- **Cadeia discover** (`discovery.py`: Gemini→NVIDIA pra bulk text/image) + **Graphify** (code-AST) —
  orquestração de leitura em massa = o caso de uso-MÃE de PTC (uma chamada de código itera N reads).
- **5 executors** (`executors.json`: claude/codex CLI, openai-compat/nvidia-compat/gemini-compat HTTP)
  — a superfície de PARIDADE onde o PTC tem que funcionar igual.
- **Adapter-conformance** (T-ADAPTERCONF, `accountingSemantics`, trust tiers) — a disciplina de paridade.
- **Model economy + delegation ledger** — o DNA de custo/token que o PTC otimiza.
- **MCP** (`capabilities_view.py`, capabilities.json) — as tools expostas.

## A pergunta
> Como o harness (e os repos onde trabalhamos) se beneficiam de PTC — quantificando LATÊNCIA,
> EFICIÊNCIA e CONSUMO DE TOKENS? Como IMPLEMENTAR PTC across vendors (Anthropic/OpenAI nativos) E
> OpenAI-compatible open-weights (que não têm nativo), com PARIDADE? E o que a fronteira de
> tool-calling (novos assuntos) traz que encaixa no PTC e no nosso tool-calling tradicional?

## Sub-perguntas
1. **Onde PTC ganha no harness:** quais fluxos (discover bulk, graphify, fan-out de workflow, leituras
   em massa, reduce) cortam round-trips/tokens com PTC? Quantificar o ganho esperado.
2. **O mecanismo:** como o modelo emite código que chama as tools do harness (verbos harness.py, MCP)
   e roda no sandbox SPEC-151; o que expõe as tools como funções; como os resultados voltam (só o
   filtrado). Determinístico e seguro (o sandbox contém).
3. **Paridade cross-vendor:** vendors com code-exec NATIVO (Anthropic/OpenAI) vs open-weights (glm/
   llama via nvidia/openai-compat) que NÃO têm → o harness roda o código emitido no próprio sandbox
   pra dar a MESMA capacidade. Como o adapter-conformance/accountingSemantics cobre isso.
4. **Segurança:** PTC = o modelo escrevendo código que executa → conecta ao sandbox (SPEC-151) + ao
   RD-TAINT (D023, secret nunca egressa) + ao secret-scan. O que o código emitido PODE tocar.
5. **Fronteira (Flow A web):** MCP, tool-search/RAG-sobre-tools (quando há muitas tools), parallel
   tool calling, computer-use, structured outputs, tool-result caching, "tools as code" — o que é
   novo, e como cada um encaixa no PTC vs no tradicional.

## Critérios (DNA do harness)
- **Measure-before-control:** o ganho de latência/token de PTC é MEDIDO (baseline tradicional vs PTC
  na mesma tarefa), não afirmado. Reusa o delegation ledger + accountingSemantics.
- **Paridade real:** o mesmo comportamento across executors, com o adapter-conformance verificando.
- **Segurança:** o código emitido roda contido (sandbox); secret não egressa (RD-TAINT).
- **Anti-fabricação:** citação → fonte + data (a fronteira é web, marcar `[web]` untrusted-até-verificar).
- **Reusa** sandbox + discover + executors + MCP — não um runtime paralelo.

## Ondas
- Onda A (NVIDIA, 5): design/reasoning — mecanismo PTC no harness, reuso do sandbox, abstração de
  paridade, onde ganha latência/token.
- Onda B (Sonnet 5 HIGH, 3, COM WebSearch): fronteira web — (1) estado-da-arte de PTC across vendors
  + evidência de ganho latência/token; (2) implementação de paridade (nativo vs sandbox-side pra
  open-weights); (3) fronteira de tool-calling (MCP/tool-search/parallel/computer-use/…) + o fit.

## Convergência (Fase 5)
Isolar: onde PTC ganha (quantificado), o mecanismo (sandbox + tools-as-funções), a abstração de
paridade cross-vendor, os controles de segurança, e o mapa da fronteira → PTC/tradicional. O que é
buildável já (um probe measure-only latência/token PTC-vs-tradicional numa tarefa) vs o motor
(owner-gated). Sintetizar em desenho + incrementos de backlog + citações verificáveis.

---

# Fase 5 — convergência (4 ondas: NVIDIA 5 + 3 Sonnet 5 high com WebSearch)

## O que é + o win (unânime)
PTC = o modelo emite CÓDIGO que orquestra tools num sandbox; resultados intermediários ficam LOCAIS
(não re-alimentam o contexto); só o filtrado volta. Win = menos round-trips (LATÊNCIA, 1:1) + menos
TOKENS (output grande não volta). **Não-linear com o tamanho do result-set.** Analogia mais apertada
(NVIDIA w-005): **database query pushdown** (MapReduce/Spark) — empurra o código imperativo pra onde
o dado está, linhas intermediárias ficam no worker-node, só o agregado retorna; PTC-code = UDF.

## O REFRAME que muda o desenho (onda paridade — load-bearing)
"Nativo vs sandbox" é a pergunta ERRADA. O protocolo pause/resume (Anthropic, lido no doc primário):
a execução pausa em CADA tool_use, volta pro NOSSO servidor, NÓS rodamos a tool, devolvemos. **O
corpo das tools SEMPRE roda no nosso lado**; o container do vendor só segura o LOOP de orquestração.
→ **Rotear o loop pelo NOSSO `sandbox_spawn` por padrão pra TODO executor** (inclusive claude);
container nativo = opt-in. Ganha conformance/taint/accounting uniformes.

## Fit no harness (onde ganha)
- **Substrato:** o sandbox SPEC-151 JÁ é o que PTC precisa. Camada fina (NVIDIA w-001): um módulo
  `harness_tools` de funções (assinatura Anthropic `dict → str` async) injetado no namespace do
  sandbox; o modelo emite UM script; só o `stdout` filtrado volta.
- **Fluxos de maior ganho:** a cadeia **discover bulk** (o caso-MÃE), o **reduce/fan-out** do
  workflow, os **graphify bulk** — muitos reads → um script. (Fork-join JÁ é parallel-calling na
  orquestração; PTC = o loop IN-TURN de UM worker.)

## Paridade cross-vendor
- **CodeAct (arXiv:2402.01030, ICML 2024)** = a raiz acadêmica + o COMPORTAMENTO portável (+20%
  success vs JSON). Infra de PTC HOSPEDADA = só 2 vendors: **Anthropic (nov/2025, Python)** +
  **OpenAI (GPT-5.6, 2026-07-09, JavaScript/V8)** — MESMO `allowed_callers` (indústria convergindo).
  **A premissa da rodada mudou em pleno voo** (o round doc assumia OpenAI só com code-interpreter).
- **Open-weights (glm/llama/deepseek/qwen/mistral + NVIDIA-NIM)** = SEM PTC hospedado nativo →
  **emulado pelo loop do NOSSO sandbox**: prompt-contract (assinaturas + 1 bloco ```python) →
  code-extraction determinística (reusa o idiom de `HARNESS_RESULT`) → **gate AST estático ANTES de
  executar** (reusa o `ast.walk` do `sandbox_spawn.evaluate_chokepoint`) → `sandbox_spawn(bounded)`
  com o namespace injetado → só o filtrado volta. Buildável model-agnóstico (LangChain Open PTC,
  Cloudflare Code Mode, HF smolagents provam).

## Segurança (ondas trust — 2 achados fortes)
- **🔒 O 4º SINK DE TAINT (novo, sobre o D023):** o D023 lista 3 sinks (prompt/result-persistido/log).
  PTC abre um QUARTO: o **stdout/stderr do sandbox** (volta pro modelo por design). Um secret
  `print()`-ado no script atravessa SEM tocar os 3 sinks → **o check de taint tem que rodar no stdout
  capturado do sandbox** ou PTC reabre o buraco do D023. Um call-site a mais no envelope existente.
- **Lethal-trifecta (Willison):** PTC colapsa "dado-privado + conteúdo-não-confiável + egresso" num
  script só, removendo o checkpoint natural per-call → invariante NOVO: um namespace de stub não
  combina stub-que-lê-secret + stub-com-egresso sem `declares_egress` + o 4º-sink ativo.
- Stubs `dict → str` só (NUNCA `run_shell(str)` — fecha a classe de command-injection por construção);
  ausência dos builtins perigosos no namespace (backstop do gate AST); `HARNESS_SANDBOX_OVERRIDE`
  inalcançável de dentro do código emitido. O return filtrado = o único chokepoint de confiança.

## Novas classes de falha (NVIDIA w-003)
- **Partial-batch:** falha do script perde o BATCH inteiro (retry per-call é granular; PTC não) →
  checkpoint/resume DENTRO do sandbox.
- **CPU-time = eixo de custo NÃO-rastreado:** PTC troca token por COMPUTE → medir o CPU do sandbox.
- **Liveness:** script travado não produz turn do modelo → detecção de timeout.
- **Accounting blind-spot:** o ledger não vê tool-calls internos ao sandbox → fechar.

## Conformance / accounting (T-ADAPTERCONF)
Nova capability `programmatic-tool-calling` com `supportState` (claude/openai=native, resto=emulated).
- **c9 `ptcTokenScope`** (novo sub-campo): a Anthropic DESCONTA os tokens de tool-result nativos → um
  comparativo naive de "tokens billed" native-vs-emulated favorece o claude por motivo que não é
  design nosso. Campo `vendor-discounted|full-emulated|unknown`, report-only, nunca gateia.
- **c5 no-amplification:** o stub-set do worker PTC tem que ser subconjunto PROVÁVEL das tools já
  declaradas — um worker que emite código não pode ganhar alcance que não teria 1-call-por-vez.

## Measure-before-control (o gate — CRÍTICO)
PTC é uma APOSTA DE SHAPE-DE-WORKLOAD, NÃO default-on. **τ²-bench (dado da PRÓPRIA Anthropic): +8% de
custo em fluxo sequencial curto** ("sequential single-call workflows do not benefit"). Números de
vendor (20-98%) SEM replicação independente; PointFive (arXiv:2607.12161, 2026-07): token-reduction ≠
billed-cost com caching (r=0.15). Melhor número NÃO-vendor: LLMCompiler (ICML 2024) 3.7x latência/6x
custo vs ReAct. → **probe measure-only PRIMEIRO:** rodar a cadeia discover TRADICIONAL vs PTC-emulado
no NOSSO tráfego, matched-budget, logar no `cost_metrics` (observed vs estimated) + o CPU-time, gate
no noise floor L13. Hipótese de break-even a FALSIFICAR: N>~3-4 calls.

## Portfólio / buildável
- **BUILDÁVEL JÁ (measure-only): N-PTC-PROBE (EXP-24)** — a comparação latência/token/CPU tradicional-
  vs-PTC-emulado numa tarefa real (discover), noise-floor gated. NUNCA muda o caminho de produção.
- **OWNER-GATED:** o **N-PTC-ENGINE** (o módulo `harness_tools` + o loop de sandbox + o relay
  caller-tag pause/resume) — é controle + segurança → precisa do probe justificar + security review.
  O **4º taint sink** (dobra RD-TAINT/D023). A extensão de conformance/accounting.

## Fronteira que encaixa (Flow A web, citado + datado)
- **Tool Search / RAG-sobre-tools** (Gorilla arXiv:2305.15334; Anthropic Tool Search Tool, 85%
  redução, APPEND-not-swap pra preservar cache) — stacka com PTC (o script busca a tool antes de
  invocar). Testável SEM o engine. Alto valor (o harness já mescla MCP de 5 surfaces).
- **MCP-as-code** — quando `capabilities.json.mcpServers` (hoje `{}`) for populado; mesmo módulo de stub.
- **Structured outputs / constrained code-grammar** — defense-in-depth sobre o sandbox (código num
  subset seguro antes de executar). `[judgment]`, sem produto shipado.

## Rastreabilidade
| Evidência | Ideia | Experimento | Task | Status |
|---|---|---|---|---|
| 4/4 (código-orquestra-tools) + CodeAct + pushdown | harness_tools no sandbox + loop | N-PTC-PROBE = EXP-24 | N-PTC | desenhado; probe buildável, engine owner-gated |
| paridade w-004 + NVIDIA w-004 (4º sink) | taint no stdout do sandbox | — | dobra RD-TAINT/D023 | desenhado (security) |
| vendor-scan (OpenAI 2026-07-09 PTC) | premissa atualizada; parity = só sandbox pros open-weights | — | N-PTC-ENGINE | [web] verificar |
| τ²-bench/PointFive/LLMCompiler | PTC é aposta de workload; medir no nosso tráfego | EXP-24 | — | measure-first |
