"""Probe #18 (2026-08-27):

Widget upload = <a class=dt-input-upload> dengan data-inputtype
FirebaseDocUpload/FirebaseImageUpload, tanpa input[type=file] statis.
Asumsi: klik anchor -> JS buat input[type=file] -> input.click() ->
dialog file OS. Untuk automasi: override HTMLInputElement.click (file)
supaya dialog tidak muncul, klik anchor, ambil input yang dibuat,
send_keys dummy_hitam.png, amati:
1) widget setelah upload (nama file / thumbnail / hidden value URL
   firebasestorage)
2) POST ke Firebase Storage di performance log
3) Cancel form -> file yatim di Firebase? (kecil, 244 byte)
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

JS_INTERCEPT = """
window.__fileInputs = [];
const orig = HTMLInputElement.prototype.click;
HTMLInputElement.prototype.click = function () {
    if (this.type === 'file') { window.__fileInputs.push(this); return; }
    return orig.apply(this, arguments);
};
return 'intercept aktif';
"""


def dump_group(label):
    return driver.execute_script(
        "const modal = document.querySelector('.modal.show');"
        "if (!modal) return 'modal hilang';"
        "const groups = [...modal.querySelectorAll('.form-group')];"
        "const g = groups.find(x => {"
        "  const l = x.querySelector('label');"
        "  return l && l.innerText.indexOf(arguments[0]) === 0;"
        "});"
        "if (!g) return 'group tidak ada';"
        "return {teks: (g.innerText || '').replace(/\\s+/g,' ')"
        "          .trim().slice(0, 200),"
        "  html: g.outerHTML.replace(/\\s+/g, ' ').slice(0, 900)};",
        label,
    )


def post_net():
    hasil = []
    try:
        for entri in driver.get_log("performance"):
            pesan = json.loads(entri["message"]).get("message", {})
            if pesan.get("method") != "Network.requestWillBeSent":
                continue
            req = pesan.get("params", {}).get("request", {})
            if req.get("method") != "POST":
                continue
            url = req.get("url", "")
            if "firebasestorage" in url or "upload" in url.lower():
                hasil.append({
                    "url": url[:100],
                    "size": len(req.get("postData") or ""),
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
    print("[form] intercept:", driver.execute_script(JS_INTERCEPT), flush=True)

    # klik anchor Upload (Lampiran Sketsa/Gambar = FirebaseImageUpload)
    driver.execute_script(
        "const modal = document.querySelector('.modal.show');"
        "const g = [...modal.querySelectorAll('.form-group')].find(x => {"
        "  const l = x.querySelector('label');"
        "  return l && l.innerText.indexOf('Lampiran Sketsa') === 0;"
        "});"
        "const a = g.querySelector('.dt-input-upload');"
        "if (a) a.click(); return !!a;"
    )
    page.pace(2.0)
    jumlah = driver.execute_script("return window.__fileInputs.length;")
    print(f"[form] input file dibuat: {jumlah}", flush=True)

    if jumlah:
        # kirim file ke input pertama yang dibuat
        el = driver.execute_script("return window.__fileInputs[0];")
        el.send_keys(GAMBAR)
        print("[form] dummy_hitam.png dikirim", flush=True)
        page.pace(6.0)
        print("[form] group SETELAH upload:",
              json.dumps(dump_group("Lampiran Sketsa"), indent=1), flush=True)
        print("[net] POST firebase:", post_net(), flush=True)

        # batal -- file yatim di firebase kalau upload langsung saat pilih
        page.batal_form()
        page.pace(3.0)
        print("[net] POST setelah Cancel:", post_net(), flush=True)

    print("[SELESAI]", flush=True)
finally:
    driver.quit()
