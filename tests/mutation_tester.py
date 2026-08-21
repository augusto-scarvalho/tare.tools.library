#!/usr/bin/env python3
"""
Zero-Dependency Mutation Testing Engine for tare.tools.library
Generates systematic syntactic and semantic mutants on core library tools
and validates that the test suite kills 100% of mutations.
"""

import os
import sys
import time
import shutil
import tempfile
import subprocess
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional


@dataclass
class MutationRule:
    name: str
    target_pattern: str
    replacement_pattern: str
    description: str


@dataclass
class MutationResult:
    mutant_id: int
    target_file: str
    rule_name: str
    line_number: int
    original_line: str
    mutated_line: str
    status: str  # "KILLED", "SURVIVED", "TIMEOUT", "ERROR"
    output: str = ""


CORE_MUTATION_RULES = [
    # 1. Relational Operator Mutations (ROR)
    MutationRule("ROR_GE_TO_GT", ">= 0.90", "> 0.90", "Relaxed deduplication threshold to strict greater-than"),
    MutationRule("ROR_GE_TO_LT", ">= 0.90", "< 0.90", "Inverted deduplication threshold operator"),
    MutationRule("ROR_EQ_TO_NEQ", "dim != q_dim:", "dim == q_dim:", "Inverted vector dimension mismatch guard"),
    MutationRule("ROR_GPU_EQ_0", "n_gpu == 0", "n_gpu != 0", "Inverted GPU layers offload probe check"),
    MutationRule("ROR_DEV_CPU", 'dev == "cpu"', 'dev != "cpu"', "Inverted CPU device string probe check"),
    MutationRule("ROR_NOT_MODEL", "required_model not in model_ids", "required_model in model_ids", "Inverted model identity check"),

    # 2. Concurrency & Durability Primitives
    MutationRule("AOD_XB_TO_WB", "open(\"xb\")", "open(\"wb\")", "Downgraded atomic exclusive creation ('xb') to overwrite ('wb')"),
    MutationRule("AOD_BYPASS_FSYNC", "os.fsync(tf.fileno())", "pass # os.fsync bypassed", "Bypassed manifest fsync durability call"),
    MutationRule("AOD_DISABLE_WAL", "PRAGMA journal_mode=WAL;", "PRAGMA journal_mode=DELETE;", "Disabled SQLite WAL mode"),

    # 3. Namespace & Isolation Semantics
    MutationRule("ISO_ALLOW_ANY_DEFAULT", "allow_any_namespace: bool = False", "allow_any_namespace: bool = True", "Relaxed vector namespace isolation default to True"),
    MutationRule("ISO_PROV_FILTER_BYPASS", "provenance = ?", "1 = 1", "Bypassed SQL WHERE provenance filter"),
    MutationRule("ISO_MODEL_FILTER_BYPASS", "model_name = ?", "1 = 1", "Bypassed SQL WHERE model_name filter"),

    # 4. Fail-Closed Return Inversions
    MutationRule("FC_READINESS_TRUE", 'return {"ready": False, "error": "Server is running in CPU-only mode', 'return {"ready": True, "error": "Server is running in CPU-only mode', "Inverted CPU readiness probe to fail-open"),
    MutationRule("FC_OFFLINE_TRUE", 'return {"online": False, "error": str(e2)', 'return {"online": True, "error": str(e2)', "Inverted offline health check to return online"),
]


TARGET_MODULES = [
    "tools/ingest.py",
    "tools/build_manifest.py",
    "tools/indexer/embed_corpus.py",
    "tools/inference/local_client.py",
    "tools/bookkeeper/dedup_detector.py",
]


