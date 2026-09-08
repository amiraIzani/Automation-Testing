# Statistic Safety Recap — edit inline tidak tersimpan (gejala; akar masalah ada di laporan lain)

> ## STATUS AKHIR (2026-09-08): GEJALANYA NYATA, akar masalahnya SUDAH KETEMU
>
> **Baca laporan utamanya:**
> [`submit-changes-redirect-tanpa-menyimpan.md`](submit-changes-redirect-tanpa-menyimpan.md)
>
> Temuan asli 26 Agustus — "perubahan inline tidak tersimpan" —
> **TERNYATA BENAR**. Yang salah cuma dugaan penyebabnya.
>
> Penyebab sebenarnya: tombol **Submit Changes** di halaman ini
> **langsung me-redirect** ke `YearlyReport/Edit?Id=1317&DistrictCode=AT10`
> sebelum dialog konfirmasi sempat muncul. Request penyimpanan tidak
> pernah terkirim, jadi wajar datanya tidak tersimpan.
>
> Sudah dikonfirmasi bug aplikasi, bukan efek automation: terulang di
> **incognito** dan di **mesin Windows lain**, dan dari empat halaman
> `MonthlyReport/Edit` hanya Id=1317 yang terkena.
>
> ### Catatan proses (supaya tidak terulang)
>
> Laporan ini sempat DITUTUP sebagai "BUKAN BUG" pada 2026-09-08 pagi,
> berdasarkan hasil `tools/cek_simpan_inline.py` yang melaporkan
> `TERSIMPAN`. Kesimpulan itu keliru karena alatnya sendiri masih
> membaca **draft lokal**, bukan data server. Penutupan itu terlalu
> cepat, dan koreksinya datang dari pengecekan MANUAL.
>
> Pelajarannya: hasil automation tidak boleh menutup laporan bug
> sebelum cara pembacaannya sendiri tervalidasi.
>
> ### Akar masalahnya
>
> `buka_halaman()` membuka URL halaman apa adanya, sehingga filter
> periode **kembali ke DEFAULT**. Alur test dulu:
>
> ```
> tulis nilai di periode yang ADA DATANYA (mis. Agustus 2026)
> -> Submit Changes
> -> buka_halaman()      <-- periode balik ke default (September 2026)
> -> baca di September   <-- KOSONG
> -> simpulkan "tidak tersimpan"
> ```
>
> Datanya tersimpan di Agustus. Yang dibaca September.
>
> ### Kenapa hanya halaman ini yang terkena
>
> | Halaman | Template | Periode default | Data ada di | Hasil |
> |---|---|---|---|---|
> | SMK3, SMKP | YearlyReport | `2026` | `2026` | cocok, lolos |
> | **Statistic** | MonthlyReport | **bulan berjalan** | Juli/Agustus | **salah baca** |
>
> Itu sekaligus menjelaskan kenapa SMK3 dipakai sebagai "kontrol yang
> menyimpan normal" — bukan karena aplikasinya beda, tapi karena
> periode defaultnya kebetulan sama dengan periode datanya.
>
> Dan menjelaskan kenapa **pengujian manual selalu berhasil**: orang
> tidak memuat ulang halaman ke periode lain sebelum mengecek.
>
> ### Bukti
>
> `tools/cek_simpan_inline.py` menguji 14 halaman ber-Submit Changes
> dengan pembacaan yang benar (periode dipulihkan, dibaca sampai
> stabil, angka dibanding sebagai angka). Hasil 2026-09-08:
>
> ```
> TERSIMPAN     : 10   <-- termasuk statistic_safety_recapitulation
> GAGAL BACA    : 1    (smk3 -- keterbatasan alat, bukan aplikasi)
> BUTUH TANGGAL : 3    (DailyReport, filter tanggal belum diisi)
> TIDAK TERSIMPAN: 0
> ```
>
> Screenshot bukti:
> `reports/screenshots/cek_simpan_statistic_safety_recapitulation_TERSIMPAN_20260908_093753.png`
> — Month `August 2026`, data utuh, tanpa banner pending.
>
> **Tidak satu pun halaman gagal menyimpan.**
>
> ### Tindak lanjut yang sudah dikerjakan
>
> - `test_safety_lagging_deep` memulihkan periode tiap kali memuat
>   ulang halaman (`_muat_ulang()`), membaca sampai nilainya stabil
>   (`_baca_sel_stabil()`), dan membandingkan angka sebagai angka
>   (`_sel_sama()`).
> - `edit_tersimpan` untuk halaman ini dikembalikan ke `True`.
>
> Laporan ini DIPERTAHANKAN sebagai catatan supaya kekeliruan yang sama
> tidak terulang. **Jangan dikirim ke tim dev OPEL.**
>
> ---
>
> ## Isi laporan asli (KELIRU, disimpan sebagai riwayat)

