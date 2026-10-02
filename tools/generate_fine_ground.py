#!/usr/bin/env python3
"""Offline, dependency-free tileable ground detail; no engine, assets or geometry.

Writes one 256-square RGBA PNG whose texels are periodic in both axes:
R/G = signed height slope (d/du, d/dv) of a gravel/grain relief,
B   = signed mineral (dirt, gravel) albedo grain,
A   = signed asphalt aggregate albedo grain.
The terrain shader samples it in world metres and fades it with distance.
"""
from pathlib import Path
import argparse, hashlib, json, math, random, struct, zlib

ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / 'game'
CONFIG = GAME / 'presentation/fine_ground_v1.json'
OUT = GAME / 'presentation/fine_ground'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def png(path, w, h, channels, data):
    def chunk(kind, b):
        return struct.pack('>I', len(b)) + kind + b + struct.pack('>I', zlib.crc32(kind + b) & 0xffffffff)
    color = {1: 0, 3: 2, 4: 6}[channels]
    rows = b''.join(b'\0' + bytes(data[y * w * channels:(y + 1) * w * channels]) for y in range(h))
    path.write_bytes(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, color, 0, 0, 0))
                     + chunk(b'IDAT', zlib.compress(rows, 9)) + chunk(b'IEND', b''))


def lattice(ix, iz, seed):
    h = (ix * 374761393 + iz * 668265263 + seed * 1447) & 0xffffffff
    h = ((h ^ (h >> 13)) * 1274126177) & 0xffffffff
    return ((h ^ (h >> 16)) & 65535) / 32767.5 - 1


def periodic_noise(n, cells, seed):
    """Smooth value noise with `cells` lattice cells across the tile; wraps exactly."""
    out = [0.0] * (n * n)
    for y in range(n):
        q = (y + .5) * cells / n; iz = math.floor(q); tz = q - iz; tz = tz * tz * (3 - 2 * tz)
        z0 = iz % cells; z1 = (iz + 1) % cells
        for x in range(n):
            p = (x + .5) * cells / n; ix = math.floor(p); tx = p - ix; tx = tx * tx * (3 - 2 * tx)
            x0 = ix % cells; x1 = (ix + 1) % cells
            a = lattice(x0, z0, seed); b = lattice(x1, z0, seed); c = lattice(x0, z1, seed); d = lattice(x1, z1, seed)
            out[y * n + x] = (a + (b - a) * tx) * (1 - tz) + (c + (d - c) * tx) * tz
    return out


def stamp(n, rng, count, radius_range, tone_bias):
    """Wrapped elliptical domes; returns (height, tone) with max-height ownership."""
    height = [0.0] * (n * n); tone = [0.0] * (n * n)
    lo, hi = radius_range
    for _ in range(count):
        cx = rng.random() * n; cz = rng.random() * n
        r = lo * (hi / lo) ** rng.random(); aspect = .6 + .4 * rng.random(); angle = rng.random() * math.pi
        t = max(-1.0, min(1.0, rng.gauss(tone_bias, .45)))
        c, s = math.cos(angle), math.sin(angle); span = math.ceil(r) + 1
        for dz in range(-span, span + 1):
            for dx in range(-span, span + 1):
                px = math.floor(cx) + dx; pz = math.floor(cz) + dz
                ox = px + .5 - cx; oz = pz + .5 - cz
                u = (ox * c + oz * s) / r; v = (-ox * s + oz * c) / (r * aspect)
                d = u * u + v * v
                if d >= 1:
                    continue
                i = (pz % n) * n + px % n; hv = math.sqrt(1 - d) * r / hi
                if hv > height[i]:
                    height[i] = hv; tone[i] = t
    return height, tone


def normalize(values):
    mean = sum(values) / len(values); centered = [v - mean for v in values]
    peak = sorted(abs(v) for v in centered)[int(.995 * (len(values) - 1))] or 1.0
    return [max(-1.0, min(1.0, v / peak)) for v in centered]


def encode(v):
    return max(0, min(255, round(127.5 + 127.5 * v)))


def generate(output=OUT):
    cfg = json.loads(CONFIG.read_text())['detail']; n = cfg['resolution']; seed = cfg['seed']
    rng = random.Random(seed)
    stones, stone_tone = stamp(n, rng, cfg['pebbles'], cfg['pebble_radius_px'], 0.0)
    chips, chip_tone = stamp(n, rng, cfg['aggregate'], cfg['aggregate_radius_px'], 0.35)
    broad = periodic_noise(n, 8, seed + 1); mid = periodic_noise(n, 32, seed + 2); fine = periodic_noise(n, 128, seed + 3)
    # Relief: stones sit proud of a softly undulating grain bed.
    relief = [.55 * stones[i] + .20 * broad[i] + .15 * mid[i] + .10 * fine[i] for i in range(n * n)]
    gx = [0.0] * (n * n); gz = [0.0] * (n * n)
    for y in range(n):
        for x in range(n):
            gx[y * n + x] = relief[y * n + (x + 1) % n] - relief[y * n + (x - 1) % n]
            gz[y * n + x] = relief[((y + 1) % n) * n + x] - relief[((y - 1) % n) * n + x]
    gx = normalize(gx); gz = normalize(gz)
    # Mineral grain: individual stone tones, darker gaps between stones, dusty mottling.
    mineral = normalize([(.55 * stone_tone[i] if stones[i] > 0 else -.35) + .30 * mid[i] + .25 * fine[i] + .20 * broad[i] for i in range(n * n)])
    # Asphalt: pale aggregate chips in a darker binder with faint wear.
    asphalt = normalize([(.55 * chip_tone[i] + .20 if chips[i] > 0 else -.15) + .15 * fine[i] + .30 * mid[i] + .40 * broad[i] for i in range(n * n)])
    data = bytearray(n * n * 4)
    for i in range(n * n):
        data[i * 4:i * 4 + 4] = bytes((encode(gx[i]), encode(gz[i]), encode(mineral[i]), encode(asphalt[i])))
    output.mkdir(parents=True, exist_ok=True)
    png(output / 'fine_ground_detail.png', n, n, 4, data)
    # Keep raw PNG bytes in the export. An ignored folder or a normal Texture
    # import cannot satisfy FileAccess reads in the packaged game.
    (output / 'fine_ground_detail.png.import').write_text('[remap]\n\nimporter="keep"\n')
    resident = sum(max(1, n >> level) ** 2 * 4 for level in range(int(math.log2(n)) + 1))
    index = {'version': json.loads(CONFIG.read_text())['version'], 'config_sha256': sha(CONFIG), 'size': [n, n],
             'channels': 'RGBA8: slope_u, slope_v, mineral_grain, asphalt_grain (all signed, 127.5 bias)',
             'resident_texture_bytes_upper_bound': resident,
             'artifacts': {'fine_ground_detail.png': sha(output / 'fine_ground_detail.png')}}
    (output / 'fine_ground_index.json').write_text(json.dumps(index, indent=2, sort_keys=True) + '\n')
    print('Generated fine ground detail', n, 'x', n, '·', (output / 'fine_ground_detail.png').stat().st_size, 'PNG bytes ·', resident, 'resident bytes', flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--output', type=Path, default=OUT); generate(p.parse_args().output)
