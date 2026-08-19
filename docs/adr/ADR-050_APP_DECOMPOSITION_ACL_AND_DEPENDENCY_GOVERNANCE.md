# ADR-050: Decomposição Poliglota de Aplicações, Camadas Anticorrupção (ACL), Gestão Defensiva de Dependências, Concorrência CAS e Governança de Forks de Alto Desempenho

- **Status:** Ratificado e Aprovado por Consenso Pleno Tripartite (Google, Anthropic e OpenAI — Versão v004 Definitiva)
- **Referência:** `CASE-2026-08-19-APP-DECOMPOSITION-ACL-AND-DEPENDENCY-GOVERNANCE-V4`
- **Data:** 2026-08-19
- **Autores:** Antigravity Mediator sob deliberação tripartite (OpenAI Codex, Google Gemini 3.7, Anthropic Claude Fable 5) e direção de Engenharia Humana
- **Escopo:** `tare.tools.os`, `tare.tools.kernel`, `tare.tools.specgraph`, `tare.tools.backlog-graph`, `tare.tools.dialog-engine`, `tare.tools.research`, `slop.cpp`

---

## 1. Contexto & Fundamentação Teórico-Prática

O desenvolvimento de um **Agent Operating System** para engenharia de software autônoma e colaborativa enfrenta o clássico dilema *"Buy vs. Build"* (Reaproveitamento vs. Construção Própria).

Historicamente, arquiteturas multiagente degeneram em dois extremos patológicos:
1. **Síndrome de Não-Inventado-Aqui (NIH):** Tentativa de reescrever parsers sintáticos, bancos relacionais, motores de inferência e sandboxes do zero, gerando atrasos crônicos, bugs de baixo nível e código frágil.
2. **Acoplamento Parasitário & Inchaço de Dependências (Dependency Bloat):** Adoção descuidada de frameworks e pacotes externos que arrastam árvores gigantes de dependências transitivas, impõem paradigmas invasivos no heap central e acumulam uma dívida impagável de desincronização (*upstream desync debt*).

Para alcançar **máxima performance de execução** sem abrir mão de **modularidade estrita, isolamento operacional e soberania de código**, este ADR estabelece a fundamentação teórica baseada em:
- **Ocultamento de Informação (Parnas, 1972):** Módulos expõem apenas interfaces mínimas e ocultam suas decisões internas de implementação.
- **Camada Anticorrupção / Ports & Adapters (Evans DDD, Cockburn Hexagonal):** O domínio central do OS nunca consome tipos ou estruturas de terceiros diretamente; adapters isolam a variabilidade externa através de contratos versionados e envelopes padronizados.
- **Eficiência Poliglota por Camadas de Custo Físico:** Distribuição tecnológica estrita baseada no custo computacional de cada subdomínio (C++/CUDA no silício, C/POSIX no sandbox, Rust/C-ABI no parsing e Python 3.12+ na orquestração de alto nível).
- **Linearizabilidade & Single-Writer Authoritative Ledger (Lamport, 1978; Liskov, 1988):** Transições de estado autoritativas via Compare-And-Swap (CAS) atômico em processo escritor único local, transações ACID fechadas com receipts imutáveis, reserva de idempotência vinculada a `request_digest` criptográfico e coordenação remota exclusivamente por RPC autenticado.
- **Princípio do Padrão Seguro / Fail-Closed (Saltzer & Schroeder, 1975):** Todo nó ou subsistema que não possuir os pré-requisitos de isolamento ou compatibilidade física deve recusar tarefas de execução de forma explícita, emitindo recibo formal de erro, jamais degradando silenciosamente para um estado inseguro.

---

## 2. Decisões Arquiteturais Propostas (Objetivos In-Scope)

