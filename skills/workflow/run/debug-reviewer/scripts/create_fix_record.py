"""Create a compact reviewed repair description; persist only with explicit ``--out``."""
from __future__ import annotations
import argparse, json
from pathlib import Path
from parse_openfoam_log import parse

def main()->int:
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--log',type=Path,required=True); p.add_argument('--out',type=Path)
    p.add_argument('--root-cause',required=True); p.add_argument('--repair-scope',required=True); p.add_argument('--earliest-stage',choices=['plan','write','run','postprocess'],required=True)
    p.add_argument('--verification-command'); p.add_argument('--verification-return-code',type=int); p.add_argument('--before-hash'); p.add_argument('--after-hash'); p.add_argument('--diff-ref'); p.add_argument('--limitation',action='append',default=[])
    a=p.parse_args(); failure=parse(a.log); verified=a.verification_return_code==0 and bool(a.verification_command)
    record={'failure_signature':failure['failure_signature'],'first_deterministic_error':failure['first_deterministic_error'],'failure_category':failure['category'],'root_cause':a.root_cause,'repair_scope':a.repair_scope,'earliest_affected_stage':a.earliest_stage,'verification_command':a.verification_command,'verification_return_code':a.verification_return_code,'verified':verified,'before_hash':a.before_hash,'after_hash':a.after_hash,'diff_ref':a.diff_ref,'limitations':a.limitation}
    if a.out: a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(record,ensure_ascii=False,indent=2)); return 0 if verified else 1
if __name__=='__main__': raise SystemExit(main())
