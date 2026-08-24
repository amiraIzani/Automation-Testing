"""
tools/pulihkan_statistik.py
===========================
Kembalikan 4 sel baris Januari Pegawai di halaman Statistic Safety
Recapitulation yang sempat berubah karena bug scoping grid (helper
lama salah sasaran ke tabel template):
  TipePegawai        'AUTO-TEST' -> 'Pegawai'
  JumlahAccidentRingan  ''      -> '1'
  FirstAidCase         ''      -> '4'
  PenyakitAkibatKerja  ''      -> '1'
(nilai asli dari scan website 2026-08-20)
Semua diisi dulu, lalu Submit SEKALI, lalu verifikasi.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from config import config
from pages.hss_safety_page import HssSafetyPage

RESTORE = {
    "TipePegawai": "Pegawai",
    "JumlahAccidentRingan": "1",
    "FirstAidCase": "4",
    "PenyakitAkibatKerja": "1",
}

opt = Options()
opt.add_argument("--start-maximized")
opt.add_argument(f"--user-data-dir={config.CHROME_PROFILE_PATH}")
opt.add_experimental_option("excludeSwitches", ["enable-automation"])
driver = webdriver.Chrome(options=opt)
driver.implicitly_wait(0)
page = HssSafetyPage(driver)
page.buka_halaman("statistic_safety_recapitulation")
page.reset_cari_grid()

for field, nilai in RESTORE.items():
    sekarang = page.baca_sel_grid(field, baris=0)
    print(f"{field}: sekarang={sekarang!r} target={nilai!r}")
    if sekarang != nilai:
        page.isi_sel_grid(field, nilai, baris=0)

# submit sekali untuk semua perubahan
page.submit_changes()
page.tunggu_processing_selesai()
page._tunggu_tabel()

ok = True
for field, nilai in RESTORE.items():
    sekarang = page.baca_sel_grid(field, baris=0)
    print(f"verifikasi {field}: {sekarang!r}")
    if sekarang != nilai:
        ok = False
print("SELESAI -", "SEMUA KEMBALI NORMAL" if ok else "MASIH ADA YANG BERBEDA")

driver.quit()
