# 🏛️ DOUTRINA DE ENGENHARIA FRUGAL DE TARE.TOOLS

> **Manifesto e Princípios Soberanos de Arquitetura, Governança e Computação.**  
> *Uma filosofia de engenharia agnóstica de hardware, atemporal, inclusiva e centrada na frugalidade radical de tokens e recursos para qualquer usuário.*

---

## 🧭 1. Os 5 Princípios Fundamentais

### I. A Primazia da Via Negativa (Subtração antes de Adição)
* O software mais confiável, rápido e sustentável é aquele que **evitou complexidade desnecessária**.
* Nenhuma abstração prematura, microsserviço ou camada intermediária deve existir para necessidades hipotéticas (*YAGNI*).
* A biblioteca padrão e os recursos nativos do sistema operacional têm prioridade máxima sobre a introdução de frameworks pesados ou dependências externas proprietárias.

### II. A Regra do Falsificador Empírico (Sem Teste que Falhe = Sem Código)
* Nenhuma decisão técnica, rejeição de plano ou revisão de código é aceita com base em opiniões abstratas ou especulações teóricas.
* Toda crítica precisa ser acompanhada de um **teste de reprodução automatizado (`reproduction_test`)** que demonstre uma quebra real de runtime, contrato ou segurança. Sem falsificador verificável, a objeção é sumariamente descartada.

### III. Liberdade de Computação & Soberania (BYOC — Bring Your Own Compute)
* O ecossistema não impõe barreiras de hardware nem dependências forçadas de nuvem. Ele é projetado para **três realidades de usuários**:
  1. **Usuário Zero-Hardware (Free-Tier):** Opera com custo $0.00 utilizando quotas gratuitas de provedores de fronteira e modelos abertos.
  2. **Usuário Profissional / Empresa (Pay-As-You-Go):** Utiliza chaves de API comerciais de qualquer fornecedor (Google, Anthropic, OpenAI, Moonshot, etc.) gerenciadas com segurança no Keyring do SO.
  3. **Usuário Soberano / Homelab (Local Compute):** Executa modelos locais em qualquer infraestrutura (RTX, Apple Silicon, AMD, Intel ou CPU) via servidores OpenAI-compatíveis (`llama-server`, `vLLM`, `Ollama`, etc.), garantindo privacidade total, zero telemetria e operação offline air-gapped.
* *Premissa Central:* **O usuário é o proprietário dos seus dados e do seu poder computacional.**

### IV. Fidelidade Estrita ao Contrato Deliberado (Separação de Poderes)
* **Na Fase de Concepção e Governança:** Debate livre, plural e impiedoso pela Via Negativa para cortar escopo supérfluo.
* **Na Fase de Implementação:** Uma vez que um contrato ou plano é ratificado (`DECISION.md` / `PACKET.md`), o agente implementador atua com **disciplina cirúrgica**. Não cabe ao implementador sabotar ou descartar requisitos formalmente aprovados; seu dever é entregar a implementação mais simples, limpa e fiel ao contrato.

### V. Ergonomia Unix & CLI First (Frugalidade Radical de Contexto)
* Agentes autônomos e desenvolvedores operam com máxima eficiência através da interface universal do terminal Unix (`stdout`, `stdin`, pipes e `exit codes`), com **zero tokens de injeção de schema**.
* Protocolos de integração com IDEs e sandboxes são mantidos como **gateways minimalistas (<150 tokens)**, banindo servidores inchados (*Fat MCP*) que consomem milhares de tokens do contexto do usuário a cada interação.

---

## 👥 2. Matriz de Arquétipos de Usuários Atendidos

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 🌐 ARQUITETURA INCLUSIVA DE SUBSTRATOS (BYOC — TARE.TOOLS)                                      │
├───────────────────────────────────┬──────────────────────────────────┬──────────────────────────┤
│ 1. DESENVOLVEDOR SEM GPU / FREE   │ 2. ENGENHEIRO / EMPRESA (APIs)   │ 3. SOBERANO / HOMELAB    │
├───────────────────────────────────┼──────────────────────────────────┼──────────────────────────┤
│ • Hardware: Laptop / PC comum     │ • Hardware: Qualquer estação     │ • Hardware: GPU / NPU    │
│ • Provedores: Google AI Free,     │ • Provedores: Chaves comerciais  │ • Provedores: llama.cpp, │
│   NVIDIA NIM Free, Groq, Ollama   │   (OpenAI, Anthropic, Google)    │   vLLM, Ollama, Exo      │
│ • Custo: $0.00 / mês              │ • Custo: Conforme demanda        │ • Custo: Custo elétrico  │
│ • Modo: Nuvem Frugal              │ • Modo: Máxima Potência          │ • Modo: 100% Offline     │
└───────────────────────────────────┴──────────────────────────────────┴──────────────────────────┘
```

---

## 📜 3. Guia de Decisão Atemporal

| Quando Você For... | A Doutrina tare.tools Orienta: |
| :--- | :--- |
| **Criar uma nova ferramenta** | Escreva um utilitário CLI simples com I/O limpo; não crie servidores de RPC complexos. |
| **Revisar o código de outro agente** | Exija um comando de teste que falhe; não reprove por preferência de estilo. |
| **Salvar estado crítico** | Use a biblioteca padrão com arquivos atômicos (`.tmp` + `os.replace`); não instale bancos pesados sem necessidade. |
| **Configurar IA para seu time** | Escolha a melhor combinação de modelos para seu bolso e hardware (BYOC); o motor cuidará do fallback automaticamente. |
| **Iterar em uma deliberação** | Pare na 3ª rodada; se não houver consenso, peça a decisão de um humano em 1 página. |
