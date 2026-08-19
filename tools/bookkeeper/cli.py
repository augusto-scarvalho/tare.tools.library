"""CLI Interface for Bookkeeper in tare.tools.library."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .dedup_detector import detect_duplicates
from .ssot_registry import audit_ssot_registry
from .tombstone_manager import apply_tombstone, verify_tombstones


def main() -> int:
    parser = argparse.ArgumentParser(description="Bookkeeper CLI for tare.tools.library")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommand: dedup
    dedup_parser = subparsers.add_parser("dedup", help="Scan for duplicate and near-duplicate documents")
    dedup_parser.add_argument("--root", default=".", help="Root directory to scan")
    dedup_parser.add_argument("--threshold", type=float, default=0.70, help="Similarity threshold (0.0 - 1.0)")

    # Subcommand: ssot
    ssot_parser = subparsers.add_parser("ssot", help="Audit CANONICAL_SSOT registry for split-brain violations")
    ssot_parser.add_argument("--root", default=".", help="Root directory to audit")

    # Subcommand: tombstone
    tomb_parser = subparsers.add_parser("tombstone", help="Apply or verify tombstone markers")
    tomb_parser.add_argument("--verify", action="store_true", help="Verify all tombstone target links")
    tomb_parser.add_argument("--file", help="File to apply tombstone to")
    tomb_parser.add_argument("--target", help="Canonical target URL / path")
    tomb_parser.add_argument("--reason", default="Superseded during library consolidation", help="Reason for tombstone")

    # Subcommand: audit (all-in-one)
    audit_parser = subparsers.add_parser("audit", help="Run full bookkeeping audit suite")
    audit_parser.add_argument("--root", default=".", help="Root directory to audit")

    args = parser.parse_args()
    root_path = Path(args.root if hasattr(args, "root") else ".")

    if args.command == "dedup":
        print(f"[BOOKKEEPER] Running Deduplication Audit on '{root_path}' (threshold={args.threshold})...")
        report = detect_duplicates(root_path, similarity_threshold=args.threshold)
        print(f"[SUMMARY] Total files scanned: {report.total_files_scanned}")
        if report.is_clean:
            print("[OK] No duplicate documents detected! Acervo is clean.")
            return 0
        else:
            print(f"[WARN] Found {len(report.duplicates_found)} duplicate/near-duplicate pairs:")
            for m in report.duplicates_found:
                tag = "[EXACT]" if m.is_exact else f"[{m.similarity_score * 100:.1f}%]"
                print(f"  - {tag} '{m.file_a}' <--> '{m.file_b}' (overlap: {m.overlap_tokens} tokens)")
            return 0  # Informational

    elif args.command == "ssot":
        print(f"[BOOKKEEPER] Auditing SSOT Registry on '{root_path}'...")
        report = audit_ssot_registry(root_path)
        print(f"[SUMMARY] Total documents: {report.total_documents} | Canonical SSOT docs: {report.canonical_documents}")
        if report.is_valid:
            print("[OK] SSOT Registry is 100% compliant! Exactly 1 canonical doc per topic.")
            return 0
        else:
            print(f"[ERROR] Found {len(report.violations)} SSOT split-brain violations:")
            for v in report.violations:
                print(f"  - Doc ID '{v.doc_id}': conflicting files: {v.files}")
            return 1

    elif args.command == "tombstone":
        if args.verify:
            print(f"[BOOKKEEPER] Verifying Tombstones in '{root_path}'...")
            res = verify_tombstones(root_path)
            print(f"[SUMMARY] Total tombstones: {res.total_tombstones} | Valid: {res.valid_tombstones}")
            if res.is_healthy:
                print("[OK] All tombstones are pointing to existing files!")
                return 0
            else:
                print(f"[ERROR] Found {len(res.broken_pointers)} broken tombstone pointers:")
                for src, tgt in res.broken_pointers:
                    print(f"  - '{src}' -> broken target '{tgt}'")
                return 1
        elif args.file and args.target:
            print(f"[TOMBSTONE] Applying Tombstone to '{args.file}' -> pointing to '{args.target}'...")
            apply_tombstone(args.file, args.target, args.reason)
            print("[OK] Tombstone applied successfully!")
            return 0
        else:
            print("[ERROR] Must specify --verify or both --file and --target")
            return 1

    elif args.command == "audit":
        print(f"[BOOKKEEPER] Running Full Library Audit Suite on '{root_path}'...")
        ssot_rep = audit_ssot_registry(root_path)
        tomb_res = verify_tombstones(root_path)
        dedup_rep = detect_duplicates(root_path, similarity_threshold=0.85)

        print("\n--- AUDIT SUMMARY ---")
        print(f"1. SSOT Compliance: {'[OK] PASS' if ssot_rep.is_valid else '[FAIL]'}")
        print(f"2. Tombstone Health: {'[OK] PASS' if tomb_res.is_healthy else '[FAIL]'}")
        print(f"3. High Duplication (>85%): {len(dedup_rep.duplicates_found)} pairs detected.")

        if not ssot_rep.is_valid or not tomb_res.is_healthy:
            return 1
        print("[SUCCESS] Full Library Audit PASSED!\n")
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
