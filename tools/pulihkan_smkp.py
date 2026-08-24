"""
tools/pulihkan_smkp.py
======================
Kembalikan nilai Deskripsi baris pertama halaman SMKP yang sempat
diubah oleh probe (AUTO-TEST-EDIT-SMKP) ke nilai aslinya.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from config import config
from pages.hss_safety_page import HssSafetyPage

ASLI = "Tinjauan manajemen dilakukan dengan komite"

opt = Options()
opt.add_argument("--start-maximized")
opt.add_argument(f"--user-data-dir={config.CHROME_PROFILE_PATH}")
opt.add_experimental_option("excludeSwitches", ["enable-automation"])
driver = webdriver.Chrome(options=opt)
driver.implicitly_wait(0)

page = HssSafetyPage(driver)
page.buka_halaman("smkp")
nilai = page.baca_sel_grid("Deskripsi", baris=0)
print("nilai sekarang:", nilai)
if nilai != ASLI:
    page.edit_dan_submit("Deskripsi", ASLI)
    print("setelah restore:", page.baca_sel_grid("Deskripsi", baris=0))
else:
    print("sudah asli, tidak perlu restore")

driver.quit()
print("selesai")
