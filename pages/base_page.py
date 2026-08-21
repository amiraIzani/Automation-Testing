"""
pages/base_page.py
===================
BasePage berisi fungsi umum yang dipakai di SEMUA page object (klik,
ketik teks, tunggu elemen, dll), supaya tidak ditulis ulang di setiap
page object.

CATATAN: berbeda dari project NewDLA (ExtJS), framework front-end yang
dipakai OPEL belum dikonfirmasi -- helper di file ini sengaja dibuat
GENERIC (tidak mengasumsikan ExtJS/x-mask). Kalau setelah eksplorasi
UI OPEL ternyata memakai framework tertentu (ExtJS, Angular Material,
MUI, dsb.) dengan pola loading-mask/overlay yang khas, tambahkan
method wait_loading_overlay_gone() di sini dengan locator yang sesuai
-- supaya tetap terpusat di satu tempat seperti pola project lama.

Prioritas locator yang disarankan (dari paling stabil ke paling rapuh):
  1. data-testid / data-qa / atribut khusus testing (kalau ada)
  2. id / name yang stabil (bukan id auto-generate framework)
  3. teks yang tampil ke user (label tombol, header, dsb.)
  4. class css yang stabil

Framework ini menghindari time.sleep() tetap (fixed) -- semua
"menunggu" memakai WebDriverWait + expected_conditions supaya tidak
flaky dan tidak boros waktu menunggu tanpa alasan.
"""

import os
import time
from datetime import datetime

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    TimeoutException,
    StaleElementReferenceException,
    ElementClickInterceptedException,
    NoSuchElementException,
)

from config import config


