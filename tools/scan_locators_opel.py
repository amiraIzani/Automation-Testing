"""
tools/scan_locators_opel.py
===========================
Scanner locator untuk website OPEL (https://dev-opel.antm.tech/).

Adaptasi dari scan_locators_v2.py (project NewDLA), tapi dibuat GENERIC
(tidak mengasumsikan ExtJS) karena framework front-end OPEL belum
dikonfirmasi. Menyambung ke Chrome yang SUDAH terbuka lewat remote
debugging (pola NewDLA: user login manual SEKALI, scanner tinggal
menempel ke sesi browser yang sama).

Pemakaian:
    python tools/scan_locators_opel.py                          # scan halaman saat ini
    python tools/scan_locators_opel.py --url https://...        # navigasi dulu, lalu scan
    python tools/scan_locators_opel.py --scope ".modal-content" # scan hanya di dalam scope
    python tools/scan_locators_opel.py --name login_b2c         # nama output file

Output (disimpan di reports/scan/):
    <name>.md    -> locator terbaca manusia (gaya *_locator.md NewDLA)
    <name>.json  -> data mentah (kalau mau diproses ulang)
    <name>.png   -> screenshot full page
"""

import argparse
import json
import re
from datetime import datetime
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ==========================================================
# KONFIGURASI
# ==========================================================

REMOTE_DEBUGGING_ADDRESS = "127.0.0.1:9222"

REPORTS_SCAN_DIR = Path(__file__).resolve().parent.parent / "reports" / "scan"

# Id framework auto-generate (ExtJS: "ext-123", MUI: ":r1:", dll) -- id
# semacam ini TIDAK layak dipakai sebagai locator.
POLA_ID_AUTO_GENERATE = re.compile(
    r"^([a-z]+-\d+$|:r\d+:|[A-Za-z]+_[0-9]+$)", re.IGNORECASE
)


# ==========================================================
# CHROME
# ==========================================================

def sambungkan_ke_chrome():
    options = Options()
    options.debugger_address = REMOTE_DEBUGGING_ADDRESS
    return webdriver.Chrome(options=options)


def screenshot_full_page(driver, filepath):
    """Screenshot FULL page (bukan cuma viewport) lewat CDP."""
    try:
        import base64

        result = driver.execute_cdp_cmd(
            "Page.captureScreenshot",
            {"format": "png", "captureBeyondViewport": True, "fromSurface": True},
        )
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "wb") as f:
            f.write(base64.b64decode(result["data"]))
        return filepath
    except Exception as exc:
        print(f"[WARN] Gagal full-page screenshot ({exc}), fallback viewport.")
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        driver.save_screenshot(filepath)
        return filepath


def deteksi_framework(driver):
    """Coba deteksi framework front-end dari global JS."""
    script = r"""
    const hasil = [];
    if (window.Ext && window.Ext.versions) hasil.push('ExtJS ' + window.Ext.versions.extjs);
    if (window.angular) hasil.push('Angular');
    if (window.React) hasil.push('React');
    if (window.Vue) hasil.push('Vue');
    if (window.Materialize) hasil.push('Materialize');
    if (document.querySelector('.mat-mdc-button, .mat-mdc-table, mat-toolbar, .MuiButton-root')) hasil.push('Material/MUI terdeteksi di DOM');
    if (window.jQuery) hasil.push('jQuery');
    return hasil;
    """
    try:
        return driver.execute_script(script)
    except Exception:
        return []


# ==========================================================
# SCAN
# ==========================================================

