"""Extract concise execution evidence from a schema-valid run record."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[5]; sys.path.insert(0,str(ROOT))
from skills._shared.scripts.artifact_io import read_json
from skills._shared.scripts.schema_validate import validate

def main()->int:
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('run_record',type=Path); a=p.parse_args()
    errors=validate(a.run_record,ROOT/'schemas/run_record.schema.json')
    if errors: print(json.dumps({'status':'failed','errors':errors},ensure_ascii=False,indent=2)); return 1
    x=read_json(a.run_record); elapsed=sum(float(c.get('elapsed_seconds',0)) for c in x.get('commands',[]))
    result={'status':{'succeeded':'passed','failed':'failed','blocked':'blocked'}[x['terminal_status']],'attempt_id':x['attempt_id'],'mode':x['mode'],'case_sha256':x['case_sha256'],'command_count':len(x['commands']),'elapsed_seconds':elapsed,'completed_time_or_iteration':x.get('completed_time_or_iteration'),'first_deterministic_error':x.get('first_deterministic_error'),'status_basis':'Schema-valid terminal run record.','evidence_refs':[a.run_record.as_posix()]}
    print(json.dumps(result,ensure_ascii=False,indent=2)); return 0 if x['terminal_status']=='succeeded' else 1
if __name__=='__main__': raise SystemExit(main())
