"""Prepare badge-sized product images: assets/source/*.webp -> assets/products/*.png (gitignored).

Crops to the product, removes the blue ONE-KEY wifi badge, and fits within the hero area.
Run: uv run --with pillow python tools/prep_images.py
"""
import json
from PIL import Image

from _logo import ROOT

BOX = (276, 130)   # max hero size on the 320x240 card (white panel is 292x142)
products = json.load(open(ROOT / "assets" / "products.json"))
out = ROOT / "assets" / "products"
out.mkdir(exist_ok=True)
for p in products:
    im = Image.open(ROOT / "assets" / "source" / f"{p['slug']}.webp").convert("RGBA")
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if a and b > 140 and b - r > 70 and abs(g - 150) < 90:   # ONE-KEY wifi tag blue
                px[x, y] = (r, g, b, 0)
    alpha = im.getchannel("A").point(lambda v: 255 if v > 8 else 0)
    im = im.crop(alpha.getbbox())
    im.thumbnail(BOX, Image.LANCZOS)
    im.save(out / f"{p['slug']}.png", optimize=True)
    print(f"{p['slug']}: {im.size}")
