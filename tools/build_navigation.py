#!/usr/bin/env python3
"""Build human-readable GitHub navigation from MASTER_CATALOG.json.

Generated files never duplicate historical document bytes. They provide navigable
views over corpus/original and optional translated derivatives under
corpus/translations/en. Python stdlib only.
"""
from __future__ import annotations
import json, os, re
from pathlib import Path
from urllib.parse import quote, unquote

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "catalog" / "MASTER_CATALOG.json"
TRANSLATIONS = ROOT / "corpus" / "manifests" / "translations" / "en"
LIBRARY_REFERENCES = ROOT / "corpus" / "library-references"
IDENTITY_CROSSWALK = ROOT / "catalog" / "identity-crosswalk"

TOPIC_DIRS = [
    ("00_north-star-historical", "North Star histórica", {"Project / Workspace", "Routing & Adaptation", "Workflow"}, ["programa formal", "arquitetura multiagente"]),
    ("01_methodology-docs/research-program", "Metodologia e programa de pesquisa", set(), ["programa formal", "pesquisa"]),
    ("02_harness-architecture", "Harness / Agent OS Architecture", {"Project / Workspace", "Identity / Authority / Policy"}, ["arquitetura", "review"]),
    ("03_workflow", "Workflow", {"Workflow"}, ["workflow", "task"]),
    ("04_routing-reputation", "Routing & Reputation", {"Routing & Adaptation", "Reputation / Qualification"}, ["routing", "roteamento"]),
    ("05_runtime-model-inference", "Runtime / Model / Inference", {"Runtime", "Model / Inference"}, ["runtime", "endpoints", "cli"]),
    ("06_capabilities-effects", "Capability / Effects", {"Capability / Effects"}, ["capability", "effect"]),
    ("07_reliability", "Reliability", {"Reliability"}, ["reliability"]),
    ("08_validation-assurance", "Validation / Assurance / Evidence", {"Validation / Assurance", "Evidence / Provenance"}, ["testes", "gates", "assurance", "validation"]),
    ("09_governance-audit", "Governance / Audit / Authority", {"Governance / Audit", "Identity / Authority / Policy"}, ["auditoria", "governance", "kimi"]),
    ("10_interoperability-protocols", "Protocols / Interoperability", {"Protocols / Interoperability"}, ["protocolos", "interoperabilidade"]),
    ("11_project-workspace", "Project / Workspace", {"Project / Workspace"}, ["project", "workspace"]),
    ("12_memory-context", "Memory / Context", {"Memory / Context"}, ["memory", "context"]),
    ("13_resources-scheduling", "Resources / Scheduling / Economics", {"Observability / Economics / Resources"}, ["resource", "container", "scheduling"]),
    ("14_sandbox-isolation", "Sandbox / Isolation", {"Sandbox / Isolation"}, ["sandbox", "container"]),
    ("15_experience-tui-repl", "Experience / TUI / REPL", {"Experience / Human Interface"}, ["tui", "repl", "experience"]),
    ("16_vendors-runtimes", "Vendors / Runtimes", {"Runtime", "Model / Inference"}, ["google", "kimi", "vendor", "endpoints"]),
    ("17_local-models-benchmarks", "Local Models / Benchmarks", set(), ["local", "benchmark", "llm"]),
    ("18_evolution-control", "Evolution Control", {"Evolution Control"}, ["evolution"]),
    ("19_legacy-system-reconstruction", "Legacy / Cognitive System Reconstruction", set(), ["legacy", "nlu", "state machine", "reconstruction"]),
]

def load_entries():
    return json.loads(CATALOG.read_text(encoding="utf-8"))

def load_translations():
    by_source = {}
    if not TRANSLATIONS.exists(): return by_source
    for p in sorted(TRANSLATIONS.glob("*.json")):
        m=json.loads(p.read_text(encoding="utf-8"))
        by_source[m["translation_of"]]=m
    return by_source

