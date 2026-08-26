"""Probe #7 (2026-08-26):

A) MASTER ALAT: apakah delete + Submit Changes = commit server?
   klik delete 1 baris -> Submit Changes + jawab konfirmasi ->
   reload -> hitung. Kalau berkurang, berarti delete = pending change
   yang butuh Submit (fix untuk test delete).

B) INCIDENT: cari aksi mana yang mematikan Export. Setelah tiap aksi,
   klik Export dan cek file terunduh.

C) WITNESS: buka form -> isi otomatis penanda 'PROBE7' -> save ->
   submit -> dump grid (baris pertama + total + search 'PROBE7').
"""
import json
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

def klik_delete_dummy():
    return driver.execute_script(
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

def coba_export(label, sebelum):
    try:
        page.export_data()
    except Exception as exc:
        print(f"  [export:{label}] ERROR {type(exc).__name__}: {exc}", flush=True)
        return
    page.pace(6.0)
    baru = sorted(set(os.listdir(config.DOWNLOAD_DIR)) - sebelum)
    print(f"  [export:{label}] file_baru={[os.path.basename(b) for b in baru]}",
          flush=True)

try:
    LoginPage(driver).login()
    print("[OK] login", flush=True)

    # A) delete + Submit Changes
    page.buka_halaman("master_alat_keselamatan_operasi")
    page.reset_cari_grid()
    page.pace(3.0)
    awal = jumlah_dummy()
    print(f"[A-delete] jumlah dummy awal: {awal}", flush=True)
    if awal > 0 and klik_delete_dummy():
        page.pace(1.5)
        print("[A-delete] klik delete OK -> Submit Changes...", flush=True)
        page.submit_changes()
        page.tunggu_processing_selesai()
        page.pace(3.0)
        print(f"[A-delete] setelah submit (lokal): {jumlah_dummy()}", flush=True)
        driver.get(driver.current_url)
        try:
            page._tunggu_tabel()
        except Exception:
            pass
        page.tunggu_processing_selesai()
        page.pace(3.0)
        print(f"[A-delete] SETELAH RELOAD: {jumlah_dummy()} (awal {awal})",
              flush=True)

    # B) incident incremental export
    page.buka_halaman("incident_investigation_form")
    sebelum = set(os.listdir(config.DOWNLOAD_DIR))
    print("[B-incident] urutan export inkremental...", flush=True)
    coba_export("sebelum-aksi", sebelum)
    try:
        page.create_dengan_form_sungguhan()
    except Exception as exc:
        print(f"  [B] create form ERROR {type(exc).__name__}: {exc}", flush=True)
    coba_export("setelah-create-form", sebelum)
    try:
        page.klik_create_lalu_batal()
    except Exception as exc:
        print(f"  [B] create polos ERROR {type(exc).__name__}: {exc}", flush=True)
    coba_export("setelah-create-polos", sebelum)
    try:
        page.buka_modal_import()
        page.pace(1.0)
        page.tutup_modal()
    except Exception as exc:
        print(f"  [B] import ERROR {type(exc).__name__}: {exc}", flush=True)
    coba_export("setelah-import", sebelum)
    try:
        page.toggle_fullscreen()
        page.tunggu_fullscreen(True)
        page.pace(1.0)
        page.toggle_fullscreen()
        page.tunggu_fullscreen(False)
    except Exception as exc:
        print(f"  [B] fullscreen ERROR {type(exc).__name__}: {exc}", flush=True)
    coba_export("setelah-fullscreen", sebelum)
    try:
        page.buka_dropdown_columns()
        page.pace(1.0)
        page.tutup_dropdown_columns()
    except Exception as exc:
        print(f"  [B] columns ERROR {type(exc).__name__}: {exc}", flush=True)
    coba_export("setelah-columns", sebelum)
    try:
        page.submit_changes()
        page.tunggu_processing_selesai()
    except Exception as exc:
        print(f"  [B] submit ERROR {type(exc).__name__}: {exc}", flush=True)
    coba_export("setelah-submit", sebelum)

    # C) witness create + grid dump
    page.buka_halaman("witness_statement_report")
    try:
        page.create_dengan_form_sungguhan()
        print("[C-witness] create_dengan_form_sungguhan: OK", flush=True)
    except Exception as exc:
        print(f"[C-witness] create ERROR {type(exc).__name__}: {exc}", flush=True)
    page.reset_cari_grid()
    page.pace(2.0)
    dump = driver.execute_script(
        f"const t = {page.JS_GRID};"
        "if (!t) return {grid: false};"
        "const trs = [...t.querySelectorAll('tbody tr')];"
        "const baris = trs.slice(0, 3).map(r => {"
        "  const v = [...r.querySelectorAll('input')].map(i=>i.value||'')"
        "      .filter(Boolean).join('|');"
        "  return (r.innerText || '').replace(/\\s+/g, ' ').slice(0, 200) + ' :: ' + v.slice(0, 150);"
        "});"
        "const infoEl = document.querySelector('.dataTables_info');"
        "return {grid: true, total_baris: trs.length,"
        " info: infoEl ? infoEl.innerText : '(none)', baris};"
    )
    print("[C-witness] grid:", json.dumps(dump, ensure_ascii=False)[:2000], flush=True)
    page.cari_di_grid("PROBE7")
    page.pace(2.0)
    ditemukan = driver.execute_script(
        f"const t = {page.JS_GRID};"
        "return t ? t.querySelectorAll('tbody tr').length : -1;"
    )
    print(f"[C-witness] setelah search PROBE7: {ditemukan} baris", flush=True)

    print("[SELESAI]", flush=True)
finally:
    driver.quit()
