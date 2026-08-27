"""Probe #20 (2026-08-27):

Dugaan: widget upload memakai showOpenFilePicker (File System Access
API) -> dialog OS native yang TIDAK bisa di-automasi Selenium secara
langsung. Konfirmasi:
1) override showOpenFilePicker -> klik anchor -> apakah dipanggil?
2) kalau iya: mock handle yang mengembalikan File (dibangun dari
   bytes dummy_hitam.png via base64) -> amati alur upload aplikasi:
   POST ke Firebase, widget berubah (thumbnail/nama file/URL).
"""
import base64
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

GAMBAR = Path(__file__).resolve().parent / "dummy_hitam.png"
B64 = base64.b64encode(GAMBAR.read_bytes()).decode()


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
                    "url": url[:110],
                    "size": len(req.get("postData") or ""),
                })
    except Exception:
        pass
    return hasil


try:
    LoginPage(driver).login()
    print("[OK] login", flush=True)

    page.buka_halaman("incident_investigation_form")
    try:
        page.buka_form_create()
    except Exception:
        # quirk SPA stuck -- klik JS langsung (probe 21: modal terbuka
        # normal dengan klik JS)
        driver.execute_script(
            "const bs = [...document.querySelectorAll('button')];"
            "const b = bs.find(x => (x.innerText || '').trim()"
            "  === 'Create with Form');"
            "if (b) b.click();"
        )
        page.tunggu_modal_terbuka()
    page.pace(2.0)

    # 1) deteksi mekanisme
    driver.execute_script(
        "window.__pickerCalls = [];"
        "window.showOpenFilePicker = async function(...a) {"
        "  window.__pickerCalls.push(a.length);"
        "  throw new Error('picker di-sadap probe');"
        "};"
    )
    driver.execute_script(
        "const modal = document.querySelector('.modal.show');"
        "const a = modal.querySelector('.dt-input-upload');"
        "a.scrollIntoView({block: 'center'});"
        "a.click();"
    )
    page.pace(2.0)
    dipanggil = driver.execute_script("return window.__pickerCalls;")
    print(f"[picker] showOpenFilePicker dipanggil: {dipanggil}", flush=True)

    # 2) kalau showOpenFilePicker, mock handle + File dari bytes lokal
    if dipanggil:
        driver.execute_script(
            f"window.__file = new File([Uint8Array.from("
            f"atob('{B64}'), c => c.charCodeAt(0))], 'dummy_hitam.png',"
            " {type: 'image/png'});"
            "window.showOpenFilePicker = async () => ["
            "  { getFile: async () => window.__file } ];"
            "return window.__file.size;"
        )
        driver.execute_script(
            "const modal = document.querySelector('.modal.show');"
            "const a = modal.querySelector('.dt-input-upload');"
            "a.scrollIntoView({block: 'center'});"
            "a.click();"
        )
        page.pace(8.0)
        state = driver.execute_script(
            "const modal = document.querySelector('.modal.show');"
            "const g = [...modal.querySelectorAll('.form-group')].find(x => {"
            "  const l = x.querySelector('label');"
            "  return l && l.innerText.indexOf('Lampiran Sketsa') === 0;"
            "});"
            "return {teks: (g ? g.innerText : '').replace(/\\s+/g,' ')"
            "          .trim().slice(0, 250),"
            "  html: g ? g.outerHTML.replace(/\\s+/g, ' ').slice(0, 1000)"
            "          : null};"
        )
        print("[form] widget SETELAH upload mock:",
              json.dumps(state, indent=1), flush=True)
        print("[net] POST firebase:", post_net(), flush=True)

    print("[SELESAI]", flush=True)
finally:
    driver.quit()
