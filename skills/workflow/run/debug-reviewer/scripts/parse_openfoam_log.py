"""Extract the first deterministic OpenFOAM failure and a conservative category."""
from __future__ import annotations
import argparse, hashlib, json, re
from pathlib import Path
PATTERNS=[
 ('environment',re.compile(r'command not found|no such file or directory|permission denied|MPI|mpirun|cannot open shared object',re.I)),
 ('dictionary',re.compile(r'FOAM FATAL IO ERROR|keyword .* undefined|cannot find file|wrong token|ill defined primitiveEntry',re.I)),
 ('mesh',re.compile(r'negative volume|mesh.*topology|cannot find patch|cannot find cellZone|cannot find faceZone|AMI',re.I)),
 ('field_or_boundary',re.compile(r'cannot find field|boundary condition|patchField|dimensions? .* mismatch|size .* does not match',re.I)),
 ('model',re.compile(r'unknown .* model|select .* model|thermophysical|momentumTransport|phaseProperties|species',re.I)),
 ('numerical',re.compile(r'floating point|not finite|nan|diverg|bounding|Courant Number',re.I)),
]
ERROR_RE=re.compile(r'FOAM FATAL|fatal error|\bERROR\b|segmentation fault|floating point exception|undefined',re.I)
def parse(path:Path)->dict:
    lines=path.read_text(encoding='utf-8',errors='replace').splitlines(); idx=next((i for i,l in enumerate(lines) if ERROR_RE.search(l)),None)
    if idx is None: return {'first_deterministic_error':None,'category':'unclassified','context':[],'failure_signature':None,'line_count':len(lines)}
    context=lines[max(0,idx-2):min(len(lines),idx+6)]; joined='\n'.join(context); category=next((name for name,pat in PATTERNS if pat.search(joined)),'unclassified')
    error=lines[idx].strip(); signature=hashlib.sha256(re.sub(r'\d+','<n>',error).encode()).hexdigest()[:16]
    return {'first_deterministic_error':error,'category':category,'context':context,'failure_signature':signature,'line_count':len(lines)}
def main()->int:
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('log',type=Path);a=p.parse_args();r=parse(a.log);print(json.dumps(r,ensure_ascii=False,indent=2));return 0 if r['first_deterministic_error'] else 1
if __name__=='__main__': raise SystemExit(main())
