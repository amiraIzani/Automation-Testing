"""Probe #23 (2026-08-27):

Alur upload otomatis yang AMAN:
1) patch HTMLInputElement.prototype.click (file) -> no-op sambil
   mencatat input (dialog OS tidak muncul)
2) klik anchor .dt-input-upload -> tunggu input#imgFile muncul
3) send_keys dummy.png (1x1 transparan, 67 byte, dibuat dari base64)
4) amati: widget berubah (nama file/thumbnail), POST ke firebase
5) Cancel form -> cek POST lanjutan (resiko file yatim)

CATATAN: probe ini meng-upload 1 file 67 byte ke Firebase DEV --
ukuran terkecil yang bisa dibuat, tidak bisa dihindari untuk
membuktikan alurnya.
"""
import base64
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException

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

# PNG 1x1 transparan (67 byte)
PNG_B64 = ("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJ"
           "AAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==")
GAMBAR = Path(__file__).resolve().parent / "_dummy_tiny.png"
GAMBAR.write_bytes(base64.b64decode(PNG_B64))

JS_PATCH = """
window.__fileInputs = [];
HTMLInputElement.prototype.click = function () {
    if (this.type === 'file') { window.__fileInputs.push(this); return; }
    return HTMLInputElement.prototype.click.__orig.apply(this, arguments);
};
HTMLInputElement.prototype.click.__orig = HTMLInputElement.prototype.click;
return 'patch aktif';
"""


def post_firebase():
    hasil = []
    for entri in driver.get_log("performance"):
        pesan = json.loads(entri["message"]).get("message", {})
        if pesan.get("method") != "Network.requestWillBeSent":
            continue
        req = pesan.get("params", {}).get("request", {})
        url = req.get("url", "")
        if req.get("method") == "POST" and ("firebase" in url
                                            or "upload" in url.lower()):
            hasil.append({"url": url[:110],
                          "size": len(req.get("postData") or "")})
    return hasil


def state_group():
    return driver.execute_script(
        "const modal = document.querySelector('.modal.show');"
        "const g = [...modal.querySelectorAll('.form-group')].find(x => {"
        "  const l = x.querySelector('label');"
        "  return l && l.innerText.indexOf('Lampiran Sketsa') === 0;"
        "});"
        "if (!g) return 'group tidak ada';"
        "return {teks: (g.innerText || '').replace(/\\s+/g,' ')"
        "          .trim().slice(0, 200),"
        "  img: g.querySelectorAll('img').length,"
        "  inputFile: g.querySelectorAll('input[type=file]').length,"
        "  hidden: [...g.querySelectorAll('input')]"
        "    .map(i => i.value || '').filter(v => v).slice(0, 2)};"
    )


try:
    LoginPage(driver).login()
    print("[OK] login", flush=True)

    page.buka_halaman("incident_investigation_form")
    try:
        page.buka_form_create()
    except TimeoutException:
        driver.execute_script(
            "const bs = [...document.querySelectorAll('button')];"
            "const b = bs.find(x => (x.innerText || '').trim()"
            "  === 'Create with Form'); if (b) b.click();"
        )
        page.tunggu_modal_terbuka()
    page.pace(2.0)
    print("[form] patch:", driver.execute_script(JS_PATCH), flush=True)

    # klik anchor Lampiran Sketsa/Gambar (FirebaseImageUpload)
    driver.execute_script(
        "const modal = document.querySelector('.modal.show');"
        "const g = [...modal.querySelectorAll('.form-group')].find(x => {"
        "  const l = x.querySelector('label');"
        "  return l && l.innerText.indexOf('Lampiran Sketsa') === 0;"
        "});"
        "const a = g.querySelector('.dt-input-upload');"
        "a.scrollIntoView({block: 'center'});"
        "a.click(); return true;"
    )
    # tunggu input file muncul
    page._wait(15).until(
        lambda _: driver.execute_script(
            "return document.querySelectorAll('input[type=\"file\"]').length > 0;"
        ),
        "input file tidak muncul setelah klik anchor upload",
    )
    print("[form] input file muncul:", driver.execute_script(
        "return [...document.querySelectorAll('input[type=\"file\"]')]"
        ".map(i => i.id);"), flush=True)

    # kirim file
    el = driver.find_element("css selector", "input[type='file']")
    el.send_keys(str(GAMBAR))
    print("[form] dummy_tiny.png (67 byte) dikirim", flush=True)
    page.pace(8.0)
    print("[form] group SETELAH upload:", json.dumps(state_group(), indent=1),
          flush=True)
    print("[net] POST firebase:", post_firebase(), flush=True)

    # batal form
    page.batal_form()
    page.pace(3.0)
    print("[net] POST setelah Cancel:", post_firebase(), flush=True)
    print("[SELESAI]", flush=True)
finally:
    driver.quit()
    GAMBAR.unlink(missing_ok=True)
