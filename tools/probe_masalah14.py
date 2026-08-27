"""Probe #14 (2026-08-27):

smk3/smkp: cek kenapa wait `baca_sel_grid_anchor(field, anchor) != ''`
tidak pernah terpenuhi (run 2026-08-27 09:00). Dump per baris:
nilai input Month + nilai input field target + jumlah baris.

kemungkinan: field target (PPkomKetidaksesuaianMaj / Deskripsi) di
baris Juli KOSONG sekarang (data DEV berubah), padahal anchor Month
ketemu -- wait-nya mensyaratkan field non-kosong sehingga timeout.
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from config import config
from pages.hss_safety_page import HssSafetyPage
from pages.login_page import LoginPage

opt = Options()
opt.add_argument("--start-maximized")
opt.add_argument(f"--user-data-dir={config.CHROME_PROFILE_PATH}")
opt.add_argument("--disable-notifications")
opt.add_experimental_option("excludeSwitches", ["enable-automation"])
opt.add_experimental_option(
    "prefs",
    {
        "download.default_directory": config.DOWNLOAD_DIR,
        "download.prompt_for_download": False,
    },
)
driver = webdriver.Chrome(options=opt)
driver.implicitly_wait(0)
page = HssSafetyPage(driver)

KASUS = [
    ("smk3", "PPkomKetidaksesuaianMaj"),
    ("smkp", "Deskripsi"),
]

try:
    LoginPage(driver).login()
    print("[OK] login", flush=True)

    for k, field in KASUS:
        page.buka_halaman(k)
        page.reset_cari_grid()
        page.pace(3.0)
        dump = driver.execute_script(
            f"const t = {page.JS_GRID};"
            "if (!t) return {baris: -1, data: []};"
            "const baris = [...t.querySelectorAll('tbody tr')];"
            "const data = baris.map(r => {"
            "  const m = r.querySelector(\"input[data-fieldname='Month']\");"
            "  const f = r.querySelector("
            "    \"input[data-fieldname='\" + arguments[0] + \"']\");"
            "  return {Month: m ? m.value : ('[no input] '"
            "    + (r.innerText||'').slice(0,30)),"
            "    field: f ? f.value : '[TIDAK ADA INPUT]'};"
            "});"
            "return {baris: baris.length, data: data};",
            field,
        )
        print(f"[{k}] jumlah_baris={dump['baris']}", flush=True)
        for i, b in enumerate(dump["data"]):
            print(f"[{k}]   baris{i}: Month={b['Month']!r} "
                  f"{field}={b['field']!r}", flush=True)

    print("[SELESAI]", flush=True)
finally:
    driver.quit()
