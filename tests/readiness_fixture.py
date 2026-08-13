from __future__ import annotations

import json
from pathlib import Path
import shutil


def make_readiness_fixture(root: Path) -> tuple[Path,Path]:
    (root/'site').mkdir(parents=True)
    profile={
        'profile_version':'1.1','source_ref':'incumbent-sha',
        'deploy_owner':'legacy/pages-deploy.yml@incumbent',
        'base_path':'/tare.tools.research/','critical_paths':['index.html'],
        'expected_materialized_file_count':1,
        'expected_materialized_inventory_digest':'2c31487ebc31417d1d29fa7131209e9e96ef696192def1d75539efedabe82a45',
    }
    (root/'site'/'INCUMBENT_PROFILE.json').write_text(json.dumps(profile),encoding='utf-8')
    workflows=root/'.github'/'workflows'; workflows.mkdir(parents=True)
    (workflows/'pages.yml').write_text('name: pages-shadow\npermissions:\n  contents: read\n',encoding='utf-8')
    incumbent=root/'incumbent'; incumbent.mkdir()
    (incumbent/'index.html').write_text('stable',encoding='utf-8')
    output=root/'output'; shutil.copytree(incumbent,output)
    (output/'publications').mkdir()
    (output/'publications'/'index.html').write_text('<!doctype html><html><body></body></html>',encoding='utf-8')
    meta=output/'publication-meta'; meta.mkdir()
    parity={
        'record_version':'1.0','status':'PASS','incumbent_source_ref':'incumbent-sha',
        'incumbent_file_count':1,'unchanged_incumbent_files':1,
        'missing_incumbent_paths':[],'modified_incumbent_paths':[],
        'critical_paths':['index.html'],'critical_missing':[],
        'additive_paths':['publications/index.html'],
    }
    (meta/'PARITY_REPORT.json').write_text(json.dumps(parity),encoding='utf-8')
    return incumbent,output
