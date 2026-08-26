"""Probe diagnosis 2026-08-26: cek LIVE penyebab 14 test gagal di
run terakhir (report 2026-08-24 16:15). Satu sesi Chrome:

1) 6 halaman "Reload Data tidak tampil" -> state btnReloadData + tombol lain
2) Master Alat -> jumlah baris dummy + struktur tombol Delete per baris
3) Master Alat -> klik Delete 1 baris dummy + amati efeknya
4) Statistic Safety -> baris anchor {Month, TipePegawai} (cek ambigu?)
5) Witness Statement -> scan field form Create (field wajib / kosong)
6) Incident Investigation -> klik Export + amati modal/alert/file unduh

TIDAK dipanggil dari pytest -- dijalankan manual:
    python tools/probe_masalah.py
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

try:
    # 0) login
    LoginPage(driver).login()
    print("[OK] login ->", driver.current_url, flush=True)

    JS_STATE_RELOAD = (
        "const el = document.querySelector('#btnReloadData');"
        "if (!el) return {ada: false};"
        "const s = window.getComputedStyle(el);"
        "const r = el.getBoundingClientRect();"
        "return {ada: true, display: s.display, visibility: s.visibility,"
        " w: r.width, h: r.height, html: el.outerHTML.slice(0, 250)};"
    )

    # 1) 6 halaman Reload Data
    for k in [
        "emergency_drill_daily",
        "golden_rules",
        "incident_investigation_form",
        "safety_kkp_p2k3_committee_meeting",
        "smk3",
        "smkp",
    ]:
        try:
            page.buka_halaman(k)
            st = driver.execute_script(JS_STATE_RELOAD)
            lain = driver.execute_script(
                "return {submit: !!document.querySelector('#btnSubmit'),"
                " export: !!document.querySelector('#btnExport'),"
                " cancel: !!document.querySelector('#btnCancel'),"
                " import: !!document.querySelector('#btnImport')};"
            )
            print(f"[reload:{k}] state={st}", flush=True)
            print(f"[reload:{k}] tombol_lain={lain}", flush=True)
        except Exception as exc:
            print(f"[reload:{k}] ERROR {type(exc).__name__}: {exc}", flush=True)

    # 2) + 3) Master Alat: struktur baris dummy + klik delete 2x
    page.buka_halaman("master_alat_keselamatan_operasi")
    page.reset_cari_grid()
    info = driver.execute_script(
        f"""
        const t = {page.JS_GRID};
        if (!t) return {{grid: false}};
        const trs = [...t.querySelectorAll('tbody tr')];
        const dummy = trs.filter(r => {{
          const t2 = r.innerText;
          const v = [...r.querySelectorAll('input')].map(i=>i.value||'').join(' ');
          return t2.includes('AUTO-TEST')||t2.includes('Dummy')
              || v.includes('AUTO-TEST')||v.includes('Dummy');
        }});
        const infoEl = document.querySelector('.dataTables_info');
        return {{
          grid: true, total: trs.length, dummy: dummy.length,
          info: infoEl ? infoEl.innerText : '(none)',
          html_dummy: dummy.slice(0, 2).map(r => r.outerHTML.slice(0, 1200)),
          html_baris_normal: (trs.find(r => !dummy.includes(r)) || {{outerHTML:''}})
              .outerHTML.slice(0, 1200),
        }};
        """
    )
    print("[master_alat] total/dummy:", info.get("total"), "/", info.get("dummy"),
          "| info:", info.get("info"), flush=True)
    for i, h in enumerate(info.get("html_dummy", [])):
        print(f"[master_alat] DUMMY#{i}: {h}", flush=True)
    print("[master_alat] BARIS NORMAL:", info.get("html_baris_normal"), flush=True)

    # klik delete baris dummy pertama, amati
    def jumlah_dummy():
        return driver.execute_script(
            f"const t = {page.JS_GRID};"
            "if (!t) return -1;"
            "const trs = [...t.querySelectorAll('tbody tr')];"
            "return trs.filter(r => {"
            "  const t2 = r.innerText;"
            "  const v = [...r.querySelectorAll('input')].map(i=>i.value||'').join(' ');"
            "  return t2.includes('AUTO-TEST')||t2.includes('Dummy')"
            "      || v.includes('AUTO-TEST')||v.includes('Dummy');"
            "}).length;"
        )

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
            "if (!b) return {ok:false, alasan:'btn-delete tidak ada',"
            " links: [...tr.querySelectorAll('a')].map(a=>a.outerHTML.slice(0,200))};"
            "b.click(); return {ok:true};"
        )
        print(f"[master_alat] delete#{percobaan+1} klik={klik} sebelum={sebelum}", flush=True)
        if klik.get("ok"):
            page.pace(1.0)
            page.jawab_konfirmasi()
            page.tunggu_processing_selesai()
            page.pace(2.0)
            sesudah = jumlah_dummy()
            modal = page._ada_modal_tampil()
            print(f"[master_alat] delete#{percobaan+1} sesudah={sesudah} modal={modal} "
                  f"url={driver.current_url}", flush=True)
        else:
            break

    # 4) Statistic Safety: baris anchor
    page.buka_halaman("statistic_safety_recapitulation")
    page.reset_cari_grid()
    baris = driver.execute_script(
        f"""
        const t = {page.JS_GRID};
        if (!t) return [];
        const inp = (r, n) => {{
          const i = r.querySelector("input[data-fieldname='"+n+"']");
          return i ? i.value : null;
        }};
        return [...t.querySelectorAll('tbody tr')].slice(0, 15).map(r => ({{
          month: inp(r,'Month'), tipe: inp(r,'TipePegawai'),
          pak: inp(r,'PenyakitAkibatKerja'),
          fields: [...r.querySelectorAll('input[data-fieldname]')].slice(0,8)
              .map(i=>i.getAttribute('data-fieldname')+':'+i.value),
        }}));
        """
    )
    print("[statistik] baris:", json.dumps(baris, ensure_ascii=False)[:2500], flush=True)

    # 5) Witness Statement: scan field form
    page.buka_halaman("witness_statement_report")
    page.buka_form_create()
    fields = driver.execute_script(page.JS_FIELD_FORM)
    print("[witness_form] fields:", json.dumps(fields, ensure_ascii=False)[:3000], flush=True)
    try:
        page.batal_form()
        print("[witness_form] modal ditutup", flush=True)
    except Exception as exc:
        print(f"[witness_form] batal ERROR {type(exc).__name__}: {exc}", flush=True)
        try:
            page.tutup_modal()
        except Exception:
            pass

    # 6) Incident Investigation: klik Export + amati
    page.buka_halaman("incident_investigation_form")
    sebelum = set(os.listdir(config.DOWNLOAD_DIR))
    print("[incident_export] klik Export...", flush=True)
    try:
        page.export_data()
    except Exception as exc:
        print(f"[incident_export] export_data ERROR {type(exc).__name__}: {exc}", flush=True)
    page.pace(3.0)
    modal = page._ada_modal_tampil()
    try:
        alert_teks = driver.switch_to.alert.text
        driver.switch_to.alert.accept()
    except Exception:
        alert_teks = None
    setelah = sorted(set(os.listdir(config.DOWNLOAD_DIR)) - sebelum)
    print(f"[incident_export] modal={modal} alert={alert_teks!r} file_baru={setelah}",
          flush=True)
    page.pace(6.0)
    setelah2 = sorted(set(os.listdir(config.DOWNLOAD_DIR)) - sebelum)
    print(f"[incident_export] +6dtk file_baru={setelah2} modal={page._ada_modal_tampil()}",
          flush=True)
    if page._ada_modal_tampil():
        try:
            page.tutup_modal()
        except Exception as exc:
            print(f"[incident_export] tutup ERROR {exc}", flush=True)

    print("[SELESAI]", flush=True)
finally:
    driver.quit()
