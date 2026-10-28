"""Download the product hero images listed in assets/products.json into assets/source/ (gitignored).

The images are Milwaukee Tool's; they are fetched from the public product pages and are not committed.
Run: python3 tools/fetch_product_images.py
"""
import json
import time
import urllib.request

from _logo import ROOT

products = json.load(open(ROOT / "assets" / "products.json"))
out = ROOT / "assets" / "source"
out.mkdir(exist_ok=True)
for p in products:
    req = urllib.request.Request(p["image"], headers={"User-Agent": "Mozilla/5.0"})
    data = urllib.request.urlopen(req, timeout=30).read()
    (out / f"{p['slug']}.webp").write_bytes(data)
    print(f"{p['slug']}: {len(data)} bytes")
    time.sleep(1)
