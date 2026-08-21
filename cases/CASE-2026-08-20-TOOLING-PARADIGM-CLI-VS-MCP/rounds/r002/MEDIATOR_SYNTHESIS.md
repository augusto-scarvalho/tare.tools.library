# SÍNTESE DO MEDIADOR CONSTITUCIONAL — RODADA 2

## 1. Consensos Estabelecidos (Imutáveis)
- Frugalidade estrita de contexto (<150 tokens) eliminando o desperdício massivo de tokens de sistema inerente ao paradigma Fat MCP.
- Aderência à filosofia Unix de componibilidade através de fluxos padronizados e envelope estruturado de telemetria (exit_code, duration_ms, timed_out).
- Preserva a interface frugal O(1), a orientação CLI First e o envelope estruturado de telemetria.

## 2. Tensões Dialéticas & Falsificadores Bloqueantes
- **[GOOGLE]**: A manutenção da assinatura `command: list[str] | str` com mera 'preferência' por lista viola o princípio de falha fechada, permitindo injeção de shell ou parsing inconsistente de argumentos entre plataformas POSIX e Windows.
  - *Falsificador Exigido:* `A invocação de `exec_command('sh -c "cat /etc/passwd"', cwd=workspace)` ou passagem de payload com operadores de controle como string ser aceita pelo gateway, demonstrando que a garantia de `shell=False` não é aplicada de forma determinística.`
- **[GOOGLE]**: A qualificação da Camada 2 como 'sandbox com contenção estrita' apoiada apenas na validação de `cwd` é tecnicamente insustentável, pois não restringe acessos a arquivos fora do workspace via caminhos absolutos, variáveis de ambiente ou chamadas diretas de sistema.
  - *Falsificador Exigido:* `A execução de `exec_command(['python', '-c', 'import os; print(os.path.exists("/etc/hosts"))'], cwd=workspace)` acessar com sucesso recursos do host fora da raiz do workspace temporário sem bloqueio no nível de sistema operacional.`
- **[OPENAI]**: A validação de cwd não confina o processo: caminhos absolutos, links simbólicos, variáveis de ambiente, arquivos de resposta e subprocessos ainda podem produzir efeitos fora do workspace.
  - *Falsificador Exigido:* `pytest -q tests/test_gateway_confinement.py deve provar, em workspace temporário, que tentativas por caminho absoluto, symlink, variável de ambiente, subprocesso e arquivo de resposta falham fechadas e não deixam efeitos externos.`
- **[OPENAI]**: O contrato command: list[str] | str mantém semântica ambígua e incompatível com a garantia de execução sem interpretação de shell.
  - *Falsificador Exigido:* `pytest -q tests/test_gateway_exec_contract.py deve provar que apenas argv explícito list[str] é aceito e que strings contendo operadores de shell são rejeitadas sem qualquer execução colateral.`
- **[ANTHROPIC]**: A nomenclatura 'sandbox confinado' e 'contenção estrita' persiste sem qualquer camada de SO (namespaces/containers/seccomp). cwd + shell=False + timeout definem apenas o diretório de trabalho; não impedem leitura/escrita por caminho absoluto, egress de rede ou consumo do host.
  - *Falsificador Exigido:* `Executar exec_command(['python','-c','open("/etc/passwd").read()'], cwd=<workspace>) e um comando de egress de rede a partir do cwd confinado: se ambos rodam, a alegação de sandbox está falsificada. Nenhum tests/test_gateway_confinement.py foi entregue provando falha-fechada para caminho absoluto, symlink, env var, subprocesso e arquivo de resposta.`
- **[ANTHROPIC]**: A assinatura mantém command: list[str] | str e apenas 'prefere' lista. 'Preferência' não é contrato; a forma str anula a garantia shell=False e reabre injeção de shell.
  - *Falsificador Exigido:* `exec_command('rg foo; rm -rf .', cwd=...) — se a forma string alcança um shell, executa payload arbitrário. Nenhum tests/test_gateway_exec_contract.py foi entregue demonstrando que strings com operadores de shell são rejeitadas e que apenas argv explícito é aceito.`

## 3. Descarte por Via Negativa (Anti-Hipertrofia)
- [google] O envelope de resposta não especifica limites máximos de saída (`max_output_bytes`) nem estratégia de truncamento seguro, expondo o gateway e o agente a estouro de buffer ou exaustão de memória. (Classificado como não-bloqueante)
