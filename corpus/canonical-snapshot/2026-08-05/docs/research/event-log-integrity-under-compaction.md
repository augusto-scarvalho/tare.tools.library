# Research — integridade tamper-evidente de log sob compactação (SPEC-164 M4+M5)

Rodada de ideação 2026-07-21. Pergunta: o `allow_gaps` da SPEC-164 enfraquece o modelo
(pergunta do owner)? Que estruturas de blockchain / logs verificáveis / authenticated
data structures resolvem "remoção legítima preservando prova de integridade sem
falso-positivo"? Qual é PROPORCIONAL ao nosso teto (sem chave, single-tenant, verificador
LOCAL, log vivo transiente + registro durável)?

Ideadores (5, em 3 vendors): 2× **Sonnet 5 high** (Anthropic; cripto-rigor e ops/custo)
+ 1× **Gemini** (Google) + 2× **NVIDIA** (`nemotron-3-nano-30b`; security e
trust-boundary). Nota de infra: a `NVIDIA_API_KEY` vive no `.env` (não no keyring) e é
carregada no boot do harness — o worker precisa rodar pelo spawn do harness ou com o
`.env` carregado; os modelos NVIDIA gigantes (nemotron-ultra-550b) deram 503 (sobrecarga)
e o nano-30b respondeu. Modelo pequeno = análise mais rasa, ponderada abaixo.

## Fundações verificadas (Discover)

| Técnica | Fonte | O que dá |
|---|---|---|
| Certificate Transparency / RFC 6962 | datatracker.ietf.org/doc/html/rfc6962 [web, forte] | Consistency proof = prova que árvore B é PREFIXO de A (só appendou, nunca deletou). Merkle, O(log n), Signed Tree Head + monitor TERCEIRO. NÃO suporta deleção. |
| Crosby-Wallach 2009 (USENIX Sec) | usenix.org/legacy/event/sec09 [web, forte] | History tree Merkle que DELETA SELETIVAMENTE eventos antigos preservando tamper-evidence (mantém o hash interno, descarta a folha). O(log n). Assinatura é ortogonal. |
| Merkle Mountain Range | eprint.iacr.org/2025/234, docs.grin.mw [web, moderada] | Accumulator append-only; pruning de folhas antigas preservando roots. Pruning padrão é PREFIXO/idade (não casa nosso padrão de remoção por TIPO). |
| Sparse Merkle Tree / accumulator RSA-bilinear | [judgment] | (Não-)pertinência em keyspace; accumulator precisa setup semi-confiável. Ferramenta errada (log sequencial, não key-value). |
| KSI / hash calendar (Guardtime) | [web, moderada] | "Keyless" = sem chave ASSIMÉTRICA por assinante, MAS troca por PUBLICAÇÃO PERIÓDICA externa amplamente testemunhada. A testemunha é a "chave" disfarçada. |
| Rekor/Sigstore (Trillian) | [judgment] | Reusa a árvore CT + monitors terceiros + servidor de log + rede. Desproporcional a um harness local. |

## Convergência (3 ideadores, 2 vendors — sinal FORTE)

1. **Merkle/CT/MMR/accumulator são OVER-ENGINEERING aqui.** Resolvem três coisas que
   NENHUMA existe no nosso caso: (a) verificador TERCEIRO sem acesso ao dado (aqui há UM
   verificador local, `repo_health.checks`, que já lê o arquivo inteiro → provas O(log n)
   são moot); (b) ESCALA de bilhões de folhas (aqui são dezenas/rodada); (c) adversário
   COM RECURSOS + assinatura/testemunha. **Sem chave nem testemunha externa, uma raiz
   Merkle recomputável por quem tem escrita é tão forjável quanto um hash simples** — Merkle
   NÃO eleva o teto sem assinatura. [Sonnet-cripto + Sonnet-ops + Gemini, forte]
2. **O esforço REAL paga no REGISTRO DURÁVEL (escalations.json), NÃO na chain viva.** A
   chain viva é TRANSIENTE (gates limpam) e o check é ADVISORY/WARN-only → dano de uma
   lacuna é "doctor diz OK indevido uma vez". O durável SOBREVIVE aos gates, é onde as
   decisões de segurança do owner moram, e tem ZERO integridade hoje (cada resolvedRecord
   é sobrescrito por chave, sem encadeamento). Dano ali é PERMANENTE. [ambos Sonnet, forte]
3. **Crosby-Wallach = a opção-C sem a árvore.** O paper que resolve nosso problema
   conceitual (deletar preservando evidência) é a MESMA ideia de "guarde o hash, descarte
   o conteúdo" — a árvore só ganha com verificador terceiro. [Sonnet-cripto, forte]
4. **Achado que corrige meu framing:** o `allow_gaps=True` que shippei é MAIS FRACO que a
   opção-C — tolera TODO gap incondicionalmente E aceita reorder de eventos VIVOS (o spec
   já declara isso no invariante 3). Não é nem a opção-C. [ambos Sonnet, forte, verificado no código]

