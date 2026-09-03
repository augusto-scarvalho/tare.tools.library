from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from pages_translation import (  # noqa: E402
    EN_ARTICLE,
    EN_METADATA,
    TRANSLATION_MANIFEST,
    validate_pages_translation,
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class PagesTranslationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.packet = Path(self.tmp.name)
        source = {
            "document_id": "research.translation.test",
            "document_type": "research",
            "status": "RESEARCH",
            "created_at": "2026-08-14",
            "language": "pt-BR",
            "title": "Fonte",
            "abstract": "Resumo",
            "authors": [{"name": "A", "role": "author"}],
            "bounded_contexts": ["Workflow"],
            "provenance": {"origin": "TEST"},
        }
        translated = {**source, "language": "en", "title": "Source", "abstract": "Abstract"}
        (self.packet / "article.html").write_text(
            '<html lang="pt-BR">fonte</html>', encoding="utf-8"
        )
        (self.packet / EN_ARTICLE).write_text(
            '<html lang="en">source</html>', encoding="utf-8"
        )
        (self.packet / "document-metadata.json").write_text(
            json.dumps(source), encoding="utf-8"
        )
        (self.packet / EN_METADATA).write_text(json.dumps(translated), encoding="utf-8")
        self.manifest = {
            "packet_version": "1.1",
            "document_id": source["document_id"],
            "requested_channels": ["pages"],
            "artifacts": [
                "article.html",
                "document-metadata.json",
                EN_ARTICLE,
                EN_METADATA,
                TRANSLATION_MANIFEST,
            ],
            "primary_artifact": "article.html",
        }
        translation = {
            "schema_version": "1.0",
            "translation_id": "translation.test.en",
            "translation_of": source["document_id"],
            "source_path": "article.html",
            "source_sha256": sha(self.packet / "article.html"),
            "translation_path": EN_ARTICLE,
            "translation_sha256": sha(self.packet / EN_ARTICLE),
            "translation_size_bytes": (self.packet / EN_ARTICLE).stat().st_size,
            "source_language": "pt-BR",
            "target_language": "en",
            "translation_status": "MACHINE_TRANSLATED_UNREVIEWED",
            "translator": "test",
            "translated_at": "2026-08-14T00:00:00Z",
        }
        (self.packet / TRANSLATION_MANIFEST).write_text(
            json.dumps(translation), encoding="utf-8"
        )

    def tearDown(self):
        self.tmp.cleanup()

    def test_valid_pt_br_pages_derivative_passes(self):
        errors, projection = validate_pages_translation(self.packet, self.manifest)
        self.assertEqual(errors, [])
        self.assertEqual(projection["primary_artifact"], EN_ARTICLE)

    def test_missing_derivative_is_denied(self):
        (self.packet / EN_ARTICLE).unlink()
        errors, _ = validate_pages_translation(self.packet, self.manifest)
        self.assertTrue(any(EN_ARTICLE in error for error in errors), errors)

    def test_bad_hash_and_superseded_derivative_are_denied(self):
        manifest = json.loads((self.packet / TRANSLATION_MANIFEST).read_text(encoding="utf-8"))
        manifest["translation_sha256"] = "0" * 64
        manifest["translation_status"] = "SUPERSEDED"
        (self.packet / TRANSLATION_MANIFEST).write_text(
            json.dumps(manifest), encoding="utf-8"
        )
        errors, _ = validate_pages_translation(self.packet, self.manifest)
        self.assertTrue(any("status" in error for error in errors), errors)
        self.assertTrue(any("translation_sha256" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
