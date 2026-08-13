from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import unittest


ROOT=Path(__file__).resolve().parents[1]
VALIDATOR=ROOT/'tools'/'validate_canonical_html.py'


class CanonicalHtmlTests(unittest.TestCase):
    def test_example_packet_passes(self):
        packet=ROOT/'incoming'/'example-reliability-publication'/'PUBLISH_MANIFEST.json'
        result=subprocess.run([sys.executable,str(VALIDATOR),str(packet)],text=True,capture_output=True)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)

    def test_active_html_is_rejected(self):
        from tools.validate_canonical_html import ProfileParser
        parser=ProfileParser(); parser.feed('<article data-tare-document><script>bad()</script></article>')
        self.assertIn('active element not allowed: script',parser.errors)


if __name__=='__main__':
    unittest.main()