```mermaid
flowchart TD
    subgraph Layer1 ["1. Experience Plane (TypeScript / WebGL)"]
        WebUI["Cockpit Visual & Visualização de Grafos<br>Cytoscape.js / Canvas WebGL (Budget: p95 &le; 16.6ms / 60 FPS)"]
    end

    subgraph Layer2 ["2. Control & Orchestration Plane (Python 3.12+)"]
        OSRemote["Nó Remoto MARM (Worker / Agent)<br>(Gera UUIDv7 + SHA-256 Digest Local)"]
        OSMaster["Nó Mestre / Authoritative State Governor<br>(Single-Writer Authoritative Ledger Service)"]
        KernelContracts["tare.tools.kernel / contracts/v1<br>(JSON Schemas, GraphML, DDL & Topology Doc)"]
    end

    subgraph Layer3 ["3. Anti-Corruption Layer & Storage Substrate (ACL)"]
        AiderAdapter["AiderDriver Adapter (CLI Subprocess)<br>Contrato v1.0.0 | Validação Bidirecional"]
        TreeSitterAdapter["TreeSitter Adapter (C-ABI Pure Bindings)<br>Zero-Copy Parse | Bounds & Timeouts"]
        AuthoritativeLedger["Authoritative SQLite WAL Ledger (Disco Local NVMe)<br>Transação Atômica Única: CAS + Operation Receipt Digest"]
        TelemetryIPC["IPC Telemetry Observer & Benchmarking<br>(Métricas: RSS, Latência JSON, Contenção ERR_CAS_CONFLICT)"]
    end

    subgraph Layer4 ["4. High-Performance Hardware Substrate & Sandbox"]
        SlopCPP["slop.cpp (Fork Otimizado do llama.cpp)<br>Gate 4-Tiers: CUDA sm_86 + Perf + VRAM + Equivalência Greedy"]
        BwrapSandbox["Bubblewrap (bwrap) Sandbox<br>Linux Namespaces (--unshare-net, --ro-bind)<br>Budget: overhead &le; 42ms"]
        PlatformGate{"Platform Matrix & Fail-Closed Gate<br>(Nó Linux vs. Windows Host)"}
    end

    WebUI -->|JSON-RPC / WebSockets (Schema v1)| OSMaster
    OSRemote -->|Authenticated RPC (mTLS / Tailscale)| OSMaster
    OSMaster -.->|Governa Contratos & Topologia| KernelContracts
    OSMaster -->|Subprocess IPC / JSON Schema v1| AiderAdapter
    OSMaster -->|C-ABI Bindings| TreeSitterAdapter
    OSMaster -->|Transação Atômica Local (In-Process)| AuthoritativeLedger
    OSMaster -->|Tailscale HTTP / mTLS| SlopCPP
    AiderAdapter --> PlatformGate
    PlatformGate -->|Host Linux com bwrap| BwrapSandbox
    PlatformGate -->|Host Windows / Sem bwrap| RefuseExecution["ERR_PLATFORM_UNSUPPORTED<br>(Fail-Closed Receipt / Sem Bypass)"]
    AiderAdapter -.-> TelemetryIPC
    AuthoritativeLedger -.-> TelemetryIPC
```

---

### A. Decomposição Poliglota, Matriz de Plataformas & Budgets de Performance

A distribuição tecnológica por domínio de especialização física é parametrizada com uma matriz de suporte de plataformas explícita e limites orçamentários (*budgets*) auditáveis:

| Camada | Tecnologia & Versão Pinada | Plataformas Suportadas | Comportamento Fail-Closed em Plataforma Não-Suportada | Budget de Performance & Hardware de Referência |
| :--- | :--- | :--- | :--- | :--- |
| **Inferência & GPU** | **C++20 / CUDA 12 (`slop.cpp` fork)** | Linux (x86_64) c/ NVIDIA GPU ($\ge \text{sm\_86}$) | Emite `ERR_INFERENCE_HARDWARE_UNAVAILABLE`. Rejeita inferência local; roteia para nó remoto via Tailscale. | Prefill $\ge 600\text{ t/s}$, Geração $\ge 80\text{ t/s}$ (RTX 3090, batch=1, Q4_K_M). TTFT p95 $\le 120\text{ ms}$. |
| **Isolamento & Sandbox** | **C / POSIX (`bubblewrap` v0.9+)** | Linux (Kernel $\ge 5.10$ c/ user namespaces) | **Recusa imediata da task** com receipt `ERR_PLATFORM_UNSUPPORTED`. **Proibido bypass** para execução insegura no host. | Overhead de spawn de processo isolado p95 $\le 42\text{ ms}$ (CPU i7-12700H / AMD 5950X). |
| **Parsing Sintático AST** | **`tree-sitter` (C / Rust C-ABI)** | Linux (x86_64), Windows (x64), macOS (ARM64) | N/A (Multiplataforma universal via C-ABI puro). | Parse incremental p95 $\le 5\text{ ms}$ por arquivo de 10k linhas de código; full parse $\le 50\text{ ms}$ em 100k linhas. |
| **Persistência & Ledger CAS** | **SQLite (WAL + JSONB) Single-Writer** | Linux (x86_64), Windows (x64), macOS (ARM64) | Proibido acesso direto de múltiplos nós via filesystem compartilhado (NFS/SMB). Acesso remoto unicamente via RPC autenticado. | Latência de escrita de transação atômica CAS+Receipt p99 $\le 4\text{ ms}$ (NVMe local do nó escritor autoritativo). |
| **Orquestração & FSM** | **Python 3.12+ (CPython)** | Linux (x86_64), Windows (x64), macOS (ARM64) | N/A (Core do runtime do Agent OS). | Latência de despacho de evento na FSM p99 $\le 2\text{ ms}$. |
| **Cockpit & Visualização** | **TypeScript + WebGL / Cytoscape.js** | Navegadores Modernos (Chrome/Edge/Firefox $\ge 120$) | Degradação graciosa para visualização em tabela estática (DOM). | Renderização contínua de grafos (até 28k nós): tempo de quadro p95 $\le 16.6\text{ ms}$ ($\ge 60\text{ FPS}$). |

