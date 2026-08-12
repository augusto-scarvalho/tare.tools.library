import subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def test_new_research_ingestion_validator():
    p=subprocess.run([sys.executable,str(ROOT/'tools/validate_new_research_ingestion.py')],cwd=ROOT,capture_output=True,text=True)
    assert p.returncode==0, p.stdout+'\n'+p.stderr
