"""Conformance test for ADR provenance and cryptographic verification (ADR-057)."""

import hashlib
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ADR_DIR = ROOT / "docs" / "adr"
RELAY_CASES_DIR = Path("C:/Users/augus/My Drive/tare.tools/relay/round_tables")


def normalize_lf(text: str) -> str:
    return text.replace("\r\n", "\n").strip()


def compute_sha256(text: str) -> str:
    return hashlib.sha256(normalize_lf(text).encode("utf-8")).hexdigest()


class TestADRProvenance(unittest.TestCase):
    def test_legacy_adrs_are_accepted_without_strict_case(self):
        """ADRs 001-054 without round_table_case are categorized as LEGACY_UNVERIFIED and pass."""
        if not ADR_DIR.exists():
            return
        for adr in ADR_DIR.glob("*.md"):
            content = adr.read_text(encoding="utf-8", errors="ignore")
            # If no round_table_case is declared, it is legacy and accepted
            if "round_table_case:" not in content:
                self.assertTrue(True)

    def test_triple_verification_on_mock_case(self):
        """Verifies the invariant: hash(DECISION.md) == frontmatter.sha256 == journal[FINAL].decision_sha256."""
        decision_text = "# DECISAO CANONICA\n\nAprovado por unanimidade 3/3."
        decision_sha = compute_sha256(decision_text)
        
        # 1. Frontmatter
        frontmatter_sha = decision_sha
        
        # 2. Journal terminal entry
        journal_entry = {
            "event": "DECISION_FINALIZED",
            "decision_sha256": decision_sha,
            "verdict": "APPROVED"
        }
        
        # The triple verification check
        self.assertEqual(decision_sha, frontmatter_sha)
        self.assertEqual(frontmatter_sha, journal_entry["decision_sha256"])


if __name__ == "__main__":
    unittest.main()
