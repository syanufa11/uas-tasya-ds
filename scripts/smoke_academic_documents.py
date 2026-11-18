"""Generate and reopen synthetic academic documents; no private research data used."""

import argparse
from pathlib import Path
from xml.etree import ElementTree
from zipfile import ZipFile

from docx import Document
from docx.oxml import OxmlElement
from docx.shared import Cm
from docx.shared import Pt as WordPt
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE
from pptx.util import Inches, Pt

LABEL = "Contoh sintetis untuk uji format"
SUMMARY = "Rata-rata dari 6, 7, dan 8 adalah 7. Contoh ini bukan hasil penelitian."
SOURCE = "https://python-docx.readthedocs.io/en/latest/"


def check_package(path: Path) -> None:
    """Check ZIP integrity and XML well-formedness; this is not visual QA."""
    with ZipFile(path) as package:
        if package.testzip() is not None:
            raise ValueError(f"Corrupt ZIP: {path.name}")
        for name in package.namelist():
            if name.endswith((".xml", ".rels")):
                ElementTree.fromstring(package.read(name))


def build_word(path: Path) -> None:
    """Exercise headings, table, caption, editable equation, references, and editing."""
    document = Document()
    section = document.sections[0]
    section.page_width, section.page_height = Cm(21), Cm(29.7)
    section.top_margin = section.bottom_margin = Cm(2.5)
    section.left_margin = section.right_margin = Cm(2.5)
    normal = document.styles["Normal"]
    normal.font.name, normal.font.size = "Calibri", WordPt(11)
    document.add_heading(LABEL, 0)
    document.add_paragraph("Dokumen ini memeriksa format laporan akademik.")
    document.add_heading("Metode dan contoh perhitungan", 1)
    document.add_paragraph("Tiga nilai sintetis digunakan untuk menghitung rata-rata aritmetika.")
    document.add_paragraph("Tabel 1 Nilai sintetis tanpa satuan", style="Caption")
    table = document.add_table(rows=1, cols=2, style="Table Grid")
    table.rows[0].cells[0].text, table.rows[0].cells[1].text = "Pengamatan", "Nilai"
    for index, value in enumerate((6, 7, 8), 1):
        cells = table.add_row().cells
        cells[0].text, cells[1].text = str(index), str(value)
    paragraph = document.add_paragraph()
    math = OxmlElement("m:oMath")
    run, text = OxmlElement("m:r"), OxmlElement("m:t")
    text.text = "μ = (6 + 7 + 8) / 3 = 7"
    run.append(text)
    math.append(run)
    paragraph._p.append(math)
    document.add_paragraph("μ menyatakan rata-rata aritmetika tiga nilai sintetis.")
    document.add_heading("Pembahasan", 1)
    document.add_paragraph(SUMMARY)
    document.add_paragraph("Perhitungan ini hanya menguji konsistensi isi tabel dan narasi.")
    document.add_heading("Referensi perangkat lunak", 1)
    document.add_paragraph(f"Dokumentasi python-docx. {SOURCE}")
    document.core_properties.author = ""
    document.save(path)
    edited = Document(path)
    edited.add_paragraph("Status: contoh telah dibuka ulang dan disunting secara lokal.")
    edited.save(path)
    reopened = Document(path)
    assert SUMMARY in [item.text for item in reopened.paragraphs]
    assert [row.cells[1].text for row in reopened.tables[0].rows[1:]] == ["6", "7", "8"]
    assert reopened._element.xpath("//m:oMath")


def slide_text(slide, text: str, x: float, y: float, width: float, size: int = 24):
    """Add readable text at deterministic coordinates for the small smoke deck."""
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(width), Inches(1.2))
    box.text_frame.word_wrap = True
    paragraph = box.text_frame.paragraphs[0]
    paragraph.text, paragraph.font.size = text, Pt(size)
    return box


def build_slides(path: Path) -> None:
    """Exercise editable text, table, process diagram, and round-trip editing."""
    deck = Presentation()
    deck.slide_width, deck.slide_height = Inches(13.333), Inches(7.5)
    slide = deck.slides.add_slide(deck.slide_layouts[6])
    slide_text(slide, LABEL, 0.7, 0.5, 12, 34)
    slide_text(slide, "Uji format presentasi akademik", 0.7, 2.0, 12, 28)
    slide_text(slide, "Data sintetis digunakan hanya untuk memeriksa isi dan layout.", 0.7, 3.5, 11)
    slide = deck.slides.add_slide(deck.slide_layouts[6])
    slide_text(slide, "Nilai sintetis dan rata-rata", 0.7, 0.5, 12, 34)
    table = slide.shapes.add_table(4, 2, Inches(0.8), Inches(2), Inches(5), Inches(3)).table
    table.cell(0, 0).text, table.cell(0, 1).text = "Pengamatan", "Nilai"
    for index, value in enumerate((6, 7, 8), 1):
        table.cell(index, 0).text, table.cell(index, 1).text = str(index), str(value)
    for row in table.rows:
        for cell in row.cells:
            for paragraph in cell.text_frame.paragraphs:
                paragraph.font.size = Pt(24)
    slide_text(slide, SUMMARY, 6.5, 2, 5.8)
    slide = deck.slides.add_slide(deck.slide_layouts[6])
    slide_text(slide, "Alur pemeriksaan dan keterbatasan", 0.7, 0.5, 12, 34)
    for index, label in enumerate(("Buat file", "Buka ulang", "Periksa visual")):
        shape = slide.shapes.add_shape(
            MSO_SHAPE.CHEVRON, Inches(0.8 + index * 4.1), Inches(2), Inches(3.7), Inches(1.1)
        )
        shape.text = label
        shape.text_frame.paragraphs[0].font.size = Pt(22)
    slide_text(slide, "Validasi struktur perlu dilengkapi pemeriksaan tampilan.", 0.8, 4, 11.5)
    deck.core_properties.author = ""
    deck.save(path)
    edited = Presentation(path)
    edited.core_properties.subject = "Contoh sintetis telah disunting lokal"
    edited.save(path)
    reopened = Presentation(path)
    assert len(reopened.slides) == 3
    texts = [
        shape.text
        for slide in reopened.slides
        for shape in slide.shapes
        if shape.has_text_frame
    ]
    assert SUMMARY in texts
    values = [shape.table for shape in reopened.slides[1].shapes if shape.has_table][0]
    assert [values.cell(index, 1).text for index in range(1, 4)] == ["6", "7", "8"]


def main() -> None:
    """Create examples only in an explicit scratch directory without overwriting files."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    paths = [args.output_dir / f"academic-smoke.{ext}" for ext in ("docx", "pptx")]
    if any(path.exists() for path in paths):
        raise FileExistsError("Use a fresh output directory; existing samples are preserved.")
    for builder, path in zip((build_word, build_slides), paths, strict=True):
        builder(path)
        check_package(path)
        print(f"PASS build/edit/reopen/XML/CRC/content: {path.name}")
    print("Native application opening and visual QA must be checked separately.")


if __name__ == "__main__":
    main()
