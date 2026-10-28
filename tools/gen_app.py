"""Generate app/milwaukee/__init__.py from app/template.py + the flattened logo."""
from pathlib import Path

from _logo import ROOT, centred

data, width = centred()
import json

products = [(p["slug"], p["name"], p["category"], p["page"].rstrip("/").split("/")[-1]) for p in json.load(open(ROOT / "assets" / "products.json"))]
src = (ROOT / "app" / "template.py").read_text()
src = src.replace("__PRODUCTS__", repr(products)).replace("__DATA__", repr(data)).replace("__W__", repr(round(width, 2)))
out = ROOT / "app" / "milwaukee" / "__init__.py"
out.write_text(src)
compile(src, str(out), "exec")
print(f"wrote {out.relative_to(ROOT)} ({len(src)} bytes)")
