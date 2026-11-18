---
name: data-cleaning
description: >-
  Membersihkan dan mengintegrasikan Samsung Health berdasarkan audit, termasuk
  interval tidur, agregasi, missing values, dan fitur turunan. Gunakan untuk
  dataset analisis terjejak; bukan audit read-only.
---

# Data Cleaning

## Kondisi penggunaan

Gunakan setelah unit analisis dan masalah kualitas sumber diidentifikasi.

## Workflow

1. Ambil aturan dari audit dan brief; tetapkan kontrak input/output, kunci unik,
   satuan, basis waktu, serta keputusan untuk tiap masalah kualitas.
2. Bangun fungsi deterministik dengan konfigurasi eksplisit; simpan hasil
   terpisah dari sumber. Karantina record yang gagal beserta alasannya.
3. Normalisasi tipe/satuan/waktu berdasarkan bukti. Tetapkan penanganan sesi
   lintas hari, overlap, dan tidur siang sesuai unit analisis. Jangan otomatis
   menjumlahkan interval overlap atau mengisi hari tanpa catatan dengan nol.
4. Periksa kardinalitas sebelum join dan rekonsiliasi jumlah sesudahnya.
   Dokumentasikan deduplikasi/agregasi serta provenance setiap fitur.
5. Tangani missing, sentinel, dan outlier per variabel. Pisahkan transformasi
   deterministik dari imputasi/scaling berbasis distribusi yang harus dipelajari
   hanya pada data latih dalam tahap modeling.

## Aturan validasi

- Rekonsiliasi record masuk, dikarantina/dihapus, digabung, dan keluar dengan
  alasan; audit ulang missing, kunci, rentang, satuan, dan urutan waktu.
- Uji kasus batas relevan dengan fixture sintetis berlabel: lintas tengah
  malam, overlap, missing, dan join one-to-many; cocokkan hasil hitung harapan.
- Eksekusi ulang pada input/config sama menghasilkan data setara; sumber tetap
  utuh. Fitur turunan memiliki rumus dan tidak dilabeli skor resmi Samsung.

## Output yang diharapkan

Kode transformasi, dataset olahan lokal, kamus fitur, log keputusan/jumlah record,
dan hasil validasi sebelum-sesudah cleaning.
