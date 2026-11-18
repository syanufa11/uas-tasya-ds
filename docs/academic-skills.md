# Integrasi skill akademik TASK 10

## Audit dan pemilihan

Audit 18 November 2026 menemukan 15 skill di `.github/skills/` dan 3 di
`.agents/skills/`. `academic-report` sudah mengatur isi, CRISP-DM, keterlacakan
bukti, dan pemeriksaan template Word. Belum ada skill khusus authoring PPTX,
format DOCX, parafrase, atau penyederhanaan bahasa. Semua skill lama dipertahankan.

| Skill baru di `.github/skills/` | Aktivasi dan batas tanggung jawab |
| --- | --- |
| `pptx-presentation` | Pembuatan/penyuntingan slide dan file PPTX |
| `docx-academic-report` | Pembuatan/penyuntingan file Word; isi ilmiah memakai `academic-report` |
| `academic-paraphrasing` | Hanya penyuntingan teks sumber yang diminta |
| `clear-indonesian-writing` | Narasi akademik Indonesia formal tingkat S2 |

Copilot Instructions berisi routing singkat. Metadata tersedia saat discovery;
isi `SKILL.md` dimuat sesuai tugas, sedangkan `references/` hanya saat diperlukan.
Tidak ada salinan baru di `.agents/skills/` dan tidak ada perubahan `skills-lock.json`
karena empat skill ini ditulis khusus proyek, bukan instalasi paket upstream.
Routing sudah diperiksa melalui skenario di bawah; aktivasi otomatis pada sesi
Copilot yang sedang berjalan belum diuji dan bergantung dukungan versi klien.

| Permintaan | Skill yang relevan |
| --- | --- |
| Buat slide UAS dari hasil analisis | PPTX + bahasa; `academic-report` bila perlu menyusun pembahasan |
| Isi template laporan Word | DOCX + bahasa + `academic-report` untuk isi penelitian |
| Parafrase paragraf yang diberikan | Parafrase + bahasa, tanpa memuat skill format dokumen |
| Sederhanakan penjelasan metode | Bahasa; tanpa otomatis memparafrase atau mengubah klaim |
| Perbaiki kode pemrosesan | Skill Python yang relevan; empat skill baru tidak diperlukan |

## Referensi resmi, lisensi, dan kompatibilitas

Sumber ditinjau langsung; tidak ada teks, kode, helper, maupun aset upstream
yang disalin. Karena itu tidak ada paket pihak ketiga baru yang diretribusikan
sebagai bagian skill ini. Jika kelak menyalin implementasi, tinjau kembali lisensi
per file dan sertakan LICENSE, atribusi/NOTICE, serta penanda perubahan yang diwajibkan.

