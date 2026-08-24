"""
tools/cek_soc.py
================
Reproduksi urutan coba_tombol di SOC Recapitulation sampai Create with
Form, untuk tahu kenapa modal tidak terbuka.
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
page.buka_halaman("soc_recapitulation")

page.reload_data()
log("setelah reload ok, url: " + driver.current_url)

log("klik create lalu batal...")
hasil = page.klik_create_lalu_batal()
log("create->batal hasil: " + str(hasil) + " url: " + driver.current_url)

log("buka form create...")
try:
    page.buka_form_create()
    log("form create TERBUKA")
    page.batal_form()
except Exception as exc:
    log("form create GAGAL: " + repr(exc))
    info = driver.execute_script(
        "return [...document.querySelectorAll('.modal')].map(function(m) {"
        "  const s = window.getComputedStyle(m);"
        "  const r = m.getBoundingClientRect();"
        "  return {id: m.id, cls: m.className,"
        "    tampil: s.display !== 'none' && s.visibility !== 'hidden'"
        "      && r.height > 0};"
        "});"
    )
    log("modal: " + str(info))
    log("url: " + driver.current_url)

driver.quit()
with open(os.path.join(config.REPORTS_DIR, "cek_soc.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(out))
print("selesai")
