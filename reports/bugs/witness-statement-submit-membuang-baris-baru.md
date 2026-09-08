# Bug: Witness Statement Report — Submit Changes membuang baris baru (semua jalur input)

- **Tanggal ditemukan (otomatis)**: 2026-09-08 lewat
  `test_safety_create_inline[Witness Statement]`
- **Dikonfirmasi manual**: 2026-09-08 oleh pemilik produk — *"setelah
  Submit Changes malah hilang semua"*
- **Halaman**: Safety > Transaction > Leading Indicator > Witness Statement Report
  (`https://dev-opel.antm.tech/Reporting/Timesheet/DailyReport/Edit?Id=1336`)
- **Severity**: TINGGI — data yang sudah diketik user hilang total
  setelah Submit, tanpa pesan error apa pun.
- **Status**: **TERBUKA**

## Langkah reproduksi

1. Buka halaman, set **Date = 08/09/2026**, District **[AT10] KANTOR PUSAT**.
2. Pastikan tab **Keterangan Saksi** aktif.
3. Klik **Create** → muncul baris draft kosong di grid.
4. Isi beberapa kolom teks langsung di grid (mis. **Nama Saksi** =
   `UJI-MANUAL`).
5. Klik **Submit Changes** → jawab konfirmasi.

## Hasil yang diharapkan

Baris tersimpan dan tetap tampil di grid.

## Hasil aktual

Baris **hilang** setelah Submit. Grid kembali
`Showing 0 to 0 of 0 entries`. Tidak ada pesan error.

Bukti otomatis: 26 kolom terbukti terisi sebelum Submit —
`NoInsiden`, `NamaSaksi`, `NIK`, `NomorID`, `Jabatan`, `Perusahaan`,
`DepartemenDivisi`, `TempatTanggalLahir`, `Umur`,
`LamanyaBekerjaPadaJabatan`, `PengalamanBekerja`, `Tupoksi`,
`LokasiKerja`, `AlamatDapatDihubungi`, `NamaPengawasLangsung`,
`HariTanggalKejadian`, `TanggalWaktuWawancara`, `NomorUrutWawancara`,
`RingkasanInsiden`, `KeteranganRingkas`, `KondisiKesehatanSaksi`,
`TempatPernyataan`, `TanggalPernyataan`, `NamaPewawancara`,
`NIKPewawancara`, `JabatanPewawancara`.

Screenshot:
`reports/screenshots/test_safety_create_inline[Witness Statement]_20260908_152718.png`
— Date `08/09/2026`, tab Keterangan Saksi aktif, grid kosong.

## Berlaku di KEDUA jalur input

Yang membuat temuan ini kuat: dua cara input berbeda gagal dengan
gejala sama, ditemukan berjarak 13 hari dan lewat test yang berbeda.

| Jalur input | Ditemukan | Gejala |
|---|---|---|
| **Create with Form** (modal) | 2026-08-26 | baris baru tidak muncul di grid |
| **Create + isi langsung di grid** | 2026-09-08 | baris hilang setelah Submit |

Jalur modal sudah lebih dulu terdaftar di
`HssSafetyPage.CREATE_FORM_TANPA_PERSISTENSI` dengan catatan
*"TIDAK menampilkan baris baru di grid yang bisa dibaca"*. Waktu itu
dikira sekadar masalah tampilan; sekarang jelas datanya memang tidak
tersimpan.

## Bukan masalah template, tanggal, atau tab

Sudah disingkirkan satu per satu:

| Kecurigaan | Bukti bahwa bukan itu |
|---|---|
| Salah tanggal | Screenshot: `Date = 08/09/2026`, sesuai yang di-set |
| Salah tab | Tab "Keterangan Saksi" aktif — tab tempat tombol Create berada |
| Bug template DailyReport | **Initial Incident/Accident** (Id=1335, DailyReport, tanggal & alur sama persis) **LULUS** |
| Kolom tanggal baris tidak terisi | `HariTanggalKejadian`, `TanggalWaktuWawancara`, `TanggalPernyataan` semuanya terisi |
| Test membaca draft lokal | Verifikasi lewat **Reload Data**, bukan reload halaman |

Dari 9 halaman ber-tombol Create yang diuji jalur inline-nya:
**7 lulus**, 1 skip (Incident Investigation — baris draft tidak muncul),
**1 gagal (halaman ini)**.

## Yang masih perlu dipastikan

- Apakah baris yang SUDAH ADA sebelumnya ikut hilang, atau hanya baris
  baru? Grid pada pengujian ini memang kosong sejak awal, jadi belum
  terjawab. Kalau data lama ikut hilang, severity naik jadi kritis.
- Apakah tab kedua ("Pertanyaan Wawancara") juga terkena?
- Apakah berlaku di semua district, atau khusus AT10?

## Saran perbaikan (untuk tim dev OPEL)

- Submit Changes di halaman ini harus menyimpan baris baru, konsisten
  dengan Id=1335 yang templatenya sama.
- Selama belum diperbaiki: tampilkan error eksplisit kalau penyimpanan
  gagal — kehilangan data yang senyap jauh lebih berbahaya daripada
  pesan gagal.

## Penanganan di automation test

`witness_statement_report` didaftar di
`HssSafetyPage.CREATE_INLINE_TIDAK_TERSIMPAN` supaya suite tidak merah
permanen. Kegagalan dicetak sebagai `[BUG DIKENAL]`, dan kalau suatu
saat berhasil, test mencetak `[BUG SUDAH DIPERBAIKI?]` supaya halaman
ini dikeluarkan dari daftar.
