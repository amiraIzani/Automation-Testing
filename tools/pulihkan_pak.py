"""
tools/pulihkan_pak.py
=====================
Restore PenyakitAkibatKerja baris January Pegawai (Statistic) ke '1'
(nilai asli scan 2026-08-20) + verifikasi baris Juli (anchor yang
dipakai test).
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
page.buka_halaman("statistic_safety_recapitulation")

# 1) restore January Pegawai PAK -> 1
anchor_jan = {"Month": "January", "TipePegawai": "Pegawai"}
sekarang = page.baca_sel_grid_anchor("PenyakitAkibatKerja", anchor_jan)
print("January Pegawai PAK sekarang:", repr(sekarang))
if sekarang != "1":
    page.isi_sel_grid_anchor("PenyakitAkibatKerja", "1", anchor_jan)
    page.submit_changes()
    page.tunggu_processing_selesai()
    page._tunggu_tabel()
    print("setelah restore:", repr(page.baca_sel_grid_anchor("PenyakitAkibatKerja", anchor_jan)))

# 2) verifikasi baris July Pegawai (anchor test)
anchor_jul = {"Month": "July", "TipePegawai": "Pegawai"}
print("July Pegawai PAK:", repr(page.baca_sel_grid_anchor("PenyakitAkibatKerja", anchor_jul)))
print("July Pegawai MedicalTreatment:", repr(page.baca_sel_grid_anchor("MedicalTreatment", anchor_jul)))

driver.quit()
print("selesai")
