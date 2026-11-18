# Panduan CI/CD dan Deployment Streamlit Community Cloud

Dokumen ini menjelaskan arsitektur *Continuous Integration / Continuous Deployment* (CI/CD), pengujian lokal, serta langkah deployment dashboard Streamlit untuk proyek **uas-tasya-ds** menggunakan layanan hosting gratis **Streamlit Community Cloud** (bukan GitHub Pages, karena GitHub Pages hanya mendukung konten statis dan tidak dapat menjalankan server Python/Streamlit).

---

## 1. Arsitektur CI/CD

```text
Push / PR ke branch main (atau workflow_dispatch)
        │
        ▼
GitHub Actions (.github/workflows/ci.yml)
  1. Checkout repository
  2. Setup Python 3.11 + cache pip
  3. Install dependensi (requirements.txt, pytest, ruff)
  4. Cek sintaks Python (compileall)
  5. Lint dengan Ruff
  6. Unit & smoke tests dengan pytest
  7. Validasi konfigurasi (.streamlit/config.toml) & AppTest
  8. Pemeriksaan file sensitif & kebocoran kredensial (scripts/check_privacy.py)
        │
        ▼ (setelah terhubung ke Streamlit Community Cloud)
Streamlit Community Cloud (https://share.streamlit.io/)
  - Menarik kode dari branch `main`
  - Menginstal dependensi dari `requirements.txt` / `dashboard/requirements.txt`
  - Menjalankan entrypoint `dashboard/app.py` dalam mode demo sintetis
```

Seluruh pipeline berjalan **tanpa** membutuhkan ekspor data Samsung Health pribadi.

---

## 2. Cara Menjalankan Aplikasi Secara Lokal

1. Pastikan Python 3.11 (atau versi kompatibel) telah terpasang.
2. Instal dependensi:
   ```bash
   pip install -r requirements.txt
   ```
3. Jalankan dashboard dari root repositori:
   ```bash
   streamlit run dashboard/app.py
   ```
4. Buka URL lokal yang tampil di terminal (default `http://localhost:8501`).

> **Catatan Mode Demo:** Dashboard menampilkan banner `DEMO SINTETIS` dan seluruh grafik berasal dari generator acak deterministik (`seed=42`) di `dashboard/common.py`, **bukan** hasil analisis data Samsung Health asli.

---

## 3. Cara Menjalankan Pengujian dan Pemeriksaan Lokal

Dari root repositori:

- **Pemeriksaan sintaks Python:**
  ```bash
  python -m compileall -q dashboard scripts tests
  ```
- **Lint (Ruff):**
  ```bash
  ruff check dashboard tests scripts/check_privacy.py
  ```
- **Pengujian unit dan smoke test (pytest):**
  ```bash
  pytest -v
  ```
- **Pemeriksaan privasi & file sensitif sebelum commit/push:**
  ```bash
  python scripts/check_privacy.py
  ```

---

## 4. Langkah Deployment ke Streamlit Community Cloud

> **Prasyarat:** Akun GitHub yang memiliki akses ke repositori `syanufa11/uas-tasya-ds` dan otorisasi Streamlit Community Cloud.