## Divergência (tipada)

| Eixo | Sonnet-cripto (rigor) | Sonnet-ops (custo) |
|---|---|---|
| A opção-C basta? | **NÃO** — tem um FURO: prova existência, não adjacência. Um forjador cita QUALQUER hash removido como prevHash de uma linha nova. Fix: **opção C+** = pares `{hash_do_SUCESSOR: hash_removido}` (amarra a exceção à identidade do sucessor via 2ª pré-imagem SHA-256). Fecha reorder + forjamento-por-citação. Selo deve ACUMULAR (não sobrescrever). | **É MAIS do que precisa** — o ganho de C só importa se houver 2ª via de remoção fora do compactador (marginal no modelo de ameaça). E o conjunto cresce sem teto num arquivo durável. |
| Onde investir | C+ na chain viva + nota que o durável tem valor marginal sem testemunha | **Pular a chain viva; dar hash-chain SIMPLES ao durável** (stateHash + prevStateHash por write do escalations.json). Mais barato que C (sem set), mais barato que Merkle (sem árvore). |
| Convergem em | Não-Merkle; o durável importa; sem-chave = teto real | idem |

### Divergência CROSS-VENDOR (NVIDIA vs Sonnet — a que o owner pediu)

| | NVIDIA (nemotron-nano) | Sonnet 5 high (ambos) + Gemini |
|---|---|---|
| Estrutura do durável | **MMR (Merkle Mountain Range)** — O(log n) inclusion proof, "forte" | **hash-chain SIMPLES** (1 elo/write) — MMR é over-engineering |
| Vale o O(log n)? | SIM (NVIDIA-1 disse "no external witness needed" — a posição mais agressiva) | NÃO — moot: o verificador é LOCAL e já lê o arquivo inteiro; O(log n) só paga com verificador TERCEIRO |
| Precisa de testemunha? | NVIDIA-1 disse não; **NVIDIA-2 corrigiu: MMR puro precisa de STH** → propõe **ancoragem git** como a testemunha barata | Sim — sem testemunha/assinatura, raiz Merkle recomputável = tão forjável quanto hash |

**O ponto de discórdia real:** o VALOR do inclusion-proof O(log n). NVIDIA acha que
justifica o MMR; Sonnet+Gemini dizem que é moot HOJE (verificador local já tem tudo) e só
paga quando existir verificador terceiro (CI/multi-tenant futuro) — o mesmo gatilho da
infra-de-chave. [Sonnet forte, NVIDIA preliminar — modelo pequeno]

### Convergência NOVA e forte (Sonnet-cripto + NVIDIA-2, cross-vendor)

**Ancoragem externa via git** = a testemunha terceira BARATA sem infra de chave:
commitar periodicamente o head-hash/selo num arquivo git-tracked que o owner revisa.
Reescrever histórico git é visível/forense — eleva o teto "sem chave" de forma útil,
sem provisionar chave nem serviço. Os dois vendors chegaram nisso independentemente. É a
melhor resposta ao teto tamper-evident-não-proof. [cross-vendor, moderada]

## Recomendação (síntese do orquestrador)

**Não ir para Merkle/CT/MMR** (unânime — over-engineering sem chave). Duas peças, baratas,
stdlib, sem dependência nova:

1. **Chain viva → opção C+ (pares sucessor→removido), não o allow_gaps atual.** Fecha o
   furo que o owner intuiu (reorder + edição auto-consistente que hoje escapam), amarrando
   cada gap tolerado à identidade do sucessor. É a resposta direta a "allow_gaps enfraquece".
2. **Registro durável → hash-chain simples de 1 elo por write** (`stateHash` = sha256 do
   doc canônico sem o próprio campo; `prevStateHash` = o do write anterior). Fecha o gap
   MAIS profundo (zero integridade hoje no arquivo que sobrevive aos gates e guarda as
   decisões de segurança). Pega edição pontual E rollback para snapshot antigo.

3. **Ancoragem git (a peça nova, convergência Sonnet-cripto + NVIDIA-2)** — commitar
   periodicamente o head-hash/selo do durável num arquivo git-tracked que o owner revisa.
   É a testemunha externa barata que eleva o teto SEM infra de chave. Barato, incremental,
   e responde diretamente ao "sem chave = tamper-evident não proof". [cross-vendor, moderada]

**Atrás do gatilho de verificador-terceiro / infra-de-chave (não construir agora):**
MMR (NVIDIA) ou Merkle root ASSINADO (Crosby-Wallach/RFC-6962). O ganho O(log n) + provas
compactas só paga quando um verificador que NÃO tem o arquivo inteiro existir (CI externo,
multi-tenant). Até lá, hash-chain simples + ancoragem git dá o mesmo teto de segurança
por muito menos código. [Sonnet forte; a divergência do NVIDIA é o sinal para reabrir
ISSO quando o gatilho chegar]

