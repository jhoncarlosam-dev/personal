#!/usr/bin/env python3
"""Convierte el informe en Markdown a un documento de Word con formato APA."""

import re
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
OUT = BASE / "Informe_Fase4_Redes_y_Comunicaciones.docx"
PARTS = [
    BASE / "01-intro.md",
    BASE / "02-ipv4.md",
    BASE / "03-ipv6.md",
    BASE / "04-escaneo.md",
    BASE / "05-cierre.md",
]

NAVY = RGBColor(0x1B, 0x3A, 0x4B)
RED = RGBColor(0x8C, 0x2A, 0x30)


def set_run_font(run, name="Times New Roman", size=12, bold=False, italic=False, color=None):
    run.font.name = name
    run._element.rPr.rFonts.set(qn("w:eastAsia"), name)
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    if color is not None:
        run.font.color.rgb = color


def shade_cell(cell, color):
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), color)
    shd.set(qn("w:val"), "clear")
    tc_pr.append(shd)


def set_cell_border(cell, color="C4A35A"):
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    tc_borders = OxmlElement("w:tcBorders")
    for edge in ("top", "left", "bottom", "right"):
        element = OxmlElement(f"w:{edge}")
        element.set(qn("w:val"), "single")
        element.set(qn("w:sz"), "8")
        element.set(qn("w:color"), color)
        tc_borders.append(element)
    tc_pr.append(tc_borders)


def add_page_field(paragraph):
    run = paragraph.add_run()
    set_run_font(run, size=10, color=NAVY)
    for kind, text in (("begin", None), ("instr", " PAGE "), ("end", None)):
        if kind == "instr":
            node = OxmlElement("w:instrText")
            node.set(qn("xml:space"), "preserve")
            node.text = text
        else:
            node = OxmlElement("w:fldChar")
            node.set(qn("w:fldCharType"), kind)
        run._r.append(node)


def add_markup(paragraph, text, size=12, base_italic=False):
    pattern = re.compile(r"(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)")
    pos = 0
    for match in pattern.finditer(text):
        if match.start() > pos:
            run = paragraph.add_run(text[pos:match.start()])
            set_run_font(run, size=size, italic=base_italic)
        token = match.group(0)
        if token.startswith("**"):
            run = paragraph.add_run(token[2:-2])
            set_run_font(run, size=size, bold=True, italic=base_italic)
        elif token.startswith("`"):
            run = paragraph.add_run(token[1:-1])
            set_run_font(run, name="Courier New", size=max(9, size - 2), italic=base_italic)
        else:
            run = paragraph.add_run(token[1:-1])
            set_run_font(run, size=size, italic=True)
        pos = match.end()
    if pos < len(text):
        run = paragraph.add_run(text[pos:])
        set_run_font(run, size=size, italic=base_italic)


def is_special(line):
    stripped = line.lstrip()
    return (
        stripped.startswith("#")
        or stripped.startswith("|")
        or stripped.startswith("- ")
        or stripped.startswith("```")
        or stripped.startswith(":::")
        or stripped.startswith("![")
        or stripped.startswith("{{archivo:")
        or stripped.startswith("<!--")
        or re.match(r"\d+\. ", stripped) is not None
    )


