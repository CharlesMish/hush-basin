#!/usr/bin/env python3
"""Compare authored blockquoted script against implemented string literals."""
import json, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
source=(ROOT/'game/scripts/courier/slices_text.gd').read_text()
strings=[json.loads(x) for x in re.findall(r'"(?:[^"\\]|\\.)*"',source)]
omitted={"That's a fresh one. It'll be in good company.":'No distinguishable fresh-chip evidence.',
         "Chisels. Good. On the bench. No—leave them there. I'll take them.":'Existing survey-pack host retains its own receipt, as authorized.'}
rows=[]
for file in ['QUARRY_SLICE_V1_1.md','CHAPTER_3_SLICE_V1_1.md']:
    for line in (ROOT/'docs'/file).read_text().splitlines():
        if line.startswith('> '):
            text=line[2:].strip().strip('"')
            rows.append({'document':file,'text':text,'exact':text in strings,'authorized_omission':omitted.get(text)})
result={'status':'PASS' if all(r['exact'] or r['authorized_omission'] for r in rows) else 'FAIL',
        'authored_passages':len(rows),'exact':sum(r['exact'] for r in rows),'passages':rows}
print(json.dumps(result,indent=2,ensure_ascii=False))
raise SystemExit(0 if result['status']=='PASS' else 1)
