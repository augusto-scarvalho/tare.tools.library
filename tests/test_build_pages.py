from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from build_pages import build
from validate_pages_contract import validate as validate_contract


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_html(*,title: str,abstract: str,lang: str,extra: str='') -> str:
    return f'''<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><title>{title}</title></head><body><main><article data-tare-document><header data-tare-role="document-header"><h1>{title}</h1><p data-tare-role="abstract">{abstract}</p></header><aside data-tare-role="authority-boundary">RESEARCH.</aside><section id="scope" data-tare-section="scope"><h2>Scope</h2>{extra}</section><section id="evidence" data-tare-section="evidence"><h2>Evidence</h2></section><section id="findings" data-tare-section="findings"><h2>Findings</h2></section><section id="limitations" data-tare-section="limitations"><h2>Limitations</h2></section><section id="references" data-tare-section="references"><h2>References</h2></section></article></main></body></html>'''


class BuildPagesTests(unittest.TestCase):
    def _git_init(self,root: Path) -> None:
        subprocess.run(['git','init','-q',str(root)],check=True)
        (root/'seed').write_text('x',encoding='utf-8')
        subprocess.run(['git','-C',str(root),'add','.'],check=True)
        subprocess.run(['git','-C',str(root),'-c','user.name=t','-c','user.email=t@x.invalid','commit','-qm','seed'],check=True)

    def _write_publication(self,root: Path,name: str,*,lang: str='en',extra: str='',asset: bool=False) -> Path:
        packet=root/'research'/'03_workflow'/name; packet.mkdir(parents=True)
        title=f'Study {name[-1].upper()}'; abstract=f'Abstract {name[-1].upper()}.'
        html=canonical_html(title=title,abstract=abstract,lang=lang,extra=extra)
        (packet/'article.html').write_text(html,encoding='utf-8')
        artifacts=['article.html','document-metadata.json']
        if asset:
            (packet/'diagram.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1 1"><title>diagram</title></svg>',encoding='utf-8')
            artifacts.append('diagram.svg')
        did=f'research.test.{name}'
        metadata={
            'document_id':did,'title':title,'document_type':'research','status':'RESEARCH','created_at':'2026-08-13',
            'language':lang,'abstract':abstract,'authors':[{'name':'Test','role':'editor'}],
            'bounded_contexts':['Workflow'],'provenance':{'origin':'TEST'},
        }
        (packet/'document-metadata.json').write_text(json.dumps(metadata),encoding='utf-8')
        manifest={
            'packet_version':'1.1','document_id':did,'document_type':'research','status':'RESEARCH','repository':'tare.tools.research',
            'bounded_contexts':['Workflow'],'artifacts':artifacts,'primary_artifact':'article.html','requested_channels':['pages'],'canonical_change':False,
        }
        manifest_path=packet/'PUBLISH_MANIFEST.json'; manifest_path.write_text(json.dumps(manifest,indent=2),encoding='utf-8')
        manifest_sha=sha(manifest_path)
        decision={
            'decision_version':'1.0','decision_id':f'editorial.{name}.001','document_id':did,'manifest_sha256':manifest_sha,
            'decision':'accept','pages_approved':True,'reviewer':{'name':'Reviewer','role':'editorial-reviewer','identity_ref':'test'},
            'reviewed_at':'2026-08-13T17:30:00Z',
        }
        decision_path=packet/'EDITORIAL_DECISION.json'; decision_path.write_text(json.dumps(decision,indent=2),encoding='utf-8')
        record={
            'record_version':'1.1','document_id':did,'manifest_sha256':manifest_sha,
            'artifact_sha256':{x:sha(packet/x) for x in artifacts},'primary_artifact':'article.html',
            'requested_channels':['pages'],'pages_approved':True,
            'editorial_decision':{'decision_id':decision['decision_id'],'decision':'accept','pages_approved':True,'reviewer':decision['reviewer'],'reviewed_at':decision['reviewed_at'],'sha256':sha(decision_path)},
        }
        (packet/'PUBLICATION_RECORD.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
        site=root/'site'; site.mkdir(exist_ok=True)
        records=sorted(
            path.relative_to(root).as_posix()
            for path in root.rglob('PUBLICATION_RECORD.json')
        )
        (site/'LEGACY_PAGES_PROJECTIONS.json').write_text(
            json.dumps({
                'schema':'tare.tools/legacy-pages-projections/1.0',
                'status':'FROZEN_READ_ONLY',
                'publication_records':records,
            }),
            encoding='utf-8',
        )
        return packet

    def _write_incumbent(self,root: Path) -> Path:
        incumbent=root/'incumbent'; incumbent.mkdir()
        critical=[
            'index.html','NAVIGATION.html','studies/index.html','research/index.html',
            'research/work/reliability-effect-reconciliation.html',
            'bridge-editions/2026-08-11/runtime-reliability-sandbox-scientific-refresh.html',
            'assets/site.css','assets/site.js','search.json',
        ]
        for rel in critical:
            path=incumbent/rel; path.parent.mkdir(parents=True,exist_ok=True); path.write_text(f'incumbent:{rel}',encoding='utf-8')
        return incumbent

    def test_shadow_build_preserves_incumbent_and_projects_approved_studies(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); self._git_init(root)
            packet_b=self._write_publication(root,'study-b')
            link='../study-b/article.html#findings'
            extra=f'<p><a href="{link}">Related B</a></p><img src="diagram.svg" alt="diagram">'
            packet_a=self._write_publication(root,'study-a',lang='pt-BR',extra=extra,asset=True)
            subprocess.run(['git','-C',str(root),'add','.'],check=True)
            subprocess.run(['git','-C',str(root),'-c','user.name=t','-c','user.email=t@x.invalid','commit','-qm','publications'],check=True)
            incumbent=self._write_incumbent(root); original_index=sha(incumbent/'index.html')
            output=root/'site-output'
            studies=build(root,output,base_path='/tare.tools.research/',incumbent=incumbent)
            self.assertEqual({x['document_id'] for x in studies},{'research.test.study-a','research.test.study-b'})
            self.assertEqual(sha(output/'index.html'),original_index)
            self.assertEqual(validate_contract(output,root,incumbent,'/tare.tools.research/'),[])
            page=output/'p'/'research-test-study-a'/'index.html'; soup=BeautifulSoup(page.read_text(encoding='utf-8'),'html.parser')
            self.assertEqual(soup.html['lang'],'pt-BR')
            self.assertEqual(soup.find('link',rel='stylesheet')['href'],'/tare.tools.research/assets/publisher/signal.css')
            self.assertEqual(soup.find('a',string='Related B')['href'],'/tare.tools.research/p/research-test-study-b/#findings')
            self.assertEqual(soup.find('img')['src'],'assets/diagram.svg')
            record=json.loads((page.parent/'PROJECTION_RECORD.json').read_text(encoding='utf-8'))
            self.assertTrue(record['semantic_parity'])
            self.assertEqual(record['source_semantic_fingerprint'],record['projected_semantic_fingerprint'])
            self.assertEqual(record['link_rewrites'][0]['kind'],'cross-publication')
            parity=json.loads((output/'publication-meta'/'PARITY_REPORT.json').read_text(encoding='utf-8'))
            self.assertEqual(parity['status'],'PASS')
            self.assertEqual(parity['modified_incumbent_paths'],[])
            urls=[x['url'] for x in json.loads((output/'publications'/'search.json').read_text(encoding='utf-8'))]
            self.assertTrue(all(x.startswith('/tare.tools.research/p/') for x in urls))
            soup.find('a',string='Related B')['href']='/tare.tools.research/p/research-test-study-b/#missing'
            page.write_text(str(soup),encoding='utf-8')
            self.assertTrue(any('broken fragment' in error for error in validate_contract(output,root,incumbent,'/tare.tools.research/')))

    def test_unresolved_internal_link_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); self._git_init(root)
            self._write_publication(root,'study-a',extra='<a href="missing-study.html">Missing</a>')
            subprocess.run(['git','-C',str(root),'add','.'],check=True)
            subprocess.run(['git','-C',str(root),'-c','user.name=t','-c','user.email=t@x.invalid','commit','-qm','publication'],check=True)
            with self.assertRaisesRegex(ValueError,'unresolved internal href'):
                build(root,root/'site-output',base_path='/tare.tools.research/')

    def test_unallowlisted_publication_record_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); self._git_init(root)
            packet=self._write_publication(root,'study-a')
            unlisted=root/'research'/'03_workflow'/'unlisted'
            unlisted.mkdir(parents=True)
            (unlisted/'PUBLICATION_RECORD.json').write_bytes(
                (packet/'PUBLICATION_RECORD.json').read_bytes()
            )
            with self.assertRaisesRegex(ValueError,'unallowlisted publication records'):
                build(root,root/'site-output',base_path='/tare.tools.research/')

    def test_rejected_decision_cannot_be_overridden_by_publication_record(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); self._git_init(root)
            packet=self._write_publication(root,'study-a')
            decision_path=packet/'EDITORIAL_DECISION.json'
            decision=json.loads(decision_path.read_text(encoding='utf-8'))
            decision.update(decision='reject',pages_approved=False)
            decision_path.write_text(json.dumps(decision,indent=2),encoding='utf-8')
            record_path=packet/'PUBLICATION_RECORD.json'
            record=json.loads(record_path.read_text(encoding='utf-8'))
            record['editorial_decision']['sha256']=sha(decision_path)
            record_path.write_text(json.dumps(record,indent=2),encoding='utf-8')
            subprocess.run(['git','-C',str(root),'add','.'],check=True)
            subprocess.run(['git','-C',str(root),'-c','user.name=t','-c','user.email=t@x.invalid','commit','-qm','publication'],check=True)
            with self.assertRaisesRegex(ValueError,'does not authorize Pages publication'):
                build(root,root/'site-output',base_path='/tare.tools.research/')

    def test_pages_contract_rechecks_editorial_decision_source(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); self._git_init(root)
            packet=self._write_publication(root,'study-a')
            subprocess.run(['git','-C',str(root),'add','.'],check=True)
            subprocess.run(['git','-C',str(root),'-c','user.name=t','-c','user.email=t@x.invalid','commit','-qm','publication'],check=True)
            incumbent=self._write_incumbent(root); output=root/'site-output'
            build(root,output,base_path='/tare.tools.research/',incumbent=incumbent)
            decision=json.loads((packet/'EDITORIAL_DECISION.json').read_text(encoding='utf-8'))
            decision.update(decision='reject',pages_approved=False)
            (packet/'EDITORIAL_DECISION.json').write_text(json.dumps(decision,indent=2),encoding='utf-8')
            errors=validate_contract(output,root,incumbent,'/tare.tools.research/')
            self.assertTrue(any('does not authorize Pages publication' in error for error in errors),errors)

    def test_missing_same_page_fragment_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); self._git_init(root)
            self._write_publication(root,'study-a',extra='<a href="#missing">Missing</a>')
            subprocess.run(['git','-C',str(root),'add','.'],check=True)
            subprocess.run(['git','-C',str(root),'-c','user.name=t','-c','user.email=t@x.invalid','commit','-qm','publication'],check=True)
            with self.assertRaisesRegex(ValueError,'unresolved internal fragment'):
                build(root,root/'site-output',base_path='/tare.tools.research/')

    def test_missing_cross_publication_fragment_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); self._git_init(root)
            self._write_publication(root,'study-b')
            self._write_publication(root,'study-a',extra='<a href="../study-b/article.html#missing">Missing</a>')
            subprocess.run(['git','-C',str(root),'add','.'],check=True)
            subprocess.run(['git','-C',str(root),'-c','user.name=t','-c','user.email=t@x.invalid','commit','-qm','publication'],check=True)
            with self.assertRaisesRegex(ValueError,'unresolved internal fragment'):
                build(root,root/'site-output',base_path='/tare.tools.research/')


if __name__=='__main__': unittest.main()
