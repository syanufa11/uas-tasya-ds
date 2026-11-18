---
name: python-collaboration
description: >-
  Panduan kolaborasi Git dan GitHub: alur kerja branch, konvensi commit,
  tinjauan kode/PR, pencegahan kebocoran data sensitif, dan sinkronisasi CI.
  Gunakan sebelum melakukan commit, review perubahan, atau push ke remote.
---

# Python Collaboration

Adaptasi dari *Intermediate Research Software Development Skills (Python)* (The Carpentries Incubator, CC BY 4.0).

## Kondisi penggunaan

Gunakan saat meninjau perubahan (`git status`, `git diff`), menyusun pesan commit, menyiapkan PR/code review, atau memeriksa kompatibilitas GitHub Actions sebelum push.

## Workflow

1. **Periksa ruang lingkup perubahan**: Jalankan `git status` dan `git diff` untuk memastikan hanya file yang relevan yang berubah dan tidak ada artefak sementara.
2. **Audit privasi sebelum commit**:
   - Pastikan folder `samsunghealth_*/`, `data_audit/`, dataset pribadi, `.env`, dan kredensial tidak masuk staging.
   - Jangan pernah commit jika ada risiko kebocoran data kesehatan pribadi.
3. **Gunakan pesan commit yang deskriptif**: Ikuti format ringkas seperti `feat:`, `fix:`, `refactor:`, `test:`, `docs:`, atau `chore:` yang menjelaskan *apa* dan *mengapa*.
4. **Tinjau kualitas & CI**: Pastikan `ruff check` dan `pytest` lulus secara lokal serta alur GitHub Actions tidak bergantung pada dataset pribadi.
5. **Sinkronisasi aman**: Push ke branch yang sesuai tanpa `--force` dan tanpa menimpa riwayat remote.

## Aturan validasi

- `git status` bersih dari file sensitif atau sementara yang tidak diinginkan.
- Pesan commit jelas dan sesuai perubahan aktual.
- Seluruh pemeriksaan lint dan test terverifikasi sebelum push.

## Output yang diharapkan

Riwayat Git yang bersih, aman dari kebocoran data, terdokumentasi jelas, dan selaras dengan pengecekan CI.
