# AGENTS.md — tare.tools.library Operating Contract & Tooling Invariants

> **The Central Technical Library & Canonical SSOT of Architectural Knowledge, Specifications, and System Memory.**

---

## 🏛️ 1. Authority & Governance Boundaries (ADR-051 & ADR-052)

`tare.tools.library` is the **Single Source of Truth (SSOT)** for:
* **Decisões Arquiteturais Globais:** [`docs/adr/`](docs/adr/) (ADR-001 a ADR-052).
* **Especificações Funcionais OpenSDD:** [`specs/`](specs/) (`SPEC-KERNEL-001`, `SPEC-SPECGRAPH-001`, `SPEC-BACKLOG-001`, `SPEC-DIALOG-001`, `SPEC-LIBRARY-001`).
* **Experimentos & Benchmarks Empíricos:** [`experiments/`](experiments/) (`EXP-01` a `EXP-05`).
* **Relatórios Forenses de Causa Raiz (RCA):** `docs/post-mortems/`.
* **Memória Histórica Imutável:** [`archaeology/`](archaeology/) (`status: archived_immutable`).

---

## ⚡ 2. Mandatory Agent Tool Protocols (CLI-First)

Todos os agentes de IA (Antigravity, Codex, subagentes e scripts autônomos) DEVEM seguir os 4 protocolos operacionais abaixo:

### 🔹 Protocolo 1: Pre-Task Grounding (Consulta à SSOT antes de Codificar)
Antes de propor designs ou implementar código em qualquer satélite, o agente deve consultar a especificação correspondente para obter os Critérios de Aceitação (`AC-01..N`):
```powershell
# Extrair critérios de aceitação de uma SPEC:
python -m tools.query --spec SPEC-KERNEL-001

# Buscar decisões arquiteturais por conceito ou palavra-chave:
python -m tools.query --search "CAS"
python -m tools.query --adr ADR-051
```

### 🔹 Protocolo 2: Ingestão Automatizada de Novos Artefatos
Ao concluir estudos, benchmarks, sessões de design ou relatórios de incidentes, o agente DEVE usar o motor de ingestão (que calcula SHA-256 e valida duplicatas automaticamente):
```powershell
# Ingerir novo experimento empírico:
python -m tools.ingest --file resultado.md --type experiment --category local-llm --title "Benchmark RTX 3090"

# Ingerir nova decisão ou proposta:
python -m tools.ingest --file adr_draft.md --type adr --title "ADR-053 ..."

# Ingerir transcrição de chat histórico:
python -m tools.ingest --file chat.md --type chat --title "Sessão de Alinhamento 2026-08-19"
```

### 🔹 Protocolo 3: Sincronização do Manifesto Canônico
Sempre que uma nova ADR, SPEC ou experimento for adicionado/modificado, o agente DEVE compilar o manifesto da biblioteca para consumo pelo SpecGraph e Backlog-Graph:
```powershell
# Recompilar catalog/LIBRARY_MANIFEST.json:
python -m tools.build_manifest
```

### 🔹 Protocolo 4: Auditoria de Higiene Documental (Bookkeeper)
Antes de abrir qualquer Pull Request ou concluir releases, o agente DEVE validar que a biblioteca está 100% livre de duplicatas e violações de SSOT:
```powershell
# Executar a suíte de auditoria completa:
python -m tools.bookkeeper.cli audit --root docs
```

---

## 🎯 3. O Mandato Documental Ágil (Invariante Constitucional)

* **Prerrogativa Humana:** Artigos científicos e papers formais são produzidos sob demanda exclusiva do Operador Humano.
* **Mandato dos Agentes:** *“Documentar a coisa certa, no lugar certo, na hora certa”*:
  1. *Nos Satélites de Código:* Apenas documentação operacional direta de APIs, CLI e testes.
  2. *Nos Incidentes:* Relatórios de RCA com medições e hashes em `docs/post-mortems/`.
  3. *Nos Benchmarks:* Logs de hardware e dados empíricos em `experiments/`.
  4. *Nas Decisões Globais:* ADRs canônicas consolidadas em `docs/adr/`.
