#!/usr/bin/env python3
"""Download the staged export over HTTP; record byte identities and real headers."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('origin', help='Origin only, e.g. https://DEPLOYMENT.pages.dev')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads((ROOT / 'hosting/cloudflare/build-manifest.json').read_text())
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    base = args.origin.rstrip('/') + '/builds/' + manifest['build_id'] + '/'
    results = []
    for pass_name in ('first', 'second', 'range'):
        for entry in manifest['files']:
            large = entry['name'] in ('index.wasm', 'index.pck')
            if pass_name == 'range' and not large:
                continue
            request_headers = {
                'Accept-Encoding': 'identity',
                'User-Agent': 'Hush-Basin-Hosting-Proof/1.0',
            }
            if pass_name == 'range':
                request_headers['Range'] = 'bytes=0-15'
            url = base + entry['name']
            start = time.monotonic()
            stamp = datetime.now(timezone.utc).isoformat()
            request = urllib.request.Request(url, headers=request_headers)
            digest = hashlib.sha256()
            count = 0
            with urllib.request.urlopen(request, timeout=180) as response:
                headers = dict(response.headers.items())
                status = response.status
                final_url = response.url
                with (output / f"{pass_name}-{entry['name']}").open('wb') as downloaded:
                    for chunk in iter(lambda: response.read(1024 * 1024), b''):
                        count += len(chunk)
                        digest.update(chunk)
                        downloaded.write(chunk)
            result = {
                'pass': pass_name, 'url': url, 'final_url': final_url, 'utc': stamp,
                'request_headers': request_headers, 'status': status,
                'headers': headers, 'bytes': count, 'sha256': digest.hexdigest(),
                'seconds': round(time.monotonic() - start, 3),
                'matches_export': status == 200 and count == entry['bytes'] and digest.hexdigest() == entry['sha256'],
            }
            results.append(result)
            (output / 'responses.json').write_text(json.dumps(results, indent=2) + '\n')
            print(json.dumps({k:result[k] for k in ('pass','url','status','bytes','sha256','seconds','matches_export')}), flush=True)
    assert all(r['matches_export'] for r in results), 'At least one HTTP body did not match the full export'
    print('PASS: all 20 HTTP responses match the recorded export, including deliberately ignored Range requests')


if __name__ == '__main__':
    main()