def parse(markdown):
    lines = markdown.splitlines()
    blocks = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        if line.strip().startswith("<!-- salto"):
            blocks.append(("break",))
            i += 1
            continue
        if line.strip().startswith(":::evidencia"):
            i += 1
            buf = []
            while i < len(lines) and lines[i].strip() != ":::":
                buf.append(lines[i])
                i += 1
            i += 1
            blocks.append(("evidence", "\n".join(buf).strip()))
            continue
        if line.startswith("```"):
            i += 1
            buf = []
            while i < len(lines) and not lines[i].startswith("```"):
                buf.append(lines[i])
                i += 1
            i += 1
            blocks.append(("code", "\n".join(buf).rstrip()))
            continue
        if line.strip().startswith("{{archivo:"):
            raw = line.strip()[10:]
            raw = raw[:-2] if raw.endswith("}}") else raw
            blocks.append(("code", (ROOT / raw).read_text(encoding="utf-8").rstrip()))
            i += 1
            continue
        if line.startswith("#"):
            level = len(line) - len(line.lstrip("#"))
            blocks.append(("h", min(level, 3), line.lstrip("#").strip()))
            i += 1
            continue
        if line.startswith("!["):
            match = re.match(r"!\[(.*?)\]\((.*?)\)", line.strip())
            blocks.append(("image", match.group(1), match.group(2)))
            i += 1
            continue
        if line.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                cells = [cell.strip() for cell in lines[i].strip().strip("|").split("|")]
                rows.append(cells)
                i += 1
            data = [row for row in rows if not all(re.fullmatch(r":?-{3,}:?", cell or "-") for cell in row)]
            blocks.append(("table", data))
            continue
        if line.startswith("- "):
            items = []
            while i < len(lines) and lines[i].startswith("- "):
                items.append(lines[i][2:].strip())
                i += 1
            blocks.append(("ul", items))
            continue
        if re.match(r"\d+\. ", line):
            items = []
            while i < len(lines) and re.match(r"\d+\. ", lines[i]):
                items.append(re.sub(r"^\d+\.\s+", "", lines[i]).strip())
                i += 1
            blocks.append(("ol", items))
            continue
        buf = [line.strip()]
        i += 1
        while i < len(lines) and lines[i].strip() and not is_special(lines[i]):
            buf.append(lines[i].strip())
            i += 1
        blocks.append(("p", " ".join(buf)))
    return blocks


def configure_styles(document):
    normal = document.styles["Normal"]
    normal.font.name = "Times New Roman"
    normal.font.size = Pt(12)
    normal.font.color.rgb = RGBColor(0x21, 0x25, 0x29)
    normal._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
    pf = normal.paragraph_format
    pf.line_spacing = 1.5
    pf.space_after = Pt(8)
    pf.space_before = Pt(0)
    for level, size in ((1, 16), (2, 14), (3, 12)):
        style = document.styles[f"Heading {level}"]
        style.font.name = "Times New Roman"
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.color.rgb = NAVY
        style.font.italic = False
        style._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
        style.paragraph_format.space_before = Pt(16 if level == 1 else 12)
        style.paragraph_format.space_after = Pt(6)
        style.paragraph_format.line_spacing = 1.15


