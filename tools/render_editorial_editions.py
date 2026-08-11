from pathlib import Path
import hashlib, json, re, html, shutil
from bs4 import BeautifulSoup
import mistune
from urllib.parse import urlparse

ROOT=Path(__file__).resolve().parents[1]
SNAP=ROOT/'corpus/canonical-snapshot/2026-08-05/docs/research'
TRANS=ROOT/'corpus/canonical-snapshot/2026-08-05/translations/en/docs/research'
OUT=ROOT/'editorial-editions/2026-08-05-private-github-snapshot'
MAN=OUT/'manifests'
OUT.mkdir(parents=True,exist_ok=True); MAN.mkdir(parents=True,exist_ok=True)

CSS='''
:root{--bg:#f4f6fb;--surface:#fff;--surface2:#eef2f8;--text:#18212f;--muted:#647084;--line:#d8deea;--brand:#3759d7;--brand2:#6e3dc8;--accent:#008f7a;--warn:#9a5a00;--danger:#b53030;--code:#111827;--codeText:#e5e7eb;--shadow:0 16px 40px rgba(31,45,70,.08);--radius:16px;--content:1120px}
[data-theme=dark]{--bg:#0e1420;--surface:#151d2b;--surface2:#1c2637;--text:#edf2f8;--muted:#a5b2c5;--line:#2d3a4f;--brand:#8aa4ff;--brand2:#b591ff;--accent:#5dd4be;--warn:#ffc56d;--danger:#ff8a8a;--code:#090d14;--codeText:#dce6f2;--shadow:0 18px 50px rgba(0,0,0,.28)}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--bg);color:var(--text);font:16px/1.66 Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}a{color:var(--brand);text-underline-offset:.18em}.shell{display:grid;grid-template-columns:310px minmax(0,1fr);min-height:100vh}.sidebar{position:sticky;top:0;height:100vh;overflow:auto;padding:24px 18px;border-right:1px solid var(--line);background:var(--surface)}.brand{display:flex;gap:12px;align-items:center;margin:0 6px 18px}.brand-mark{width:40px;height:40px;display:grid;place-items:center;border-radius:12px;color:#fff;font-weight:900;background:linear-gradient(135deg,var(--brand),var(--brand2))}.brand strong,.brand span{display:block}.brand span{font-size:12px;color:var(--muted)}.controls{display:flex;gap:8px;margin:0 6px 16px}.controls button{border:1px solid var(--line);background:var(--surface2);color:var(--text);padding:7px 10px;border-radius:10px;cursor:pointer}.toc-title{margin:16px 8px 8px;color:var(--muted);font-size:11px;font-weight:900;text-transform:uppercase;letter-spacing:.08em}.toc{list-style:none;margin:0;padding:0}.toc li{margin:1px 0}.toc a{display:block;padding:7px 9px;border-radius:9px;color:var(--muted);text-decoration:none;font-size:13px;line-height:1.3}.toc a:hover{background:var(--surface2);color:var(--text)}.main{min-width:0}.container{width:min(var(--content),calc(100% - 48px));margin:0 auto;padding:34px 0 80px}.section{margin:0 0 28px;padding:34px 40px;background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);box-shadow:var(--shadow)}.hero{padding-top:54px;background:linear-gradient(145deg,color-mix(in srgb,var(--brand) 9%,var(--surface)),var(--surface) 55%,color-mix(in srgb,var(--brand2) 7%,var(--surface)))}.eyebrow{color:var(--brand);font-size:12px;font-weight:900;letter-spacing:.09em;text-transform:uppercase}h1{margin:10px 0 12px;font-size:clamp(38px,5.6vw,70px);line-height:1.03;letter-spacing:-.045em}h2{margin:0 0 22px;font-size:clamp(27px,3.2vw,41px);line-height:1.12;letter-spacing:-.03em}h3{margin:28px 0 10px;font-size:21px}.subtitle{max-width:900px;color:var(--muted);font-size:20px}.badges{display:flex;flex-wrap:wrap;gap:8px;margin:22px 0}.badge{display:inline-block;padding:5px 9px;border:1px solid var(--line);border-radius:999px;background:var(--surface2);font-size:11px;font-weight:900;letter-spacing:.03em}.badge.current{border-color:var(--accent)}.badge.target{border-color:var(--brand)}.badge.proposed{border-color:var(--warn)}.badge.research{border-color:var(--brand2)}.meta{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin:24px 0 6px}.meta>div{padding:13px;border:1px solid var(--line);border-radius:12px;background:color-mix(in srgb,var(--surface) 86%,transparent)}.meta b,.meta span{display:block}.meta b{font-size:11px;text-transform:uppercase;color:var(--muted)}.meta span{font-weight:700;word-break:break-word}.callout{margin:20px 0;padding:17px 20px;border-left:5px solid var(--brand);border-radius:0 12px 12px 0;background:var(--surface2)}.callout.warn{border-color:var(--warn)}.callout.insight{border-color:var(--accent)}p{margin:10px 0 16px}blockquote{margin:20px 0;padding:14px 20px;border-left:4px solid var(--brand);background:var(--surface2);border-radius:0 10px 10px 0}pre{overflow:auto;padding:20px;border-radius:13px;background:var(--code);color:var(--codeText);font-size:13px;line-height:1.58}code{font-family:"SFMono-Regular",Consolas,monospace}table{width:100%;border-collapse:collapse;margin:18px 0 24px;font-size:14px}th,td{padding:11px 12px;border:1px solid var(--line);text-align:left;vertical-align:top}th{background:var(--surface2);font-size:12px;text-transform:uppercase}img{max-width:100%}hr{border:0;border-top:1px solid var(--line);margin:30px 0}.footer{text-align:center;color:var(--muted);font-size:13px;padding:10px 0 50px}.content h2,.content h3,.content h4{scroll-margin-top:18px}.content ul,.content ol{padding-left:1.5rem}.content li{margin:5px 0}.provenance-list{font-size:14px;color:var(--muted)}
@media(max-width:980px){.shell{display:block}.sidebar{position:relative;height:auto;border-right:0;border-bottom:1px solid var(--line)}.toc{columns:2}.meta{grid-template-columns:repeat(2,1fr)}}@media(max-width:680px){.container{width:calc(100% - 20px);padding-top:16px}.section{padding:24px 19px}.toc{columns:1}.meta{grid-template-columns:1fr}table{display:block;overflow:auto}}@media print{.sidebar{display:none}.shell{display:block}.container{width:100%;padding:0}.section{box-shadow:none;break-inside:avoid}}
'''

