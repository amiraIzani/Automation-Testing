"""
tools/cek_district.py
=====================
Cek opsi cbDistrict yang ENABLED (bisa dipilih) di 3 halaman Lagging.
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from config import config

opt = Options()
opt.add_argument("--start-maximized")
opt.add_argument(f"--user-data-dir={config.CHROME_PROFILE_PATH}")
opt.add_experimental_option("excludeSwitches", ["enable-automation"])
driver = webdriver.Chrome(options=opt)
driver.implicitly_wait(0)

halaman = {
    "1317": "Reporting/Timesheet/MonthlyReport/Edit?Id=1317",
    "1308": "Reporting/Timesheet/YearlyReport/Edit?Id=1308",
    "1307": "Reporting/Timesheet/YearlyReport/Edit?Id=1307",
}
for id_h, url in halaman.items():
    driver.get(config.BASE_URL + url)
    for _ in range(60):
        ok = driver.execute_script(
            "const s = document.querySelector('#cbDistrict');"
            "return !!s && window.getComputedStyle(s).display !== 'none';"
        )
        if ok:
            break
        time.sleep(1)
    opsi = driver.execute_script(
        "const s = document.querySelector('#cbDistrict');"
        "return Array.from(s.options).map(o => ({"
        "  t: o.text, d: o.disabled, sel: o.selected}));"
    )
    enabled = [o["t"] for o in opsi if not o["d"]]
    print(f"\nId={id_h} enabled: {enabled}")
    print("semua:", [(o["t"][:30], "disabled" if o["d"] else "OK") for o in opsi])

driver.quit()
print("selesai")
