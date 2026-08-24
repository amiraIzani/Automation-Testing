"""
tools/cek_baca.py
=================
Cek kenapa baca_sel_grid('PenyakitAkibatKerja', 0) kosong di Statistic:
dump input baris pertama (data-fieldname + value) sebelum & sesudah
reset_cari_grid, dengan jeda berbeda.
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
page.buka_halaman("statistic_safety_recapitulation")


def dump(tag):
    info = driver.execute_script(
        "const t = [...document.querySelectorAll('table.reportData')]"
        ".find(t => t.querySelectorAll('tbody tr').length > 0);"
        "if (!t) return 'tidak ada tabel';"
        "const row0 = t.querySelector('tbody tr');"
        "if (!row0) return 'tidak ada baris';"
        "const ins = [...row0.querySelectorAll('input')].map(i =>"
        "  i.getAttribute('data-fieldname') + '=' + i.value);"
        "return {jumlahInput: ins.length, fields: ins};"
    )
    log(f"{tag}: {dump.__doc__ and ''}{info}")


dump("langsung setelah buka")
log("baca PenyakitAkibatKerja: " + repr(page.baca_sel_grid("PenyakitAkibatKerja", 0)))

page.reset_cari_grid()
dump("setelah reset_cari_grid")
log("baca PenyakitAkibatKerja: " + repr(page.baca_sel_grid("PenyakitAkibatKerja", 0)))

time.sleep(2)
dump("setelah reset + 2 detik")
log("baca PenyakitAkibatKerja: " + repr(page.baca_sel_grid("PenyakitAkibatKerja", 0)))

# cek apakah input input[data-fieldname] ada tapi value kosong
kosong = driver.execute_script(
    "return document.querySelectorAll(\"input[data-fieldname='PenyakitAkibatKerja']\").length;"
)
log("jumlah input PenyakitAkibatKerja di DOM: " + str(kosong))

driver.quit()
with open(os.path.join(config.REPORTS_DIR, "cek_baca.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(out))
print("selesai")
