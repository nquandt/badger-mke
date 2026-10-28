"""Build menu_patch/app.py from the original menu app.py:
  - registers a Milwaukee logo icon in ICONS
  - puts "milwaukee" first in APP_ORDER
  - makes the milwaukee tile Milwaukee red

Usage: python tools/build_menu_patch.py [icon_width]   (default 1.32; 1.0 = 48px)
"""
import sys

from _logo import ROOT, load

width_units = float(sys.argv[1]) if len(sys.argv) > 1 else 1.32
paths, cx, cy, w = load()
u = width_units / w
contours = [tuple(round(v, 3) for x, y in c for v in ((x - cx) * u, (y - cy) * u)) for p in paths for c in p["contours"]]

src = (ROOT / "menu_patch" / "app.py.orig").read_text()
imp = "from icons import ICONS\n"
rgb = "        self.rgb = ui.PALETTE[ordinal % len(ui.PALETTE)]\n"
order = 'APP_ORDER = (\n    "badge",'
assert src.count(imp) == 1 and src.count(rgb) == 1 and src.count(order) == 1, "menu app.py changed upstream"

icon = ('\n# custom icon for the Milwaukee Tool logo app (same format as icons.ICONS: white vector contours)\n'
        'ICONS["milwaukee"] = (\n' + "".join(f"    {c!r},\n" for c in contours) + ")\n")
src = src.replace(imp, imp + icon).replace(order, 'APP_ORDER = (\n    "milwaukee",\n    "badge",')
src = src.replace(rgb, rgb + '        if slug == "milwaukee":\n            self.rgb = (219, 1, 28)  # Milwaukee red\n')
compile(src, "app.py", "exec")
(ROOT / "menu_patch" / "app.py").write_text(src)
print(f"wrote menu_patch/app.py (icon ~{round(width_units * 48)}px wide)")
