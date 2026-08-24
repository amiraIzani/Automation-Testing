"""Cek perilaku search grid + akumulasi baris dummy + validasi form
Incident (debug sementara -- hapus setelah hijau).

    python tools/cek_verif.py master_alat
    python tools/cek_verif.py mwt_daily
    python tools/cek_verif.py incident

- master_alat/mwt_daily: totalRows, halaman, hasil search 'Dummy'
  dan 'AUTO-TEST' (apakah dt.search benar2 memfilter server-side).
- incident: buka modal create, dump SEMUA form-group (termasuk tab
  tersembunyi) + field wajib, isi otomatis, Save, kalau validasi
  gagal dump field yang invalid/kosong.
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from config import config
from pages.hss_safety_page import HssSafetyPage

MODE = sys.argv[1] if len(sys.argv) > 1 else "master_alat"

opt = Options()
opt.add_argument("--start-maximized")
opt.add_argument(f"--user-data-dir={config.CHROME_PROFILE_PATH}")
opt.add_argument("--disable-notifications")
opt.add_experimental_option("excludeSwitches", ["enable-automation"])
driver = webdriver.Chrome(options=opt)
driver.implicitly_wait(0)
page = HssSafetyPage(driver)

JS_GRID_INFO = r"""
const t = (() => {
  const ts = [...document.querySelectorAll('table.reportData')];
  const ada = ts.find(x => x.querySelectorAll('tbody tr').length > 0);
  return ada || ts.find(x => x.id && x.id.indexOf('tableData_') === 0) || ts[0] || null;
})();
const dt = (t && window.jQuery) ? jQuery(t).DataTable() : null;
const info = dt ? dt.page.info() : null;
const baris = t ? [...t.querySelectorAll('tbody tr')].slice(0, 5).map(tr => {
  const ins = [...tr.querySelectorAll('input')].map(i => (i.value || '')).filter(v => v);
  return ins.slice(0, 4);
}) : [];
return {
  total: info ? info.recordsTotal : -1,
  tampil: info ? info.recordsDisplay : -1,
  halaman: info ? (info.page + 1) + '/' + info.pages : -1,
  contoh: baris,
};
"""


def cari(teks):
    driver.execute_script(
        "const t = (() => {"
        "  const ts = [...document.querySelectorAll('table.reportData')];"
        "  const ada = ts.find(x => x.querySelectorAll('tbody tr').length > 0);"
        "  return ada || ts.find(x => x.id && x.id.indexOf('tableData_') === 0)"
        "      || ts[0] || null;"
        "})();"
        "if (t && window.jQuery) jQuery(t).DataTable().search(arguments[0]).draw();",
        teks,
    )
    for _ in range(30):
        time.sleep(0.5)
        if not driver.execute_script(
            "return !!document.querySelector('.dataTables_processing');"
        ):
            break


def grid_info():
    return driver.execute_script(JS_GRID_INFO)


if MODE in ("master_alat", "mwt_daily"):
    kunci = {
        "master_alat": "master_alat_keselamatan_operasi",
        "mwt_daily": "mwt_daily",
    }[MODE]
    page.buka_halaman(kunci)
    time.sleep(2)
    print(f"[{MODE}] tanpa search:", grid_info())
    cari("Dummy")
    print(f"[{MODE}] search 'Dummy':", grid_info())
    cari("AUTO-TEST")
    print(f"[{MODE}] search 'AUTO-TEST':", grid_info())
    cari("")
    print(f"[{MODE}] search kosong :", grid_info())
    driver.quit()
    sys.exit(0)

# MODE == incident
page.buka_halaman("incident_investigation_form")
page.buka_form_create()
time.sleep(1.5)

dump = driver.execute_script(r"""
const modal = document.querySelector('.modal.show');
const tab = [...modal.querySelectorAll('a[data-toggle="tab"]')]
    .map(a => (a.innerText || '').trim()).filter(Boolean);
