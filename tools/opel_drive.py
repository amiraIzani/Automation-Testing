"""
tools/opel_drive.py
===================
Helper navigasi + scan DOM untuk eksplorasi website OPEL lewat Chrome
yang sudah terbuka (remote debugging 9222). Dipakai interaktif dari
python -c / sesi eksplorasi -- BUKAN bagian dari test suite.

Contoh pemakaian interaktif:
    from tools.opel_drive import *
    d = attach()
    click_text(d, 'HSS')
    print_menu(d)
"""

import json
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

ADDRESS = "127.0.0.1:9222"


def attach():
    options = Options()
    options.debugger_address = ADDRESS
    return webdriver.Chrome(options=options)


def js(driver, script, *args):
    return driver.execute_script(script, *args)


def click_text(driver, text, tag=None, timeout=10):
    """Klik elemen yang teks-nya persis `text` (tag opsional).
    Pakai scrollIntoView + JS click supaya kebal dari elemen di luar
    viewport / tertutup overlay (menu sidebar OPEL suka begini)."""
    element = driver.find_element(
        By.XPATH,
        f"//{tag or '*'}[normalize-space(text())='{text}']",
    )
    js(driver, "arguments[0].scrollIntoView({block: 'center'});", element)
    time.sleep(0.5)
    js(driver, "arguments[0].click();", element)
    time.sleep(2)


def click_contains(driver, text, tag=None, timeout=10):
    """Klik elemen yang teks-nya MENGANDUNG `text` (JS click)."""
    element = driver.find_element(
        By.XPATH,
        f"//{tag or '*'}[contains(normalize-space(.), '{text}')]",
    )
    js(driver, "arguments[0].scrollIntoView({block: 'center'});", element)
    time.sleep(0.5)
    js(driver, "arguments[0].click();", element)
    time.sleep(2)


def print_menu(driver):
    """Cetak struktur menu sidebar yang sedang terlihat."""
    items = js(
        driver,
        r"""
        const out = [];
        document.querySelectorAll('nav li, .page-sidebar li, ul li').forEach(li => {
            const style = window.getComputedStyle(li);
            const rect = li.getBoundingClientRect();
            if (style.display === 'none' || rect.width <= 0 || rect.height <= 0) return;
            const selfText = Array.from(li.childNodes)
                .filter(n => n.nodeType === 3)
                .map(n => n.textContent.trim()).join(' ')
                || Array.from(li.children)
                    .filter(c => c.tagName !== 'UL')
                    .map(c => c.innerText.trim()).filter(Boolean).join(' ');
            const text = (selfText || li.innerText || '').replace(/\s+/g, ' ').trim().slice(0, 120);
            if (!text) return;
            const a = li.querySelector(':scope > a, :scope > span, :scope > button');
            const sub = Array.from(li.querySelectorAll(':scope > ul > li > a, :scope > ul > li > span'))
                .map(x => x.innerText.replace(/\s+/g, ' ').trim())
                .filter(t => t && t !== text)
                .slice(0, 40);
            out.push({
                text,
                href: a ? (a.getAttribute('href') || '') : '',
                cls: li.className.toString().slice(0, 80),
                visible_children: sub,
            });
        });
        return out;
        """,
    )
    for it in items:
        print(f"- {it['text']}  [{it['cls']}]  href={it['href']}")
        for sub in it["visible_children"]:
            print(f"    * {sub}")
    return items


def outer_html(driver, locator_css, max_len=2000):
    """Ambil outerHTML elemen pertama yang cocok (untuk inspeksi manual)."""
    try:
        return js(
            driver,
            "return (document.querySelector(arguments[0]) || {}).outerHTML || '(tidak ada)';",
            locator_css,
        )[:max_len]
    except Exception as exc:
        return f"(error: {exc})"


def scan_now(driver, name, scope=None):
    """Panggil scanner dari modul tools (simpan md/json/png)."""
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from tools.scan_locators_opel import (
        ambil_elemen,
        ambil_navigasi,
        deteksi_framework,
        format_markdown,
        screenshot_full_page,
        REPORTS_SCAN_DIR,
    )

    data = ambil_elemen(driver, scope=scope)
    navigasi = ambil_navigasi(driver)
    framework = deteksi_framework(driver)
    url = driver.current_url
    title = driver.title

    (REPORTS_SCAN_DIR / f"{name}.md").write_text(
        format_markdown(data, navigasi, framework, url, title), encoding="utf-8"
    )
    (REPORTS_SCAN_DIR / f"{name}.json").write_text(
        json.dumps({"url": url, "title": title, "framework": framework,
                    "elements": data, "navigasi": navigasi}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    png = screenshot_full_page(driver, REPORTS_SCAN_DIR / f"{name}.png")
    print(f"[scan] {name} -> {len(data)} elemen, {len(navigasi)} link | {png}")
    return data, navigasi


def html_elemen(driver, selector, max_len=3000):
    """Dump outerHTML elemen2 yang cocok dengan selector CSS."""
    hasil = js(
        driver,
        r"""
        const out = [];
        document.querySelectorAll(arguments[0]).forEach(el => {
            if (el.getBoundingClientRect().height > 0)
                out.push(el.outerHTML);
        });
        return out;
        """,
        selector,
    )
    print(f"[{selector}] -> {len(hasil)} elemen terlihat:")
    for h in hasil[:5]:
        print(h[:max_len])
        print("-" * 80)
    return hasil