def add_cover(document):
    def center(text, size=12, bold=False, color=None, after=4, before=0):
        p = document.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(after)
        p.paragraph_format.space_before = Pt(before)
        p.paragraph_format.line_spacing = 1.15
        run = p.add_run(text)
        set_run_font(run, size=size, bold=bold, color=color or NAVY)
        return p

    center("Universidad Nacional Abierta y a Distancia", 16, True, before=24)
    center("Vicerrectoría Académica y de Investigación", 12)
    center("Escuela de Ciencias Básicas, Tecnología e Ingeniería", 12)
    center("Programa de Ingeniería de Sistemas", 12, after=12)
    center("Curso: Redes y comunicaciones", 12)
    center("Código: 202016898", 12, after=14)
    center("Fase 4. Componente práctico", 14, True)
    center("Prácticas simuladas", 14, True, after=16)
    center("Diseño de redes IPv4 e IPv6 con servicios convergentes", 16, True)
    center("y análisis de visibilidad de un segmento autorizado", 16, True, after=16)
    center("Tutor: Alkigner Cuesta Rodriguez", 12)
    center("Estudiante: Jhon Carlos Acevedo Mendoza", 12, True)
    center("Código del estudiante: [ESCRIBA SU CÓDIGO]", 12, color=RED)
    center("Centro: [ESCRIBA SU CEAD O UDR]", 12, color=RED, after=8)
    center("Noviembre de 2026", 12, after=12)

    p = document.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(4)
    run = p.add_run("Integrantes que sí participaron en el foro y en la construcción")
    set_run_font(run, size=11, italic=True, color=NAVY)

    table = document.add_table(rows=5, cols=3)
    table.style = "Table Grid"
    headers = ["Nombre", "Código", "Rol en el grupo"]
    data = [
        ["Jhon Carlos Acevedo Mendoza", "[CÓDIGO]", "Direccionamiento, topología y consolidación"],
        ["[Integrante 2]", "[CÓDIGO]", "[Rol acordado]"],
        ["[Integrante 3]", "[CÓDIGO]", "[Rol acordado]"],
        ["[Integrante 4]", "[CÓDIGO]", "[Rol acordado]"],
    ]
    for index, text in enumerate(headers):
        cell = table.rows[0].cells[index]
        cell.text = ""
        paragraph = cell.paragraphs[0]
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = paragraph.add_run(text)
        set_run_font(run, size=11, bold=True, color=RGBColor(255, 255, 255))
        shade_cell(cell, "1B3A4B")
    for row_index, row_data in enumerate(data, start=1):
        for col_index, text in enumerate(row_data):
            cell = table.rows[row_index].cells[col_index]
            cell.text = ""
            paragraph = cell.paragraphs[0]
            run = paragraph.add_run(text)
            color = RED if text.startswith("[") else None
            set_run_font(run, size=11, color=color)

    note = document.add_paragraph()
    note.alignment = WD_ALIGN_PARAGRAPH.CENTER
    note.paragraph_format.space_before = Pt(10)
    run = note.add_run(
        "La guía del curso pide incluir solo a quienes hayan aportado durante el tiempo de la actividad. "
        "Borre las filas que no correspondan a una persona real del grupo."
    )
    set_run_font(run, size=10, italic=True)
    document.add_page_break()


def add_warning(document):
    table = document.add_table(rows=1, cols=1)
    cell = table.cell(0, 0)
    cell.text = ""
    shade_cell(cell, "FBF3D5")
    set_cell_border(cell, "8C2A30")
    paragraph = cell.paragraphs[0]
    run = paragraph.add_run("Antes de entregar, lea esto. ")
    set_run_font(run, size=12, bold=True, color=RED)
    run = paragraph.add_run(
        "Este documento trae el diseño, los cálculos, la configuración y la lectura de los referentes. "
        "No trae capturas de una simulación que todavía no se ha ejecutado, ni resultados de Nmap o de PRTG, "
        "ni el video. Esos tres elementos los produce el grupo en sus computadores. "
        "Entregar los recuadros amarillos vacíos, o llenarlos con imágenes de otra red, deja la evidencia incompleta. "
        "El Acuerdo 029 de 2013, citado en la propia guía, trata como falta presentar como propia una ejecución que no se realizó."
    )
    set_run_font(run, size=12)
    document.add_paragraph()


