#!/usr/bin/env python3
"""Check export-only preservation against an explicit native source checkpoint."""
import argparse
import configparser
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
BASELINE = "df221870b45de53e4ebb5ea8889b6cf1114054c6"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", default=BASELINE)
    args = parser.parse_args()
    def git(*argv):
        return subprocess.check_output(["git", *argv], cwd=ROOT)
    files = git("ls-tree", "-r", "--name-only", args.baseline, "game").decode().splitlines()
    changed = [p for p in files if p != "game/export_presets.cfg" and
               (not (ROOT/p).is_file() or (ROOT/p).read_bytes() != git("show", f"{args.baseline}:{p}"))]
    config = configparser.ConfigParser(interpolation=None)
    config.read(ROOT/"game/export_presets.cfg")
    checks = {
        "native_checkpoint_files_unchanged": not changed,
        "web_platform": config['preset.0']['platform'] == '"Web"',
        "single_thread": config['preset.0.options']['variant/thread_support'] == 'false',
        "no_extensions": config['preset.0.options']['variant/extensions_support'] == 'false',
        "no_service_worker": config['preset.0.options']['progressive_web_app/enabled'] == 'false',
        "runtime_data_included": all(s in config['preset.0']['include_filter'] for s in
                                      ['world/*.json', 'world/generated/*.json', 'world/generated/*.bin',
                                       'presentation/*.json', 'tests/fixtures/*.json']),
    }
    print(json.dumps({"baseline":args.baseline,"preserved_files":len(files),"checks":checks,
                      "changed":changed,"status":"PASS" if all(checks.values()) else "FAIL"},indent=2))
    return 0 if all(checks.values()) else 1


if __name__ == '__main__':
    raise SystemExit(main())
