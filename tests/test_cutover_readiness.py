from __future__ import annotations

import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from cutover_readiness import generate
from pages_common import semantic_fingerprint


class CutoverReadinessTests(unittest.TestCase):
    def test_semantic_surface_detects_same_text_structure_loss(self):
        strong=BeautifulSoup('<article><p><strong>same words</strong></p></article>','html.parser').article
        plain=BeautifulSoup('<article><p><span>same words</span></p></article>','html.parser').article
        self.assertEqual(strong.get_text(' ',strip=True),plain.get_text(' ',strip=True))
        self.assertNotEqual(semantic_fingerprint(strong),semantic_fingerprint(plain))


if __name__=='__main__': unittest.main()
