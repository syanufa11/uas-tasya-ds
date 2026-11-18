# Pengolahan DOCX

- Dependensi opsional: `requirements-documents.txt`; setup dan smoke test:
  `docs/academic-skills.md` di root repository.
- Buat `Document()` atau edit `Document(path)`. Terapkan `Title`, `Heading 1`,
  `Heading 2`, `Normal`, dan `Caption`. Ikuti aturan kampus/template untuk margin,
  font dan spasi; jangan memaksakan format baru pada template pengguna.
- Hindari mengganti `paragraph.text` pada paragraf dengan field, hyperlink,
  atau format campuran karena run aslinya dapat hilang. Edit run yang diperlukan.
- Gunakan tabel native dengan header yang jelas dan lebar sesuai area cetak.
  Grafik berasal dari artefak analisis; caption memuat nomor, judul, dan sumber.
- Untuk rumus sederhana gunakan OMML (`m:oMath`), definisikan simbol dan unit.
  Konversi LaTeX kompleks dengan tool terverifikasi jika tersedia; jangan
  mengasumsikan teks LaTeX mentah otomatis menjadi persamaan Word.
- Gunakan field `SEQ`/`REF`/`TOC` bila butuh penomoran, cross-reference, atau
  daftar isi dinamis. `python-docx` tidak menghitung hasil field: perbarui dan
  periksa di Word/LibreOffice. Penomoran statis boleh untuk dokumen sederhana,
  tetapi harus dicocokkan ulang setelah revisi.
- Daftar pustaka mengikuti gaya yang diminta; cocokkan sitasi dua arah dengan
  daftar pustaka dan verifikasi metadata di sumber primer.
- Validasi ZIP CRC dan XML, lalu buka ulang. Render dengan Word/LibreOffice
  ke PDF/PNG dan periksa semua halaman: margin, glyph rumus, tabel, caption,
  header/footer, serta page break. Jika renderer tidak tersedia, nyatakan batas QA.

API primer: [python-docx](https://python-docx.readthedocs.io/en/latest/).