## Resposta direta à pergunta do owner

Sim, `allow_gaps` enfraquece — mas a correção **não** é blockchain/Merkle (over-engineering
sem chave, confirmado por 2 vendors). É (1) a opção C+ na chain viva e/ou (2) uma
hash-chain simples no registro durável, que é onde a integridade realmente falta. O teto
"sem chave = tamper-evident, não tamper-proof" é intrínseco e honesto; só assinatura +
testemunha externa o eleva, e isso fica atrás do gatilho de infra-de-chave.

---

# Round 2 — Double Diamond #2 (9 ideadores, 9 divergências) — 2026-07-21

Pedido do owner: aprofundar sobre os candidatos, caçar papers que CRUZAM os domínios,
e rodar 9 ideadores (3 Sonnet 5 high × 3 NVIDIA-GLM × 3 Gemini) com 9 divergências.

**Cobertura de modelos (honesta):** Sonnet 5 high ×3 (via Agent). NVIDIA-GLM = `z-ai/glm-5.2`
nos 3 (sem fallback — GLM respondeu desta vez). Gemini: o assento cripto rodou em
`gemini-3-flash-preview` (o pedido do owner); os outros 2 caíram para `gemini-2.5-flash`
(3-flash-preview indisponível/limitado naqueles). Cada vendor rodou 3 perspectivas:
A=engenheiro-mínimo, B=criptógrafo, C=arquiteto-de-fronteira.

## Papers cross-domain (Discover 2 — verificados)

| Fonte | O que cruza | Achado |
|---|---|---|
| **SealFS / SealFSv2** (Computers & Security 2021; Int.J.Info.Sec 2022) [web, forte] | secure-logging single-machine × nosso regime local | Tamper-evidence local SEM hardware/rede. v1=keystream armazenado (segurança teórica), v2=ratchet (degradação linear) — knob custo↔segurança. Garantia: "atacante não forja dados gerados ANTES de controlar o sistema". |
| **Bellare-Yee / Schneier-Kelsey / Ma-Tsudik FssAgg / Logcrypt** [web, forte] | forward-integrity × chave-que-evolui | Família da MAC simétrica que ratcheta+deleta → integridade forward SEM PKI. Teto: protege o PASSADO contra compromisso POSTERIOR, não contra escritor-adversário-desde-t0. |
| **halo-record (GitHub) / "AuditableLLM"** [web, moderada — corrigido round 3: o ID 2512.17259 pertence ao Verifiability-First; a fonte do "AuditableLLM" é secundária/não-verificada] | audit-log de AGENTE de IA × nosso design EXATO | Log hash-chained, dependency-free, "verifiable by anyone" para agentes de IA. **É o nosso design, construído por terceiros** → o piso hash-chain NÃO é ingênuo, é padrão emergente do campo. |
| **Verifiability-First Agents (arXiv 2512.17259)** [web, forte] | proveniência de agente × assinatura | Action Attestation Layer: recibos ASSINADOS por ação num Provenance Log. Precisa de chave. |
| **OriginStamp — "Auditing LLM Decision Trails with Blockchain"** [web, moderada] | trilha de decisão LLM × âncora externa | Ancoragem blockchain de trilhas de decisão de LLM = a ideia OTS/git-anchor, domínio-exato. |
| **OpenTimestamps / GitTrustedTimestamps (RFC3161)** [web, forte] | git-como-notário × âncora keyless | Git é Merkle-tree → reescrever histórico é visível; OTS = calendário/blockchain testemunhado, keyless, sub-cent. |
| **VCT — Verifiable transcripts for LLM conversations (arXiv 2606.23003)** [web, moderada] | transcript de LLM × log verificável | Roubar a FORMA (log quente + checkpoint testemunhado periódico), não a maquinaria (assume múltiplos relying parties + gossip de STH que não temos). |

**Achado que muda o mapa:** o campo de audit-log de AGENTES DE IA convergiu INDEPENDENTEMENTE
no nosso design exato (hash-chain dependency-free — halo-record, AuditableLLM). E os DOIS
únicos jeitos que o campo usa pra passar desse piso são exatamente os dois que já
tínhamos: **assinar** (Verifiability-First) ou **ancorar externamente** (OriginStamp/OTS).
Nada mais. Isso DES-nebuliza: não há uma terceira estrutura mágica.

## Convergências fortes (9 ideadores, 3 vendors)

1. **MMR = rejeitar. UNÂNIME 9/9.** O(log n) inclusion-proof é moot quando o verificador lê
   o arquivo inteiro em escala de dezenas de eventos. (SHIFT vs round 1: o nemotron-nano
   era pró-MMR; o GLM-5.2 maior rejeita firmemente — o pró-MMR era artefato de modelo pequeno.)
2. **A integridade-zero do escalations.json é O gap real** → hash-chain simples no durável. ~9/9.
   Sonnet-B: o durável só APPENDA (compactação ali é append, não deleção) → NÃO tem o
   problema de gap/falso-positivo que é 100% da chain VIVA.
