# SÍNTESE DO MEDIADOR CONSTITUCIONAL — RODADA 2

## 1. Consensos Estabelecidos (Imutáveis)
- Desacoplamento granular e determinístico de papéis operacionais (seat_google, seat_openai, seat_anthropic, scribe_compactor, mediator, indexer_embeddings).
- Excelente alavancagem econômica combinando tiers gratuitos auditados (NVIDIA NIM Free, Gemini Free) com soberania local.
- Modelo conceitual claro para parametrização dinâmica de rotas de inferência sem necessidade de recompilação.

## 2. Tensões Dialéticas & Falsificadores Bloqueantes
- **[GOOGLE]**: Delta vazio nesta rodada ({}), postergando as correções indispensáveis apontadas na síntese da Rodada 1.
  - *Falsificador Exigido:* `Verificação empírica formal`
- **[GOOGLE]**: Risco de contaminação de estado global e flaky tests devido ao uso de cópia rasa (shallow copy) na matriz de papéis e nos perfis padrão ao executar mutações como insert.
  - *Falsificador Exigido:* `Verificação empírica formal`
- **[GOOGLE]**: Asserção de teste em test_byoc_router.py vulnerável a falso positivo por reutilizar o mesmo alvo já presente na cascata.
  - *Falsificador Exigido:* `Verificação empírica formal`
- **[GOOGLE]**: Ambiguidade no contrato de is_offline_capable() quando aplicado ao perfil 'hybrid', cujo suporte offline varia por papel funcional.
  - *Falsificador Exigido:* `Verificação empírica formal`
- **[OPENAI]**: A cópia rasa da matriz e o compartilhamento do perfil hybrid permitem que pin_role_target mutile estado de classe e contamine outras instâncias e testes.
  - *Falsificador Exigido:* `Verificação empírica formal`
- **[OPENAI]**: O Falsificador 2 usa alvo já presente na cascata e não prova que o prepend foi efetivamente aplicado.
  - *Falsificador Exigido:* `Verificação empírica formal`
- **[OPENAI]**: O Falsificador 3 não verifica disco nem /v1/models e usa identificador diferente dos nomes GGUF declarados.
  - *Falsificador Exigido:* `Verificação empírica formal`
- **[OPENAI]**: requires_network=True no perfil hybrid contradiz a capacidade offline dependente do papel.
  - *Falsificador Exigido:* `Verificação empírica formal`
- **[OPENAI]**: A RFC não define que a execução do failover da cascata pertence ao chamador.
  - *Falsificador Exigido:* `Verificação empírica formal`
- **[OPENAI]**: O endpoint Tailscale permanece duplicado e o pino claude-3-7-sonnet-20250219 continua obsoleto.
  - *Falsificador Exigido:* `Verificação empírica formal`
- **[ANTHROPIC]**: byoc_router.py:146 — dict(self.DEFAULT_HYBRID_ROLE_MATRIX) é cópia rasa; insert(0, ...) em :150 muta a lista do atributo de classe. Estado vaza entre instâncias e entre testes (ordem do pytest passa a importar). Não corrigido.
  - *Falsificador Exigido:* `Verificação empírica formal`
- **[ANTHROPIC]**: byoc_router.py:120 — dict(self.DEFAULT_PROFILES) compartilha as instâncias ComputeProfile, inclusive o 'hybrid' que aponta para o próprio DEFAULT_HYBRID_ROLE_MATRIX. Não corrigido.
  - *Falsificador Exigido:* `Verificação empírica formal`
- **[ANTHROPIC]**: byoc_router.py:10 — PIN_LOCAL_SOVEREIGN_BEST='qwen38-27b.gguf' diverge dos nomes físicos citados na RFC (Qwen3.8-27B-Q4_K_M.gguf / -UD-Q4_K_XL.gguf). Falsificador 3 continua infalsificável: nenhum teste consulta disco ou /v1/models.
  - *Falsificador Exigido:* `Verificação empírica formal`
- **[ANTHROPIC]**: tests/test_byoc_router.py:68-77 — o teste de pin insere alvo igual ao já presente na cascata; não distingue prepend real de no-op. Não corrigido.
  - *Falsificador Exigido:* `Verificação empírica formal`
- **[ANTHROPIC]**: byoc_router.py:113 — perfil 'hybrid' com requires_network=True torna is_offline_capable() ambíguo para o único perfil em que a resposta depende do papel. RFC ainda não define o contrato.
  - *Falsificador Exigido:* `Verificação empírica formal`
- **[ANTHROPIC]**: RFC não declara que a semântica de failover da 'cascata' é responsabilidade do chamador (nada no código itera a lista em falha).
  - *Falsificador Exigido:* `Verificação empírica formal`
- **[ANTHROPIC]**: byoc_router.py:96 — 'pro' pinado em claude-3-7-sonnet-20250219, modelo obsoleto, num documento cujo título promete 'pinos canônicos auditados'. IP 100.107.245.30 repetido 8x como literal.
  - *Falsificador Exigido:* `Verificação empírica formal`

## 3. Descarte por Via Negativa (Anti-Hipertrofia)
- Nenhum item descartado nesta rodada.
