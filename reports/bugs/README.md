# Indeks Laporan Bug — HSS Safety

Ringkasan status semua laporan di folder ini. **Baca ini dulu** sebelum
mengirim apa pun ke tim dev OPEL — sebagian laporan sudah ditutup dan
tidak boleh dikirim.

Terakhir diperbarui: **2026-09-08**

| Laporan | Status | Kirim ke dev? |
|---|---|---|
| [submit-changes-redirect-tanpa-menyimpan](submit-changes-redirect-tanpa-menyimpan.md) | **TERBUKA** | **YA** |
| [witness-statement-submit-membuang-baris-baru](witness-statement-submit-membuang-baris-baru.md) | **TERBUKA** | **YA** |
| [statistic-safety-recap-inline-edit-tidak-tersimpan](statistic-safety-recap-inline-edit-tidak-tersimpan.md) | Gejala dari laporan di atas | Tidak — sudah tercakup |
| [master-alat-submit-drops-new-row](master-alat-submit-drops-new-row.md) | Sudah diperbaiki aplikasi | Tidak |
| [lagging-cancel-does-not-discard-edit](lagging-cancel-does-not-discard-edit.md) | BUKAN BUG (salah asumsi test) | Tidak |

---

## 1. Submit Changes redirect tanpa menyimpan — **TERBUKA**

Satu-satunya bug aplikasi yang masih terbuka.

- **Halaman**: Statistic Safety Recapitulation, `MonthlyReport/Edit?Id=1317`
- **Gejala**: klik Submit Changes langsung me-redirect ke
  `YearlyReport/Edit?Id=1317&DistrictCode=...` **sebelum dialog
  konfirmasi muncul**. Request penyimpanan tidak pernah terkirim.
- **Cakupan**: hanya Id=1317. Tiga halaman `MonthlyReport/Edit` lain
  (1316, 1312, 1319) normal — jadi bug konfigurasi, bukan bug template.
- **Sifat**: **INTERMITEN.** Tidak muncul di setiap percobaan. Ini
  WAJIB disebut saat melapor, supaya tidak ditutup sebagai
  "cannot reproduce".
- **Bukan efek testing**: terulang di incognito dan di mesin lain.
- **Di suite**: didaftar di
  `HssSafetyPage.SUBMIT_REDIRECT_TANPA_SIMPAN` supaya suite tidak merah
  permanen. Pemeriksaan penyimpanan dilonggarkan jadi peringatan
  `[BUG DIKENAL]`; langkah lain tetap di-assert ketat.

## 2. Witness Statement — Submit membuang baris baru — **TERBUKA**

- **Halaman**: Witness Statement Report, `DailyReport/Edit?Id=1336`
- **Gejala**: baris baru (jalur mana pun) **hilang** setelah Submit
  Changes. Dikonfirmasi manual: *"setelah Submit Changes malah hilang
  semua"*.
- **Berlaku di kedua jalur input**: Create with Form (ketemu
  2026-08-26) dan Create + isi langsung di grid (2026-09-08).
- **Bukan bug template**: Initial Incident/Accident (Id=1335,
  DailyReport, alur sama persis) lulus.
- **Di suite**: didaftar di
  `HssSafetyPage.CREATE_INLINE_TIDAK_TERSIMPAN`.

## 3. Statistic Safety Recap tidak menyimpan — gejala, bukan akar

Temuan asli 2026-08-26. **Gejalanya nyata**, tapi akar masalahnya
ternyata laporan nomor 1. Dipertahankan sebagai riwayat.

Catatan proses: laporan ini sempat ditutup sebagai "BUKAN BUG" pada
2026-09-08 berdasarkan hasil automation yang ternyata membaca **draft
lokal**, bukan data server. Koreksinya datang dari pengecekan manual.

## 4. Master Alat — Submit membuang baris baru — SUDAH DIPERBAIKI

Ditemukan 2026-08-31, diverifikasi manual 2026-09-07: sudah tidak
terjadi lagi. Ditutup.

## 5. Cancel tidak membuang perubahan — BUKAN BUG

Laporan yang keliru. Draft lokal memang **sengaja** dipertahankan OPEL
sebagai fitur perlindungan (kalau halaman ter-reload atau koneksi
putus). Yang membuangnya adalah tombol **Reload Data**, bukan Cancel.

Test yang melahirkan laporan ini memakai asumsi salah dan sudah
diperbaiki: sekarang yang diuji adalah Reload Data.

---

## Pelajaran yang berlaku untuk laporan berikutnya

Empat laporan di atas menghasilkan tiga pelajaran yang mahal:

1. **Jangan tutup laporan bug berdasarkan hasil automation sebelum cara
   pembacaan automation-nya sendiri tervalidasi.** Laporan 1 & 2 sempat
   ditutup keliru karena alatnya membaca draft lokal.
2. **Verifikasi penyimpanan HARUS lewat Reload Data**, bukan reload
   browser atau `buka_halaman()` — keduanya memulihkan draft lokal dan
   menampilkan nilai yang baru saja diketik, seolah tersimpan.
3. **Sebutkan kalau bug-nya intermiten.** Bug tidak deterministik yang
   dilaporkan seolah pasti terjadi biasanya ditutup sebagai
   "cannot reproduce".

Alat bantu yang memverifikasi hal-hal ini: `tools/cek_simpan_inline.py`.
