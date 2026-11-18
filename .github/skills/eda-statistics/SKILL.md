---
name: eda-statistics
description: >-
  Mengeksplorasi pola tidur dan aktivitas Samsung Health serta statistik
  deskriptif atau inferensial untuk data temporal individu. Gunakan untuk EDA,
  grafik, asosiasi, dan uji hipotesis; bukan tuning model.
---

# EDA dan Statistik

## Kondisi penggunaan

Gunakan ketika definisi variabel, unit analisis, dan status cleaning jelas.

## Workflow

1. Tetapkan pertanyaan, unit observasi, periode, denominator, dan subset.
   Tampilkan cakupan/gap sebelum membandingkan kelompok.
2. Hitung distribusi, median/kuartil atau rerata/simpangan baku sesuai bentuk
   data; sertakan jumlah observasi valid dan missing untuk tiap ringkasan.
3. Jelajahi tren waktu, variasi hari, outlier, dan hubungan aktivitas-tidur.
   Untuk jam melintasi tengah malam, gunakan representasi sirkular atau acuan
   waktu yang dinyatakan; jangan merata-ratakan jam secara naif.
4. Jika inferensi diminta, periksa autokorelasi, distribusi, ukuran sampel efektif,
   dan asumsi uji. Pilih metode yang menghormati dependensi waktu. Untuk banyak
   pengujian, tentukan koreksi atau tandai sebagai eksploratif.
5. Laporkan effect size dan interval ketidakpastian jika layak, kemudian
   interpretasikan tanpa mengubah asosiasi menjadi kausalitas.

## Aturan validasi

- Angka/grafik memakai subset, filter, dan satuan eksplisit; missing bukan nol.
- Observasi berulang satu individu bukan sampel individu independen; gunakan
  block bootstrap bila bootstrap temporal memang diperlukan.
- Untuk studi prediktif, gunakan train dalam pemilihan fitur/hipotesis;
  jangan memakai test untuk mengarahkan eksperimen.
- Periksa label, legenda, ukuran plot, dan keterbacaan render.

## Output yang diharapkan

Tabel statistik dan grafik berlabel, metode/asumsi, interpretasi berbasis output,
serta keterbatasan cakupan, dependensi waktu, dan generalisasi.
