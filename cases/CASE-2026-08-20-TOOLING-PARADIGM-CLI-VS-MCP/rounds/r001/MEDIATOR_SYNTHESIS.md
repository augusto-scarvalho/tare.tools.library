# SÍNTESE DO MEDIADOR CONSTITUCIONAL — RODADA 1

## 1. Consensos Estabelecidos (Imutáveis)
- Redução drástica do overhead de system prompt ao transicionar de schemas O(N) para uma interface frugal O(1) (<150 tokens), otimizando o Time-To-First-Token (TTFT) e o raciocínio útil do modelo.
- Aderência à filosofia Unix de componibilidade através de fluxos padronizados (stdin/stdout/stderr, exit codes e JSON/JSONL estruturado), simplificando a testabilidade e a portabilidade entre diferentes agentes.
- Contrato de segurança com falha fechada para isolamento de diretório (cwd restrito ao workspace), mitigação de command injection via shell=False e envelope de telemetria completo (duration_ms, timed_out, exit_code).

## 2. Tensões Dialéticas & Falsificadores Bloqueantes
- **[OPENAI]**: Confinar apenas cwd não confina a execução: caminhos absolutos em argumentos, variáveis de ambiente, executáveis, links simbólicos, arquivos de resposta e subprocessos ainda podem acessar ou alterar recursos externos.
  - *Falsificador Exigido:* `Um teste automatizado que execute pytest -q tests/test_gateway_confinement.py deve provar que tentativas por caminho absoluto, symlink, variável de ambiente, subprocesso e arquivo de resposta falham fechadas sem efeitos fora de um workspace temporário.`
- **[OPENAI]**: Aceitar command como list[str] ou str torna ambígua a semântica de shell=False e pode reintroduzir interpretação de shell ou comportamento divergente entre plataformas.
  - *Falsificador Exigido:* `Um teste automatizado que execute pytest -q tests/test_gateway_exec_contract.py deve demonstrar sem execução colateral que strings contendo operadores de shell são rejeitadas e que apenas argv explícito é aceito.`
- **[ANTHROPIC]**: cwd confinado ao workspace + shell=False + timeout NÃO constituem sandbox nem 'contenção estrita'. cwd apenas define o diretório de trabalho; não impede que o comando leia/escreva via caminhos absolutos ou '../', abra rede, ou consuma o host. Isolamento real exige camada de SO (namespaces/containers/seccomp), que a proposta declara fora de escopo.
  - *Falsificador Exigido:* `Executar exec_command(['python','-c','open("/etc/passwd").read()'], cwd=<workspace>) ou um comando que faça egress de rede: se ambos rodam apesar do 'confinamento', a alegação de sandbox está falsificada.`
- **[ANTHROPIC]**: Aceitar command como `str` além de `list[str]` reintroduz injeção de shell e anula a garantia shell=False. 'Preferência' não é contrato executável.
  - *Falsificador Exigido:* `exec_command('rg foo; rm -rf .', cwd=...) — se a forma string chega a um shell, há execução de payload arbitrário; a mitigação declarada falha.`

## 3. Descarte por Via Negativa (Anti-Hipertrofia)
- [google] A flexibilidade do tipo de comando (list[str] | str) em exec_command pode induzir inconsistências de tokenização de argumentos em ambientes heterogêneos (POSIX vs Windows) caso command seja fornecido como string e interpretado sem shlex.split canônico sob shell=False. (Classificado como não-bloqueante)
- [google] Ausência de especificação de teto máximo de bytes (max_output_bytes) e estratégia de truncamento (tail/head truncation) para stdout/stderr no envelope de resposta do Lean Gateway. (Classificado como não-bloqueante)
- [openai] As afirmações de zero tokens, schema menor que 150 tokens, redução superior a 80% e custo O(1) não possuem tokenizer, corpus, baseline nem procedimento de medição definidos. (Classificado como não-bloqueante)
- [openai] O envelope não limita volume de saída nem define cancelamento da árvore de processos, permitindo exaustão de memória ou subprocessos órfãos apesar do timeout. (Classificado como não-bloqueante)
- [anthropic] Custo de descoberta é deslocado, não eliminado: sem schemas, o agente precisa conhecer a existência e as flags de ferramentas custom (round_table_engine.py, specgraph). Ferramentas conhecidas (git/pytest/rg) estão ok; as próprias não. (Classificado como não-bloqueante)
