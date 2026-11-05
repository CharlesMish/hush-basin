#!/usr/bin/env python3
"""Hem Loop layout helper: check or re-solve loop closure, optionally draw a map.

  python3 tools/rink_layout.py --check            # exit 1 if the loop does not close
  python3 tools/rink_layout.py --solve            # rewrite SIDING/SOUTH lengths to close it
  python3 tools/rink_layout.py --png out.png      # top-down sketch (needs Pillow)
"""
from __future__ import annotations
import argparse, json, math
from pathlib import Path

COURSE = Path(__file__).resolve().parents[1] / "game/rink/hem_loop_course.json"
SOLVE = ("SIDING", "SOUTH")


def fwd(yaw):
    return (-math.sin(yaw), -math.cos(yaw))


def walk(pieces, start_yaw):
    x = z = 0.0
    yaw = start_yaw
    dirs = {}
    length = 0.0
    pts = []
    for pc in pieces:
        f = fwd(yaw)
        if pc["kind"] == "straight":
            dirs[pc["id"]] = f
            n = max(1, int(pc["len"]))
            for i in range(n):
                pts.append((x + f[0] * pc["len"] * i / n, z + f[1] * pc["len"] * i / n, pc))
            x += f[0] * pc["len"]
            z += f[1] * pc["len"]
            length += pc["len"]
        else:
            a = math.radians(pc["deg"]); r = pc["r"]; sg = 1 if a > 0 else -1
            lf = (f[1], -f[0]); cx, cz = x + lf[0] * r * sg, z + lf[1] * r * sg
            n = max(1, int(abs(a) * r))
            for i in range(n):
                y = yaw + a * i / n; fy = fwd(y); ly = (fy[1], -fy[0])
                pts.append((cx - ly[0] * r * sg, cz - ly[1] * r * sg, pc))
            yaw += a
            f2 = fwd(yaw); lf2 = (f2[1], -f2[0])
            x, z = cx - lf2[0] * r * sg, cz - lf2[1] * r * sg
            length += abs(a) * r
    return x, z, yaw, dirs, length, pts


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--solve", action="store_true")
    ap.add_argument("--png")
    a = ap.parse_args()
    data = json.loads(COURSE.read_text())
    pcs = data["pieces"]; y0 = math.radians(data["start_yaw_degrees"])
    if a.solve:
        for pc in pcs:
            if pc["id"] in SOLVE:
                pc["len"] = 0.0
        ex, ez, _, dirs, _, _ = walk(pcs, y0)
        (p, q), (r, s) = dirs[SOLVE[0]], dirs[SOLVE[1]]
        det = p * s - q * r
        l1 = (-ex * s + ez * r) / det; l2 = (-p * ez + q * ex) / det
        for pc in pcs:
            if pc["id"] == SOLVE[0]: pc["len"] = round(l1, 3)
            if pc["id"] == SOLVE[1]: pc["len"] = round(l2, 3)
        COURSE.write_text(json.dumps(data, indent=2) + "\n")
    x, z, yaw, _, length, pts = walk(pcs, y0)
    gap = math.hypot(x, z); turn = math.degrees(yaw - y0)
    print(json.dumps({"closure_gap_m": round(gap, 4), "total_turn_deg": round(turn, 3), "length_m": round(length, 2),
                      "lengths": {pc["id"]: (pc["len"] if pc["kind"] == "straight" else round(abs(math.radians(pc["deg"])) * pc["r"], 2)) for pc in pcs}}))
    if a.png:
        from PIL import Image, ImageDraw
        xs = [p[0] for p in pts]; zs = [p[1] for p in pts]
        k = min(860 / (max(xs) - min(xs) + 80), 660 / (max(zs) - min(zs) + 80))
        ox, oz = min(xs) - 40, min(zs) - 40
        img = Image.new("RGB", (900, 700), (40, 34, 28)); d = ImageDraw.Draw(img)
        for X, Z, pc in pts:
            d.ellipse([(X - ox) * k - 2, (Z - oz) * k - 2, (X - ox) * k + 2, (Z - oz) * k + 2], fill=(200, 200, 190))
        img.save(a.png)
    if a.check and (gap > 0.05 or abs(abs(turn) - 360.0) > 0.01):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
