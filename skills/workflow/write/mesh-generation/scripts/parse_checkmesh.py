"""Parse a raw ``checkMesh`` log into one credibility-oriented stdout result."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[5]; sys.path.insert(0,str(ROOT))
from skills._shared.scripts.openfoam_text import parse_checkmesh_log

def main()->int:
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('log',type=Path); a=p.parse_args()
    data=parse_checkmesh_log(a.log)
    if data['fatal'] or data['passed'] is False and data['terminal_found']:
        status='failed'; basis='checkMesh reported a blocking topology/geometry result.'
    elif data['passed'] and data['warnings']:
        status='limited'; basis='checkMesh completed, but warnings require contextual quality review.'
    elif data['passed']:
        status='passed'; basis='checkMesh completed without a detected blocking result.'
    else:
        status='not_assessed'; basis='No decisive checkMesh terminal result was parsed.'
    result={'status':status,'status_basis':basis,**data}
    print(json.dumps(result,ensure_ascii=False,indent=2)); return 0 if status in {'passed','limited'} else 1
if __name__=='__main__': raise SystemExit(main())
