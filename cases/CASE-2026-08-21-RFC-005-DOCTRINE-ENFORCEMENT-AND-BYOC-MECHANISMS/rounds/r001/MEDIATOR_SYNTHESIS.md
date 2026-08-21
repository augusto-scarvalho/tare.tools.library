# SÍNTESE DO MEDIADOR CONSTITUCIONAL — RODADA 1

## 1. Consensos Estabelecidos (Imutáveis)
- Contenção segura e determinística de execução no MCP Gateway utilizando argv puro (`shell=False`) e validação canônica de diretório.
- Imposição de teto estrito de contexto (<150 tokens) e priorização da biblioteca padrão via Via Negativa, minimizando a superfície de ataque e latência de inferência.
- Rastreabilidade formal bidirecional entre especificações EARS e testes com `@pytest.mark.verifies`, garantindo falsificabilidade empírica contínua.

## 2. Tensões Dialéticas & Falsificadores Bloqueantes
- **[OPENAI]**: O Frugality Guard não possui política determinística para distinguir dependência necessária de dependência inflada, e o limite de 150 tokens não fixa serialização, tokenizer nem versão.
  - *Falsificador Exigido:* `Duas implementações conformes analisam o mesmo import de requests: uma o rejeita por existir urllib e outra o aceita por requisitos de TLS e ergonomia. Serialize o mesmo schema com tokenizers distintos e obtenha resultados em lados opostos do teto.`
- **[OPENAI]**: O marcador @pytest.mark.verifies cria associação declarativa, mas não demonstra que o teste falsifica o requisito nem que exercita o código normativo correspondente.
  - *Falsificador Exigido:* `Crie um teste marcado com verifies("SPEC-REQ-001") contendo apenas assert True; se specgraph trace aprovar a cobertura, a garantia bidirecional é falsa.`
- **[OPENAI]**: cwd canônico não confina um processo arbitrário: executáveis e argumentos ainda podem acessar caminhos externos, rede, ambiente, subprocessos e recursos ilimitados.
  - *Falsificador Exigido:* `Execute a partir de um cwd permitido um argv Python que leia um arquivo absoluto externo ou invoque um filho persistente; se funcionar, o gateway não é confinado apesar de shell=False e da validação de cwd.`
- **[OPENAI]**: O roteador BYOC mistura política de custo, fornecedores específicos e mecanismos opcionais sem definir descoberta de capacidades, ordem de fallback, limites de contexto ou condição terminal de indisponibilidade.
  - *Falsificador Exigido:* `Ative profile free sem credencial Gemini e sem binário llama.cpp, ou envie um bundle maior que o contexto do SLM; duas implementações podem falhar, truncar silenciosamente ou escolher rotas diferentes sem violar o texto.`
- **[OPENAI]**: EmergencyHaltReceipt não define schema versionado, persistência atômica, código de saída, precedência sobre efeitos pendentes nem comportamento quando o recibo não puder ser gravado.
  - *Falsificador Exigido:* `Torne o destino do recibo somente leitura e provoque risco de integridade; se o executor continuar, improvisar outro destino ou encerrar sem evidência verificável, o contrato não determina um resultado conforme.`
- **[ANTHROPIC]**: O critério de sucesso 'validação de schema < 150 tokens' é inauditável sem tokenizador especificado. Contagem de tokens é dependente de modelo; '150 tokens' não é uma grandeza física até fixar o tokenizador de referência.
  - *Falsificador Exigido:* `Rodar o guard sobre um mesmo schema JSON-RPC com dois tokenizadores distintos (ex: cl100k_base vs tokenizer de um SLM local) e obter contagens divergentes que cruzem o limiar de 150 em direções opostas — o build passa e falha para o mesmo artefato conforme o backend.`

## 3. Descarte por Via Negativa (Anti-Hipertrofia)
- [google] A análise estática de imports do Frugality Guard pode acusar falsos-positivos em importações dinâmicas ou opcionais de desenvolvimento caso não suporte anotações explícitas de exceção. (Classificado como não-bloqueante)
- [google] O roteador BYOC em perfis locais (`llama.cpp`) pode induzir latência excessiva se não houver probe ativo de prontidão do socket antes do despacho da inferência. (Classificado como não-bloqueante)
- [openai] A exigência genérica de 100% de testes unitários é ambígua e pode incentivar cobertura superficial, além de não validar integrações reais com keyring, endpoints e processos locais. (Classificado como não-bloqueante)
- [anthropic] Mecanismo 1 (Frugality Guard) reinventa contratos de dependência já resolvidos por ferramentas instaladas/maduras (import-linter, ruff). Construir um auditor de imports próprio é a hipertrofia que a Via Negativa proíbe. (Classificado como não-bloqueante)
- [anthropic] Mecanismo 3 falha o build para 'código normativo em produção sem falsificador', mas 'código normativo' não tem definição operacional. Sem um predicado decidível, o gate produz falsos positivos e vira fricção burocrática. (Classificado como não-bloqueante)
- [anthropic] Mecanismo 6: 'validação de contenção de diretório canônico' não menciona resolução de symlinks; contenção baseada em prefixo de path é evadível. (Classificado como não-bloqueante)
