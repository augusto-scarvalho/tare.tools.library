from pathlib import Path
import hashlib,json,sys,tempfile,unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from cutover_readiness_support import visual_evidence


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class VisualEvidenceTests(unittest.TestCase):
    def _fixture(self, root: Path):
        output=root/'out'; (output/'p/canary').mkdir(parents=True); (output/'assets/publisher').mkdir(parents=True)
        files={
            'p/canary/index.html':b'<html><body>ok</body></html>',
            'assets/publisher/signal.css':b'body{}',
            'assets/publisher/site.js':b'void 0',
        }
        for rel,data in files.items(): (output/rel).write_bytes(data)
        evidence={
            'record_version':'1.0',
            'record_kind':'pages-visual-validation-evidence',
            'document_id':'research.pages.canary.v1',
            'renderer':{'engine':'Chromium','harness':'Playwright'},
            'validated_projection':{
                'page_path':'p/canary/index.html','page_sha256':digest(files['p/canary/index.html']),
                'signal_css_path':'assets/publisher/signal.css','signal_css_sha256':digest(files['assets/publisher/signal.css']),
                'signal_js_path':'assets/publisher/site.js','signal_js_sha256':digest(files['assets/publisher/site.js']),
            },
            'viewports':[
                {'name':'desktop','no_horizontal_overflow':True,'image_loaded':True,'table_visible':True,'code_visible':True,'figure_visible':True,'details_visible':True,'screenshot_sha256':'a'*64},
                {'name':'mobile','no_horizontal_overflow':True,'image_loaded':True,'table_visible':True,'code_visible':True,'figure_visible':True,'details_visible':True,'screenshot_sha256':'b'*64},
            ],
        }
        path=root/'site/PAGES_VISUAL_EVIDENCE.json'; path.parent.mkdir(parents=True); path.write_text(json.dumps(evidence),encoding='utf-8')
        return output,path

    def test_matching_visual_evidence_passes(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); output,_=self._fixture(root)
            self.assertEqual(visual_evidence(root,output,'research.pages.canary.v1')['status'],'PASS')

    def test_projection_change_makes_visual_evidence_stale(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); output,_=self._fixture(root)
            (output/'assets/publisher/signal.css').write_text('body{overflow:auto}',encoding='utf-8')
            result=visual_evidence(root,output,'research.pages.canary.v1')
            self.assertEqual(result['status'],'FAIL')
            self.assertTrue(any('stale' in error for error in result['errors']))

    def test_mobile_overflow_assertion_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); output,path=self._fixture(root)
            evidence=json.loads(path.read_text(encoding='utf-8'))
            evidence['viewports'][1]['no_horizontal_overflow']=False
            path.write_text(json.dumps(evidence),encoding='utf-8')
            result=visual_evidence(root,output,'research.pages.canary.v1')
            self.assertEqual(result['status'],'FAIL')
            self.assertIn('mobile visual assertion failed: no_horizontal_overflow',result['errors'])

if __name__=='__main__': unittest.main()
