# SÍNTESE DO MEDIADOR CONSTITUCIONAL — RODADA 1

## 1. Consensos Estabelecidos (Imutáveis)
- Desacoplamento granular de papéis funcionais com cascatas de fallback explícitas e determinísticas.
- Otimização econômica sólida integrando tiers gratuitos auditados (NVIDIA NIM Free, Gemini Free e inferência local soberana).
- Critérios de falsificação empírica claros (KeyError para papéis desconhecidos, mutabilidade de pin em runtime e validação física de hardware).

## 2. Tensões Dialéticas & Falsificadores Bloqueantes
- **[ANTHROPIC]**: tools/mesh/byoc_router.py:146 — dict(self.DEFAULT_HYBRID_ROLE_MATRIX) é cópia rasa; insert(0, ...) na linha 150 muta a lista compartilhada do atributo de classe. Além disso, o perfil 'hybrid' em DEFAULT_PROFILES referencia o próprio dict de classe e dict(self.DEFAULT_PROFILES) na linha 120 compartilha as instâncias de ComputeProfile. Resultado: um pin em qualquer instância altera todas as outras e persiste entre testes — ordem de execução do pytest passa a influenciar resultados.
  - *Falsificador Exigido:* `Verificação empírica formal`
- **[ANTHROPIC]**: Falsificador 3 não é falsificável hoje: PIN_LOCAL_SOVEREIGN_BEST = 'qwen38-27b.gguf' enquanto a RFC cita 'Qwen3.8-27B-Q4_K_M.gguf' / 'Qwen3.8-27B-UD-Q4_K_XL.gguf'. Nenhum teste toca disco ou /v1/models do llama-server; a 'comprovação empírica' existe apenas no texto.
  - *Falsificador Exigido:* `Verificação empírica formal`
- **[ANTHROPIC]**: tests/test_byoc_router.py:68-77 — o teste de pin insere um alvo idêntico ao que já está na cascata (mesmo modelo qwen), então a asserção passaria mesmo se o prepend fosse ignorado e o item caísse em outra posição. O teste não distingue sucesso de no-op.
  - *Falsificador Exigido:* `Verificação empírica formal`
- **[ANTHROPIC]**: ComputeProfile 'hybrid' tem requires_network=True, tornando is_offline_capable() sem sentido para o único perfil onde a resposta depende do papel. Contrato ambíguo.
  - *Falsificador Exigido:* `Verificação empírica formal`
- **[ANTHROPIC]**: O termo 'cascata' sugere failover automático, mas nada no código itera a lista em caso de falha. Aceitável por YAGNI, mas a RFC deve declarar explicitamente que a semântica de fallback é responsabilidade do chamador.
  - *Falsificador Exigido:* `Verificação empírica formal`
- **[ANTHROPIC]**: Menor: IP Tailscale 100.107.245.30 repetido 8 vezes como literal; perfil 'pro' pinado em 'claude-3-7-sonnet-20250219', modelo obsoleto num documento que se propõe a auditar pinos canônicos.
  - *Falsificador Exigido:* `Verificação empírica formal`

## 3. Descarte por Via Negativa (Anti-Hipertrofia)
- Nenhum item descartado nesta rodada.
