# RFC-008: Nova Taxonomia Canônica do Repositório, Eliminação de Pastas Fantasmas e Instituição do Arquivo Histórico Controlado (`docs/archive/`)

## 1. Sumário Executivo & Diagnóstico
O repositório `tare.tools.library` acumula resquícios de diretivas legadas que proibiam a alteração de estruturas originais. Como resultado, o repositório apresenta:
1. **Pastas Fantasmas:** Diretórios como `sources/academic/`, `sources/bibliography/`, `proposals/experiments/` que contêm unicamente arquivos `.gitkeep`.
2. **Fragmentação Taxonômica:** 20 pastas numeradas de `research/00_` a `research/19_` contendo placeholders isolados, pastas de staging temporário (`incoming/`) e snapshots datados (`refresh-editions/`).
3. **Falta de Categoria Coringa Controlada:** Ausência de um espaço canônico seguro (`docs/archive/`) para artefatos consolidados de referência histórica que não pertencem ao runtime diário.

---

## 2. A Nova Taxonomia Canônica do Repositório

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

---

## 3. Regras de Governança para o `docs/archive/` (Categoria Coringa)
- **Permitido:** Snapshots consolidados de transições arquiteturais passadas, artefatos de staging formalmente arquivados e relatórios de marcos legados.
- **Proibido (Enforcement via FrugalityGuard):** Zero transcrições brutas de chats com IA, zero dumps de logs voláteis e zero notas confidenciais (estes continuam no Cofre Soberano no nó `aaaaa`).

---

## 4. Plano de Ação & Migração Mecânica
1. Mover `refresh-editions/` e `incoming/` para `docs/archive/`.
2. Consolidar os estudos válidos de `research/` em `docs/research/` e `docs/architecture/`.
3. Purgar todos os `.gitkeep` e diretórios vazios de `sources/`, `proposals/` e `research/`.
4. Atualizar os apontamentos e caminhos nos testes para garantir 100% da suíte passando verde.
