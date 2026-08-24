"""
tools/cek_field.py
==================
Cek tipe input tiap kolom di grid Statistic (1317) & SMK3 (1308) +
nilai tbDate/cbDistrict, supaya field yang dipilih untuk test edit
inline benar-benar editable dan aman di-revert.
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

for id_halaman in ("1317", "1308"):
    driver.get(config.BASE_URL + f"Reporting/Timesheet/YearlyReport/Edit?Id={id_halaman}" if id_halaman == "1308" else config.BASE_URL + f"Reporting/Timesheet/MonthlyReport/Edit?Id={id_halaman}")
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
    log(f"\n===== halaman Id={id_halaman} : {driver.current_url} =====")
    tb = driver.execute_script(
        "const i = document.querySelector('#tbDate');"
        "return i ? {val: i.value, type: i.type} : null;"
    )
    log("tbDate: " + str(tb))
    cb = driver.execute_script(
        "const s = document.querySelector('#cbDistrict');"
        "if (!s) return null;"
        "return {val: s.value, opts: Array.from(s.options).map(o => o.text)};"
    )
    log("cbDistrict: " + str(cb))
    fields = driver.execute_script(
        "const t = [...document.querySelectorAll('table.reportData')]"
        ".find(t => t.querySelectorAll('tbody tr').length > 0);"
        "const row0 = t.querySelector('tbody tr');"
        "return [...row0.querySelectorAll('input')].map(i => ({"
        "  field: i.getAttribute('data-fieldname'),"
        "  type: i.type, req: !!i.required, ro: !!i.readOnly,"
        "  val: i.value.slice(0, 40)}));"
    )
    log("input row0: " + str(fields))

driver.quit()
with open(os.path.join(config.REPORTS_DIR, "cek_field.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(out))
print("selesai")