def load_library_references():
    refs=[]
    cross={}
    if IDENTITY_CROSSWALK.exists():
        for cp in sorted(IDENTITY_CROSSWALK.glob("*.json")):
            c=json.loads(cp.read_text(encoding="utf-8")); cross[c["file_library_id"]]=c
    if not LIBRARY_REFERENCES.exists(): return refs
    for p in sorted(LIBRARY_REFERENCES.rglob("*.reference.json")):
        d=json.loads(p.read_text(encoding="utf-8"))
        d["_reference_path"]=p.relative_to(ROOT).as_posix()
        d["_materialization"]=cross.get(d["file_library_id"])
        refs.append(d)
    return refs

def reference_matches(entry, contexts, keywords):
    ectx=set(entry.get("suggested_contexts", []))
    if contexts and ectx.intersection(contexts): return True
    hay=(entry.get("title", "") + " " + (entry.get("lineage_family") or "")).lower()
    return any(k.lower() in hay for k in keywords)

def reference_table(entries, base_dir: Path):
    out=["| Referência pendente | Prioridade | Tipo | Família | Idioma | Estado |", "|---|---|---|---|---|---|"]
    for e in entries:
        link=rel_link_from(base_dir,e["_reference_path"])
        family=e.get("lineage_family") or "—"
        lang=e.get("native_language") or "unknown"
        out.append(f"| **[{e['title']}]({link})**<br><sub>`{e['file_library_id']}`</sub> | `{e['priority']}` | `{e['suggested_kind']}` | `{family}` | `{lang}` | `{e['translation_status']}` |")
    return "\n".join(out)

def rel_link_from(base_dir: Path, target_rel: str) -> str:
    target = ROOT / target_rel
    rel = target.relative_to(ROOT) if base_dir == ROOT else Path(os.path.relpath(target, base_dir))
    return quote(rel.as_posix(), safe="/._-~")

def matches(entry, contexts, keywords):
    ectx = set(entry.get("bounded_contexts", []))
    if contexts and ectx.intersection(contexts): return True
    hay = (entry.get("title", "") + " " + entry.get("document_id", "")).lower()
    return any(k.lower() in hay for k in keywords)

def language_links(entry, base_dir, translations):
    pt = f"[PT-BR]({rel_link_from(base_dir, entry['path'])})"
    tr=translations.get(entry['document_id'])
    if tr:
        en=f"[EN]({rel_link_from(base_dir,tr['translation_path'])})"
        state=tr.get('translation_status','')
        return f"{pt} · {en}<br><sub>`{state}`</sub>"
    return f"{pt} · EN pending"

def table(entries, base_dir: Path, translations):
    out = ["| Documento | Status | Tipo | Contextos | Idiomas |", "|---|---|---|---|---|"]
    for e in entries:
        contexts = ", ".join(e.get("bounded_contexts", []))
        out.append(f"| **{e['title']}**<br><sub>`{e['document_id']}`</sub> | `{e['status']}` | `{e['document_type']}` | {contexts} | {language_links(e,base_dir,translations)} |")
    return "\n".join(out)

def build_topic_readmes(entries, translations, refs):
    for dirname, title, contexts, keywords in TOPIC_DIRS:
        d = ROOT / "docs/research" / dirname; d.mkdir(parents=True, exist_ok=True)
        selected = [e for e in entries if matches(e, contexts, keywords)]
        pending = [e for e in refs if not e.get("_materialization") and reference_matches(e, contexts, keywords)]
        lines = [
            f"# {title}", "",
            "> Índice temático. Os bytes históricos PT-BR permanecem imutáveis em `corpus/original/`; traduções EN são derivatives versionados. Referências File Library permanecem apenas metadata até os bytes exatos serem materializados.", "",
            f"Documentos materializados relacionados: **{len(selected)}**. Referências pendentes de reidratação: **{len(pending)}**.", "",
            "## Materializados", "",
        ]
        lines.append(table(selected,d,translations) if selected else "_Nenhum documento materializado classificado nesta família ainda._")
        lines += ["", "## Pendentes de reidratação", ""]
        lines.append(reference_table(pending,d) if pending else "_Nenhuma referência File Library pendente nesta família._")
        lines += ["", "## Navegação", "", "- [Índice geral](../../catalog/DOCUMENT_INDEX.md)", "- [Fila de reidratação](../../catalog/REHYDRATION_QUEUE.md)", "- [Catálogo mestre](../../catalog/MASTER_CATALOG.md)", "- [Status de tradução](../../catalog/TRANSLATION_STATUS.md)", "- [Fila de tradução EN](../../catalog/TRANSLATION_QUEUE.md)", "- [README do corpus](../../README.md)", ""]
        (d / "README.md").write_text("\n".join(lines), encoding="utf-8")

