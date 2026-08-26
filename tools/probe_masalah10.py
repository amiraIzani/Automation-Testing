"""Probe #10 (2026-08-26): witness create dengan No. Insiden ASLI.

1) Baca nilai NoInsiden baris pertama halaman Incident Investigation.
2) Witness: buka form create -> isi otomatis + No. Insiden = nilai
   asli -> save -> submit -> cek penanda tampil di grid.
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

try:
    LoginPage(driver).login()
    print("[OK] login", flush=True)

    # 1) baca NoInsiden asli dari halaman incident
    page.buka_halaman("incident_investigation_form")
    page.reset_cari_grid()
    page.pace(2.0)
    nilai = driver.execute_script(
        f"const t = {page.JS_GRID};"
        "if (!t) return null;"
        "const i = t.querySelector(\"input[data-fieldname='NoInsiden']\");"
        "return i ? i.value : null;"
    )
    print(f"[incident] NoInsiden baris pertama: {nilai!r}", flush=True)
    # juga jumlah baris di tab Data Insiden
    n = driver.execute_script(
        f"const t = {page.JS_GRID};"
        "return t ? t.querySelectorAll('tbody tr').length : -1;"
    )
    print(f"[incident] jumlah baris grid: {n}", flush=True)

    if nilai:
        # 2) witness create dengan NoInsiden asli
        page.buka_halaman("witness_statement_report")
        page.buka_form_create()
        page.pace(1.0)
        page.isi_form_create_otomatis(
            penanda="PROBE10", tambahan={"No. Insiden": nilai}
        )
        page.simpan_form()
        page.submit_changes()
        page.tunggu_processing_selesai()
        page.pace(3.0)
        ada = driver.execute_script(
            f"const t = {page.JS_GRID};"
            "return t ? t.innerText.includes('PROBE10') : false;"
        )
        n2 = driver.execute_script(
            f"const t = {page.JS_GRID};"
            "return t ? t.querySelectorAll('tbody tr').length : -1;"
        )
        print(f"[witness] setelah create dgn NoInsiden asli: "
              f"adaPROBE10={ada} baris={n2}", flush=True)
    else:
        print("[witness] TIDAK ada NoInsiden di halaman incident -- "
              "hipotesis batal", flush=True)

    print("[SELESAI]", flush=True)
finally:
    driver.quit()
