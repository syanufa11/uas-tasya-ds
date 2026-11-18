---
name: python-testing
description: >-
  Menulis dan menjalankan pengujian otomatis Python menggunakan pytest dengan
  fixture sintetis, kasus batas, dan regression testing. Gunakan saat menambah
  fungsi di src/, memvalidasi transformasi data, atau memperbaiki bug.
---

# Python Testing

Adaptasi dari *Intermediate Research Software Development Skills (Python)* (The Carpentries Incubator, CC BY 4.0).

## Kondisi penggunaan

Gunakan saat menambah atau mengubah fungsi parsing, validasi waktu, cleaning, deteksi overlap, perhitungan metrik, atau memperbaiki bug agar tidak terulang.

## Workflow

1. **Gunakan fixture sintetis**: Buat data uji kecil yang aman dan anonim di `tests/` (`@pytest.fixture`); jangan pernah bergantung pada folder `samsunghealth_*` atau `data_audit/` pribadi.
2. **Uji perilaku inti dan kasus batas (`@pytest.mark.parametrize`)**:
   - Input kosong, kolom hilang, dan missing values (`NaN`/`None`/string kosong).
   - Sesi tidur lintas tengah malam, durasi nol/negatif, dan sesi overlap vs bersentuhan.
   - Parsing timestamp ISO/epoch dan konversi zona waktu tanpa pergeseran ganda.
3. **Tambahkan regression test**: Setiap bug yang ditemukan harus disertai test yang gagal sebelum perbaikan dan lulus setelah perbaikan.
4. **Verifikasi determinisme dan integritas**: Pastikan fungsi tidak memodifikasi input mentah secara in-place tanpa sengaja dan menghasilkan output identik pada input sama.
5. **Jalankan suite pengujian**: Eksekusi `pytest` dari root proyek setelah perubahan selesai.

## Aturan validasi

- Seluruh test berjalan mandiri tanpa akses ke data kesehatan pribadi atau jaringan eksternal.
- Assertion memeriksa nilai, tipe, dan flag kasus bermasalah secara spesifik (bukan sekadar tidak error).
- Hasil `pytest` dilaporkan apa adanya sesuai eksekusi aktual.

## Output yang diharapkan

Suite test di `tests/` berbasis fixture sintetis yang mencakup jalur normal, edge cases, dan bukti eksekusi `pytest` yang lulus.
