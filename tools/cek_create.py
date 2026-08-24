"""
tools/cek_create.py
===================
Fokus: perilaku tombol 'Create' (polos) & link Instructions di
Incident Investigation + halaman lain. Cek: modal? baris baru? URL?
tab browser baru?
"""
import os
import sys
import time

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


def jumlah_baris():
    return driver.execute_script(
        "const t = " + page.JS_GRID + ";"
        "return t ? t.querySelectorAll('tbody tr').length : -1;"
    )


def modal_ada():
    return driver.execute_script(
        "return [...document.querySelectorAll('.modal.show')]"
        ".some(m => m.getBoundingClientRect().height > 50);"
    )


# --- Incident: Create polos ---
page.buka_halaman("incident_investigation_form")
log("baris sebelum Create: " + str(jumlah_baris()))
page.click_js_saat_tampil(page.BTN_CREATE)
time.sleep(3)
log("URL setelah Create: " + driver.current_url)
log("modal ada: " + str(modal_ada()))
log("baris setelah Create: " + str(jumlah_baris()))
if modal_ada():
    page.batal_form() if page.is_present(page.BTN_CANCEL_MODAL, timeout=2) else page.tutup_modal()

# --- Instructions: tab baru? ---
handles_awal = driver.window_handles
try:
    page.buka_instruksi()
    time.sleep(3)
    handles_baru = [h for h in driver.window_handles if h not in handles_awal]
    log("tab baru setelah Instructions: " + str(len(handles_baru)))
    if handles_baru:
        driver.switch_to.window(handles_baru[0])
        log("URL tab baru: " + driver.current_url)
        driver.close()
        driver.switch_to.window(handles_awal[0])
    log("modal setelah Instructions: " + str(modal_ada()))
    if modal_ada():
        page.tutup_modal()
except Exception as exc:
    log("instructions: " + repr(exc))

# --- Emergency Drill Daily: Create polos (halaman Create lain) ---
page.buka_halaman("emergency_drill_daily")
log("baris sebelum Create: " + str(jumlah_baris()))
page.click_js_saat_tampil(page.BTN_CREATE)
time.sleep(3)
log("URL setelah Create: " + driver.current_url)
log("modal ada: " + str(modal_ada()))
log("baris setelah Create: " + str(jumlah_baris()))
if modal_ada():
    page.batal_form() if page.is_present(page.BTN_CANCEL_MODAL, timeout=2) else page.tutup_modal()

driver.quit()
with open(os.path.join(config.REPORTS_DIR, "cek_create.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(out))
print("selesai")
