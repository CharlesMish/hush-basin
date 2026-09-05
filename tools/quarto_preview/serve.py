#!/usr/bin/env python3
"""Loopback-only geometry review using an already installed Babylon core.

No package installation, native engine substitution, or game-source mutation.
"""
from __future__ import annotations

import argparse
import json
import mimetypes
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
CANONICAL = ROOT / "game/presentation/quarto_native_v1.json"


def camera_settings() -> dict:
    text = (ROOT / "game/scripts/craft_tuning.gd").read_text()
    overrides = (ROOT / "game/resources/default_tuning.tres").read_text()
    keys = ("camera_distance", "camera_height", "camera_look_ahead", "camera_look_height",
            "spread_camera_fov", "drive_fov_increase", "fold_duration", "deploy_duration")
    result = {}
    for key in keys:
        match = re.search(rf"\b{key}(?::\s*float)?\s*=\s*([\d.]+)", overrides)
        if not match:
            match = re.search(rf"\b{key}(?::\s*float)?\s*=\s*([\d.]+)", text)
        if match:
            result[key] = float(match.group(1))
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--babylon-root", type=Path, required=True,
                        help="Existing @babylonjs/core directory; no install occurs")
    parser.add_argument("--port", type=int, default=5192)
    args = parser.parse_args()
    engine = args.babylon_root.resolve()
    if not (engine / "Engines/engine.js").is_file():
        parser.error("--babylon-root must contain Engines/engine.js")
    if not CANONICAL.is_file():
        parser.error(f"Missing canonical vehicle data: {CANONICAL}")

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            path = unquote(urlsplit(self.path).path)
            if path == "/camera.json":
                self.send_bytes(json.dumps(camera_settings()).encode(), "application/json")
                return
            if path == "/vehicle.json":
                self.send_bytes(CANONICAL.read_bytes(), "application/json")
                return
            if path.startswith("/engine/"):
                base, relative = engine, path.removeprefix("/engine/")
            else:
                base, relative = HERE, path.lstrip("/") or "index.html"
            candidate = (base / relative).resolve()
            if not candidate.is_relative_to(base) or not candidate.is_file():
                self.send_error(404)
                return
            mime = mimetypes.guess_type(candidate.name)[0] or "application/octet-stream"
            if candidate.suffix in (".js", ".mjs"):
                mime = "text/javascript"
            self.send_bytes(candidate.read_bytes(), mime)

        def send_bytes(self, data: bytes, mime: str) -> None:
            self.send_response(200)
            self.send_header("Content-Type", mime)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(data)

        def log_message(self, format: str, *values: object) -> None:
            if values and str(values[1]) != "200":
                super().log_message(format, *values)

    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"Quarto geometry preview: http://127.0.0.1:{server.server_port}", flush=True)
    print("Babylon appearance is provisional; native Godot validation remains separate.", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