---

### B. Camadas Anticorrupção (ACL), Contratos Versionados & Isolamento de Processos

1. **Inviolabilidade do Core de Domínio & AST Linter Obrigatório:**
   - Nenhuma entidade de negócio do `tare.tools.os` ou dos repositórios satélites pode herdar, importar ou depender diretamente de tipos de bibliotecas de terceiros.
   - A pureza do core é assegurada compulsoriamente por um **linter estático de AST arquitetural** executado como pre-commit hook e step bloqueante no CI, impedindo imports fora da stdlib ou de contratos canônicos na raiz de `tare.tools.kernel` e `tare.tools.os`.
   - Os repositórios satélites (`specgraph`, `backlog-graph`, `kernel`, `dialog-engine`) comunicam-se exclusivamente através de esquemas imutáveis definidos em `tare.tools.kernel/contracts/v1/` (JSON Schemas, GraphML, Topologia de Rede e SQLite DDL).

2. **Fronteira de Processo com Schemas Versionados (Request / Response / Receipt):**
   - Toda invocação de ferramenta externa via CLI/subprocesso é estritamente envelopada por contratos bidirecionais versionados (ex: `AiderDriverRequest_v1`, `AiderDriverResponse_v1`).
   - Se o processo externo falhar, travar ou emitir payload malformado, o adapter faz **quarantine fail-closed**, gerando um `ErrorReceipt` estruturado sem corromper a memória do Agent OS.

---

### C. Governança de Forks de Alto Desempenho (`slop.cpp`): Qualification Gate de 4 Tiers

Para manter as alavancas de hardware de baixo nível sem acumular dívida de desincronização (*upstream desync debt*):

```
       Upstream Canonical (llama.cpp @ master)
                │ (Rebase Periódico via Tag Estável)
                ▼
  ┌─────────────────────────────────────────────────────────────┐
  │       Fork slop.cpp (Branch: feature/tare-cuda-levers)      │
  │  • Patch 1: [B2b] DMA Pinning Buffer                        │
  │  • Patch 2: Prefetch Skip-Staging Direct Copy               │
  │  • Patch 3: MoE Hot-Cache Expert Retention                  │
  │  • Patch 4: MTP Speculative Decoding (n=3)                  │
  └──────────────────────────────┬──────────────────────────────┘
                                 │
                                 ▼
              Qualification Gate Automatizado (bless_fork.sh - 4 Tiers)
              • Tier 1: Compilação Limpa sm_86 (CUDA 12)
              • Tier 2: Aferição Física de TTFT & Throughput (Prefill &ge; 600 t/s)
              • Tier 3: Verificação de VRAM Safety & Memory Leak
              • Tier 4: Equivalência Semântica Greedy (Zero Drift de Logits)
```

1. **Patches Atômicos & Isolados:** Nossos diferenciais de aceleração vivem como commits limpos e documentados em cima da branch `master` upstream.
2. **Portão Automatizado de 4 Tiers (`bless_fork.sh`):** Nenhum rebase do upstream é aceito se não passar no qualification gate completo (incluindo teste de equivalência semântica greedy de logits).
3. **Upstream First:** Correções e melhorias genéricas de interesse amplo da comunidade são enviadas como PRs ao upstream canônico para manter nosso delta mínimo.

