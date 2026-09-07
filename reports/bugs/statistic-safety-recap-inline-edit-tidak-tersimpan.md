# Bug: Statistic Safety Recapitulation — perubahan inline tidak tersimpan lewat Submit Changes

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
