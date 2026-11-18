"""Build and verify the local proposal through Microsoft PowerPoint automation."""

import csv
import json
import os
import re
from pathlib import Path
from xml.etree import ElementTree
from zipfile import ZipFile

import win32com.client

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "presentations"
QA = ROOT / "artifacts" / "task11-qa"
TITLE = (
    "Analisis Pola dan Keteraturan Tidur Berdasarkan Data Historis "
    "Samsung Health Menggunakan Pendekatan Data Science"
)
NAVY, INDIGO, CYAN = "101C36", "818CF8", "56D9EA"
WHITE, MUTED = "F4F7FC", "BCCAE0"

NARRATIVES = [
    "Pemahaman pola dan keteraturan tidur dapat membantu evaluasi rutinitas pribadi. "
    "Namun, ingatan sehari-hari sulit memberikan gambaran objektif mengenai perubahan "
    "durasi maupun jadwal tidur. Proposal ini memanfaatkan riwayat pencatatan Samsung "
    "Health untuk menelaah kebiasaan tersebut secara sistematis. Masalah utamanya adalah "
    "belum tersedianya gambaran berbasis data mengenai durasi, jadwal, dan konsistensi "
    "tidur yang tercatat. Penelitian berfokus pada satu individu dan menggunakan "
    "pendekatan deskriptif. Temuannya akan menjadi bahan refleksi pribadi, bukan "
    "diagnosis medis atau ukuran kualitas tidur fisiologis.",
    "Penelitian ini memiliki tiga tujuan. Pertama, memetakan durasi dan jadwal tidur "
    "untuk menjawab bagaimana pola durasi dalam riwayat pencatatan. Kedua, menelaah "
    "keteraturan dari waktu ke waktu untuk mengetahui konsistensi jadwal mulai dan "
    "selesai tidur. Ketiga, membandingkan hari kerja dan akhir pekan apabila cakupan "
    "datanya memadai. Pengelompokan tersebut perlu memperhatikan kalender karena "
    "akhir pekan belum tentu sama dengan hari libur aktual. Hasil yang diharapkan "
    "adalah gambaran kebiasaan tidur berbasis data sebagai dasar evaluasi pribadi "
    "secara nonmedis. Seluruh poin ini merupakan rencana, belum hasil penelitian.",
    "Data berasal dari ekspor pribadi Samsung Health dalam format CSV dan JSON. "
    "Tabel utama com.samsung.shealth.sleep memuat 653 catatan sesi dengan rentang "
    "timestamp ekspor 1 Februari 2025 hingga 17 November 2026. Rentang ini belum "
    "menyatakan tanggal lokal final. Variabel utama mencakup waktu mulai, waktu "
    "selesai, dan durasi bila tersedia. Alurnya meliputi ekspor, identifikasi file "
    "tidur, parsing, audit kualitas, cleaning, kemudian analisis. Audit sudah tersedia, "
    "sedangkan laporan cleaning belum ditemukan. Validasi zona waktu, nilai kosong, "
    "dan sesi tumpang-tindih perlu diselesaikan sebelum analisis.",
]


def color(value):
    """Convert RGB hex to the integer used by Office automation."""
    r, g, b = (int(value[i : i + 2], 16) for i in (0, 2, 4))
    return r + 256 * g + 65536 * b


def text(slide, content, x, y, w, h, size=20, ink=WHITE, bold=False):
    """Add a native, editable text box with fixed margins and no autofit."""
    box = slide.Shapes.AddTextbox(1, x, y, w, h)
    frame = box.TextFrame2
    frame.MarginLeft = frame.MarginRight = 0
    frame.MarginTop = frame.MarginBottom = 0
    frame.WordWrap = -1
    frame.AutoSize = 0
    frame.TextRange.Text = content
    frame.TextRange.Font.Name = "Aptos"
    frame.TextRange.Font.Size = size
    frame.TextRange.Font.Bold = -1 if bold else 0
    frame.TextRange.Font.Fill.ForeColor.RGB = color(ink)
    frame.TextRange.ParagraphFormat.SpaceAfter = 0
    box.Width, box.Height = w, h
    return box