def build_document_index(entries, translations, refs):
    translated=sum(1 for e in entries if e['document_id'] in translations)
    lines = [
        "# Índice de documentos e estudos", "",
        "> Índice humano gerado deterministicamente. PT-BR aponta para originals preservados byte-for-byte; EN aponta para derivatives com provenance próprio. File Library references são metadata de descoberta até materialização exata.", "",
        f"Documentos materializados: **{len(entries)}**. Tradução EN disponível: **{translated}/{len(entries)}**. Referências File Library: **{len(refs)}** total · **{sum(1 for r in refs if not r.get('_materialization'))}** pendente(s) de materialização.", "",
        "## Materializados", "", table(entries, ROOT / "catalog", translations), "",
        "## File Library — pendentes de reidratação", "",
        "Veja a [fila completa de reidratação](REHYDRATION_QUEUE.md). Os links abaixo abrem somente o metadata sidecar, nunca um falso original.", "",
        reference_table([r for r in refs if not r.get("_materialization")], ROOT / "catalog") if refs else "_Nenhuma referência pendente._", "",
        "## Por tema", "",
    ]
    for dirname, title, contexts, keywords in TOPIC_DIRS:
        count = sum(1 for e in entries if matches(e, contexts, keywords))
        pending = sum(1 for e in refs if not e.get("_materialization") and reference_matches(e, contexts, keywords))
        lines.append(f"- [{title}](../docs/research/{dirname}/README.md) — {count} materializado(s) · {pending} pendente(s)")
    lines += ["", "## Provenance", "", "Cada original possui sidecar em [`corpus/manifests/`](../corpus/manifests/) com SHA-256 e provenance. Traduções possuem sidecar em [`corpus/manifests/translations/en/`](../corpus/manifests/translations/en/) e obedecem à [Translation Policy](../TRANSLATION_POLICY.md). Referências ainda não materializadas ficam em [`corpus/library-references/`](../corpus/library-references/) e nunca recebem `source_path` local inventado.", ""]
    (ROOT / "catalog" / "DOCUMENT_INDEX.md").write_text("\n".join(lines), encoding="utf-8")

def build_master_catalog_md(entries, translations):
    lines = ["# Master Catalog", "", "Initial bootstrap import: 2026-08-11.", "", "Este catálogo é a visão tabular completa. Para navegação por tema, veja [DOCUMENT_INDEX.md](DOCUMENT_INDEX.md).", "",
             "| Document ID | Status | Type | Contexts | PT-BR / EN | Source SHA-256 |", "|---|---|---|---|---|---|"]
    for e in entries:
        ctx = ", ".join(e.get("bounded_contexts", []))
        lines.append(f"| `{e['document_id']}` | {e['status']} | {e['document_type']} | {ctx} | {language_links(e,ROOT/'catalog',translations)} | `{e['sha256'][:16]}…` |")
    lines.append("")
    (ROOT / "catalog" / "MASTER_CATALOG.md").write_text("\n".join(lines), encoding="utf-8")

def build_translation_status(entries, translations):
    lines=["# Translation Status", "", "> English translations are derivatives. PT-BR originals remain the historical source artifacts.", "",
           f"Coverage: **{len(translations)}/{len(entries)}** documents have an English derivative.", "", "| Document | English | Review state | Source hash | Translation hash |", "|---|---|---|---|---|"]
    for e in entries:
        tr=translations.get(e['document_id'])
        if tr:
            link=rel_link_from(ROOT/'catalog',tr['translation_path'])
            lines.append(f"| {e['title']} | [open]({link}) | `{tr['translation_status']}` | `{tr['source_sha256'][:12]}…` | `{tr['translation_sha256'][:12]}…` |")
        else:
            lines.append(f"| {e['title']} | pending | — | `{e['sha256'][:12]}…` | — |")
    lines += ["", "See [TRANSLATION_POLICY.md](../TRANSLATION_POLICY.md) for authority and fidelity rules.", ""]
    (ROOT/'catalog'/'TRANSLATION_STATUS.md').write_text('\n'.join(lines),encoding='utf-8')

