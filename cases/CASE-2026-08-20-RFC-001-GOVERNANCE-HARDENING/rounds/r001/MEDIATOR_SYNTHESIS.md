# SÍNTESE DO MEDIADOR CONSTITUCIONAL — RODADA 1

## 1. Consensos Estabelecidos (Imutáveis)
- Eliminação matemática de loops infinitos através do hard cap determinístico em N=3 e transição FSM para HELD_PROGRESS_REVIEW com escalonamento humano.
- Via Negativa explícita que proíbe complexidade acidental (sem PKI, TLS interno ou bancos distribuídos desnecessários, mantendo I/O atômico em poucas linhas).
- Economia de contexto e estabilidade semântica via Âncoras Imutáveis no topo do prompt e deltas O(n) indexados por hash de seção.

## 2. Tensões Dialéticas & Falsificadores Bloqueantes
- **[OPENAI]**: overtime_granted não possui limite total nem transição terminal definida, permitindo sucessivas prorrogações e contradizendo N <= 3.
  - *Falsificador Exigido:* `Um teste de FSM prova que nenhuma sequência de eventos, inclusive concessões repetidas de overtime, executa mais que o máximo absoluto formalmente definido.`
- **[OPENAI]**: Deltas com hashes de seção não definem serialização canônica, encadeamento com o estado anterior nem reconstrução determinística do documento vigente.
  - *Falsificador Exigido:* `Um teste reproduz o mesmo hash e o mesmo estado final a partir da âncora e dos deltas em implementações independentes, rejeitando delta ausente, reordenado ou adulterado.`
- **[OPENAI]**: Nomes de arquivos e famílias de modelo não constituem pinos soberanos imutáveis; pesos, quantização, tokenizer ou parâmetros podem mudar mantendo o mesmo nome.
  - *Falsificador Exigido:* `Cada execução valida um SHA-256 registrado dos artefatos efetivos e falha fechada quando qualquer peso, tokenizer, template ou configuração determinística diverge.`
- **[ANTHROPIC]**: A proposta define os verdicts (APPROVE/REJECT/REVISE) e severidades (blocking/non-blocking) por assento, mas não define a regra de agregação que decide FRONTIER_UNANIMOUS. Não está dito se um REVISE quebra a unanimidade, nem se um issue 'non-blocking' conta contra o consenso.
  - *Falsificador Exigido:* `Dois assentos emitem APPROVE e um emite REVISE com apenas um issue non-blocking. Se o motor não consegue decidir deterministicamente entre APROVAR e transitar para HELD_PROGRESS_REVIEW a partir apenas do schema, o contrato de quórum está subespecificado — a mesma classe de 'quórum quebrado' do post-mortem.`

## 3. Descarte por Via Negativa (Anti-Hipertrofia)
- [google] O mecanismo de deltas O(n) por hash de seção pode introduzir atrito de parsing caso modelos emitam formatações de diff imperfeitas. (Classificado como não-bloqueante)
- [openai] Limitar gravação atômica e locking por contagem de linhas é um critério estético, não uma garantia de correção ou portabilidade. (Classificado como não-bloqueante)
- [anthropic] A Solução B (deltas ADDED/MODIFIED/DELETED com hash SHA-256 por seção) é complexidade acidental sob o próprio teto N≤3 — viola a Via Negativa de anti-hipertrofia que o RFC declara. (Classificado como não-bloqueante)
- [anthropic] PIN_LOCAL_SOVEREIGN_GENERAL e PIN_LOCAL_COMPACTOR apontam para o mesmo artefato (qwen38-27b.gguf), mas o schema não fixa se rodam como uma instância única com prompts distintos ou dois carregamentos concorrentes na RTX 3090 (24GB). (Classificado como não-bloqueante)
