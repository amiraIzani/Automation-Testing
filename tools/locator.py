"""
tools/locator.py
================
Baca semua JSON hasil scan halaman Safety lalu cetak ringkasan ID
stabil (bukan id auto-generate), tombol, dan select per halaman --
dipakai untuk menyusun dokumentasi locator yang bersih.
"""

import glob
import json
import os
import re

POLA_ID_OTOMATIS = re.compile(r"^(input_\d+|cb\w+_\d+|btn\w+_\d+|modal_\d+)$")

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCAN_DIR = os.path.join(BASE, "reports", "scan", "safety")

for f in sorted(glob.glob(os.path.join(SCAN_DIR, "[0-9]*.json"))):
    d = json.load(open(f, encoding="utf-8"))
    name = os.path.basename(f)[:-5]
    ids = set()
    txt_buttons = set()
    for e in d["elements"]:
        if (
            e["id"]
            and not POLA_ID_OTOMATIS.match(e["id"])
            and not e["id"].startswith("tableData")
            and not e["id"].startswith("modal")
        ):
            ids.add(e["id"])
        if e["tag"] == "button" and e["text"]:
            txt_buttons.add(e["text"][:30])
    print(f"{name:<48}")
    if ids:
        print(f"  IDs    : {', '.join(sorted(ids))}")
    if txt_buttons:
        print(f"  Tombol : {', '.join(sorted(txt_buttons))}")
    print()
