"""Probe #22 (2026-08-27):

Klik anchor .dt-input-upload: bukan showOpenFilePicker (probe 20),
bukan input.click() di modal (probe 18). Cek efek klik SECARA LENGKAP:
- jendela browser baru?
- input[type=file] BARU di SELURUH dokumen?
- request jaringan baru (semua method)?
- console error?
- teks/state anchor berubah?
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
opt.set_capability("goog:loggingPrefs", {"performance": "ALL", "browser": "ALL"})
driver = webdriver.Chrome(options=opt)
driver.implicitly_wait(0)
page = HssSafetyPage(driver)


def net_baru(sebelum):
    hasil = []
    for entri in driver.get_log("performance"):
        pesan = json.loads(entri["message"]).get("message", {})
        if pesan.get("method") != "Network.requestWillBeSent":
            continue
        req = pesan.get("params", {}).get("request", {})
        url = req.get("url", "")
        if any(k in url.lower() for k in ("upload", "firebase", "file",
                                          "attachment", "lampiran")):
            hasil.append({"m": req.get("method"), "url": url[:110]})
    return hasil[-6:]


try:
    LoginPage(driver).login()
    print("[OK] login", flush=True)

    page.buka_halaman("incident_investigation_form")
    try:
        page.buka_form_create()
    except Exception:
        driver.execute_script(
            "const bs = [...document.querySelectorAll('button')];"
            "const b = bs.find(x => (x.innerText || '').trim()"
            "  === 'Create with Form'); if (b) b.click();"
        )
        page.tunggu_modal_terbuka()
    page.pace(2.0)

    handles_awal = len(driver.window_handles)
    print(f"[hal] window handles awal = {handles_awal}", flush=True)

    # klik anchor Upload pertama
    driver.execute_script(
        "const modal = document.querySelector('.modal.show');"
        "const a = modal.querySelector('.dt-input-upload');"
        "a.scrollIntoView({block: 'center'});"
        "a.click(); return true;"
    )
    page.pace(4.0)

    print(f"[klik] window handles sesudah = {len(driver.window_handles)}",
          flush=True)
    print("[klik] input file di seluruh dokumen:",
          driver.execute_script(
              "return [...document.querySelectorAll('input[type=\"file\"]')]"
              ".map(i => ({id: i.id, cls: i.className,"
              "  parent: (i.parentElement.className || '').slice(0, 60)}));"),
          flush=True)
    print("[klik] anchor sesudah:",
          driver.execute_script(
              "const modal = document.querySelector('.modal.show');"
              "const a = modal.querySelector('.dt-input-upload');"
              "return (a.outerHTML || '').replace(/\\s+/g,' ').slice(0, 260);"),
          flush=True)
    print("[klik] console error:",
          [e.get("message", "")[:130] for e in driver.get_log("browser")[-5:]],
          flush=True)
    print("[klik] request jaringan:",
          [n for n in net_baru([])][-6:], flush=True)

    print("[SELESAI]", flush=True)
finally:
    driver.quit()