3. **Nenhuma estrutura keyless interna eleva o teto acima de tamper-evident; só testemunha
   externa OU chave.** Unânime.
4. **C+ acima do allow_gaps nu para a chain viva.** 8/9 (NVIDIA-A é o único "chain viva não vale").
5. **Se construir testemunha: git primeiro, OTS mais forte, TPM desproporcional.** Ordem unânime.

## As 9 divergências (tipadas)

| # | Eixo | Lado A | Lado B | Resolução do orquestrador |
|---|---|---|---|---|
| D1 | **Forward-secure MAC ajuda AQUI?** | **Moot** (NVIDIA×3, Gemini-A/C, Sonnet-A): worker segura a chave, adversário-desde-t0 pode pré-salvar chaves → zero ganho, falsa confiança | **Bounded-real** (Gemini-3-flash, Sonnet-B): protege entradas ANTES de um drift/jailbreak MID-round, SE houver fronteira de seed confiável + deleção real | **Sonnet-B reconcilia:** a variável decisiva é se existe PREFIXO HONESTO. Nosso GATE é essa fronteira. Não é moot no nosso deployment real — é um ganho BOUNDED (janela gate-start→drift), delete só best-effort em software. Deferir, não rejeitar. |
| D2 | **Status do allow_gaps** | Piso honesto (NVIDIA-A: log é transiente) | **Regressão** (Sonnet-C: "silencia o único alarme"; Sonnet-B: "conserta falso-positivo vestindo rótulo de segurança"; Gemini-B/C: "botão de apagar história") | 8/9: **é regressão vs estrita**, não só "mais fraco". Responde direto ao owner: sua intuição estava certa e é pior que pensava. C+ é o fix mínimo real. |
| D3 | **C+ vale na chain viva?** | Construir (Sonnet×3, Gemini-B/C, NVIDIA-C) | Cerimônia num log que o gate descarta (NVIDIA-A) | Construir — mas ver D4/D5. |
| D4 | **C+ é independente?** | Independente (maioria tratou b e c como opções separadas) | **Acoplado** (Sonnet-A: "C+ não tem dente sem c" — o selo mora no durável de integridade-zero; worker reescreve o selo) | Sonnet-A vence: **shippar b+c JUNTOS**, senão C+ é fachada. |
| D5 | **C+ é autenticação?** | Fecha "reorder + forge-by-citation" (NVIDIA-C, Gemini) | **Bookkeeping, não autenticação** (Sonnet-B: 2ª-preimagem impede SUBSTITUIÇÃO, não FABRICAÇÃO; "não chamar de gap-tolerance criptograficamente segura") | Rotular honesto: C+ = não-fungibilidade de forjas (bookkeeping), não move a fronteira de confiança. |
| D6 | **git-anchor eleva o teto?** | Sim, é o único passo keyless que eleva (Gemini×3, NVIDIA-C) | **Emprestado/condicional** (Sonnet-B: "como escopado, não mais forte que c + cerimônia"; Sonnet-C: só se push p/ remote inalcançável + owner revisa, senão "teatro"; Sonnet-A: só como carona nos commits que JÁ acontecem; NVIDIA-A: deferir) | git-anchor NÃO é auto-elevador: vale sse (remote inalcançável pelo worker + revisão). Versão barata = carona no commit de handoff/NEXT_STEPS que já roda toda rodada. |
| D7 | **TPM/TEE** | #1 por princípio (Gemini-A/C rankeiam RoT de hardware no topo) | **Never-build** (NVIDIA-A "absurdo", NVIDIA-C "grosseiramente desproporcional/teatro") | Sonnet-C: fora-de-escopo-mas-real — TPM inconsistente em Win/Linux/macOS (paridade D045 quebra). Parquear, não perseguir, neste tier. |
| D8 | **QUAL adversário? (a raiz)** | Malicioso-desde-t0 (NVIDIA×3): tudo interno colapsa; interno = "teatro de segurança" | **Careless/drift/hijack-mid-run** (Sonnet×3, esp. B: "é exatamente a falha que um agente que dá drift produz") | **A chave da síntese:** o valor de C+/durável DEPENDE de qual adversário. O harness enfrenta OS DOIS; o dominante REALISTA é o worker que dá drift/bug/injection mid-run → interno pega o caso realista, só não chamar de "elevar teto". |
| D9 | **Chave própria do owner é in-scope?** | "sem infra de chave" = limite duro (todos menos Sonnet-B ruleram assinatura fora) | **Sonnet-B:** um único keypair ed25519/minisign (sem CA/HSM) contradiz "sem chave" na LETRA, não no ESPÍRITO; é a ÚNICA coisa que tira o worker da fronteira de confiança do registro durável → **levar ao owner como PERGUNTA, não assumir** | Ver "Decisão para o owner" abaixo. |

## Recomendação (síntese do orquestrador, round 2)