---

### D. Portão de Admissão de Dependências (Dependency Admission Gate - DAGate)

Toda nova biblioteca candidata a ingressar no ecossistema deve ser aprovada no checklist formal:

| Critério de Admissão | Regra / Limite Máximo | Ação se Falhar |
| :--- | :--- | :--- |
| **Peso Transitivo** | $\le 3$ dependências transitivas diretas. | Rejeitar; adotar alternativa zero-dependency ou rodar via CLI isolado. |
| **Licenciamento** | Licença permissiva (Apache-2.0, MIT, BSD, ISC). | Rejeitar imediatamente se for GPL viral ou restritiva comercial. |
| **Invasividade de API** | Biblioteca opera por dados puros (JSON, bytes, structs) sem obrigar herança de classes base. | Envelopar compulsoriamente em uma Camada Anticorrupção (ACL). |
| **Hermeticidade & Resiliência** | Falha da biblioteca não derruba o processo do Agent OS. | Envelopar em try/except fail-closed com receipt de telemetria. |

---

## 2.1 Não-Objetivos Explícitos (Via Negativa & Fronteiras Arquiteturais)

1. **Sem Reinvenção de Ferramentas Maduras da Indústria:** É proibido construir parsers de AST manuais, bancos relacionais proprietários ou ferramentas caseiras de isolamento quando `tree-sitter`, `sqlite` e `bubblewrap` já resolvem com excelência.
2. **Sem Importação In-Process de Frameworks Pesados:** O `tare.tools.os` não importa pacotes de terceiros diretamente no heap principal; a separação via CLI/subprocesso é obrigatória para ferramentas ricas.
3. **Sem Acoplamento Direto Inter-Satélites:** Os repositórios satélites (`specgraph`, `backlog-graph`, `kernel`, `dialog-engine`) comunicam-se estritamente por schemas de dados (JSON Schema, SQLite, GraphML), nunca por imports de código Python cruzados.
4. **Sem Forks Não-Goverrnados:** É expressamente proibido manter cópias manuais de bibliotecas externas sem um script automatizado de qualificação e política de rebase documentada.
5. **Sem Degradação Insegura de Sandbox:** É terminantemente proibido executar código gerado por LLMs sem isolamento de sandbox no host quando o `bubblewrap` não estiver disponível; a execução deve falhar fechado com código de erro explícito.

---

## 3. Matriz de Falsificação & Rastreabilidade

| Invariante / Requisito | Mecanismo de Verificação | Teste / Falsificador Automatizado | Módulo de Implementação |
| :--- | :--- | :--- | :--- |
| **`REQ-DEC-01`: Pureza do Core de Domínio** | Linter estático de imports via AST em `tare.tools.kernel` | `tests/test_architecture_boundaries.py` | `tests/` & CI Pre-commit |
| **`REQ-DEC-02`: Hermeticidade do Sandbox** | Teste de execução com tentativa de acesso a rede/arquivos host | `EXP-04` & `tests/test_sandboxed_execution.py` | `scripts/bwrap_runner.py` |
| **`REQ-DEC-03`: Qualification Gate do Fork** | Execução de `tools/scripts_sh/bless_fork.sh` no `slop.cpp` | `tests/test_fork_qualification.py` | `slop.cpp/tools/scripts_sh/bless_fork.sh` |
| **`REQ-DEC-04`: Latência de Parsing AST** | Benchmark de parse com `tree-sitter` em base de 100k linhas | `tare.tools.specgraph/tests/test_ast_perf.py` | `tare.tools.specgraph` |
| **`REQ-DEC-05`: Single-Writer CAS Concurrency** | Teste de contenção paralela com 100 threads escritoras | `tests/test_single_writer_cas.py` | `tare.tools.kernel/data_plane` |

---

## 4. Roadmap de Implementação

1. **Fase 1 (Camada de Contratos & Schemas):** Criação dos schemas canônicos v1 em `tare.tools.kernel/contracts/v1/` e linter de AST arquitetural.
2. **Fase 2 (Adapters de Isolamento CLI & TreeSitter):** Implementação dos adapters isolados de `tree-sitter` e `AiderDriver` com receipts JSON imutáveis.
3. **Fase 3 (Gate de 4 Tiers no `slop.cpp`):** Automação do script `bless_fork.sh` com validação de equivalência semântica greedy de logits.
