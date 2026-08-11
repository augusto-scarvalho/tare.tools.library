#!/usr/bin/env python3
import json,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
g=json.loads((root/'catalog/RESEARCH_RELATION_GRAPH.json').read_text(encoding='utf-8'))
ids=[n['id'] for n in g['nodes']]
assert len(ids)==len(set(ids)), 'duplicate node ids'
known=set(ids)
for e in g['edges']:
    assert e['from'] in known, ('missing from',e)
    assert e['to'] in known, ('missing to',e)
    assert e['basis'] in {'observed_citation','observed_crosswalk','document_structure','curated','inferred','mechanical_derivation'}
    assert e['confidence'] in {'high','medium','low'}
assert g['statistics']['historical_artifacts']==93
print(f"RESEARCH_RELATION_GRAPH PASS nodes={len(ids)} edges={len(g['edges'])}")