class MutationTester:
    def __init__(self, root_dir: Path, test_command: Optional[List[str]] = None):
        self.root_dir = root_dir.resolve()
        self.test_command = test_command or [sys.executable, "-m", "pytest", "tests/test_library_tools.py", "tests/test_bookkeeper.py", "-q"]

    def discover_mutations(self) -> List[Tuple[Path, MutationRule, int, str, str]]:
        """Find all applicable mutations in target files."""
        discovered = []
        for rel_path in TARGET_MODULES:
            file_path = self.root_dir / rel_path
            if not file_path.exists():
                continue
            lines = file_path.read_text(encoding="utf-8").splitlines()
            for line_idx, line in enumerate(lines, 1):
                for rule in CORE_MUTATION_RULES:
                    if rule.target_pattern in line:
                        mutated_line = line.replace(rule.target_pattern, rule.replacement_pattern, 1)
                        discovered.append((file_path, rule, line_idx, line, mutated_line))
        return discovered

    def run_test_suite(self) -> Tuple[bool, str]:
        """Run the test suite. Returns (passed, output)."""
        try:
            res = subprocess.run(
                self.test_command,
                cwd=str(self.root_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                timeout=45,
            )
            return (res.returncode == 0, res.stdout)
        except subprocess.TimeoutExpired:
            return (False, "TIMEOUT")
        except Exception as e:
            return (False, f"ERROR: {e}")

    def run_mutation_analysis(self) -> List[MutationResult]:
        with tempfile.TemporaryDirectory(prefix="tare-library-mutants-") as tmp_dir:
            shadow_root = Path(tmp_dir)
            shutil.copytree(
                self.root_dir / "tools",
                shadow_root / "tools",
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
            )
            (shadow_root / "tests").mkdir()
            for rel_path in ("tests/test_library_tools.py", "tests/test_bookkeeper.py"):
                shutil.copy2(self.root_dir / rel_path, shadow_root / rel_path)
            for rel_path in ("AGENTS.md", "pytest.ini"):
                if (self.root_dir / rel_path).exists():
                    shutil.copy2(self.root_dir / rel_path, shadow_root / rel_path)
            if (self.root_dir / "ontology").exists():
                shutil.copytree(self.root_dir / "ontology", shadow_root / "catalog/ontology")
            return MutationTester(shadow_root, self.test_command)._run_mutation_analysis_in_place()

    def _run_mutation_analysis_in_place(self) -> List[MutationResult]:
        mutations = self.discover_mutations()
        print(f"\n[MUTATION ENGINE] Discovered {len(mutations)} applicable mutation targets across {len(TARGET_MODULES)} modules.")
        print("[TEST] Validating baseline test suite before mutation run...")
        base_pass, base_out = self.run_test_suite()
        if not base_pass:
            print("[ERROR] Baseline test suite FAILED! Cannot proceed with mutation testing.")
            print(base_out)
            sys.exit(1)
        print("[OK] Baseline test suite is 100% GREEN.\n")

        results = []
        for mutant_id, (target_file, rule, line_num, orig_line, mut_line) in enumerate(mutations, 1):
            rel_file = str(target_file.relative_to(self.root_dir)).replace("\\", "/")
            print(f"[{mutant_id:02d}/{len(mutations):02d}] Testing Mutant {mutant_id:02d}: {rule.name} on {rel_file}:{line_num}")
            print(f"       - Original: {orig_line.strip()[:65]}")
            print(f"       + Mutated : {mut_line.strip()[:65]}")

            # Backup original file
            backup_content = target_file.read_text(encoding="utf-8")
            try:
                # Apply mutation
                lines = backup_content.splitlines()
                lines[line_num - 1] = mut_line
                target_file.write_text("\n".join(lines), encoding="utf-8")

                # Run tests against mutant
                test_passed, test_out = self.run_test_suite()

                if not test_passed:
                    # Test failed -> mutant was successfully caught!
                    status = "KILLED"
                    print(f"       -> Result : KILLED (Test Suite Caught Mutation)\n")
                else:
                    # Test passed -> mutant survived! Test suite missed the regression!
                    status = "SURVIVED"
                    print(f"       -> Result : SURVIVED (Test Suite Missed Mutation)\n")

                results.append(MutationResult(
                    mutant_id=mutant_id,
                    target_file=rel_file,
                    rule_name=rule.name,
                    line_number=line_num,
                    original_line=orig_line.strip(),
                    mutated_line=mut_line.strip(),
                    status=status,
                    output=test_out[:200],
                ))
            finally:
                # Restore original file immediately
                target_file.write_text(backup_content, encoding="utf-8")

        return results


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    tester = MutationTester(root)
    results = tester.run_mutation_analysis()

    total = len(results)
    killed = sum(1 for r in results if r.status == "KILLED")
    survived = sum(1 for r in results if r.status == "SURVIVED")
    score = (killed / total * 100.0) if total > 0 else 0.0

    print("=" * 80)
    print(f"[MUTATION SCORE REPORT] {score:.1f}% Mutants Killed ({killed}/{total})")
    print("=" * 80)
    print(f"Total Mutants Generated: {total}")
    print(f"Mutants Killed (Tests Caught Bug): {killed}")
    print(f"Mutants Survived (Coverage Gaps):  {survived}")
    print("-" * 80)

    if survived > 0:
        print("[WARNING] SURVIVING MUTANTS REQUIRING TEST STRENGTHENING:")
        for r in results:
            if r.status == "SURVIVED":
                print(f"  - [{r.rule_name}] at {r.target_file}:{r.line_number}")
                print(f"    Original: {r.original_line}")
                print(f"    Mutated : {r.mutated_line}\n")
        return 1
    else:
        print("[SUCCESS] ALL MUTANTS KILLED! Test suite has 100% Mutation Resilience on core invariants.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
