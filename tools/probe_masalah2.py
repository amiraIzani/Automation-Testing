"""Probe #2 (2026-08-26): gali penyebab sisa kegagalan.

1) Semua elemen #btnReloadData di 6 halaman (duplikat? parent chain?)
   + cek apakah tombol JADI tampak setelah navigasi ulang
2) Statistic Safety: edit field Nearmiss baris {Month:July, TipePegawai:
   Pegawai} (+1 -> Submit -> buka ulang -> baca -> revert -> Submit ->
   buka ulang -> baca) -- uji apakah field ini benar2 editable
3) Witness Statement: buka form create (dengan re-navigasi kalau modal
   macet) -> dump field -> batal
4) Incident Investigation: klik Export -> amati modal/alert/file unduh
   (tunggu 90 detik, cek folder unduhan berkala)
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

JS_RELOAD_ALL = """
const els = [...document.querySelectorAll('#btnReloadData')];
return els.map(el => {
  const s = window.getComputedStyle(el);
  const r = el.getBoundingClientRect();
  let chain = [];
  let p = el;
  for (let i = 0; i < 5 && p; i++) {
    const ps = window.getComputedStyle(p);
    const pr = p.getBoundingClientRect();
    chain.push({tag: p.tagName, cls: (p.className || '').toString().slice(0, 60),
                display: ps.display, w: pr.width, h: pr.height});
    p = p.parentElement;
  }
  return {w: r.width, h: r.height, chain};
});
"""

try:
    LoginPage(driver).login()
    print("[OK] login ->", driver.current_url, flush=True)

    # 1) Reload Data: semua match + parent chain + efek navigasi ulang
    for k in ["emergency_drill_daily", "incident_investigation_form", "smk3"]:
        page.buka_halaman(k)
        semua = driver.execute_script(JS_RELOAD_ALL)
        print(f"[reload2:{k}] jumlah={len(semua)}")
        for i, el in enumerate(semua):
            print(f"[reload2:{k}] #{i} w={el['w']} h={el['h']} chain={json.dumps(el['chain'])}")
        # navigasi ulang & cek lagi
        driver.get(driver.current_url)
        try:
            page._tunggu_tabel()
        except Exception:
            pass
        page.tunggu_processing_selesai()
        page.pace(2.0)
        semua2 = driver.execute_script(JS_RELOAD_ALL)
        print(f"[reload2:{k}] SETELAH NAV ULANG: jumlah={len(semua2)} "
              f"dimensi={[(e['w'], e['h']) for e in semua2]}", flush=True)

    # 2) Statistic: edit Nearmiss + submit + verifikasi + revert
    page.buka_halaman("statistic_safety_recapitulation")
    page.reset_cari_grid()
    anchor = {"Month": "July", "TipePegawai": "Pegawai"}
    awal = page.baca_sel_grid_anchor("Nearmiss", anchor)
    print(f"[statistik] Nearmiss awal={awal!r}", flush=True)
    if awal:
        uji = str(int(float(awal)) + 1)
        page.isi_sel_grid_anchor("Nearmiss", uji, anchor)
        page.pace(1.0)
        page.submit_changes()
        page.pace(2.0)
        page.buka_halaman("statistic_safety_recapitulation")
        page.reset_cari_grid()
        baca = page.baca_sel_grid_anchor("Nearmiss", anchor)
        print(f"[statistik] setelah submit+reload: {baca!r} (harap {uji!r})", flush=True)
        # revert
        page.isi_sel_grid_anchor("Nearmiss", awal, anchor)
        page.pace(1.0)
        page.submit_changes()
        page.pace(2.0)
        page.buka_halaman("statistic_safety_recapitulation")
        page.reset_cari_grid()
        baca2 = page.baca_sel_grid_anchor("Nearmiss", anchor)
        print(f"[statistik] setelah revert+reload: {baca2!r} (harap {awal!r})", flush=True)

    # 3) Witness Statement: form create dengan retry
    page.buka_halaman("witness_statement_report")
    terbuka = False
    for percobaan in range(3):
        try:
            page.buka_form_create()
            terbuka = True
            break
        except Exception as exc:
            print(f"[witness_form] coba#{percobaan+1} gagal: {type(exc).__name__}: {exc}",
                  flush=True)
            driver.get(driver.current_url)
            try:
                page._tunggu_tabel()
            except Exception:
                pass
            page.tunggu_processing_selesai()
            page.pace(2.0)
    if terbuka:
        fields = driver.execute_script(page.JS_FIELD_FORM)
        print("[witness_form] fields:", json.dumps(fields, ensure_ascii=False)[:3500],
              flush=True)
        try:
            page.batal_form()
        except Exception as exc:
            print(f"[witness_form] batal ERROR {exc}", flush=True)
            try:
                page.tutup_modal()
            except Exception:
                pass
    else:
        print("[witness_form] modal TIDAK PERNAH terbuka (3 percobaan)", flush=True)

    # 4) Incident Investigation: export
    page.buka_halaman("incident_investigation_form")
    sebelum = set(os.listdir(config.DOWNLOAD_DIR))
    print("[incident_export] klik Export...", flush=True)
    try:
        page.export_data()
    except Exception as exc:
        print(f"[incident_export] export_data ERROR {type(exc).__name__}: {exc}",
              flush=True)
    for detik in (5, 15, 30, 60, 90):
        time.sleep(detik - (0 if detik == 5 else
                            (5 if detik == 15 else (15 if detik == 30 else
                             (30 if detik == 60 else 60)))))
        modal = page._ada_modal_tampil()
        try:
            alert_teks = driver.switch_to.alert.text
            driver.switch_to.alert.accept()
        except Exception:
            alert_teks = None
        baru = sorted(set(os.listdir(config.DOWNLOAD_DIR)) - sebelum)
        print(f"[incident_export] t+{detik}s modal={modal} alert={alert_teks!r} "
              f"file_baru={baru}", flush=True)
        if baru:
            break
    # dump modal yang ada (kalau ada) supaya tahu isinya
    if page._ada_modal_tampil():
        dump = driver.execute_script(
            "const m = document.querySelector('.modal.show');"
            "return m ? m.outerHTML.slice(0, 2000) : '(none)';"
        )
        print("[incident_export] HTML modal:", dump, flush=True)
        try:
            page.tutup_modal()
        except Exception as exc:
            print(f"[incident_export] tutup ERROR {exc}", flush=True)

    print("[SELESAI]", flush=True)
finally:
    driver.quit()