md=mistune.create_markdown(escape=False, plugins=['table','strikethrough','task_lists','url'])

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def slugify(s):
    import unicodedata
    s=unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower()
    s=re.sub(r'[^a-z0-9]+','-',s).strip('-')
    return s or 'section'

def classify(name):
    n=name.lower()
    if 'implementation-plan' in n or 'implementation-brief' in n or n.startswith('plan-'):
        return 'IMPLEMENTATION_RESEARCH', 'PROPOSED'
    if 'forensics' in n or 'verification' in n or 'evidence' in n or 'tracking-log' in n or 'selfassessment' in n:
        return 'EVIDENCE_ARCHIVE', 'RESEARCH'
    if 'backlog' in n or 'round' in n or 'groom' in n or 'monitor' in n or 'race-mode' in n:
        return 'RESEARCH_ITERATION', 'RESEARCH'
    if name.endswith('.json'):
        return 'DATASET_OR_MANIFEST', 'RESEARCH'
    return 'SCIENTIFIC_RESEARCH', 'RESEARCH'

def extract_title(raw, suffix):
    if suffix=='.html':
        soup=BeautifulSoup(raw,'html.parser')
        h=soup.find(['h1','title'])
        if h: return h.get_text(' ',strip=True)
    for line in raw.splitlines():
        if line.startswith('# '): return re.sub(r'^#\s+','',line).strip()
    return Path('x').stem

def render_body(raw,suffix):
    if suffix=='.md': return md(raw)
    if suffix=='.html':
        soup=BeautifulSoup(raw,'html.parser')
        # Prefer main/container semantic content; fall back to body children.
        node=soup.find('main') or soup.find(class_='main') or soup.find('body') or soup
        # remove scripts/styles from embedded source; edition owns presentation
        for x in node.find_all(['script','style','nav']): x.decompose()
        return ''.join(str(c) for c in node.contents)
    if suffix=='.json':
        try: pretty=json.dumps(json.loads(raw),ensure_ascii=False,indent=2)
        except: pretty=raw
        return '<pre><code>'+html.escape(pretty)+'</code></pre>'
    return '<pre>'+html.escape(raw)+'</pre>'

