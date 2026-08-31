"""
config.py
=========
Semua pengaturan project (URL, timeout, path profil Chrome, mode headless)
dipusatkan di sini. Kalau ada yang berubah (URL staging, timeout, dst),
cukup ubah di 1 tempat -- tidak perlu cari-cari di banyak file test.

Semua nilai bisa di-override lewat environment variable, supaya:
- Tiap anggota tim bisa punya path Chrome profile sendiri-sendiri.
- Bisa dijalankan headless di CI/CD tanpa ubah kode.
"""

import os

# ------------------- URL aplikasi yang akan diuji -------------------
# OPEL (dev environment). Ganti lewat env OPEL_BASE_URL kalau perlu
# testing ke environment lain (staging/prod) tanpa ubah kode.
BASE_URL = os.getenv("OPEL_BASE_URL", "https://dev-opel.antm.tech/")

# ------------------- Login Azure AD B2C -------------------
# OPEL login pakai Azure AD B2C (redirect ke antamapps.b2clogin.com).
# Sama seperti pola NewDLA: Selenium TIDAK mengisi email/password di
# form B2C (rawan diblokir/butuh MFA) -- Chrome memakai folder profile
# yang sesi Azure AD-nya SUDAH aktif (login manual dilakukan SEKALI di
# luar automation). Override lewat env OPEL_CHROME_PROFILE.
CHROME_PROFILE_PATH = os.getenv("OPEL_CHROME_PROFILE", r"D:\selenium-chrome-profile-opel")

# Domain yang dipakai untuk mendeteksi bahwa browser sedang di tengah
# proses redirect Azure AD B2C (login_page.py menunggu sampai URL
# KELUAR dari domain ini dan kembali ke BASE_URL).
B2C_LOGIN_DOMAIN = os.getenv("OPEL_B2C_DOMAIN", "antamapps.b2clogin.com")

# ------------------- Mode browser -------------------
# HEADLESS=true -> Chrome tanpa jendela (cocok untuk CI/CD).
HEADLESS = os.getenv("OPEL_HEADLESS", "false").strip().lower() in ("1", "true", "yes")

# ------------------- Timeout default (detik) untuk WebDriverWait -------------------
DEFAULT_TIMEOUT = int(os.getenv("OPEL_TIMEOUT", "15"))

# Timeout lebih panjang untuk proses yang butuh loading data lama
# (redirect SSO Azure AD B2C, render grid Timesheet/Safety yang di
# dev server bisa >30 detik, upload dokumen, dll).
LONG_TIMEOUT = int(os.getenv("OPEL_LONG_TIMEOUT", "60"))

# ------------------- Jeda antar-aksi (detik) -------------------
# HANYA untuk kebutuhan visual (alur bisa diikuti mata saat browser
# dibuka), BUKAN untuk menunggu elemen (itu tugas WebDriverWait).
# Default 2.0 detik SERAGAM untuk semua aksi (permintaan user
# 2026-08-28: 2-3 detik antar-aksi, jangan terlalu cepat) --
# di-override lewat env OPEL_ACTION_PACE kalau perlu.
ACTION_PACE_SECONDS = float(os.getenv("OPEL_ACTION_PACE", "2.0"))

# ------------------- Lokasi folder laporan & screenshot -------------------
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS_DIR = os.path.join(PROJECT_ROOT, "reports")
SCREENSHOT_DIR = os.path.join(REPORTS_DIR, "screenshots")

# ------------------- Folder unduhan (file export dari tombol Export) -------------------
# Chrome diarahkan ke folder ini lewat prefs di conftest.py supaya file
# export bisa diverifikasi otomatis (tidak tersangkut di Downloads user).
DOWNLOAD_DIR = os.path.join(REPORTS_DIR, "downloads")
