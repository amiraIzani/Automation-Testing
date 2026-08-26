"""Probe #6 (2026-08-26):

1) MASTER ALAT - apakah delete benar2 commit ke server?
   klik delete baris dummy -> dump modal/alert -> jawab -> hitung
   -> RELOAD halaman -> hitung lagi. Kalau setelah reload jumlahnya
   kembali, berarti delete cuma menghapus lokal (optimistic UI) dan
   server tidak menghapus -- penjelasan kenapa test delete tidak
   pernah bisa bersih (jumlah dummy tumbuh tiap run).
2) WITNESS - scan field form create (yang mana lookup/required/kosong)
   + cek grid kolom yang tampil (th) untuk tahu apakah penanda 'Dummy'
   bisa tampil di grid sama sekali.
3) INCIDENT - reproduksi urutan coba_semua_tombol sebelum Export
   (Create form -> Create -> Import -> FullScreen -> Columns -> Submit)
   lalu klik Export 2x dan amati modal/alert/file tiap percobaan.
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

def dump_modal():
    return driver.execute_script(
        "const out = [];"
        "document.querySelectorAll('.modal, .bootbox').forEach(m => {"
        "  const s = window.getComputedStyle(m);"
        "  const r = m.getBoundingClientRect();"
        "  if (s.display !== 'none' && r.width > 0)"
        "    out.push((m.className || '').toString().slice(0, 80));"
        "});"
        "return out;"
    )

try:
    LoginPage(driver).login()
    print("[OK] login", flush=True)

    # 1) delete commit check
    page.buka_halaman("master_alat_keselamatan_operasi")
    page.reset_cari_grid()
    page.pace(3.0)
    print(f"[delete] jumlah dummy saat buka: {jumlah_dummy()}", flush=True)
    for percobaan in range(2):
        sebelum = jumlah_dummy()
        klik = driver.execute_script(
            f"const t = {page.JS_GRID};"
            "if (!t) return {ok:false};"
            "const tr = [...t.querySelectorAll('tbody tr')].find(r => {"
            "  const t2 = r.innerText;"
            "  const v = [...r.querySelectorAll('input')].map(i=>i.value||'').join(' ');"
            "  return t2.includes('AUTO-TEST')||t2.includes('Dummy')"
            "      || v.includes('AUTO-TEST')||v.includes('Dummy');"
            "});"
            "if (!tr) return {ok:false};"
            "const b = tr.querySelector('a.btn-delete');"
            "if (!b) return {ok:false, alasan:'btn-delete tidak ada'};"
            "b.click(); return {ok:true};"
        )
        print(f"[delete] #{percobaan+1} klik={klik} sebelum={sebelum}", flush=True)
        page.pace(1.5)
        print(f"[delete] #{percobaan+1} modal setelah klik: {dump_modal()}", flush=True)
        page.jawab_konfirmasi()
        page.tunggu_processing_selesai()
        page.pace(2.0)
        sesudah = jumlah_dummy()
        print(f"[delete] #{percobaan+1} setelah jawab: {sesudah} "
              f"modal={dump_modal()}", flush=True)
        driver.get(driver.current_url)
        try:
            page._tunggu_tabel()
        except Exception:
            pass
        page.tunggu_processing_selesai()
        page.pace(3.0)
        setelah_reload = jumlah_dummy()
        print(f"[delete] #{percobaan+1} SETELAH RELOAD: {setelah_reload} "
              f"(sebelum klik {sebelum})", flush=True)

    # 2) witness: scan form + kolom grid
    page.buka_halaman("witness_statement_report")
    page.buka_form_create()
    page.pace(1.5)
    fields = driver.execute_script(page.JS_FIELD_FORM)
    print("[witness_form] fields:", json.dumps(fields, ensure_ascii=False)[:4000],
          flush=True)
    # kolom grid yang tampil
    kolom = driver.execute_script(
        f"const t = {page.JS_GRID};"
        "if (!t) return [];"
        "return [...t.querySelectorAll('thead th')].map(th =>"
        "  th.getAttribute('data-name') || (th.innerText||'').trim()).filter(Boolean);"
    )
    print("[witness_grid] kolom tampil:", kolom, flush=True)
    try:
        page.batal_form()
    except Exception as exc:
        print(f"[witness_form] batal ERROR {exc}", flush=True)
        try:
            page.tutup_modal()
        except Exception:
            pass

    # 3) incident: urutan aksi sebelum Export lalu export 2x
    page.buka_halaman("incident_investigation_form")
    print("[incident] urutan aksi...", flush=True)
    try:
        page.create_dengan_form_sungguhan()
        print("[incident] create form: OK", flush=True)
    except Exception as exc:
        print(f"[incident] create form ERROR {type(exc).__name__}: {exc}", flush=True)
    try:
        page.klik_create_lalu_batal()
        print("[incident] create polos: OK", flush=True)
    except Exception as exc:
        print(f"[incident] create polos ERROR {type(exc).__name__}: {exc}", flush=True)
    try:
        page.buka_modal_import()
        page.pace(1.0)
        page.tutup_modal()
        print("[incident] import: OK", flush=True)
    except Exception as exc:
        print(f"[incident] import ERROR {type(exc).__name__}: {exc}", flush=True)
    try:
        page.toggle_fullscreen()
        page.tunggu_fullscreen(True)
        page.pace(1.0)
        page.toggle_fullscreen()
        page.tunggu_fullscreen(False)
        print("[incident] fullscreen: OK", flush=True)
    except Exception as exc:
        print(f"[incident] fullscreen ERROR {type(exc).__name__}: {exc}", flush=True)
    try:
        page.buka_dropdown_columns()
        page.pace(1.0)
        page.tutup_dropdown_columns()
        print("[incident] columns: OK", flush=True)
    except Exception as exc:
        print(f"[incident] columns ERROR {type(exc).__name__}: {exc}", flush=True)
    try:
        page.submit_changes()
        page.tunggu_processing_selesai()
        print("[incident] submit: OK", flush=True)
    except Exception as exc:
        print(f"[incident] submit ERROR {type(exc).__name__}: {exc}", flush=True)
    sebelum = set(os.listdir(config.DOWNLOAD_DIR))
    for percobaan in range(2):
        try:
            page.export_data()
        except Exception as exc:
            print(f"[incident] export#{percobaan+1} ERROR {type(exc).__name__}: {exc}",
                  flush=True)
        page.pace(6.0)
        baru = sorted(set(os.listdir(config.DOWNLOAD_DIR)) - sebelum)
        print(f"[incident] export#{percobaan+1}: modal={dump_modal()} "
              f"file_baru={baru}", flush=True)
        if baru:
            break

    print("[SELESAI]", flush=True)
finally:
    driver.quit()
