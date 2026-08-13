# 1 — Evidência empírica e diagnóstico

**Status:** `RESEARCH / INTERNAL EMPIRICAL EVIDENCE`  
**Parent:** [Assurance Topology](README.md)

## Caso operacional

A seed empírica é a sequência PR #16 → Issue #17 no repositório canônico privado. Depois que os reparos de baseline permitiram ao CI alcançar o aggregate scenario gate, os três OS ficaram vermelhos. A investigação mostrou que `scenario FAIL` não possuía uma única interpretação.

O mesmo treasury continha:

- regressões CURRENT;
- conformance/architecture checks;
- `NOT_CURRENT` negative evidence por design;
- candidate/qualification experiments;
- platform fixtures;
- process/crash/recovery probes;
- system/integration scenarios;
- fixtures históricas incompatíveis com contratos mais novos.

CI-REGRESSION-01 foi criado para classificar antes de corrigir ou decidir blocking semantics.

## Negative evidence ≠ candidate regression

P2/P3/P5 já continham checks intencionalmente negativos enquanto capabilities permanecessem `NOT_CURRENT`. O aggregate antigo tratava todo rc não-zero como blocking regression. O corrective passou a preservar o FAIL real e só reconhecer `expected-negative` quando declaration + failed-count consistency + reviewed policy row coincidem. Ordinary/legacy failure, unknown tag, malformed policy e partial declaration continuam fail-closed.

Auditoria independente aceitou o mecanismo somente para o subject exato e registrou um limite: policy bytes modificáveis pelo candidate não se tornam Authority. Future autonomous promotion precisará de trusted provenance para mudanças que alterem blocking semantics.

## Fixture debt observado

Foram encontrados exemplos de:

- governance fixtures anteriores a receipts/producer semantics atuais;
- fixture artifacts que não exercitavam settlement CURRENT;
- import closure incompleta;
- POSIX process-group incorreto;
- path string equality em vez de resolved identity;
- executable bit ausente;
- worktree contra Git state read-only;
- stat metadata confundida com content mutation;
- test pins apontando para owner antigo após module extraction;
- generated projection drift;
- fault injection com comportamento timing-sensitive.

Portanto alguns reds eram defects de produto, outros stale fixtures, outros negative evidence e outros reliability evidence ainda inconclusivos.

## Diagnóstico estrutural

No checkpoint estudado, todo PR executa Ubuntu/Windows/macOS em Python 3.13, cada leg com compile → product-release → spec-pack → aggregate scenarios + muitas fixtures standalone; soak roda à parte. `.harness/project.json` descreve `scenarios` como todos os `testing/scenarios/*.py` agregados.

Ao mesmo tempo, `testing/QUALITY_GATES.md` já recomenda o gate mais estreito capaz de produzir nova informação e separa bounded release hygiene de deep fixtures/soak.

**Finding de pesquisa:** o incumbent preserva um treasury de evidência valioso, mas o PR CI cresceu até operar como uma system-qualification matrix quase universal.

## Evidência contrária obrigatória

Uma publicação futura deve preservar também hypotheses falsificadas, residual reds, nondeterminism, implementer claims corrigidos pela auditoria, corrective cost e failures detectados apenas pelo full treasury. Sem isso, o estudo sofreria survivorship/favorable-closure bias.

O repositório canônico privado permanece source of truth; este documento não substitui Git/code/gates.
