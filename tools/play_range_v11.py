#!/usr/bin/env python3
"""Local Mechanics Range V1.1, with retained F2/F3 cargo receipts."""
from pathlib import Path
import datetime
import subprocess
from launch import resolve_engine, prepare_project, launch_lock, ROOT

def main():
    engine, version = resolve_engine(None)
    prepare_project(engine, force_parse=True)
    folder = ROOT/'review_logs'
    folder.mkdir(exist_ok=True)
    stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    log = folder/('alpha-'+stamp+'.jsonl')
    print('Hush Basin — Mechanics Range V1.1 / five jobs ·', version, '\nF3 receipts:', log, flush=True)
    with launch_lock():
        return subprocess.call([str(engine), '--path', str(ROOT/'game'),
            '--log-file', str(folder/('engine-'+stamp+'.log')), '--', '--cargo-log', str(log)])

if __name__ == '__main__': raise SystemExit(main())
