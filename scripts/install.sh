#!/usr/bin/env bash
# Install the app (and optionally the menu patch) onto a GitHub Badger 2350 over USB. macOS.
#
#   scripts/install.sh            # app only
#   scripts/install.sh --menu     # app + patched menu (red first tile with logo icon)
#
# /system is read-only from MicroPython, so this reboots the badge into USB Disk Mode,
# copies files onto the BADGER volume, ejects it, then reboots the badge normally.
set -euo pipefail
cd "$(dirname "$0")/.."

PORT="${BADGE_PORT:-$(ls /dev/cu.usbmodem* 2>/dev/null | head -1)}"
[ -n "$PORT" ] || { echo "No badge serial port found (is it switched on, with a data cable?)"; exit 1; }
MPR=(uvx mpremote connect "$PORT")

echo "Rebooting $PORT into USB Disk Mode..."
"${MPR[@]}" exec "import powman; powman.reset_into_msc()" >/dev/null 2>&1 || true
for _ in $(seq 20); do [ -d /Volumes/BADGER ] && break; sleep 1; done
[ -d /Volumes/BADGER ] || { echo "BADGER volume did not appear"; exit 1; }

mkdir -p /Volumes/BADGER/apps/milwaukee
cp app/milwaukee/__init__.py /Volumes/BADGER/apps/milwaukee/__init__.py
if ls assets/products/*.png >/dev/null 2>&1; then
  mkdir -p /Volumes/BADGER/apps/milwaukee/products
  cp assets/products/*.png /Volumes/BADGER/apps/milwaukee/products/
fi
if [ "${1:-}" = "--menu" ]; then
  # refuse to patch a menu that isn't the one the patch was built from
  cmp -s menu_patch/app.py.orig /Volumes/BADGER/apps/menu/app.py \
    || cmp -s menu_patch/app.py /Volumes/BADGER/apps/menu/app.py \
    || { echo "Badge menu app.py differs from menu_patch/app.py.orig (firmware update?). Not patching."; diskutil eject /Volumes/BADGER; exit 1; }
  cp menu_patch/app.py /Volumes/BADGER/apps/menu/app.py
fi
sync
diskutil eject /Volumes/BADGER

echo "Waiting for the badge to reboot..."
sleep 9
"${MPR[@]}" exec "import machine; machine.reset()" >/dev/null 2>&1 || true
echo "Done. Open the Milwaukee tile on the badge."
