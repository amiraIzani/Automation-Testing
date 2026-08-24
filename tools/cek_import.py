"""
tools/cek_import.py
===================
Cek struktur modal Import di halaman Lagging (SMKP Id=1307): id elemen
di dalam modal (link template, input file, tombol), supaya helper
import di page object bisa dipakai dengan benar.
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from config import config

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

url = config.BASE_URL + "Reporting/Timesheet/YearlyReport/Edit?Id=1307"
driver.get(url)

for _ in range(60):
    ok = driver.execute_script(
        "const ts = [...document.querySelectorAll('table.reportData')];"
        "return ts.some(t => {const r = t.getBoundingClientRect();"
        "  const s = window.getComputedStyle(t);"
        "  return s.display !== 'none' && r.height > 10"
        "    && t.querySelectorAll('tbody tr').length > 0;});"
    )
    if ok:
        break
    time.sleep(1)
log("URL: " + driver.current_url)

# klik tombol Import
btn = driver.find_element(By.XPATH, "//button[normalize-space(.)='Import']")
driver.execute_script("arguments[0].click();", btn)
for _ in range(15):
    ada = driver.execute_script(
        "const m = document.querySelector('#modalImport');"
        "if (!m) return false;"
        "const s = window.getComputedStyle(m);"
        "const r = m.getBoundingClientRect();"
        "return s.display !== 'none' && s.visibility !== 'hidden' && r.height > 0;"
    )
    if ada:
        break
    time.sleep(1)
log("modalImport tampil: " + str(ada))

# dump semua elemen penting di dalam modal
info = driver.execute_script(
    "const m = document.querySelector('#modalImport');"
    "if (!m) return 'TIDAK ADA #modalImport';"
    "const ids = [...m.querySelectorAll('[id]')].map(e => ({"
    "  id: e.id, tag: e.tagName, type: e.getAttribute('type'),"
    "  cls: (e.className || '').toString().slice(0, 70),"
    "  teks: (e.innerText || '').slice(0, 60)}));"
    "const links = [...m.querySelectorAll('a')].map(a => ({"
    "  href: a.getAttribute('href'), id: a.id, teks: a.innerText.slice(0, 60)}));"
    "const inputs = [...m.querySelectorAll('input')].map(i => ({"
    "  id: i.id, name: i.name, type: i.getAttribute('type')}));"
    "const btns = [...m.querySelectorAll('button')].map(b => ({"
    "  id: b.id, teks: (b.innerText || '').trim().slice(0, 40),"
    "  cls: (b.className || '').toString().slice(0, 70)}));"
    "return {ids: ids, links: links, inputs: inputs, buttons: btns};"
)
log("isi modalImport: " + str(info))

driver.quit()
with open(os.path.join(config.REPORTS_DIR, "cek_import.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(out))
print("selesai")
