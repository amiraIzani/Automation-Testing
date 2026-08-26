"""Probe #12 (2026-08-26): matrix export -- apakah export mati di
SEMUA halaman sekarang (server) atau cuma Incident.

Untuk tiap halaman: klik Export -> tunggu 10 dtk -> catat file baru.
"""
import os
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

    for k in ["incident_investigation_form", "master_alat_keselamatan_operasi",
              "smk3", "mwt_daily"]:
        page.buka_halaman(k)
        page.reset_cari_grid()
        page.pace(2.0)
        sebelum = set(os.listdir(config.DOWNLOAD_DIR))
        hasil = []
        for percobaan in range(3):
            try:
                page.export_data()
            except Exception as exc:
                print(f"[{k}] export#{percobaan+1} ERROR "
                      f"{type(exc).__name__}: {exc}", flush=True)
                break
            page.pace(10.0)
            baru = sorted(set(os.listdir(config.DOWNLOAD_DIR)) - sebelum)
            hasil.append(len(baru))
            print(f"[{k}] export#{percobaan+1}: file_baru={len(baru)}", flush=True)
            if baru:
                break
        print(f"[{k}] RINGKAS: {hasil}", flush=True)

    print("[SELESAI]", flush=True)
finally:
    driver.quit()
