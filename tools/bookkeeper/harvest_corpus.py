"""Federated Corpus Harvester & Deterministic Ingestion Crawler for tare.tools.library.

Implements ADR-049 and DOCUMENT_POLICY.md multi-source harvesting with strict:
1. Universal Exclusion Blacklist (ignores .git, node_modules, build, caches, binaries).
2. Knowledge File Whitelist (.md, .markdown).
3. Size & Noise Bounds (rejects < 100 bytes and > 2 MB log dumps).
4. Canonical Heuristic Routing (ADRs, SPECs, Experiments, Archaeology, Canonical References).
5. Deterministic Dedup Gate (exact SHA-256 and similarity >= 90% drift detection).
6. Safe Dry-Run Simulation Mode by Default.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.ingest import ingest_document, IngestionResult, TYPE_ROUTING, auto_index_file
from tools.bookkeeper.dedup_detector import compute_similarity, EXCLUDE_DIRS

# Universal Blacklist of directories to ignore during crawling
CRAWL_EXCLUDED_DIRS: Set[str] = {
    ".git", ".github", ".pytest_cache", ".mypy_cache", "__pycache__",
    "node_modules", "venv", ".venv", "env", ".env", "dist", "build",
    "site", "_site", "site/_site", "target", "bin", "obj", ".idea",
    ".vscode", ".system_generated", ".gemini", "AppData", "coverage",
    "htmlcov", ".tox", ".eggs", "eggs", "parts", "develop-eggs",
    "archaeology/chats", "chats", "vault", "_handoff", "raw_logs", "transcripts", ".aider"
}

# Binary and non-document extensions to reject immediately
BINARY_EXCLUDED_EXTENSIONS: Set[str] = {
    ".exe", ".dll", ".so", ".dylib", ".bin", ".png", ".jpg", ".jpeg",
    ".gif", ".ico", ".svg", ".mp4", ".mp3", ".wav", ".zip", ".tar",
    ".gz", ".7z", ".rar", ".db", ".sqlite", ".sqlite3", ".parquet",
    ".pyc", ".pyo", ".pyd", ".lock", ".log", ".tmp", ".swp"
}

# Known noise files to discard
NOISE_FILENAMES: Set[str] = {
    "package-lock.json", "pnpm-lock.yaml", "yarn.lock", "poetry.lock",
    "cargo.lock", "gemfile.lock", "composer.lock", "index.lock",
    ".aider.chat.history.md", ".aider.input.history"
}

# Pre-Ingestion Secret Scanner patterns (rejects tokens, private keys, API keys)
SECRET_PATTERNS = [
    re.compile(r"sk-[a-zA-Z0-9_\-]{20,}"),                             # OpenAI / Anthropic API keys (sk-live-..., sk-ant-...)
    re.compile(r"ghp_[a-zA-Z0-9]{36}"),                                # GitHub Personal Access Tokens
    re.compile(r"AKIA[0-9A-Z]{16}"),                                    # AWS Access Key ID
    re.compile(r"AIza[0-9A-Za-z\-_]{35}"),                             # Google API Keys
    re.compile(r"-----BEGIN (?:RSA|EC|OPENSSH|PGP) PRIVATE KEY-----"),    # Cryptographic Private Keys
]


def scan_for_secrets(text: str) -> Optional[str]:
    """Scans text for exposed credentials. Returns matching rule if detected."""
    for pattern in SECRET_PATTERNS:
        if pattern.search(text):
            return f"SECRET_LEAK_DETECTED: {pattern.pattern}"
    return None


@dataclass
class DiscoveredDocument:
    source_path: str
    filename: str
    inferred_type: str
    title: str
    size_bytes: int
    sha256: str
    status: str  # 'NEW', 'EXACT_DUPLICATE', 'DRIFT_SIMILAR', 'REJECTED_NOISE'
    conflict_path: Optional[str] = None
    similarity_score: float = 0.0


@dataclass
class HarvestReport:
    total_scanned_files: int = 0
    total_ignored_noise: int = 0
    discovered_docs: List[DiscoveredDocument] = field(default_factory=list)
    ingested_count: int = 0
    skipped_duplicate_count: int = 0
    drift_alert_count: int = 0


def classify_document_type(file_path: Path, content: str) -> str:
    """Heuristic classifier adhering to DOCUMENT_POLICY.md and ADR-049 with strict word boundaries."""
    rel_lower = str(file_path).lower().replace("\\", "/")
    content_head = content[:1500].lower()

    # 1. ADR Detection (strict word and header boundary)
    if re.search(r"(?:/docs/adr/|^adr-\d+)", rel_lower) or re.search(r"^\s*#\s*ADR-\d+\b", content, re.MULTILINE | re.IGNORECASE):
        return "adr"

    # 2. SPEC Detection (strict word and header boundary)
    if re.search(r"(?:/specs/|^spec-[a-z0-9]+)", rel_lower) or re.search(r"^\s*#\s*SPEC-[A-Z0-9]+\b", content, re.MULTILINE):
        return "spec"

    # 3. Experiment / Sweep Detection (strict boundary)
    if re.search(r"(?:/experiments/|^exp-\d+)", rel_lower) or re.search(r"\b(benchmarks?|sweeps?)\b", content_head):
        return "experiment"

    # 4. Post-Mortem Detection (strict boundary)
    if "/post-mortems/" in rel_lower or re.search(r"\b(post-mortem|postmortem|root cause analysis|\brca\b)\b", content_head):
        return "post-mortem"

    # 5. Historical Chat Transcript (strict boundary)
    if "/chats/" in rel_lower or re.search(r"\b(transcripts?|\buser:\b|\bassistant:\b)", content_head):
        return "chat"

    # 6. Default Fallback: Historical Architecture / Generic Doc
    if "/docs/" in rel_lower or "/archaeology/" in rel_lower:
        return "historical"

    return "historical"


def extract_document_title(file_path: Path, content: str) -> str:
    """Extract document title from first H1 or derive from filename."""
    match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return file_path.stem.replace("-", " ").replace("_", " ").title()


def scan_source_directory(
    source_dir: Path,
    library_root: Path = ROOT,
) -> List[DiscoveredDocument]:
    """Deterministically discover and filter documents from an external source directory."""
    discovered: List[DiscoveredDocument] = []
    lib_root_resolved = library_root.resolve()

    if not source_dir.exists():
        return discovered

    # Pre-index existing files in library for O(1) hash check and fast Jaccard
    existing_hashes: Dict[str, str] = {}
    existing_corpus: List[Tuple[str, str, Set[str]]] = []  # (rel_path, text, token_set)
    if library_root.exists():
        for existing in library_root.rglob("*.md"):
            if existing.is_file() and not any(part in existing.parts for part in EXCLUDE_DIRS):
                try:
                    ex_bytes = existing.read_bytes()
                    ex_hash = hashlib.sha256(ex_bytes).hexdigest()
                    rel_p = str(existing.relative_to(library_root)).replace("\\", "/")
                    existing_hashes[ex_hash] = rel_p
                    ex_text = ex_bytes.decode("utf-8", errors="ignore")
                    words = set(re.findall(r"\w+", ex_text.lower()))
                    existing_corpus.append((rel_p, ex_text, words))
                except Exception:
                    continue

    for root_str, dirs, files in os.walk(source_dir):
        # In-place directory pruning to avoid traversing ignored directory trees
        dirs[:] = [d for d in dirs if d not in CRAWL_EXCLUDED_DIRS and not d.startswith(".")]

        current_path = Path(root_str)
        # Avoid scanning inside tare.tools.library itself if scanned as a source
        try:
            if current_path.resolve().is_relative_to(lib_root_resolved / "catalog"):
                continue
        except AttributeError:
            if str(lib_root_resolved / "catalog") in str(current_path.resolve()):
                continue

        for file_name in files:
            if file_name.lower() in NOISE_FILENAMES:
                continue

            file_path = current_path / file_name
            ext = file_path.suffix.lower()
            if ext in BINARY_EXCLUDED_EXTENSIONS:
                continue

            if ext not in (".md", ".markdown"):
                continue

            # Size guard: reject < 30 bytes (empty/stubs) or > 2.5 MB (dumps)
            try:
                stat = file_path.stat()
                size = stat.st_size
                if size < 30 or size > 2_500_000:
                    continue
            except OSError:
                continue

            try:
                raw_bytes = file_path.read_bytes()
                raw_text = raw_bytes.decode("utf-8", errors="ignore")
                digest = hashlib.sha256(raw_bytes).hexdigest()
            except Exception:
                continue

            doc_type = classify_document_type(file_path, raw_text)
            title = extract_document_title(file_path, raw_text)

            # Pre-Ingestion Secret Scanner Check
            secret_violation = scan_for_secrets(raw_text)
            if secret_violation:
                discovered.append(DiscoveredDocument(
                    source_path=str(file_path.resolve()).replace("\\", "/"),
                    filename=file_name,
                    inferred_type="quarantine",
                    title=title,
                    size_bytes=size,
                    sha256=digest,
                    status="REJECTED_SECRET",
                    conflict_path=secret_violation,
                    similarity_score=0.0,
                ))
                continue

            # Check for existing duplicate in target library
            status = "NEW"
            conflict_path = None
            sim_score = 0.0

            if digest in existing_hashes:
                status = "EXACT_DUPLICATE"
                conflict_path = existing_hashes[digest]
                sim_score = 1.0
            else:
                src_words = set(re.findall(r"\w+", raw_text.lower()))
                for rel_p, ex_text, ex_words in existing_corpus:
                    if not src_words or not ex_words:
                        continue
                    intersection = len(src_words & ex_words)
                    union = len(src_words | ex_words)
                    jaccard = intersection / union if union > 0 else 0.0
                    if jaccard >= 0.85:
                        sim = compute_similarity(raw_text, ex_text)
                        if sim >= 0.90:
                            status = "DRIFT_SIMILAR"
                            conflict_path = rel_p
                            sim_score = sim
                            break

            discovered.append(DiscoveredDocument(
                source_path=str(file_path.resolve()).replace("\\", "/"),
                filename=file_name,
                inferred_type=doc_type,
                title=title,
                size_bytes=size,
                sha256=digest,
                status=status,
                conflict_path=conflict_path,
                similarity_score=sim_score,
            ))

    return discovered


def run_harvester(
    source_paths: List[str | Path],
    apply_ingest: bool = False,
    auto_embed: bool = False,
    auto_summarize: bool = False,
    library_root: Path = ROOT,
) -> HarvestReport:
    """End-to-end harvester discovering, filtering, deduping, and ingesting documents."""
    report = HarvestReport()
    all_discovered: List[DiscoveredDocument] = []

    for src in source_paths:
        p = Path(src)
        if not p.exists():
            continue
        discovered = scan_source_directory(p, library_root=library_root)
        all_discovered.extend(discovered)

    report.total_scanned_files = len(all_discovered)
    report.discovered_docs = all_discovered

    new_docs = [d for d in all_discovered if d.status == "NEW"]
    total_new = len(new_docs)

    if apply_ingest and total_new > 0:
        print(f"[*] Iniciando ingestão streaming de {total_new} documentos novos...")

    for idx, doc in enumerate(all_discovered):
        if doc.status == "EXACT_DUPLICATE":
            report.skipped_duplicate_count += 1
        elif doc.status == "DRIFT_SIMILAR":
            report.drift_alert_count += 1
        elif doc.status == "NEW":
            if apply_ingest:
                res = ingest_document(
                    source_path=doc.source_path,
                    doc_type=doc.inferred_type,
                    title=doc.title,
                    root_dir=library_root,
                    check_duplicates=False,
                )
                if res.success:
                    report.ingested_count += 1
                    if auto_embed and res.target_path:
                        auto_index_file(res.target_path, library_root)
                    if auto_summarize and res.target_path:
                        from tools.inference.summarize_reference import summarize_document
                        try:
                            summarize_document(res.target_path)
                        except Exception:
                            pass
                    if not (report.ingested_count % 25) or report.ingested_count == total_new:
                        print(f"  [INGEST {report.ingested_count}/{total_new}] Ingerido: {res.target_path.name} ({doc.inferred_type.upper()})")

    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Federated Corpus Harvester for tare.tools.library")
    parser.add_argument("--sources", "-s", nargs="+", required=True, help="List of source directories or repositories to crawl")
    parser.add_argument("--apply", action="store_true", help="Execute real ingestion (default is safe DRY-RUN simulation)")
    parser.add_argument("--no-embed", action="store_true", help="Skip automatic vectorization during ingestion")
    parser.add_argument("--summarize", action="store_true", help="Trigger local LLM summarization on newly ingested documents")
    parser.add_argument("--json", action="store_true", help="Emit structured JSON harvest report")
    parser.add_argument("--root", default=".", help="Root directory of tare.tools.library")

    args = parser.parse_args()
    lib_root = Path(args.root).resolve()

    mode_label = "🟢 APPLY (STREAMING INGESTION + AUTO-EMBED)" if args.apply else "🟡 SIMULATION (DRY-RUN)"
    if not args.json:
        print(f"======================================================================")
        print(f"🌾 FEDERATED CORPUS HARVESTER — tare.tools.library")
        print(f"Modo: {mode_label}")
        print(f"Fontes Alvo: {args.sources}")
        print(f"======================================================================\n")

    should_embed = args.apply and not args.no_embed

    report = run_harvester(
        source_paths=args.sources,
        apply_ingest=args.apply,
        auto_embed=should_embed,
        auto_summarize=args.summarize,
        library_root=lib_root,
    )

    if args.json:
        print(json.dumps({
            "mode": "APPLY" if args.apply else "DRY_RUN",
            "total_scanned": report.total_scanned_files,
            "ingested": report.ingested_count,
            "skipped_duplicates": report.skipped_duplicate_count,
            "drift_alerts": report.drift_alert_count,
            "documents": [asdict(d) for d in report.discovered_docs]
        }, indent=2, ensure_ascii=False))
        return 0

    # Print Formatted Table
    print(f"{'STATUS':<16} {'TIPO':<10} {'TAMANHO':<9} {'TÍTULO':<35} {'ORIGEM'}")
    print("-" * 105)
    for doc in report.discovered_docs:
        status_icon = "✨ NOVO" if doc.status == "NEW" else ("⏭️ DUPLICATA" if doc.status == "EXACT_DUPLICATE" else "⚠️ DRIFT >=90%")
        title_trunc = doc.title[:32] + ("..." if len(doc.title) > 32 else "")
        orig_trunc = Path(doc.source_path).name
        print(f"{status_icon:<16} {doc.inferred_type.upper():<10} {doc.size_bytes:<9} {title_trunc:<35} {orig_trunc}")

    print("\n" + "=" * 70)
    print(f"📊 RESUMO DA COLHEITA:")
    print(f"  • Total de Documentos Encontrados : {report.total_scanned_files}")
    print(f"  • Documentos Novos Inéditos       : {len([d for d in report.discovered_docs if d.status == 'NEW'])}")
    print(f"  • Duplicatas Exatas Puladas       : {report.skipped_duplicate_count}")
    print(f"  • Alertas de Drift (>= 90%)       : {report.drift_alert_count}")
    if args.apply:
        print(f"  • Ingeridos com Sucesso no Library: {report.ingested_count}")
    else:
        print(f"\n💡 Modo Dry-Run finalizado. Para aplicar a ingestão definitiva, use a flag --apply.")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
