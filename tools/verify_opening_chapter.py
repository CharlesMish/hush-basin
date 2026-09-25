#!/usr/bin/env python3
"""Bounded regression and process-restart runner; isolated evidence saves only."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
from launch import ROOT, resolve_engine

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--native', action='store_true')
    args = p.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    engine, version = resolve_engine(None)
    records = []
    def run(name, script, extra=(), native=False):
        c = [str(engine)] + ([] if native else ['--headless', '--fixed-fps', '60'])
        c += ['--path', str(ROOT/'game'), '--log-file', str(out/f'{name}.engine.log'),
              '--script', 'res://tests/'+script, '--', '--result', str(out/f'{name}.json')]
        c += list(extra)
        try:
            result = subprocess.run(c, stdout=(out/f'{name}.stdout.log').open('w'), stderr=subprocess.STDOUT, timeout=720, cwd=ROOT)
            code = result.returncode
        except subprocess.TimeoutExpired:
            code = 'TIMEOUT'
        data = json.loads((out/f'{name}.json').read_text()) if (out/f'{name}.json').exists() else {}
        checks = data.get('checks', {})
        status = data.get('status', 'see log')
        row = {'name': name, 'command': c, 'exit': code, 'status': status, 'checks': len(checks),
               'failed_checks': [k for k,v in checks.items() if not v] if isinstance(checks, dict) else []}
        records.append(row)
        (out/'commands.json').write_text(json.dumps(records, indent=2)+'\n')
        print(name, code, status, len(checks), flush=True)
    def saved(name):
        return ['--save', str(out/f'{name}.save.json'), '--cargo-log', str(out/f'{name}.cargo.jsonl')]
    run('movement', 'world_polish_c1.gd', ['--output', str(out/'c1.jsonl')])
    for name, script, extra in [
        ('cargo','alpha_cargo_matrix.gd',[]),('cargo_protected','alpha_cargo_matrix.gd',['--protected']),
        ('vehicle','quarto_vehicle_v1.gd',[]),('run','run_v0_probe.gd',[]),('paused_retry','paused_retry_addendum.gd',[]),
        ('receiver','receiver_comprehension_native.gd',saved('receiver')),
        ('narrative_store','narrative_store_probe.gd',saved('narrative_store')),
        ('narrative_flow','narrative_native.gd',saved('narrative_flow')),
        ('narrative_edges','narrative_native.gd',saved('narrative_edges')+['--phase','edges']),
        ('chapter_store','chapter_store_probe.gd',saved('chapter_store')),
        ('chapter_guards','chapter_native.gd',saved('chapter_guards')+['--phase','guards']),
        ('chapter_edges','chapter_native.gd',saved('chapter_edges')+['--phase','edges']),
        ('chapter_flow','chapter_native.gd',saved('chapter_flow'))]:
        run(name, script, extra)
    restart_source = out/'chapter_guards.save.json'
    for snapshot in sorted(out.glob('chapter_guards.save.json.*')):
        suffix = snapshot.name.removeprefix('chapter_guards.save.json.')
        if not suffix[0].isdigit():
            continue
        name = 'restart_'+suffix
        shutil.copyfile(snapshot,out/f'{name}.save.json')
        run(name,'chapter_native.gd',saved(name)+['--phase','inspect_'+suffix])
    if args.native:
        run('chapter_native','chapter_native.gd',saved('chapter_native')+['--captures',str(out/'captures')],True)
        run('chapter_native_edges','chapter_native.gd',saved('chapter_native_edges')+['--phase','edges'],True)
    trace = out/'c1.jsonl'
    digest = hashlib.sha256(trace.read_bytes()).hexdigest() if trace.exists() else ''
    parity = digest == '29f1049f8e16ec65d288407c35e6ccae46e87c711bb6b54b134e6158c68b9443'
    passed = parity and all(r['exit']==0 and r['status']!='FAIL' and not r['failed_checks'] for r in records)
    report={'status':'PASS' if passed else 'FAIL','engine':version,'movement_exact':parity,'trace_sha256':digest,'records':records}
    (out/'suite.json').write_text(json.dumps(report,indent=2)+'\n')
    return 0 if passed else 1

if __name__ == '__main__':
    raise SystemExit(main())
