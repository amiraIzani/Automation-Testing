"""
tools/cek_soc2.py
=================
Cek grid SOC: apakah ada baris kosong (draft) yang nyangkut dari
percobaan Create, + tombol aksi apa yang tersedia per baris.
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

info = driver.execute_script(
    "const t = " + page.JS_GRID + ";"
    "if (!t) return 'tidak ada grid';"
    "const rows = [...t.querySelectorAll('tbody tr')];"
    "return {"
    "  jumlah: rows.length,"
    "  ringkasan: rows.map(tr => {"
    "    const vals = [...tr.querySelectorAll('input')].map(i => i.value)"
    "      .filter(v => v !== '');"
    "    const aksi = [...tr.querySelectorAll('td:last-child a')]"
    "      .map(a => a.getAttribute('title'));"
    "    return {terisi: vals.length, aksi: aksi,"
    "      teks: tr.innerText.slice(0, 80)};"
    "  }).slice(0, 15)"
    "};"
)
print(info)

driver.quit()
