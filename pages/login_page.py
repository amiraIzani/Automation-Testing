"""
pages/login_page.py
====================
Login OPEL (https://dev-opel.antm.tech/). Hasil eksplorasi UI
(2026-08-20, OPEL v2.6.7):

- Di environment DEV saat ini, login terjadi OTOMATIS: driver.get
  (BASE_URL) -> 1 redirect -> langsung /My/Dashboard (cookie
  ASP.NET Core diterbitkan server tanpa form apapun, kemungkinan
  integrated auth domain internal).
- Form Azure AD B2C (antamapps.b2clogin.com) TIDAK muncul dari mesin
  ini. Locator B2C di bawah tetap dipakai hanya untuk DETEKSI
  "stuck di form login" (kalau mekanisme auth dev berubah atau
  testing di environment lain yang benar-benar memakai B2C).
- Profile Chrome tetap dipakai sesuai pola NewDLA supaya aman untuk
  environment staging/prod yang mungkin masih memakai B2C.

Alur saat driver.get(BASE_URL) dipanggil:
1. OPEL menerbitkan sesi (DEV: otomatis; environment lain: lewat
   redirect Azure AD B2C).
2. Browser berakhir di /My/Dashboard -> HOME_LOADED_MARKER (logo
   OPEL di header) tampil.

Kalau browser justru BERHENTI di form login B2C (field email tampil),
automation harus berhenti dan minta user login manual ulang
(lihat is_stuck_on_b2c_form()).
"""

from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

from config import config
from pages.base_page import BasePage


class LoginPage(BasePage):
    # ------------------- Locator form B2C (dipakai HANYA untuk deteksi,
    # bukan untuk auto-isi) -------------------
    # NOTE: locator field email/password B2C ini generik (umum dipakai
    # template B2C custom policy default Microsoft) -- verifikasi lagi
    # begitu form ini benar-benar tampil di eksplorasi pertama, karena
    # custom policy ANTAM bisa saja beda id-nya.
    B2C_EMAIL_INPUT = (By.ID, "email")
    B2C_PASSWORD_INPUT = (By.ID, "password")
    B2C_SIGNIN_BUTTON = (By.ID, "next")

    # Marker halaman utama OPEL: avatar user di kanan atas header.
    # Dikonfirmasi dari eksplorasi UI (scan 2026-08-20): begitu login
    # selesai, browser berakhir di /My/Dashboard dan avatar ini tampil
    # (ukuran 32x32, selalu terlihat di semua ukuran layar).
    # CATATAN: logo header (a.page-logo-link) TIDAK bisa dipakai
    # sebagai marker -- di viewport <1600px ukurannya 0x0 (disembunyikan
    # CSS SmartAdmin).
    # CATATAN: di environment DEV saat ini, login terjadi OTOMATIS
    # (auth internal dev -- TANPA form B2C, 1 redirect langsung ke
    # /My/Dashboard). Form B2C hanya muncul kalau mekanisme auth
    # dev berubah / di environment lain.
    HOME_LOADED_MARKER = (
        By.CSS_SELECTOR,
        "a.header-icon[data-toggle='dropdown'] img.profile-image",
    )

    # --------------- Topbar / user (dikonfirmasi dari UI) ---------------
    # Trigger dropdown avatar user (di kanan atas header). Title-nya
    # adalah email user -- kalau email berubah, ganti lewat
    # config/task data (test_data.json "user.email").
    AVATAR_DROPDOWN_TRIGGER = HOME_LOADED_MARKER
    # Nama user tampil di dropdown (konfirmasi user yang login).
    USER_NAME_IN_DROPDOWN = (By.CSS_SELECTOR, ".dropdown-menu .info-card-text")
    # Tombol logout: <a class="dropdown-item" href="javascript: signOut()">
    LOGOUT_LINK = (By.CSS_SELECTOR, "a.dropdown-item[href=\"javascript: signOut()\"]")
    # Bell notifikasi + badge jumlah notifikasi.
    NOTIFICATION_BELL = (By.ID, "linkNotificationCount")
    NOTIFICATION_BADGE = (By.ID, "bdgNotificationCount")
    NOTIFICATION_DROPDOWN = (By.ID, "dropdownNotification")

    def buka_halaman_login(self):
        """Navigasi ke BASE_URL. Kalau sesi Azure AD profile masih aktif,
        browser akan auto-redirect balik ke OPEL tanpa isi form apapun."""
        self.driver.get(config.BASE_URL)

    def tunggu_selesai_redirect_b2c(self, timeout=None):
        """Tunggu sampai URL keluar dari domain B2C (antamapps.b2clogin.com)
        dan kembali ke domain OPEL -- menandakan sesi Azure AD profile
        berhasil dipakai otomatis (tidak stuck di form login)."""
        timeout = timeout or config.LONG_TIMEOUT
        try:
            self.wait_url_not_contains(config.B2C_LOGIN_DOMAIN, timeout=timeout)
        except TimeoutException as exc:
            raise TimeoutException(
                "Masih di halaman Azure AD B2C setelah "
                f"{timeout} detik. Kemungkinan sesi Chrome profile "
                f"('{config.CHROME_PROFILE_PATH}') sudah expired -- "
                "login manual ulang di luar automation, lihat README."
            ) from exc

    def is_stuck_on_b2c_form(self, timeout=3):
        """True kalau browser berhenti di form login B2C (field email
        tampil) -- artinya sesi Chrome profile TIDAK aktif dan automation
        tidak bisa lanjut tanpa login manual."""
        return self.is_visible(self.B2C_EMAIL_INPUT, timeout=timeout)

    def tunggu_halaman_utama_tampil(self, timeout=None):
        """Tunggu marker halaman utama OPEL tampil setelah redirect selesai.
        GANTI HOME_LOADED_MARKER dengan elemen asli (logo/menu/avatar)
        begitu sudah dikonfirmasi dari eksplorasi UI."""
        return self.find(self.HOME_LOADED_MARKER, timeout=timeout or config.LONG_TIMEOUT)

    def login(self):
        """Method tingkat tinggi: buka halaman, tunggu redirect B2C
        selesai otomatis, lalu pastikan halaman utama tampil. Kalau
        stuck di form B2C, lempar error yang jelas (bukan timeout buta)."""
        self.buka_halaman_login()
        if self.is_stuck_on_b2c_form(timeout=5):
            raise RuntimeError(
                "Browser berhenti di form login Azure AD B2C. Sesi "
                f"Chrome profile ('{config.CHROME_PROFILE_PATH}') belum "
                "aktif atau sudah expired. Login manual sekali di luar "
                "automation (buka Chrome dengan profile yang sama, "
                "login ke OPEL, lalu tutup Chrome), baru jalankan test lagi."
            )
        self.tunggu_selesai_redirect_b2c()
        self.tunggu_halaman_utama_tampil()

    def logout(self):
        """Buka dropdown avatar (kanan atas), klik Logout (memanggil
        signOut()). Setelah logout browser kembali ke halaman login /
        signin-oidc."""
        self.click(self.AVATAR_DROPDOWN_TRIGGER)
        self.click(self.LOGOUT_LINK)
