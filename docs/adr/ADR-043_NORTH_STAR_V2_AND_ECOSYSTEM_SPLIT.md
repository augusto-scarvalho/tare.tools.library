# ADR-043: North Star 2.0 Architectural Transition, Ecosystem Modular Split, and Adversarial Deliberation Synthesis

> **Status:** SUPERSEDED BY [ADR-045: North Star do Ecossistema tare.tools & tare-kernel (Agent OS 2.0)](ADR-045_ECOSYSTEM_AND_KERNEL_NORTH_STAR.md)  
> **Date:** 2026-08-17 (Superseded on 2026-08-18)  
> **Authors:** Antigravity Mediator, Google Chair (`gemini-3.7-flash-high`), Anthropic Chair (`claude-fable-5-high`), OpenAI Chair (`gpt-5.6-sol-high`)  
> **Context Directory:** `02_harness-architecture`  
> **Canonical Target:** `tare-kernel` (Microkernel Agent OS em 5 Planos)  
>
> **Nota de Linhagem Histórica:** Este documento registra a exploração formal de segurança e congelamento do protótipo v1. Suas premissas hiper-adversariais (AppContainers obrigatórios, SIDs dedicados, chaves offline) foram **formalmente substituídas e desregulamentadas pelo ADR-045** para estabelecer uma experiência de desenvolvedor pragmática, veloz e sem sobre-engenharia no Windows 11. Para referência consultiva de ameaças, consulte [KERNEL_SECURITY_AND_THREAT_MODEL.md](KERNEL_SECURITY_AND_THREAT_MODEL.md).  

---

## 1. Scope / Escopo

Este Architectural Decision Record (ADR-043) formaliza o encerramento do ciclo de pesquisa v1 do `tare.tools`, o congelamento do protótipo monolítico de 187 módulos (`universal-agent-harness-prototype`), o arquivamento do grafo de 174 nós (`work-graph.json`) e a divisão física do ecossistema em repositórios independentes no GitHub centrados no **`tare-kernel` (North Star 2.0)**.

### Decisões Fundamentais Estabelecidas:
1. **Encerramento e Congelamento Formal do v1:** O protótipo legado é classificado permanentemente como `SUPERSEDED_RESEARCH_PROTOTYPE (FROZEN)`. O grafo de 174 nós foi congelado com digest SHA-256 verificado em `continuity/work-graph-v1-archive.json` e mapeado através de `continuity/v1_to_v2_crosswalk.json`.
2. **Topologia Modular em Repositórios Standalone:** O código é desacoplado em pacotes independentes no GitHub para permitir reuso direto em outros projetos de software:
   * `tare-backlog-graph`: Motor de gestão de backlogs em grafo acíclico dirigido (DAG) em Python puro.
   * `watson-dialog-tools`: Suíte de diagnósticos, testes e análise topológica para IBM Watson Assistant (127 testes passando).
   * `tare.tools.research`: Hub de documentação, estudos e ADRs integrado ao GitHub Pages.
   * `tare-kernel`: O microkernel desacoplado em 5 Planos (Data, Control, Assurance, Compute, Experience).
3. **Função Objetivo de Governança:** O desenvolvimento de todo o novo núcleo é estritamente orientado à minimização do tempo até a confiança verificável: $\min(\text{Time-to-Trust})$.

---

## 2. Evidence / Evidências Empíricas & Deliberação Tripartite

### A. Diagnóstico Empírico do Deadlock de Governança no v1
O protótipo v1 operava com acoplamento circular no mesmo processo/filesystem:
$$\text{Agente modifica código} \longrightarrow \text{Hook exige attestation} \longrightarrow \text{Attestation exige CI verde} \longrightarrow \text{CI falha em checagens estáticas circulares do harness}$$
A tentativa de resolver o problema adicionando mais regras estáticas e verificações SLSA agravou o livelock, comprovando que governança e execução de agentes não podem residir no mesmo domínio de privilégio.