def ambil_elemen(driver, scope=None):
    """Kembalikan daftar elemen interaktif yang TERLIHAT di halaman
    (atau di dalam scope kalau diberikan)."""

    script = r"""
    const scope = arguments[0]
        ? document.querySelector(arguments[0])
        : document;

    if (!scope) {
        return [];
    }

    const selector =
        'a, button, input, select, textarea, [contenteditable="true"],' +
        '[role="button"], [role="tab"], [role="menuitem"], [role="checkbox"], [role="radio"], [role="option"], [role="treeitem"],' +
        '[onclick], [data-testid], [data-qa], [data-test], [aria-label], [placeholder],' +
        '[ng-model], [formcontrolname]';

    const elements =
        Array.from(scope.querySelectorAll(selector));

    function getLabel(el){
        let label = '';
        try{
            if(el.labels && el.labels.length){
                label = el.labels[0].innerText;
            }
            if(!label && el.parentElement){
                label = el.parentElement.innerText;
            }
            if(!label){
                const row = el.closest('div,td,tr');
                if(row){
                    label = row.innerText;
                }
            }
        }catch(e){}
        return (label || '')
            .replace(/\s+/g,' ')
            .trim()
            .slice(0,120);
    }

    return elements
        .filter(el => {
            const style = window.getComputedStyle(el);
            const rect = el.getBoundingClientRect();
            return (
                style.display !== 'none' &&
                style.visibility !== 'hidden' &&
                rect.width > 0 &&
                rect.height > 0
            );
        })
        .map(el => ({
            tag: el.tagName.toLowerCase(),
            type: el.getAttribute('type') || '',
            text: (el.innerText || el.value || '')
                .replace(/\s+/g,' ')
                .trim()
                .slice(0,120),
            label: getLabel(el),
            id: el.getAttribute('id') || '',
            name: el.getAttribute('name') || '',
            data_testid: el.getAttribute('data-testid') || '',
            data_qa: el.getAttribute('data-qa') || el.getAttribute('data-test') || '',
            data_name: el.getAttribute('data-name') || '',
            data_action: el.getAttribute('data-action') || '',
            data_toggle: el.getAttribute('data-toggle') || '',
            data_target: el.getAttribute('data-target') || '',
            aria_label: el.getAttribute('aria-label') || '',
            placeholder: el.getAttribute('placeholder') || '',
            title: el.getAttribute('title') || '',
            data_qtip: el.getAttribute('data-qtip') || '',
            role: el.getAttribute('role') || '',
            href: el.getAttribute('href') || '',
            ng_model: el.getAttribute('ng-model') || '',
            formcontrolname: el.getAttribute('formcontrolname') || '',
            class_name: (el.getAttribute('class') || '').slice(0,200),
            options: el.tagName === 'SELECT'
                ? Array.from(el.options).map(o => o.textContent.trim()).filter(Boolean).slice(0,50)
                : []
        }));
    """

    return driver.execute_script(script, scope or None)


def ambil_navigasi(driver):
    """Kembalikan daftar semua link + item menu yang terlihat (untuk
    memetakan struktur menu aplikasi)."""
    script = r"""
    const elements = Array.from(document.querySelectorAll('a[href], [role="menuitem"], [role="treeitem"], li'));
    const hasil = [];
    for (const el of elements){
        const style = window.getComputedStyle(el);
        const rect = el.getBoundingClientRect();
        if (style.display === 'none' || style.visibility === 'hidden' || rect.width <= 0 || rect.height <= 0) continue;
        const text = (el.innerText || '').replace(/\s+/g,' ').trim().slice(0,120);
        if (!text) continue;
        hasil.push({
            tag: el.tagName.toLowerCase(),
            text: text,
            href: el.getAttribute('href') || '',
            role: el.getAttribute('role') || '',
            class_name: (el.getAttribute('class') || '').slice(0,150)
        });
    }
    return hasil;
    """
    try:
        return driver.execute_script(script)
    except Exception:
        return []


# ==========================================================
# LOCATOR
# ==========================================================

