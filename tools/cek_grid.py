"""
tools/cek_grid.py
=================
Cek struktur grid inline-edit di halaman Lagging (SMKP Id=1307):
apakah sel bisa diedit (input dalam td?), dan alur edit -> Submit.
Tulis hasil ke reports/cek_grid.txt. Cepat -- hanya 1 halaman.
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

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

# tunggu tabel tampil
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

info = driver.execute_script(
    "const t = [...document.querySelectorAll('table.reportData')]"
    ".find(t => t.querySelectorAll('tbody tr').length > 0);"
    "if (!t) return 'tidak ada tabel berisi';"
    "const tr = t.querySelector('tbody tr');"
    "const cells = [...tr.children].map(td => {"
    "  const inp = td.querySelector('input');"
    "  return {th: td.getAttribute('data-name') || td.innerText.slice(0,20),"
    "    tag: td.tagName, cls: td.className,"
    "    adaInput: !!inp,"
    "    inputType: inp ? inp.getAttribute('type') : null,"
    "    inputValue: inp ? inp.value : null,"
    "    inputClass: inp ? inp.className : null,"
    "    tdHtml: td.outerHTML.slice(0, 220)};"
    "});"
    "return {id: t.id, kelas: t.className, jumlahBaris:"
    "  t.querySelectorAll('tbody tr').length, selPertama: cells};"
)
log("struktur grid: " + str(info))

# coba klik satu input di baris pertama lalu ubah nilainya (tanpa submit)
driver.execute_script(
    "const t = [...document.querySelectorAll('table.reportData')]"
    ".find(t => t.querySelectorAll('tbody tr').length > 0);"
    "const inp = t.querySelector('tbody tr input');"
    "if (inp) { inp.click(); inp.focus(); }"
)
time.sleep(2)
log("setelah klik input pertama")

driver.quit()
with open(os.path.join(config.REPORTS_DIR, "cek_grid.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(out))
print("selesai")
