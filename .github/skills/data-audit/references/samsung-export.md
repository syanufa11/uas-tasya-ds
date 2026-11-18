# Parsing ekspor Samsung Health

Baca saat memeriksa file mentah atau mengubah parser. Pola dari audit lokal
berikut perlu diverifikasi ulang pada ekspor lain.

- CSV dapat memiliki BOM, preamble sebelum header, serta field kosong tambahan
  di ujung record. Deteksi per file; jangan memakai `skiprows=1` tanpa verifikasi.
  Toleransi field terminal hanya jika kosong dan lebar record selain itu sesuai.
  Hindari `on_bad_lines='skip'`.
- Pertahankan nama kolom asli. Catat header ganda, lebar record tidak sesuai,
  encoding gagal, dan JSON kosong/tidak valid secara terpisah.
- JSON bisa berupa object, list, atau string berisi JSON bertingkat. Bedakan
  key tidak hadir, null, string kosong, dan array kosong. Persentase missing
  perlu denominator jelas; path nested bukan tabel persegi.
- Timestamp teks tanpa zona tidak otomatis UTC/Asia/Jakarta. Kandidat epoch
  detik/milidetik memerlukan bukti nama field, rentang, dan relasi lintas sumber.
  Jangan mengonversi durasi/target jam menjadi tanggal.
- Selisih `end_time - start_time` adalah durasi interval tercatat. Periksa
  nilai negatif, lintas tengah malam, overlap, dan basis waktu terlebih dahulu.
- Kolom skor/tahap kosong, nilai konstan nol, kode negatif, atau batas integer
  bukan ukuran kualitas valid tanpa definisi terverifikasi. Cache preferensi
  dan ringkasan aplikasi tidak menggantikan sesi pengukuran.
- JSON byte-identik dapat dirujuk sesi berbeda. Periksa foreign key,
  kardinalitas, orphan, dan penggandaan baris sebelum merekomendasikan join.
- Inventaris lokal memiliki sel metadata besar. Pembacaan dengan modul `csv`
  memerlukan batas field memadai; audit saat ini menggunakan
  `csv.field_size_limit(100_000_000)`. pandas dapat menjadi alternatif.