1. Buka dan login ke [https://share.streamlit.io/](https://share.streamlit.io/).
2. Hubungkan (*connect*) akun GitHub Anda jika belum terhubung, dan berikan izin akses ke repositori.
3. Klik **Create app** (atau **New app**), lalu pilih repository `syanufa11/uas-tasya-ds`.
4. Pilih branch **`main`**.
5. Tentukan **Main file path** (entrypoint): **`dashboard/app.py`**.
6. Klik **Deploy!** untuk melakukan deployment awal dan tunggu hingga proses build dependensi selesai.
7. Setelah aplikasi berstatus *Running*, buka URL publik yang diberikan oleh Streamlit Community Cloud dan verifikasi bahwa keenam halaman (*Overview*, *Sleep Analytics*, *Physical Activity*, *Sleep & Activity Relationship*, *Data Quality*, *Methodology*) tampil normal dengan banner **DEMO SINTETIS**.

---

## 5. Cara Memperbarui Dashboard Melalui GitHub

1. Lakukan perubahan pada kode di branch kerja lokal.
2. Jalankan pemeriksaan lokal (`ruff`, `pytest`, `scripts/check_privacy.py`).
3. Commit dan push perubahan ke branch `main` (atau buat Pull Request ke `main`).
4. GitHub Actions akan menjalankan workflow `.github/workflows/ci.yml` secara otomatis.
5. Setelah branch `main` diperbarui, Streamlit Community Cloud akan menarik perubahan terbaru dan melakukan *redeploy* otomatis.

---

## 6. Troubleshooting Dependency dan Deployment

- **`ModuleNotFoundError: No module named 'views'` atau `'common'`:**
  Pastikan entrypoint disetel ke `dashboard/app.py` dan `sys.path.insert(0, str(Path(__file__).parent))` tetap ada di `dashboard/app.py`.
- **Dependensi gagal terinstal di Streamlit Community Cloud:**
  Periksa apakah paket tercantum di `requirements.txt` (root) dan `dashboard/requirements.txt`, serta tidak ada paket khusus OS Windows yang ditambahkan.
- **Konfigurasi tema tidak terbaca:**
  Pastikan `.streamlit/config.toml` di root dan `dashboard/.streamlit/config.toml` berformat TOML yang valid.
- **Error `ImportError: DLL load failed` pada `pyarrow` di Windows lokal:**
  Pada sebagian sistem Windows dengan kebijakan *Application Control / Smart App Control*, file `.pyd` yang baru diunduh (misalnya `pyarrow/lib.pyd`) dapat diblokir oleh OS. Hal ini tidak memengaruhi runner Linux (`ubuntu-latest`) di GitHub Actions maupun Streamlit Community Cloud.

### Windows: pandas `offsets` atau PyArrow diblokir App Control

Pada environment lokal Python 3.11, pandas 3.1.1 dan PyArrow 26.0.1 gagal dimuat
dengan pesan `An Application Control policy has blocked this file`. Kombinasi
pandas 2.2.3 dan PyArrow 19.0.1 berhasil diimpor dan melewati lima pemeriksaan
dashboard, termasuk Streamlit AppTest. Hasil ini berlaku pada perangkat yang diuji;
penerimaan wheel tetap bergantung pada kebijakan Windows masing-masing perangkat.

Konfigurasi sekali saja dari root proyek: hentikan Streamlit dengan `Ctrl+C`, lalu
pasang dependensi Windows tanpa mengubah kebijakan keamanan:

```powershell
.\.venv\Scripts\python.exe -m pip install --only-binary=:all: -r requirements-windows.txt
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -c "import pandas, pyarrow; print(pandas.__version__, pyarrow.__version__)"
```

Setiap sesi, jalankan dashboard dengan interpreter environment yang sama:

```powershell
.\.venv\Scripts\python.exe -m streamlit run dashboard/app.py
```

Mulai ulang proses Streamlit setelah mengganti dependensi agar modul lama tidak
tetap tersimpan dalam memori. Jika wheel ini juga diblokir, periksa event 3077/3033
di Event Viewer > Applications and Services Logs > Microsoft > Windows >
CodeIntegrity > Operational dan gunakan proses persetujuan kebijakan perangkat.
Lihat [panduan event App Control dari Microsoft](https://learn.microsoft.com/en-us/windows/security/application-security/application-control/app-control-for-business/operations/event-id-explanations).

---

## 7. Kebijakan Privasi Dataset

1. **Tanpa data pribadi di GitHub dan hosting:** Folder ekspor `samsunghealth_*/`, `data_audit/`, serta dataset mentah maupun hasil *cleaning* dikecualikan melalui `.gitignore` dan diverifikasi oleh `scripts/check_privacy.py`.
2. **Data demo sintetis eksplisit:** Hosting publik hanya menjalankan generator data sintetis (`dashboard/common.py`) yang diberi label jelas sebagai demo sintetis, bukan data kesehatan pribadi.
3. **Tanpa kredensial di repositori:** File `.env`, `secrets.toml`, token, dan kunci privat dilarang masuk ke repositori.


## Pembaruan TASK 12

Dataset demo aktif ada di `src/samsung_health/dashboard_data.py`; dashboard tidak
membaca ekspor pribadi. Dependensi UI minimum Streamlit 1.67 dan Plotly 6.
Pilih tema melalui Settings > Appearance. Filter tersedia bersama pada sidebar.
Lihat [bukti QA dan keterbatasan TASK 12](task12-dashboard.md).