def sectionize(body):
    soup=BeautifulSoup(body,'html.parser')
    toc=[]
    # remove first h1 because hero owns it
    h1=soup.find('h1')
    if h1: h1.decompose()
    headings=soup.find_all(['h2','h3'])
    # Legacy HTML may already contain IDs on headings or nested anchors. Preserve unique
    # historical IDs; generate collision-safe editorial IDs only when needed.
    all_ids=[x.get('id') for x in soup.find_all(id=True)]
    counts={k:all_ids.count(k) for k in set(all_ids)}
    reserved=set(all_ids)
    generated={}
    for h in headings:
        label=h.get_text(' ',strip=True)
        existing=h.get('id')
        if existing and counts.get(existing,0)==1:
            sid=existing
        else:
            base='ed-'+slugify(label)
            generated[base]=generated.get(base,0)+1
            sid=base if generated[base]==1 else f'{base}-{generated[base]}'
            while sid in reserved:
                generated[base]+=1
                sid=f'{base}-{generated[base]}'
            h['id']=sid
            reserved.add(sid)
        toc.append((h.name,sid,label))
    # Group top-level h2 chunks into cards. Keep preamble separately.
    out=[]; current=[]
    for child in list(soup.contents):
        if getattr(child,'name',None)=='h2':
            if current: out.append('<section class="section content">'+''.join(map(str,current))+'</section>'); current=[]
        current.append(child)
    if current: out.append('<section class="section content">'+''.join(map(str,current))+'</section>')
    return '\n'.join(out),toc

def make_html(src, edition_src, lang, relation, editorial_note):
    raw=edition_src.read_text(errors='replace')
    source_raw=src.read_text(errors='replace')
    title=extract_title(raw,edition_src.suffix.lower())
    body=render_body(raw,edition_src.suffix.lower())
    sections,toc=sectionize(body)
    dtype,status=classify(src.name)
    toc_html=''.join(f'<li class="{level}"><a href="#{sid}">{html.escape(label)}</a></li>' for level,sid,label in toc)
    source_rel=src.relative_to(ROOT).as_posix()
    edition_rel=edition_src.relative_to(ROOT).as_posix()
    source_sha=sha(src); edition_sha=sha(edition_src)
    subtitle={
        'SCIENTIFIC_RESEARCH':'Historical research edition migrated to the current tare.tools documentation standard.',
        'IMPLEMENTATION_RESEARCH':'Historical implementation-research edition. Proposal content is not canonical authority.',
        'EVIDENCE_ARCHIVE':'Historical evidence/forensics edition. Preserved as evidence rather than normalized into architecture.',
        'RESEARCH_ITERATION':'Historical research iteration/round. Preserved as an intermediate research artifact.',
        'DATASET_OR_MANIFEST':'Historical dataset or manifest rendered for navigability.'
    }[dtype]
    if lang.startswith('pt'): subtitle=subtitle.replace('Historical','Edição histórica —')
    html_doc=f'''<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)} — tare.tools historical edition</title><style>{CSS}</style></head><body>
<div class="shell"><aside class="sidebar"><div class="brand"><div class="brand-mark">t</div><div><strong>tare.tools</strong><span>Research Library · historical edition</span></div></div><div class="controls"><button onclick="toggleTheme()">Theme</button><button onclick="window.print()">Print</button></div><div class="toc-title">Contents</div><ul class="toc">{toc_html}</ul></aside><main class="main"><div class="container">
<section class="section hero"><div class="eyebrow">{html.escape(dtype.replace('_',' '))} · 2026-08-05 snapshot</div><h1>{html.escape(title)}</h1><p class="subtitle">{html.escape(subtitle)}</p><div class="badges"><span class="badge {status.lower()}">{status}</span><span class="badge">{html.escape(lang)}</span><span class="badge">{html.escape(relation)}</span><span class="badge">HISTORICAL</span></div><div class="meta"><div><b>Source SHA-256</b><span>{source_sha[:20]}…</span></div><div><b>Edition SHA-256</b><span>{edition_sha[:20]}…</span></div><div><b>Source snapshot</b><span>Private GitHub export · 2026-08-05</span></div><div><b>Authority</b><span>Research/evidence only</span></div></div><div class="callout warn"><strong>Historical authority boundary.</strong> This edition improves navigation, presentation and language accessibility. It does not silently promote historical claims into CURRENT or TARGET architecture. Current Git/ADRs/SPECs/tests/code take precedence.</div><div class="callout insight"><strong>Editorial treatment.</strong> {html.escape(editorial_note)}</div></section>
{sections}
<section class="section"><h2 id="edition-provenance">Edition provenance</h2><ul class="provenance-list"><li>Historical source: <code>{html.escape(source_rel)}</code></li><li>Edition input: <code>{html.escape(edition_rel)}</code></li><li>Source SHA-256: <code>{source_sha}</code></li><li>Edition-input SHA-256: <code>{edition_sha}</code></li><li>Snapshot date: 2026-08-05</li><li>Migration date: 2026-08-11</li><li>Semantic authority: RESEARCH / historical evidence, never automatic architecture ratification.</li></ul></section>
<div class="footer">tare.tools · historical research library · preserve provenance, separate evidence from authority</div></div></main></div><script>function toggleTheme(){{const e=document.documentElement;e.dataset.theme=e.dataset.theme==='dark'?'':'dark';}}</script></body></html>'''
    return html_doc, {'title':title,'document_type':dtype,'status':status,'language':lang,'relation':relation,'source_path':source_rel,'source_sha256':source_sha,'edition_input_path':edition_rel,'edition_input_sha256':edition_sha}