def render(document, blocks):
    in_references = False
    for block in blocks:
        kind = block[0]
        if kind == "break":
            document.add_page_break()
            continue
        if kind == "h":
            _, level, text = block
            in_references = text.strip().lower() == "referencias"
            document.add_heading(text, level=level)
            continue
        if kind == "p":
            paragraph = document.add_paragraph()
            paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            paragraph.paragraph_format.first_line_indent = Cm(0 if in_references else 1.25)
            if in_references:
                paragraph.paragraph_format.left_indent = Cm(1.25)
                paragraph.paragraph_format.first_line_indent = Cm(-1.25)
                paragraph.paragraph_format.space_after = Pt(10)
            add_markup(paragraph, block[1], base_italic=False)
            continue
        if kind == "ul":
            for item in block[1]:
                paragraph = document.add_paragraph(style="List Bullet")
                paragraph.paragraph_format.line_spacing = 1.5
                add_markup(paragraph, item)
            continue
        if kind == "ol":
            for item in block[1]:
                paragraph = document.add_paragraph(style="List Number")
                paragraph.paragraph_format.line_spacing = 1.5
                add_markup(paragraph, item)
            continue
        if kind == "table":
            rows = block[1]
            if not rows:
                continue
            columns = max(len(row) for row in rows)
            table = document.add_table(rows=len(rows), cols=columns)
            table.style = "Table Grid"
            table.autofit = True
            for r_index, row in enumerate(rows):
                for c_index in range(columns):
                    text = row[c_index] if c_index < len(row) else ""
                    cell = table.rows[r_index].cells[c_index]
                    cell.text = ""
                    paragraph = cell.paragraphs[0]
                    paragraph.paragraph_format.space_after = Pt(2)
                    paragraph.paragraph_format.line_spacing = 1.0
                    add_markup(paragraph, text, size=10, base_italic=False)
                    if r_index == 0:
                        shade_cell(cell, "1B3A4B")
                        for run in paragraph.runs:
                            run.font.color.rgb = RGBColor(255, 255, 255)
                            run.bold = True
                    elif r_index % 2 == 0:
                        shade_cell(cell, "F4F7F6")
            document.add_paragraph().paragraph_format.space_after = Pt(4)
            continue
        if kind == "code":
            for line in (block[1] or "").splitlines() or [""]:
                paragraph = document.add_paragraph()
                paragraph.paragraph_format.space_before = Pt(0)
                paragraph.paragraph_format.space_after = Pt(0)
                paragraph.paragraph_format.line_spacing = 1.0
                paragraph.paragraph_format.left_indent = Cm(0.5)
                run = paragraph.add_run(line if line else " ")
                set_run_font(run, name="Courier New", size=9)
                shading = OxmlElement("w:shd")
                shading.set(qn("w:fill"), "F4F4F4")
                shading.set(qn("w:val"), "clear")
                paragraph._p.get_or_add_pPr().append(shading)
            document.add_paragraph().paragraph_format.space_after = Pt(6)
            continue
        if kind == "image":
            _, alt, path = block
            image_path = (BASE / path).resolve()
            paragraph = document.add_paragraph()
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = paragraph.add_run()
            run.add_picture(str(image_path), width=Inches(6.3))
            caption = document.add_paragraph()
            caption.alignment = WD_ALIGN_PARAGRAPH.CENTER
            caption.paragraph_format.space_after = Pt(10)
            add_markup(caption, alt, size=11, base_italic=True)
            continue
        if kind == "evidence":
            table = document.add_table(rows=1, cols=1)
            cell = table.cell(0, 0)
            cell.text = ""
            shade_cell(cell, "FBF3D5")
            set_cell_border(cell, "C4A35A")
            first = cell.paragraphs[0]
            add_markup(first, block[1], size=11)
            second = cell.add_paragraph()
            second.paragraph_format.space_before = Pt(8)
            run = second.add_run("[Inserte aquí la captura tomada por el grupo. Recorte la barra del sistema si muestra datos personales que no hagan falta.]")
            set_run_font(run, size=11, italic=True, color=RED)
            spacer = document.add_paragraph()
            spacer.paragraph_format.space_after = Pt(8)
            continue


def main():
    document = Document()
    section = document.sections[0]
    section.top_margin = Cm(2.54)
    section.bottom_margin = Cm(2.54)
    section.left_margin = Cm(2.54)
    section.right_margin = Cm(2.54)
    section.page_width = Inches(8.5)
    section.page_height = Inches(11)
    footer = section.footer
    footer.is_linked_to_previous = False
    paragraph = footer.paragraphs[0]
    paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = paragraph.add_run("Fase 4 · Redes y comunicaciones · 202016898  ·  p. ")
    set_run_font(run, size=10, color=NAVY)
    add_page_field(paragraph)
    configure_styles(document)
    add_cover(document)
    add_warning(document)
    text = "\n\n".join(path.read_text(encoding="utf-8") for path in PARTS)
    render(document, parse(text))
    document.save(OUT)
    print(OUT)


if __name__ == "__main__":
    main()