const groups = [];
modal.querySelectorAll('.form-group').forEach(g => {
    const l = g.querySelector('label');
    const teks = l ? (l.innerText || '').trim() : '';
    if (!teks) return;
    const r = g.getBoundingClientRect();
    const f = g.querySelector('input, select, textarea');
    const e = {label: teks, tampil: r.height > 0 && r.width > 0,
        required: f ? !!f.required : false,
        type: f ? (f.getAttribute('type') || f.tagName).toLowerCase() : null,
        lookup: !!g.querySelector('.dt-input-lookup-hidden')};
    if (e.required || !e.tampil) groups.push(e);
});
return {tab, wajibAtautTersembunyi: groups};
""")
print("tab modal:", dump["tab"])
print("field wajib / tersembunyi:")
for g in dump["wajibAtautTersembunyi"]:
    print(f"  - {g['label']!r} tampil={g['tampil']} required={g['required']} "
          f"type={g['type']} lookup={g['lookup']}")

# isi semua field yang tampil, lalu Save (klik NATIVE sekali saja) --
# amati XHR + apakah modal tertutup
try:
    page.isi_form_create_otomatis()
    print("field tampil terisi")
    dump_select = driver.execute_script(r"""
const modal = document.querySelector('.modal.show');
if (!modal) return [];
const out = [];
modal.querySelectorAll('.form-group').forEach(g => {
    const sel = g.querySelector('select');
    if (!sel) return;
    const l = g.querySelector('label');
    const rect = g.getBoundingClientRect();
    out.push({label: (l ? l.innerText : '').trim().slice(0, 45),
        tampil: rect.height > 0,
        val: sel.value,
        opsi: Array.from(sel.options).map(o => o.text.trim()).slice(0, 12)});
});
return out;
""")
    print("semua SELECT di modal:")
    for s in dump_select:
        print(f"  - {s['label']!r} tampil={s['tampil']} val={s['val']!r}")
        print(f"    opsi: {s['opsi']}")
    tombol_save = driver.find_elements(
        "xpath",
        "//div[contains(@class,'modal') and contains(@class,'show')]"
        "//button[normalize-space(.)='Save']",
    )
    if tombol_save:
        print("Save native click...")
        try:
            tombol_save[0].click()
        except Exception as exc:
            print("native click error:", exc)
            driver.execute_script("arguments[0].click();", tombol_save[0])
    else:
        print("tombol Save tidak ketemu")
    time.sleep(5)
    net = driver.execute_script(r"""
const perf = performance.getEntriesByType('resource')
    .filter(e => e.initiatorType === 'xmlhttprequest' || e.initiatorType === 'fetch')
    .map(e => (e.name || '').slice(0, 130));
return perf.slice(-8);
""")
    print("XHR terakhir:", net)
    dump2 = driver.execute_script(r"""
const modal = document.querySelector('.modal.show');
const alert = [...document.querySelectorAll('.alert, .bootbox, .invalid-feedback, .toast, .sweetalert-container, .swal2-container')]
    .map(a => (a.innerText || '').trim().replace(/\s+/g, ' ').slice(0, 150)).filter(Boolean).slice(0, 8);
const invalid = [];
if (modal) modal.querySelectorAll('input, select, textarea').forEach(f => {
    const cls = (f.className || '').toString();
    const kosong = f.required && !(f.value || '').trim();
    if (/is-invalid|error|has-error/i.test(cls) || kosong)
        invalid.push({tag: f.tagName, tipe: f.getAttribute('type') || '',
            required: !!f.required, kosong, cls: cls.slice(0, 60)});
});
return {modalMasih: !!modal, alert, invalid};
""")
    print("state:", dump2)
    if dump2["modalMasih"]:
        print("-> modal MASIH terbuka (Save ditolak)")
    else:
        print("-> modal TERTUTUP (Save diterima)")
except Exception as exc:
    print("GAGAL:", type(exc).__name__, str(exc)[:120])
finally:
    try:
        page.batal_form()
        print("(form dibatalkan -- tidak menyimpan)")
    except Exception:
        pass
driver.quit()
