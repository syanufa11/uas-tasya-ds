# uas-tasya-ds — Analisis Data Tidur Samsung Health

Proyek Data Science tingkat S2 untuk audit, pembersihan, analisis pola dan konsistensi tidur, serta visualisasi dashboard berbasis ekspor data pribadi Samsung Health menggunakan kerangka kerja **CRISP-DM** (*Business Understanding, Data Understanding, Data Preparation, Modeling, Evaluation, Deployment*).

---

## 1. Tujuan Project

- Melakukan audit *read-only* terhadap struktur, skema, tipe data, kelengkapan, dan rentang waktu pada ekspor mentah Samsung Health.
- Menyiapkan alur pembersihan dan transformasi data yang *reproducible* tanpa mengubah data mentah dan tanpa *data leakage* pada data temporal.
- Menganalisis pola durasi, waktu tidur/bangun, serta konsistensi tidur (termasuk perbandingan hari kerja dan akhir pekan).
- Menyediakan dashboard interaktif berbasis Streamlit untuk eksplorasi metrik kualitas data, pola tidur, dan metodologi penelitian (saat ini menggunakan data demo sintetis yang aman untuk publikasi).

---

## 2. Sumber Data dan Keterbatasannya

- **Sumber data utama**: Ekspor lokal Samsung Health (`samsunghealth_*/`) yang disimpan secara privat di komputer lokal dan **tidak** diunggah ke GitHub.
- **Data demo dashboard**: Saat ini `dashboard/common.py` menyediakan generator data sintetis (`synthetic_sleep()` dan `synthetic_quality()`) dengan penanda eksplisit bahwa data tersebut adalah **demo sintetis**, bukan data Samsung Health asli.
- **Keterbatasan data**:
  - Ekspor Samsung Health bersifat personal (*single-subject*), sehingga hasilnya tidak dapat digeneralisasikan ke populasi luas.
  - Skema ekspor Samsung Health memiliki *preamble* khusus (`com.samsung.*`), format waktu campuran (epoch ms/detik maupun string ISO), serta potensi *missing values*, sesi tumpang-tindih (*overlapping*), atau inkonsistensi zona waktu.
  - Variabel seperti *sleep score*, *sleep stage*, atau *sleep efficiency* tidak selalu tersedia di semua perangkat/ekspor dan tidak diasumsikan ada sebelum diverifikasi melalui audit.
  - Data mentah tidak disertakan di repositori demi menjaga privasi.

---

## 3. Struktur Project

```text
uas-tasya-ds/
├── .github/
│   ├── copilot-instructions.md     # Pedoman proyek (CRISP-DM, privasi, reproduktibilitas)
│   ├── instructions/               # Aturan spesifik Python, notebook, Streamlit, laporan
│   ├── skills/                     # AI Skills modular per tahap CRISP-DM
│   └── workflows/
│       └── ci.yml                  # GitHub Actions CI (lint, pytest, validasi Streamlit, privasi)
├── .streamlit/
│   └── config.toml                 # Konfigurasi tema & browser Streamlit (root)
├── dashboard/
│   ├── .streamlit/config.toml      # Konfigurasi tema Streamlit (lokal dashboard)
│   ├── views/
│   │   ├── overview.py             # Halaman ringkasan metrik utama
│   │   ├── patterns.py             # Halaman pola tidur
│   │   ├── consistency.py          # Halaman konsistensi tidur
│   │   ├── quality.py              # Halaman kualitas data
│   │   └── methodology.py          # Halaman metodologi & keterbatasan
│   ├── app.py                      # Entrypoint aplikasi Streamlit
│   ├── common.py                   # Helper UI & generator data demo sintetis
│   └── requirements.txt            # Dependensi Python untuk dashboard
├── docs/
│   └── deployment.md               # Panduan CI/CD, testing, & Streamlit Community Cloud
├── scripts/
│   ├── audit_samsung_health.py     # Skrip audit lokal read-only (output ke data_audit/)
│   └── check_privacy.py            # Pemeriksaan file sensitif & kredensial pada Git
├── tests/
│   ├── test_dashboard.py           # Pengujian unit & smoke test dashboard
│   └── test_privacy.py             # Pengujian guard privasi repositori
├── .gitignore                      # Aturan pengecualian data privat & artefak lokal
├── pyproject.toml                  # Konfigurasi Ruff dan pytest
├── README.md                       # Dokumentasi utama project
├── requirements.txt                # Dependensi utama (kompatibel Streamlit Cloud)
└── skills-lock.json                # Metadata kunci skills
```

