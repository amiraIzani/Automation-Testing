"""
tools/cek_modal2.py
===================
1) SMKP: buka modal Import -> klik Download Template -> dump kondisi
   semua .modal.show + tombol -> coba tutup berbagai cara.
2) Statistic: buka fresh -> dump tombol toolbar (id+teks) -> cek
   Reload Data ada/tidak.
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

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

# ---- 1) SMKP modal ----
page.buka_halaman("smkp")
page.buka_modal_import()
log("modal terbuka: " + str(page._ada_modal_tampil()))

state = driver.execute_script(
    "return [...document.querySelectorAll('.modal')].map(m => ({"
    "  id: m.id, cls: m.className,"
    "  tampil: (() => {const s = window.getComputedStyle(m);"
    "    const r = m.getBoundingClientRect();"
    "    return s.display !== 'none' && s.visibility !== 'hidden'"
    "      && r.height > 0;})(),"
    "  tombol: [...m.querySelectorAll('button')].map(b =>"
    "    ((b.innerText || '').trim().slice(0, 20) || b.className)"
    "      .slice(0, 40))"
    "}));"
)
log("semua modal: " + str(state))

# klik download template
page.download_template_import()
log("setelah klik template, file terunduh")
time.sleep(1)
log("modal masih tampil: " + str(page._ada_modal_tampil()))

# coba tutup via klik X langsung
hasil_x = driver.execute_script(
    "const m = document.querySelector('#modalImport');"
    "if (!m) return 'modalImport hilang';"
    "const x = m.querySelector('button.close');"
    "if (!x) return 'tidak ada button.close';"
    "x.click(); return 'klik X ok';"
)
log("aksi: " + str(hasil_x))
time.sleep(2)
log("setelah klik X: " + str(page._ada_modal_tampil()))

# kalau masih tampil, klik Close teks
if page._ada_modal_tampil():
    hasil_c = driver.execute_script(
        "const m = document.querySelector('#modalImport');"
        "const b = [...m.querySelectorAll('button')]"
        ".find(x => (x.innerText || '').trim() === 'Close');"
        "if (!b) return 'tidak ada tombol Close';"
        "b.click(); return 'klik Close ok';"
    )
    log("aksi: " + str(hasil_c))
    time.sleep(2)
    log("setelah klik Close: " + str(page._ada_modal_tampil()))

if page._ada_modal_tampil():
    driver.find_element(By.CSS_SELECTOR, "body").send_keys(Keys.ESCAPE)
    time.sleep(2)
    log("setelah ESC: " + str(page._ada_modal_tampil()))

# ---- 2) Statistic toolbar ----
page.buka_halaman("statistic_safety_recapitulation")
toolbar = driver.execute_script(
    "const ids = ['btnReloadData', 'btnImport', 'btnSubmit', 'btnExport',"
    " 'btnCancel', 'tbDate', 'cbDistrict'];"
    "const out = {};"
    "ids.forEach(i => {"
    "  const el = document.getElementById(i);"
    "  if (!el) { out[i] = 'TIDAK ADA'; return; }"
    "  const s = window.getComputedStyle(el);"
    "  const r = el.getBoundingClientRect();"
    "  out[i] = (s.display !== 'none' && s.visibility !== 'hidden'"
    "    && r.height > 0) ? 'TAMPIL' : 'HIDDEN';"
    "});"
    "const btns = [...document.querySelectorAll('button')]"
    "  .map(b => (b.innerText || '').trim()).filter(t => t);"
    "out['_semuaTeksTombol'] = btns;"
    "return out;"
)
log("statistic toolbar: " + str(toolbar))

driver.quit()
with open(os.path.join(config.REPORTS_DIR, "cek_modal2.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(out))
print("selesai")
