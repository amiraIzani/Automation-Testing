"""Diagnosa alur create Master Alat: pantau XHR Save/Submit + semua tabel (hapus nanti)."""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from config import config
from pages.safety_master_alat_keselamatan_operasi_page import SafetyMasterAlatKeselamatanOperasiPage

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
options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

driver = webdriver.Chrome(options=options)
driver.implicitly_wait(0)

def xhr_baru():
    """List XHR POST/GET ke server (bukan static) sejak terakhir dipanggil."""
    out = []
    for entry in driver.get_log("performance"):
        msg = json.loads(entry["message"])["message"]
        if msg["method"] == "Network.responseReceived":
            url = msg["params"]["response"]["url"]
            if any(k in url for k in ("/Timesheet/", "/Master/", "/api/", "/Reporting/")):
                status = msg["params"]["response"]["status"]
                out.append((msg["params"]["response"].get("mimeType", "")[:12],
                            status, url[:160]))
    return out

def tabelan():
    return driver.execute_script(
        "return [...document.querySelectorAll('table')].map(t => ({"
        "  id: t.id, cls: (t.className||'').toString().slice(0,40),"
        "  rows: t.querySelectorAll('tbody tr').length}))"
    )

try:
    equip = "AUTO-TEST-" + time.strftime("%H%M%S")
    page = SafetyMasterAlatKeselamatanOperasiPage(driver).buka()
    print("TABEL AWAL:", tabelan())

    page.buka_form_create()
    page.isi_form_create_otomatis(tambahan={"Equipment No": equip})
    print("isi form selesai; Location =", page.baca_lookup("Location"), "Type =", page.baca_lookup("Type"))
    page.simpan_form()
    print("SAVE selesai. TABEL:", tabelan())
    print("XHR setelah SAVE:", xhr_baru())

    page.submit_changes()
    page.tunggu_processing_selesai()
    time.sleep(2)
    print("SUBMIT selesai. TABEL:", tabelan())
    print("XHR setelah SUBMIT:", xhr_baru())

    for val in ("AP01", "AT01", "AT10"):
        page.pilih_unit(val)
        page.reload_data()
        ada = page.tabel_berisi(equip, timeout=8)
        print(f"unit {val} -> berisi '{equip}': {ada}")
finally:
    driver.quit()
