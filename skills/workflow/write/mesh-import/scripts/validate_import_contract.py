"""Validate external-mesh provenance and, when available, the actual imported inventory."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parents[5]; sys.path.insert(0,str(ROOT))
from skills._shared.scripts.artifact_io import read_json
from skills._shared.scripts.openfoam_text import parse_boundary_file, parse_zone_names
SUPPORTED_FORMATS={'foam','fluent','gmsh','ideas','nastran','starccm','cgns'}

def relative(value:str)->bool:
    p=Path(value); return bool(value) and not p.is_absolute() and '..' not in p.parts and not (len(value)>=2 and value[1]==':')

def main()->int:
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--spec',type=Path,required=True); p.add_argument('--source',required=True); p.add_argument('--format',required=True); p.add_argument('--case-dir',type=Path); a=p.parse_args()
    spec=read_json(a.spec); mesh=spec['mesh']; errors=[]; warnings=[]
    if mesh['route'] not in {'import','reuse'}: errors.append('mesh-import requires route import or reuse')
    if mesh['method'] not in {'external','existing_polyMesh','combined'}: errors.append(f"unsupported import method: {mesh['method']}")
    if not relative(a.source): errors.append('source must be a portable relative/stable reference')
    if a.format.lower() not in SUPPORTED_FORMATS: errors.append(f'unsupported or unresolved format: {a.format}')
    actual_patches={}; cell=[]; face=[]
    if a.case_dir:
        poly=a.case_dir/'constant/polyMesh'; actual_patches={x['name']:x.get('type') for x in parse_boundary_file(poly/'boundary')}; cell=parse_zone_names(poly/'cellZones'); face=parse_zone_names(poly/'faceZones')
        expected={x['name']:x['mesh_type'] for x in mesh['required_patches'] if x.get('required',False)}
        missing=sorted(set(expected)-set(actual_patches)); mismatch=sorted(n for n,t in expected.items() if n in actual_patches and actual_patches[n] and t!=actual_patches[n])
        missing_c=sorted(set(mesh['required_cell_zones'])-set(cell)); missing_f=sorted(set(mesh['required_face_zones'])-set(face))
        if missing: errors.append('missing required patches: '+', '.join(missing))
        if mismatch: errors.append('patch type mismatches: '+', '.join(mismatch))
        if missing_c: errors.append('missing required cellZones: '+', '.join(missing_c))
        if missing_f: errors.append('missing required faceZones: '+', '.join(missing_f))
    else: warnings.append('actual imported inventory not yet supplied; conversion and checkMesh evidence remain required')
    result={'passed':not errors,'source':a.source,'format':a.format.lower(),'route':mesh['route'],'method':mesh['method'],'actual_patches':actual_patches,'actual_cell_zones':cell,'actual_face_zones':face,'warnings':warnings,'errors':errors}
    print(json.dumps(result,ensure_ascii=False,indent=2)); return 0 if not errors else 1
if __name__=='__main__': raise SystemExit(main())
