from pathlib import Path
import re, json, hashlib
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1]
SNAP=ROOT/'corpus/canonical-snapshot/2026-08-05/docs/research'
OUT=ROOT/'editorial-editions/2026-08-05-private-github-snapshot'

def text_of(p):
    s=p.read_text(errors='replace')
    if p.suffix.lower()=='.html': return BeautifulSoup(s,'html.parser').get_text('\n')
    return s

def has(rx,t): return bool(re.search(rx,t,re.I|re.M))
def classify(n):
    l=n.lower()
    if 'implementation-plan' in l or 'implementation-brief' in l or l.startswith('plan-'): return 'implementation research'
    if 'forensics' in l or 'verification' in l or 'evidence' in l or 'tracking-log' in l: return 'evidence/forensics'
    if 'backlog' in l or 'groom' in l: return 'backlog/governance working note'
    if 'round' in l or 'monitor' in l or 'race-mode' in l: return 'research iteration/experiment round'
    return 'research/study'
rows=[]; details=[]
for p in sorted(SNAP.rglob('*')):
    if not p.is_file() or p.name=='baseline-delegations-frozen-2026-07-30.json': continue
    t=text_of(p)
    cls=classify(p.name)
    checks={
      'numbered_index': has(r'(^|\n)#{1,4}\s*(índice|index|sum[aá]rio)|table of contents',t),
      'problem_objectives': has(r'problema|objetiv|question|pergunta',t),
      'reliable_sources': has(r'arxiv|doi|github\.com|docs\.|microsoft|google|openai|anthropic|nvidia|paper|fonte|source',t),
      'bleeding_edge': has(r'bleeding|preprint|issue|pull request|\bPR\b|fork|experiment|experimento',t),
      'consolidation': has(r's[íi]ntese|consolida|proposal|proposta|recommend|recomenda|portfolio|portf[oó]lio',t),
      'inline_refs': has(r'https?://|\[[^\]]+\]\(https?://',t),
      'bibliography': has(r'bibliograf|references|refer[eê]ncias',t),
      'implementation_companion_hint': 'implementation' in p.name.lower() or has(r'implementa[cç][aã]o|implementation',t),
      'html_source': p.suffix.lower()=='.html',
    }
    score=sum(checks.values())
    rows.append((p.relative_to(SNAP).as_posix(),cls,score,checks))

md=['# Editorial Migration Gap Report — 2026-08-05 snapshot','',
'Assessment against the **current tare.tools research-document standard**. This is a structural heuristic, not a scientific-quality score and not architectural authority. Historical artifacts are not rewritten merely to improve this score.','',
'## Standard derived from the owner\'s current generation prompt','',
'For a **scientific/exploratory research** edition, the current target format expects: numbered contents; explicit problems/objectives; reliable/primary sources; bleeding-edge sources and repository signals; synthesis/proposal; inline bibliographic references; final bibliography; a separate technical implementation proposal for harness analysis; HTML delivery; and explicit future-research pointers when adjacent topics emerge.','',
'For **implementation/evidence/forensics/backlog** artifacts, provenance and documentary class take precedence over forcing paper-like structure.','',
'## Corpus assessment','',
'| Source | Class | Structural coverage | Missing target elements |','|---|---|---:|---|']
for path,cls,score,c in rows:
    missing=[k.replace('_',' ') for k,v in c.items() if not v]
    md.append(f'| `{path}` | {cls} | {score}/9 | {", ".join(missing) if missing else "—"} |')
md += ['', '## Migration policy', '',
'1. Preserve exact historical source bytes and hashes.','2. Create editorial editions as derivatives.','3. Translate PT-BR/mixed sources to EN without silently reconciling claims.','4. For scientific studies, apply the current HTML visual system and flag missing bibliography/source classes rather than fabricate them.','5. Keep implementation plans/proposals separate from scientific research whenever the historical lineage supports that separation.','6. Record **RESEARCH REFRESH NEEDED** separately from **TRANSLATION NEEDED**. A translation does not imply that old external claims have been reverified.','7. Future refreshes should use primary/mainline sources first, then bleeding-edge sources, and preserve ADOPT / ADAPT / RETIRE / OPEN decisions as research findings rather than architecture authority.']
(OUT/'MIGRATION_GAP_REPORT.md').write_text('\n'.join(md)+'\n',encoding='utf-8')

standard='''# tare.tools Research Documentation Standard — 2026-08-11\n\nStatus: **TARGET EDITORIAL STANDARD**. This governs presentation and research hygiene; it does **not** grant architectural authority to document claims.\n\n## A. Scientific & Exploratory Research document\n\n1. Numbered table of contents.\n2. Problem definition, assumptions and objectives.\n3. CURRENT × TARGET × PROPOSED × RESEARCH framing when tare.tools is discussed.\n4. Reliable sources: peer-reviewed papers, established scientific literature, standards, official vendor engineering/docs, influential practitioners where appropriate, and mainline repositories.\n5. Bleeding edge: recent preprints, mainline issues/PRs/discussions/experiments and well-provenanced emerging work.\n6. Critical comparison of evidence quality; research is evidence, never automatic normative authority.\n7. Consolidated proposal for the studied problem, including promising emerging experiments/evolutions.\n8. Inline bibliographic references.\n9. Bibliography at the end.\n10. Explicit limitations, falsifiable hypotheses, experimental program and research pointers when useful.\n11. HTML editorial delivery: fixed sidebar/index, editorial hero, strong hierarchy, callouts/cards, responsive tables, UTF-8, unique IDs and valid internal anchors.\n\n## B. Technical Implementation Research companion\n\nA separate document should be produced when the research yields implementable architecture. It must be marked **PROPOSED / IMPLEMENTATION RESEARCH** until reconciled with repo truth.\n\nRequired sections: bounded-context ownership; canonical equivalents before new primitives; CURRENT/TARGET gap; contracts and invariants; migration/compatibility/rollback; Windows + POSIX/CI requirements; evidence/gates; candidate BDD scenarios; dependencies and transverse impacts; explicit non-goals; Implementation Packet candidates.\n\nIt must not silently redesign ratified architecture during implementation.\n\n## C. Historical migration rule\n\nHistorical documents are immutable evidence. Editorial migration may translate, re-render, add provenance banners and indexes, but must not silently update claims or pretend older TARGET/PROPOSED ideas became CURRENT. Scientific refresh is a separate derivative operation with its own date and sources.\n'''
(OUT/'RESEARCH_DOCUMENT_STANDARD.md').write_text(standard,encoding='utf-8')
print('wrote',len(rows),'assessments')
