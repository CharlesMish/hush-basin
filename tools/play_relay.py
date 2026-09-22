#!/usr/bin/env python3
"""One local Relay experiment; no export, network or deployment."""
import argparse
import datetime
import subprocess
from launch import resolve_engine, prepare_project, launch_lock, ROOT

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--control', action='store_true', help='Review control: same legs/pay/Relay work, no named project or visual change')
    args = parser.parse_args()
    engine, version = resolve_engine(None)
    prepare_project(engine, force_parse=True)
    folder = ROOT / 'review_logs'
    folder.mkdir(exist_ok=True)
    stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    log = folder / ('relay-' + stamp + '.jsonl')
    print("Hush Basin — Ren's Receiver ·", version,
          '\nProject persists locally. Dispatch → Reset Project Experiment replays it.',
          '\nCredits, liner and mastery are session only. F3 bookmark:', log, flush=True)
    with launch_lock():
        return subprocess.call([str(engine), '--path', str(ROOT / 'game'),
            '--log-file', str(folder / ('engine-' + stamp + '.log')),
            '--', '--cargo-log', str(log)] + (['--relay-control'] if args.control else []))

if __name__ == '__main__':
    raise SystemExit(main())
