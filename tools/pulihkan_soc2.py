"""
tools/pulihkan_soc2.py
======================
Coba hapus baris draft kosong di SOC dengan klik MOUSE asli
(ActionChains) + amati dialog konfirmasi yang muncul.
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains

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
page.buka_halaman("soc_recapitulation")

# klik Delete baris kosong dengan mouse asli (cari ulang tiap retry
# -- grid sering redraw / elemen stale)
JS_CARI = (
    "const t = " + page.JS_GRID + ";"
    "const tr = [...t.querySelectorAll('tbody tr')].find(r => {"
    "  const ins = [...r.querySelectorAll('input')];"
    "  return ins.length > 0 && ins.every(i => i.value === '');"
    "});"
    "return tr ? tr.querySelector('a.btn-delete') : null;"
)
for _ in range(3):
    try:
        el = driver.execute_script(JS_CARI)
        if el is None:
            log("tidak ada tombol delete baris kosong")
            break
        ActionChains(driver).move_to_element(el).click().perform()
        log("klik mouse asli dilakukan")
        break
    except Exception as exc:
        log("klik gagal (retry): " + repr(exc))
        time.sleep(1)
time.sleep(2)
log("modal tampil: " + str(page._ada_modal_tampil()))
info = driver.execute_script(
    "return [...document.querySelectorAll('.modal')].map(function(m) {"
    "  const s = window.getComputedStyle(m);"
    "  const r = m.getBoundingClientRect();"
    "  return {id: m.id, cls: m.className,"
    "    tampil: s.display !== 'none' && s.visibility !== 'hidden'"
    "      && r.height > 0,"
    "    tombol: Array.prototype.slice.call(m.querySelectorAll('button'))"
    "      .map(function(b) { return (b.innerText || '').trim().slice(0, 20);"
    "      })};"
    "});"
)
log("modal: " + str(info))

# jawab Ya (bootbox-accept atau tombol Yes)
page.jawab_konfirmasi(timeout=6)
time.sleep(2)
page.tunggu_processing_selesai()

page.buka_halaman("soc_recapitulation")
jumlah = driver.execute_script(
    "const t = " + page.JS_GRID + ";"
    "return t ? t.querySelectorAll('tbody tr').length : -1;"
)
log("jumlah baris sesudah: " + str(jumlah))

driver.quit()
with open(os.path.join(config.REPORTS_DIR, "pulihkan_soc2.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(out))
print("selesai")
