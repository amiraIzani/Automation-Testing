"""Probe #8 (2026-08-26):

1) MASTER ALAT: klik delete -> BACA TEKS bootbox yang muncul.
2) INCIDENT: create polos -> export (harus gagal) -> bersihkan draft
   localStorage + navigasi ulang -> export lagi. Menentukan apakah
   draft lokal yang memblokir export.
3) WITNESS: dump nilai + tipe filter tanggal (tbDate) -> set ke hari
   ini -> cek jumlah baris grid -> buka form -> isi -> save -> submit
   -> cek penanda tampil.
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

def jumlah_baris():
    return driver.execute_script(
        f"const t = {page.JS_GRID};"
        "return t ? t.querySelectorAll('tbody tr').length : -1;"
    )

try:
    LoginPage(driver).login()
    print("[OK] login", flush=True)

    # 1) teks alert delete
    page.buka_halaman("master_alat_keselamatan_operasi")
    page.reset_cari_grid()
    page.pace(3.0)
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
    page.pace(2.0)
    teks = driver.execute_script(
        "const m = document.querySelector('.bootbox, .modal.show');"
        "return m ? (m.innerText || '').replace(/\\s+/g, ' ').trim().slice(0, 300)"
        " : '(tidak ada)';"
    )
    print(f"[alert-delete] klik={klik} TEKS: {teks!r}", flush=True)
    page.jawab_konfirmasi()
    page.tunggu_processing_selesai()
    page.buka_halaman("master_alat_keselamatan_operasi")  # restore

    # 2) incident: draft memblokir export?
    page.buka_halaman("incident_investigation_form")
    sebelum = set(os.listdir(config.DOWNLOAD_DIR))
    try:
        page.klik_create_lalu_batal()
    except Exception as exc:
        print(f"[incident] create polos ERROR {type(exc).__name__}: {exc}",
              flush=True)
    page.pace(3.0)
    try:
        page.export_data()
    except Exception as exc:
        print(f"[incident] export ERROR {type(exc).__name__}: {exc}", flush=True)
    page.pace(6.0)
    baru = sorted(set(os.listdir(config.DOWNLOAD_DIR)) - sebelum)
    print(f"[incident] export setelah create-polos: {[os.path.basename(b) for b in baru]}",
          flush=True)
    # cek draft localStorage
    draft = driver.execute_script(
        "const m = /Id=(\\d+)/.exec(window.location.href);"
        "if (!m) return [];"
        "const prefix = 'dr_' + m[1] + '_';"
        "return Object.keys(window.localStorage).filter(k => k.indexOf(prefix) === 0);"
    )
    print(f"[incident] draft localStorage: {draft}", flush=True)
    if not baru:
        # bersihkan draft + navigasi ulang + export lagi
        print("[incident] bersihkan draft + nav ulang...", flush=True)
        driver.execute_script(
            "const m = /Id=(\\d+)/.exec(window.location.href);"
            "if (!m) return;"
            "const prefix = 'dr_' + m[1] + '_';"
            "Object.keys(window.localStorage).forEach(k => {"
            "  if (k.indexOf(prefix) === 0) window.localStorage.removeItem(k);"
            "});"
        )
        driver.get(driver.current_url)
        try:
            page._tunggu_tabel()
        except Exception:
            pass
        page.tunggu_processing_selesai()
        page.pace(3.0)
        try:
            page.export_data()
        except Exception as exc:
            print(f"[incident] export2 ERROR {type(exc).__name__}: {exc}",
                  flush=True)
        page.pace(6.0)
        baru2 = sorted(set(os.listdir(config.DOWNLOAD_DIR)) - sebelum)
        print(f"[incident] export SETELAH bersih draft: "
              f"{[os.path.basename(b) for b in baru2]}", flush=True)

    # 3) witness: filter tanggal vs grid kosong
    page.buka_halaman("witness_statement_report")
    page.reset_cari_grid()
    page.pace(2.0)
    f = driver.execute_script(
        "const el = document.querySelector('#tbDate');"
        "return el ? {value: el.value, type: el.type || el.tagName,"
        " html: el.outerHTML.slice(0, 300)} : null;"
    )
    print(f"[witness] tbDate: {f}", flush=True)
    print(f"[witness] jumlah baris (filter sekarang): {jumlah_baris()}", flush=True)
    # set tanggal ke hari ini
    hari_ini = time.strftime("%Y-%m-%d")
    try:
        page.set_filter_tanggal(hari_ini)
    except Exception as exc:
        print(f"[witness] set_filter ERROR {type(exc).__name__}: {exc}",
              flush=True)
    page.tunggu_processing_selesai()
    page.pace(3.0)
    print(f"[witness] tbDate setelah set: {page.baca_filter_tanggal()!r} "
          f"baris={jumlah_baris()}", flush=True)
    # create dummy
    try:
        page.buka_form_create()
        page.pace(1.0)
        page.isi_form_create_otomatis(penanda="PROBE8")
        page.simpan_form()
        page.submit_changes()
        page.tunggu_processing_selesai()
        page.pace(3.0)
        print(f"[witness] setelah create+submit: baris={jumlah_baris()}",
              flush=True)
        page.cari_di_grid("PROBE8")
        page.pace(2.0)
        print(f"[witness] search PROBE8: baris={jumlah_baris()}", flush=True)
    except Exception as exc:
        print(f"[witness] create ERROR {type(exc).__name__}: {exc}", flush=True)

    print("[SELESAI]", flush=True)
finally:
    driver.quit()
