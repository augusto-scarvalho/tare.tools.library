"""Tests for Emergency Halt Protocol (RFC-005)."""
import json
import tempfile
from pathlib import Path
import pytest

from tools.policy.halt_protocol import EmergencyHaltReceipt, emit_halt


@pytest.mark.verifies("RFC-005-REQ-HALT-001")
def test_emergency_halt_emission_and_loading():
    with tempfile.TemporaryDirectory() as tmpdir:
        out_dir = Path(tmpdir)
        receipt_path = emit_halt(
            case_id="RFC-005-TEST",
            reason="Physical VRAM allocation failure on RTX 3090",
            violation_class="PHYSICAL_IMPOSSIBILITY",
            falsifier_evidence="CUDA out of memory",
            recommendation="Offload MoE layers to CPU",
            output_dir=out_dir,
        )

        assert receipt_path.exists()
        assert receipt_path.name == "HALT_RECEIPT.json"

        loaded = EmergencyHaltReceipt.load_from_file(receipt_path)
        assert loaded.case_id == "RFC-005-TEST"
        assert loaded.violation_class == "PHYSICAL_IMPOSSIBILITY"
        assert "CUDA out of memory" in loaded.falsifier_evidence