> **Catatan direktori lokal (diabaikan oleh Git):**
> `samsunghealth_*/` (ekspor mentah), `data_audit/` (hasil audit privat), serta direktori `data/`, `data_raw/`, `data_clean/`, `data_processed/`, `outputs/`, dan `artifacts/` hanya ada secara lokal dan tidak dilacak oleh Git.

---

## 4. Teknologi

- **Bahasa**: Python 3.x
- **Dashboard & Visualisasi**: Streamlit (`>=1.36`), Altair
- **Pengolahan Data**: pandas, NumPy
- **Kerangka Kerja & Dokumentasi**: CRISP-DM, Git, Markdown

---

## 5. Cara Instalasi

1. **Clone repositori:**
   ```bash
   git clone <url-repositori>
   cd uas-tasya-ds
   ```

2. **Buat dan aktifkan virtual environment (disarankan):**
   ```bash
   python -m venv .venv
   # Windows (PowerShell):
   .venv\Scripts\Activate.ps1
   # Linux/macOS:
   source .venv/bin/activate
   ```

3. **Instal dependensi dashboard:**
   ```bash
   pip install -r dashboard/requirements.txt
   ```

---

## 6. Cara Menjalankan Dashboard

Jalankan perintah berikut dari root proyek:

```bash
streamlit run dashboard/app.py
```

Dashboard akan terbuka di browser (default `http://localhost:8501`) dan menampilkan lima halaman navigasi: *Overview*, *Sleep Patterns*, *Sleep Consistency*, *Data Quality*, dan *Methodology* menggunakan data demo sintetis.

---

## 7. Cara Menjalankan Pengujian

Jalankan pemeriksaan berikut dari root proyek (tidak memerlukan data Samsung Health pribadi):

- **Pemeriksaan sintaks Python:**
  ```bash
  python -m compileall -q dashboard scripts tests
  ```
- **Lint dengan Ruff:**
  ```bash
  ruff check dashboard tests scripts/check_privacy.py
  ```
- **Unit test dan smoke test (`pytest`):**
  ```bash
  pytest -v
  ```
- **Pemeriksaan privasi & file sensitif sebelum commit:**
  ```bash
  python scripts/check_privacy.py
  ```
- **Menjalankan audit data lokal (hanya jika folder `samsunghealth_*` tersedia secara lokal):**
  ```bash
  python scripts/audit_samsung_health.py
  ```

---

## 8. CI/CD dan Deployment (Streamlit Community Cloud)

- **CI otomatis:** Workflow `.github/workflows/ci.yml` berjalan pada setiap `push` ke `main`, `pull_request` ke `main`, serta `workflow_dispatch` untuk menjalankan pemeriksaan sintaks, Ruff, `pytest`, validasi konfigurasi/import Streamlit, dan guard privasi.
- **Free Hosting:** Target deployment menggunakan **Streamlit Community Cloud** (`https://share.streamlit.io/`) dengan branch `main` dan entrypoint `dashboard/app.py` (mode demo sintetis, tanpa dataset pribadi).
- Panduan lengkap arsitektur CI/CD, langkah deployment, pembaruan dashboard, dan troubleshooting tersedia di [docs/deployment.md](docs/deployment.md).

---

## 9. Kebijakan Privasi

Proyek ini menerapkan prinsip *privacy-by-design*:

1. **Data mentah tetap lokal:** Folder ekspor `samsunghealth_*/` bersifat *read-only*, tidak dimodifikasi, dan dikecualikan melalui `.gitignore`.
2. **Audit dan hasil olahan bersifat privat:** Seluruh isi `data_audit/`, dataset mentah, maupun dataset hasil *cleaning* tidak pernah di-commit ke Git atau diunggah ke layanan eksternal.
3. **Pemisahan CSV demo sintetis:** `.gitignore` tidak memblokir `*.csv` secara global agar dataset sintetis yang aman untuk demo tetap dapat dikelola di repositori jika diperlukan, sementara seluruh folder data nyata dan file berpola identitas/kesehatan tetap diblokir.
4. **Tanpa kredensial atau PII di repositori:** File `.env`, kunci privat, token, serta informasi identitas pribadi (PII) dan kesehatan dilarang masuk ke riwayat Git, log, maupun laporan publik.

---

## 9. Atribusi & Lisensi Referensi

Praktik pengembangan perangkat lunak Python pada AI Skills (`.github/skills/python-*`) diadaptasi dari materi **Intermediate Research Software Development Skills (Python)** oleh [The Carpentries Incubator](https://github.com/carpentries-incubator/python-intermediate-development):

- Materi instruksional diadaptasi di bawah lisensi **Creative Commons Attribution 4.0 International (CC BY 4.0)**.
- Contoh kode program mengikuti lisensi **MIT**.
