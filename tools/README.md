# tools/ — skrip bantu di luar pytest

Semua skrip di sini dijalankan **manual**, bukan lewat pytest.
`pytest.ini` menyetel `testpaths = tests`, jadi folder ini tidak pernah
ikut ter-collect.

Semuanya butuh sesi login aktif di profil Chrome
(`config.CHROME_PROFILE_PATH`) — lihat README utama bagian Setup.

Jalankan dari root project:

```powershell
py tools/<nama_skrip>.py
```

---

## Diagnosa (dipakai saat menyelidiki kegagalan test)

| Skrip | Kegunaan |
|---|---|
| **`cek_simpan_inline.py`** | Menguji apakah edit inline di grid **benar-benar tersimpan** ke server, di 14 halaman ber-Submit Changes. Membaca lewat **Reload Data** (bukan reload halaman) supaya tidak tertipu draft lokal. Punya `--dry-run`, `--hanya <halaman>`, `--field <NamaKolom>` |
| `cek_grid_semua_halaman.py` | Melaporkan setiap `<table class="reportData">` yang dirender tiap halaman — id, jumlah baris, apakah DataTables ter-init. Dibuat waktu `JS_GRID` salah memilih tabel decoy |
| `probe_columns.py` | Melihat elemen item kolom yang harus diklik di dropdown Columns |
| `probe_menu_href.py` | Diagnosa kenapa link menu sidebar tidak terlihat oleh XPath |

`cek_simpan_inline.py` adalah yang paling penting: alat inilah yang
membuktikan bug `submit-changes-redirect` dan meluruskan tiga
kesimpulan keliru sebelumnya. Lihat `reports/bugs/README.md`.

## Pembersihan data DEV

| Skrip | Kegunaan |
|---|---|
| `cleanup_dummy_master_alat.py` | Hapus baris dummy (`AUTO-TEST*`, `Dummy*`) dan draft kosong di grid Master Alat. Punya `--dry-run` |
| `cleanup_dummy_semua.py` | Sama, tapi untuk SEMUA halaman Safety yang bisa membuat baris |

Dijalankan sesekali supaya data DEV tidak menumpuk oleh sisa test.
Keduanya beroperasi di **district yang sedang aktif** saja — sesuai
perilaku test yang membuat dummy-nya.

## Scanner & generator (dipakai saat membangun page object)

| Skrip | Kegunaan |
|---|---|
| `scan_locators_opel.py` | Scanner locator generic untuk OPEL |
| `scan_safety_batch.py` | Batch scan SEMUA halaman Safety sekaligus |
| `scan_form_safety.py` | Scan modal "Create with Form" tiap halaman transaction |
| `locator.py` | Baca hasil scan JSON, cetak ringkasan id stabil / tombol / select |
| `generate_safety_pages.py` | Generate `pages/safety_*_page.py` dari hasil scan |
| `opel_drive.py` | Helper navigasi + scan DOM interaktif, lewat Chrome yang sudah terbuka (remote debugging port 9222) |

Kelompok ini dipakai saat page object pertama kali dibuat
(scan 2026-08-20). Jarang dijalankan lagi, tapi **dipertahankan**:
kalau OPEL mengubah struktur halaman, inilah cara memperbarui locator
tanpa menulis ulang manual.