**Construir agora (barato, keyless, fecha os gaps contra o adversário REALISTA — D8):**
1. **Hash-chain simples no escalations.json** (c) — #1 unânime; fecha a integridade-zero do
   artefato que sobrevive; estruturalmente SEM problema de gap (durável só appenda).
2. **C+ ACOPLADO a (c)** (b+c juntos, D4) — troca a regressão do allow_gaps por manifesto de
   gap falsificável, mas rotulado honesto como não-fungibilidade/bookkeeping (D5), não autenticação.

**Deferir com GATILHO NOMEADO (não "depois" vago):**
3. **git-anchor** — só como carona nos commits de handoff que já rodam (D6). Gatilho: quando
   quisermos proteção contra worker DELIBERADAMENTE adversário (não só careless) + push p/
   remote inalcançável + revisão do owner. Barato o bastante pra já entrar na versão-carona.
4. **Forward-secure MAC** (D1) — ganho bounded contra drift mid-round. Gatilho: definir a
   fronteira de prefixo-honesto (gate-start) primeiro; delete é best-effort em software. ~30 linhas.

**Levar ao OWNER como decisão (D9):** um único keypair ed25519/minisign do owner (sem CA/HSM)
NÃO é a infra-PKI que descartamos. É a única coisa que tira o worker da fronteira de confiança
para o registro DURÁVEL (as decisões ratificadas do próprio owner). Sonnet-B: isso deve ser
uma PERGUNTA a quem pôs a restrição "sem chave", não uma suposição. → decisão do owner.

**Rejeitar:** MMR (9/9), TPM/TEE (desproporcional multi-OS neste tier).

## O que o round 2 ADICIONA ao round 1

(a) allow_gaps é REGRESSÃO, não só fraco (D2 — resposta direta ao owner). (b) C+ deve ACOPLAR
ao durável (D4). (c) C+ é bookkeeping, não autenticação — rótulo honesto (D5). (d) forward-secure
NÃO é moot — é ganho bounded contra drift mid-round ancorado no gate-start (D1, reconcilia a
divergência cross-vendor). (e) uma chave mínima do owner é discutivelmente in-scope e é o único
fix real do durável — PERGUNTA para o owner (D9). (f) MMR unânime-rejeitado até pelo NVIDIA
maior (o pró-MMR do round 1 era artefato de modelo pequeno).

---

# Reavaliação independente — Fable 5 xhigh, 2026-07-21 (pedido do owner)

Os rounds 1-2 foram orquestrados por Opus 4.8. Reavaliação por outro modelo, contra as
saídas CRUAS dos 9 ideadores E contra o código real do repo (o que nenhum ideador viu).

## Achado principal: a PREMISSA do estudo está desatualizada no nosso próprio código

O brief inteiro assume "worker pode reescrever AMBOS os logs (class-B worker-writable)"
como fato imutável — e toda a conclusão "só testemunha externa ou chave eleva o teto"
deriva DELA. Mas no código real:

1. **Workers sandboxados NÃO enxergam o escalations.json real.** `controlled_writes.py`
   (`workflow_runtime_ignore`, com self-check) EXCLUI `.harness/state`, `state-store`,
   `targets`, `runs` dos workspaces de worker — o worker nem recebe cópia; escritas de
   `.harness/` de worker aparecem no MERGE mediado (SPEC-148 `protected-path-modified`).
2. **A maquinaria de negação por SO já existe e é nossa** (SPEC-148/163): icacls deny-ACE
   + RO-bit nos protegidos do workspace, com guarda anti-junction (M3). Estender o
   registro protegido ao ledger durável é reuso, não construção nova.
3. **Append-only por SO é viável multi-OS** para o log VIVO se um dia quisermos:
   NTFS separa `FILE_APPEND_DATA` de `FILE_WRITE_DATA`; Linux `chattr +a`; macOS
   `uappnd` — caminho de paridade D045 declarável. Nenhum dos 9 ideadores viu essa
   alavanca porque o brief não expôs SPEC-148/workspaces (efeito âncora, ver abaixo).

**Consequência:** o conjunto realista de escritores dos arquivos REAIS é o contexto
CONFIÁVEL (overseer/CLI/gate) — e o adversário que importa ali é exatamente o
drift/hijack mid-run (D8, lado Sonnet), não o malicioso-desde-t0 (lado NVIDIA). O
"qualquer estrutura interna é teatro" do NVIDIA SUBpesa o caso realista no NOSSO
deployment; o par b+c defende justamente o caso que sobrou. A recomendação build-now
(b+c) SUSTENTA — com justificativa mais forte que a original.

## Correções à síntese do Opus