### B. Evidência de Interferência de Sincronizadores em Nuvem
A inspeção forense da pasta compartilhada (`My Drive`) revelou 21 instâncias de arquivos duplicados por colisão de sincronização (`coordinator (1).db-shm` a `coordinator (19).db-shm`), demonstrando que armazenar bancos de dados mutáveis e Write-Ahead Logs (WAL) em diretórios sincronizados por nuvem quebra a semântica de `fsync` e introduz corrupção de estado por escritores concorrentes invisíveis.

### C. Síntese das 6 Rodadas da Mesa Redonda Tripartite (Consenso Dialético)
A proposta arquitetural foi submetida a 6 rodadas consecutivas de auditoria adversarial independente entre três assentos de fronteira:

| Rodada | Versão | Votos dos Assentos (Google / Anthropic / OpenAI) | Descobertas Adversariais & Emendas Críticas |
|---|:---:|:---:|---|
| **R1** | `v001` | `REVISE` / `REVISE` / `REVISE` | Identificada circularidade no bootstrap do Notário e inconsistência de Quorum Raft em malha de 2 máquinas físicas. |
| **R2** | `v002` | `APPROVE` / `REVISE` / `REVISE` | Identificado risco crítico do Google Drive como escritor fantasma; exigida migração de estado mutável para `%LOCALAPPDATA%`. |
| **R3** | `v003` | `APPROVE` / `REVISE` / `REVISE` | Falsificada a premissa de que *Job Objects* comuns no Windows impedem `OpenProcess`/`ReadProcessMemory` entre processos do mesmo usuário. |
| **R4** | `v004` | `APPROVE` / `REVISE` / `REVISE` | Identificada vulnerabilidade no token HMAC (risco de Coordenador forjar aprovações); imposta Assinatura Assimétrica Ed25519. |
| **R5** | `v005` | `APPROVE` / `REVISE` / `REVISE` | Formalização de CAS atômico via transação SQLite `BEGIN IMMEDIATE` e Capability Envelopes amarrando repositório e branch. |
| **R6** | `v006` | `APPROVE` / `REVISE` / `REVISE` | Definição de modelo de ameaça honesto no Windows 11 com chaves Ed25519 assinadas offline e isolamento de SID/AppContainer. |

---

## 3. Findings / Especificação da Arquitetura & Invariantes T-01 a T-06

```
+-----------------------------------------------------------------------------------+
| EXPERIENCE PLANE: Web Cockpit (:8765) SSE | 1-Click Nonce Ed25519 | CLI `tare`     |
+-----------------------------------------------------------------------------------+
                                          | Ingress RPC (mTLS / Tailscale)
+-----------------------------------------------------------------------------------+
| CONTROL PLANE: Ingress Gatekeeper | Merge Train (Budget=3) | Landing Saga WAL     |
+-----------------------------------------------------------------------------------+
               |                                            |
+------------------------------+             +--------------------------------------+
| DATA PLANE (Single-Writer):  |             | ASSURANCE PLANE:                     |
| Local SQLite (%LOCALAPPDATA%)|             | Notary Signer Enclave (SID dedicado) |
| CAS BEGIN IMMEDIATE atômico  |             | Hermetic Oracle Runner (AppContainer)|
+------------------------------+             +--------------------------------------+
                                          |
+-----------------------------------------------------------------------------------+
| COMPUTE PLANE: Task Workspaces Efêmeros (Zero escrita no host / Git canônico)     |
+-----------------------------------------------------------------------------------+
```

### Invariantes Normativos Ratificados:

* **T-01 (Bootstrap Genesis & Criptografia Assimétrica Ed25519):**  
  Toda autoridade raiz do cluster é baseada em assinaturas assimétricas Ed25519. O cluster inicializa a partir de um manifesto `genesis.json` assinado **offline pelo Operador Humano**, eliminando qualquer dependência circular de bootstrap do Notário.
