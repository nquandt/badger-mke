"""Generate the browser previews: preview/index.html (animation) and preview/states.html (UI screens)."""
import json

from _logo import ROOT, centred

data, width = centred()
src = (ROOT / "preview" / "template.html").read_text()
src = src.replace("__DATA__", json.dumps(data)).replace("__W__", str(round(width, 2)))
(ROOT / "preview" / "index.html").write_text(src)
print(f"wrote preview/index.html ({len(src)} bytes)")

states = (ROOT / "preview" / "states_template.html").read_text()
products = json.load(open(ROOT / "assets" / "products.json"))
products = [{"slug": q["slug"], "name": q["name"], "cat": q["category"], "url": q["page"]} for q in products]
states = states.replace("__PRODUCTS__", json.dumps(products)).replace("__DATA__", json.dumps(data)).replace("__W__", str(round(width, 2)))
(ROOT / "preview" / "states.html").write_text(states)
print(f"wrote preview/states.html ({len(states)} bytes)")
