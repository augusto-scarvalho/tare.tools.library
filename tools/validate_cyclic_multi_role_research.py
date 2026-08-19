from __future__ import annotations
import hashlib, json, sys
from pathlib import Path

def validate(root: Path) -> list[str]:
    errs=[]
    run=root/'experiments/assurance/cyclic-multi-role-research-protocol/2026-08-11-run-001'
    m=json.loads((run/'RUN_MANIFEST.json').read_text(encoding='utf-8'))
    if m.get('executor',{}).get('epistemic_independence')!='NOT_INDEPENDENT': errs.append('same-model run must be NOT_INDEPENDENT')
    if m.get('strict_proof_eligible') is not False: errs.append('same-model screening run cannot be strict-proof eligible')
    required=[f'{i:02d}-' for i in range(1,12)]
    files=[x['file'] for x in m.get('role_artifacts',[])]
    for prefix in required:
        if not any(f.startswith(prefix) for f in files): errs.append('missing role '+prefix)
    for x in m.get('role_artifacts',[]):
        p=run/x['file']
        if not p.exists(): errs.append('missing '+str(p)); continue
        b=p.read_bytes()
        b_norm=b.replace(b'\r\n', b'\n')
        h=hashlib.sha256(b).hexdigest()
        h_norm=hashlib.sha256(b_norm).hexdigest()
        if h!=x['sha256'] and h_norm!=x['sha256']: errs.append('hash mismatch '+x['file'])
        if len(b)!=x['bytes'] and len(b_norm)!=x['bytes']: errs.append('size mismatch '+x['file'])
    adv=(run/'09-adversarial-review-round1.md').read_text(encoding='utf-8')
    if adv.count('### AR-') < 5: errs.append('adversarial review too weak')
    final=(run/'11-final-audit.md').read_text(encoding='utf-8')
    for token in ['NOT_INDEPENDENT','INELIGIBLE','Exactly one next research recommendation']:
        if token not in final: errs.append('final audit missing '+token)
    return errs

if __name__=='__main__':
    root=Path(__file__).resolve().parents[1]
    e=validate(root)
    if e:
        print('CMRP VALIDATION FAIL')
        [print('-',x) for x in e]
        raise SystemExit(1)
    print('CMRP VALIDATION PASS')
