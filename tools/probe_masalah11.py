"""Probe #11 (2026-08-26):

1) SMK3 & SMKP: dump nilai input[data-fieldname='Month'] semua baris
   + nilai filter tanggal -- cek kenapa anchor {'Month': 'Juli'}
   tidak ketemu.
2) Statistic: export -> dump HTML/teks modal yang nyangkut -> navigasi
   ke Incident Investigation -> cek apakah modal masih ada (SPA
   global?) -> coba export incident.
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

def dump_modal():
    return driver.execute_script(
        "const out = [];"
        "document.querySelectorAll('.modal, .bootbox').forEach(m => {"
        "  const s = window.getComputedStyle(m);"
        "  const r = m.getBoundingClientRect();"
        "  if (s.display !== 'none' && r.width > 0)"
        "    out.push({cls: (m.className||'').toString().slice(0,90),"
        "              teks: (m.innerText||'').replace(/\\s+/g,' ').trim().slice(0,200)});"
        "});"
        "return out;"
    )

try:
    LoginPage(driver).login()
    print("[OK] login", flush=True)

    # 1) smk3 + smkp: nilai Month di grid
    for k in ["smk3", "smkp"]:
        page.buka_halaman(k)
        page.reset_cari_grid()
        page.pace(3.0)
        baris = driver.execute_script(
            f"const t = {page.JS_GRID};"
            "if (!t) return [];"
            "return [...t.querySelectorAll('tbody tr')].map(r => {"
            "  const i = r.querySelector(\"input[data-fieldname='Month']\");"
            "  return i ? i.value : ('[tidak ada input Month] '"
            "    + (r.innerText||'').slice(0, 40));"
            "});"
        )
        f = driver.execute_script(
            "const el = document.querySelector('#tbDate');"
            "return el ? el.value : null;"
        )
        print(f"[{k}] filter={f!r} barisMonth={baris}", flush=True)

    # 2) statistic export -> modal nyangkut -> ke incident
    page.buka_halaman("statistic_safety_recapitulation")
    page.reset_cari_grid()
    page.pace(2.0)
    sebelum = set(os.listdir(config.DOWNLOAD_DIR))
    print("[statistik] klik export...", flush=True)
    try:
        page.export_data()
    except Exception as exc:
        print(f"[statistik] export ERROR {type(exc).__name__}: {exc}",
              flush=True)
    page.pace(8.0)
    baru = sorted(set(os.listdir(config.DOWNLOAD_DIR)) - sebelum)
    print(f"[statistik] file_baru={[os.path.basename(b) for b in baru]}",
          flush=True)
    print(f"[statistik] modal: {dump_modal()}", flush=True)

    # navigasi ke incident -- modal ikut? export jalan?
    page.buka_halaman("incident_investigation_form")
    page.pace(2.0)
    print(f"[incident] modal SETELAH navigasi: {dump_modal()}", flush=True)
    sebelum2 = set(os.listdir(config.DOWNLOAD_DIR))
    try:
        page.export_data()
    except Exception as exc:
        print(f"[incident] export ERROR {type(exc).__name__}: {exc}",
              flush=True)
    page.pace(8.0)
    baru2 = sorted(set(os.listdir(config.DOWNLOAD_DIR)) - sebelum2)
    print(f"[incident] file_baru={[os.path.basename(b) for b in baru2]} "
          f"modal={dump_modal()}", flush=True)

    print("[SELESAI]", flush=True)
finally:
    driver.quit()
