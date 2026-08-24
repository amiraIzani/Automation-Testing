"""
tools/cek_tombol.py
===================
Probe perilaku tombol yang belum pernah dites, di halaman aslinya:
1. SMKP: klik btn-edit baris pertama -> apa yang muncul? tutup.
2. SMKP: klik link Instructions -> apa yang muncul? tutup.
3. SOC Recapitulation: klik Select Finding -> apa yang muncul? tutup.
4. Incident Investigation: klik tombol 'Create' (polos) -> apa? tutup.
5. Safety Recap: klik Export Excel -> file terunduh?
6. Master Alat: klik btn-delete baris AUTO-TEST -> dialog? tolak.
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from config import config
from pages.hss_safety_page import HssSafetyPage

out = []


def log(t):
    print(t, flush=True)
    out.append(str(t))


def dump_modal(driver, tag):
    info = driver.execute_script(
        "return [...document.querySelectorAll('.modal.show')].map(function(m) {"
        "  return {id: m.id,"
        "    teks: (m.innerText || '').replace(/\\n/g, ' ').slice(0, 150),"
        "    tombol: Array.prototype.slice.call("
        "      m.querySelectorAll('button')).map(function(b) {"
        "      return (b.innerText || '').trim().slice(0, 25);"
        "    })};"
        "});"
    )
    log(f"[{tag}] modal.show: {info}")


opt = Options()
opt.add_argument("--start-maximized")
opt.add_argument(f"--user-data-dir={config.CHROME_PROFILE_PATH}")
opt.add_experimental_option("excludeSwitches", ["enable-automation"])
driver = webdriver.Chrome(options=opt)
driver.implicitly_wait(0)
page = HssSafetyPage(driver)

# 1) SMKP btn-edit
page.buka_halaman("smkp")
driver.execute_script(
    "const t = " + page.JS_GRID + ";"
    "const b = t.querySelector('a.btn-edit');"
    "b.click();"
)
time.sleep(2)
dump_modal(driver, "smkp btn-edit")
page.tutup_modal() if page._ada_modal_tampil() else log("[smkp btn-edit] tidak ada modal")

# 2) SMKP Instructions
try:
    page.buka_instruksi()
    time.sleep(2)
    dump_modal(driver, "smkp instructions")
    if page._ada_modal_tampil():
        page.tutup_modal()
except Exception as exc:
    log("instructions error: " + repr(exc))

# 3) SOC Select Finding
page.buka_halaman("soc_recapitulation")
try:
    page.click_js_saat_tampil(page.BTN_SELECT_FINDING)
    time.sleep(2)
    dump_modal(driver, "soc select finding")
    if page._ada_modal_tampil():
        page.tutup_modal()
except Exception as exc:
    log("select finding error: " + repr(exc))

# 4) Incident Create polos
page.buka_halaman("incident_investigation_form")
try:
    page.click_js_saat_tampil(page.BTN_CREATE)
    time.sleep(2)
    dump_modal(driver, "incident create")
    if page._ada_modal_tampil():
        page.tutup_modal()
except Exception as exc:
    log("create error: " + repr(exc))

# 5) Safety Recap Export Excel
page.buka_halaman("safety_recap")
try:
    os.makedirs(config.DOWNLOAD_DIR, exist_ok=True)
    sebelum = set(os.listdir(config.DOWNLOAD_DIR))
    page.click_js_saat_tampil(page.BTN_EXPORT_EXCEL)
    page.jawab_konfirmasi()
    time.sleep(4)
    baru = [n for n in os.listdir(config.DOWNLOAD_DIR) if n not in sebelum]
    log(f"[safety recap export] file baru: {baru}")
except Exception as exc:
    log("export excel error: " + repr(exc))

# 6) Master Alat delete baris dummy
page.buka_halaman("master_alat_keselamatan_operasi")
page.cari_di_grid("AUTO-TEST")
time.sleep(1)
ada_baris = page.tabel_berisi("AUTO-TEST")
log(f"[master alat] baris AUTO-TEST ada: {ada_baris}")
if ada_baris:
    driver.execute_script(
        "const t = " + page.JS_GRID + ";"
        "const b = t.querySelector('a.btn-delete');"
        "if (b) b.click();"
    )
    time.sleep(2)
    dump_modal(driver, "master alat delete dialog")
    # tolak: klik No / Cancel
    ditolak = page._klik_jika_ada((
        By.XPATH,
        "//div[contains(@class,'modal') and contains(@class,'show')]"
        "//button[normalize-space(.)='No' or normalize-space(.)='Cancel'"
        " or normalize-space(.)='Batal']",
    ))
    log("ditolak: " + str(ditolak))
    time.sleep(2)
    log("baris masih ada setelah tolak: " + str(page.tabel_berisi("AUTO-TEST")))

driver.quit()
with open(os.path.join(config.REPORTS_DIR, "cek_tombol.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(out))
print("selesai")
