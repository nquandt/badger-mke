"""Flatten assets/logo.svg (curves -> polylines) into assets/logo.flat.json.

Run: uv run --with svgelements python tools/flatten.py
"""
import json
from pathlib import Path

from svgelements import SVG, Close, Move, Path as SvgPath

ROOT = Path(__file__).resolve().parent.parent
svg = SVG.parse(str(ROOT / "assets" / "logo.svg"))

out = []
for p in (e for e in svg.elements() if isinstance(e, SvgPath)):
    contours = []
    for sub in abs(p).as_subpaths():
        pts = []
        for seg in SvgPath(sub):
            if isinstance(seg, Move):
                pts.append((seg.end.x, seg.end.y))
                continue
            if isinstance(seg, Close):
                continue
            steps = 1 if type(seg).__name__ == "Line" else max(3, int(seg.length() / 3))
            for i in range(1, steps + 1):
                q = seg.point(i / steps)
                pts.append((q.x, q.y))
        if len(pts) > 1 and pts[0] == pts[-1]:
            pts.pop()
        contours.append(pts)
    out.append({"fill_rule": p.values.get("fill-rule", "nonzero"), "contours": contours})

(ROOT / "assets" / "logo.flat.json").write_text(json.dumps(out))
print(f"{len(out)} paths, {sum(len(p['contours']) for p in out)} contours")
