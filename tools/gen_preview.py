"""Generate preview/index.html (browser preview of the animation) from preview/template.html."""
import json

from _logo import ROOT, centred

data, width = centred()
src = (ROOT / "preview" / "template.html").read_text()
src = src.replace("__DATA__", json.dumps(data)).replace("__W__", str(round(width, 2)))
(ROOT / "preview" / "index.html").write_text(src)
print(f"wrote preview/index.html ({len(src)} bytes)")
