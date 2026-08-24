"""
tools/pulihkan_total.py
=======================
Restore menyeluruh halaman Statistic:
1. Dump semua table.reportData (grid utama + template) baris pertama.
2. Set nilai benar (TipePegawai='Pegawai', FirstAidCase='4',
   PenyakitAkibatKerja='1') di baris January Pegawai grid UTAMA DAN di
   baris pertama semua tabel template (diduga ikut tersubmit menimpa
   baris asli).
3. Submit sekali, lalu buka ulang & verifikasi.
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from config import config
from pages.hss_safety_page import HssSafetyPage

TARGET = {"TipePegawai": "Pegawai", "FirstAidCase": "4",
          "PenyakitAkibatKerja": "1"}

opt = Options()
opt.add_argument("--start-maximized")
opt.add_argument(f"--user-data-dir={config.CHROME_PROFILE_PATH}")
opt.add_experimental_option("excludeSwitches", ["enable-automation"])
driver = webdriver.Chrome(options=opt)
driver.implicitly_wait(0)
page = HssSafetyPage(driver)
page.buka_halaman("statistic_safety_recapitulation")

JS_DUMP = (
    "const ts = [...document.querySelectorAll('table.reportData')];"
    "return ts.map((t, i) => ({"
    "  i: i, id: t.id, baris: t.querySelectorAll('tbody tr').length,"
    "  row0: t.querySelector('tbody tr') ?"
    "    [...t.querySelector('tbody tr').querySelectorAll('input')]"
    "      .filter(x => x.value).map(x => x.getAttribute('data-fieldname')"
    "        + '=' + x.value) : null"
    "}));"
)

print("sebelum:")
print(driver.execute_script(JS_DUMP))

# set nilai benar di SEMUA tabel (baris pertama yang cocok pola template
# punya TipePegawai) + grid utama baris January Pegawai
JS_SET = (
    "const target = arguments[0];"
    "const ts = [...document.querySelectorAll('table.reportData')];"
    "ts.forEach(t => {"
    "  const rows = [...t.querySelectorAll('tbody tr')];"
    "  rows.forEach(tr => {"
    "    const month = tr.querySelector(\"input[data-fieldname='Month']\");"
    "    const tipe = tr.querySelector(\"input[data-fieldname='TipePegawai']\");"
    "    const cocok = month && month.value === 'January' && tipe &&"
    "      (tipe.value === 'AUTO-TEST' || tipe.value === 'Pegawai');"
    "    if (!cocok) return;"
    "    Object.entries(target).forEach(([f, v]) => {"
    "      const inp = tr.querySelector(\"input[data-fieldname='\" + f + \"']\");"
    "      if (inp && inp.value !== v) {"
    "        inp.value = v;"
    "        inp.dispatchEvent(new Event('change', {bubbles: true}));"
    "      }"
    "    });"
    "  });"
    "});"
)
driver.execute_script(JS_SET, TARGET)
time.sleep(1)

page.submit_changes()
page.tunggu_processing_selesai()
page._tunggu_tabel()

print("setelah submit:")
print(driver.execute_script(JS_DUMP))

# buka ulang untuk verifikasi state segar
page.buka_halaman("statistic_safety_recapitulation")
print("fresh reload:")
print(driver.execute_script(JS_DUMP))

driver.quit()
print("selesai")
