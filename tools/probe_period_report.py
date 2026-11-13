"""Probe: bandingkan halaman Reporting lama (Timesheet/*/View) dengan
URL baru di menu (PeriodReport/View) -- terlihat 2026-09-11.

Untuk tiap Id: buka URL lama & baru, catat URL akhir (redirect?),
judul panel, dan elemen yang dipakai page object (tabel reportData,
filter tbDate/cbDistrict, tombol toolbar). Juga cari link Safety Recap
di seluruh sidebar. READ-ONLY: tidak mengklik tombol apa pun."""
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

from config import config

HALAMAN = {
    1306: "Timesheet/MonthlyReport/View",
    1324: "Timesheet/YearlyReport/View",
    1325: "Timesheet/YearlyReport/View",
    1323: "Timesheet/YearlyReport/View",
}
OUT = os.getenv("PROBE_OUT", ".")

JS_ELEMEN = """
const tampil = el => !!el && el.getBoundingClientRect().height > 0
  && getComputedStyle(el).visibility !== 'hidden';
const cek = sel => {
  const all = [...document.querySelectorAll(sel)];
  return all.length ? (all.some(tampil) ? 'tampil' : 'ada-tersembunyi') : '-';
};
const tombol = [...document.querySelectorAll('button, a.btn')]
  .filter(tampil).map(b => (b.innerText || '').trim()).filter(Boolean);
const panel = document.querySelector('.panel-hdr h2, .panel-hdr, h1');
return {
  judul: panel ? panel.innerText.trim().replace(/\\s+/g, ' ').slice(0, 120) : '',
  tabel_reportData: cek('table.reportData.dataTable'),
  tbDate: cek('#tbDate'), cbDistrict: cek('#cbDistrict'),
  btnExport: cek('#btnExport'), btnCancel: cek('#btnCancel'),
  btnReloadData: cek('#btnReloadData'),
  tombol: [...new Set(tombol)].slice(0, 25),
};
"""

options = Options()
options.add_argument("--start-maximized")
options.add_argument(f"--user-data-dir={config.CHROME_PROFILE_PATH}")
options.add_argument("--disable-notifications")
options.add_experimental_option("excludeSwitches", ["enable-automation"])

d = webdriver.Chrome(options=options)
d.implicitly_wait(0)
base = config.BASE_URL.rstrip("/")


def buka(url):
    d.get(url)
    WebDriverWait(d, config.LONG_TIMEOUT).until(
        lambda x: x.execute_script("return document.readyState") == "complete"
    )
    time.sleep(6)  # beri waktu DataTables render (probe saja)


try:
    for id_, lama in HALAMAN.items():
        for label, path in (("LAMA", f"Reporting/{lama}?Id={id_}"),
                            ("BARU", f"Reporting/PeriodReport/View?Id={id_}")):
            buka(f"{base}/{path}")
            info = d.execute_script(JS_ELEMEN)
            print(f"\n[{id_} {label}] {path}")
            print(f"  url akhir : {d.current_url}")
            for k, v in info.items():
                print(f"  {k:<16}: {v}")
            if label == "BARU":
                d.save_screenshot(os.path.join(OUT, f"period_{id_}.png"))

    buka(base)
    recap = d.execute_script(
        "return [...document.querySelectorAll(\"nav a[href*='SafetyRecap']\")]"
        ".map(a => {"
        "  const r = []; let li = a.closest('li');"
        "  li = li ? li.parentElement.closest('li') : null;"
        "  while (li) { const s = li.querySelector(':scope > a span');"
        "    r.unshift(s ? s.innerText.trim() : '?');"
        "    li = li.parentElement.closest('li'); }"
        "  return {href: a.getAttribute('href'), text: a.innerText.trim(),"
        "          rantai: r.join(' > ')};"
        "});"
    )
    print("\n[Safety Recap di sidebar]", recap or "TIDAK ADA")
finally:
    d.quit()
