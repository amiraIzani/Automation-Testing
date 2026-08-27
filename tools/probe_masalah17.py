"""Probe #17 (2026-08-27):

Investigasi widget upload (.dt-input-upload) di form Incident:
1) struktur DOM group upload (input[type=file]? hidden? accept?)
2) kirim dummy_hitam.png -> apa yang berubah di widget (nama file
   tampil? hidden value? thumbnail?)
3) network performance log: apakah file di-POST LANGSUNG saat dipilih
   atau baru saat Save?
4) Cancel form -> ada POST lanjutan? (resiko file yatim di server)
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from config import config
from pages.hss_safety_page import HssSafetyPage
from pages.login_page import LoginPage

opt = Options()
opt.add_argument("--start-maximized")
opt.add_argument(f"--user-data-dir={config.CHROME_PROFILE_PATH}")
opt.add_argument("--disable-notifications")
opt.add_experimental_option("excludeSwitches", ["enable-automation"])
opt.set_capability("goog:loggingPrefs", {"performance": "ALL"})
driver = webdriver.Chrome(options=opt)
driver.implicitly_wait(0)
page = HssSafetyPage(driver)

GAMBAR = str(Path(__file__).resolve().parent / "dummy_hitam.png")

JS_DUMP = r"""
const modal = document.querySelector('.modal.show');
if (!modal) return 'modal tidak ada';
const out = [];
modal.querySelectorAll('.form-group').forEach(g => {
    const a = g.querySelector('.dt-input-upload');
    if (!a) return;
    const l = g.querySelector('label');
    const fi = g.querySelector('input[type="file"]');
    const hid = g.querySelector('input[type="hidden"]');
    out.push({label: (l ? l.innerText : '').trim().slice(0, 50),
        anchor: a.outerHTML.replace(/\s+/g, ' ').slice(0, 220),
        fileInput: fi ? {id: fi.id, accept: fi.getAttribute('accept'),
            multiple: fi.multiple, tampil: fi.getBoundingClientRect().height > 0}
            : null,
        hidden: hid ? {id: hid.id, value: hid.value.slice(0, 60)} : null,
        teksGroup: (g.innerText || '').replace(/\s+/g, ' ').trim().slice(0, 120)});
});
return out;
"""


def post_upload():
    """Ambil URL POST dari performance log (Network.requestWillBeSent)."""
    hasil = []
    try:
        for entri in driver.get_log("performance"):
            pesan = json.loads(entri["message"]).get("message", {})
            metode = pesan.get("method")
            if metode != "Network.requestWillBeSent":
                continue
            req = pesan.get("params", {}).get("request", {})
            if req.get("method") != "POST":
                continue
            post = req.get("postData") or ""
            if "upload" in req.get("url", "").lower() or "Upload" in post \
                    or "File" in req.get("url", "") or "Base64" in post:
                hasil.append({
                    "url": req.get("url", "")[:120],
                    "postData": post[:160],
                })
    except Exception:
        pass
    return hasil


try:
    LoginPage(driver).login()
    print("[OK] login", flush=True)

    page.buka_halaman("incident_investigation_form")
    page.buka_form_create()
    page.pace(2.0)
    print("[form] SEBELUM upload:", json.dumps(driver.execute_script(JS_DUMP),
          indent=1), flush=True)

    # kirim file dummy ke semua input[type=file] di modal
    els = driver.find_elements("css selector", ".modal.show input[type='file']")
    print(f"[form] jumlah input file = {len(els)}", flush=True)
    for i, el in enumerate(els):
        try:
            el.send_keys(GAMBAR)
            print(f"[form] file dummy dikirim ke input #{i}", flush=True)
        except Exception as exc:
            print(f"[form] input #{i} GAGAL: {repr(exc)[:140]}", flush=True)
    page.pace(3.0)
    print("[form] SETELAH upload:", json.dumps(driver.execute_script(JS_DUMP),
          indent=1), flush=True)
    print("[net] POST setelah pilih file:", post_upload(), flush=True)

    # Cancel form -- cek ada POST file lanjutan / file yatim
    page.batal_form()
    page.pace(3.0)
    print("[net] POST setelah Cancel:", post_upload(), flush=True)

    print("[SELESAI]", flush=True)
finally:
    driver.quit()
