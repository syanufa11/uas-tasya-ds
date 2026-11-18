---
name: docx-academic-report
description: >-
  Membuat atau mengedit laporan akademik Word .docx dengan heading, tabel,
  caption, rumus, dan daftar pustaka yang konsisten. Aktif untuk keluaran Word;
  gunakan academic-report untuk logika pembahasan, bukan sebagai generator DOCX.
---

# Laporan akademik Word

## Workflow

1. Baca rubrik, template, gaya sitasi, dan artefak bukti. Untuk isi penelitian,
   gunakan `academic-report` yang sudah ada; jangan menduplikasi alur CRISP-DM.
2. Jika ada template, buat cadangan sebelum menimpa; pertahankan cover,
   identitas, logo, section, header/footer, serta aset yang diminta.
3. Buat/edit dengan `python-docx`. Baca [panduan format](references/docx-workflow.md)
   saat menangani styles, caption, daftar isi, atau rumus. Gunakan heading
   semantik dan styles, bukan format manual berulang.
4. Cocokkan narasi, tabel, gambar, simbol, unit, dan sitasi dengan sumbernya.
   Terapkan `clear-indonesian-writing`; aktifkan `academic-paraphrasing` hanya
   untuk penyuntingan teks sumber yang diminta.
5. Simpan file baru, buka ulang, render seluruh halaman, inspeksi, dan revisi.

## Checklist validasi

- [ ] Heading bertingkat, margin, spasi, font, penomoran, dan daftar isi konsisten.
- [ ] Tabel tidak melewati margin; caption dan objeknya tidak terpisah secara buruk.
- [ ] Rumus benar, simbol didefinisikan, satuan dan nomor persamaan konsisten.
- [ ] Setiap sitasi memiliki sumber nyata yang mendukung klaim; tidak ada referensi rekaan.
- [ ] Angka dan simpulan cocok dengan artefak analisis; bagian belum tersedia ditandai.
- [ ] DOCX dibuka ulang; seluruh halaman render diperiksa untuk pemenggalan dan glyph.
- [ ] Cover/aset template terpelihara; metadata, komentar, dan revisi ditinjau sebelum berbagi.

## Hasil

File `.docx`, ringkasan perubahan, status pembukaan dan QA visual, serta bagian
yang masih memerlukan bukti atau pembaruan field. Jangan mengklaim field dinamis
telah diperbarui jika belum diperiksa di aplikasi.