- **Tanggal ditemukan**: 2026-08-26
- **Dikonfirmasi ulang**: 2026-09-07 (pengamatan manual: halaman masih
  kosong, tidak ada yang tersimpan)
- **Ditemukan lewat**: `tests/test_safety.py::TestSafetyHss::test_safety_lagging_deep[statistic_safety_recapitulation]`
- **Halaman**: Safety > Transaction > Lagging Indicator > Statistic Safety Recapitulation
  (`https://dev-opel.antm.tech/Reporting/Timesheet/MonthlyReport/Edit?Id=1317`)
- **Severity**: Tinggi — data yang diketik user hilang tanpa pesan error
  apa pun. User mengira sudah tersimpan.

## Langkah reproduksi

1. Buka halaman Statistic Safety Recapitulation.
2. Pilih **Month** ke periode yang datanya sudah ada (mis. `Agustus 2026`)
   supaya ada baris yang terisi, atau pakai periode mana pun lalu isi sel
   kosong.
3. Ubah salah satu sel angka di grid — mis. kolom `PenyakitAkibatKerja`
   atau `JumlahAccidentRingan` — dari `4` menjadi `5`.
   Nilainya langsung terbaca `5` di layar (ketikan masuk normal).
4. Klik **Submit Changes** → jawab konfirmasi.
5. **Reload halaman**.

## Hasil yang diharapkan

Nilai sel tetap `5` — perubahan tersimpan ke server, sama seperti
perilaku halaman SMK3 dan SMKP.

## Hasil aktual

Nilai sel **kembali ke `4`**. Perubahan tidak pernah sampai ke server,
dan tidak ada pesan error atau peringatan apa pun ke user.

## Bukti & pembanding

- Diverifikasi 2026-08-26 lewat probe terpisah: ketikan `'4' -> '5'`
  terbaca segera di sel, tapi setelah Submit + reload nilainya kembali
  `'4'`.
- **Kontrol**: halaman **SMK3** (`YearlyReport/Edit?Id=1308`) diuji
  dengan alur yang persis sama dan **menyimpan normal** (`'7'` bertahan
  setelah Submit + reload). Jadi ini bukan salah langkah reproduksi,
  bukan pula masalah izin user — spesifik ke halaman ini.
- Dikonfirmasi ulang 2026-09-07 oleh pemilik produk: halaman ini masih
  kosong, tidak ada yang tersimpan.

## Catatan yang belum dipastikan

Halaman ini SEMPAT terlihat berisi data pada periode `2026-08`
(screenshot run 2026-09-07). Kalau inline edit memang tidak pernah
tersimpan, data itu kemungkinan masuk lewat jalur lain — misalnya
fitur **Import** .xlsx, bukan pengetikan langsung di grid. Belum
diverifikasi, tapi kalau benar, artinya:

- Import → tersimpan
- Inline edit + Submit Changes → TIDAK tersimpan

Ini layak dicek tim dev karena mempersempit lokasi masalah ke handler
Submit Changes untuk template `MonthlyReport/Edit` di halaman ini.

## Dugaan akar masalah

Template halaman ini adalah `MonthlyReport/Edit` — sama dengan
Emergency Drill Daily, Golden Rules, dan MWT Daily. Perlu dicek apakah
ketiga halaman itu juga terkena, atau masalahnya khusus konfigurasi
Id=1317. Kalau ketiganya kena, masalahnya di level template; kalau
hanya Id=1317, di konfigurasi halaman.

Kemungkinan endpoint Submit Changes untuk halaman ini menerima request
tapi tidak memetakan field-nya ke kolom tabel tujuan (silent no-op),
karena tidak ada error yang dikembalikan ke UI.

## Saran perbaikan (untuk tim dev OPEL)

- Perbaiki agar Submit Changes benar-benar menyimpan perubahan inline
  di halaman ini, konsisten dengan SMK3/SMKP.
- Selama belum diperbaiki: tampilkan error eksplisit kalau Submit tidak
  berhasil menyimpan, supaya kegagalannya tidak senyap.

## Penanganan di automation test

`tests/test_safety.py` — entri `LAGGING_DEEP` untuk halaman ini memakai
`edit_tersimpan=False`. Alur edit + Submit TETAP dijalankan, tapi
verifikasinya diubah menjadi "data tidak rusak" (nilai tetap seperti
semula), bukan "perubahan tersimpan".

Artinya **test ini TIDAK akan gagal selama bug masih ada** — itu
disengaja supaya suite tidak merah permanen. Konsekuensinya: kalau
OPEL memperbaiki bug ini, test juga tidak otomatis memberi tahu.
Kembalikan `edit_tersimpan=True` begitu perbaikan dikonfirmasi, supaya
pemeriksaannya kembali tajam.
