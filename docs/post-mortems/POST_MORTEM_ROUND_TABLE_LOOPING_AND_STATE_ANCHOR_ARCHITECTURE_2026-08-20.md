# 📋 Post-Mortem e Especificação de Arquitetura: Governança Frugal da Mesa Redonda (State Anchor, Local LLM Scribe & Dialectical Compaction)

**Data:** 2026-08-20  
**Caso Referência:** `CASE-2026-08-20-TOOLING-PARADIGM-CLI-VS-MCP`  
**Status da Sessão Anterior:** `SHELVED_INVALID_CONVERGENCE_LOOP`  
**Autor:** Antigravity Mediator, Engenharia de Governança & Augusto  

---

## 1. Sumário Executivo do Incidente
Durante a deliberação sobre o paradigma de consumo de ferramentas (*CLI vs. Lean MCP vs. Fat MCP*), a Mesa Redonda Tripartite executou **51 rodadas consecutivas** ao longo de mais de 1 hora.

### O Descarrilamento de Escopo:
* **Pauta Original:** Frugalidade de tokens, priorização do terminal para agentes avançados e definição de um único gateway despachante para ambientes sandboxed.
* **Resultado Hipertrófico (Rodadas 40 a 51):** Discussão sobre atomismo de `MoveFileExW` no Windows, sincronização de `F_FULLFSYNC` no APFS, normalização de zeros negativos em serializadores JSON e autorizadores de SQLite em nível de byte por célula.

---

## 2. As 4 Causas Raízes Estruturais

| Causa Raiz | Mecanismo de Falha | Consequência no Sistema |
| :--- | :--- | :--- |
| **1. Brecha de Hard-Limit** | `run_full_deliberation` possuía teto de 3 rodadas, mas o comando `conduct` isolado não validava o acumulador global de rodadas. | Scripts iterativos executaram rodadas indefinidamente sem parada mecânica. |
| **2. Viés de Complacência do Mediador** | O Mediador aceitava cegamente qualquer apontamento teórico dos assentos, adicionando mais código à proposta a cada turno. | A proposta cresceu de 50 linhas para mais de 700 linhas de pura complexidade acidental. |
| **3. Entropia & Perda da Âncora Raiz** | O prompt da rodada $N$ continha a proposta integral e os pareceres da rodada $N-1$, sem a pergunta-raiz e critérios de negócio. | Os modelos esqueceram a motivação original e passaram a auditar um banco ACID local em vez de uma diretriz de ferramentas. |
| **4. Loop com Quorum Indisponível** | O assento da Anthropic estava sem quota de sessão (*rate limit*). | O quórum de 3/3 era inatingível, mantendo o caso em loop fantasma. |

---

## 3. Arquitetura de Governança Frugal: O Papel do LLM Local na RTX 3090

Para manter a densidade semântica dos debates sem gastar tokens comerciais de API, a arquitetura divide estritamente as responsabilidades:

```mermaid
flowchart TD
    subgraph FRONTEIRA [Modelos de Fronteira Comerciais: Juízes de Alto Nível]
        G["Google Chair (Gemini 3.7 Flash High)"]
        A["Anthropic Chair (Fable 5 High)"]
        O["OpenAI Chair (Sol 5.6 Pro)"]
    end

    subgraph LOCAL [LLM Local na RTX 3090 (WSL2 / node aaaaa): Custo Zero]
        SUM["1. Escriba Dialético Local:<br>Destila pareceres brutos em Tese/Antítese/Síntese"]
        TRIAGE["2. Triador de Bike-Shedding:<br>Compara issues contra a Âncora e Via Negativa"]
        DIFF_GEN["3. Sintetizador de Dossiê:<br>Monta o Dossiê Enxuto para a Rodada Seguinte"]
    end

    G & A & O -->|"Votos e Textos Brutos (~10k tokens)"| SUM
    SUM --> TRIAGE
    TRIAGE --> DIFF_GEN
    DIFF_GEN -->|"Dossiê Dialético Destilado (~600 tokens)"| G & A & O

    style FRONTEIRA fill:#e8f4f8,stroke:#007bff
    style LOCAL fill:#d4edda,stroke:#28a745
```

---

## 4. O Protocolo de Contexto Frugal em 3 Camadas

Em vez de reenviar textos integrais ou diffs sintáticos cegos, o prompt da Rodada 2 em diante adota a **Estrutura Dialética de Alta Fidelidade**:

### Camada 1: A Âncora Imutável (Root Anchor - Topo do Prompt)
```markdown
## 🎯 OBJETIVO RAIZ & ESCOPO NUCLEAR (IMUTÁVEL):
- Pergunta Original: "Como evitar gastar tokens com MCP e priorizar a CLI?"
- Resultado Esperado: Definir a taxonomia de consumo de ferramentas.
- Via Negativa / Fora de Escopo: Implementações de baixo nível de SO, drivers e concorrência distribuída.
```

### Camada 2: O Dossiê Dialético Estruturado (Gerado a Custo Zero pelo LLM Local)
```markdown
## 🏛️ ESTADO DIALÉTICO DA MESA REDONDA (RODADA 1 ➔ RODADA 2)

### 1. Consensos Estabelecidos (Preceitos Inegociáveis):
- Unanimidade entre os 3 assentos: CLI tem prioridade zero-token; Fat MCP banido; Lean Gateway com 1 tool despachante.

### 2. Tensões e Argumentação da Rodada Anterior:
- Tese OpenAI: Risco de explosão de memória em consultas grandes.
- Contra-Tese Google: Adicionar paginação complexa prejudica a DX e gasta tokens.
- Síntese do Mediador: Adotado streaming interno com teto seguro padrão de 32KB, mantendo a API externa enxuta.

### 3. Registro de Descarte por Via Negativa:
- Objeção Rejeitada: Pedido de driver Win32 customizado descartado por estar fora do escopo.
```

### Camada 3: O Delta Contratual com Ponteiro Criptográfico
```markdown
### 🔄 Δ Alterações na Versão (v001#4a8e... ➔ v002#9f1c...):
- [Seção 3: Envelope Canônico] ➔ MODIFICADA: Adicionado campo "max_bytes": 32768.
- [Seção 4: Implementação] ➔ REDUZIDA: Removido código defensivo de kernel Win32.
```

---

## 5. Invariantes Mecânicos de Execução e Confiabilidade

1. **Hard Limit Inflexível de 3 Rodadas:** Qualquer caso com `current_round > 3` trava com status terminal `HELD_NO_CONVERGENCE`.
2. **Aborto Imediato por Quorum:** Indisponibilidade de qualquer assento por quota/rede congela imediatamente com `HELD_UNAVAILABLE`.
3. **Mecanismo Anti-Filibuster:** Objeções descartadas por *Via Negativa* entram na lista de preclusão e não podem reabrir votação de bloqueio.
4. **Custo e Velocidade:** Redução de $>85\%$ nos tokens de entrada de cada assento e eliminação completa de queima de tokens para tarefas de resumo/síntese.


---

## 6. Lição Aprendida: A Separação de Poderes do Mediador
O maior aprendizado do incidente de 51 rodadas foi reconhecer o **conflito de interesses do agente de chat**. Quando o mesmo agente que programa e dialoga com o usuário tenta atuar como mediador, ele se torna vulnerável à fadiga de contexto e à complacência aditiva. A governança exige um **Mediador Constitucional Isolado**, que opere com contexto frio e mandato explícito de eliminação de hipertrofia técnica.
