"""
tools/dump_statistik.py
=======================
Dump SEMUA baris grid utama Statistic (Month, TipePegawai + 4 field
yang sempat tersentuh test) untuk dibandingkan dengan scan asli.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from config import config
from pages.hss_safety_page import HssSafetyPage

FIELDS = ["Month", "TipePegawai", "JumlahAccidentRingan",
          "JumlahAccidentBerat", "JumlahAccidentMati", "FirstAidCase",
          "MedicalTreatment", "PenyakitAkibatKerja", "MonthInt"]

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
    "return [...t.querySelectorAll('tbody tr')].map(tr => {"
    "  const sel = {};"
    "  tr.querySelectorAll('input').forEach(i => {"
    "    const f = i.getAttribute('data-fieldname');"
    "    if (f) sel[f] = i.value;"
    "  });"
    "  return sel;"
    "});"
)

print("jumlah baris:", len(rows))
for i, r in enumerate(rows):
    print(i, {f: r.get(f, "-") for f in FIELDS})

driver.quit()