| Sumber yang diperiksa | Temuan dan keputusan |
| --- | --- |
| [Anthropic skills](https://github.com/anthropics/skills/tree/e4bb5d960d87126ff3b3a8af1a104b7db67560ba) | Skill DOCX/PPTX tersedia; [lisensi DOCX](https://github.com/anthropics/skills/blob/e4bb5d960d87126ff3b3a8af1a104b7db67560ba/skills/docx/LICENSE.txt) dan [PPTX](https://github.com/anthropics/skills/blob/e4bb5d960d87126ff3b3a8af1a104b7db67560ba/skills/pptx/LICENSE.txt) adalah Apache-2.0. |
| [DOCX upstream](https://github.com/anthropics/skills/blob/e4bb5d960d87126ff3b3a8af1a104b7db67560ba/skills/docx/SKILL.md) | Menggunakan Node `docx` dan helper OOXML; asumsi paket preinstalled tidak berlaku di semua lingkungan proyek. |
| [PPTX upstream](https://github.com/anthropics/skills/blob/e4bb5d960d87126ff3b3a8af1a104b7db67560ba/skills/pptx/SKILL.md) | Menggunakan `pptxgenjs`, Node, serta helper Python/shell. Tidak diimpor agar tidak menambah toolchain Node dan helper yang tidak diperlukan. |
| [OpenAI skills](https://github.com/openai/skills/tree/49f948faa9258a0c61caceaf225e179651397431) | README menandai katalog deprecated dan mengarahkan ke [OpenAI plugins](https://github.com/openai/plugins). Daftar `.curated` diperiksa: `doc` dan `slides` tidak tersedia pada snapshot ini. Lisensi bersifat per skill; tidak diasumsikan satu lisensi untuk seluruh katalog. |
| [GitHub Agent Skills](https://docs.github.com/en/copilot/concepts/customizations/agent-skills) | Mendukung `.github/skills/`, metadata YAML, dan pemuatan sesuai relevansi; dukungan IDE tergantung versi. |

Dipilih implementasi khusus Python agar sesuai proyek, ringan, dan tidak
membutuhkan akun/API eksternal. Skill penulisan hanya berupa instruksi, tanpa
dependensi runtime. Tidak ada jaminan skor similarity atau referensi otomatis.

Dependensi opsional dipisahkan dari requirements dashboard/Colab:

| Dependensi | Versi yang diuji | Lisensi | Fungsi |
| --- | --- | --- | --- |
| `python-docx` | 1.2.0 | MIT | Membuat, membaca, menyunting Word |
| `python-pptx` | 1.0.2 | MIT | Membuat, membaca, menyunting slide |
| `PyYAML` | 6.0.3 | MIT | Memvalidasi frontmatter skill |

Dependensi transitif yang diperiksa pada lingkungan uji: lxml 6.1.1
(BSD-3-Clause), typing-extensions 4.16.0 (PSF-2.0), Pillow 12.2.0 (MIT-CMU),
dan XlsxWriter 3.2.9 (BSD-2-Clause). Office/LibreOffice adalah
renderer terpisah, bukan dependensi runtime dashboard. Microsoft Office mengikuti
lisensi instalasi pengguna. Template kompleks, field dinamis Word, dan fitur
PowerPoint yang tidak didukung library harus diuji di aplikasi setelah editing.

## Setup dan penggunaan

Konfigurasi sekali pada lingkungan Python authoring yang dipilih:

```powershell
python -m pip install -r requirements-documents.txt
```

Tidak perlu instalasi ulang setiap sesi. Gunakan interpreter lingkungan tersebut
untuk pemeriksaan berikut (otomatis menghasilkan contoh sintetis saja):

```powershell
python scripts/validate_academic_skills.py
python scripts/smoke_academic_documents.py --output-dir artifacts/task10-smoke
```

Gunakan direktori baru setiap pengujian; smoke test menolak overwrite.
`artifacts/` sudah diabaikan Git. Script memeriksa create/edit/reopen, CRC ZIP,
XML, nilai tabel, persamaan Word, dan konsistensi ringkasan kedua format.
Script tidak otomatis menguji aplikasi Office atau kualitas visual.

Setiap dokumen final tetap perlu dibuka di Word/PowerPoint atau LibreOffice,
dirender, dan diperiksa seluruh halaman/slide. Pisahkan hasil pemeriksaan paket,
pembukaan aplikasi, dan QA visual. File uji sementara dihapus setelah inspeksi;
script reproduksi dipertahankan.

## Pemeriksaan TASK 10

- Validator: 22 skill (19 `.github` + 3 `.agents`), tanpa masalah metadata/link lokal.
- Smoke test: DOCX dan PPTX berhasil dibuat, disunting, dibuka ulang, serta lolos CRC/XML dan konsistensi isi.
- Word native: DOCX dibuka read-only dan diekspor ke PDF, 1 halaman.
- PowerPoint native: PPTX dibuka read-only dan diekspor ke PDF/PNG, 3 slide.
- QA visual: seluruh 1 halaman dan 3 slide diperiksa; tabel, glyph rumus,
  diagram, margin, serta teks terbaca tanpa clipping/overlap.
- Bahasa: contoh parafrase mempertahankan 30 pengamatan, r = 0,42, dan negasi
  kausalitas; contoh penyederhanaan menjelaskan MAE tanpa menambah hasil.
- Kualitas isi: kedua dokumen memakai 6, 7, 8 dan rata-rata 7; semuanya dilabeli sintetis.
- Ruff pada dua script baru: lulus. `quick_validate.py` resmi pada empat skill
  baru: seluruhnya valid.
- Regresi `python -m pytest -q` memakai Python sistem: 21 lulus, 1 gagal pada
  smoke dashboard karena Windows App Control memblokir DLL PyArrow; tetap
  terjadi di luar sandbox. Tidak ada kode dashboard yang diubah dalam TASK 10.
  Lingkungan `.venv` memiliki PyArrow 19.0.1 yang dapat diimpor, tetapi belum
  memiliki pytest; suite ini tidak membuktikan status regresi lingkungan tersebut.
- Pemeriksaan privasi sebelum commit: lulus, 100 file terindeks diperiksa;
  `git diff --cached --check` juga lulus. File uji sementara telah dihapus.

Pengujian ini memvalidasi contoh sederhana. Template kampus yang kompleks dan
aktivasi skill dalam antarmuka Copilot belum diuji secara langsung.
