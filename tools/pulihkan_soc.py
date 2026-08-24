"""
tools/pulihkan_soc.py
=====================
Hapus baris draft kosong yang nyangkut di SOC dari percobaan Create
sebelumnya (pakai helper _hapus_baris_kosong + konfirmasi Ya).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from config import config
from pages.hss_safety_page import HssSafetyPage

opt = Options()
opt.add_argument("--start-maximized")
opt.add_argument(f"--user-data-dir={config.CHROME_PROFILE_PATH}")
opt.add_experimental_option("excludeSwitches", ["enable-automation"])
driver = webdriver.Chrome(options=opt)
driver.implicitly_wait(0)
page = HssSafetyPage(driver)
page.buka_halaman("soc_recapitulation")

sebelum = driver.execute_script(
    "const t = " + page.JS_GRID + ";"
    "return t ? t.querySelectorAll('tbody tr').length : -1;"
)
print("jumlah baris sebelum:", sebelum)

page._hapus_baris_kosong()
page.tunggu_processing_selesai()
page.buka_halaman("soc_recapitulation")

sesudah = driver.execute_script(
    "const t = " + page.JS_GRID + ";"
    "return t ? t.querySelectorAll('tbody tr').length : -1;"
)
print("jumlah baris sesudah:", sesudah)

driver.quit()
print("selesai")
