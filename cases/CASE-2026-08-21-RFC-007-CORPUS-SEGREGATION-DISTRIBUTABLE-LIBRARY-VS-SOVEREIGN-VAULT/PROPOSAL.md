# RFC-007: Segregação Arquitetural do Acervo de Conhecimento: Substrato Distribuível (tare.tools.library) vs. Cofre Soberano Privado (Sovereign Vault & Cold Storage)

## 1. Sumário Executivo & Diagnóstico
Atualmente, o repositório `tare.tools.library` acumulou um duplo papel contraditório:
1. **Papel A (Substrato Distribuível de Software):** Pacote de conhecimento canônico, ferramentas de runtime (Lean MCP, BYOC Router, Discovery, Query) e especificações (SDD) distribuído aos usuários finais para habilitar a operação, auto-cura e auto-evolução dos agentes do ecossistema.
2. **Papel B (Depósito Histórico Global / Baú de Arqueologia):** Armazenamento indiscriminado de transcrições brutas de chats (ChatGPT/Claude/Gemini), estudos exploratórios proprietários ("molho secreto"), logs de benchmarks extensos e anotações pessoais.

Essa sobreposição gera **risco grave de vazamento de segredos/propriedade intelectual**, **hipertrofia desnecessária do repositório público** e **poluição do contexto de RAG** dos usuários finais com ruído histórico irrelevante para a operação em tempo de execução.

---

## 2. A Nova Doutrina de Segregação em Duas Camadas

### 2.1 Camada 1: Substrato Distribuível (`tare.tools.library` no GitHub)
O repositório público/distribuível deve ser estritamente minimalista, auditável e orientado ao valor de runtime dos agentes do usuário:
- **`docs/` & `docs/adr/`:** Decisões arquiteturais canônicas (ADRs 001-065), manuais de operação e doutrina de engenharia.
- **`specs/`:** Especificações SDD formais em formato EARS necessárias para verificação e auto-cura.
- **`tools/`:** Mecanismos de runtime (`mesh/`, `governance/`, `policy/`, `discovery/`, `inference/`, `indexer/`).
- **`catalog/`:** Catálogo mestre curado de capacidades e documentos de referência.
- **Critério de Inclusão:** *"Este documento é indispensável para que o agente do usuário final opere, valide contratos ou se auto-cure no ecossistema?"* Se NÃO, o documento **não** pode estar no repositório.

### 2.2 Camada 2: Cofre Soberano & Cold Storage (`tare.tools.vault` / Nó `aaaaa` / Storage Seguro)
Todos os artefatos históricos, exploratórios ou proprietários são preservados em armazenamento soberano e privado:
- **`archaeology/chats/` & Transcrições Brutas:** Histórico de sessões passadas com LLMs.
- **Estudos Proprietários & Molho Secreto:** Formulações de produto, estratégias de negócios e rascunhos confidenciais.
- **Logs de Benchmark Brutos:** Dumps extensos de profiling e testes de estresse.
- **Critério de Inclusão:** *"Este documento possui valor de preservação histórica ou segredo de negócio, mas não é dependência do runtime do usuário."*

---

## 3. Mecanismos Executáveis de Enforcement & Purga

1. **Purga e Desacoplamento do Acervo de `tare.tools.library`:**
   - Remoção de todos os arquivos brutos de `archaeology/chats/` e `experiments/` não-canônicos do working tree do GitHub.
   - Manutenção apenas de amostras canônicas e estudos de referência formalmente catalogados em `docs/`.
2. **Atualização do `FrugalityGuard` e do Crawler (`harvest_corpus.py`):**
   - Inclusão de `archaeology/chats`, `raw_logs`, `transcripts` e padrões de rascunho na lista negra permanente de ingestão (`CRAWL_EXCLUDED_DIRS` e `NOISE_FILENAMES`).
   - Scanner estrito de segredos e propriedades intelectuais antes de qualquer ingestão no `library`.
3. **Budget de Tamanho do Repositório Distribuído:**
   - O repositório `tare.tools.library` deve manter um orçamento total enxuto (< 50 MB), garantindo downloads ultrarrápidos para os usuários finais.

---

## 4. Falsificadores e Critérios de Aceitação
- **Falsificador 1 (Purga Segura):** Execução de script de exportação para o cofre seguro no nó `aaaaa` antes de qualquer deleção local.
- **Falsificador 2 (Invariante de Testes):** A suíte `pytest` do `tare.tools.library` deve passar 100% verde após a segregação.
- **Falsificador 3 (Garantia de Não-Vazamento):** Zero arquivos com padrões de chat dump ou anotações confidenciais no repositório rastreado pelo Git.
