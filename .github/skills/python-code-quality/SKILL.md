---
name: python-code-quality
description: >-
  Menjaga kualitas kode Python sesuai PEP 8, Ruff, type hints, docstrings,
  penanganan error eksplisit, dan maintainability. Gunakan saat menulis,
  merapikan, atau meninjau kode Python di src/, scripts/, dashboard/, dan tests/.
---

# Python Code Quality

Adaptasi dari *Intermediate Research Software Development Skills (Python)* (The Carpentries Incubator, CC BY 4.0).

## Kondisi penggunaan

Gunakan saat menulis kode Python baru, meninjau PR/diff, atau membersihkan temuan linter sebelum commit.

## Workflow

1. **Patuhi konvensi gaya (PEP 8 & Ruff)**: Jalankan `ruff check` untuk memastikan impor rapi, tidak ada variabel/impor tak terpakai, dan gaya konsisten.
2. **Gunakan type hints dan docstrings ringkas**:
   - Berikan type hints pada parameter dan nilai kembali fungsi publik.
   - Tulis docstring singkat yang menjelaskan tujuan, argumen penting, dan nilai kembali (atau keterbatasan asumsi).
3. **Tangani error secara eksplisit**:
   - Tangkap exception spesifik (mis. `ValueError`, `UnicodeDecodeError`), bukan `except:` kosong.
   - Jangan menyembunyikan kegagalan atau diam-diam membuang baris bermasalah; catat atau karantina dengan alasan jelas.
4. **Tinjau keterbacaan**: Hindari duplikasi logika, fungsi terlalu panjang dengan nesting dalam, dan magic numbers tanpa penjelasan.

## Aturan validasi

- `ruff check` lulus tanpa error pada direktori kode proyek.
- Tidak ada `except Exception` yang menelan error tanpa logging atau propagasi yang jelas.
- Komentar menjelaskan *mengapa* suatu aturan/batasan diterapkan, bukan mengulang isi kode.

## Output yang diharapkan

Kode Python bersih, bertipe jelas, terdokumentasi ringkas, aman terhadap error, dan lolos pemeriksaan `ruff`.
