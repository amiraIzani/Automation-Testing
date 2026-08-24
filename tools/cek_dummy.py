"""Cek kenapa penanda 'Dummy' tidak muncul di grid Golden Rules
setelah create + submit (debug sementara -- hapus setelah hijau).

    python tools/cek_dummy.py

Buka halaman, dump nilai tbDate (filter bulan) + baris grid saat ini,
lalu cari 'Dummy' lewat DataTables API dan dump hasil pencariannya
(server-side) -- untuk tahu apakah baris dummy benar2 tersimpan tapi
tersembunyi oleh filter, atau memang tidak tersimpan.
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from config import config

KUNCI = sys.argv[1] if len(sys.argv) > 1 else "golden_rules"

opt = Options()
opt.add_argument("--start-maximized")
opt.add_argument(f"--user-data-dir={config.CHROME_PROFILE_PATH}")
opt.add_experimental_option("excludeSwitches", ["enable-automation"])
driver = webdriver.Chrome(options=opt)
driver.implicitly_wait(0)

driver.get(config.BASE_URL + "Reporting/Timesheet/MonthlyReport/Edit?Id=1316")

for _ in range(60):
    ok = driver.execute_script(
        "const ts = [...document.querySelectorAll('table.reportData')];"
        "return ts.some(t => t.querySelectorAll('tbody tr').length > 0);"
    )
    if ok:
        break
    time.sleep(1)

JS_DUMP = r"""
const t = (() => {
  const ts = [...document.querySelectorAll('table.reportData')];
  const ada = ts.find(x => x.querySelectorAll('tbody tr').length > 0);
  return ada || ts.find(x => x.id && x.id.indexOf('tableData_') === 0) || ts[0] || null;
})();
const dt = (t && window.jQuery) ? jQuery(t).DataTable() : null;
const info = dt ? dt.page.info() : null;
const rows = t ? [...t.querySelectorAll('tbody tr')].slice(0, 8).map(tr => {
  const ins = [...tr.querySelectorAll('input')].map(i => (i.value || '') ).filter(v => v);
  return {teks: (tr.innerText || '').replace(/\s+/g, ' ').slice(0, 150), nilai: ins.slice(0, 6)};
}) : [];
return {
  tanggalFilter: (document.querySelector('#tbDate') || {}).value || null,
  totalRows: info ? info.recordsTotal : -1,
  rowsTampil: info ? info.recordsDisplay : -1,
  halaman: info ? (info.page + 1) + '/' + info.pages : -1,
  baris: rows,
};
"""

print("=== SEBELUM SEARCH ===")
print(driver.execute_script(JS_DUMP))

driver.execute_script(
    "const t = (() => {"
    "  const ts = [...document.querySelectorAll('table.reportData')];"
    "  const ada = ts.find(x => x.querySelectorAll('tbody tr').length > 0);"
    "  return ada || ts.find(x => x.id && x.id.indexOf('tableData_') === 0)"
    "      || ts[0] || null;"
    "})();"
    "if (t && window.jQuery) jQuery(t).DataTable().search('Dummy').draw();"
)
for _ in range(20):
    time.sleep(0.5)
    selesai = driver.execute_script(
        "return !document.querySelector('.dataTables_processing');"
    )
    if selesai:
        break

print("\n=== SETELAH SEARCH 'Dummy' ===")
print(driver.execute_script(JS_DUMP))

driver.quit()