| Claim do round 2 | Veredito | Correção |
|---|---|---|
| D2: "allow_gaps é REGRESSÃO vs estrita" | **Overclaim retórico** | Sob a estrita, um strip malicioso tem a MESMA assinatura de um gap legítimo de compactação (prevHash-mismatch) — o alarme era ruído sempre-vermelho em operação normal, não sinal. Verdade precisa: estrita = ruído sem sinal; allow_gaps = silêncio (mantém só stale-edit); C+ = SINAL (gap tem que bater com o selo). A conclusão (C+ é o fix) sobrevive; o "pior que a estrita" não. |
| D4: "C+ sem dente sem (c)" | Sustentado, com nuance | O valor do acoplamento é contra drift/corrupção do contexto confiável — o deliberado recomputa as duas chains trivialmente (custo ~zero), e o worker sandboxado nem alcança o arquivo. |
| D1: forward-secure bounded-real | Sustentado, MAIS fraco que declarado | `append_event` roda em N processos CLI efêmeros → o estado do ratchet teria que PERSISTIR EM DISCO entre invocações → chave atual legível-em-repouso no mesmo contexto; e detectar rewrite-total-com-seed-novo exige ancorar um commitment do seed. O "~30 linhas" omite isso. Defer mantido, valor rebaixado. |
| D6: git-anchor carona "já vale" | Levemente vendido demais | Nesta máquina o contexto confiável alcança `.git`; sem push p/ remote fora do alcance + revisão real, a carona é só forense-de-reflog. Defer com a condição EXPLÍCITA como gatilho. |
| "O campo convergiu no nosso design" (halo-record/AuditableLLM) | Confiança rebaixada forte→**moderada** | Fontes finas (1 repo GitHub, blogs, arXiv não lido inteiro). Inconsistência de citação RESOLVIDA no Discover do round 3: **arXiv 2512.17259 = Verifiability-First Agents** (verificado em arxiv.org/abs/2512.17259); a atribuição "AuditableLLM" estava errada e foi corrigida na tabela acima. |
| D9: chave do owner | Mantido pendente, urgência MENOR | Com a exclusão de workspace + registro protegido, o que a chave compra é assinatura contra drift do contexto confiável — real, mas o gap que ela fecharia é menor do que o round 2 sugere. Avaliar DEPOIS da opção-ACL. |
| MMR 9/9 rejeitado; TPM desproporcional; honestidade de cobertura de modelos | Sustentados | — |

## Falha metodológica a registrar (para o research-playbook)

O brief do round 2 entregou o CARDÁPIO de candidatos + as conclusões do round 1 aos
ideadores → efeito âncora: o painel majoritariamente RANQUEOU o cardápio em vez de
expandi-lo (só Sonnet-B escapou, com a chave-do-owner). A alavanca ACL/workspace — a
mais barata de todas, já construída — ficou invisível para 9/9 porque não estava no
brief. Lição: waves de ideação precisam de um assento "o que NÃO está no cardápio" e/ou
um assento code-grounded que leia o repo antes de opinar.

## Recomendação revisada (Fable — superada pelo round 3 abaixo)

1. **Build-now b+c mantido** (chain durável + C+ acoplado) — defende o adversário
   realista (drift no contexto confiável); rótulo honesto de bookkeeping mantido.
2. **NOVO candidato barato ANTES de qualquer criptografia extra:** adicionar
   `.harness/state/escalations.json` (e o ledger de decisão) ao registro
   protegido/merge-checado (reuso SPEC-148) — verificação prévia: confirmar que nenhum
   fluxo legítimo de worker escreve o arquivo real (a exclusão de workspace sugere que
   não). Eleva a barra REAL contra worker sandboxado com maquinaria existente,
   zero chave, zero testemunha.
3. git-anchor / forward-secure / chave do owner: defer com os gatilhos corrigidos acima.
4. Append-only por SO no log vivo: registrar como opção de paridade D045, sem construir.

---

# Round 3 — CONSOLIDAÇÃO FINAL (Double Diamond #3, 2026-07-21, orquestrador Fable 5 xhigh)

Brief re-enquadrado pela reavaliação (modelo T1-T4 por camadas, alavancas L1-L7 com
correções honestas, anti-âncora explícita: "atacar/expandir > ranquear"). Painel de 6:
Sonnet 5 high ×2 (RED, DECIDER), GLM-5.2 ×2 (idem — sem fallback), Gemini ×2
(2.5-flash; 3-flash-preview indisponível nesta janela). Discover prévio resolveu a
citação (2512.17259 = Verifiability-First, verificado) e a assimetria multi-OS do
append-only (chattr +a exige root p/ set E unset; icacls por-usuário; uappnd reversível).

## A anti-âncora funcionou: 3 classes de alavanca e 1 camada de adversário NOVAS

1. **T1.5 "lixo autêntico" (5/6 assentos — a maior convergência da rodada).** O worker
   envenena dados/resultados; o contexto confiável escreve FIELMENTE uma entrada
   sintaticamente perfeita (chain ok, ACL ok, assinatura ok) e semanticamente maliciosa.
   GLM-RED: "a chain é testemunha do ataque, não barreira". TODAS as L1-L7 autenticam
   forma, não conteúdo. Contra-medida real (Sonnet-RED): **proveniência de decisão** —
   encadear NA entrada ratificada as referências causais do que a produziu (tool
   outputs, worker results). O harness JÁ tem o esqueleto: `parentEventId` (DAG causal)
   + actor tipado (SPEC-161) — é disciplina de wiring, não estrutura nova.
