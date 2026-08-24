"""Debug alur create sungguhan Golden Rules langkah demi langkah
(debug sementara -- hapus setelah hijau).

    python tools/cek_create2.py [kunci_halaman]

Mirip create_dengan_form_sungguhan tapi SETIAP langkah dicatat:
jumlah baris sebelum/sesudah Save, apakah Submit memicu processing,
dan hasil pencarian 'Dummy' setelah reload.
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from config import config
from pages.hss_safety_page import HssSafetyPage

KUNCI = sys.argv[1] if len(sys.argv) > 1 else "golden_rules"

opt = Options()
opt.add_argument("--start-maximized")
opt.add_argument(f"--user-data-dir={config.CHROME_PROFILE_PATH}")
opt.add_argument("--disable-notifications")
opt.add_experimental_option("excludeSwitches", ["enable-automation"])
opt.set_capability("unhandledPromptBehavior", "accept")
driver = webdriver.Chrome(options=opt)
driver.implicitly_wait(0)

page = HssSafetyPage(driver)


def info():
    return driver.execute_script(
        f"const t = {page.JS_GRID};"
        "if (!t) return {baris: -1};"
        "const ins = [...t.querySelectorAll('tbody tr input')];"
        "const isi = ins.map(i => i.value).filter(v => v);"
        "return {baris: t.querySelectorAll('tbody tr').length,"
        "  adaDummy: isi.some(v => v.includes('Dummy')),"
        "  contoh: isi.slice(0, 6)};"
    )


try:
    page.buka_halaman(KUNCI)
    print("[1] halaman terbuka:", driver.current_url)
    print("    grid awal:", info())

    page.buka_form_create()
    print("[2] modal form terbuka")
    page.isi_form_create_otomatis()
    print("[3] field selesai diisi (upload dilewati)")

    # cek nilai field di modal sebelum Save
    nilai = driver.execute_script(
        "const m = document.querySelector('.modal.show');"
        "if (!m) return null;"
        "return [...m.querySelectorAll('input, select, textarea')]"
        ".map(i => ({t: i.getAttribute('type') || i.tagName,"
        " v: (i.value || '').slice(0, 40)}))"
        ".filter(x => x.v);"
    )
    print("    nilai field modal:", nilai)

    page.simpan_form()
    print("[4] Save diklik + modal tertutup")
    print("    grid setelah Save:", info())

    page.submit_changes()
    print("[5] Submit diklik + konfirmasi dijawab")
    print("    grid setelah Submit:", info())

    url_awal = driver.current_url
    driver.get(url_awal)
    for _ in range(60):
        ok = driver.execute_script(
            "const ts = [...document.querySelectorAll('table.reportData')];"
            "return ts.some(t => t.querySelectorAll('tbody tr').length > 0);"
        )
        if ok:
            break
        time.sleep(1)
    print("[6] reload halaman")
    print("    grid setelah reload:", info())

    page.cari_di_grid("Dummy")
    time.sleep(2)
    print("[7] setelah cari 'Dummy':", info())
except Exception as exc:
    print("GAGAL:", type(exc).__name__, exc)
    import traceback
    traceback.print_exc()
finally:
    driver.quit()
