# Developer and Operator Guide: tare.tools.library

Este guia estabelece os padrões operacionais para manipulação, consulta e desenvolvimento no substrato de conhecimento `tare.tools.library`.

## 1. Estrutura Canônica
- `docs/adr/`: Decisões arquiteturais ratificadas (ADRs 001 a 067).
- `docs/architecture/`: Doutrina de engenharia e diagramas de topologia.
- `docs/assurance/`: Protocolos formais de verificação (CMRP).
- `docs/archive/`: Arquivo histórico controlado (snapshots e transições arquivadas).
- `specs/`: Especificações SDD em formato EARS para auto-cura dos agentes.
- `tools/`: Motores de runtime (Lean MCP, BYOC Router, Governance, Policy, Indexer).
- `tests/`: Suíte de testes automatizados e falsificadores contínuos.

## 2. Invariantes de Frugalidade
- Não adicionar transcrições de chat ou logs brutos ao Git (armazenar no Cofre Soberano no nó aaaaa).
- Não criar pastas vazias com `.gitkeep`.
- Manter o repositório sob o orçamento de 50 MB.
