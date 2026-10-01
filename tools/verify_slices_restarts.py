#!/usr/bin/env python3
"""Separate-process successor resume checks, including both partial thread states."""
import argparse,json,subprocess,sys
from pathlib import Path
from launch import ROOT
p=argparse.ArgumentParser();p.add_argument('--evidence',type=Path,required=True);p.add_argument('--name',default='restarts-final');a=p.parse_args()
base=a.evidence.resolve();out=base/a.name;out.mkdir(exist_ok=False)
sources=[('ch2-native-final','ch2_delivered'),('ch2-native-final','ch2_released'),('ch2-native-final','ch2_old_returned'),
         ('ch3-ren_first','ren_only'),('ch3-sleeve_first','sleeve_only')]
sources += [('ch3-native-final',s) for s in ['held','pads_answer','ready','both','aboard_tray_one','aboard_quarry_sleeve','aboard_tray_two','aboard_thread_box','aboard_kneeling_pads','aboard_relined_sleeve','aboard_tagged_mending']]
rows=[]
for folder,suffix in sources:
    command=[sys.executable,str(ROOT/'tools/verify_slices.py'),'--phase','resume_'+suffix,'--resume',str(base/folder/('save.json.'+suffix)),'--output',str(out/suffix)]
    r=subprocess.run(command,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
    data=json.loads((out/suffix/'command.json').read_text()) if (out/suffix/'command.json').exists() else {'status':'NO_RESULT','output':r.stdout[-1200:]}
    rows.append(data);print(suffix,data['status'],data.get('checks',0),flush=True)
    (out/'suite.json').write_text(json.dumps({'status':'PASS' if all(x['status']=='PASS' for x in rows) else 'FAIL','records':rows},indent=2)+'\n')
raise SystemExit(0 if all(x['status']=='PASS' for x in rows) else 1)
