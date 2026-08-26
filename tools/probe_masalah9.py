"""Probe #9 (2026-08-26):

1) MASTER ALAT delete: klik delete -> YES -> tunggu 20 DETIK (kasih
   waktu AJAX delete server) -> reload -> hitung. Uji apakah delete
   cuma lambat atau memang tidak commit.
2) WITNESS: create dummy -> submit -> sweep SEMUA opsi cbDistrict satu
   per satu -> hitung baris grid. Cari district mana yang memuat baris
   baru (kalau ada).
"""
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select

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

def jumlah_dummy():
    return driver.execute_script(
        f"const t = {page.JS_GRID};"
        "if (!t) return -1;"
        "return [...t.querySelectorAll('tbody tr')].filter(r => {"
        "  const t2 = r.innerText;"
        "  const v = [...r.querySelectorAll('input')].map(i=>i.value||'').join(' ');"
        "  return t2.includes('AUTO-TEST')||t2.includes('Dummy')"
        "      || v.includes('AUTO-TEST')||v.includes('Dummy');"
        "}).length;"
    )

def jumlah_baris():
    return driver.execute_script(
        f"const t = {page.JS_GRID};"
        "return t ? t.querySelectorAll('tbody tr').length : -1;"
    )

try:
    LoginPage(driver).login()
    print("[OK] login", flush=True)

    # 1) delete + tunggu 20 dtk
    page.buka_halaman("master_alat_keselamatan_operasi")
    page.reset_cari_grid()
    page.pace(3.0)
    awal = jumlah_dummy()
    klik = driver.execute_script(
        f"const t = {page.JS_GRID};"
        "if (!t) return false;"
        "const tr = [...t.querySelectorAll('tbody tr')].find(r => {"
        "  const t2 = r.innerText;"
        "  const v = [...r.querySelectorAll('input')].map(i=>i.value||'').join(' ');"
        "  return t2.includes('AUTO-TEST')||t2.includes('Dummy')"
        "      || v.includes('AUTO-TEST')||v.includes('Dummy');"
        "});"
        "if (!tr) return false;"
        "const b = tr.querySelector('a.btn-delete');"
        "if (b) { b.click(); return true; }"
        "return false;"
    )
    print(f"[delete] klik={klik} awal={awal}", flush=True)
    page.pace(1.5)
    page.jawab_konfirmasi()
    print(f"[delete] setelah YES (lokal): {jumlah_dummy()}", flush=True)
    print("[delete] tunggu 20 dtk untuk AJAX delete...", flush=True)
    time.sleep(20)
    driver.get(driver.current_url)
    try:
        page._tunggu_tabel()
    except Exception:
        pass
    page.tunggu_processing_selesai()
    page.pace(3.0)
    print(f"[delete] SETELAH tunggu+reload: {jumlah_dummy()} (awal {awal})",
          flush=True)

    # 2) witness: create + sweep district
    page.buka_halaman("witness_statement_report")
    page.reset_cari_grid()
    page.pace(2.0)
    try:
        page.buka_form_create()
        page.pace(1.0)
        page.isi_form_create_otomatis(penanda="PROBE9")
        page.simpan_form()
        page.submit_changes()
        page.tunggu_processing_selesai()
        print("[witness] create+submit selesai tanpa error", flush=True)
    except Exception as exc:
        print(f"[witness] create ERROR {type(exc).__name__}: {exc}", flush=True)
    # sweep district
    opsi = driver.execute_script(
        "const s = document.querySelector('#cbDistrict');"
        "if (!s) return null;"
        "return {selected: s.selectedIndex,"
        " opsi: [...s.options].map((o, i) => ({i, t: o.text.trim(),"
        " v: o.value, dis: o.disabled})),"
        " value: s.value};"
    )
    print("[witness] cbDistrict:", json.dumps(opsi, ensure_ascii=False)[:1500],
          flush=True)
    if opsi:
        for o in opsi["opsi"]:
            if o["dis"]:
                continue
            try:
                el = page._ambil_js_visible(page.FILTER_UNIT)
                Select(el).select_by_index(o["i"])
                page.pace(3.0)
                n = jumlah_baris()
                ada = driver.execute_script(
                    f"const t = {page.JS_GRID};"
                    "return t ? t.innerText.includes('PROBE9') : false;"
                )
                print(f"[witness] district '{o['t']}': baris={n} "
                      f"adaPROBE9={ada}", flush=True)
            except Exception as exc:
                print(f"[witness] district '{o['t']}' ERROR "
                      f"{type(exc).__name__}: {exc}", flush=True)
    print("[SELESAI]", flush=True)
finally:
    driver.quit()