def kandidat_locator(e):
    """Urutan prioritas locator (paling stabil dulu), mengikuti
    rekomendasi di pages/base_page.py."""
    hasil = []

    if e["data_testid"]:
        hasil.append((f'By.CSS_SELECTOR, "[data-testid=\'{e["data_testid"]}\']"', "data-testid"))

    if e["data_qa"]:
        hasil.append((f'By.CSS_SELECTOR, "[data-qa=\'{e["data_qa"]}\']"', "data-qa"))

    if e["id"] and not POLA_ID_AUTO_GENERATE.match(e["id"]):
        hasil.append((f'By.ID, "{e["id"]}"', "id"))

    if e["name"]:
        hasil.append((f'By.NAME, "{e["name"]}"', "name"))

    if e["data_name"]:
        hasil.append((f'By.CSS_SELECTOR, "[data-name=\'{e["data_name"]}\']"', "data-name"))

    if e["data_action"]:
        hasil.append((f'By.CSS_SELECTOR, "[data-action=\'{e["data_action"]}\']"', "data-action"))

    if e["data_toggle"]:
        hasil.append((f'By.CSS_SELECTOR, "[data-toggle=\'{e["data_toggle"]}\']"', "data-toggle"))

    if e["ng_model"]:
        hasil.append((f'By.CSS_SELECTOR, "[ng-model=\'{e["ng_model"]}\']"', "ng-model"))

    if e["formcontrolname"]:
        hasil.append((f'By.CSS_SELECTOR, "[formcontrolname=\'{e["formcontrolname"]}\']"', "formcontrolname"))

    if e["aria_label"]:
        hasil.append((f'By.CSS_SELECTOR, "[aria-label=\'{e["aria_label"]}\']"', "aria-label"))

    if e["placeholder"]:
        hasil.append((f'By.CSS_SELECTOR, "[placeholder=\'{e["placeholder"]}\']"', "placeholder"))

    if e["data_qtip"]:
        hasil.append((f'By.CSS_SELECTOR, "[data-qtip=\'{e["data_qtip"]}\']"', "data-qtip"))

    if e["text"]:
        text = e["text"].replace('"', "'")
        hasil.append((f'By.XPATH, "//*[normalize-space(text())=\'{text}\']"', "text"))

    if e["title"]:
        hasil.append((f'By.CSS_SELECTOR, "[title=\'{e["title"]}\']"', "title"))

    if not hasil and e["class_name"]:
        cls = e["class_name"].split()[0]
        if not cls.startswith(("Mui", "mat-", "ng-", "css-", "x-", "ant-")):
            hasil.append((f'By.CSS_SELECTOR, ".{cls}"', "class"))

    return hasil


def kategori(e):
    tag = e["tag"]
    tipe = e["type"]
    if tag == "a":
        return "MENU_LINK"
    if e["role"] == "tab":
        return "TAB"
    if tipe == "checkbox":
        return "CHECKBOX"
    if tipe == "radio":
        return "RADIO"
    if tag == "select":
        return "DROPDOWN"
    if tag == "button" or e["role"] == "button":
        return "BUTTON"
    if tag in ["input", "textarea"] or e["role"] in ["checkbox", "radio"]:
        return "INPUT"
    return "LAINNYA"


# ==========================================================
# FORMAT OUTPUT
# ==========================================================

