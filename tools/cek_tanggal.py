"""Cek filter tanggal halaman DailyReport (Incident Id=1334): nilai
tbDate saat buka, jumlah baris grid, dan efek set tanggal (debug
sementara -- hapus setelah hijau).

    python tools/cek_tanggal.py
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

opt = Options()
opt.add_argument("--start-maximized")
opt.add_argument(f"--user-data-dir={config.CHROME_PROFILE_PATH}")
opt.add_argument("--disable-notifications")
opt.add_experimental_option("excludeSwitches", ["enable-automation"])
driver = webdriver.Chrome(options=opt)
driver.implicitly_wait(0)
page = HssSafetyPage(driver)

page.buka_halaman("incident_investigation_form")
time.sleep(2)
tb = driver.execute_script(
    "const el = document.querySelector('#tbDate');"
    "return el ? {val: el.value, tipe: el.getAttribute('type'),"
    " tampil: el.getBoundingClientRect().height > 0} : null;"
)
print("tbDate:", tb)
print("grid:", driver.execute_script(
    f"const t = {page.JS_GRID};"
    "return t ? t.querySelectorAll('tbody tr').length : -1;"
))

# coba set tanggal hari ini
try:
    page.set_filter_tanggal("2026-08-20")
    print("tanggal diset ke 2026-08-20")
except Exception as exc:
    print("set tanggal gagal:", repr(exc)[:150])
time.sleep(4)
print("tbDate setelah set:", driver.execute_script(
    "const el = document.querySelector('#tbDate');"
    "return el ? el.value : null;"
))
print("grid setelah set:", driver.execute_script(
    f"const t = {page.JS_GRID};"
    "return t ? t.querySelectorAll('tbody tr').length : -1;"
))
driver.quit()
