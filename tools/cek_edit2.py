"""
tools/cek_edit2.py
==================
1) Cek & restore AuditExecutionDate baris pertama SMK3 (mungkin rusak
   oleh run test sebelumnya yang memakai send_keys datetime-local).
2) Probe field mana yang BENAR2 editable (nilai tersimpan setelah
   Submit) di SMK3 & Statistic: kandidat field number diubah +1 lalu
   DIKEMBALIKAN. Hasil di reports/cek_edit2.txt.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from config import config
from pages.hss_safety_page import HssSafetyPage

out = []


def log(t):
    print(t, flush=True)
    out.append(str(t))


opt = Options()
opt.add_argument("--start-maximized")
opt.add_argument(f"--user-data-dir={config.CHROME_PROFILE_PATH}")
opt.add_experimental_option("excludeSwitches", ["enable-automation"])
driver = webdriver.Chrome(options=opt)
driver.implicitly_wait(0)
page = HssSafetyPage(driver)

# ---- 1) cek & restore SMK3 AuditExecutionDate ----
page.buka_halaman("smk3")
tanggal = page.baca_sel_grid("AuditExecutionDate", baris=0)
log("SMK3 AuditExecutionDate row0 sekarang: " + repr(tanggal))
ASLI = "2026-07-10T08:31"
if tanggal != ASLI:
    page.edit_dan_submit("AuditExecutionDate", ASLI)
    log("restore -> " + repr(page.baca_sel_grid("AuditExecutionDate", baris=0)))

# ---- 2) probe field editable SMK3 ----
def probe(kunci, field):
    try:
        page.buka_halaman(kunci)
        awal = page.baca_sel_grid(field, baris=0)
        log(f"\n[{kunci}.{field}] nilai awal: {awal!r}")
        if not awal:
            log("  -> nilai awal kosong, skip")
            return False
        uji = str(int(float(awal)) + 1)
        page.edit_dan_submit(field, uji)
        kini = page.baca_sel_grid(field, baris=0)
        log(f"  setelah submit: {kini!r}")
        berhasil = kini == uji
        if berhasil:
            page.edit_dan_submit(field, awal)
            log(f"  revert -> {page.baca_sel_grid(field, baris=0)!r}")
        return berhasil
    except Exception as exc:
        log(f"  ERROR: {exc!r}")
        return False


for f in ("PPkomKetidaksesuaianMaj", "PPkomKesesuaian", "TotalScore"):
    probe("smk3", f)

for f in ("FirstAidCase", "JumlahAccidentRingan", "PenyakitAkibatKerja"):
    probe("statistic_safety_recapitulation", f)

driver.quit()
with open(os.path.join(config.REPORTS_DIR, "cek_edit2.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(out))
print("selesai")
