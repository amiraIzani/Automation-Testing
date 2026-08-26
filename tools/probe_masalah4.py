"""Probe #4 (2026-08-26):

1) Inventarisasi toolbar SEMUA halaman Safety: daftar tombol tampak
   (teks + id), jumlah #btnReloadData (dan visibilitasnya), apakah ADA
   tombol tampak berteks 'Reload Data' (id apa pun).
2) Statistic: dump baris lengkap Januari/Pegawai + daftar (Month,
   TipePegawai) semua baris terlihat; lalu uji edit FirstAidCase
   Januari/Pegawai (+1 -> Submit -> reload -> baca -> revert -> Submit
   -> reload -> baca).
3) Witness: klik Create with Form -> tunggu -> dump SEMUA elemen
   .modal (class + sebagian HTML) + jumlah tab browser.
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

JS_TOOLBAR = """
const out = {tombol_tampak: [], reload_matches: []};
document.querySelectorAll('#btnReloadData').forEach(el => {
  const r = el.getBoundingClientRect();
  out.reload_matches.push({w: r.width, h: r.height});
});
document.querySelectorAll('button, a[title="Filling instructions"]').forEach(el => {
  const s = window.getComputedStyle(el);
  const r = el.getBoundingClientRect();
  if (s.display === 'none' || s.visibility === 'hidden' || r.width <= 0 || r.height <= 0) return;
  const t = (el.innerText || el.title || '').replace(/\\s+/g, ' ').trim();
  if (t && t.length <= 40) out.tombol_tampak.push(t);
});
return out;
"""

try:
    LoginPage(driver).login()
    print("[OK] login ->", driver.current_url, flush=True)

    # 1) inventarisasi toolbar semua halaman
    for kunci in sorted(page.HALAMAN):
        try:
            page.buka_halaman(kunci)
        except Exception as exc:
            print(f"[toolbar:{kunci}] BUKA ERROR {type(exc).__name__}: {exc}", flush=True)
            continue
        hasil = driver.execute_script(JS_TOOLBAR)
        print(f"[toolbar:{kunci}] tombol={hasil['tombol_tampak']} "
              f"reload={hasil['reload_matches']}", flush=True)

    # 2) statistic: dump baris + uji edit FirstAidCase
    page.buka_halaman("statistic_safety_recapitulation")
    page.reset_cari_grid()
    page.pace(2.0)
    baris = driver.execute_script(
        f"""
        const t = {page.JS_GRID};
        if (!t) return [];
        const inp = (r, n) => {{
          const i = r.querySelector("input[data-fieldname='"+n+"']");
          return i ? i.value : null;
        }};
        return [...t.querySelectorAll('tbody tr')].map(r => ({{
          month: inp(r,'Month'), tipe: inp(r,'TipePegawai'),
          firstaid: inp(r,'FirstAidCase'), med: inp(r,'MedicalTreatment'),
          nearmiss: inp(r,'Nearmiss'), pak: inp(r,'PenyakitAkibatKerja'),
          rowidx: (r.querySelector('input[data-fieldname]') || {{}})
              .getAttribute('data-rowindex'),
        }}));
        """
    )
    print("[statistik] semua baris:", json.dumps(baris, ensure_ascii=False)[:3000],
          flush=True)
    anchor = {"Month": "January", "TipePegawai": "Pegawai"}
    awal = page.baca_sel_grid_anchor("FirstAidCase", anchor)
    print(f"[statistik] FirstAidCase awal={awal!r} anchor={anchor}", flush=True)
    if awal:
        uji = str(int(float(awal)) + 1)
        page.isi_sel_grid_anchor("FirstAidCase", uji, anchor)
        page.pace(2.0)
        page.submit_changes()
        page.pace(3.0)
        page.buka_halaman("statistic_safety_recapitulation")
        page.reset_cari_grid()
        baca = page.baca_sel_grid_anchor("FirstAidCase", anchor)
        print(f"[statistik] setelah submit+reload: {baca!r} (harap {uji!r})",
              flush=True)
        page.isi_sel_grid_anchor("FirstAidCase", awal, anchor)
        page.pace(2.0)
        page.submit_changes()
        page.pace(3.0)
        page.buka_halaman("statistic_safety_recapitulation")
        page.reset_cari_grid()
        baca2 = page.baca_sel_grid_anchor("FirstAidCase", anchor)
        print(f"[statistik] setelah revert+reload: {baca2!r} (harap {awal!r})",
              flush=True)

    # 3) witness: klik Create with Form -> dump semua .modal
    page.buka_halaman("witness_statement_report")
    try:
        page.click_js_saat_tampil(page.BTN_CREATE_FORM)
    except Exception as exc:
        print(f"[witness] klik Create with Form ERROR {type(exc).__name__}: {exc}",
              flush=True)
    for detik in (3, 8, 15):
        time.sleep(detik - (3 if detik == 8 else 8 if detik == 15 else 0))
        dump = driver.execute_script(
            "const out = [];"
            "document.querySelectorAll('.modal, .bootbox').forEach(m => {"
            "  const s = window.getComputedStyle(m);"
            "  const r = m.getBoundingClientRect();"
            "  out.push({cls: (m.className || '').toString().slice(0, 80),"
            "            display: s.display, w: r.width, h: r.height,"
            "            html: m.outerHTML.slice(0, 600)});"
            "});"
            "return out;"
        )
        print(f"[witness] t+{detik}s jumlah .modal={len(dump)} tab={len(driver.window_handles)}",
              flush=True)
        for i, m in enumerate(dump):
            print(f"[witness]   modal#{i}: cls={m['cls']} {m['display']} "
                  f"{m['w']}x{m['h']}", flush=True)
        if dump:
            print(f"[witness]   modal#0 html: {dump[0]['html']}", flush=True)
            break
    # bersihkan kalau ada modal kebuka
    try:
        if page._ada_modal_tampil():
            page.tutup_modal()
    except Exception:
        pass

    print("[SELESAI]", flush=True)
finally:
    driver.quit()
