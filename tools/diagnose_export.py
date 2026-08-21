"""Pantau visibilitas toolbar Master Alat per detik setelah buka (hapus nanti)."""
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

driver = webdriver.Chrome(options=options)
driver.implicitly_wait(0)

def pantau(tag):
    return driver.execute_script(
        "const vis = sel => {"
        "  const el = document.querySelector(sel);"
        "  if (!el) return 'TIDAK ADA';"
        "  const s = window.getComputedStyle(el); const r = el.getBoundingClientRect();"
        "  return (s.display !== 'none' && s.visibility !== 'hidden'"
        "          && r.width > 0 && r.height > 0) ? 'tampil' : 'hidden';"
        "};"
        "const proc = vis('.dataTables_processing');"
        "return 'reload=' + vis('#btnReloadData') + ' export=' + vis('#btnExport')"
        "     + ' submit=' + vis('#btnSubmit') + ' processing=' + proc;"
    )

try:
    page = SafetyMasterAlatKeselamatanOperasiPage(driver).buka()
    print(pantau(0))
    dump = driver.execute_script(
        "return [...document.querySelectorAll('[id]')]"
        "  .filter(e => /btn|reload/i.test(e.id))"
        "  .map(e => {"
        "    const s = window.getComputedStyle(e); const r = e.getBoundingClientRect();"
        "    const vis = s.display !== 'none' && s.visibility !== 'hidden'"
        "            && r.width > 0 && r.height > 0;"
        "    return {id: e.id, tag: e.tagName, teks: (e.innerText||'').trim().slice(0,25),"
        "            vis: vis, cls: (e.className||'').toString().slice(0,40)};"
        "  });"
    )
    for d in dump:
        print(d)
    print("HTML btnReloadData:", driver.execute_script(
        "const e = document.querySelector('#btnReloadData');"
        "return e ? e.outerHTML.slice(0, 400) : 'TIDAK ADA';"
    ))
    print("parent HTML:", driver.execute_script(
        "const e = document.querySelector('#btnReloadData');"
        "return e && e.parentElement ? e.parentElement.outerHTML.slice(0, 500) : 'TIDAK ADA';"
    ))
finally:
    driver.quit()
