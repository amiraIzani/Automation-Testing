"""
pages/safety_recap_page.py
==============================
Page object: Safety > Reporting > Safety Recap.
(Reporting/Supersafe/HSSE/ReportingSafetyRecap (custom, bukan pola Timesheet)).

Semua locator hasil SCAN website OPEL (2026-08-20, v2.6.7):
    - data mentah : reports/scan/safety/05_safety_recap.md / .json / .png
    - dokumentasi : locators/hss_safety.md

Mewarisi locator umum dari HssSafetyPage (toolbar tbDate/cbDistrict,
tombol Export/Import/Submit, modal Import, dll).
"""

from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

from config import config
from pages.hss_safety_page import HssSafetyPage, TidakPunyaAkses


class SafetyRecapPage(HssSafetyPage):
    KUNCI = "safety_recap"

    # Halaman custom (bukan pola Timesheet): tabelnya
    # #tableBulanan / #tableTahunan (bukan table.reportData).
    TABLE_BULANAN = (By.ID, "tableBulanan")
    TABLE_TAHUNAN = (By.ID, "tableTahunan")
    LINK_BULANAN = (By.ID, "linkBulanan")
    LINK_TAHUNAN = (By.ID, "linkTahunan")

    def buka(self):
        """Buka halaman Safety Recap (tunggu tabel Bulanan tampil).
        Halaman ini kadang butuh fetch data lebih lama (pipeline
        Supersafe/HSSE) -- retry navigasi sekali kalau timeout.
        Kalau tidak punya akses, otomatis kembali via driver.back()
        dan lempar TidakPunyaAkses."""
        url = config.BASE_URL.rstrip("/") + "/" + self.HALAMAN[self.KUNCI].lstrip("/")

        def _tunggu():
            self._wait(config.LONG_TIMEOUT).until(
                lambda d: self.driver.execute_script(self._js_tampil(), "#tableBulanan", 10),
                f"Tabel Bulanan tidak kunjung tampil di {url}",
            )

        self.driver.get(url)
        try:
            _tunggu()
        except TimeoutException:
            pesan = self._halaman_tidak_punya_akses()
            if pesan:
                print(
                    f"\n[TIDAK PUNYA AKSES] Halaman '{self.KUNCI}' "
                    f"({url}): {pesan}"
                    "\n  -> Kembali ke halaman sebelumnya (driver.back())"
                )
                self.driver.back()
                self.pace(1.0)
                raise TidakPunyaAkses(
                    f"Tidak punya akses ke halaman '{self.KUNCI}': {pesan}"
                )
            self.driver.get(url)
            try:
                _tunggu()
            except TimeoutException:
                pesan = self._halaman_tidak_punya_akses()
                if pesan:
                    print(
                        f"\n[TIDAK PUNYA AKSES] Halaman '{self.KUNCI}' "
                        f"({url}): {pesan}"
                        "\n  -> Kembali ke halaman sebelumnya (driver.back())"
                    )
                    self.driver.back()
                    self.pace(1.0)
                    raise TidakPunyaAkses(
                        f"Tidak punya akses ke halaman '{self.KUNCI}': {pesan}"
                    )
                raise
        return self

