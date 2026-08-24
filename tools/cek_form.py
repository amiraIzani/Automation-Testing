"""Cek struktur field modal Create with Form beberapa halaman (debug
sementara -- hapus setelah suite hijau).

    python tools/cek_form.py

Membuka profil Chrome yang sama dengan pytest (session login masih
aktif), buka modal Create with Form, lalu dump struktur field: label,
tag, type, required + snippet outerHTML group (dipotong). Modal
DITUTUP lewat Cancel -- tidak menyimpan apa pun ke server.
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from config import config
from pages.hss_safety_page import HssSafetyPage

# Ambil kunci halaman dari argumen (default dua halaman yang sedang di-debug).
KUNCI = sys.argv[1:] or ["golden_rules", "mwt_daily"]

JS_DUMP = r"""
const modal = document.querySelector('.modal.show');
if (!modal) return {error: 'modal tidak ada'};
const out = [];
modal.querySelectorAll('.form-group').forEach(g => {
    const l = g.querySelector('label');
    const teks = l ? (l.innerText || '').trim() : '';
    if (!teks) return;
    const r = g.getBoundingClientRect();
    const f = g.querySelector('input, select, textarea');
    const e = {label: teks, tampil: r.width > 0 && r.height > 0};
    if (f) {
        e.tag = f.tagName;
        e.type = f.getAttribute('type') || '';
        e.required = !!f.required;
        e.hiddenAttr = !!f.getAttribute('hidden');
        e.display = window.getComputedStyle(f).display;
        e.html = g.outerHTML.slice(0, 400);
    } else {
        // group TANPA input/select/textarea (mis. widget upload) --
        // dump html lebih panjang + cari input file di SELURUH modal
        e.html = g.outerHTML.replace(/\s+/g, ' ').slice(0, 900);
        e.modalFileInputs = Array.from(
            modal.querySelectorAll('input[type="file"]')).map(i =>
            ({id: i.id, cls: i.className, name: i.getAttribute('name')}));
    }
    out.push(e);
});
return out;
"""


def main():
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument(f"--user-data-dir={config.CHROME_PROFILE_PATH}")
    options.add_argument("--disable-notifications")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(0)

    page = HssSafetyPage(driver)
    for kunci in KUNCI:
        print(f"\n===== {kunci} =====")
        try:
            page.buka_halaman(kunci)
            page.buka_form_create()
            time.sleep(1)
            fields = driver.execute_script(JS_DUMP)
            if isinstance(fields, dict) and fields.get("error"):
                print("ERROR:", fields["error"])
                continue
            for f in fields:
                print(f"- {f['label']!r} tampil={f['tampil']} "
                      f"tag={f.get('tag')} type={f.get('type')!r} "
                      f"required={f.get('required')} hidden={f.get('hiddenAttr')} "
                      f"display={f.get('display')}")
                if f.get("html"):
                    print("  HTML:", f["html"].replace("\n", " ")[:380])
            # tutup TANPA menyimpan
            page.batal_form()
            print("(modal ditutup, tidak menyimpan apa pun)")
        except Exception as exc:
            print("GAGAL:", repr(exc))
            try:
                page.batal_form()
            except Exception:
                pass
    driver.quit()


if __name__ == "__main__":
    main()
