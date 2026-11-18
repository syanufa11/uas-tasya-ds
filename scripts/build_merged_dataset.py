"""Build a PRIVATE candidate daily Samsung Health CSV and validation report."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from verify_dataset_feasibility import fingerprint, read_entity  # noqa: E402

from samsung_health.merged import UNITS, build_daily, prior_activity_dates, validate_daily  # noqa: E402


def crosscheck_activity(raw: Path, activity: pd.DataFrame) -> dict:
    """Reconcile every referenced JSON; verify internal units without sensor claims."""
    paths: dict[str, list[Path]] = {}
    for path in raw.rglob("*.json"):
        paths.setdefault(path.name, []).append(path)
    units, hourly, utc_matches, local_matches = set(), 0, 0, 0
    step_errors, time_errors = [], []
    without_bins = 0
    for _, row in activity.iterrows():
        candidates = paths.get(str(row["extra_data"]), [])
        if len(candidates) != 1:
            raise ValueError("Missing or ambiguous activity JSON reference")
        obj = json.loads(candidates[0].read_text(encoding="utf-8-sig"))
        bins = obj.get("mUnitDataList", [])
        if not bins:
            without_bins += 1
            continue
        units.update(b["mTimeUnit"] for b in bins)
        steps = sum(b["walkStep"] + b["runStep"] for b in bins)
        active = sum(b["mWalkTime"] + b["mRunTime"] + b["mOthersTime"] for b in bins)
        step_errors.append(abs(float(row["step_count"]) - steps))
        time_errors.append(abs(float(row["active_time"]) - active))
        for hour in obj.get("hourlyDataList", []):
            stamp = pd.to_datetime(hour["startTime"], unit="ms", utc=True)
            day = pd.Timestamp(row["day_time"]).date()
            hourly += 1
            utc_matches += int(stamp.date() == day)
            local_matches += int(stamp.tz_convert("Asia/Jakarta").date() == day)
    if units != {600000} or max(step_errors) != 0 or max(time_errors) > 1:
        raise ValueError("Activity internal reconciliation failed; review units/schema")
    return {"json_files": len(activity), "without_bins_not_reconciled": without_bins,
            "mTimeUnit": sorted(units),
            "max_step_difference": max(step_errors), "max_active_time_difference": max(time_errors),
            "hourly_entries": hourly, "utc_date_matches": utc_matches,
            "jakarta_date_matches": local_matches}


def main() -> None:
    """Read original export without modification; publish outputs only in ignored paths."""
    roots = [p for p in ROOT.glob("samsunghealth_*") if p.is_dir()]
    if len(roots) != 1:
        raise ValueError("Expected exactly one local Samsung Health export directory")
    raw = roots[0]
    before = fingerprint(raw)
    sleep = read_entity(raw, "com.samsung.shealth.sleep")
    activity = read_entity(raw, "com.samsung.shealth.activity.day_summary")
    crosscheck = crosscheck_activity(raw, activity)
    frame, cleaning = build_daily(sleep, activity)
    validation = validate_daily(frame)
    starts = frame.sleep_start_local.dropna()
    dates = prior_activity_dates(starts)
    cutoff = pd.to_datetime(dates, utc=True) + pd.Timedelta(days=1)
    violations = int(cutoff.gt(pd.to_datetime(starts, utc=True)).sum())
    assert violations == 0
    assert validation["duplicate_dates"] == 0
    assert len(validation["informative_non_key_columns"]) >= 5
    assert before == fingerprint(raw), "Raw source files changed"
    evidence = {
        "status": "CANDIDATE: timezone/day boundary and activity units await confirmation",
        "pandas_version": pd.__version__, "python_version": sys.version.split()[0],
        "raw_files_hash_verified_unchanged": len(before),
        "input_rows": {"sleep": len(sleep), "activity": len(activity)},
        "cleaning": cleaning, "validation": validation,
        "activity_json_crosscheck": crosscheck,
        "source_periods": {
            "sleep_start_raw": [str(sleep["com.samsung.health.sleep.start_time"].min()),
                                str(sleep["com.samsung.health.sleep.start_time"].max())],
            "activity_day_labels": [str(activity.day_time.min()), str(activity.day_time.max())],
        },
        "numeric_ranges": {
            c: {"min": float(frame[c].min()), "max": float(frame[c].max())}
            for c in ["sleep_duration_minutes", "sleep_interval_minutes", "step_count",
                      "active_time_minutes", "bedtime_hour", "wake_hour"]
        },
        "temporal_boundary_violations_conservative_rule": violations,
        "column_units": UNITS,
        "source_schema": {
            name: {col: {"missing": int(df[col].isna().sum()),
                         "observed_dtype": str(df[col].dtype)} for col in columns}
            for name, df, columns in [
                ("sleep", sleep, ["com.samsung.health.sleep.start_time",
                                  "com.samsung.health.sleep.end_time",
                                  "com.samsung.health.sleep.time_offset", "sleep_duration"]),
                ("activity", activity, ["day_time", "step_count", "active_time"]),
            ]
        },
    }
    out = ROOT / "data_processed" / "samsung_health_merged.csv"
    out.parent.mkdir(exist_ok=True)
    export = frame.copy()
    export["date"] = export.date.dt.strftime("%d/%m/%Y")
    for col in ["step_count", "secondary_sleep_session_count", "day_of_week", "is_weekend"]:
        export[col] = export[col].astype("Int64")
    export.to_csv(out, index=False, encoding="utf-8", na_rep="", lineterminator="\n")
    reread = pd.read_csv(out, dtype={"date": str})
    pd.testing.assert_frame_equal(
        export.reset_index(drop=True).astype(object).where(export.notna(), float("nan")),
        reread.astype(object), check_dtype=False, check_exact=False,
    )
    assert pd.to_datetime(reread.date, format="%d/%m/%Y").equals(frame.date)
    (ROOT / "data_audit" / "task13_validation.json").write_text(
        json.dumps(evidence, indent=2, ensure_ascii=False), encoding="utf-8",
    )
    write_report(evidence)
    print("Private candidate CSV, report, and aggregate validation saved locally.")


def write_report(evidence: dict) -> None:
    """Generate the private academic report from actual aggregate validation."""
    v = evidence["validation"]
    lines = [
        "# Integrasi Dataset Samsung Health — TASK 13",
        "", "**PRIVAT, hanya lokal. Status: kandidat; belum siap untuk ML final.**", "",
        "## Data Understanding dan Data Preparation", "",
        "Sumber: CSV sleep dan activity.day_summary dari satu ekspor asli. Parser proyek "
        "menangani preamble, BOM UTF-8, header kedua, dan field terminal kosong; struktur "
        "malformed ditolak. Tidak ada imputasi, penggabungan seri langkah, atau perubahan raw.",
        "", "Sumber langkah alternatif step_daily_trend dan pedometer_day_summary mempunyai "
        "beberapa sumber per hari (audit TASK 01); keduanya tidak ditambahkan atau dijumlahkan. "
        "activity.day_summary menjadi satu-satunya sumber aktivitas dan langkah.",
        "", "## Aturan waktu, agregasi, dan join", "",
        "Zona keluaran Asia/Jakarta. Teks waktu tidur diasumsikan UTC lalu dikonversi sekali "
        "ke +07:00; offset seluruh sesi diperiksa. Snapshot epoch cache dalam audit mendukung "
        "asumsi ini, tetapi belum ada konfirmasi tampilan aplikasi untuk seluruh histori. "
        "day_time aktivitas dipertahankan sebagai label hari kandidat, tanpa pergeseran jam. "
        "Batas hari lokal aktivitas belum terverifikasi: join ini masih bersyarat.",
        "", "Unit: satu baris per tanggal kalender kontinu pada union cakupan sumber. "
        "Tidur diatribusikan ke tanggal bangun lokal. Kedua record pada overlap/interval "
        "identik dikarantina, bukan dijumlahkan atau dipilih sembarang. Dari sesi layak per "
        "tanggal, dipilih interval terpanjang; seri dipecahkan dengan awal UTC paling awal. "
        "Sesi lain dihitung sebagai sesi sekunder dan tidak dijumlahkan. Label sekunder tidak "
        "membuktikan tidur siang. Tidak ada klasifikasi nap fisiologis yang tersedia.",
        "", "Aktivitas harus unik per tanggal; duplikasi ditolak. Outer join one_to_one, lalu "
        "reindex kalender. Missing tetap kosong, termasuk durasi asli yang tidak tercatat. "
        "Nol aktivitas yang benar-benar ada pada sumber dipertahankan tanpa menyimpulkan "
        "ketidakaktifan. Tidak ada ID, UUID, profil, atau metadata identitas dalam CSV.",
        "", "Format date dd/mm/yyyy mengikuti arahan pengguna terbaru, menggantikan syarat "
        "ISO pada brief awal. Timestamp lengkap tetap ISO 8601 dengan +07:00. Baca date "
        "dengan format eksplisit %d/%m/%Y; jangan gunakan inferensi bulan/hari.",
        "", "## Kamus kolom", "",
        "sleep_start_local dan sleep_end_local berasal dari com.samsung.health.sleep.start_time "
        "dan end_time; sleep_duration_minutes dari sleep_duration asli. sleep_interval_minutes "
        "= (end-start)/60 detik, tidak mengisi durasi asli. step_count dan active_time berasal "
        "hanya dari activity.day_summary. active_time/60000 merupakan konversi menit empiris "
        "berdasarkan mTimeUnit=600000 serta rekonsiliasi JSON pada TASK 11A; bukan konfirmasi "
        "resmi satuan ekspor. distance_km tidak dimasukkan karena satuan jarak ekspor belum pasti.",
        "", "| Kolom | Satuan/definisi | Missing | Persen |", "| --- | --- | ---: | ---: |",
    ]
    for col, unit in UNITS.items():
        miss = v["missing"][col]
        lines.append(f"| {col} | {unit} | {miss['count']} | {miss['percent']:.4f}% |")
    lines.extend([
        "", "## Hasil validasi aktual", "",
        "Rekonsiliasi aktivitas dijalankan ulang pada setiap build. JSON tanpa bin tidak "
        "dianggap sebagai pengukuran nol dan tidak direkonstruksi; nilai ringkasan CSV "
        "tetap dipertahankan. Jumlah JSON tanpa bin dan selisih maksimum pada JSON yang "
        "memiliki bin dicatat dalam activity_json_crosscheck. Timestamp jam menunjukkan "
        "perbedaan kecocokan tanggal UTC versus Jakarta, sehingga batas hari aktivitas "
        "tetap dinyatakan belum final.", "",
        "```json", json.dumps(evidence, ensure_ascii=False, indent=2), "```", "",
        "## Kelayakan dan batas penggunaan", "",
        "Minimal lima kolom informatif terpenuhi secara struktur; lima field sumber adalah "
        "awal tidur, akhir tidur, durasi tersimpan, langkah, dan durasi aktif. Durasi interval, "
        "jam, serta kalender merupakan turunan dan tidak dihitung sebagai pengukuran independen. "
        "Awal, akhir, serta durasi saling berkaitan; lima field bukan lima dimensi independen.",
        "", "EDA eksploratif dapat dilakukan dengan label kandidat dan pemeriksaan missing. "
        "Regresi dan clustering final belum layak sebelum konfirmasi waktu/batas hari dan "
        "satuan aktivitas. Data berasal dari satu individu dan tidak mendukung generalisasi "
        "populasi atau klaim klinis. Interval tercatat tidak membuktikan durasi tidur fisiologis. "
        "Stage, skor tidur, dan efisiensi tidak tersedia secara valid. Rentang awal/akhir ekspor "
        "dan hari terbaru dapat parsial. Nilai nol tidak membuktikan perangkat dipakai seharian.",
        "", "Join tanggal sama hanya untuk deskripsi, bukan bukti aktivitas mendahului tidur. "
        "Untuk asosiasi retrospektif gunakan prior_activity_dates: D=tanggal UTC mulai tidur-1; "
        "akhir konservatif D+1 00:00 UTC harus <= mulai tidur. Ambil aktivitas lewat lookup "
        "tanggal D dengan validate one_to_one/many_to_one, bukan shift baris subset berlubang. "
        "Jangan memakai tanggal bangun-1 secara otomatis. Pemilihan sesi terpanjang bersifat "
        "retrospektif. Prediksi memerlukan definisi target sebelum pengamatan, verifikasi "
        "ketersediaan fitur, split kronologis dan preprocessing hanya pada data latih. "
        "Jangan memasukkan akhir/jam bangun/durasi interval target untuk memprediksi durasinya. "
        "Clustering memerlukan scaling, representasi sin/cos jam, seleksi fitur redundan, "
        "dan evaluasi stabilitas; belum ada model atau metrik performa yang dijalankan.",
        "", "## Reproduksi dan privasi", "",
        "```powershell", "python scripts/build_merged_dataset.py",
        "python -m pytest -q", "python -m ruff check src/samsung_health/merged.py "
        "scripts/build_merged_dataset.py tests/test_merged_dataset.py", "```", "",
        "CSV UTF-8 tanpa BOM, separator koma; hanya satu CSV utama di data_processed/. "
        "JSON diagnostik di data_audit/task13_validation.json. Laporan ini juga diabaikan Git "
        "karena berisi statistik kesehatan. Dokumentasi publik hanya memuat metode. "
        "Dashboard demo tetap sintetis; tidak dihubungkan ke CSV privat. Tidak ada push "
        "selama masalah validasi kritis belum selesai.",
    ])
    (ROOT / "reports" / "dataset_integration_report.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8",
    )


if __name__ == "__main__":
    main()
