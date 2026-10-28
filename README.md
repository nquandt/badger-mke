# Milwaukee Tool badge

A custom app for the **GitHub Universe Badger 2350** (RP2350, 320×240 color LCD, MicroPython) that shows the
Milwaukee Tool logo with a procedural, never-quite-repeating animation.

## What it does

- Every cycle randomly composes an **entrance** (impact slam / mask wipe + bolt strike / bolt-first strike),
  a **hold** of roughly 9–20 s with random glitch bursts (tear, RGB split, bolt flicker, jitter, bolt zap,
  rare color invert), and an **exit** (glitch out / reverse mask wipe / CRT power-off). No entrance or exit
  plays twice in a row.
- Five buttons: Up, Down, Left, Right, Select (Select doubles as back).
  - **Left/Right**: previous/next screen (logo, five product cards, level). On the contact QR they switch LinkedIn/GitHub.
  - **Up**: play/pause on the logo (pause snaps to the plain logo); QR on a card; zero on the level.
  - **Down**: contact QR on the logo, product QR on a card.
  - **Select**: close a QR, else go to the logo; on the logo it exits to the menu.
  - Returns to the logo after 25 s idle. Level bubble direction is uncalibrated (`LEVEL_SX/LEVEL_SY`).
- Optional menu patch: first tile, Milwaukee red, big logo icon.

## Install

Needs [uv](https://docs.astral.sh/uv/) (for `mpremote`), macOS, and a USB **data** cable with the badge switched on.

```bash
scripts/install.sh           # app only
scripts/install.sh --menu    # app + patched menu (red first tile with logo icon)
```

`/system` is read-only from MicroPython, so the script reboots the badge into USB Disk Mode, copies files to
the `BADGER` volume, ejects it, and reboots. Set `BADGE_PORT` to override serial port detection.
The menu patch refuses to apply if the badge's `menu/app.py` differs from `menu_patch/app.py.orig`
(e.g. after a firmware update).

## Layout

| Path | What |
| --- | --- |
| `app/template.py` | The app source (logo data is injected at build time) |
| `app/milwaukee/__init__.py` | Generated, installable app |
| `assets/logo.svg` | Logo extracted from the milwaukeetool.com header (inline SVG) |
| `assets/logo.flat.json` | Logo curves flattened to polylines for the badge's `shape.custom` |
| `menu_patch/` | `app.py.orig` is the badge's original menu file; `app.py` is generated |
| `preview/` | Browser preview of the animation (`template.html` → generated `index.html`) |
| `tools/` | Generators |

## Rebuild

```bash
uv run --with svgelements python tools/flatten.py   # logo.svg -> logo.flat.json (only if the SVG changes)
python3 tools/gen_app.py                            # app/template.py -> app/milwaukee/__init__.py
python3 tools/gen_preview.py                        # preview/template.html -> preview/index.html
python3 tools/build_menu_patch.py 1.32              # menu patch; arg = icon width (1.0 = 48px)
```

Tuning constants are at the top of `app/template.py` (`SPEED`, `HOLD_MS`, durations, burst weights).
To preview, serve `preview/` (`python3 -m http.server`) and open it; the Speed/Hold sliders mirror
`SPEED`/`HOLD_MS`. The preview seeds each cycle deterministically, while the badge uses the hardware RNG,
so exact sequences differ.

## Product images (not committed)

`assets/products.json` lists the featured products, their milwaukeetool.com pages and hero image URLs.
The photos are Milwaukee Tool's, so they are fetched on demand and gitignored:

```bash
python3 tools/fetch_product_images.py                       # -> assets/source/*.webp
uv run --with pillow python tools/prep_images.py            # -> assets/products/*.png (badge-sized, cropped)
python3 tools/gen_preview.py && python3 -m http.server      # open /preview/states.html (serve from the repo root)
```

`preview/states.html` is a mockup of the planned UI (product cards, QR screens, level); it is not on the badge yet.

## Badge notes

- Serial port is `/dev/cu.usbmodem*`. Any `mpremote` connection interrupts the running menu and leaves the
  screen blank; finish with `machine.reset()`.
- Folders in `/system/apps` containing `__init__.py` appear in the menu automatically.
- Firmware updates may overwrite `/system`; re-run the installer.

The Milwaukee logo is a trademark of Milwaukee Electric Tool Corporation, used here for a personal badge.
