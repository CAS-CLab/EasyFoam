"""Ensure ``fvSolution`` contains exactly the CaseSpec-declared algorithm block."""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[5]; sys.path.insert(0,str(ROOT))
from skills._shared.scripts.openfoam_text import read_text

def inspect(case:Path,algorithm:str)->dict:
    path=case/'system/fvSolution'
    if not path.is_file(): return {'passed':False,'expected':[],'found':[],'errors':['system/fvSolution missing']}
    text=read_text(path)
    found=[name for name in ('SIMPLE','PISO','PIMPLE') if re.search(r'(?m)^\s*'+name+r'\s*\{',text)]
    expected=[] if algorithm=='not_applicable' else [algorithm]
    errors=[] if found==expected else [f'expected algorithm blocks {expected}, found {found}']
    return {'passed':not errors,'expected':expected,'found':found,'errors':errors}

def main()->int:
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--case',type=Path,required=True);p.add_argument('--algorithm',choices=['SIMPLE','PISO','PIMPLE','not_applicable'],required=True);a=p.parse_args();r=inspect(a.case,a.algorithm);print(json.dumps(r,ensure_ascii=False,indent=2));return 0 if r['passed'] else 1
if __name__=='__main__': raise SystemExit(main())
