import subprocess,sys
from pathlib import Path

def test_information_survival_ingestion_validator():
    root=Path(__file__).resolve().parents[1]
    p=subprocess.run([sys.executable,str(root/'tools/validate_information_survival_ingestion.py')],cwd=root,text=True,capture_output=True)
    assert p.returncode==0, p.stdout+'\n'+p.stderr
