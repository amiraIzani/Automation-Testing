"""Probe #26 (2026-08-27):

Setelah form Incident diisi + upload file dummy, Save TIDAK menutup
modal (validasi gagal, run_verif7). Dump: pesan validasi/alert di
modal, state input file, console error.
"""
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
opt.set_capability("goog:loggingPrefs", {"browser": "ALL"})
driver = webdriver.Chrome(options=opt)
driver.implicitly_wait(0)
page = HssSafetyPage(driver)


def dump_state():
    return driver.execute_script(
        "const modal = document.querySelector('.modal.show');"
        "if (!modal) return {modal: false};"
        "const valid = [...modal.querySelectorAll("
        "  '.text-danger, .invalid-feedback, .field-validation-error,"
        "  .alert, .swal2-container, .bootbox')].map(e =>"
        "  (e.innerText || '').replace(/\\s+/g, ' ').trim().slice(0, 120));"
        "const fi = modal.querySelector('input[type=file]#imgFile');"
        "return {modal: true,"
        "  validasi: valid.filter(v => v),"
        "  file: fi ? {files: fi.files ? fi.files.length : -1,"
        "    name: fi.getAttribute('name')} : null,"
        "  tombolSave: modal.querySelectorAll('button').length};"
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
    page.pace(1.0)
    page.isi_form_create_otomatis(penanda="Probe26")
    print("[form] state setelah isi:", dump_state(), flush=True)

    # klik Save
    driver.execute_script(
        "const modal = document.querySelector('.modal.show');"
        "const b = [...modal.querySelectorAll('button')].find(x =>"
        "  (x.innerText || '').trim() === 'Save');"
        "if (b) b.click(); return !!b;"
    )
    page.pace(8.0)
    print("[save] state setelah Save:", dump_state(), flush=True)
    print("[save] console error:",
          [e.get("message", "")[:140] for e in driver.get_log("browser")[-6:]],
          flush=True)

    # bersihkan: tutup paksa + Cancel
    try:
        page.batal_form()
    except Exception:
        driver.execute_script(
            "document.querySelectorAll('.modal.show, .modal-backdrop')"
            ".forEach(m => m.remove());"
        )
    print("[SELESAI]", flush=True)
finally:
    driver.quit()
