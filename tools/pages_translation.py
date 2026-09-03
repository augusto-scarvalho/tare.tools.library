from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path


TRANSLATION_MANIFEST = "TRANSLATION_MANIFEST.en.json"
EN_ARTICLE = "article.en.html"
EN_METADATA = "document-metadata.en.json"


def file_hash(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _json(path: Path, label: str) -> tuple[dict | None, list[str]]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return None, [f"{label} invalid: {exc}"]
    if not isinstance(value, dict):
        return None, [f"{label} must be an object"]
    return value, []


def validate_pages_translation(
    packet: Path, manifest: dict, *, legacy_decision: bool = False
) -> tuple[list[str], dict | None]:
    """Validate a retained pt-BR to English legacy Pages derivative."""
    if "pages" not in manifest.get("requested_channels", []):
        return [], None
    source_metadata, errors = _json(packet / "document-metadata.json", "document metadata")
    if errors or source_metadata is None:
        return errors, None
    if source_metadata.get("language") != "pt-BR":
        return [], None
    if legacy_decision:
        return [], None
    required = (TRANSLATION_MANIFEST, EN_ARTICLE, EN_METADATA)
    errors = [
        f"Pages pt-BR record requires retained {name}"
        for name in required
        if not (packet / name).is_file()
    ]
    artifacts = manifest.get("artifacts", [])
    errors.extend(
        f"Pages pt-BR record must declare {name} as an artifact"
        for name in required
        if name not in artifacts
    )
    if errors:
        return errors, None
    translation, errors = _json(packet / TRANSLATION_MANIFEST, "translation manifest")
    translated_metadata, metadata_errors = _json(packet / EN_METADATA, "English metadata")
    errors.extend(metadata_errors)
    if errors or translation is None or translated_metadata is None:
        return errors, None
    primary = manifest.get("primary_artifact")
    expected = {
        "schema_version": "1.0",
        "translation_of": manifest.get("document_id"),
        "source_path": primary,
        "translation_path": EN_ARTICLE,
        "source_language": "pt-BR",
        "target_language": "en",
    }
    for key, value in expected.items():
        if translation.get(key) != value:
            errors.append(f"translation manifest {key} mismatch")
    if translation.get("translation_status") not in {
        "MACHINE_TRANSLATED_UNREVIEWED",
        "HUMAN_REVIEWED",
    }:
        errors.append("translation manifest status must be current")
    for key in ("translation_id", "translator", "translated_at"):
        if not isinstance(translation.get(key), str) or not translation[key].strip():
            errors.append(f"translation manifest {key} required")
    source = packet / str(primary)
    article = packet / EN_ARTICLE
    if not source.is_file():
        errors.append("translation source artifact missing")
    elif translation.get("source_sha256") != file_hash(source):
        errors.append("translation manifest source_sha256 mismatch")
    if translation.get("translation_sha256") != file_hash(article):
        errors.append("translation manifest translation_sha256 mismatch")
    if translation.get("translation_size_bytes") not in {None, article.stat().st_size}:
        errors.append("translation manifest translation_size_bytes mismatch")
    for key in (
        "document_id",
        "document_type",
        "status",
        "created_at",
        "authors",
        "bounded_contexts",
    ):
        if translated_metadata.get(key) != source_metadata.get(key):
            errors.append(f"English metadata {key} must preserve source identity")
    if translated_metadata.get("language") != "en":
        errors.append("English metadata language must be en")
    for key in ("title", "abstract"):
        if not isinstance(translated_metadata.get(key), str) or not translated_metadata[key].strip():
            errors.append(f"English metadata {key} required")
    return errors, None if errors else {
        "language": "en",
        "primary_artifact": EN_ARTICLE,
        "metadata_artifact": EN_METADATA,
        "translation_manifest": TRANSLATION_MANIFEST,
        "translation_manifest_sha256": file_hash(packet / TRANSLATION_MANIFEST),
    }
