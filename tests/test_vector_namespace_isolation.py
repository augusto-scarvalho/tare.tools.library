from __future__ import annotations

from pathlib import Path

from tools.indexer.embed_corpus import LibraryVectorDB


def _insert(vdb: LibraryVectorDB, path: str, model: str, sha256: str, chunk_index: int = 0) -> None:
    vdb.upsert_chunk(
        doc_id=f"{model}:{path}",
        relative_path=path,
        chunk_index=chunk_index,
        chunk_text=f"content for {model} at {path}",
        sha256=sha256,
        embedding=[1.0, 0.0],
        provenance="real",
        model_name=model,
    )


def test_hash_listing_and_stale_removal_preserve_model_namespace(tmp_path: Path) -> None:
    vdb = LibraryVectorDB(tmp_path / "vectors.db")
    _insert(vdb, "docs/shared.md", "model-a", "sha-a")
    _insert(vdb, "docs/shared.md", "model-b", "sha-b", chunk_index=1)
    _insert(vdb, "docs/model-b-only.md", "model-b", "sha-b-only")

    assert vdb.get_indexed_file_hashes("model-a") == {"docs/shared.md": "sha-a"}
    assert vdb.remove_stale_documents(set(), "model-a") == 1
    assert vdb.get_indexed_file_hashes("model-a") == {}
    assert vdb.get_indexed_file_hashes("model-b") == {
        "docs/model-b-only.md": "sha-b-only",
        "docs/shared.md": "sha-b",
    }
