"""Probe: petakan link Safety > Reporting ke subgroup barunya.

OPEL (terlihat 2026-09-11) memecah Safety > Reporting menjadi subgroup
'Lagging Indicator' & 'Leading Indicator' -- link halaman tidak lagi
langsung di bawah Reporting. Script ini membuka kedua subgroup lalu
mencetak rantai judul menu (span) di atas setiap link Reporting.
READ-ONLY: hanya membuka menu, tidak mengklik link halaman."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from config import config
from pages.hss_safety_page import HssSafetyPage

options = Options()
options.add_argument("--start-maximized")
options.add_argument(f"--user-data-dir={config.CHROME_PROFILE_PATH}")
options.add_argument("--disable-notifications")
options.add_experimental_option("excludeSwitches", ["enable-automation"])

d = webdriver.Chrome(options=options)
d.implicitly_wait(0)

try:
    page = HssSafetyPage(d)
    d.get(config.BASE_URL)
    page._wait(config.LONG_TIMEOUT).until(
        lambda _: page.is_any_visible(page.MENU_HSS)
    )
    for rantai in (
        ("HSS",),
        ("HSS", "Safety"),
        ("HSS", "Safety", "Reporting"),
    ):
        page.buka_submenu(rantai[-1], induk=(rantai[-2] if len(rantai) > 1
                                             else None), rantai=rantai)
    for sub in ("Lagging Indicator", "Leading Indicator"):
        try:
            page.buka_submenu(
                sub, induk="Reporting",
                rantai=("HSS", "Safety", "Reporting", sub),
            )
            print(f"[OK] subgroup '{sub}' terbuka")
        except Exception as e:  # noqa: BLE001 -- probe, cetak saja
            print(f"[GAGAL] buka subgroup '{sub}': {type(e).__name__} {e}")

    rows = d.execute_script(
        "const out = [];"
        "document.querySelectorAll(\"nav a[href*='Reporting']\").forEach(a => {"
        "  const rantai = [];"
        "  let li = a.closest('li');"
        "  li = li ? li.parentElement.closest('li') : null;"
        "  while (li) {"
        "    const s = li.querySelector(':scope > a span');"
        "    rantai.unshift(s ? (s.innerText || '').trim() : '?');"
        "    li = li.parentElement.closest('li');"
        "  }"
        "  const r = a.getBoundingClientRect();"
        "  out.push({href: a.getAttribute('href'),"
        "    text: (a.innerText || '').trim(),"
        "    rantai: rantai.join(' > '), tampil: r.height > 0});"
        "});"
        "return out;"
    )
    for row in rows:
        if "Safety" in row["rantai"]:
            print(row)
finally:
    d.quit()