* **T-02 (Confinamento Estrito do Compute Plane):**  
  O Compute Plane roda em sandboxes efêmeros (AppContainer / Restricted Token) sem acesso de escrita no disco do host e com rede de saída deny-by-default. Toda alteração trafega como proposta de patch imutável endereçada por hash.
* **T-03 (Substrato Local & CAS Atômico no Data Plane):**  
  Todo o estado mutável (`data.db`, WAL, chaves) reside em `%LOCALAPPDATA%\tare-kernel\`. O Coordenador impõe Fencing Monotônico CAS via transação SQLite `BEGIN IMMEDIATE` atômica:
  $$\text{assert}(expected\_epoch == current\_epoch \land expected\_version == current\_version \land \text{UNIQUE}(op\_id))$$
* **T-04 (Landing Saga WAL de 6 Estados & Egress Exclusivo):**  
  A sincronização com o Git remoto opera sob uma saga compensatória:
  $$\text{PREPARED\_LANDING} \longrightarrow \text{PUSHING} \longrightarrow \text{COMMITTED} \mid \text{RECONCILING} \longrightarrow \text{ABORTED} \mid \text{HUMAN\_PARKED}$$
  Pushes remotos exigem Capability Envelopes assinados por Ed25519 amarrando `(repo_url, target_ref, expected_old_oid, candidate_new_oid, op_id)`. Se o budget de 3 rebases esgotar, a proposta transiciona deterministicamente para `HUMAN_PARKED`.
* **T-05 (Segregação de Privilégios por SID/AppContainer no Windows):**  
  O *Notary Signer Enclave* executa sob uma conta Windows dedicada com DPAPI e ACLs exclusivas. O *Hermetic Oracle Runner* executa em AppContainer estéril com protocolo IPC tipado e `challenge_nonce` supervisionado.
* **T-06 (Aprovação Humana 1-Click Assinada por Chave Privada):**  
  O token de aprovação é emitido por assinatura Ed25519 da chave privada do Operador Humano:
  $$\text{ApprovalToken} = \text{Sign}_{\text{PrivKey\_Human}}(\text{proposal\_sha256} \parallel \text{candidate\_commit} \parallel \text{target\_epoch} \parallel \text{op\_id} \parallel \text{expiry\_utc})$$

---

## 4. Limitations / Limitações e Análise de Ameaças

1. **Modelo de Ameaça do Administrador Local no Windows:** Em estações de desenvolvimento Windows 11 Home onde o usuário interativo detém privilégios administrativos locais (`SeDebugPrivilege`), o isolamento por software é *tamper-evident*, mas não *tamper-proof*. A proteção contra ataques de administrador local é garantida pela exigência de que a chave raiz de assinatura do `genesis.json` resida em custódia offline do operador.
2. **Topologia de 2 Máquinas Físicas:** A malha opera intencionalmente em regime de **Single-Writer com Fail-Closed**. Se o Nó Coordenador Primário falhar, o segundo nó **não se auto-promove** a escritor, prevenindo dual-writers e split-brain. A promoção de um novo líder requer intervenção humana explícita com revogação da chave anterior.
3. **Consistência Dual Git Remoto vs Data Plane:** O Git remoto não implementa 2PC. Falhas de rede durante o push dependem de reconciliação idempotente por `op_id` no Egress Service.

---

## 5. References / Referências Canônicas

1. **ADR-042:** *Arquitetura de Microkernel Desacoplado para o tare.tools Agent OS* (Publicado em 2026-08-17).
2. **RFC 8785:** *JSON Canonicalization Scheme (JCS)* — Serialização determinística de envelopes de atestação.
3. **RFC 8032:** *Edwards-Curve Digital Signature Algorithm (Ed25519)*.
4. **SQLite WAL Architecture:** *Write-Ahead Logging and Concurrency Isolation semantics in SQLite3*.
5. **Jepsen Distributed Systems Safety Analysis:** *Fencing tokens, monotonic epochs, and split-brain prevention under network partitions*.