def update_root_readme(entries, translations, refs):
    translated=sum(1 for e in entries if e['document_id'] in translations)
    content=f'''# tare.tools Research Corpus

> **THIS REPOSITORY IS EVIDENCE, NOT ARCHITECTURAL AUTHORITY.**

Este repositório preserva pesquisa, fontes, experimentos, arqueologia, propostas e versões históricas do tare.tools.

Em conflito, prevalecem o repositório canônico `tare-tools`, Git, código, arquitetura ratificada, ADRs, SPECs, BDDs e gates.

English overview: **[README.en.md](README.en.md)**.

## Comece aqui

- **[Índice unificado de todos os documentos e estudos](catalog/ALL_DOCUMENTS_INDEX.md)** — 11 seed originals de chat, 1 live-ingestion exact source, 93 cópias exatas do snapshot privado e {len(refs)} referências File Library, com origem/authority explícitas.
- **[Índice dos originals de chat materializados](catalog/DOCUMENT_INDEX.md)** — navegação PT-BR | EN por documento e por tema.
- **[Primeira ingestão viva — Identity, Lineage, Learning & Evolution](catalog/NEW_RESEARCH_INGESTIONS/identity-lineage-learning-2026-08-12.md)** — ResearchObject transversal de 12/08, com review, technical delta, graph edges e Frontier curation.
- **[Baseline histórico do GitHub privado](canonical-references/baselines/private-github-main-2026-08-05/README.md)** — snapshot exato de 05/08, não CURRENT.
- **[Índice das pesquisas presentes no snapshot privado](catalog/CANONICAL_SNAPSHOT_RESEARCH_INDEX.md)** — 93 arquivos byte-for-byte de `docs/docs/research/`.
- **[Fila de tradução EN do snapshot privado](catalog/CANONICAL_SNAPSHOT_TRANSLATION_QUEUE.md)** — sources não-EN materializados e elegíveis para tradução.
- **[Fila de reidratação](catalog/REHYDRATION_QUEUE.md)** — File Library refs ainda sem bytes locais; tradução fica bloqueada até materialização exata.
- **[Linhagens descobertas na File Library](catalog/LIBRARY_LINEAGES.md)** — projeção de descoberta.
- **[Reconciliação de linhagens](catalog/LINEAGE_RECONCILIATION.md)** — separa ordem por versão, siblings e duplicatas ainda não provadas.
- **[Expected identity assertions](catalog/IDENTITY_ASSERTIONS.md)** — hashes/tamanhos reportados por manifests independentes para future exact-byte verification.
- **[Índice normalizado de fontes](sources/SOURCE_INDEX.md)** — URLs extraídas deterministicamente dos originals materializados.
- **[Cobertura da reidratação](catalog/REHYDRATION_COVERAGE.md)** — baseline histórico vs. estado atual, sem somar identidades não reconciliadas.
- **[Catálogo mestre](catalog/MASTER_CATALOG.md)** — tabela completa com IDs, status, contextos, links e hashes.
- **[Status das traduções](catalog/TRANSLATION_STATUS.md)** — cobertura e estado de revisão das versões inglesas.
- **[Fila de tradução EN](catalog/TRANSLATION_QUEUE.md)** — somente sources já materializados que ainda aguardam derivação inglesa.
- **[QA das traduções](catalog/TRANSLATION_QA.md)** — checks estruturais de fidelidade e provenance.
- **[Workflow de tradução no chat](CHAT_TRANSLATION_WORKFLOW.md)** — contrato operacional para traduzir durante a revisão sem reconciliar arquitetura.
- **[Status da revisão](catalog/REVIEW_STATUS.md)** — separa revisão arquivística, tradução e reconciliation arquitetural.
- **[Translation Policy](TRANSLATION_POLICY.md)** — autoridade do original e regras de fidelidade.
- **[Cronologia](catalog/CHRONOLOGY.md)** — visão temporal.
- **[Famílias de versões](catalog/VERSION_FAMILIES.md)** — lineage conhecido/pendente.
- **[Research Graph](catalog/RESEARCH_GRAPH.json)** — relações estruturadas.
- **[Coverage](catalog/COVERAGE.md)** — cobertura do corpus.

### Seed atual

Foram materializados **{len(entries)} documentos** do corpus de chat nesta árvore. O baseline histórico privado acrescenta **93 cópias exatas de `docs/docs/research/`**, mantidas em um namespace separado para não confundir origem. Veja [`ALL_DOCUMENTS_INDEX.md`](catalog/ALL_DOCUMENTS_INDEX.md).

No corpus principal, foram materializados **{len(entries)} documentos** nesta árvore. Os originals PT-BR ficam em `corpus/original/`; versões EN derivadas ficam em `corpus/translations/en/`. Tradução EN disponível: **{translated}/{len(entries)}**. Há **{len(refs)} referências File Library** registradas; **{sum(1 for r in refs if not r.get("_materialization"))}** ainda aguardam materialização exata, sem reconstrução a partir de snippets.

## Status permitidos

- `RESEARCH` — evidência, hipótese, revisão, investigação.
- `PROPOSED` — proposta ainda não ratificada.
- `HISTORICAL` — preservação/arqueologia.
- `EXPERIMENTAL` — resultado experimental ainda não promovido.

`TARGET` não deve nascer aqui como autoridade. Um documento pode **referenciar** TARGET canônico, mas promoção é realizada no repositório canônico.

## Estrutura

- [`docs/research/`](docs/research/) — índices e pesquisas temáticas.
- `findings/` — sínteses ADOPT/ADAPT/RETIRE/OPEN.
- `proposals/` — propostas ainda não ratificadas.
- `experiments/` — protocolos e resultados.
- `archaeology/` — chats, sessões e evolução histórica.
- `sources/` — bibliografia e source manifests.
- [`corpus/original/`](corpus/original/) — bytes históricos PT-BR imutáveis.
- [`corpus/translations/en/`](corpus/translations/en/) — traduções inglesas derivadas.
- `corpus/normalized/` — versões processáveis derivadas.
- [`corpus/manifests/`](corpus/manifests/) — provenance sidecars.
- [`corpus/library-references/`](corpus/library-references/) — referências File Library de descoberta.
- [`catalog/identity-crosswalk/`](catalog/identity-crosswalk/) — vínculo entre uma referência e bytes exatos materializados, sem reescrever o registro de descoberta.
- [`catalog/`](catalog/) — índices, catálogos e grafo.
- `incoming/` — staging documental antes do roteamento.
- `schemas/` — contratos de metadata/publicação/tradução.
- `tools/` — automação determinística.

## Regra de autoridade

Research / experiment / archaeology / proposal **informam**, mas não ratificam arquitetura. Tradução não altera authority/status. Promoção para TARGET exige o fluxo canônico no repositório `tare-tools`.
'''
    (ROOT / "README.md").write_text(content, encoding="utf-8")


