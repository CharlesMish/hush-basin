#!/usr/bin/env python3
"""Local owner-review entry; session-only mastery, retained F2/F3 evidence."""
from pathlib import Path
import datetime
import subprocess
from launch import resolve_engine, prepare_project, launch_lock, ROOT

def main():
    engine, version = resolve_engine(None)
    prepare_project(engine, force_parse=True)
    folder = ROOT / 'review_logs'
    folder.mkdir(exist_ok=True)
    stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    log = folder / ('mastery-' + stamp + '.jsonl')
    print('Hush Basin — Mastery Alpha v1 / five open jobs ·', version,
          '\nSession resets on exit. F3 diagnostic bookmarks:', log, flush=True)
    with launch_lock():
        return subprocess.call([str(engine), '--path', str(ROOT / 'game'),
            '--log-file', str(folder / ('engine-' + stamp + '.log')),
            '--', '--cargo-log', str(log)])

if __name__ == '__main__':
    raise SystemExit(main())
