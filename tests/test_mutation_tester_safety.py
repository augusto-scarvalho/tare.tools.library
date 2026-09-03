from __future__ import annotations

import importlib.util
import subprocess
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("library_mutation_tester", ROOT / "tests" / "mutation_tester.py")
assert SPEC is not None and SPEC.loader is not None
mutation_tester = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mutation_tester)


def test_runner_distinguishes_failure_timeout_and_error(tmp_path: Path) -> None:
    tester = mutation_tester.MutationTester(tmp_path)
    with patch.object(mutation_tester.subprocess, "run", return_value=SimpleNamespace(returncode=1, stdout="failed")):
        assert tester.run_test_suite() == ("FAIL", "failed")
    with patch.object(mutation_tester.subprocess, "run", return_value=SimpleNamespace(returncode=2, stdout="usage")):
        assert tester.run_test_suite() == ("ERROR", "usage")
    with patch.object(mutation_tester.subprocess, "run", side_effect=subprocess.TimeoutExpired(["pytest"], 45)):
        assert tester.run_test_suite() == ("TIMEOUT", "TIMEOUT")


def test_shadow_copy_preserves_ontology_registry_and_reports_source_integrity(capsys) -> None:
    tester = mutation_tester.MutationTester(ROOT)

    def observe_shadow(shadow_tester: object) -> list[bool]:
        shadow_root = shadow_tester.root_dir
        return [(shadow_root / "catalog" / "FEDERATED_ONTOLOGIES.json").is_file()]

    with patch.object(mutation_tester.MutationTester, "_run_mutation_analysis_in_place", autospec=True, side_effect=observe_shadow):
        assert tester.run_mutation_analysis() == [True]
    assert "ALL_SOURCES_UNCHANGED=True" in capsys.readouterr().out
