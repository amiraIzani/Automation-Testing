"""Probe: dump href & visibilitas link submenu Safety > Reporting
(buat diagnosa kenapa //nav//a[contains(@href,...)] tidak visible)."""
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
    page.buka_submenu("HSS")
    page.buka_submenu("Safety", induk="HSS")
    page.buka_submenu("Reporting", induk="Safety")
    page.buka_submenu("Transaction", induk="Safety")

    # klik sign grup 'Leading Indicator' manual lalu dump state li-nya
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.action_chains import ActionChains

    sign = d.find_element(
        By.XPATH,
        "//nav//li[.//span[normalize-space(text())='Transaction']]"
        "//a[contains(@title,'Leading Indicator')]"
        "//b[contains(@class,'collapse-sign')]",
    )
    ActionChains(d).move_to_element(sign).click().perform()
    import time
    time.sleep(3)
    state = d.execute_script(
        "const out = [];"
        "document.querySelectorAll('nav span').forEach(s => {"
        "  const li = s.closest('li');"
        "  const r = s.getBoundingClientRect();"
        "  if (r.height > 0) out.push({teks: (s.innerText || '').trim(),"
        "    liClass: li ? li.className : '(no li)',"
        "    y: r.y});"
        "});"
        "return out;"
    )
    print("[span menu yang TAMPIL sesudah klik sign grup]", state)

    rows = d.execute_script(
        "const out = [];"
        "document.querySelectorAll(\"nav a[href*='Reporting']\").forEach(a => {"
        "  const r = a.getBoundingClientRect();"
        "  let p = a; let hidden = false;"
        "  while (p && p !== document.body) {"
        "    const ps = window.getComputedStyle(p);"
        "    if (ps.display === 'none' || ps.visibility === 'hidden')"
        "      { hidden = true; break; }"
        "    p = p.parentElement;"
        "  }"
        "  out.push({href: a.getAttribute('href'),"
        "    text: (a.innerText || '').trim(),"
        "    rect: [r.x, r.y, r.width, r.height], hidden: hidden});"
        "});"
        "return out;"
    )
    for row in rows:
        print(row)
finally:
    d.quit()