def base(deck, number, section):
    slide = deck.Slides.Add(number, 12)
    slide.FollowMasterBackground = 0
    slide.Background.Fill.ForeColor.RGB = color(NAVY)
    text(slide, section, 44, 25, 820, 22, 12, CYAN, True)
    text(slide, f"{number:02d}", 886, 25, 30, 22, 12, MUTED)
    return slide


def add_flow(slide):
    labels = [
        "Ekspor",
        "Identifikasi\nfile tidur",
        "Parsing",
        "Audit\nkualitas",
        "Cleaning",
        "Analisis",
    ]
    for i, label in enumerate(labels):
        x = 44 + i * 147
        shape = slide.Shapes.AddShape(1, x, 335, 132, 59)
        shape.Fill.ForeColor.RGB = color("27375C" if i < 4 else "1B2946")
        shape.Line.ForeColor.RGB = color(CYAN if i < 4 else INDIGO)
        shape.Line.Weight = 1
        box = text(slide, label, x + 5, 346, 122, 42, 16, WHITE, True)
        box.TextFrame2.TextRange.ParagraphFormat.Alignment = 2
        if i < 5:
            line = slide.Shapes.AddConnector(1, x + 134, 364, x + 145, 364)
            line.Line.ForeColor.RGB = color(CYAN)
            line.Line.EndArrowheadStyle = 3
    text(
        slide,
        "Audit tersedia; cleaning dan analisis merupakan tahap lanjutan",
        44,
        404,
        872,
        28,
        15,
        MUTED,
    )


def verify_sources():
    csv.field_size_limit(100_000_000)
    with (ROOT / "data_audit/inventory.csv").open(encoding="utf-8-sig", newline="") as stream:
        entries = list(csv.DictReader(stream))
    sleep = [r for r in entries if r["relative_path"].startswith("com.samsung.shealth.sleep.")]
    assert len(sleep) == 1 and int(sleep[0]["row_count"]) == 653
    report = (ROOT / "data_audit/audit_report.md").read_text(encoding="utf-8-sig")
    assert "2025-02-01 19:50:00" in report and "2026-11-17 23:20:00" in report
    assert not (ROOT / "reports/cleaning_report.md").exists()


