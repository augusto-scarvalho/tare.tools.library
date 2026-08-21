# PROPOSTA FORMAL DE GOVERNANÇA: RFC-004 (Colheita Arquitetural do SpecGraph Histórico e Alinhamento com a Doutrina Frugal)

## 🎯 1. Objetivo Raiz & Escopo Nuclear (Âncora Imutável)
- **Pergunta Fundamental:** Quais conceitos, formalismos e estruturas dos planos históricos do SpecGraph (elaborados pelo Claude Fable em `OneDrive/Documentos/projetos/SpecGraph`) devem ser resgatados e incorporados ao `tare.tools.specgraph` atual, e o que deve ser purgado pela Via Negativa para manter o sistema 100% frugal, ágil e agnóstico de hardware?
- **Critério de Sucesso:** Definir o alinhamento definitivo entre os 8 estágios históricos do Fable e a implementação prática atual (68 testes passando), preservando as "joias" conceituais sem importar complexidade acidental.
- **Não-Objetivos (Via Negativa):**
  - Proibir re-introdução de Rust/PyO3 complexo onde o Python AST puro já resolve com <10ms de latência.
  - Proibir frameworks pesados de BDD/Gherkin onde o pytest nativo com `@pytest.mark` e EARS cobre os critérios de aceitação.
  - Proibir bancos de dados OLAP/DuckDB para metadados que cabem em JSON Lines atômicos.

---

## 💎 2. As Joias Arquiteturais Resgatadas do Fable (A Serem Mantidas e Integradas)

1. **Rastreabilidade Causal Bidirecional:**
   - *Intenção $	o$ Requisito (EARS) $	o$ Decisão (ADR) $	o$ Símbolo de Código (AST) $	o$ Teste $	o$ Evidência Executável*.
2. **Reviewer Context Bundle (Frugalidade Radical de Contexto):**
   - O conceito do Fable de "empacotador de contexto mínimo" que seleciona cirurgicamente apenas os nós e ranges de código relevantes para a tarefa do agente, cortando >85% de tokens inúteis.
3. **Cálculo de Blast Radius & Análise de Impacto:**
   - Saber exatamente quais testes e especificações precisam ser revalidados quando um arquivo é modificado.
4. **Critérios de Aceitação em Sintaxe EARS com Ponteiros Empíricos:**
   - `WHEN <trigger> [WHILE <state>] THE SYSTEM SHALL <response>` — amarrado a um teste falsificador explícito.
5. **Detecção Proativa de Drift Documental:**
   - Apontar código órfão (sem spec) e especificações governadas por decisões (ADRs) superadas.

---

## ✂️ 3. A Purga por Via Negativa (O Que Foi Descartado dos Planos Antigos)

1. **Rust Core + PyO3 Bindings:** Substituído por Python nativo (AST da stdlib), mantendo zero fricção de compilação em qualquer SO (Windows, Linux, macOS) sem ferramenta de build extra.
2. **Gherkin / Cucumber BDD Overhead:** Substituído por `@pytest.mark.verifies("SPEC-001", "AC-01")` direto nos testes do pytest.
3. **DuckDB / Bancos OLAP Intermediários:** Substituído por manifestos auditáveis em JSON atômico com hash SHA-256.
4. **Hiper-Estagiamento Teórico (8 estágios separados):** Consolidado em uma única biblioteca coesa (`tare.tools.specgraph`) já funcional e testada.

---

## 📜 4. Ponteiros Canônicos para os Planos Originais
- 📁 [`C:/Users/augus/OneDrive/Documentos/projetos/SpecGraph/specs/README.md`](file:///C:/Users/augus/OneDrive/Documentos/projetos/SpecGraph/specs/README.md) (Índice dos 8 Estágios do Fable)
- 📄 [`C:/Users/augus/OneDrive/Documentos/projetos/SpecGraph/docs/ideation/05-specgraph-third-round-synthesis.md`](file:///C:/Users/augus/OneDrive/Documentos/projetos/SpecGraph/docs/ideation/05-specgraph-third-round-synthesis.md)
- 📄 [`C:/Users/augus/OneDrive/Documentos/projetos/SpecGraph/docs/ideation/08-specgraph-architecture-stack-double-diamond.md`](file:///C:/Users/augus/OneDrive/Documentos/projetos/SpecGraph/docs/ideation/08-specgraph-architecture-stack-double-diamond.md)
- 💻 [`C:/projects/tare.tools.specgraph/src/specgraph/`](file:///C:/projects/tare.tools.specgraph/src/specgraph/) (Implementação Atual em Python Puro)

---

## 📜 5. Formato de Parecer Exigido para Cada Assento
```json
{
  "seat": "<google | anthropic | openai>",
  "execution_nonce": "<sentinel_nonce>",
  "verdict": "<APPROVE | REJECT | REVISE>",
  "confidence": 0.95,
  "summary": "<Resumo técnico de 2 a 3 frases>",
  "strengths": ["<Ponto forte 1>", "<Ponto forte 2>"],
  "issues": [
    {
      "severity": "<blocking | non-blocking>",
      "claim": "<Afirmação técnica>",
      "falsifier": "<Condição empírica que falsifica a proposta>"
    }
  ],
  "recommendations": ["<Recomendação 1>"]
}
```
