"""Private EDA artefacts. Never load these outputs into the public dashboard."""

from __future__ import annotations

import json
import platform
from importlib.metadata import version
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from .readiness import NUMERIC, TARGET, audit_candidate, load_candidate, source_hash  # noqa: E402


def write_diagnostics(source: Path, output: Path, report: Path) -> dict:
    """Create local-only EDA and a report from the same audited input."""
    frame = load_candidate(source)
    audit = audit_candidate(frame)
    output.mkdir(parents=True, exist_ok=True)
    report.parent.mkdir(parents=True, exist_ok=True)
    audit["source_sha256"] = source_hash(source)
    audit["versions"] = {"python": platform.python_version(), **{
        package: version(package)
        for package in ("pandas", "numpy", "scikit-learn", "matplotlib", "nbformat", "nbclient")
    }}
    (output / "audit.json").write_text(
        json.dumps(audit, indent=2, ensure_ascii=False, allow_nan=False), encoding="utf-8"
    )
    corr = frame[NUMERIC].corr()
    corr.to_csv(output / "descriptive_correlations.csv")
    by_day = frame.groupby("day_of_week")[NUMERIC[:3]].agg(["count", "mean", "median"])
    by_day.to_csv(output / "day_patterns.csv")
    figures = []

    fig, ax = plt.subplots(figsize=(8, 4), layout="constrained")
    frame[TARGET].dropna().plot.hist(bins=20, ax=ax)
    ax.set(xlabel="Durasi tersimpan (menit)", ylabel="Jumlah observasi",
           title="Distribusi tidur kandidat — privat")
    figures.append((fig, "sleep_distribution.png"))

    fig, axes = plt.subplots(1, 2, figsize=(10, 4), layout="constrained")
    for ax, col, label in zip(axes, NUMERIC[1:3], ["Langkah", "Menit aktif kandidat"], strict=True):
        frame[col].plot.hist(bins=20, ax=ax)
        ax.set(xlabel=label, ylabel="Jumlah hari", title="Distribusi aktivitas — privat")
    figures.append((fig, "activity_distribution.png"))

    fig, axes = plt.subplots(1, 3, figsize=(12, 4), layout="constrained")
    for ax, col in zip(axes, NUMERIC[:3], strict=True):
        frame.groupby("day_of_week")[col].mean().plot.bar(ax=ax)
        ax.set(title=col, xlabel="Senin=0 … Minggu=6", ylabel="Rata-rata kandidat")
    figures.append((fig, "day_patterns.png"))

    fig, ax = plt.subplots(figsize=(8, 6), layout="constrained")
    heat = ax.imshow(corr, vmin=-1, vmax=1, cmap="coolwarm")
    labels = ["Tidur", "Langkah", "Aktif", "Hari", "Weekend"]
    ax.set_xticks(range(len(labels)), labels, rotation=30, ha="right")
    ax.set_yticks(range(len(labels)), labels)
    for i in range(len(labels)):
        for j in range(len(labels)):
            ax.text(j, i, f"{corr.iloc[i, j]:.2f}", ha="center", va="center")
    ax.set_title("Korelasi deskriptif tanggal sama; bukan prediksi atau kausalitas")
    fig.colorbar(heat, ax=ax, label="Pearson r, pairwise complete")
    figures.append((fig, "correlations.png"))

    fig, ax = plt.subplots(figsize=(10, 5), layout="constrained")
    frame.isna().mean().mul(100).sort_values().plot.barh(ax=ax)
    ax.set(xlabel="Missing (%)", title="Kelengkapan data — privat")
    figures.append((fig, "missing_values.png"))
    for fig, name in figures:
        fig.savefig(output / name, dpi=130)
        plt.close(fig)

    summary = frame[NUMERIC[:3]].describe().round(3).to_string()
    outliers = json.dumps(audit["iqr_outlier_counts"], ensure_ascii=False)
    sleep_day_means = frame.groupby("day_of_week")[TARGET].mean()
    observations = (
        f"Rata-rata durasi tersimpan {frame[TARGET].mean():.2f} menit; "
        f"median {frame[TARGET].median():.2f} menit. "
        f"Rata-rata menurut hari terendah pada indeks {sleep_day_means.idxmin()} "
        f"({sleep_day_means.min():.2f} menit), tertinggi pada indeks "
        f"{sleep_day_means.idxmax()} ({sleep_day_means.max():.2f} menit), Senin=0. "
        f"Pearson tidur–langkah tanggal sama r={corr.loc[TARGET, 'step_count']:.4f}; "
        f"tidur–menit aktif r={corr.loc[TARGET, 'active_time_minutes']:.4f}. "
        "Keduanya asosiasi deskriptif lemah pada label kandidat. "
        f"Langkah dan menit aktif sangat berkorelasi "
        f"(r={corr.loc['step_count', 'active_time_minutes']:.4f}); "
        "redundansi ini harus dipertimbangkan saat menafsirkan importance. "
        "Sampel tidur per hari tidak sama dengan sampel aktivitas; missing dan "
        "perbedaan cakupan dapat membiaskan perbandingan.\n\n"
    )
    blocked_models = "\n".join(
        f"| {name} | Belum dilatih | — | — | — |"
        for name in ("DummyRegressor", "LinearRegression", "RandomForestRegressor")
    )
    report.write_text(
        "# Evaluasi Model Samsung Health — TASK 16\n\n"
        "**PRIVAT — lokal saja. Pelatihan ditunda karena masalah kritis.**\n\n"
        "## Data Understanding\n\n"
        f"CSV aktual: {audit['rows']} baris × {audit['columns']} kolom; "
        f"{len(audit['informative_columns'])} kolom informatif selain kunci. "
        f"Lima field sumber lengkap pada {audit['five_source_fields_complete']} baris. "
        f"Duplikasi baris/tanggal: {audit['duplicate_rows']}/{audit['duplicate_dates']}. "
        "Lima field bukan lima dimensi independen. cleaning_report.md tidak tersedia; "
        "rujukan cleaning terdapat pada dataset_integration_report.md dan modul integrasi.\n\n"
        + "\n".join(f"- {reason}" for reason in audit["blockers"])
        + "\n\nTipe data, missing per kolom, hash input, dan versi ada di audit.json. "
        "date dibaca eksplisit dd/mm/yyyy; timestamp wajib +07:00 dan dihitung di UTC.\n\n"
        "## Target dan aturan waktu\n\n"
        "Target yang direncanakan adalah sleep_duration_minutes untuk sesi berikutnya. "
        "date pada CSV adalah tanggal bangun Asia/Jakarta, bukan tanggal aktivitas "
        "sebelum tidur. Tidak dilakukan join tanggal bangun−1 atau shift baris bergap. "
        "Diagnostik retrospektif menggunakan D=tanggal UTC mulai tidur−1, lookup tanggal "
        "aktivitas D, dengan akhir D+1 00:00 UTC ≤ awal tidur. "
        f"Pasangan lengkap kandidat: {audit['retrospective_complete_pairs']}; "
        f"pelanggaran batas konservatif: {audit['candidate_boundary_violations']}. "
        "Ini tidak membuktikan ketersediaan fitur maupun validitas target prospektif.\n\n"
        "Fitur final belum ditetapkan. Kandidat: step_count, active_time_minutes, "
        "day_of_week dan is_weekend pada waktu prediksi; previous_sleep_duration "
        "dan previous_bedtime hanya dari sesi yang telah selesai sebelum waktu prediksi. "
        "Jam historis perlu representasi sin/cos. distance_km tidak tersedia karena "
        "satuan belum pasti. Akhir tidur, jam bangun, interval dan bedtime target "
        "dilarang menjadi input. Riwayat sesi lengkap diperlukan untuk mengatasi "
        "seleksi sesi terpanjang pada CSV harian.\n\n"
        "## EDA eksploratif\n\n" + observations + "```text\n" + summary + "\n```\n\n"
        f"Target hilang: {audit['missing'][TARGET]}; hari bernilai langkah nol: "
        f"{audit['zero_step_days']}. Missing target tidak diimputasi. "
        "Nol tidak membuktikan perangkat dipakai. Outlier aturan 1,5×IQR: "
        + outliers + ". Flag tidak dihapus otomatis dan bukan diagnosis.\n\n"
        "Distribusi, pola hari (count/mean/median), matriks korelasi dan grafik missing "
        "tersimpan di artifacts/task16/. Korelasi pairwise pada tanggal sama hanya "
        "deskriptif; kalender redundan dan missing dapat memengaruhi asosiasi. "
        "Tidak digunakan sebagai bukti aktivitas mendahului tidur atau sebab-akibat.\n\n"
        "## Modeling dan Evaluation\n\n"
        "Sampel efektif untuk pelatihan: **0 (tertahan validasi)**. "
        "Train=0, test=0; belum ada split atau tuning yang dijalankan.\n\n"
        "| Model | Status | MAE (menit) | RMSE (menit) | R² |\n"
        "| --- | --- | --- | --- | --- |\n" + blocked_models + "\n\n"
        "Tidak ada model terbaik. Spesifikasi Pipeline tersedia tetapi belum fit. "
        "Actual vs Predicted, residual, feature importance dan analisis kesalahan "
        "belum dapat dihitung. K-Means ditunda karena kontrak waktu dan satuan "
        "belum terverifikasi; tidak ada silhouette score.\n\n"
        "Setelah kontrak diperbaiki: rencanakan 80% awal train, 20% akhir test, "
        "purge label yang melintasi waktu prediksi split, dan expanding temporal "
        "validation pada train. TimeSeriesSplit hanya bila cakupan dan jarak waktu "
        "memadai; data bergap memerlukan fold tanggal. Tuning terbatas RF melalui "
        "max_depth={3,None}, min_samples_leaf={5,10}, n_estimators=200; pilih dengan "
        "MAE validasi, tanpa melihat test. MAE utama, RMSE dan R² pelengkap pada "
        "test identik. Jika semua kalah Dummy median, simpulkan tidak ada perbaikan. "
        "Permutation importance perlu kehati-hatian terhadap fitur berkorelasi.\n\n"
        "## Keterbatasan dan reproduksi\n\n"
        "Satu individu, missing target, cakupan awal/akhir parsial, bias pencatatan "
        "dan seleksi sesi menghalangi generalisasi populasi dan klaim klinis. "
        "Dashboard publik hanya menampilkan status metode tanpa membaca CSV privat. "
        "Jalankan notebook dari kernel bersih; output publik harus dikosongkan. "
        "Eksekusi lokal tidak memverifikasi Drive atau render Colab.\n",
        encoding="utf-8",
    )
    return audit