def main():
    verify_sources()
    OUT.mkdir(exist_ok=True)
    QA.mkdir(parents=True, exist_ok=True)
    target = OUT / "Proposal_UAS_Data_Science.pptx"
    if target.exists():
        raise FileExistsError(target)
    app = win32com.client.DispatchEx("PowerPoint.Application")
    app.Visible = True
    deck = app.Presentations.Add(0)
    deck.PageSetup.SlideWidth, deck.PageSetup.SlideHeight = 960, 540
    try:
        slide = base(deck, 1, "BUSINESS UNDERSTANDING / LATAR BELAKANG")
        text(slide, TITLE, 44, 69, 872, 138, 28, WHITE, True)
        text(
            slide, "Pemahaman pola tidur membantu evaluasi rutinitas pribadi.", 44, 237, 872, 32, 21
        )
        text(
            slide,
            "Evaluasi berbasis ingatan sulit menangkap perubahan kebiasaan.",
            44,
            282,
            872,
            32,
            21,
        )
        text(
            slide,
            "Riwayat Samsung Health memberi dasar pencatatan untuk analisis.",
            44,
            327,
            872,
            32,
            21,
        )
        text(slide, "PERNYATAAN MASALAH", 44, 393, 872, 23, 13, CYAN, True)
        text(
            slide,
            (
                "Belum tersedia gambaran objektif tentang durasi, jadwal, dan\nkonsisten"
                "si tidur berdasarkan riwayat pencatatan pribadi."
            ),
            44,
            424,
            872,
            60,
            21,
            WHITE,
            True,
        )
        text(
            slide,
            "Ruang lingkup: pola tidur satu individu, tanpa diagnosis medis",
            44,
            503,
            872,
            22,
            14,
            MUTED,
        )

        slide = base(deck, 2, "BUSINESS UNDERSTANDING / TUJUAN DAN MANFAAT")
        text(slide, "Tujuan dan pertanyaan penelitian", 44, 68, 872, 48, 32, WHITE, True)
        text(slide, "TUJUAN", 44, 141, 406, 24, 14, CYAN, True)
        text(slide, "PERTANYAAN PENELITIAN", 500, 141, 416, 24, 14, INDIGO, True)
        rows = [
            (
                "01  Memetakan durasi dan\n      jadwal tidur",
                "Bagaimana pola durasi tidur\ndalam riwayat pencatatan?",
            ),
            (
                "02  Menelaah keteraturan tidur\n      dari waktu ke waktu",
                "Seberapa konsisten jadwal\ntidur yang tercatat?",
            ),
            (
                "03  Membandingkan hari kerja\n      dan akhir pekan*",
                "Apakah pola tidur berbeda antara\nhari kerja dan akhir pekan?",
            ),
        ]
        for i, (objective, question) in enumerate(rows):
            y = 183 + i * 86
            text(slide, objective, 44, y, 420, 66, 21)
            text(slide, question, 500, y, 416, 66, 21)
        text(slide, "MANFAAT", 44, 449, 150, 24, 13, CYAN, True)
        text(
            slide,
            "Gambaran kebiasaan berbasis data untuk evaluasi pribadi secara nonmedis.",
            44,
            475,
            872,
            29,
            18,
        )
        text(
            slide, "*Perbandingan dilakukan jika cakupan data memadai.", 44, 513, 872, 20, 13, MUTED
        )

        slide = base(deck, 3, "DATA ACQUISITION / SUMBER DAN ALUR DATA")
        text(slide, "Data historis Samsung Health", 44, 68, 872, 48, 32, WHITE, True)
        text(slide, "Ekspor data pribadi dalam CSV dan JSON", 44, 133, 872, 30, 22)
        text(slide, "Dataset utama: com.samsung.shealth.sleep", 44, 168, 872, 28, 20, MUTED)
        text(slide, "653", 44, 215, 142, 68, 46, CYAN, True)
        text(slide, "catatan sesi tidur", 188, 219, 320, 31, 22, WHITE, True)
        text(slide, "1 Februari 2025–17 November 2026", 188, 252, 718, 29, 21)
        text(
            slide,
            "Rentang timestamp ekspor; zona waktu lokal belum final",
            188,
            285,
            718,
            24,
            15,
            MUTED,
        )
        add_flow(slide)
        text(
            slide,
            "Variabel: waktu mulai, waktu selesai, durasi bila tersedia",
            44,
            446,
            872,
            28,
            20,
        )
        text(
            slide,
            "Perlu validasi: zona waktu, missing values, dan sesi overlap",
            44,
            487,
            872,
            28,
            19,
            CYAN,
        )

        refs = [
            (
                "Sumber: brief TASK 11; README.md; data_audit/audit_report.md bagian 6A"
                ". Batas: data satu individu dan pencatatan, bukan pengukuran fisiologi"
                "s tervalidasi."
            ),
            (
                "Sumber: brief TASK 11; data_audit/audit_report.md bagian 4 dan 6A. Har"
                "i kerja/akhir pekan memerlukan definisi kalender dan kecukupan cakupan"
                "."
            ),
            (
                "Sumber: data_audit/audit_report.md bagian 2, 3, 5, 7, 8; data_audit/in"
                "ventory.csv; data_audit/sleep_data_dictionary.csv. Waktu awal dan akhi"
                "r lengkap pada 653 baris; sleep_duration terisi pada 422 baris. Tidak "
                "memasukkan nilai sesi individual. reports/cleaning_report.md belum ter"
                "sedia saat penyusunan."
            ),
        ]
        for i in range(1, 4):
            deck.Slides(i).NotesPage.Shapes.Placeholders(2).TextFrame.TextRange.Text = (
                NARRATIVES[i - 1] + "\n\n" + refs[i - 1]
            )
        for key in ("Author", "Last Author", "Company", "Manager", "Comments"):
            try:
                deck.BuiltInDocumentProperties(key).Value = ""
            except Exception:
                pass
        deck.SaveAs(str(target), 24)
        deck.Close()
        deck = app.Presentations.Open(str(target), -1, 0, 0)
        assert deck.Slides.Count == 3
        fits = []
        for slide in deck.Slides:
            for shape in slide.Shapes:
                if shape.HasTextFrame and shape.TextFrame2.HasText:
                    tr = shape.TextFrame2.TextRange
                    fits.append(
                        {
                            "slide": slide.SlideIndex,
                            "text": tr.Text[:50],
                            "height": round(tr.BoundHeight, 2),
                            "box_height": round(shape.Height, 2),
                        }
                    )
                    assert tr.BoundHeight <= shape.Height + 2, fits[-1]
                    assert tr.BoundWidth <= shape.Width + 2, fits[-1]
            slide.Export(str(QA / f"slide-{slide.SlideIndex}.png"), "PNG", 1600, 900)
        (QA / "text-fit.json").write_text(json.dumps(fits, indent=2), encoding="utf-8")
    finally:
        deck.Close()
        app.Quit()
    # Office replaces lastModifiedBy at save time; clear personal metadata afterward.
    sanitized = QA / "sanitized.pptx"
    with ZipFile(target) as source, ZipFile(sanitized, "w") as clean:
        for entry in source.infolist():
            data = source.read(entry.filename)
            if entry.filename == "docProps/core.xml":
                # Preserve namespace declarations used inside xsi:type values.
                data = re.sub(
                    rb"(<(?:dc:creator|cp:lastModifiedBy)>).*?"
                    rb"(</(?:dc:creator|cp:lastModifiedBy)>)",
                    rb"\1\2",
                    data,
                )
            clean.writestr(entry, data)
    os.replace(sanitized, target)
    with ZipFile(target) as package:
        assert package.testzip() is None
        for name in package.namelist():
            if name.endswith((".xml", ".rels")):
                ElementTree.fromstring(package.read(name))
        assert (
            len(
                [
                    n
                    for n in package.namelist()
                    if n.startswith("ppt/slides/slide") and n.endswith(".xml")
                ]
            )
            == 3
        )
        assert not any(n.startswith("ppt/embeddings/") for n in package.namelist())
    notes = ["# Catatan presentasi proposal UAS Data Science", "", TITLE, ""]
    for i, narrative in enumerate(NARRATIVES, 1):
        notes.extend([f"## Slide {i} · sekitar 30–45 detik", "", narrative, ""])
    notes.extend(
        [
            "## Sumber dan status",
            "",
            (
                "Narasi mengacu pada brief TASK 11, README.md, data_audit/audit_report."
                "md, data_audit/inventory.csv, dan data_audit/sleep_data_dictionary.csv"
                ". Periode mengikuti timestamp teks ekspor, bukan tanggal lokal final. "
                "Laporan cleaning belum tersedia pada saat penyusunan. Proposal belum m"
                "enyajikan hasil analisis penelitian. Tidak ada catatan sesi individual"
                " atau identitas akun dalam slide."
            ),
            "",
        ]
    )
    (OUT / "catatan_presentasi.md").write_text("\n".join(notes), encoding="utf-8")
    print(
        json.dumps(
            {
                "slides": 3,
                "native_powerpoint_reopen": True,
                "rendered": 3,
                "zip_xml": "pass",
                "text_fit": "pass",
                "embedded_dataset": False,
            }
        )
    )


if __name__ == "__main__":
    main()