2. **L10 testemunha de auditoria do kernel (4/6):** ETW/USN/SACL (Win), auditd (Linux),
   EndpointSecurity (macOS) — trilha fora do domínio de escrita do adversário userland;
   classe mais forte que ACL/atributo; posicionada como o FIX honesto da assimetria do
   L3 (instala-se uma vez com admin, lê-se por leitor separado).
3. **Recovery/resposta (4/6):** detecção sem resposta é teatro — quarentena
   read-only em mismatch, fork do append point do último known-good, retomada só por
   ação do owner FORA do loop do agente (o alarme não pode depender do processo
   driftado agir contra si).
4. **Ataque de rollback/frescor (Sonnet-RED):** restaurar um snapshot ANTIGO
   validamente-encadeado (até validamente-assinado) apaga ratificações recentes sem
   quebrar nada — chain/assinatura autenticam conteúdo-num-ponto, não recência.
   Contra-medida barata descoberta na síntese: **cross-testemunho live↔durável** — o
   evento de compactação no log vivo registra o stateHash durável que produziu; o
   doctor compara → restore-de-backup careless é pego. (T2 cuidadoso reescreve os dois
   — teto inalterado, declarado.)

## Correções de matriz ratificadas (contra o round 2 E contra o meu brief)

- **"T2 recomputa trivialmente" assume T2 que CONHECE o esquema** (GLM-DECIDER). O T2
  realista (injection vindo de output de ferramenta, sem fonte do harness) deixa chain
  stale → L1/L2 pegam MUITO mais do realista que o creditado. L1 sobe de valor.
- **L6 "inforjável por T2+T3" é FALSO como declarado** (6/6 em alguma forma; Gemini-
  DECIDER como strongest disagreement): chave em disco no mesmo usuário = roubável por
  T2/T3. E Sonnet-RED corta mais fundo: **assinatura disparada pelo agente** deixa o
  T1.5 atravessar o signer com veneno validamente assinado. L6 só vale com (a) segredo
  out-of-band no momento de assinar (passphrase/hardware) e (b) prova-de-presença
  humana mostrando o TEXTO LITERAL ratificado — nunca "o agente concluiu que o owner
  aprovou". Sem as duas condições, L6 é falsa confiança.
- **L5 morto na arquitetura atual** (5/6): processos CLI efêmeros → ratchet em disco →
  o processo driftado É o key-holder. Zero contra T2 por construção. Defer ≈ never até
  existir daemon de vida longa com ratchet só-memória.
- **L3 vs T3 ~zero até no Windows** (Sonnet-RED): o dono do arquivo (mesmo usuário do
  T3) retém WRITE_DAC e re-ACLa de volta. L3 é alavanca anti-careless/anti-ignorante
  (T1, T2-sem-fonte), nunca anti-deliberado-mesmo-usuário. No Linux, curiosamente
  FORTE vs T2 user-level depois de setado (unset exige root) — mas o setup exige root.
- **L1 sem verificador rodando é inerte** (Sonnet-DECIDER): shipar L1 = shipar o
  verify JUNTO na cadência existente (doctor/gate), ou não shipar.

## Achados VERIFICADOS no código durante a rodada (não especulação)

- **`.env` NÃO está na exclusão de workspace** (`workflow_runtime_ignore` não lista) →
  chaves NVIDIA/GEMINI legíveis por worker no workspace. O painel (GLM-RED M4,
  Sonnet-RED) apontou "prioridade invertida": vazamento de credencial ≥ tamper de
  ledger. Fix de 1 linha + fixture. CONFIRMADO 2026-07-21.
- **Override é env bare** (`HARNESS_ALLOW_PROTECTED_WRITE=1` em
  protect_canonical_files.py) — endurecer p/ nonce-por-sessão fecha
  bypass acidental/replay (rótulo honesto: NÃO fecha T2 deliberado).
- A verificar (backlog): TOCTOU no merge seam (GLM-RED M1); scrub de env no spawn de
  worker; caminho de promoção T1→T2 via artefatos de código não-revisados executados
  em rodada posterior (Sonnet-RED).

## CARTÃO DE DECISÃO FINAL (para ratificação do owner)

