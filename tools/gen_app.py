"""Generate app/milwaukee/__init__.py from app/template.py + the flattened logo."""
from pathlib import Path

from _logo import ROOT, centred

data, width = centred()
src = (ROOT / "app" / "template.py").read_text()
src = src.replace("__DATA__", repr(data)).replace("__W__", repr(round(width, 2)))
out = ROOT / "app" / "milwaukee" / "__init__.py"
out.write_text(src)
compile(src, str(out), "exec")
print(f"wrote {out.relative_to(ROOT)} ({len(src)} bytes)")
