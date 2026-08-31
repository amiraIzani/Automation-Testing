# Bug: Submit Changes membuang baris baru (Create with Form) kalau ada draft kosong lain di grid

- **Tanggal ditemukan**: 2026-08-31
- **Ditemukan lewat**: `tests/test_safety.py::TestSafetyHss::test_safety_master_alat_create`
- **Halaman**: Safety > Transaction > Leading Indicator > Master Alat Keselamatan Operasi
  (`https://dev-opel.antm.tech/Reporting/Timesheet/StaticReport/Edit?Id=1321`)
- **Kemungkinan berlaku juga di**: halaman lain dengan grid CRUD serupa yang
  punya tombol "Create" (polos) + "Create with Form" + "Submit Changes"
  (SOC Recapitulation, MWT Daily, Golden Rules, dll — belum diverifikasi
  satu-satu, tapi arsitektur grid & tombolnya sama).
- **Severity**: Tinggi — kehilangan data user secara SENYAP (tanpa error
  apa pun ke user).

## Langkah reproduksi

1. Buka halaman Master Alat Keselamatan Operasi.
2. Pastikan ada **minimal satu baris draft kosong** di grid (semua sel
   kosong). Ini gampang terjadi tanpa sengaja: user klik tombol **Create**
   (bukan "Create with Form") yang langsung menambah baris draft kosong ke
   grid, lalu user membatalkan niatnya / pindah halaman tanpa mengisi atau
   menghapus baris itu.
3. Klik **Create with Form**, isi semua field wajib dengan data valid
   (Equipment No unik, Location & Type dari combo lookup, Capacity angka).
4. Klik **Save** — baris baru muncul di grid sebagai draft belum ter-submit.
5. Klik **Submit Changes**.
6. Reload halaman (atau cari Equipment No yang baru dibuat lewat search/API
   grid).

## Hasil yang diharapkan

Baris baru (Equipment No yang baru dibuat di langkah 3) tersimpan dan tetap
tampil di grid setelah reload.

## Hasil aktual

Baris baru **hilang total** dari grid setelah Submit Changes + reload —
seolah tidak pernah dibuat, tanpa pesan error apa pun. Baris draft kosong
dari langkah 2 tetap ada, tidak berubah.

## Bukti

Screenshot kegagalan test otomatis:
`reports/screenshots/test_safety_master_alat_create_20260831_131606.png`

Screenshot menunjukkan baris #2 di grid kosong total (Equipment No,
Location, Type, Capacity semuanya blank) berdampingan dengan puluhan baris
`AUTO-TEST-*` yang sudah tersimpan dari run-run sebelumnya — sementara baris
baru `AUTO-TEST-114211` yang seharusnya dibuat pada percobaan itu tidak
pernah muncul di grid manapun (sudah dicek lewat search API DataTables,
termasuk setelah reload halaman).

## Dugaan akar masalah

Endpoint Submit Changes tampaknya memvalidasi/mem-proses SEMUA baris
pending sebagai satu batch. Kalau salah satu baris pending (draft kosong)
gagal validasi, kemungkinan seluruh batch — termasuk baris lain yang VALID
— ikut dibuang, bukan cuma baris yang bermasalah.

## Saran perbaikan (untuk tim dev OPEL)

- Submit Changes seharusnya memvalidasi tiap baris pending SECARA
  INDEPENDEN: baris valid tetap tersimpan meski ada baris lain yang gagal.
- Baris draft kosong (dibuat lewat tombol "Create" tapi tidak diisi)
  sebaiknya otomatis diabaikan/tidak dikirim ke Submit, bukan dianggap
  baris pending yang gagal validasi.
- Minimal: tampilkan pesan error eksplisit yang menunjuk baris mana yang
  bermasalah, supaya kegagalan tidak senyap.

## Workaround yang sudah diterapkan di automation test

`pages/hss_safety_page.py` — helper `_hapus_baris_kosong()` sekarang
dipanggil di awal setiap alur Create with Form
(`test_safety_master_alat_create` dan `create_dengan_form_sungguhan()`)
untuk membersihkan draft kosong lebih dulu, supaya test tidak lagi
tersandung bug ini. Ini HANYA workaround di sisi test — bug di aplikasinya
sendiri belum diperbaiki.

## Catatan tambahan (kebersihan data DEV)

Grid Master Alat Keselamatan Operasi di DEV saat ini sudah menumpuk puluhan
baris `AUTO-TEST-*` dari run-run sebelumnya (21 Aug, 27 Aug, 28 Aug, 31 Aug)
yang tidak pernah dibersihkan. Baris-baris ini tidak memicu bug di atas
(karena tidak kosong), tapi sebaiknya dibersihkan manual sesekali supaya
data DEV tidak terus menumpuk.
