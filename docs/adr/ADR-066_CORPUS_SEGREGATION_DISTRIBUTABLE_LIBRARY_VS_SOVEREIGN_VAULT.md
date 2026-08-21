# ADR-066: Segregação Arquitetural do Acervo de Conhecimento: Substrato Distribuível (tare.tools.library) vs. Cofre Soberano Privado (Sovereign Vault)

## Status
**RATIFIED / RATIFICADO_POR_GOVERNANÇA_TRIPARTITE** (Homologado via `CASE-2026-08-21-RFC-007-CORPUS-SEGREGATION-DISTRIBUTABLE-LIBRARY-VS-SOVEREIGN-VAULT`)

## Data de Ratificação
2026-08-21

## Quórum de Deliberação
- **Modo de Quórum:** `FRONTIER_UNANIMOUS`
- **Assentos Participantes:**
  - Google (`gemini-3.7-flash` via `agy.EXE`)
  - OpenAI (`gpt-5.6-sol` via `codex.exe`)
  - Anthropic (`claude-fable-5-high` via `claude.exe`)
  - Mediador Independente (Síntese Dialética Autônoma)

---

## 1. Contexto & Diagnóstico
O repositório `tare.tools.library` acumulava artefatos de naturezas conflitantes: de um lado, o substrato canônico de software, especificações SDD e ferramentas de runtime necessárias para os usuários finais; do outro, transcrições brutas de chats com IA, logs de benchmarking pesados e formulações proprietárias. Essa sobreposição representava risco de vazamento de propriedade intelectual, hipertrofia e poluição de RAG.

---

## 2. Decisão Arquitetural: A Doutrina das Duas Camadas

### 2.1 Camada 1: Substrato Distribuível (`tare.tools.library` no GitHub)
O repositório rastreado pelo Git contém estritamente o pacote de runtime:
1. **`docs/` e `docs/adr/`:** Decisões arquiteturais (ADRs 001-066), doutrina de engenharia e manuais.
2. **`specs/`:** Especificações SDD formais em formato EARS para conformidade mecânica e auto-cura.
3. **`tools/`:** Motores de runtime (`mesh/`, `governance/`, `policy/`, `discovery/`, `inference/`, `indexer/`).
4. **`catalog/`:** Catálogo mestre curado de capacidades e índices.
5. **Orçamento Máximo de Repositório:** Mantido sob teto estrito (< 50 MB total rastreado).

### 2.2 Camada 2: Cofre Soberano & Cold Storage (`tare.tools.vault` / Nó `aaaaa`)
Armazenamento privado e criptograficamente verificado no nó `aaaaa` (`/home/augus/vault/corpus_archive/` com `MANIFEST.sha256`):
1. **`archaeology/chats/`:** Histórico de conversas, minerações brutas e prompts de sessões passadas.
2. **Estudos Proprietários & Molho Secreto:** Formulações confidenciais e estratégias de negócios.
3. **Logs Extensos de Benchmarking:** Dumps pesados de testes de estresse.

### 2.3 Mecanismos Executáveis de Enforcement
1. **Quarentena via `.gitignore`:** Ignora permanentemente `archaeology/chats/`, `experiments/`, `vault/`, `_handoff/` e artefatos de scraping.
2. **Falsificadores Contínuos em CI (`tests/test_frugality_guard.py`):**
   - `test_repo_tracked_size_budget`: Valida teto < 50 MB.
   - `test_no_raw_chat_dumps_tracked`: Falha imediatamente se qualquer dump ou transcrição de chat for rastreada no Git.
   - `test_gitignore_quarantines_archaeology_and_experiments`: Valida a presença obrigatória das regras de quarentena.

---

## 3. Consequências
- Repositório 100% livre de segredos, rascunhos ou transcrições de chat.
- RAG do usuário final limpo e focado estritamente em valor de runtime e especificações canônicas.
- Preservação integral do histórico corporativo no Cofre Soberano do nó `aaaaa`.
