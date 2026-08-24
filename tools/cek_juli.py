"""
tools/cek_juli.py
=================
Cek & (kalau perlu) restore baris July Pegawai Statistic setelah
kegagalan edit test -- apakah '2' tersimpan ke server?
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

anchor = {"Month": "July", "TipePegawai": "Pegawai"}
sekarang = page.baca_sel_grid_anchor("PenyakitAkibatKerja", anchor)
print("July Pegawai PAK:", repr(sekarang))
if sekarang not in ("1", ""):
    page.isi_sel_grid_anchor("PenyakitAkibatKerja", "1", anchor)
    page.submit_changes()
    page.tunggu_processing_selesai()
    page._tunggu_tabel()
    print("setelah restore:", repr(page.baca_sel_grid_anchor("PenyakitAkibatKerja", anchor)))

# juga cek nilai2 lain baris July Pegawai
for f in ("Month", "TipePegawai", "FirstAidCase", "MedicalTreatment", "Nearmiss"):
    print(f, "=", repr(page.baca_sel_grid_anchor(f, anchor)))

driver.quit()
print("selesai")
