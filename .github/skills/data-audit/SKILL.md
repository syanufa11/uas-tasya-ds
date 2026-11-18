---
name: data-audit
description: >-
  Mengaudit struktur, kualitas, cakupan waktu, dan kelayakan variabel ekspor
  Samsung Health secara read-only. Gunakan untuk inventaris, kamus data,
  atau pemeriksaan ulang skema; tidak melakukan cleaning dataset final.
---

# Data Audit

## Kondisi penggunaan

Gunakan sebelum cleaning atau ketika ekspor, skema, dan asumsi variabel berubah.

## Workflow

1. Baca hasil di `data_audit/` bila tersedia dan cocokkan provenance dengan
   sumber saat ini; hasil lama tidak otomatis berlaku pada ekspor baru.
2. Untuk parsing mentah, baca [aturan Samsung Health](references/samsung-export.md).
   Periksa `scripts/audit_samsung_health.py` sebelum menjalankan ulang dari root
   dengan `python scripts/audit_samsung_health.py`; eksekusi memperbarui hasil
   lokal di `data_audit/`, bukan sumber mentah.
3. Inventarisasi seluruh CSV/JSON, tipe teramati, null/key tidak hadir,
   duplikasi, rentang waktu, satuan, zona waktu, dan relasi antarfile.
4. Periksa interval tidur, overlap, gap, sentinel, kolom konstan/kosong, dan
   asal perangkat. Telusuri data pendamping tanpa memperlakukannya sebagai
   sesi baru atau bukti tersedianya skor/tahap tidur.
5. Susun kamus data dan keputusan kelayakan per variabel; tandai definisi
   yang perlu dokumentasi. Ajukan rencana cleaning tanpa menerapkannya.

## Aturan validasi

- Rekonsiliasi jumlah file/record dan kegagalan parse; nyatakan cakupan penuh
  atau sampling. Bandingkan manifest/hash sumber sebelum-sesudah.
- Bedakan tipe inferensi dengan skema resmi dan duplikasi byte dengan
  duplikasi kejadian. Jangan diam-diam membuang baris bermasalah.
- Temuan belum terverifikasi tidak dinaikkan menjadi fakta semantik.

## Output yang diharapkan

Inventaris, kamus data, laporan audit lokal, status kelayakan variabel, dan daftar
masalah beserta rekomendasi cleaning. Artefak sensitif tetap di `data_audit/`.