def format_markdown(data, navigasi, framework, url, title):
    lines = []
    lines.append(f"# Scan Locator OPEL")
    lines.append("")
    lines.append(f"- URL   : {url}")
    lines.append(f"- Title : {title}")
    lines.append(f"- Waktu : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if framework:
        lines.append(f"- Framework terdeteksi : {', '.join(framework)}")
    lines.append(f"- Total elemen interaktif : {len(data)}")
    lines.append("")

    grouped = {}
    for item in data:
        grouped.setdefault(kategori(item), []).append(item)

    for cat in ["MENU_LINK", "TAB", "BUTTON", "INPUT", "DROPDOWN", "CHECKBOX", "RADIO", "LAINNYA"]:
        items = grouped.get(cat)
        if not items:
            continue
        lines.append("")
        lines.append("## " + cat)
        lines.append("")
        for e in items:
            title_el = e["text"] or e["label"] or e["placeholder"] or "(kosong)"
            lines.append(f"### {title_el}")
            lines.append("")
            lines.append(f"- tag : `<{e['tag']}>`")
            if e["label"]:
                lines.append(f"- Label : {e['label']}")
            if e["placeholder"]:
                lines.append(f"- Placeholder : {e['placeholder']}")
            if e["role"]:
                lines.append(f"- role : {e['role']}")
            if e["options"]:
                lines.append(f"- Options : {', '.join(e['options'][:30])}")
            locs = kandidat_locator(e)
            if locs:
                lines.append("- Locator kandidat :")
                for loc, sumber in locs:
                    lines.append(f"  - `{loc}` ({sumber})")
            else:
                lines.append("- Locator kandidat : (tidak ada yang stabil, cek JSON)")
            lines.append("")

    if navigasi:
        lines.append("")
        lines.append("## STRUKTUR NAVIGASI / LINK")
        lines.append("")
        for n in navigasi:
            href = f" -> {n['href']}" if n["href"] else ""
            lines.append(f"- [{n['tag']}] {n['text']}{href}")

    return "\n".join(lines)


# ==========================================================
# MAIN
# ==========================================================

def main():
    parser = argparse.ArgumentParser(description="Scanner locator website OPEL")
    parser.add_argument("--url", default=None, help="URL tujuan sebelum scan")
    parser.add_argument("--scope", default=None, help="CSS selector scope (mis. modal/popup)")
    parser.add_argument("--name", default=None, help="Nama file output (tanpa ekstensi)")
    parser.add_argument("--wait", default=5, type=int, help="Detik tunggu setelah load sebelum scan")
    parser.add_argument("--wait-url", default=None, help="Tunggu sampai URL mengandung teks ini")
    args = parser.parse_args()

    print(f"Menyambung ke Chrome {REMOTE_DEBUGGING_ADDRESS}")
    driver = sambungkan_ke_chrome()
    print(f"Terhubung: {driver.title} | {driver.current_url}")

    if args.url:
        print(f"Navigasi ke: {args.url}")
        driver.get(args.url)

    if args.wait_url:
        print(f"Menunggu URL mengandung: {args.wait_url}")
        try:
            WebDriverWait(driver, 120).until(EC.url_contains(args.wait_url))
        except Exception:
            print("[WARN] URL tidak kunjung sesuai, lanjut scan apa adanya.")

    import time

    time.sleep(args.wait)

    url = driver.current_url
    title = driver.title
    framework = deteksi_framework(driver)
    print(f"Framework terdeteksi: {framework or '(tidak ada)'}")

    data = ambil_elemen(driver, scope=args.scope)
    navigasi = ambil_navigasi(driver)
    print(f"Elemen ditemukan: {len(data)} | link/menu: {len(navigasi)}")

    name = args.name or re.sub(r"[^a-z0-9]+", "_", title.lower()).strip("_") or "scan"
    REPORTS_SCAN_DIR.mkdir(parents=True, exist_ok=True)

    md_path = REPORTS_SCAN_DIR / f"{name}.md"
    md_path.write_text(format_markdown(data, navigasi, framework, url, title), encoding="utf-8")

    json_path = REPORTS_SCAN_DIR / f"{name}.json"
    json_path.write_text(
        json.dumps({"url": url, "title": title, "framework": framework,
                    "elements": data, "navigasi": navigasi}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    png_path = screenshot_full_page(driver, REPORTS_SCAN_DIR / f"{name}.png")
    print(f"\nScreenshot: {png_path}")

    print(f"\nHasil disimpan ke: {md_path}")
    print(f"JSON           : {json_path}")
    print("\n" + "-" * 60)
    print(format_markdown(data, [], framework, url, title))


if __name__ == "__main__":
    main()
