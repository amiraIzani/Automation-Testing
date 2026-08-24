"""
tools/dump_unit.py
==================
Dump baris Januari (row 0) grid Statistic untuk unit AP01 dan AT02,
untuk memastikan tidak ada perubahan data yang tersisa dari run test
lama (filter unit sempat berpindah saat bug scoping grid).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from config import config
from pages.hss_safety_page import HssSafetyPage

FIELDS = ["Month", "TipePegawai", "JumlahAccidentRingan", "FirstAidCase",
          "MedicalTreatment", "PenyakitAkibatKerja"]

opt = Options()
opt.add_argument("--start-maximized")
opt.add_argument(f"--user-data-dir={config.CHROME_PROFILE_PATH}")
opt.add_experimental_option("excludeSwitches", ["enable-automation"])
driver = webdriver.Chrome(options=opt)
driver.implicitly_wait(0)
page = HssSafetyPage(driver)
page.buka_halaman("statistic_safety_recapitulation")

for value_unit in ("AP01", "AT02", "AT10"):
    page.pilih_unit_by_value(value_unit)
    page.tunggu_processing_selesai()
    rows = driver.execute_script(
        "const t = " + page.JS_GRID + ";"
        "if (!t) return [];"
        "return [...t.querySelectorAll('tbody tr')].slice(0, 2).map(tr => {"
        "  const sel = {};"
        "  tr.querySelectorAll('input').forEach(i => {"
        "    const f = i.getAttribute('data-fieldname');"
        "    if (f) sel[f] = i.value;"
        "  });"
        "  return sel;"
        "});"
    )
    print(f"\nunit {value_unit}:")
    for i, r in enumerate(rows):
        print(" ", i, {f: r.get(f, "-") for f in FIELDS})

# kembalikan ke AT10
page.pilih_unit_by_value("AT10")
driver.quit()
