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
Antes de propor designs ou implementar código em qualquer satélite, o agente deve consumir a projeção limitada e específica do repositório através do SpecGraph:
```powershell
# Caminho canônico para agentes nos satélites:
specgraph ground --repo tare.tools.kernel `
  --library-manifest C:\projects\tare.tools.library\catalog\LIBRARY_MANIFEST.json `
  --max-bytes 8192 --format json
```

`tare.tools.library` continua dona do conteúdo, ingestão, deduplicação,
publicação e geração do manifesto; não é dependência síncrona direta dos
adaptadores de fornecedor. O Kernel transporta os bytes do comando e o Agent
Runtime os admite antes do provedor. Não há descoberta automática de manifesto.

Somente mantenedores trabalhando dentro da própria Library usam `tools.query`
como ferramenta editorial/diagnóstica direta:

```powershell
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

### 🔹 Protocolo 5: Gestão de Heavy Compute, Malha e Mobilidade (ADR-053, ADR-054 & ADR-055)
**Regra Constitucional:** O laptop `acer-augusto` é estritamente um Thin-Client. Agentes de IA NUNCA devem rodar loops de indexação massiva, benchmarks pesados ou reter bancos vetoriais brutos (> 50 MB) localmente. Toda tarefa de computação pesada DEVE ser despachada para a workstation `aaaaa` (RTX 3090) via `tare.tools.mesh`, e as buscas semânticas devem usar o roteador sensível à latência:
```powershell
# 1. Checar telemetria da GPU (temperatura, VRAM livre, carga CUDA):
python tools/mesh/mesh.py gpu

# 2. Verificar estado e conectividade dos nós da malha:
python tools/mesh/mesh.py status

# 3. Sincronizar alterações de código com a workstation:
python tools/mesh/mesh.py sync aaaaa

# 4. Executar comando ou teste pesado na workstation (WSL2/NVMe):
python tools/mesh/mesh.py exec aaaaa "python tools/indexer/embed_corpus.py --root ."

# 5. Busca semântica com roteamento adaptativo de latência (ADR-055):
# (Consulta a RTX 3090 na mesma LAN em < 10ms; usa fallback leve offline/WAN)
python tools/query.py --semantic "conceito arquitetural" --limit 5

# 6. Uso programático em Python SDK:
from tools.mesh import MeshClient
mesh = MeshClient()
gpu_telemetry = mesh.gpu("aaaaa")
mesh.exec("pytest tests/heavy/", node="aaaaa")
```

### 🔹 Protocolo 6: Governança Criptográfica & Proibição de Simulação Sintética (ADR-057)
**Regra Constitucional:** Agentes de IA são **terminantemente proibidos** de forjar deliberações, simular votos de cadeiras ou criar arquivos em `relay/round_tables/` via ferramentas de escrita direta. Toda deliberação arquitetural DEVE ser executada pelo motor oficial `relay/round_table_engine.py`:
```powershell
# 1. Inicializar caso formal:
python "C:\Users\augus\My Drive\tare.tools\relay\round_table_engine.py" init <CASE_ID> "<TITLE>" <PROPOSAL_FILE> --profile generalist --standalone-offline

# 2. Conduzir rodadas adversariais reais:
python "C:\Users\augus\My Drive\tare.tools\relay\round_table_engine.py" conduct <CASE_ID> --standalone-offline

# 3. Validar a Tríplice Verificação Criptográfica (ADR-057):
# hash(DECISION.md em LF) == frontmatter.round_table_sha256 == journal[FINAL].decision_sha256
python -m unittest tests/test_adr_provenance.py
```

---

## 🎯 3. O Mandato Documental Ágil (Invariante Constitucional)

* **Prerrogativa Humana:** Artigos científicos e papers formais são produzidos sob demanda exclusiva do Operador Humano.
* **Mandato dos Agentes:** *“Documentar a coisa certa, no lugar certo, na hora certa”*:
  1. *Nos Satélites de Código:* Apenas documentação operacional direta de APIs, CLI e testes.
  2. *Nos Incidentes:* Relatórios de RCA com medições e hashes em `docs/post-mortems/`.
  3. *Nos Benchmarks:* Logs de hardware e dados empíricos em `experiments/`.
  4. *Nas Decisões Globais:* ADRs canônicas consolidadas em `docs/adr/`.

### 🔹 Protocolo 6: Doutrina de Engenharia Frugal & Anti-Hipertrofia (RFC-001 / RFC-002 / RFC-003)
Todos os agentes e subagentes que atuam no repositório DEVEM operar sob a **[`Doutrina de Engenharia Frugal`](docs/ENGINEERING_DOCTRINE.md)**:
1. **Via Negativa (Subtração antes de Adição):** O melhor código é aquele que nunca precisou ser escrito. Nunca crie classes, interfaces ou abstrações para casos de uso hipotéticos (*YAGNI*). Use a biblioteca padrão do Python antes de bibliotecas externas.
2. **Regra do Falsificador:** Nenhuma crítica ou rejeição é válida sem um comando de teste automatizado (`reproduction_test`) que falhe na prática.
3. **Ergonomia CLI First:** Ferramentas devem ser primariamente utilitários CLI via terminal (0 tokens de schema). Servidores Fat MCP são proibidos.
4. **Fidelidade ao Contrato:** Uma vez ratificado o `DECISION.md` ou `PACKET.md`, o implementador deve entregar exatamente o que foi acordado, sem insubordinação ou corte de requisitos ratificados.
5. **Liberdade de Computação (BYOC):** Suporte nativo tanto a desenvolvedores sem GPU ($0.00) quanto a empresas (APIs comerciais) e homelabbers (modelos locais offline na RTX 3090).
