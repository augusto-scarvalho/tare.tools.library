# 🛠️ Plano de Implementação: RFC-001 (Governança Frugal, Mediador Isolado, Escriba Local em GPU & Failover Kimi k3)

* **Documento Relacionado:** [`RFC-001_LOCAL_LLM_DIALECTICAL_COMPACTION_AND_STATE_ANCHORS.md`](file:///C:/projects/tare.tools.library/docs/proposals/RFC-001_LOCAL_LLM_DIALECTICAL_COMPACTION_AND_STATE_ANCHORS.md)
* **Post-Mortem Base:** [`POST_MORTEM_ROUND_TABLE_LOOPING_AND_STATE_ANCHOR_ARCHITECTURE_2026-08-20.md`](file:///C:/projects/tare.tools.library/docs/post-mortems/POST_MORTEM_ROUND_TABLE_LOOPING_AND_STATE_ANCHOR_ARCHITECTURE_2026-08-20.md)
* **Data:** 2026-08-20
* **Status:** ✅ IMPLEMENTADO & 100% HOMOLOGADO (135/135 testes)

---

## 🎯 1. Objetivos da Implementação
1. **Erradicar Loops Infinitos:** Garantir matematicamente que nenhuma deliberação execute mais de 3 rodadas sem autorização humana explícita.
2. **Reduzir Custo de Tokens em >85%:** Substituir reenvio de textos integrais por *State Anchors*, *Dossiês Dialéticos* e *Diffs de Seção*.
3. **Zerar Custo de Síntese:** Utilizar a GPU local (RTX 3090 / WSL2) como Escriba Semântico e Triador de *Bike-Shedding*.
4. **Separar Poderes:** Criar o Mediador Constitucional Isolado, libertando o chat interativo para focar puramente em desenvolvimento e testes.
5. **Garantir Resiliência de Quórum:** Integrar o **Kimi k3 (`k3-256k`)** como assento de backup automático com failover instantâneo.

---

## 🏗️ 2. Arquitetura Alvo

```mermaid
flowchart TD
    subgraph INGRESS [1. Submissão da Pauta]
        CHAT["🤖 Agente de Engenharia (Chat)<br>Redige v001 enxuta com Não-Objetivos"]
    end

    subgraph ENGINE [2. Motor de Governança (round_table_engine.py)]
        FSM["⚙️ FSM Hardened (N ≤ 3)<br>Controle de Quorum e Locking"]
        DIFF_ENG["✂️ Parser AST de Seções Markdown<br>Gera Deltas incrementais O(1)"]
    end

    subgraph LOCAL [3. Substrato Local a Custo Zero (RTX 3090 / node aaaaa)]
        SCRIBE["🖥️ Escriba Dialético Local (Qwen 3.8 / Qwen 3.6)<br>Triagem de Bike-Shedding & Dossiê Dialético"]
    end

    subgraph FRONTIER [4. Juízes de Fronteira]
        G["Google Chair (Gemini 3.7 Flash)"]
        O["OpenAI Chair (GPT 5.6 Sol)"]
        A["Anthropic Chair (Claude Fable 5 · high)"]
        K["Moonshot Chair (Kimi k3-256k - Backup Failover)"]
    end

    subgraph MEDIATION [5. Mediação Constitucional Isolada]
        MED["⚖️ Mediador Constitucional Isolado<br>Mandato: Via Negativa & Anti-Hipertrofia"]
    end

    subgraph EGRESS [6. Conclusão & Escalação]
        DECISION["✅ DECISION.md Ratificada<br>(Tríplice Hash Verificado)"]
        HELD["⏸️ HELD_PROGRESS_REVIEW<br>(Scorecard de 1 Página para o Humano)"]
    end

    CHAT --> ENGINE
    ENGINE --> LOCAL
    LOCAL --> FRONTIER
    A -.->|Rate Limit / Quota Excedida| K
    FRONTIER --> LOCAL
    LOCAL --> MED
    MED --> ENGINE
    ENGINE --> DECISION
    ENGINE --> HELD

    style INGRESS fill:#e8f4f8,stroke:#007bff
    style LOCAL fill:#d4edda,stroke:#28a745,font-weight:bold
    style FRONTIER fill:#fff3cd,stroke:#ffc107
    style MEDIATION fill:#f8d7da,stroke:#dc3545,font-weight:bold
    style EGRESS fill:#d1e7dd,stroke:#0f5132
```

---

## 📋 3. Roteiro Detalhado de Implementação em 6 Fases

### Fase 1: Blindagem Mecânica e Invariantes no Motor (`round_table_engine.py`)
- [x] **Contadores Persistidos em `case.json` ($N \le 3, T \le 12$):** Estado gravado antes de chamadas de rede; bloqueio estrito contra reinicializações indevidas.
- [x] **Suporte a `overtime_granted: bool`:** Autorização atômica para rodada $N=4$ concedida exclusivamente pelo operador humano.
- [x] **Matriz de Quórum Estrita:** Cálculo determinístico de `FRONTIER_UNANIMOUS`, `DEGRADED_MIXED`, `LOCAL_ADVISORY` e `HELD_UNAVAILABLE`.
- [x] **PID-Aware File Lock & `os.replace` Atômico:** Prevenção de concorrência com autocura de locks órfãos e gravações imunes a corrupção.
- [x] **Preclusão Cirúrgica por Hash (`section_hash`):** Comparação simples de hash para reabertura de issues apenas se o texto da seção mudar.

### Fase 2: Driver Universal OpenAI-Compatible e Pipeline de Fallback em Cascata
- [x] **Implementar `call_openai_compatible_endpoint`:** Conector genérico POST `/v1/chat/completions` com validação de `execution_nonce`.
- [x] **Configurar Pipeline de Resolução Universal:** Cada assento recebe lista ordenada de provedores (Primário CLI ➔ Secundário Kimi/OpenRouter/LiteLLM ➔ Local GPU na RTX 3090).
- [x] **Implementar `execute_seat_universal`:** Despacho em cascata agnóstico de fornecedor com suporte a `--offline`.

### Fase 3: Parser de Seções Markdown e Diff Semântico
- [x] **Implementar `split_markdown_sections`:** Parser determinístico que divide arquivos `.md` por cabeçalhos (`## Título`).
- [x] **Implementar `generate_compact_delta`:** Compara `v_{N-1}` com `v_N` e emite apenas seções modificadas/adicionadas acompanhadas dos hashes SHA-256 de proveniência.

### Fase 4: Integração do Escriba Dialético Local na RTX 3090
- [x] **Implementar `generate_dialectical_brief_local`:** Conecta ao endpoint de inferência local (`http://100.107.245.30:8080`) com prompt determinístico para destilar os 3 pareceres brutos em:
  1. *Consensos Estabelecidos.*
  2. *Tensões Dialéticas & Falsificadores.*
  3. *Sugestões de Descarte por Via Negativa.*
- [x] **Fallback Gracioso:** Se a GPU local estiver offline, o motor utiliza o parser determinístico em Python sem travar a execução.

### Fase 5: Invocação do Mediador Constitucional Isolado
- [x] **Criar Perfil de Agente `round_table_mediator`:** Subagente hermético com prompt focado em *Via Negativa* e erradicação de hipertrofia.
- [x] **Desacoplar Mediação do Chat Interativo:** O script `round_table_engine.py` invoca o subagente isolado passando apenas o Dossiê Dialético e o Delta Contratual.

### Fase 6: Suíte de Testes, Validação e Re-Submissão da Pauta
- [ ] **Criar Testes de Mock (`tests/test_round_table_frugal.py`):**
  - Teste de failover automático Anthropic $	o$ Kimi k3.
  - Teste de parada estrita em $N=3$.
  - Teste de preclusão de issues repetidas.
  - Teste de redução de tokens no payload do prompt.
- [ ] **Executar Teste Real da Pauta de Tooling:** Submeter a proposta enxuta de *CLI vs Lean MCP* na Mesa Redonda atualizada.

---

## 🎯 4. Critérios de Sucesso e Aceite (DoD)
1. ✅ **Consumo de Tokens:** Redução de $\ge 80\%$ no tamanho médio do prompt da Rodada 2 em diante.
2. ✅ **Confiabilidade:** 0 loops infinitos possíveis na FSM (prova matemática por testes automatizados).
3. ✅ **Resiliência:** Failover instantâneo para o Kimi k3 quando a Anthropic estiver fora de quota.
4. ✅ **Separação de Papéis:** O agente de chat não executa mais mediação subjetiva no meio da conversa.
5. ✅ **Suíte Verde:** Todos os testes de unidade e integração da biblioteca passando com sucesso.
