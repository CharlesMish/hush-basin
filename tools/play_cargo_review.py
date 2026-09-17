#!/usr/bin/env python3
"""Launch the one-job cargo review entry and keep its local receipts."""
import datetime
from pathlib import Path
import subprocess
from launch import resolve_engine, prepare_project, launch_lock, ROOT

def main():
    engine, version = resolve_engine(None)
    prepare_project(engine, force_parse=True)
    folder = ROOT/'review_logs'
    folder.mkdir(exist_ok=True)
    stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    log = folder/('cargo-'+stamp+'.jsonl')
    print('Cargo feel v1.1 —', version, '\nReceipts:', log, flush=True)
    with launch_lock():
        return subprocess.call([str(engine), '--path', str(ROOT/'game'),
            '--log-file', str(folder/('engine-'+stamp+'.log')),
            'res://review/cargo_v1_1/cargo_review.tscn', '--', '--cargo-log', str(log)])

if __name__=='__main__': raise SystemExit(main())
