"""
tools/cek_tutup.py
==================
Reproduksi kegagalan tutup modal di SMKP lewat urutan coba_tombol:
reload_data() -> buka_modal_import() -> dump modal -> tutup_modal().
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from config import config
from pages.hss_safety_page import HssSafetyPage

out = []


def log(t):
    print(t, flush=True)
    out.append(str(t))


opt = Options()
opt.add_argument("--start-maximized")
opt.add_argument(f"--user-data-dir={config.CHROME_PROFILE_PATH}")
opt.add_experimental_option("excludeSwitches", ["enable-automation"])
driver = webdriver.Chrome(options=opt)
driver.implicitly_wait(0)
page = HssSafetyPage(driver)
page.buka_halaman("smkp")

page.reload_data()
log("setelah reload, modal tampil: " + str(page._ada_modal_tampil()))

page.buka_modal_import()
log("setelah buka import, modal tampil: " + str(page._ada_modal_tampil()))

info = driver.execute_script(
    "return [...document.querySelectorAll('.modal')].map(function(m) {"
    "  const s = window.getComputedStyle(m);"
    "  const r = m.getBoundingClientRect();"
    "  return {id: m.id, cls: m.className,"
    "    tampil: s.display !== 'none' && s.visibility !== 'hidden'"
    "      && r.height > 0};"
    "});"
)
log("semua modal: " + str(info))

try:
    page.tutup_modal()
    log("tutup_modal SUKSES")
except Exception as exc:
    log("tutup_modal GAGAL: " + repr(exc))
    info2 = driver.execute_script(
        "return [...document.querySelectorAll('.modal')].map(function(m) {"
        "  const s = window.getComputedStyle(m);"
        "  const r = m.getBoundingClientRect();"
        "  return {id: m.id, cls: m.className,"
        "    tampil: s.display !== 'none' && s.visibility !== 'hidden'"
        "      && r.height > 0};"
        "});"
    )
    log("modal tersisa: " + str(info2))

driver.quit()
with open(os.path.join(config.REPORTS_DIR, "cek_tutup.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(out))
print("selesai")