# Canonical source/translation mapping comes from the exact snapshot research index.
# Do not infer language or cross-format translation identity from filenames.
INDEX_PATH=ROOT/'catalog'/'CANONICAL_SNAPSHOT_RESEARCH_INDEX.json'
INDEX_DATA=json.loads(INDEX_PATH.read_text(encoding='utf-8'))
INDEX_BY_REL={Path(item['sourcePath']).relative_to('docs/research').as_posix():item for item in INDEX_DATA['items']}

entries=[]
for src in sorted(SNAP.rglob('*')):
    if not src.is_file(): continue
    rel=src.relative_to(SNAP).as_posix()
    item=INDEX_BY_REL.get(rel)
    if not item:
        raise RuntimeError(f'snapshot source missing from canonical research index: {rel}')
    source_lang=item.get('nativeLanguage') or 'unknown'
    # Source-language edition for every materialized research artifact, including JSON manifests/datasets.
    out_dir=OUT/'source-language'/src.relative_to(SNAP).parent
    out_dir.mkdir(parents=True,exist_ok=True)
    out_file=out_dir/(src.stem+'.html')
    doc,meta=make_html(src,src,source_lang,'SOURCE_LANGUAGE_EDITORIAL_EDITION','Presentation normalized to the current editorial system; source wording and claims are preserved.')
    out_file.write_text(doc,encoding='utf-8')
    meta['output_path']=out_file.relative_to(ROOT).as_posix(); entries.append(meta)
    # English edition: native-English source or exact registered derivative from the index.
    ed=None; relation=None
    if source_lang=='en':
        ed=src; relation='NATIVE_EN_EDITORIAL_EDITION'
    else:
        tr=item.get('englishTranslationPath')
        if tr:
            candidate=ROOT/tr
            if not candidate.is_file():
                raise RuntimeError(f'registered translation missing: {tr}')
            ed=candidate; relation='TRANSLATED_EN_EDITORIAL_EDITION'
    if ed:
        out_dir=OUT/'en'/src.relative_to(SNAP).parent; out_dir.mkdir(parents=True,exist_ok=True)
        out_file=out_dir/(src.stem+'.en.html')
        note='English source reformatted without semantic refresh.' if source_lang=='en' else 'English derivative generated from the exact historical source; translation does not reconcile or modernize historical claims.'
        doc,meta=make_html(src,ed,'en',relation,note)
        out_file.write_text(doc,encoding='utf-8')
        meta['output_path']=out_file.relative_to(ROOT).as_posix(); entries.append(meta)

# Manifest and index
(OUT/'EDITORIAL_STANDARD.md').write_text('''# tare.tools Research Editorial Standard — Historical Migration\n\nThis layer is derivative. Originals remain immutable.\n\n## Required structure\n1. Fixed sidebar and generated contents.\n2. Editorial hero and provenance metadata.\n3. Explicit CURRENT / TARGET / PROPOSED / RESEARCH boundaries.\n4. Numbered source headings are preserved when present; numbering is never invented into source claims.\n5. Tables and code remain responsive/readable.\n6. Bibliography and inline links remain part of the source content.\n7. English translations are derivatives linked to exact source hashes.\n8. Research refresh is a separate operation from translation/editorial migration.\n9. Operational logs, forensics, backlog and experiment rounds retain their original documentary class instead of being cosmetically promoted to scientific papers.\n''',encoding='utf-8')
(MAN/'editorial-manifest.json').write_text(json.dumps({'generated_at':'2026-08-11','snapshot':'2026-08-05','entries':entries},ensure_ascii=False,indent=2),encoding='utf-8')
# simple index
rows=[]
for m in entries:
    rows.append(f"| [{m['title']}]({Path(m['output_path']).relative_to('editorial-editions/2026-08-05-private-github-snapshot').as_posix()}) | `{m['language']}` | `{m['document_type']}` | `{m['relation']}` | `{m['status']}` |")
(OUT/'README.md').write_text('# Editorial Editions — 2026-08-05 Private GitHub Snapshot\n\nDerivative navigable editions. Historical originals remain immutable.\n\n| Document | Language | Class | Edition | Authority status |\n|---|---|---|---|---|\n'+'\n'.join(rows)+'\n',encoding='utf-8')
print('generated',len(entries),'editorial editions')
print('EN',sum(1 for e in entries if e['language']=='en'),'source/lang total',len(entries))
