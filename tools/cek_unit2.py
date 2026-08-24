"""
tools/cek_unit2.py
==================
Reproduksi urutan langkah deep test di SMK3: edit+submit dulu, lalu
filter tanggal, lalu dump opsi cbDistrict yang enabled per tahap.
Juga uji edit di Statistic: apakah sel mana pun bisa tersimpan.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select

from config import config
from pages.hss_safety_page import HssSafetyPage

out = []


def log(t):
    print(t, flush=True)
    out.append(str(t))


def opsi_enabled(page):
    el = page._ambil_js_visible(page.FILTER_UNIT)
    sel = Select(el)
    aktif = int(el.get_attribute("selectedIndex") or 0)
    hasil = []
    for i, o in enumerate(sel.options):
        hasil.append((i, o.get_attribute("value"), o.is_enabled(),
                      "AKTIF" if i == aktif else ""))
    return hasil


opt = Options()
opt.add_argument("--start-maximized")
opt.add_argument(f"--user-data-dir={config.CHROME_PROFILE_PATH}")
opt.add_experimental_option("excludeSwitches", ["enable-automation"])
driver = webdriver.Chrome(options=opt)
driver.implicitly_wait(0)
page = HssSafetyPage(driver)

# ---- SMK3: urutan deep test ----
page.buka_halaman("smk3")
log("\n== SMK3 awal == opsi enabled:")
log(str(opsi_enabled(page)))

# edit dulu (seperti step 1 deep test)
awal = page.baca_sel_grid("PPkomKetidaksesuaianMaj", 0)
log("PPkom awal: " + repr(awal))
page.edit_dan_submit("PPkomKetidaksesuaianMaj", str(int(awal) + 1))
log("setelah edit+submit: " + repr(page.baca_sel_grid("PPkomKetidaksesuaianMaj", 0)))
page.edit_dan_submit("PPkomKetidaksesuaianMaj", awal)
log("setelah revert: " + repr(page.baca_sel_grid("PPkomKetidaksesuaianMaj", 0)))

log("\n== SMK3 setelah edit+submit == opsi enabled:")
log(str(opsi_enabled(page)))

# filter tanggal
page.set_filter_tanggal("2026")
page.tunggu_processing_selesai()
log("\n== SMK3 setelah set tanggal == opsi enabled:")
log(str(opsi_enabled(page)))
log("pilih_unit_enabled_lain -> " + repr(page.pilih_unit_enabled_lain()))

# ---- Statistic: uji edit beberapa field ----
page.buka_halaman("statistic_safety_recapitulation")
for field in ("PenyakitAkibatKerja", "MedicalTreatment", "Nearmiss"):
    try:
        awal = page.baca_sel_grid(field, 0)
        if not awal:
            log(f"\n[statistic.{field}] nilai awal kosong, skip")
            continue
        uji = str(int(float(awal)) + 1)
        page.edit_dan_submit(field, uji)
        kini = page.baca_sel_grid(field, 0)
        log(f"[statistic.{field}] awal={awal} submit={uji} hasil={kini}")
        if kini == uji:
            page.edit_dan_submit(field, awal)
            log(f"  revert -> {page.baca_sel_grid(field, 0)!r}")
    except Exception as exc:
        log(f"[statistic.{field}] ERROR: {exc!r}")

driver.quit()
with open(os.path.join(config.REPORTS_DIR, "cek_unit2.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(out))
print("selesai")
