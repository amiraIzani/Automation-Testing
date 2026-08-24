"""Cek apakah baris draft kosong nyangkut di SERVER atau hanya di
storage browser profil selenium (debug sementara -- hapus setelah
hijau).

    python tools/cek_draft.py

Buka halaman dengan profil FRESH (bukan profil selenium) -- login
tidak ada (cookie B2C tidak ada di profil baru), jadi halaman akan
minta login; yang penting hanya: dump localStorage/sessionStorage
profil selenium (kalau ada draft di storage) + coba lihat grid.
"""
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from config import config
from pages.hss_safety_page import HssSafetyPage

KUNCI = sys.argv[1] if len(sys.argv) > 1 else "incident_investigation_form"

# 1) buka dengan profil selenium -> dump storage + grid
opt = Options()
opt.add_argument("--start-maximized")
opt.add_argument(f"--user-data-dir={config.CHROME_PROFILE_PATH}")
opt.add_argument("--disable-notifications")
opt.add_experimental_option("excludeSwitches", ["enable-automation"])
driver = webdriver.Chrome(options=opt)
driver.implicitly_wait(0)
page = HssSafetyPage(driver)

page.buka_halaman(KUNCI)
time.sleep(3)
storage = driver.execute_script(
    "const out = {};"
    "for (const k of Object.keys(window.localStorage || {}))"
    "  out['local:' + k] = (window.localStorage.getItem(k) || '').slice(0, 120);"
    "for (const k of Object.keys(window.sessionStorage || {}))"
    "  out['session:' + k] = (window.sessionStorage.getItem(k) || '').slice(0, 120);"
    "return out;"
)
print("== storage profil selenium ==")
for k, v in storage.items():
    print(f"  {k}: {v}")
grid = driver.execute_script(
    f"const t = {page.JS_GRID};"
    "return t ? {baris: t.querySelectorAll('tbody tr').length} : {baris: -1};"
)
print("grid profil selenium:", grid)
driver.quit()

# 2) buka dengan profil FRESH (temp) -> grid akan minta login; tetap
#    lihat apakah draft muncul setelah login otomatis (redirect).
opt2 = Options()
opt2.add_argument("--start-maximized")
opt2.add_argument(f"--user-data-dir={config.CHROME_PROFILE_PATH}_fresh_probe")
opt2.add_argument("--disable-notifications")
opt2.add_experimental_option("excludeSwitches", ["enable-automation"])
driver2 = webdriver.Chrome(options=opt2)
driver2.implicitly_wait(0)
try:
    driver2.get(config.BASE_URL + "Reporting/Timesheet/DailyReport/Edit?Id=1334")
    for _ in range(30):
        time.sleep(1)
        url = driver2.current_url
        if "Dashboard" in url or "Login" in url or "login" in url:
            break
    print("profil fresh -> URL:", driver2.current_url)
except Exception as exc:
    print("profil fresh error:", exc)
finally:
    driver2.quit()