class BasePage:
    def __init__(self, driver, timeout=None):
        self.driver = driver
        self.timeout = timeout or config.DEFAULT_TIMEOUT

    # ------------------------------ Helper dasar ------------------------------
    def _wait(self, timeout=None):
        return WebDriverWait(self.driver, timeout or self.timeout)

    def pace(self, seconds=None):
        """Jeda visual antar-aksi (bukan untuk menunggu elemen)."""
        time.sleep(seconds if seconds is not None else config.ACTION_PACE_SECONDS)

    def find(self, locator, timeout=None):
        """Tunggu elemen ADA di DOM, kembalikan elemennya."""
        return self._wait(timeout).until(EC.presence_of_element_located(locator))

    def find_all(self, locator, timeout=None):
        """Tunggu minimal 1 elemen ADA di DOM, kembalikan semuanya."""
        return self._wait(timeout).until(EC.presence_of_all_elements_located(locator))

    def find_visible_among(self, locator, timeout=None):
        """Ambil elemen PERTAMA yang benar2 TAMPIL dari locator yang
        match banyak elemen (yang lain hidden di DOM)."""
        elements = self._wait(timeout).until(
            EC.presence_of_all_elements_located(locator)
        )
        for element in elements:
            try:
                if element.is_displayed():
                    return element
            except StaleElementReferenceException:
                continue
        raise TimeoutException(
            f"Tidak ada elemen yang benar-benar tampil untuk locator: {locator}"
        )

    def find_all_visible(self, locator, timeout=None):
        """Sama seperti find_visible_among() tapi kembalikan SEMUA yang tampil."""
        try:
            elements = self._wait(timeout).until(
                EC.presence_of_all_elements_located(locator)
            )
        except TimeoutException:
            return []
        visible = []
        for element in elements:
            try:
                if element.is_displayed():
                    visible.append(element)
            except StaleElementReferenceException:
                continue
        return visible

    def click(self, locator, timeout=None):
        """Klik elemen. Fallback JS kalau kena StaleElement/terhalang overlay."""
        try:
            element = self._wait(timeout).until(EC.element_to_be_clickable(locator))
            element.click()
        except StaleElementReferenceException:
            element = self._wait(timeout).until(EC.element_to_be_clickable(locator))
            element.click()
        except ElementClickInterceptedException:
            element = self.find(locator, timeout=timeout)
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});", element
            )
            self.driver.execute_script("arguments[0].click();", element)
        self.pace()

    def click_via_js(self, locator_or_element, timeout=None):
        """Klik pakai JavaScript."""
        element = locator_or_element
        if isinstance(locator_or_element, tuple):
            element = self.find(locator_or_element, timeout=timeout)
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        self.driver.execute_script("arguments[0].click();", element)
        self.pace()

    def click_visible_among(self, locator, timeout=None):
        """Klik elemen yang benar2 tampil (bukan match pertama yang bisa hidden)."""
        element = self.find_visible_among(locator, timeout=timeout)
        self.click_via_js(element)
        return element

    @staticmethod
    def _js_visible(driver, element):
        """Cek visibilitas pakai computed style JS -- TERBUKTI lebih
        akurat daripada WebElement.is_displayed() yang bisa False
        negatif saat panel OPEL masih fade-transition."""
        return bool(driver.execute_script(
            "const s = window.getComputedStyle(arguments[0]);"
            "const r = arguments[0].getBoundingClientRect();"
            "return s.display !== 'none' && s.visibility !== 'hidden'"
            "&& r.width > 0 && r.height > 0;",
            element,
        ))

    def _ambil_js_visible(self, locator, timeout=None):
        """Tunggu lalu kembalikan elemen PERTAMA yang tampil menurut
        computed style JS (bukan is_displayed()). Tahan terhadap
        StaleElement -- elemen OPEL bisa diganti DOM saat redraw."""
        self.find(locator, timeout=timeout)  # pastikan ada di DOM dulu

        def _ada_tampil(d):
            for el in d.find_elements(*locator):
                try:
                    if self._js_visible(d, el):
                        return True
                except StaleElementReferenceException:
                    continue
            return False

        self._wait(timeout).until(
            _ada_tampil,
            f"Tidak ada elemen yang tampil (JS) untuk locator: {locator}",
        )
        for element in self.driver.find_elements(*locator):
            try:
                if self._js_visible(self.driver, element):
                    return element
            except StaleElementReferenceException:
                continue
        raise TimeoutException(
            f"Tidak ada elemen yang benar2 tampil untuk locator: {locator}"
        )

    def click_js_saat_tampil(self, locator, timeout=None):
        """Klik pakai JS begitu elemen benar2 tampil MENURUT computed
        style. Dipakai untuk toolbar/modal OPEL yang kena quirk
        is_displayed() false-negatif saat fade-transition -- klik
        biasa (EC.element_to_be_clickable) bisa timeout sia-sia.
        Kalau kena StaleElement (elemen diganti DOM), cari ulang
        sampai 3x sebelum menyerah."""
        for _ in range(3):
            try:
                element = self._ambil_js_visible(locator, timeout=timeout)
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block: 'center'});", element
                )
                self.driver.execute_script("arguments[0].click();", element)
                self.pace()
                return
            except StaleElementReferenceException:
                continue
        raise StaleElementReferenceException(
            f"Elemen {locator} terus-menerus stale saat diklik"
        )

    def type_text(self, locator, text, clear_first=True, timeout=None):
        """Tunggu elemen tampil, kosongkan (opsional), lalu ketik teks."""
        element = self._wait(timeout).until(EC.visibility_of_element_located(locator))
        if clear_first:
            element.clear()
        element.send_keys(text)
        self.pace()

    def type_text_visible(self, locator, text, clear_first=True, timeout=None):
        """Ketik ke elemen yang benar2 TAMPIL (untuk locator yang match
        elemen ganda di DOM) + scroll ke viewport sebelum ketik.
        Kalau kena StaleElement, cari ulang sampai 3x."""
        for _ in range(3):
            try:
                element = self._ambil_js_visible(locator, timeout=timeout)
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block: 'center'});", element
                )
                if clear_first:
                    element.clear()
                element.send_keys(text)
                self.pace()
                return
            except StaleElementReferenceException:
                continue
        raise StaleElementReferenceException(
            f"Elemen {locator} terus-menerus stale saat diketik"
        )

    def get_text(self, locator, timeout=None):
        return self.find(locator, timeout=timeout).text

    def is_visible(self, locator, timeout=None):
        """True/False apakah elemen tampil. HATI-HATI: mengunci ke match
        PERTAMA di DOM -- pakai find_visible_among untuk locator ganda."""
        try:
            WebDriverWait(self.driver, timeout or self.timeout).until(
                EC.visibility_of_element_located(locator)
            )
            return True
        except TimeoutException:
            return False

    def is_present(self, locator, timeout=None):
        """Cek apakah elemen ADA di DOM (tidak wajib terlihat)."""
        try:
            WebDriverWait(self.driver, timeout or self.timeout).until(
                EC.presence_of_element_located(locator)
            )
            return True
        except TimeoutException:
            return False

    def wait_url_contains(self, text, timeout=None):
        return self._wait(timeout).until(EC.url_contains(text))

    def wait_url_not_contains(self, text, timeout=None):
        """Tunggu sampai URL saat ini TIDAK lagi mengandung `text`.
        Dipakai untuk mendeteksi selesainya redirect SSO (mis. keluar
        dari domain login Azure AD B2C dan kembali ke aplikasi)."""
        return self._wait(timeout).until(lambda d: text not in d.current_url)

    def is_any_visible(self, locator, timeout=None):
        """True kalau ADA elemen yang benar2 tampil untuk locator."""
        try:
            self._wait(timeout).until(
                lambda _: any(
                    el.is_displayed() for el in self.driver.find_elements(*locator)
                )
            )
            return True
        except TimeoutException:
            return False

    def wait_hilang(self, locator, timeout=None):
        """Tunggu sampai TIDAK ADA elemen yang tampil untuk locator.
        Dipakai untuk menunggu modal/overlay benar-benar tertutup."""
        try:
            self._wait(timeout).until(
                lambda _: not any(
                    el.is_displayed()
                    for el in self.driver.find_elements(*locator)
                )
            )
        except TimeoutException:
            raise TimeoutException(
                f"Elemen masih tampil setelah ditunggu: {locator}"
            )

    def select_option(self, locator, teks_opsi, timeout=None):
        """Pilih opsi pada <select> native berdasarkan teks yang
        TERLIHAT (visible text), bukan value -- teks lebih intuitif
        dan stabil dibaca manusia."""
        element = self._ambil_js_visible(locator, timeout=timeout)
        try:
            Select(element).select_by_visible_text(teks_opsi)
        except NoSuchElementException as exc:
            raise NoSuchElementException(
                f"Opsi '{teks_opsi}' tidak ada di select {locator}. "
                f"Opsi tersedia: "
                f"{[o.text for o in Select(element).options]}"
            ) from exc
        self.pace()

    def find_first_visible(self, locator_candidates, timeout=None):
        """Coba kandidat locator satu per satu, kembalikan yang pertama
        ketemu & terlihat (untuk locator yang belum 100% dikonfirmasi --
        berguna di tahap awal eksplorasi UI OPEL)."""
        for locator in locator_candidates:
            if self.is_visible(locator, timeout=timeout or 3):
                return locator
        return None

    # --------------------- Screenshot manual (di luar hook conftest) ---------------------
    def take_screenshot(self, name):
        os.makedirs(config.SCREENSHOT_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(config.SCREENSHOT_DIR, f"{name}_{timestamp}.png")
        self.driver.save_screenshot(filepath)
        return filepath

    def scroll_into_view(self, locator, timeout=None):
        element = self.find(locator, timeout=timeout)
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", element
        )
        return element