**BUILD NOW (o trem M4+M5 revisado + higiene urgente):**
| # | Item | Contra o quê |
|---|---|---|
| B1 | `.env` na exclusão de workspace (1 linha + fixture) | T1 lendo credenciais — prioridade máxima da rodada |
| B2 | L1: chain durável (stateHash+prevStateHash) + selo C+ ACOPLADO + **verify no doctor/gate** (inerte sem isso) + **cross-testemunho live↔durável** (anti-rollback careless) | T2-careless E T2-sem-conhecimento-do-esquema (o realista mais provável) |
| B3 | L2: escalations.json no registro protegido (reuso SPEC-148) + override env→nonce + uso do override emite security event | T1 escape; bypass acidental/replay |
| B4 | Proveniência de decisão: resolvedRecords carregam parentEventId-chain + actor (esqueleto SPEC-161/DAG já existe) | T1.5 — a ÚNICA alavanca que toca o lixo autêntico |
| B5 | Política: ledger fora de backup/sync ambiente (nota + doctor check barato) | rollback via restore + vazamento de confidencialidade |

**DECISÃO DO OWNER FORÇADA NESTA RODADA (Sonnet-DECIDER: "deferir decisão ≠ deferir
por pré-requisito técnico faltante"):** L6 sim/não — chave minisign/ed25519 do owner
SÓ para eventos de ratificação, CONDICIONADA a (a) segredo out-of-band no sign +
(b) prova-de-presença com texto literal. Se qualquer condição for inaceitável → defer
honesto com teto declarado (T2-cuidadoso/T3 permanecem abertos no durável).

**DEFER COM GATILHO NOMEADO:** L3 (decisão de principal distinto OU downgrade formal
de paridade p/ "hash-chain parity only" + Windows-only declarado); L4 git-anchor
(remote fora de alcance + revisão do owner RECORRENTE de verdade); L5 (daemon
vida-longa com ratchet só-memória); L7 OTS (demanda externa/compliance ou
multi-tenant); L9 daemon-escritor (T2 recorrente observado); L10 kernel-audit
(quando a paridade do L3 for julgada inaceitável — substitui L3, não soma; ou 1º
incidente T2 confirmado).

**NEVER (lápides):** MMR (9/9 round 2 — verificador local lê tudo); TPM/TEE neste
tier (desproporcional multi-OS); assinatura por-evento no log vivo (sem fronteira de
confiança p/ signer em caminho quente); camada WORM bespoke (reinventa L3); blockchain
próprio (consenso p/ um hash que um append registra); SIEM-como-integridade (resolve
frota, não single-machine); **assinatura disparada por inferência do agente** (o
anti-padrão que o T1.5 explora); cadência-como-suficiência (verify no ponto de USO
para decisões, cadência é piso).

**TETO RESIDUAL PÓS-BUILD-NOW (linguagem simples):** T1 fechado (resíduo = bug de
escape, o mesmo já aceito hoje). T2: careless/sem-fonte pego no próximo gate;
T2-cuidadoso-com-fonte ainda forja — vira inforjável SÓ nas ratificações e SÓ com L6
nas duas condições. T3: ~zero de L1/L2/L3 (recomputa/re-ACLa tudo); só L6-bem-custodiada
+ testemunha externa (L4/L7/L10) elevam. T1.5: B4 dá a trilha de auditoria; prevenção
é revisão humana no ponto de ratificação, não criptografia. T4: fora de escopo.

## SE L6 — decisão do owner 2026-07-21: ADOTAR, mas só no FUTURO

Gatilho nomeado: **antes da primeira release PÚBLICA** (o owner: "vamos adotar só no
futuro, antes de uma release pública"). Até lá, o teto declarado acima vale e é honesto
para uso single-tenant/local. Ao construir, as DUAS condições de uso (passphrase/hardware
out-of-band no sign + prova-de-presença mostrando o texto literal ratificado — nunca
assinatura disparada por inferência do agente) são obrigatórias, MAIS três requisitos de
design que a análise de perda-de-chave impôs (2026-07-21):

1. **Lista de chaves públicas autorizadas** (estilo `authorized_keys`), não uma só —
   senão rotacionar a chave INVALIDA todo o histórico já assinado. Ratificações antigas
   verificam sob a pública antiga; novas sob a nova.
2. **Passphrase obrigatória** na chave privada — senão "perder o arquivo da chave" vira
   "comprometimento silencioso" (quem acha o arquivo assina como o owner). Com passphrase,
   a chave em disco é inútil sem o segredo.
3. **Caminho de rotação/revogação documentado** — tratar "perdi/vazou a chave" como fluxo
   NORMAL, não emergência.

**Semântica de perda (por que L6 é seguro de adiar E de adotar):** perder a chave NUNCA
trava o harness nem apaga o passado — só rebaixa o teto das ratificações FUTURAS ao nível
bookkeeping (o teto de hoje) até rotacionar. Pior caso da perda = "voltei ao teto atual".
Tensão honesta a pesar: passphrase protege contra vazamento mas cria risco de perder a
passphrase; backup em gerenciador de senhas resolve, mas a segurança da chave passa a ser
tão boa quanto esse backup (mesma escada, sem mágica). Timestamp externo (L4/L7) é o que
permitiria provar quais assinaturas vieram antes/depois de um vazamento — por isso L6 e a
testemunha externa se reforçam quando o gatilho público chegar.
