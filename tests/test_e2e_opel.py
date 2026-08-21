"""
tests/test_e2e_opel.py
=======================
Test E2E OPEL. Mengikuti pola NewDLA: satu sesi browser (fixture
`driver` scope="session" di conftest.py) dari Login sampai modul
terakhir -- tambahkan test method baru di bawah test_login begitu
modul lain (Dashboard, dst.) sudah dieksplorasi.

Jalankan:
    pytest                              # seluruh alur
    pytest -k test_login                # hanya modul Login
    pytest tests/test_e2e_opel.py::TestE2EOpelFlow::test_login
"""

import pytest

from pages.login_page import LoginPage


@pytest.mark.e2e
class TestE2EOpelFlow:

    @pytest.mark.login
    def test_login(self, driver, test_data):
        """Buka OPEL -> redirect Azure AD B2C -> sesi Chrome profile
        aktif -> redirect balik ke OPEL -> halaman utama tampil.

        Kalau test ini gagal dengan RuntimeError yang menyebut "form
        login Azure AD B2C", artinya sesi Chrome profile
        (config.CHROME_PROFILE_PATH) belum aktif/sudah expired --
        login manual sekali dulu (lihat README bagian Setup), baru
        jalankan test lagi.
        """
        login_page = LoginPage(driver)
        login_page.login()

        assert "dev-opel.antm.tech" in driver.current_url, (
            f"Setelah login masih di URL tak terduga: {driver.current_url}"
        )
