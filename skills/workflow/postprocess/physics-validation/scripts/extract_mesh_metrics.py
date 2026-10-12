"""Assess a raw ``checkMesh`` log without requiring an intermediate JSON file."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[5]; sys.path.insert(0,str(ROOT))
from skills._shared.scripts.openfoam_text import parse_checkmesh_log

def main()->int:
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('checkmesh_log',type=Path); a=p.parse_args(); data=parse_checkmesh_log(a.checkmesh_log)
    if data['fatal'] or (data['terminal_found'] and not data['passed']): status='failed'; basis='Blocking checkMesh evidence was detected.'
    elif data['passed'] and data['warnings']: status='limited'; basis='Topology passed but warnings require contextual quality/resolution review.'
    elif data['passed']: status='passed'; basis='checkMesh completed without detected blocking topology/geometry evidence.'
    else: status='not_assessed'; basis='No decisive checkMesh terminal result was parsed.'
    result={'status':status,'status_basis':basis,'observations':{k:v for k,v in data.items() if k not in {'source'}},'evidence_refs':[a.checkmesh_log.as_posix()]}
    print(json.dumps(result,ensure_ascii=False,indent=2)); return 0 if status in {'passed','limited'} else 1
if __name__=='__main__': raise SystemExit(main())
