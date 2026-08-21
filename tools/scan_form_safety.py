"""
tools/scan_form_safety.py
=========================
Scan modal "Create with Form" SEMUA halaman transaction Safety yang
punya tombol Create, lalu simpan daftar field (label + jenis + opsi
select) ke reports/scan/safety/forms/<kunci>.json.

Hasilnya dipakai untuk menyusun data/test_data.json -- Zahra tinggal
mengisi NILAI per label, tanpa harus membuka modal satu per satu.

    python tools/scan_form_safety.py

Tidak menyimpan data apapun ke server (modal selalu ditutup pakai
Cancel/Close setelah discan).
"""

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from pages.hss_safety_page import HssSafetyPage

REPORTS_DIR = Path(__file__).resolve().parent.parent / "reports" / "scan" / "safety"
OUT_DIR = REPORTS_DIR / "forms"

# Halaman transaction yang punya tombol "Create with Form" (hasil scan 2026-08-20).
HALAMAN_CREATE = [
    "incident_investigation_form",
    "initial_incident_accident_report",
    "witness_statement_report",
    "emergency_drill_daily",
    "master_alat_keselamatan_operasi",
    "soc_recapitulation",
    "golden_rules",
    "safety_kkp_p2k3_committee_meeting",
    "mwt_daily",
]

# Pola sama dengan FIELD_BY_LABEL di HssSafetyPage (label ->
# container saudaranya -> field pertama di dalamnya), supaya hasil
# scan 1:1 dengan field yang akan diisi automation nanti.
JS_SCAN = r"""
const modal = document.querySelector('.modal.show');
if (!modal) return {error: 'modal tidak ada'};
const tabs = Array.from(modal.querySelectorAll('a[data-toggle="tab"]'))
    .map(a => (a.innerText || '').trim()).filter(Boolean);
const out = [];
modal.querySelectorAll('label').forEach(l => {
    const rect = l.getBoundingClientRect();
    const tampil = rect.width > 0 && rect.height > 0;
    const teks = (l.innerText || '').trim();
    if (!teks) return;
    // telusuri sibling berikutnya (max 5 tingkat) cari field pertama
    let f = null, sib = l.nextElementSibling, guard = 0;
    while (sib && guard < 5) {
        f = sib.querySelector('input, select, textarea');
        if (f) break;
        sib = sib.nextElementSibling;
        guard++;
    }
    let field = null;
    if (f) {
        field = {
            tag: f.tagName,
            type: f.getAttribute('type') || '',
            required: f.required || false,
            placeholder: f.placeholder || '',
        };
        if (f.tagName === 'SELECT') {
            const total = f.options.length;
            const opsi = Array.from(f.options)
                .map(o => o.text.trim())
                .filter(t => t && !t.includes('Pilih'))
                .slice(0, 60);
            field.options = opsi;
            if (opsi.length < total) field.options.push(`... (+${total - opsi.length} opsi lain)`);
        }
    }
    out.push({label: teks, tampil, field});
});
return {tabs, fields: out};
"""


def main():
    options = Options()
    options.debugger_address = "127.0.0.1:9222"
    driver = webdriver.Chrome(options=options)
    driver.switch_to.window(driver.window_handles[-1])

    page = HssSafetyPage(driver)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ringkasan = {}

    for kunci in HALAMAN_CREATE:
        try:
            page.buka_halaman(kunci)
            page.click(page.BTN_CREATE_FORM)
            page.tunggu_modal_terbuka()
            hasil = driver.execute_script(JS_SCAN)
            if isinstance(hasil, dict) and hasil.get("error"):
                raise RuntimeError(hasil["error"])

            data = {
                "kunci": kunci,
                "url": driver.current_url,
                "waktu": time.strftime("%Y-%m-%d %H:%M:%S"),
                "tab_modal": hasil.get("tabs", []),
                "field_tampil": [f for f in hasil["fields"] if f["tampil"]],
                "field_tersembunyi": [f["label"] for f in hasil["fields"] if not f["tampil"]],
            }
            (OUT_DIR / f"{kunci}.json").write_text(
                json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
            )

            # Tutup modal (batal -- TIDAK menyimpan data ke server)
            try:
                page.batal_form()
            except Exception:
                page.click(page.BTN_CLOSE_MODAL)
                page.tunggu_modal_tertutup()

            n = len(data["field_tampil"])
            ringkasan[kunci] = {"field_tampil": n, "tab": data["tab_modal"]}
            print(f"OK  {kunci:<38} {n} field tampil | tab: {data['tab_modal']}", flush=True)
        except Exception as exc:
            print(f"!!  {kunci:<38} ERROR: {exc}", flush=True)
            try:
                page.take_screenshot(f"scan_form_gagal_{kunci}")
            except Exception:
                pass
            try:
                page.click(page.BTN_CLOSE_MODAL)
            except Exception:
                pass

    (OUT_DIR / "_ringkasan.json").write_text(
        json.dumps(ringkasan, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print()
    print(f"Selesai: {len(ringkasan)}/{len(HALAMAN_CREATE)} form terscan -> {OUT_DIR}")


if __name__ == "__main__":
    main()
