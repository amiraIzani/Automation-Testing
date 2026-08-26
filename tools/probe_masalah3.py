"""Probe #3 (2026-08-26): lanjutan -- tiap langkah mandiri (gagal satu
tidak mematikan yang lain).

1) Statistic: uji edit Nearmiss dengan jeda + fallback klik JS, lalu
   submit -> reload -> baca -> revert -> submit -> reload -> baca.
   Sekalian dump atribut input Nearmiss (readonly? disabled?).
2) Witness Statement: buka form create (retry + re-nav) -> dump field.
3) Incident Investigation: klik Export -> amati modal/alert/file unduh.
4) Bandingkan: parent chain btnReloadData di halaman yang LOLOS
   (master_alat) vs yang gagal -- konfirmasi panel-tag.d-none.
"""
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import (
    ElementNotInteractableException,
    StaleElementReferenceException,
)

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
    print("[OK] login ->", driver.current_url, flush=True)

    # 1) Statistic: edit Nearmiss hati-hati
    page.buka_halaman("statistic_safety_recapitulation")
    page.reset_cari_grid()
    page.pace(2.0)
    anchor = {"Month": "July", "TipePegawai": "Pegawai"}
    awal = page.baca_sel_grid_anchor("Nearmiss", anchor)
    el = page._ambil_elemen_sel_anchor("Nearmiss", anchor)
    if el is not None:
        atr = driver.execute_script(
            "const e = arguments[0];"
            "return {readonly: e.readOnly, disabled: e.disabled,"
            " outer: e.outerHTML.slice(0, 400)};",
            el,
        )
        print(f"[statistik] Nearmiss awal={awal!r} atribut={json.dumps(atr)}",
              flush=True)
    if awal:
        uji = str(int(float(awal)) + 1)
        # isi dengan fallback kalau klik native ditolak
        terisi = False
        for upaya in range(3):
            try:
                page.isi_sel_grid_anchor("Nearmiss", uji, anchor)
                terisi = True
                break
            except ElementNotInteractableException as exc:
                print(f"[statistik] isi upaya#{upaya+1} not-interactable: {exc}",
                      flush=True)
                page.tunggu_processing_selesai()
                page.pace(3.0)
            except StaleElementReferenceException:
                page.tunggu_processing_selesai()
                page.pace(3.0)
        if not terisi:
            # fallback: set value lewat JS + event change
            el = page._ambil_elemen_sel_anchor("Nearmiss", anchor)
            driver.execute_script(
                "arguments[0].focus();"
                "arguments[0].value = arguments[1];"
                "arguments[0].dispatchEvent(new Event('input', {bubbles: true}));"
                "arguments[0].dispatchEvent(new Event('change', {bubbles: true}));"
                "arguments[0].dispatchEvent(new KeyboardEvent('keyup', "
                "{bubbles: true, key: '1'}));",
                el, uji,
            )
            page.pace(2.0)
            print("[statistik] isi lewat JS fallback", flush=True)
        baca_segera = page.baca_sel_grid_anchor("Nearmiss", anchor)
        print(f"[statistik] nilai sel setelah isi: {baca_segera!r}", flush=True)
        page.submit_changes()
        page.pace(3.0)
        page.buka_halaman("statistic_safety_recapitulation")
        page.reset_cari_grid()
        baca = page.baca_sel_grid_anchor("Nearmiss", anchor)
        print(f"[statistik] setelah submit+reload: {baca!r} (harap {uji!r})",
              flush=True)
        # revert
        page.isi_sel_grid_anchor("Nearmiss", awal, anchor)
        page.pace(1.0)
        page.submit_changes()
        page.pace(3.0)
        page.buka_halaman("statistic_safety_recapitulation")
        page.reset_cari_grid()
        baca2 = page.baca_sel_grid_anchor("Nearmiss", anchor)
        print(f"[statistik] setelah revert+reload: {baca2!r} (harap {awal!r})",
              flush=True)

    # 2) Witness Statement: form create (retry + re-nav)
    page.buka_halaman("witness_statement_report")
    terbuka = False
    for percobaan in range(3):
        try:
            page.buka_form_create()
            terbuka = True
            break
        except Exception as exc:
            print(f"[witness_form] coba#{percobaan+1} gagal: "
                  f"{type(exc).__name__}: {exc}", flush=True)
            driver.get(driver.current_url)
            try:
                page._tunggu_tabel()
            except Exception:
                pass
            page.tunggu_processing_selesai()
            page.pace(2.0)
    if terbuka:
        fields = driver.execute_script(page.JS_FIELD_FORM)
        print("[witness_form] fields:", json.dumps(fields, ensure_ascii=False)[:4000],
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

    # 3) Incident Investigation: export + amati
    page.buka_halaman("incident_investigation_form")
    sebelum = set(os.listdir(config.DOWNLOAD_DIR))
    print("[incident_export] klik Export...", flush=True)
    try:
        page.export_data()
    except Exception as exc:
        print(f"[incident_export] export_data ERROR {type(exc).__name__}: {exc}",
              flush=True)
    for detik in (5, 15, 30, 60, 90):
        time.sleep(detik - (5 if detik == 15 else 15 if detik == 30
                            else 30 if detik == 60 else 60 if detik == 90 else 0))
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
    if page._ada_modal_tampil():
        dump = driver.execute_script(
            "const m = document.querySelector('.modal.show');"
            "return m ? m.outerHTML.slice(0, 2500) : '(none)';"
        )
        print("[incident_export] HTML modal:", dump, flush=True)
        try:
            page.tutup_modal()
        except Exception as exc:
            print(f"[incident_export] tutup ERROR {exc}", flush=True)

    # 4) Bandingkan parent chain btnReloadData: halaman lolos vs gagal
    for k in ["master_alat_keselamatan_operasi", "initial_incident_accident_report"]:
        page.buka_halaman(k)
        semua = driver.execute_script(
            "const els = [...document.querySelectorAll('#btnReloadData')];"
            "return els.map(el => {"
            "  const s = window.getComputedStyle(el);"
            "  const r = el.getBoundingClientRect();"
            "  let chain = []; let p = el;"
            "  for (let i = 0; i < 5 && p; i++) {"
            "    const ps = window.getComputedStyle(p);"
            "    const pr = p.getBoundingClientRect();"
            "    chain.push({tag: p.tagName, cls: (p.className || '').toString().slice(0, 60),"
            "                display: ps.display, w: pr.width, h: pr.height});"
            "    p = p.parentElement;"
            "  }"
            "  return {w: r.width, h: r.height, chain};"
            "});"
        )
        print(f"[banding:{k}] {json.dumps(semua)}", flush=True)

    print("[SELESAI]", flush=True)
finally:
    driver.quit()
