"""Print the actual imported OpenFOAM patch and zone inventory to stdout."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[5]; sys.path.insert(0,str(ROOT))
from skills._shared.scripts.openfoam_text import parse_boundary_file, parse_zone_names

def main()->int:
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--case-dir',type=Path,required=True); a=p.parse_args(); poly=a.case_dir/'constant/polyMesh'
    result={'passed':(poly/'boundary').is_file(),'boundary_file':'constant/polyMesh/boundary','patches':parse_boundary_file(poly/'boundary'),'cell_zones':parse_zone_names(poly/'cellZones'),'face_zones':parse_zone_names(poly/'faceZones')}
    if not result['passed']: result['errors']=['boundary file not found']
    print(json.dumps(result,ensure_ascii=False,indent=2)); return 0 if result['passed'] else 1
if __name__=='__main__': raise SystemExit(main())
