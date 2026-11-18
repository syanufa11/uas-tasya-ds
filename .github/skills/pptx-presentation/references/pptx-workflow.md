# Pengolahan PPTX

- Gunakan dependensi opsional pada `requirements-documents.txt` di root;
  panduan instalasi dan smoke test ada di `docs/academic-skills.md`.
- Untuk membuat: `Presentation()`; untuk mengedit: `Presentation(path)`.
  Baca layout dan ukuran deck sumber sebelum menambahkan slide.
- Tentukan ukuran dengan `pptx.util.Inches`, font dengan `Pt`, dan teks dengan
  paragraf/run. Jangan meratakan seluruh slide menjadi gambar.
- Tabel besar dipisah menjadi beberapa slide; diagram memakai shape dan
  connector. Gunakan chart native atau gambar dari output analisis terverifikasi.
- Pada template kompleks, simpan salinan dahulu. Animasi, objek tertanam, dan
  fitur yang tidak didukung library perlu diuji di PowerPoint setelah round-trip.
- Uji ZIP CRC, XML, buka ulang melalui library, lalu buka di PowerPoint atau
  LibreOffice. Ekspor PDF/PNG untuk memeriksa setiap slide pada ukuran baca.
  LibreOffice dapat memakai `soffice --headless --convert-to pdf --outdir DIR FILE`;
  gunakan profil sementara terpisah jika ada proses LibreOffice aktif.
- Bila renderer tidak ada, laporkan QA visual tertunda; jangan menganggap
  ekstraksi teks sebagai bukti tampilan benar.

API primer: [python-pptx](https://python-pptx.readthedocs.io/en/latest/).
