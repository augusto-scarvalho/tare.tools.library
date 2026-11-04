import importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('cmrp',ROOT/'tools/validate_cyclic_multi_role_research.py')
mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)

def test_cmrp_run_001():
    assert mod.validate(ROOT)==[]
