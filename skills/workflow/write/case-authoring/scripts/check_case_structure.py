"""Check the CaseSpec-declared formal case file structure."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[5]; sys.path.insert(0,str(ROOT))
from skills._shared.scripts.artifact_io import read_json

def required_files(spec:dict)->list[str]:
    required=['system/controlDict','system/fvSchemes','system/fvSolution','constant/polyMesh/boundary']
    required.extend(f"0/{f['name']}" for f in spec.get('fields',[]) if f.get('required',False))
    method=spec.get('mesh',{}).get('method')
    if method in {'blockMesh','combined'}: required.append('system/blockMeshDict')
    if method in {'snappyHexMesh','combined'}: required.append('system/snappyHexMeshDict')
    return sorted(set(required))

def inspect(case:Path,spec:dict)->dict:
    required=required_files(spec); missing=[x for x in required if not (case/x).is_file()]
    return {'passed':not missing,'required':required,'missing':missing}

def main()->int:
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('case',type=Path);p.add_argument('--spec',type=Path,required=True);a=p.parse_args();r=inspect(a.case,read_json(a.spec));print(json.dumps(r,ensure_ascii=False,indent=2));return 0 if r['passed'] else 1
if __name__=='__main__': raise SystemExit(main())
