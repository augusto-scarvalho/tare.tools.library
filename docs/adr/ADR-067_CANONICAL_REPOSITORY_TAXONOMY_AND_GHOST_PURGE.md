# ADR-067: Nova Taxonomia Canônica do Repositório, Eliminação de Pastas Fantasmas e Instituição do Arquivo Histórico Controlado (`docs/archive/`)

## Status
**RATIFIED / RATIFICADO_POR_GOVERNANÇA_TRIPARTITE** (Homologado via `CASE-2026-08-21-RFC-008-CANONICAL-REPOSITORY-TAXONOMY-AND-GHOST-PURGE`)

## Data de Ratificação
2026-08-21

## Quórum de Deliberação
- **Modo de Quórum:** `FRONTIER_UNANIMOUS`
- **Assentos Participantes:**
  - Google (`gemini-3.7-flash` via `agy.EXE`)
  - OpenAI (`gpt-5.6-sol` via `codex.exe`)
  - Anthropic (`claude-fable-5-high` via `claude.exe`)
  - Usuário & Mediador Independente (Deliberação Interativa)

---

## 1. Contexto & Diagnóstico
O repositório `tare.tools.library` acumulou uma grave dívida técnica de layout devido à antiga diretiva defensiva de não alterar diretórios existentes. Essa rigidez resultou em dezenas de pastas com apenas `.gitkeep`, 20 pastas numeradas de pesquisa com placeholders vazios e estruturas de staging duplicadas.

---

## 2. Decisão Arquitetural: Nova Taxonomia Canônica

### 2.1 Estrutura Canônica Aprovada
O repositório unifica sua árvore nos seguintes diretórios de primeiro nível:
```
tare.tools.library/
├── cases/              # Processos e deliberações da Mesa Redonda (RFCs 001 a 008)
├── catalog/            # Catálogo mestre, registros de capabilities e ontologia
├── docs/               # Documentação Canônica Ativa
│   ├── adr/            # ADRs 001 a 067
│   ├── architecture/   # Doutrina de engenharia e diagramas de topologia
│   ├── assurance/      # Protocolos formais de validação (CMRP)
│   ├── guides/         # Manuais e guias de auto-cura para usuários
│   ├── research/       # Estudos de engenharia consolidados
│   └── archive/        # Categoria Coringa Controlada (Histórico de referência descontinuado)
├── frontier/           # Ponteiros da fronteira epistêmica e decisões de avanço
├── schemas/            # Schemas JSON canônicos
├── specs/              # Especificações SDD formais em formato EARS
├── templates/          # Templates canônicos de publicação
├── tools/              # Motores de runtime (Mesh, BYOC Router, Lean MCP, Indexer)
└── tests/              # Suíte de testes automatizados e falsificadores de CI
```

### 2.2 Instituição do `docs/archive/` (Categoria Coringa Controlada)
- Destinado a snapshots consolidados de transições passadas (`refresh-editions/`), artefatos de staging formalmente arquivados (`incoming/`) e estudos de referência descontinuados.
- **Invariante de Frugalidade:** Permanece estritamente proibido o uso de `docs/archive/` como depósito de transcrições de chat, dumps brutos de logs ou notas confidenciais (estes pertencem exclusivamente ao Cofre Soberano no nó `aaaaa`).

### 2.3 Purga de Pastas Fantasmas
- Todos os arquivos `.gitkeep` e subpastas vazias em `sources/`, `proposals/`, `research/00..19/` e `experiments/` foram eliminados permanentemente.

---

## 3. Consequências
- Repositório perfeitamente organizado, elegante, previsível e sem artefatos fantasmas.
- Rastreabilidade limpa e direta para desenvolvedores, agentes autônomos e usuários finais.
- 100% da suíte de testes (157 testes) compatibilizada com os novos caminhos canônicos.
