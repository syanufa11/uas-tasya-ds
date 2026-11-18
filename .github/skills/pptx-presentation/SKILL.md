---
name: pptx-presentation
description: >-
  Membuat atau mengedit presentasi PowerPoint .pptx akademik, termasuk layout,
  diagram, grafik, dan pemeriksaan tampilan. Aktif untuk permintaan slide atau
  presentasi; bukan untuk laporan Word atau penyuntingan paragraf saja.
---

# Presentasi akademik

## Workflow

1. Baca rubrik, durasi, audiens, template, serta artefak analisis yang tersedia.
   Petakan setiap klaim dan angka ke bukti; gunakan `academic-report` hanya
   bila perlu menyusun pembahasan penelitian.
2. Buat alur pertanyaan, metode, bukti, keterbatasan, dan simpulan sesuai brief.
   Satu pesan utama per slide; pindahkan rincian ke catatan atau lampiran.
3. Gunakan template pengguna. Jika tidak ada, pilih 16:9, margin konsisten,
   judul sekitar 28–36 pt dan isi 20–24 pt. Pecah slide padat sebelum mengecilkan font.
4. Buat/edit dengan `python-pptx`; baca [panduan teknis](references/pptx-workflow.md)
   hanya saat mengolah file. Utamakan teks, tabel, diagram, dan grafik editable.
   Jelaskan sumbu, unit, legenda, sumber, serta ketidakpastian visualisasi.
5. Simpan sebagai file baru, buka ulang, render semua slide, periksa, dan revisi.
   Terapkan `clear-indonesian-writing` pada narasi akademik; gunakan
   `academic-paraphrasing` hanya jika ada teks sumber yang diminta disunting.

## Checklist validasi

- [ ] Angka, periode, satuan, sitasi, dan simpulan cocok dengan artefak sumber.
- [ ] Data contoh diberi label sintetis; tidak ada hasil atau referensi rekaan.
- [ ] Template, rasio slide, font, warna, dan penomoran konsisten.
- [ ] Diagram bermakna; teks terbaca; tidak ada clipping, overlap, atau slide padat.
- [ ] PPTX dibuka ulang dan setiap slide hasil render diperiksa secara visual.
- [ ] Metadata/catatan tidak membocorkan data privat; batas QA dilaporkan apa adanya.

## Hasil

File `.pptx`, ringkasan perubahan, sumber bukti, dan status pemeriksaan isi,
pembukaan file, serta QA visual. Jangan menyamakan validasi ZIP dengan uji PowerPoint.