def build_review_status(entries, translations, refs):
    lines=[
        "# Corpus Review Status", "",
        "> Review is deliberately split into archival/identity review, translation structural QA, and architectural reconciliation. Translation never implies architectural ratification.", "",
        "## Current seed review", "",
        "| Document | Archival placement | Translation | Architectural reconciliation |",
        "|---|---|---|---|",
    ]
    for e in entries:
        tr=translations.get(e['document_id'])
        tstate=tr['translation_status'] if tr else 'PENDING'
        lines.append(f"| {e['title']} | `PASS` | `{tstate}` | `PENDING_CANONICAL_REPO_RECONCILIATION` |")
    lines += [
        "", "## Rehydration review", "",
        f"- File Library references discovered: **{len(refs)}**.",
        f"- Exact-byte identity crosswalks: **{sum(1 for r in refs if r.get('_materialization'))}**.",
        f"- Reference-only artifacts still pending materialization: **{sum(1 for r in refs if not r.get('_materialization'))}**.",
        f"- Translation blocked until exact source materialization: **{sum(1 for r in refs if not r.get('_materialization') and r.get('translation_status')=='BLOCKED_EXACT_SOURCE_NOT_MATERIALIZED')}**.",
        f"- Native-English reference artifacts: **{sum(1 for r in refs if r.get('translation_status')=='NOT_REQUIRED_NATIVE_ENGLISH')}**.",
        f"- References with expected SHA-256 constraints from independent manifests: **{sum(1 for r in refs if r.get('reported_sha256'))}** (reported, not locally verified source hashes).",
        "- No reference-only artifact is allowed to claim local source bytes or a locally verified SHA-256.",
        "- Lineage order/version metadata may establish ordering, but semantic supersession requires exact content comparison; see [LINEAGE_RECONCILIATION.md](LINEAGE_RECONCILIATION.md).",
        "- Normalized external-source navigation is generated from materialized originals only; see [SOURCE_INDEX.md](../sources/SOURCE_INDEX.md).",
        "", "## Interpretation", "",
        "- `PASS` under archival placement means the item has a stable document ID, byte-preserved source, SHA-256 provenance and bounded-context placement in the catalog.",
        "- Translation state describes the English derivative only. See [TRANSLATION_QA.md](TRANSLATION_QA.md) for machine-checkable fidelity checks.",
        "- `PENDING_CANONICAL_REPO_RECONCILIATION` is intentional: CURRENT/TARGET reconciliation must be performed against the actual canonical repository/Git/specs/gates, not inferred from historical documents or chat summaries.",
        "",
        "## Recommended read-only reconciliation order", "",
        "1. North Star / formal docs/research programme and harness architecture history.",
        "2. Workflow lifecycle and Reliability Semantics.",
        "3. Governance/Audit and Validation/Assurance/tests-gates.",
        "4. Protocols/Interoperability and Runtime/CLI archaeology.",
        "5. Resources/containers and vendor-specific historical studies.",
        "",
    ]
    (ROOT/'catalog'/'REVIEW_STATUS.md').write_text('\n'.join(lines),encoding='utf-8')

