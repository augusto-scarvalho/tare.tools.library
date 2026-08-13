from __future__ import annotations

import json
import importlib
from pathlib import Path
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]

from tools.validate_canonical_html import validate_packet


def write_packet(root: Path, html: str, *, language: str="en") -> dict:
    manifest={
        "packet_version":"1.1","document_id":"research.test.html","document_type":"research",
        "status":"RESEARCH","repository":"tare.tools.research","bounded_contexts":["Reliability"],
        "artifacts":["article.html","document-metadata.json"],"primary_artifact":"article.html",
        "requested_channels":["pages"],"canonical_change":False,
    }
    metadata={
        "document_id":"research.test.html","title":"Study","document_type":"research","status":"RESEARCH",
        "created_at":"2026-08-13","language":language,"abstract":"Test abstract.",
        "authors":[{"name":"Test","role":"editor"}],"bounded_contexts":["Reliability"],
        "provenance":{"origin":"TEST"},
    }
    (root/"article.html").write_text(html,encoding="utf-8")
    (root/"document-metadata.json").write_text(json.dumps(metadata),encoding="utf-8")
    return manifest


def valid_html(lang: str="en") -> str:
    return f'''<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><title>Study</title></head><body><main><article data-tare-document><header data-tare-role="document-header"><h1>Study</h1><p data-tare-role="abstract">Test abstract.</p></header><aside data-tare-role="authority-boundary">RESEARCH.</aside><section id="scope" data-tare-section="scope"><h2>Scope</h2></section><section id="evidence" data-tare-section="evidence"><h2>Evidence</h2></section><section id="findings" data-tare-section="findings"><h2>Findings</h2></section><section id="limitations" data-tare-section="limitations"><h2>Limitations</h2></section><section id="references" data-tare-section="references"><h2>References</h2></section></article></main></body></html>'''


class CanonicalHtmlTests(unittest.TestCase):
    def test_import_uses_the_canonical_validator_module(self):
        module=importlib.import_module('tools.validate_canonical_html')
        self.assertEqual(Path(module.__file__).resolve(),ROOT/'tools'/'validate_canonical_html.py')

    def test_example_packet_passes(self):
        packet=ROOT/'incoming'/'example-reliability-publication'
        manifest=json.loads((packet/'PUBLISH_MANIFEST.json').read_text(encoding='utf-8'))
        self.assertEqual(validate_packet(packet,manifest),[])

    def test_active_html_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); html=valid_html().replace('</article>','<script>bad()</script></article>')
            errors=validate_packet(root,write_packet(root,html))
            self.assertIn('active element not allowed: script',errors)

    def test_article_must_be_direct_child_of_main(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); html=valid_html().replace('<main><article','<main><div><article').replace('</article></main>','</article></div></main>')
            errors=validate_packet(root,write_packet(root,html))
            self.assertTrue(any('main > article[data-tare-document]' in x for x in errors),errors)

    def test_required_sections_must_be_inside_article(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); html=valid_html().replace('<section id="references" data-tare-section="references"><h2>References</h2></section>','').replace('</main>','</main><section id="references" data-tare-section="references"><h2>References</h2></section>')
            errors=validate_packet(root,write_packet(root,html))
            self.assertIn('HTML role/section required exactly once: references',errors)

    def test_language_must_match_metadata(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); errors=validate_packet(root,write_packet(root,valid_html('pt-BR'),language='en'))
            self.assertIn('HTML lang disagrees with metadata language',errors)

    def test_pt_br_packet_passes(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); errors=validate_packet(root,write_packet(root,valid_html('pt-BR'),language='pt-BR'))
            self.assertEqual(errors,[])

    def test_remote_asset_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); html=valid_html().replace('</article>','<img src="https://example.test/x.png" alt="x"></article>')
            self.assertIn('remote asset not allowed: https://example.test/x.png',validate_packet(root,write_packet(root,html)))

    def test_image_requires_alt_text(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); html=valid_html().replace('</article>','<img src="diagram.svg"></article>')
            self.assertIn('image missing alt text',validate_packet(root,write_packet(root,html)))


if __name__=='__main__':unittest.main()
