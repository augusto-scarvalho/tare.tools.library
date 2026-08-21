# ADR-062: Doutrina Universal de Engenharia Frugal, Inovação Ambidestra e Liberdade de Computação (BYOC)

## Status
**RATIFIED / RATIFICADO_POR_GOVERNANÇA_TRIPARTITE** (Concluído e Homologado via `CASE-2026-08-20-ENGINEERING-DOCTRINE-AND-BYOC`)

## Data de Ratificação
2026-08-21

## Quórum de Deliberação
- **Modo de Quórum:** `FRONTIER_UNANIMOUS`
- **Assento Google:** `Gemini 3.7 Flash · high` via Antigravity CLI (`agy.EXE`)
- **Assento OpenAI:** `GPT-5.6 Sol · high` via OpenAI Codex CLI (`codex.exe`)
- **Assento Anthropic:** `Claude Fable 5 · high` via Claude Code CLI (`claude.exe`)
- **Mediador Independente:** `z-ai/glm-5.2` (Via Negativa & Síntese Dialética Autônoma)

---

## 1. Contexto & Motivação

O ecossistema `tare.tools` necessitava de uma carta magna de engenharia atemporal, imune a modismos tecnológicos, agnóstica de hardware e orientada a resultados concretos. Era mandatório consagrar princípios universais de desenvolvimento que protegessem o projeto tanto contra a **hipertrofia técnica** (fábricas desnecessárias, *YAGNI*, sobrecarga de dependências e burocracia) quanto contra a **avareza minimalista paralisante** (medo de inovar, apego a primitivos arcaicos e perda de oportunidades de saltos tecnológicos).

---

## 2. A Doutrina dos 6 Princípios Fundamentais

Ficam formalmente estabelecidos e ratificados os 6 Princípios Constitucionais de Engenharia do ecossistema:

### 2.1 Princípio I: A Primazia da Via Negativa (Subtração antes de Adição no Núcleo)
- O melhor código em produção é aquele que resolve o problema com a menor superfície de complexidade possível.
- Nenhuma abstração, fábrica, camada de indireção ou microsserviço prematuro é aceito para atender necessidades hipotéticas (*YAGNI*).
- A biblioteca padrão e primitivos nativos do sistema têm prioridade máxima sobre dependências externas.

### 2.2 Princípio II: O Equilíbrio da Frugalidade Fértil (Ambidestria de Engenharia)
- **A Armadilha do Minimalismo Paralisante:** Ser excessivamente austero a ponto de rejeitar avanços tecnológicos, saltos de inteligência e novas fronteiras por medo de escrever código. O ecossistema deve ser ambicioso, arrojado e aberto a novas ideias.
- **A Armadilha da Hipertrofia Técnica:** Construir castelos teóricos de complexidade prematura, frameworks desnecessários e burocracia desprovida de valor prático.
- **A Síntese da Ambidestria:** Liberdade irrestrita para explorar, prototipar e inovar (*Spikes*, branches de pesquisa e laboratórios), combinada com filtragem cirúrgica e rigor implacável pela Via Negativa no momento de consolidar o código na árvore estável. Visão holística do todo sem perder o foco na arquitetura sistêmica.

### 2.3 Princípio III: A Regra do Falsificador Empírico Proporcional ao Risco
- Nenhuma decisão técnica ou veto arquitetural é aceito com base em dogmas abstratos ou opiniões estéticas.
- Toda contestação técnica exige um falsificador verificável adequado à sua classe de risco:
  1. *Bugs e Regressões Funcionais:* Testes automatizados reproduzíveis (`reproduction_test`).
  2. *Desempenho e Frugalidade:* Benchmarks comparativos e medições de consumo de memória.
  3. *Segurança e Integridade:* Modelos de ameaça formais, provas de invariantes estáticos e inspeções de concorrência/TOCTOU.

### 2.4 Princípio IV: Liberdade de Computação & Soberania (BYOC — Bring Your Own Compute)
- O ecossistema suporta nativamente 3 realidades operacionais com paridade de contrato e degradação previsível:
  1. *Desenvolvedor Zero-Hardware / Free-Tier:* Opera com custo $0.00 usando quotas gratuitas de nuvem (Google Gemini Free Tier, NVIDIA NIM/Build Free Evaluation Tier de 1.000 créditos) e modelos abertos em CPU local (llama.cpp).
  2. *Empresa / Engenheiro Profissional:* Conecta chaves de API comerciais com segurança no OS Keyring.
  3. *Usuário Soberano / Homelab:* Executa modelos locais em qualquer GPU (NVIDIA, Apple Silicon, AMD, Intel) via servidores OpenAI-compatíveis, com 100% de privacidade e operação offline.
- O usuário é o único soberano do seu poder computacional e dos seus dados.

### 2.5 Princípio V: Fidelidade Contratual com Cláusula de Parada e Emenda Segura
- **Na Concepção:** Debate implacável pela Via Negativa e análise de tradeoffs para desenhar planos cirúrgicos.
- **Na Implementação:** Dever de fidelidade do agente executor ao plano aprovado (`DECISION.md` / `PACKET.md`), sem insubordinação ou corte unilateral silencioso.
- **Cláusula de Parada de Emergência:** Se durante a execução for descoberta uma vulnerabilidade crítica, inviabilidade física ou premissa falsificada, o agente DEVE interromper a execução e emitir um Laudo de Inconformidade para re-deliberação rápida, eliminando o paradoxo entre obediência cega e bom senso de engenharia.

### 2.6 Princípio VI: Ergonomia Unix & Interfaces de Frugalidade $O(1)$
- O terminal Unix e processos padrão são o canal prioritário de interação para agentes autônomos (zero sobrecarga de tokens).
- Qualquer integração MCP é admissível desde que comprove em benchmark reproduzível um custo de contexto $O(1)$ com teto de tokens delimitado por schema, paginação sob demanda e isolamento de falha.

---

## 3. Consequências & Aplicação Prática

1. **Auto-Consistência:** Vetos nominais ou dogmáticos estão formalmente proibidos; toda exigência técnica deve ser acompanhada de métrica e falsificador.
2. **Ciclo de Inovação Desbloqueado:** Branches de *spike* e laboratórios locais (`tare.tools.local-labs`) operam com liberdade criativa total para testar limites de GPU/LLM antes da purga e consolidação no núcleo.
3. **Soberania do Usuário:** Nenhuma funcionalidade pode forçar o usuário a assinar provedores de nuvem fechados se houver alternativa aberta e local viável.
