"""
tools/cek_edit.py
=================
Cek alur inline-edit -> Submit Changes -> verifikasi -> revert di
halaman SMKP (Id=1307) PAKAI helper asli page object (isi_sel_grid /
edit_dan_submit / baca_sel_grid) supaya hasilnya = hasil test asli.
"""
import os
import sys

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
log("URL: " + driver.current_url)

nilai_awal = page.baca_sel_grid("Deskripsi", baris=0)
log("nilai awal Deskripsi row0: " + str(nilai_awal))

# ubah -> submit -> verifikasi nilai baru tampil
page.edit_dan_submit("Deskripsi", "AUTO-TEST-EDIT-SMKP")
log("setelah submit: " + str(page.baca_sel_grid("Deskripsi", baris=0)))

# revert -> submit -> verifikasi kembali ke nilai awal
if nilai_awal:
    page.edit_dan_submit("Deskripsi", nilai_awal)
    log("setelah revert: " + str(page.baca_sel_grid("Deskripsi", baris=0)))

driver.quit()
with open(os.path.join(config.REPORTS_DIR, "cek_edit.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(out))
print("selesai")
