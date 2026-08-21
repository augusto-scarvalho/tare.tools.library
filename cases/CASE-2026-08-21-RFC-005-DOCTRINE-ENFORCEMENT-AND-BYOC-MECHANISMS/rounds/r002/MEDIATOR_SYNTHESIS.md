# SÍNTESE DO MEDIADOR CONSTITUCIONAL — RODADA 2

## 1. Consensos Estabelecidos (Imutáveis)
- Adesão consistente ao princípio da Via Negativa e incentivo ao uso estrito da biblioteca padrão para redução de footprint e superfície de ataque.
- Estruturação clara dos 6 pilares de governança com protocolo explícito de contenção e parada emergencial (EmergencyHaltReceipt).
- Adoção de execução por argv puro (shell=False) como baseline segura de execução no MCP Gateway.

## 2. Tensões Dialéticas & Falsificadores Bloqueantes
- **[GOOGLE]**: O teto de contexto de 150 tokens para schemas JSON-RPC permanece inauditável e não-determinístico sem a fixação de um tokenizer canônico de referência ou definição em métrica física invariante (bytes/caracteres minificados).
  - *Falsificador Exigido:* `O mesmo schema JSON-RPC serializado atinge 138 tokens em um tokenizer cl100k_base e 162 tokens no tokenizer do Gemma/Llama, fazendo com que o gate de CI aprove ou reprove o mesmo artefato de forma arbitrária conforme o ambiente.`
- **[GOOGLE]**: O roteador BYOC não especifica matriz determinística de precedência, probe ativo de disponibilidade com timeout para sockets locais, nem tratamento terminal para bundles que excedam a janela de contexto do SLM.
  - *Falsificador Exigido:* `Ao ativar profile: free sem chave de API configurada e sem binário llama.cpp instalado, o roteador entra em estado indefinido ou falha silenciosa sem emitir um EmergencyHaltReceipt com código de erro estruturado.`
- **[GOOGLE]**: A contenção de diretório canônico no MCP Gateway não define resolução de symlinks (Path.resolve) nem sanitização de variáveis de ambiente do processo filho.
  - *Falsificador Exigido:* `Um comando executado dentro de um cwd permitido acessa arquivos confidenciais externos através de um symlink pré-existente ou herda PYTHONPATH/LD_PRELOAD permitindo execução arbitrária fora do escopo confinado.`
- **[OPENAI]**: O Frugality Guard continua sem política determinística e auditável para distinguir dependências necessárias de dependências infladas.
  - *Falsificador Exigido:* `Duas implementações conformes avaliam o mesmo import de requests e chegam legitimamente a decisões opostas com base em urllib, TLS e ergonomia.`
- **[OPENAI]**: O teto de 150 tokens continua sem serialização canônica, tokenizador de referência e versão fixados.
  - *Falsificador Exigido:* `O mesmo schema serializado ou tokenizado por implementações distintas cruza o limiar de 150 tokens em sentidos opostos.`
- **[OPENAI]**: O marcador verifies demonstra apenas associação nominal, não que o teste falsifique o requisito ou exercite seu código normativo.
  - *Falsificador Exigido:* `Um teste contendo somente assert True e marcado com verifies para um requisito é aceito por specgraph trace.`
- **[OPENAI]**: shell=False e cwd validado não confinam acesso a arquivos externos, rede, ambiente, subprocessos ou consumo de recursos.
  - *Falsificador Exigido:* `Um argv Python iniciado no cwd permitido lê um caminho absoluto externo ou cria um processo filho persistente.`
- **[OPENAI]**: O roteador BYOC continua sem descoberta de capacidades, ordem normativa de fallback, limites de contexto e condição terminal de indisponibilidade.
  - *Falsificador Exigido:* `No perfil free sem credencial Gemini e sem llama.cpp, ou diante de bundle excessivo, implementações conformes divergem entre falhar, truncar e selecionar outra rota.`
- **[OPENAI]**: EmergencyHaltReceipt continua sem schema versionado, persistência atômica, código de saída, precedência sobre efeitos pendentes e regra para falha de gravação.
  - *Falsificador Exigido:* `Com o destino do recibo somente leitura, executores conformes podem continuar, escolher outro destino ou parar sem evidência verificável.`

## 3. Descarte por Via Negativa (Anti-Hipertrofia)
- [google] A rastreabilidade estática via @pytest.mark.verifies valida a anotação declarativa, mas não afere se a asserção efetivamente executa o caminho de código normativo correspondente. (Classificado como não-bloqueante)
