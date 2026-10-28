"""Shared: load the flattened logo and centre it on the origin."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load():
    paths = json.load(open(ROOT / "assets" / "logo.flat.json"))
    xs = [x for p in paths for c in p["contours"] for x, _ in c]
    ys = [y for p in paths for c in p["contours"] for _, y in c]
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    return paths, cx, cy, max(xs) - min(xs)


def centred(places=2):
    """Per path, per contour: flat [x0, y0, x1, y1, ...] centred on (0, 0)."""
    paths, cx, cy, width = load()
    data = [[[round(v, places) for x, y in c for v in (x - cx, y - cy)] for c in p["contours"]] for p in paths]
    return data, width
