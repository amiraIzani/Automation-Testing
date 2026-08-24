"""Probe widget upload di form Incident: struktur HTML group Lampiran,
apakah klik anchor memunculkan input[type=file], lalu coba isi file
dummy_hitam.png (gambar hitam boongan) dan Save (debug sementara --
hapus setelah hijau).

    python tools/cek_upload.py
"""
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from config import config
from pages.hss_safety_page import HssSafetyPage

opt = Options()
opt.add_argument("--start-maximized")
opt.add_argument(f"--user-data-dir={config.CHROME_PROFILE_PATH}")
opt.add_argument("--disable-notifications")
opt.add_experimental_option("excludeSwitches", ["enable-automation"])
driver = webdriver.Chrome(options=opt)
driver.implicitly_wait(0)
page = HssSafetyPage(driver)

GAMBAR = str(Path(__file__).resolve().parent / "dummy_hitam.png")

JS_UPLOAD = r"""
const modal = document.querySelector('.modal.show');
if (!modal) return 'modal tidak ada';
const groups = [];
modal.querySelectorAll('.form-group').forEach(g => {
    const a = g.querySelector('.dt-input-upload');
    if (!a) return;
    const l = g.querySelector('label');
    groups.push({label: (l ? l.innerText : '').trim().slice(0, 50),
        html: g.outerHTML.replace(/\s+/g, ' ').slice(0, 700)});
});
const fileInputs = Array.from(modal.querySelectorAll('input[type="file"]'))
    .map(i => ({id: i.id, name: i.getAttribute('name'),
        cls: i.className, tampil: i.getBoundingClientRect().height > 0}));
return {groups, fileInputs};
"""

try:
    page.buka_halaman("incident_investigation_form")
    page.buka_form_create()
    time.sleep(1.5)
    print("== SEBELUM klik upload ==")
    print(driver.execute_script(JS_UPLOAD))

    # klik anchor upload pertama (native)
    klik = driver.execute_script(
        "const a = document.querySelector('.modal.show .dt-input-upload');"
        "if (!a) return false;"
        "const r = a.getBoundingClientRect();"
        "return {x: r.x + r.width / 2, y: r.y + r.height / 2};"
    )
    print("posisi anchor:", klik)
    from selenium.webdriver.common.action_chains import ActionChains
    if klik:
        ActionChains(driver).move_by_offset(
            int(klik["x"]), int(klik["y"])).click().perform()
        ActionChains(driver).move_by_offset(
            -int(klik["x"]), -int(klik["y"])).perform()
    time.sleep(3)
    print("== SETELAH klik anchor ==")
    hasil = driver.execute_script(JS_UPLOAD)
    print("groups:", hasil["groups"][0]["label"] if hasil["groups"] else None)
    print("fileInputs:", hasil["fileInputs"])

    # coba isi file langsung ke input[type=file] yang ada
    els = driver.find_elements("css selector", ".modal.show input[type='file']")
    print("jumlah input file:", len(els))
    for i, el in enumerate(els):
        try:
            el.send_keys(GAMBAR)
            print(f"file dikirim ke input #{i}")
        except Exception as exc:
            print(f"input #{i} gagal:", repr(exc)[:120])
    time.sleep(2)

    # isi form + Save
    page.isi_form_create_otomatis()
    print("form terisi")
    tombol = driver.find_elements(
        "xpath",
        "//div[contains(@class,'modal') and contains(@class,'show')]"
        "//button[normalize-space(.)='Save']",
    )
    if tombol:
        try:
            tombol[0].click()
        except Exception:
            driver.execute_script("arguments[0].click();", tombol[0])
    time.sleep(6)
    state = driver.execute_script(
        "const m = document.querySelector('.modal.show');"
        "const alert = [...document.querySelectorAll('.alert, .bootbox, .swal2-container')]"
        "  .map(a => (a.innerText || '').trim().replace(/\\s+/g, ' ').slice(0, 120))"
        "  .filter(Boolean).slice(0, 6);"
        "return {modalMasih: !!m, alert};"
    )
    print("setelah Save:", state)
except Exception as exc:
    print("GAGAL:", type(exc).__name__, exc)
    import traceback
    traceback.print_exc()
finally:
    try:
        page.batal_form()
    except Exception:
        pass
    driver.quit()
