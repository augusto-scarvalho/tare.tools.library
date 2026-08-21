# RFC-009: Padronização Universal de Branches, Governança de CI/CD Pipelines e Eliminação de Aliases Legados (`master` vs `main`, `dev` vs `develop`)

## 1. Sumário Executivo & Diagnóstico
Durante a auditoria global do ecossistema `tare.tools` e repositórios satélites, constatou-se descompasso na topologia de branches e configurações de CI:
1. **Divergência de Branch Padrão (`default branch`):** Repositórios legados ou configurados com `master` enquanto ferramentas ativas usam `main`, gerando confusão de commits e avisos de *"main had recent pushes"* no GitHub.
2. **Fragmentação em Integração (`dev` vs `develop`):** Uso misto de `dev` e `develop` entre submódulos, dispersando branches ativas e duplicando setups de CI.
3. **Desalinhamento de Workflows no CI/CD:** Workflows disparando apenas em `main`, ignorando `dev`, ou utilizando versões defasadas de ações que geram alertas de depreciação do runtime do Node.js.

---

## 2. Topologia Universal de Branches (Padrão Canônico)

| Camada de Branch | Nome Canônico | Regra de Governança | Proibições Estritas |
|---|---|---|---|
| **Produção Canônica** | `main` | Branch padrão oficial (`default branch`) em 100% dos repositórios. Protegida contra push direto; exige PR com CI 100% verde. | Proibido o uso de `master`. |
| **Integração Ativa** | `dev` | Branch de integração e testes contínuos de desenvolvimento. | Proibido o uso de `develop`, `development` ou `staging`. |
| **Trabalho Efêmero** | `feat/*`, `fix/*`, `docs/*`, `agent/*`, `refactor/*`, `test/*` | Branches de escopo único. Devem ser apagadas após merge para evitar poluição no repositório. | Proibido branch names sem namespace ou soltos. |

---

## 3. Matriz Canônica de CI/CD Pipelines

Todos os repositórios do ecossistema `tare.tools` devem aderir à especificação canônica de CI:
1. **Gatilhos Padronizados:**
   ```yaml
   on:
     push:
       branches: [main, dev]
     pull_request:
       branches: [main, dev]
   ```
2. **Ambiente Hermético & Node 24+ Compatibility:**
   - Uso de `actions/checkout@v4` e `actions/setup-python@v5`.
   - Execução do Frugality Guard (<50MB Budget).
   - Execução do Falsificador da Raiz Estrita (ADR-067 / RFC-008).
   - Execução da Suíte Completa de Testes com fail-fast.

---

## 4. Plano de Ação e Falsificador Contínuo
1. Alterar a default branch para `main` em todos os repositórios remotos.
2. Sincronizar e unificar `dev` e `develop` em `dev`, purgando branches antigas.
3. Implementar falsificador contínuo `test_branch_and_ci_standardization` garantindo a integridade dos workflows.
