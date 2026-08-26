"""Probe #5 (2026-08-26): edit grid Statistic vs SMK3 (kontrol).

- Statistic: baca awal -> isi -> baca SEGERA (tanpa submit) -> submit
  -> reload -> baca. Tujuannya tahu di mana perubahannya hilang:
  ketikan tidak masuk sel (immediate tetap awal) ATAU masuk tapi
  tidak disimpan server.
- SMK3 (kontrol): alur yang sama, pastikan helper memang menyimpan
  perubahan di halaman lain -> lalu revert.
"""
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

    # --- Statistic ---
    page.buka_halaman("statistic_safety_recapitulation")
    page.reset_cari_grid()
    page.pace(2.0)
    anchor = {"Month": "January", "TipePegawai": "Pegawai"}
    awal = page.baca_sel_grid_anchor("FirstAidCase", anchor)
    print(f"[statistik] awal={awal!r}", flush=True)
    page.isi_sel_grid_anchor("FirstAidCase", "5", anchor)
    page.pace(1.0)
    segera = page.baca_sel_grid_anchor("FirstAidCase", anchor)
    print(f"[statistik] SEGERA setelah isi: {segera!r}", flush=True)
    el = page._ambil_elemen_sel_anchor("FirstAidCase", anchor)
    state = driver.execute_script(
        "const e = arguments[0];"
        "return e ? {value: e.value, cls: e.className,"
        " html: e.outerHTML.slice(0, 350)} : null;",
        el,
    )
    print(f"[statistik] state sel: {state}", flush=True)
    page.submit_changes()
    page.pace(3.0)
    page.buka_halaman("statistic_safety_recapitulation")
    page.reset_cari_grid()
    akhir = page.baca_sel_grid_anchor("FirstAidCase", anchor)
    print(f"[statistik] SETELAH submit+reload: {akhir!r}", flush=True)
    if akhir != awal:
        page.isi_sel_grid_anchor("FirstAidCase", awal, anchor)
        page.pace(1.0)
        page.submit_changes()
        page.pace(3.0)
        page.buka_halaman("statistic_safety_recapitulation")
        page.reset_cari_grid()
        print(f"[statistik] setelah revert: "
              f"{page.baca_sel_grid_anchor('FirstAidCase', anchor)!r}",
              flush=True)

    # --- SMK3 kontrol ---
    page.buka_halaman("smk3")
    page.reset_cari_grid()
    page.pace(2.0)
    anchor3 = {"Month": "Juli"}
    awal3 = page.baca_sel_grid_anchor("PPkomKetidaksesuaianMaj", anchor3)
    print(f"[smk3] awal={awal3!r}", flush=True)
    if awal3:
        uji3 = str(int(float(awal3)) + 1)
        page.isi_sel_grid_anchor("PPkomKetidaksesuaianMaj", uji3, anchor3)
        page.pace(1.0)
        segera3 = page.baca_sel_grid_anchor("PPkomKetidaksesuaianMaj", anchor3)
        print(f"[smk3] SEGERA setelah isi: {segera3!r}", flush=True)
        page.submit_changes()
        page.pace(3.0)
        page.buka_halaman("smk3")
        page.reset_cari_grid()
        akhir3 = page.baca_sel_grid_anchor("PPkomKetidaksesuaianMaj", anchor3)
        print(f"[smk3] SETELAH submit+reload: {akhir3!r} (harap {uji3!r})",
              flush=True)
        if akhir3 != awal3:
            page.isi_sel_grid_anchor("PPkomKetidaksesuaianMaj", awal3, anchor3)
            page.pace(1.0)
            page.submit_changes()
            page.pace(3.0)
            page.buka_halaman("smk3")
            page.reset_cari_grid()
            print(f"[smk3] setelah revert: "
                  f"{page.baca_sel_grid_anchor('PPkomKetidaksesuaianMaj', anchor3)!r}",
                  flush=True)

    print("[SELESAI]", flush=True)
finally:
    driver.quit()
