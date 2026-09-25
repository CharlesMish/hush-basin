#!/usr/bin/env python3
"""One contiguous local owner candidate, using the installed exact engine."""
import datetime
import subprocess
from launch import ROOT, launch_lock, prepare_project, resolve_engine

def main():
    engine, version = resolve_engine(None)
    prepare_project(engine, force_parse=True)
    logs = ROOT / 'review_logs'
    logs.mkdir(exist_ok=True)
    stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    print('Hush Basin — Opening Chapter v0.1 ·', version,
          '\nW/S thrust/brake · A/D steer · Hold Shift Drive · Space Hop',
          '\nE/Enter interact · Enter advance · Left back · X skip · Esc close/pause',
          '\nDispatch → Reset Opening Chapter starts a fresh review.', flush=True)
    with launch_lock():
        return subprocess.call([str(engine), '--path', str(ROOT/'game'),
            '--log-file', str(logs/f'chapter-engine-{stamp}.log'),
            '--', '--cargo-log', str(logs/f'chapter-{stamp}.jsonl')])

if __name__ == '__main__':
    raise SystemExit(main())
