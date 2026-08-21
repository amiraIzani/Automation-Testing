"""Cek cepat: kelas lengkap semua tabel Master Alat + yang match table.reportData (hapus nanti)."""
import sys
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

driver = webdriver.Chrome(options=options)
driver.implicitly_wait(0)

try:
    SafetyMasterAlatKeselamatanOperasiPage(driver).buka()
    info = driver.execute_script(
        "return [...document.querySelectorAll('table')].map((t, i) => ({"
        "  i: i, id: t.id, cls: (t.className||'').toString(),"
        "  rows: t.querySelectorAll('tbody tr').length,"
        "  matchReportData: t.classList.contains('reportData'),"
        "  dataTable: t.classList.contains('dataTable'),"
        "  thNames: [...t.querySelectorAll('th')].map(h => h.getAttribute('data-name')).filter(Boolean).slice(0,8)"
        "}));"
    )
    for t in info:
        print(t)
    print()
    print("querySelector('table.reportData') ->", driver.execute_script(
        "const t = document.querySelector('table.reportData');"
        "return t ? {id: t.id, rows: t.querySelectorAll('tbody tr').length} : null;"
    ))
    print("querySelector('table.dataTable') ->", driver.execute_script(
        "const t = document.querySelector('table.dataTable');"
        "return t ? {id: t.id, rows: t.querySelectorAll('tbody tr').length} : null;"
    ))
    print("ISI tableData_1889 (per baris):", driver.execute_script(
        "const t = document.querySelector('#tableData_1889');"
        "return t ? [...t.querySelectorAll('tbody tr')].map(tr =>"
        "  (tr.innerText||'').replace(/\\n/g, ' | ')) : null;"
    ))
    print("HTML BARIS PERTAMA:", driver.execute_script(
        "const tr = document.querySelector('#tableData_1889 tbody tr');"
        "return tr ? tr.innerHTML.slice(0, 700) : null;"
    ))
finally:
    driver.quit()
