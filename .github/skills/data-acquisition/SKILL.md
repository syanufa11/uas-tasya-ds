---
name: data-acquisition
description: >-
  Menyiapkan akses lokal dan provenance ekspor Samsung Health untuk UAS.
  Gunakan ketika menerima ekspor baru atau mengatur lokasi input; audit isi
  dan transformasi dataset merupakan pekerjaan terpisah.
---

# Data Acquisition

## Kondisi penggunaan

Gunakan saat ekspor pertama diterima, sumber diperbarui, atau lokasi input berubah.

## Workflow

1. Identifikasi direktori `samsunghealth_*` melalui konfigurasi/pilihan eksplisit.
   Jika ada beberapa ekspor, jangan otomatis memilih yang terbaru.
2. Catat sumber aplikasi, waktu penerimaan/ekspor jika diketahui, format, dan
   cakupan izin penggunaan; bedakan waktu ekspor dari periode observasi.
3. Buat manifest lokal berisi path relatif, ukuran, dan SHA-256 setiap file.
   Jika mengekstrak arsip, gunakan direktori terpisah, cegah path keluar dari
   tujuan ekstraksi, dan pertahankan arsip sumber.
4. Pisahkan input dari hasil olahan; periksa `.gitignore` terhadap sumber dan
   manifest sensitif sebelum menyiapkan file untuk dibagikan.
5. Serahkan lokasi input dan manifest ke audit. Jangan menggabungkan data,
   memperbaiki baris, atau menarik data tambahan yang belum diminta.

## Aturan validasi

- Rekonsiliasi file yang dipilih dengan manifest; laporkan file tidak terbaca.
- Bandingkan hash sumber dan salinan jika penyalinan dilakukan.
- Sumber tetap utuh; jangan menaruh identitas akun atau path personal di
  dokumentasi yang akan masuk Git.

## Output yang diharapkan

Konfigurasi input, manifest sumber lokal, catatan provenance, dan status kesiapan
audit beserta kendala akses. Belum menghasilkan dataset analisis.
