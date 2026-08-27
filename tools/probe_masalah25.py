"""Probe #25 (2026-08-27):

Form Incident punya 2 field upload (Lampiran Biaya & Lampiran
Sketsa). Input#imgFile: dibuat per-klik atau dipindah antar group?
-> klik anchor 1, dump lokasi input; klik anchor 2, dump lagi.
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
driver = webdriver.Chrome(options=opt)
driver.implicitly_wait(0)
page = HssSafetyPage(driver)


def dump_inputs():
    return driver.execute_script(
        "return [...document.querySelectorAll('input[type=file]')].map(i => {"
        "  const p = i.parentElement;"
        "  const g = i.closest('.form-group');"
        "  const l = g ? g.querySelector('label') : null;"
        "  return {id: i.id,"
        "    labelGroup: l ? (l.innerText || '').trim().slice(0, 40) : null,"
        "    parentCls: (p.className || '').slice(0, 60)};"
        "});"
    )


def klik_anchor(label_awal):
    driver.execute_script(
        "const modal = document.querySelector('.modal.show');"
        "const g = [...modal.querySelectorAll('.form-group')].find(x => {"
        "  const l = x.querySelector('label');"
        "  return l && l.innerText.indexOf(arguments[0]) === 0;"
        "});"
        "const a = g.querySelector('.dt-input-upload');"
        "a.scrollIntoView({block: 'center'});"
        "a.click(); return true;",
        label_awal,
    )
    page.pace(3.0)


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

    print("[a1] input sebelum klik:", dump_inputs(), flush=True)
    klik_anchor("Lampiran Biaya")
    print("[a1] input setelah klik anchor 1:", dump_inputs(), flush=True)
    klik_anchor("Lampiran Sketsa")
    print("[a2] input setelah klik anchor 2:", dump_inputs(), flush=True)

    print("[SELESAI]", flush=True)
finally:
    driver.quit()
