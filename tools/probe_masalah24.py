"""Probe #24 (2026-08-27):

send_keys ke input#imgFile TIDAK memicu upload (probe 23: tidak ada
POST firebase, widget tidak berubah). Diagnosa:
1) console error browser
2) input#imgFile masih ada? punya files?
3) event yang di-listen input tsb (via jQuery data events)
4) network apa saja setelah send_keys
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
opt.set_capability("goog:loggingPrefs", {"performance": "ALL", "browser": "ALL"})
driver = webdriver.Chrome(options=opt)
driver.implicitly_wait(0)
page = HssSafetyPage(driver)

PNG_B64 = ("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJ"
           "AAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==")
GAMBAR = Path(__file__).resolve().parent / "_dummy_tiny.png"
GAMBAR.write_bytes(base64.b64decode(PNG_B64))


def net_terakhir():
    hasil = []
    for entri in driver.get_log("performance"):
        pesan = json.loads(entri["message"]).get("message", {})
        if pesan.get("method") != "Network.requestWillBeSent":
            continue
        req = pesan.get("params", {}).get("request", {})
        hasil.append({"m": req.get("method"), "url": req.get("url", "")[:100]})
    return hasil[-8:]


def console_terakhir():
    try:
        return [e.get("message", "")[:160]
                for e in driver.get_log("browser")[-6:]]
    except Exception as exc:
        return [f"(gagal baca log: {exc})"]


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

    # patch click supaya dialog OS tidak muncul
    driver.execute_script(
        "window.__fileInputs = [];"
        "HTMLInputElement.prototype.click = function () {"
        "  if (this.type === 'file') { window.__fileInputs.push(this);"
        "    return; }"
        "  return arguments.length ?"
        "    HTMLElement.prototype.click.apply(this, arguments)"
        "    : HTMLElement.prototype.click.call(this);"
        "};"
    )
    driver.execute_script(
        "const modal = document.querySelector('.modal.show');"
        "const a = modal.querySelector('.dt-input-upload');"
        "a.scrollIntoView({block: 'center'});"
        "a.click();"
    )
    page._wait(15).until(
        lambda _: driver.execute_script(
            "return document.querySelectorAll('input[type=\"file\"]').length > 0;"
        ),
        "input file tidak muncul",
    )
    print("[form] input muncul:",
          driver.execute_script(
              "const i = document.querySelector('input[type=file]');"
              "return i ? {id: i.id, html: i.outerHTML.replace(/\\s+/g,' ')"
              "  .slice(0, 200)} : null;"),
          flush=True)

    el = driver.find_element("css selector", "input[type='file']")
    el.send_keys(str(GAMBAR))
    print("[form] file dikirim", flush=True)
    page.pace(6.0)
    print("[form] input sesudah:",
          driver.execute_script(
              "const i = document.querySelector('input[type=file]');"
              "return i ? {files: i.files ? i.files.length : -1,"
              "  ada: true} : {ada: false};"),
          flush=True)
    print("[form] console:", console_terakhir(), flush=True)
    print("[net] setelah send_keys:", net_terakhir(), flush=True)

    # coba trigger change manual (kalau handler jQuery tidak nyala)
    driver.execute_script(
        "const i = document.querySelector('input[type=file]');"
        "if (i) {"
        "  i.dispatchEvent(new Event('change', {bubbles: true}));"
        "  const ev = new Event('input', {bubbles: true});"
        "  i.dispatchEvent(ev);"
        "}"
    )
    page.pace(6.0)
    print("[form] SETELAH trigger manual:", console_terakhir(), flush=True)
    print("[net] setelah trigger manual:", net_terakhir(), flush=True)

    print("[SELESAI]", flush=True)
finally:
    driver.quit()
    GAMBAR.unlink(missing_ok=True)
