# RFC-006: Matriz Dinâmica de Topologia Híbrida, Integração do Free Tier NVIDIA Build e Pinos Canônicos Auditados

## 1. Sumário Executivo
Esta RFC estabelece a expansão do Roteador Soberano BYOC (ADR-064) através de três emendas de engenharia validadas empírica e formalmente:
1. **4º Perfil (`hybrid` - Matriz Topológica de Roteamento por Papéis):** Permite configurar cascatas granulares e dinâmicas de inferência para cada papel (`seat_google`, `seat_openai`, `seat_anthropic`, `scribe_compactor`, `mediator`, `indexer_embeddings`).
2. **Integração do Free Tier do NVIDIA Build / NIM (`nvidia-build-free`):** Inclusão formal da quota gratuita de avaliação da NVIDIA no pool de computação $0.00 ao lado do Google Gemini Free e CPU local.
3. **Fixação Canônica Auditada do Melhor Modelo Soberano Local:** Fact-check físico no nó `aaaaa` (RTX 3090) confirmando e fixando o **Qwen 3.8 27B** (`qwen38-27b` / `Qwen3.8-27B-Q4_K_M.gguf` / `Qwen3.8-27B-UD-Q4_K_XL.gguf`) como o pino de inferência local padrão.

---

## 2. Hardening e Garantias de Isolamento Implementadas
- **Isolamento Estrito de Estado (`copy.deepcopy`):** O construtor `BYOCRouter` e o método `pin_role_target` realizam cópias profundas completas das matrizes e perfis, garantindo ausência total de poluição de estado entre instâncias.
- **Predicado de Capacidade Offline (`is_offline_capable(role)`):** Avalia capacidade offline tanto no nível de perfil monolítico quanto no nível de papel específico na matriz híbrida.
- **Centralização de Constantes:** Host Tailscale (`DEFAULT_LOCAL_GPU_URL = "http://100.107.245.30:8080/v1"` e `DEFAULT_LOCAL_EMBED_URL = "http://100.107.245.30:8081"`).
- **Falsificadores com Alvo Canário:** Teste unitário em `tests/test_byoc_router.py` usando `canary-sentinel-v1.0` que prova deterministicamente o prepend de pinos e o isolamento entre múltiplas instâncias.
