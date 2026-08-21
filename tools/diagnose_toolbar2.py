"""Diagnosa 2: repro cek tombol + efek FullScreen di Incident Investigation (hapus nanti)."""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from config import config
from pages.safety_incident_investigation_form_page import SafetyIncidentInvestigationFormPage

options = Options()
options.add_argument("--start-maximized")
options.add_argument(f"--user-data-dir={config.CHROME_PROFILE_PATH}")
options.add_argument("--disable-notifications")
options.add_argument("--disable-infobars")
options.add_argument("--no-first-run")
options.add_argument("--no-default-browser-check")
options.add_argument("--disable-session-crashed-bubble")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.set_capability("unhandledPromptBehavior", "accept")

driver = webdriver.Chrome(options=options)
driver.implicitly_wait(0)

try:
    page = SafetyIncidentInvestigationFormPage(driver).buka()

    print("\n===== REPRO: cek_tombol_toolbar 3x (halaman baru tiap kali) =====")
    for i in range(3):
        p2 = SafetyIncidentInvestigationFormPage(driver).buka()
        hasil = p2.cek_tombol_toolbar("incident_investigation_form", timeout=8)
        hilang = [n for n, ok in hasil.items() if not ok]
        print(f"  iterasi {i}: hilang={hilang}")

    print("\n===== FULLSCREEN: klik lalu dump state =====")
    p3 = SafetyIncidentInvestigationFormPage(driver).buka()

    def dump_state(tag):
        st = driver.execute_script(
            "const b = document.querySelector('.fullscreen-button');"
            "const panel = b ? b.closest('.panel') : null;"
            "return {"
            "  btnText: b ? (b.innerText||'').trim() : null,"
            "  panelCls: panel ? panel.className : null,"
            "  panelContainerCls: panel ? (panel.querySelector('.panel-container')||{}).className : null,"
            "  bodyCls: document.body.className,"
            "  anyFullscreenCls: [...document.querySelectorAll('*')].filter(e => (e.className||'').toString().toLowerCase().includes('fullscreen')).slice(0,5).map(e => e.tagName+'.'+(e.className||'').toString().slice(0,50)),"
            "  winW: window.innerWidth, winH: window.innerHeight,"
            "  panelRect: panel ? (() => {const r = panel.getBoundingClientRect(); return [Math.round(r.width), Math.round(r.height)]})() : null,"
            "};"
        )
        print(f"  [{tag}] {st}")

    dump_state("sebelum klik")
    p3.toggle_fullscreen()
    dump_state("sesudah klik 1")
    p3.toggle_fullscreen()
    dump_state("sesudah klik 2 (kembali)")

finally:
    driver.quit()
