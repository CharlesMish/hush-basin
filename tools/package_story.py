#!/usr/bin/env python3
"""Complete local story source, with byte inventory and fresh-extraction verification."""
import argparse,hashlib,json,stat,subprocess,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PREFIX='Hush-Basin-Narrative-Chapters-v0.1'
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--extract',type=Path,required=True);a=p.parse_args()
out=a.output.resolve();extract=a.extract.resolve()
if out.exists() or extract.exists() or out.is_relative_to(ROOT):p.error('Use new output paths outside source.')
names=set(subprocess.check_output(['git','ls-files','-z','--cached','--others','--exclude-standard'],cwd=ROOT).decode().split('\0'))-{''}
files={}
for name in sorted(names):
    path=ROOT/name
    if path.is_file() and not path.is_symlink() and not any(x in ['.godot','.git','__pycache__','review_logs'] for x in path.relative_to(ROOT).parts):files[name]=path
sha=lambda data:hashlib.sha256(data).hexdigest()
manifest={'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
          'working_tree_changes':subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).splitlines(),
          'files':{name:sha(path.read_bytes()) for name,path in files.items()}}
out.parent.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for name,path in files.items():
        info=zipfile.ZipInfo(PREFIX+'/'+name,date_time=(2026,10,1,0,0,0));info.create_system=3
        info.external_attr=(stat.S_IFREG|stat.S_IMODE(path.stat().st_mode))<<16;info.compress_type=zipfile.ZIP_DEFLATED
        z.writestr(info,path.read_bytes(),compresslevel=9)
    z.writestr(PREFIX+'/SOURCE_MANIFEST.json',json.dumps(manifest,indent=2)+'\n')
with zipfile.ZipFile(out) as z:
    assert z.testzip() is None
    for info in z.infolist():
        target=extract/info.filename;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(z.read(info))
        target.chmod((info.external_attr>>16)&0o777 or 0o644)
for name,digest in manifest['files'].items():assert sha((extract/PREFIX/name).read_bytes())==digest
result={'status':'PASS','files':len(files),'commit':manifest['source_commit'],'zip':str(out),'bytes':out.stat().st_size,'sha256':sha(out.read_bytes()),'extracted_source':str(extract/PREFIX),'crc_and_source_bytes':'PASS'}
out.with_suffix('.package.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
