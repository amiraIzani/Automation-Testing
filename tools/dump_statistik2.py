"""
tools/dump_statistik2.py
========================
Dump grid Statistic LENGKAP dengan data-rowindex + kolom kunci untuk
mendeteksi residu perubahan dari run test sebelumnya.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from config import config
from pages.hss_safety_page import HssSafetyPage

FIELDS = ["Month", "TipePegawai", "FirstAidCase", "MedicalTreatment",
          "Nearmiss", "PenyakitAkibatKerja", "MonthInt"]

opt = Options()
opt.add_argument("--start-maximized")
opt.add_argument(f"--user-data-dir={config.CHROME_PROFILE_PATH}")
opt.add_experimental_option("excludeSwitches", ["enable-automation"])
driver = webdriver.Chrome(options=opt)
driver.implicitly_wait(0)
page = HssSafetyPage(driver)
page.buka_halaman("statistic_safety_recapitulation")

rows = driver.execute_script(
    "const t = " + page.JS_GRID + ";"
    "if (!t) return [];"
    "return [...t.querySelectorAll('tbody tr')].map((tr, domIdx) => {"
    "  const sel = {};"
    "  tr.querySelectorAll('input').forEach(i => {"
    "    const f = i.getAttribute('data-fieldname');"
    "    if (f) sel[f] = i.value;"
    "    if (f === 'Month') sel['_ri'] = i.getAttribute('data-rowindex');"
    "  });"
    "  sel['_dom'] = domIdx;"
    "  return sel;"
    "});"
)

print("jumlah baris:", len(rows))
for r in rows:
    print(r.get("_dom"), "ri=" + str(r.get("_ri")),
          {f: r.get(f, "-") for f in FIELDS})

driver.quit()
