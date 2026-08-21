# Log de pesquisa — medidor de crédito por vendor (N-VENDORCREDIT / D017)

Item #5 (owner: "pesquisar nas docs dos fornecedores + testar empiricamente; vai
testando, anotando; quando chegar em algo, a gente revisa juntos"). Log
incremental — cada rodada de pesquisa/teste anota aqui.

## Incremento 1 (2026-07-19) — docs dos 3 vendors: ACHADO QUE MUDA O DESENHO

Pesquisei as 3 documentações. **Conclusão-chave: 2 dos 3 vendors NÃO expõem o
saldo de crédito programaticamente.** O "medidor de gasolina" que a gente
imaginou (perguntar "quanto resta?") em grande parte NÃO EXISTE:

| vendor | saldo por API? | usage por API? | sinal de esgotamento | fonte |
|---|---|---|---|---|
| **Anthropic** (claude) | **NÃO** — `GET /v1/organizations/balance` → 404; feature request aberta (#47574) | SIM — Usage & Cost Admin API (precisa Admin key, ≠ key normal) | erro de quota | platform.claude.com/docs/en/manage-claude/usage-cost-api |
| **NVIDIA Build** (nvidia-compat) | **NÃO** — sem endpoint; users reclamam que nem na UI aparece | não documentado | **HTTP 402** com mensagem clara ao esgotar | forums.developer.nvidia.com |
| **OpenAI** (openai-compat) | parcial — `GET /v1/dashboard/billing/credit_grants` (dashboard, geralmente session-token, NÃO a API key; instável) | `GET /v1/usage?start_date&end_date` | erro auth/quota | community.openai.com |

## O reframe (arquiteto)
Como não dá pra PERGUNTAR o saldo de forma confiável, o desenho robusto do
N-VENDORCREDIT NÃO é "ler o medidor" — é **estimar o tanque + detectar o vazio**:

1. **Rastrear SPEND local** (já temos: delegation ledger). O T-ADAPTERCONF já
   entregou o pré-req: `accountingSemantics` diz quais vendors reportam token de
   forma CONFIÁVEL (codex + família openai-compat falham c9 → o número deles é
   estimado, não medido — então a estimativa de tanque deles é mais grossa).
2. **Saldo inicial declarado pelo owner** por vendor (ex.: "NVIDIA: 1000 credits";
   "Anthropic: $X") — um número que VOCÊ me passa (já que o vendor não passa), e
   a gente decrementa pelo spend rastreado. É uma ESTIMATIVA honesta, marcada como
   tal (não é verdade do vendor).
3. **Detecção de esgotamento empírica** pelos códigos de erro — NVIDIA 402, OpenAI
   auth/quota, os `rateLimitPatterns`/`authFailurePatterns` que já estão nos
   executor cards (`executors.json`). Quando o erro bate, o tanque REALMENTE
   acabou (verdade do vendor, ainda que tardia). O breaker já reage a isso.
4. **Alerta de tanque baixo** = estimativa (spend vs saldo declarado) cruzando um
   limiar → aviso antes do 402, com a ressalva de que é estimativa.

Isso casa com o D017 (U ponderado por escassez): a régua de escassez usa a
ESTIMATIVA de tanque, e o breaker/402 é o backstop de verdade.

## Testes empíricos a rodar (próximos incrementos — "vai testando, anotando")
- [ ] Provar o 402 do NVIDIA: capturar a shape exata da resposta de esgotamento
      (só acontece de verdade quando o crédito acaba — ou forçar com um modelo pago
      caro; anotar quando ocorrer naturalmente numa wave).
- [ ] Testar se a Anthropic Usage & Cost Admin API responde com a nossa key (é
      Admin key? temos?) — se sim, dá pra reconciliar spend real do claude.
- [ ] Testar `GET /v1/dashboard/billing/credit_grants` contra OpenAI proper (se
      tivermos key OpenAI real, não só NVIDIA/gemini compat) — anotar se funciona
      com API key ou exige session-token.
- [ ] Confirmar os `authFailurePatterns`/`rateLimitPatterns` atuais em
      executors.json cobrem as mensagens reais de esgotamento dos 3.

## Incremento 2 (2026-07-19) — a ideia do owner do `/usage`: MELHOR que o reframe

Owner: "cada fornecedor tem um atalho `/usage` que poderiamos spawnar workers bem
baratos e especificos pra usar e reportar quanto tem, de tempos em tempos". **Isso
resolve melhor que estimar o tanque** — em vez de bater numa API de saldo que não
existe, usamos a FERRAMENTA DO PRÓPRIO VENDOR que JÁ mostra o que resta:

- **claude** (Claude Code): tem `/usage` — mostra uso/limites da sessão/org. Um
  worker cheap (haiku, prompt mínimo) roda e reporta. FUNCIONA pros vendors-CLI.
- **codex**: provável ter um equivalente de usage no CLI — testar empiricamente.
- **NVIDIA/gemini** (HTTP puro, sem CLI): NÃO têm `/usage` — pra esses fica o
  reframe do incremento 1 (spend-tracking + 402/erro). Ou seja: **abordagem
  HÍBRIDA por classe de vendor** — CLI-vendors usam o `/usage` deles; HTTP-vendors
  usam spend+erro.

**Desenho revisado do N-VENDORCREDIT (com a ideia do owner):**
1. **CLI-vendors (claude, codex):** um probe periódico spawna um worker cheap que
   roda o `/usage` nativo e parseia a saída → número REAL do vendor, barato,
   sem estimativa. É o "medidor de gasolina" de verdade pra esses.
2. **HTTP-vendors (nvidia, gemini, openai-compat):** spend-tracking local
   (delegation ledger + accountingSemantics do T-ADAPTERCONF) + detecção de 402/
   quota. Estimativa + backstop.
3. **Cadência:** "de tempos em tempos" — um schedule/loop leve (o harness já tem
   `/schedule` e `/loop`) roda o probe de usage, anota no ledger, alerta em tanque
   baixo.

Testes empíricos a rodar: [ ] confirmar a shape do `claude /usage` (o que parseia);
[ ] achar o equivalente no codex; [ ] medir o custo de um worker de usage (deve ser
~centavos).

## O que preciso de você (quando a gente revisar juntos)
- O **saldo inicial declarado** de cada vendor que você quer rastrear (o número
  que o vendor não me dá). Com isso a estimativa de tanque fica real.
- Confirmar se temos uma **Anthropic Admin key** (≠ a key normal) — é o único
  jeito de reconciliar o spend real do claude.

## Sources
- Anthropic Usage & Cost API: https://platform.claude.com/docs/en/manage-claude/usage-cost-api ; balance 404 / feature request: https://github.com/anthropics/claude-code/issues/47574
- NVIDIA Build credits + 402: https://forums.developer.nvidia.com/t/api-credit-balance/309857 ; https://decodethefuture.org/en/nvidia-nim-api-explained/
- OpenAI billing endpoints: https://community.openai.com/t/get-the-remaining-credits-via-the-api/18827