def validate_links():
    failures=[]
    files=[ROOT/'README.md',ROOT/'README.en.md',ROOT/'catalog'/'DOCUMENT_INDEX.md',ROOT/'catalog'/'MASTER_CATALOG.md',ROOT/'catalog'/'TRANSLATION_STATUS.md',ROOT/'catalog'/'TRANSLATION_QUEUE.md',ROOT/'catalog'/'TRANSLATION_QA.md',ROOT/'catalog'/'REVIEW_STATUS.md',ROOT/'CHAT_TRANSLATION_WORKFLOW.md',ROOT/'catalog'/'REHYDRATION_QUEUE.md',ROOT/'catalog'/'LIBRARY_LINEAGES.md',ROOT/'catalog'/'LINEAGE_RECONCILIATION.md',ROOT/'catalog'/'IDENTITY_ASSERTIONS.md',ROOT/'catalog'/'REHYDRATION_COVERAGE.md',ROOT/'sources'/'SOURCE_INDEX.md',*sorted((ROOT/'docs/research').glob('*/README.md'))]
    for p in files:
        txt=p.read_text(encoding='utf-8')
        for link in re.findall(r"\[[^\]]*\]\(([^)]+)\)",txt):
            if '://' in link or link.startswith('#'): continue
            target=(p.parent/unquote(link.split('#',1)[0])).resolve()
            if not target.exists(): failures.append(f"{p.relative_to(ROOT)} -> {link}")
    return failures

def main():
    entries=load_entries(); translations=load_translations(); refs=load_library_references()
    build_topic_readmes(entries,translations,refs); build_document_index(entries,translations,refs); build_master_catalog_md(entries,translations); build_translation_status(entries,translations); build_review_status(entries,translations,refs); update_root_readme(entries,translations,refs)
    failures=validate_links()
    if failures:
        print('FAIL broken generated links'); [print(' -',f) for f in failures]; raise SystemExit(2)
    print(f"PASS navigation built: documents={len(entries)} translations={len(translations)} library_refs={len(refs)} topics={len(TOPIC_DIRS)} links=valid")
if __name__=='__main__': main()
