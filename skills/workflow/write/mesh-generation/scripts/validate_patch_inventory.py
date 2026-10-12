"""Compare CaseSpec patch/zone contracts with an actual ``constant/polyMesh``."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[5]; sys.path.insert(0,str(ROOT))
from skills._shared.scripts.artifact_io import read_json
from skills._shared.scripts.openfoam_text import parse_boundary_file, parse_zone_names

def main()->int:
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--spec',type=Path,required=True); p.add_argument('--case-dir',type=Path,required=True); a=p.parse_args()
    spec=read_json(a.spec); mesh=spec['mesh']; poly=a.case_dir/'constant/polyMesh'
    actual_patches={x['name']:x.get('type') for x in parse_boundary_file(poly/'boundary')}
    actual_cell=set(parse_zone_names(poly/'cellZones')); actual_face=set(parse_zone_names(poly/'faceZones'))
    expected={x['name']:x['mesh_type'] for x in mesh['required_patches'] if x.get('required',False)}
    missing=sorted(set(expected)-set(actual_patches))
    mismatches=sorted(n for n,t in expected.items() if n in actual_patches and actual_patches[n] and t!=actual_patches[n])
    missing_c=sorted(set(mesh['required_cell_zones'])-actual_cell); missing_f=sorted(set(mesh['required_face_zones'])-actual_face)
    errors=[]
    if not (poly/'boundary').is_file(): errors.append('constant/polyMesh/boundary missing')
    if missing: errors.append('missing required patches: '+', '.join(missing))
    if mismatches: errors.append('patch type mismatches: '+', '.join(mismatches))
    if missing_c: errors.append('missing required cellZones: '+', '.join(missing_c))
    if missing_f: errors.append('missing required faceZones: '+', '.join(missing_f))
    result={'passed':not errors,'actual_patches':actual_patches,'actual_cell_zones':sorted(actual_cell),'actual_face_zones':sorted(actual_face),'errors':errors}
    print(json.dumps(result,ensure_ascii=False,indent=2)); return 0 if not errors else 1
if __name__=='__main__': raise SystemExit(main())
