#!/usr/bin/env python3
"""One native launcher for the contiguous authored chapters."""
import datetime, subprocess
from launch import ROOT, launch_lock, prepare_project, resolve_engine
def main():
    engine,version=resolve_engine(None);prepare_project(engine,force_parse=True)
    logs=ROOT/'review_logs';logs.mkdir(exist_ok=True)
    stamp=datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    print('Hush Basin ·',version,'\nW/S thrust/brake · A/D steer · Hold Shift Drive · Space Hop\nE/Enter interact · Enter advance · Left back · X skip · Esc close/pause\nDispatch → Reset Story starts again. Earlier review saves are preserved.',flush=True)
    with launch_lock():
        return subprocess.call([str(engine),'--path',str(ROOT/'game'),'--log-file',str(logs/f'story-{stamp}.log'),'res://review/narrative_slices/review.tscn','--','--cargo-log',str(logs/f'story-{stamp}.jsonl')])
if __name__=='__main__':raise SystemExit(main())
