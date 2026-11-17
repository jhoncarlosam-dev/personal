#!/usr/bin/env python3
"""Arma el anexo de la Fase 3, la figura del MSV y los textos del foro."""

import copy
import shutil
import subprocess
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor

ROOT = Path(__file__).resolve().parent
TEMPLATE = Path("/tmp/plantilla.pptx")
PPTX = ROOT / "Figura_MSV_Nelumbo.pptx"
PNG = ROOT / "figura_msv.png"
PNG_RED = ROOT / "figura_red.png"
DOCX = ROOT / "Anexo_Fase_3_Nelumbo.docx"
PDF = ROOT / "Anexo_Fase_3_Nelumbo.pdf"
FORO = ROOT / "textos-para-el-foro.txt"

A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
P = "{http://schemas.openxmlformats.org/presentationml/2006/main}"
ET.register_namespace("a", "http://schemas.openxmlformats.org/drawingml/2006/main")
ET.register_namespace("p", "http://schemas.openxmlformats.org/presentationml/2006/main")
ET.register_namespace("r", "http://schemas.openxmlformats.org/officeDocument/2006/relationships")

NAVY = RGBColor(0x1F, 0x4E, 0x79)
RULE = "1F4E79"


def shape_by_name(tree, name):
    for sp in tree.iter(P + "sp"):
        nv = sp.find(".//" + P + "cNvPr")
        if nv is not None and nv.get("name") == name:
            return sp
    raise KeyError(name)


def paragraphs(sp):
    tx = sp.find(".//" + P + "txBody")
    return [el for el in list(tx) if el.tag == A + "p"]


def set_para_text(p, text, size=None, bold=False):
    run = p.find(A + "r")
    if run is not None:
        node = run.find(A + "t")
        node.text = text
        rpr = run.find(A + "rPr")
        if rpr is not None:
            if size:
                rpr.set("sz", str(size))
            if bold:
                rpr.set("b", "1")
            elif "b" in rpr.attrib:
                del rpr.attrib["b"]
        return
    end = p.find(A + "endParaRPr")
    rpr = ET.Element(A + "rPr")
    if end is not None:
        for key, value in end.attrib.items():
            if key != "b":
                rpr.set(key, value)
        for child in list(end):
            rpr.append(child)
        p.remove(end)
    else:
        rpr.set("lang", "es-CO")
        rpr.set("dirty", "0")
        latin = ET.Element(A + "latin")
        latin.set("typeface", "Verdana")
        rpr.append(latin)
    if size:
        rpr.set("sz", str(size))
    if bold:
        rpr.set("b", "1")
    run = ET.Element(A + "r")
    run.append(rpr)
    node = ET.Element(A + "t")
    node.text = text
    run.append(node)
    p.append(run)


def insert_after(sp, anchor, text, size, bold=False):
    tx = sp.find(".//" + P + "txBody")
    new = copy.deepcopy(anchor)
    for child in list(new):
        if child.tag != A + "pPr":
            new.remove(child)
    set_para_text(new, text, size=size, bold=bold)
    anchor_index = list(tx).index(anchor)
    tx.insert(anchor_index + 1, new)
    return new


def fill_slide(src, dest):
    with zipfile.ZipFile(src) as zin:
        tree = ET.ElementTree(ET.fromstring(zin.read("ppt/slides/slide1.xml")))
    entorno = shape_by_name(tree, "Rectángulo 1")
    env_ps = paragraphs(entorno)
    set_para_text(env_ps[1], "Clientes empresariales", size=1100)
    cursor = env_ps[1]
    for line in (
        "Mercado de talento",
        "Proveedores tecnológicos",
        "Entes reguladores",
    ):
        cursor = insert_after(entorno, cursor, line, 1100)

    org = shape_by_name(tree, "Rectángulo 5")
    org_ps = paragraphs(org)
    set_para_text(
        org_ps[3],
        "Nelumbo Consultores. Consultoría tecnológica de operación remota.",
        size=1100,
    )
    problem = insert_after(
        org,
        org_ps[-1],
        "Al cerrar, el saber técnico no queda documentado. La operación depende de personas.",
        1100,
    )
    problem_pr = problem.find(A + "pPr")
    if problem_pr is None:
        problem_pr = ET.Element(A + "pPr")
        problem.insert(0, problem_pr)
    problem_pr.set("algn", "l")

    processes = {
        "Rectángulo 25": "Desarrollo",
        "Rectángulo 39": "QA",
        "Rectángulo 43": "Soporte",
        "Rectángulo 45": "Diseño",
        "Rectángulo 41": "Cierre",
        "Rectángulo 37": "Lecciones",
    }
    for name, label in processes.items():
        sp = shape_by_name(tree, name)
        set_para_text(paragraphs(sp)[0], label, size=900, bold=True)

    systems = {
        "Rectángulo 47": "Director general",
        "Rectángulo 57": "Mercado y talento",
        "Rectángulo 59": "Informes vigentes",
        "Rectángulo 63": "Líderes de proyecto",
        "Rectángulo 61": "Verificar el registro",
    }
    for name, label in systems.items():
        sp = shape_by_name(tree, name)
        ps = paragraphs(sp)
        set_para_text(ps[0], para_text(ps[0]), size=1000, bold=True)
        if len(ps) > 1:
            set_para_text(ps[1], label, size=1000, bold=False)
        else:
            insert_after(sp, ps[0], label, 1000, bold=False)

    desc = shape_by_name(tree, "Rectángulo 11")
    desc_ps = paragraphs(desc)
    set_para_text(
        desc_ps[-1],
        "El saber nace en desarrollo, QA, soporte y cierre. El sistema 2 acuerda el formato y la consulta. "
        "El 3 mide satisfacción, defectos y tiempos, no si el saber circula. El 3* verifica el registro. "
        "El 4 lee talento y tecnología. El 5 autoriza la base. Esas funciones dependen unas de otras.",
        size=1000,
    )

    dest.write_bytes(b"")
    xml = ET.tostring(tree.getroot(), encoding="utf-8", xml_declaration=True)
    with zipfile.ZipFile(src, "r") as zin, zipfile.ZipFile(dest, "w") as zout:
        for item in zin.infolist():
            data = xml if item.filename == "ppt/slides/slide1.xml" else zin.read(item.filename)
            zout.writestr(item, data)


def para_text(p):
    return "".join((node.text or "") for node in p.iter(A + "t"))


def render_figure():
    work = Path("/tmp/msv-render")
    if work.exists():
        shutil.rmtree(work)
    work.mkdir()
    fill_slide(TEMPLATE, PPTX)
    subprocess.run(
        [
            "soffice",
            "--headless",
            "--norestore",
            "-env:UserInstallation=file:///tmp/lo-profile-fase3",
            "--convert-to",
            "pdf",
            "--outdir",
            str(work),
            str(PPTX),
        ],
        check=True,
        capture_output=True,
    )
    pdf = next(work.glob("*.pdf"))
    subprocess.run(
        ["pdftoppm", "-png", "-r", "140", "-singlefile", str(pdf), str(PNG.with_suffix(""))],
        check=True,
    )


def render_network():
    html_path = ROOT / "figura_red.html"
    html_path.write_text(
        """<!DOCTYPE html>
<html lang="es">
<meta charset="utf-8">
<title>Red de dependencias</title>
<style>
  html, body { margin: 0; background: #fff; }
  svg { display: block; }
</style>
<body>
<svg xmlns="http://www.w3.org/2000/svg" width="1180" height="820" viewBox="0 0 1180 820">
  <defs>
    <marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">
      <path d="M 0 1.2 L 9 5 L 0 8.8 z" fill="#1F4E79"/>
    </marker>
    <marker id="arrd" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">
      <path d="M 0 1.2 L 9 5 L 0 8.8 z" fill="#8A5A00"/>
    </marker>
  </defs>
  <rect width="1180" height="820" fill="#ffffff"/>
  <text x="590" y="28" text-anchor="middle" font-family="Arial" font-size="13" fill="#666">Las flechas continuas son dependencias de la operación. Las punteadas cierran la decisión y la retroalimentación.</text>

  <rect x="460" y="48" width="260" height="62" rx="8" fill="#F8F1E3" stroke="#1F4E79" stroke-width="1.6"/>
  <text x="590" y="73" text-anchor="middle" font-family="Arial" font-size="16" font-weight="700" fill="#1F4E79">Director general</text>
  <text x="590" y="94" text-anchor="middle" font-family="Arial" font-size="13" fill="#333">Autoriza tiempo y continuidad</text>

  <rect x="70" y="168" width="270" height="62" rx="8" fill="#F8F1E3" stroke="#1F4E79" stroke-width="1.6"/>
  <text x="205" y="193" text-anchor="middle" font-family="Arial" font-size="16" font-weight="700" fill="#1F4E79">Líderes de proyecto</text>
  <text x="205" y="214" text-anchor="middle" font-family="Arial" font-size="13" fill="#333">Criterio, formato y consulta</text>

  <rect x="840" y="168" width="270" height="62" rx="8" fill="#F8F1E3" stroke="#1F4E79" stroke-width="1.6"/>
  <text x="975" y="193" text-anchor="middle" font-family="Arial" font-size="16" font-weight="700" fill="#1F4E79">Informes de desempeño</text>
  <text x="975" y="214" text-anchor="middle" font-family="Arial" font-size="13" fill="#333">Satisfacción, defectos, tiempos</text>

  <rect x="70" y="330" width="250" height="70" rx="8" fill="#E7F4EA" stroke="#1F4E79" stroke-width="1.6"/>
  <text x="195" y="358" text-anchor="middle" font-family="Arial" font-size="16" font-weight="700" fill="#1F4E79">Fuentes del saber</text>
  <text x="195" y="380" text-anchor="middle" font-family="Arial" font-size="13" fill="#333">Cierre, QA y soporte</text>

  <rect x="390" y="330" width="220" height="70" rx="8" fill="#E7F4EA" stroke="#1F4E79" stroke-width="1.6"/>
  <text x="500" y="358" text-anchor="middle" font-family="Arial" font-size="16" font-weight="700" fill="#1F4E79">Identificar</text>
  <text x="500" y="380" text-anchor="middle" font-family="Arial" font-size="13" fill="#333">Lecciones y prácticas</text>

  <rect x="680" y="330" width="200" height="70" rx="8" fill="#E7F4EA" stroke="#1F4E79" stroke-width="1.6"/>
  <text x="780" y="358" text-anchor="middle" font-family="Arial" font-size="16" font-weight="700" fill="#1F4E79">Documentar</text>
  <text x="780" y="380" text-anchor="middle" font-family="Arial" font-size="13" fill="#333">Formato común</text>

  <rect x="940" y="330" width="190" height="70" rx="8" fill="#E7F4EA" stroke="#1F4E79" stroke-width="1.6"/>
  <text x="1035" y="358" text-anchor="middle" font-family="Arial" font-size="16" font-weight="700" fill="#1F4E79">Base interna</text>
  <text x="1035" y="380" text-anchor="middle" font-family="Arial" font-size="13" fill="#333">Plataformas ya usadas</text>

  <rect x="940" y="500" width="190" height="70" rx="8" fill="#E7F4EA" stroke="#1F4E79" stroke-width="1.6"/>
  <text x="1035" y="528" text-anchor="middle" font-family="Arial" font-size="16" font-weight="700" fill="#1F4E79">Consultar</text>
  <text x="1035" y="550" text-anchor="middle" font-family="Arial" font-size="13" fill="#333">Requerir y diseñar</text>

  <rect x="500" y="620" width="250" height="70" rx="8" fill="#E8F1F8" stroke="#1F4E79" stroke-width="1.6"/>
  <text x="625" y="648" text-anchor="middle" font-family="Arial" font-size="16" font-weight="700" fill="#1F4E79">Evaluar</text>
  <text x="625" y="670" text-anchor="middle" font-family="Arial" font-size="13" fill="#333">Si se registró y se consultó</text>

  <rect x="70" y="700" width="280" height="58" rx="8" fill="#F4F7FB" stroke="#1F4E79" stroke-width="1.4" stroke-dasharray="6 4"/>
  <text x="210" y="724" text-anchor="middle" font-family="Arial" font-size="15" font-weight="700" fill="#1F4E79">Mercado de talento</text>
  <text x="210" y="744" text-anchor="middle" font-family="Arial" font-size="12" fill="#333">La rotación se lleva el saber no escrito</text>

  <line x1="320" y1="365" x2="388" y2="365" stroke="#1F4E79" stroke-width="1.6" marker-end="url(#arr)"/>
  <line x1="610" y1="365" x2="678" y2="365" stroke="#1F4E79" stroke-width="1.6" marker-end="url(#arr)"/>
  <line x1="880" y1="365" x2="938" y2="365" stroke="#1F4E79" stroke-width="1.6" marker-end="url(#arr)"/>
  <line x1="1035" y1="400" x2="1035" y2="498" stroke="#1F4E79" stroke-width="1.6" marker-end="url(#arr)"/>
  <path d="M860 230 C 800 420, 780 540, 730 618" fill="none" stroke="#1F4E79" stroke-width="1.6" marker-end="url(#arr)"/>
  <path d="M205 230 C 205 280, 430 280, 470 328" fill="none" stroke="#1F4E79" stroke-width="1.6" marker-end="url(#arr)"/>
  <path d="M300 190 C 520 190, 700 250, 760 328" fill="none" stroke="#1F4E79" stroke-width="1.6" marker-end="url(#arr)"/>
  <path d="M500 110 C 380 130, 280 145, 230 166" fill="none" stroke="#8A5A00" stroke-width="1.5" stroke-dasharray="5 4" marker-end="url(#arrd)"/>
  <path d="M940 560 C 820 640, 760 655, 752 655" fill="none" stroke="#1F4E79" stroke-width="1.6" marker-end="url(#arr)"/>
  <path d="M1035 400 C 1120 470, 1120 680, 752 670" fill="none" stroke="#1F4E79" stroke-width="1.4" marker-end="url(#arr)"/>
  <path d="M500 655 C 360 655, 300 470, 470 390" fill="none" stroke="#8A5A00" stroke-width="1.5" stroke-dasharray="5 4" marker-end="url(#arrd)"/>
  <path d="M625 620 C 625 520, 620 180, 590 112" fill="none" stroke="#8A5A00" stroke-width="1.5" stroke-dasharray="5 4" marker-end="url(#arrd)"/>
  <path d="M350 730 C 470 760, 520 140, 560 112" fill="none" stroke="#8A5A00" stroke-width="1.4" stroke-dasharray="5 4" marker-end="url(#arrd)"/>

  <text x="330" y="338" font-family="Arial" font-size="12" fill="#1F4E79">tres entradas</text>
  <text x="430" y="250" font-family="Arial" font-size="12" fill="#1F4E79">criterio</text>
  <text x="520" y="230" font-family="Arial" font-size="12" fill="#1F4E79">formato</text>
  <text x="760" y="430" font-family="Arial" font-size="12" fill="#1F4E79">informe</text>
  <text x="360" y="128" font-family="Arial" font-size="12" fill="#8A5A00">autoriza</text>
  <text x="1088" y="560" font-family="Arial" font-size="12" fill="#1F4E79">evidencia</text>
  <text x="300" y="600" font-family="Arial" font-size="12" fill="#8A5A00">ajusta cómo se identifica</text>
  <text x="500" y="500" font-family="Arial" font-size="12" fill="#8A5A00">sostener o detener</text>
</svg>
</body>
</html>
""",
        encoding="utf-8",
    )
    svg_path = ROOT / "figura_red.svg"
    html = html_path.read_text(encoding="utf-8")
    svg_path.write_text(html[html.index("<svg") : html.index("</svg>") + len("</svg>")], encoding="utf-8")
    subprocess.run(
        ["rsvg-convert", "-w", "1180", "-h", "820", "-o", str(PNG_RED), str(svg_path)],
        check=True,
    )


def shade(cell, color):
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), color)
    shd.set(qn("w:val"), "clear")
    tc_pr.append(shd)


def set_run_font(run, size=12, bold=False, italic=False, color=None, name="Arial"):
    run.bold = bold
    run.italic = italic
    run.font.name = name
    run.font.size = Pt(size)
    if color:
        run.font.color.rgb = color
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    for attr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rfonts.set(qn(attr), name)


def add_text(paragraph, text, **kwargs):
    run = paragraph.add_run(text)
    set_run_font(run, **kwargs)
    return run


def body(document, text, space_after=6, first_line=None):
    paragraph = document.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    paragraph.paragraph_format.space_after = Pt(space_after)
    paragraph.paragraph_format.space_before = Pt(0)
    paragraph.paragraph_format.line_spacing = 1.5
    if first_line:
        paragraph.paragraph_format.first_line_indent = Cm(first_line)
    add_text(paragraph, text)
    return paragraph


def heading(document, text, level=1):
    paragraph = document.add_heading(text, level=level)
    paragraph.paragraph_format.space_before = Pt(16 if level == 1 else 12)
    paragraph.paragraph_format.space_after = Pt(6)
    paragraph.paragraph_format.line_spacing = 1.15
    for run in paragraph.runs:
        set_run_font(run, size=14 if level == 1 else 12, bold=True, color=NAVY)
    return paragraph


def set_cell(cell, text, bold=False, center=False, header=False):
    cell.text = ""
    paragraph = cell.paragraphs[0]
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER if center or header else WD_ALIGN_PARAGRAPH.LEFT
    paragraph.paragraph_format.space_after = Pt(2)
    paragraph.paragraph_format.space_before = Pt(2)
    paragraph.paragraph_format.line_spacing = 1.08
    add_text(
        paragraph,
        text,
        size=10,
        bold=bold or header,
        color=RGBColor(255, 255, 255) if header else RGBColor(0x22, 0x22, 0x22),
    )
    if header:
        shade(cell, RULE)
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    mar = OxmlElement("w:tcMar")
    for edge, value in (("top", "60"), ("left", "80"), ("bottom", "60"), ("right", "80")):
        node = OxmlElement(f"w:{edge}")
        node.set(qn("w:w"), value)
        node.set(qn("w:type"), "dxa")
        mar.append(node)
    tc_pr.append(mar)


def row_flags(row, header=False):
    tr_pr = row._tr.get_or_add_trPr()
    if header:
        mark = OxmlElement("w:tblHeader")
        tr_pr.append(mark)
    keep = OxmlElement("w:cantSplit")
    tr_pr.append(keep)


def add_table(document, headers, rows, widths):
    table = document.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    for index, header in enumerate(headers):
        set_cell(table.rows[0].cells[index], header, header=True, center=True)
    row_flags(table.rows[0], header=True)
    for r_index, row in enumerate(rows):
        for c_index, value in enumerate(row):
            set_cell(table.rows[r_index + 1].cells[c_index], value, bold=(c_index == 0))
            if r_index % 2 == 1:
                shade(table.rows[r_index + 1].cells[c_index], "F4F7FB")
        row_flags(table.rows[r_index + 1])
    for row in table.rows:
        for index, width in enumerate(widths):
            row.cells[index].width = Cm(width)
    return table


def caption(document, number, title):
    paragraph = document.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.paragraph_format.space_before = Pt(10)
    paragraph.paragraph_format.space_after = Pt(2)
    paragraph.paragraph_format.keep_with_next = True
    add_text(paragraph, f"{number} ", size=11, bold=True)
    add_text(paragraph, title, size=11, italic=True)
    return paragraph


def note(document, text):
    paragraph = document.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
    paragraph.paragraph_format.space_after = Pt(8)
    paragraph.paragraph_format.space_before = Pt(2)
    add_text(paragraph, "Nota. ", size=10, italic=True)
    add_text(paragraph, text, size=10, italic=True)


def page_number(paragraph):
    run = paragraph.add_run()
    set_run_font(run, size=9, color=RGBColor(0x55, 0x55, 0x55))
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = " PAGE "
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    run._r.append(begin)
    run._r.append(instr)
    run._r.append(end)


def configure_section(section, landscape=False):
    if landscape:
        section.orientation = WD_ORIENT.LANDSCAPE
        section.page_width = Inches(11)
        section.page_height = Inches(8.5)
        section.left_margin = Cm(1.4)
        section.right_margin = Cm(1.4)
        section.top_margin = Cm(1.5)
        section.bottom_margin = Cm(1.5)
    else:
        section.orientation = WD_ORIENT.PORTRAIT
        section.page_width = Inches(8.5)
        section.page_height = Inches(11)
        section.left_margin = Cm(2.5)
        section.right_margin = Cm(2.5)
        section.top_margin = Cm(2.3)
        section.bottom_margin = Cm(2.2)
    section.header_distance = Cm(0.6)
    section.footer_distance = Cm(0.5)
    section.different_first_page_header_footer = False
    header = section.header
    header.is_linked_to_previous = False
    hp = header.paragraphs[0]
    hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    add_text(hp, "Teoría de Sistemas en las Organizaciones  ·  Fase 3  ·  204016", size=8, color=RGBColor(0x66, 0x66, 0x66))
    footer = section.footer
    footer.is_linked_to_previous = False
    fp = footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    page_number(fp)


def set_alt(picture, text):
    picture._inline.docPr.set("descr", text)


def reference(document, parts):
    paragraph = document.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
    paragraph.paragraph_format.left_indent = Cm(1.25)
    paragraph.paragraph_format.first_line_indent = Cm(-1.25)
    paragraph.paragraph_format.space_after = Pt(8)
    paragraph.paragraph_format.line_spacing = 1.15
    for text, italic in parts:
        add_text(paragraph, text, size=12, italic=italic)
    return paragraph


def build_document():
    document = Document()
    normal = document.styles["Normal"]
    normal.font.name = "Arial"
    normal.font.size = Pt(12)
    normal._element.rPr.rFonts.set(qn("w:eastAsia"), "Arial")
    configure_section(document.sections[0])

    core = document.core_properties
    core.author = "Jhon Carlos Acevedo Mendoza"
    core.title = "Fase 3 - Evaluando la viabilidad organizacional"
    core.subject = "Modelo de Sistemas Viables aplicado a Nelumbo Consultores"
    core.category = "UNAD 204016"

    title = document.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.paragraph_format.space_after = Pt(4)
    add_text(title, "Fase 3 - Evaluando la viabilidad organizacional", size=16, bold=True, color=NAVY)

    subtitle = document.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    subtitle.paragraph_format.space_after = Pt(12)
    add_text(subtitle, "Gestión del conocimiento en Nelumbo Consultores", size=12, italic=True, color=NAVY)

    for label, value in (
        ("Nombre del estudiante: ", "Jhon Carlos Acevedo Mendoza"),
        ("Tutor: ", "Ing. Víctor Hugo Mercado Ramos"),
        ("Universidad: ", "Universidad Nacional Abierta y a Distancia"),
        ("Unidad gestora: ", "Escuela de Ciencias Básicas, Tecnología e Ingeniería"),
        ("Programa: ", "Ingeniería de Sistemas"),
        ("Curso: ", "Teoría de Sistemas en las Organizaciones"),
        ("Código: ", "204016"),
        ("Lugar y fecha: ", "17 de noviembre de 2026"),
    ):
        line = document.add_paragraph()
        line.alignment = WD_ALIGN_PARAGRAPH.CENTER
        line.paragraph_format.space_after = Pt(0)
        line.paragraph_format.line_spacing = 1.15
        add_text(line, label, size=12, bold=True)
        add_text(line, value, size=12)

    heading(document, "Introducción")
    body(
        document,
        "Este documento aplica el Modelo de Sistemas Viables (MSV) a Nelumbo Consultores, la consultora tecnológica de operación remota analizada en las fases anteriores. La problemática priorizada sigue siendo la ausencia de un sistema formal de gestión del conocimiento: al cerrar un proyecto, el saber técnico del equipo no siempre queda documentado y la operación depende de personas específicas. En este modelo, una organización es viable cuando conserva su identidad y puede seguir existiendo en un entorno que cambia (Sánchez Rueda, 1995). El escrito retoma la organización, el ODS 9 y la definición raíz de la Fase 2; describe el entorno, la operación y la gestión; identifica los cinco sistemas; y muestra que esas actividades forman una red de dependencias, no una secuencia lineal.",
    )
    body(
        document,
        "Ramírez Sánchez et al. (2009) presentan el MSV como un instrumento de la cibernética organizacional para estudiar, diagnosticar y proponer mecanismos de viabilidad. En esa lectura, la estructura que importa es el conjunto de comunicaciones que atenúan la variedad. Osorio Gómez (2007) plantea que los elementos de un sistema se interrelacionan para alcanzar un propósito común. En Nelumbo, ese propósito es que las lecciones aprendidas y las mejores prácticas queden disponibles para los proyectos siguientes.",
    )

    heading(document, "Contextualización de la organización")
    body(
        document,
        "Nelumbo Consultores es una empresa colombiana de consultoría tecnológica que opera de manera remota. Pertenece al sector de servicios de tecnologías de la información. Desarrolla software, asegura la calidad de las soluciones y acompaña la transformación digital de clientes del sector empresarial. Integra equipos de ingenieros de sistemas, analistas QA y desarrolladores, coordinados por líderes de proyecto y un director general. Sus áreas funcionales son la gestión de proyectos, el desarrollo de software, el QA y el soporte al cliente. Como sistema abierto, intercambia requerimientos, talento humano, herramientas, recursos e información técnica con sus clientes, con proveedores de tecnología, con entes reguladores y con el mercado de talento digital.",
    )
    body(
        document,
        "La problemática, retomada de la Fase 1 y precisada en la Fase 2, es la ausencia de un sistema formal de gestión del conocimiento. Cuando un proyecto finaliza, el conocimiento técnico del equipo no siempre queda documentado de manera estructurada. Esa dispersión genera dependencia de personas específicas y dificulta la escalabilidad. La retroalimentación vigente —encuestas de satisfacción, revisiones de sprint, informes de desempeño, tasa de defectos y tiempo de resolución— permite ajustar las entregas, pero no asegura que las lecciones aprendidas y las mejores prácticas queden disponibles para los proyectos siguientes.",
    )
    body(
        document,
        "La definición raíz de la Fase 2 describe el cambio esperado: que desarrolladores, analistas QA y líderes de proyecto, bajo la autoridad del director general, transformen ese saber disperso en lecciones y mejores prácticas disponibles en una base interna. El director general puede autorizar o detener la iniciativa. Los líderes deciden, en cada cierre, si el conocimiento queda documentado. La operación remota, la rotación del talento y la necesidad de articular gestión de proyectos, desarrollo, QA y soporte condicionan el sistema.",
    )
    body(
        document,
        "El desajuste es de variedad. El entorno —clientes, proveedores de tecnología, reguladores y mercado de talento— cambia más rápido que el canal que conserva lo aprendido. Cabrera-Moya y Prieto-Rodríguez (2022) recogen el criterio de Conant y Ashby: un regulador necesita al menos tanta variedad como el sistema que pretende regular. Si el saber vive en una persona, la salida de esa persona se lleva la capacidad de responder al siguiente proyecto. Los actores internos son el director general, los líderes de proyecto, los desarrolladores, los analistas QA y el soporte. Afuera están los clientes empresariales y el mercado de talento digital.",
    )
    body(
        document,
        "El Objetivo de Desarrollo Sostenible con el que se relaciona el caso es el 9: construir infraestructuras resilientes, promover la industrialización inclusiva y sostenible y fomentar la innovación (Naciones Unidas, s. f.). Una consultora que no retiene su conocimiento debilita la base con la que diseña soluciones y responde al mercado tecnológico. Conservar las lecciones y las mejores prácticas sostiene la capacidad de la firma para entregar y adaptarse, que es el aporte de Nelumbo a ese objetivo.",
    )
    body(
        document,
        "El MSV es pertinente porque muestra si el entorno, la operación y la gestión tienen canales para que el conocimiento circule (Cabrera-Moya y Prieto-Rodríguez, 2022). Sánchez Rueda (1995) lo propone como lectura de la estabilidad y de la adaptabilidad. Desde Ingeniería de Sistemas, la base interna es un canal de información: qué se atenúa al cierre, qué se amplifica al iniciar requerimientos y en qué momento la evaluación vuelve para corregir. Ramírez Sánchez et al. (2009) muestran, en la Universidad Libre, que ese diseño se hace con las personas que viven la operación. La observación recibida sobre el modelo conceptual de la Fase 2 pide, además, que los nodos queden interconectados en una red y no solo en una fila. Esa red se desarrolla después de identificar los cinco sistemas.",
    )

    heading(document, "Análisis de las tres entidades básicas del Modelo de Sistemas Viables")
    body(
        document,
        "Cabrera-Moya y Prieto-Rodríguez (2022) resumen el sistema viable en tres elementos: la operación, que produce el servicio; el metasistema de gestión, que presta recursos, normas y control; y el entorno, del que la organización depende y sobre el que también actúa. La Tabla 1 ubica esas tres entidades en Nelumbo y las relaciona con la gestión del conocimiento.",
        space_after=4,
    )
    caption(document, "Tabla 1", "Análisis de las tres entidades básicas del Modelo de Sistemas Viables en Nelumbo Consultores")
    add_table(
        document,
        ["Entidad", "Caracterización en la organización", "Contribución frente a la problemática"],
        [
            [
                "Entorno",
                "Clientes empresariales, proveedores de tecnología, entes reguladores y mercado de talento digital. Con ellos la empresa intercambia requerimientos, herramientas, normas e información técnica.",
                "Esos actores definen qué debe aprenderse y quién permanece en el equipo. Si una persona rota y el saber no está documentado, la capacidad de responder al siguiente cliente sale con ella.",
            ],
            [
                "Operación",
                "Desarrollo de software, aseguramiento de calidad y soporte al cliente, con el levantamiento de requerimientos, el diseño, las pruebas, la gestión de incidencias y la entrega. Cada proyecto es una unidad que produce el servicio y, al mismo tiempo, el conocimiento.",
                "Son quienes pueden identificar, registrar y consultar las lecciones durante el trabajo. Si el cierre solo entrega documentación técnica al cliente, la operación termina y el aprendizaje se queda en las personas.",
            ],
            [
                "Gestión",
                "Director general y líderes de proyecto. El director habilita las condiciones y puede sostener o detener la iniciativa. Los líderes coordinan el sprint, el cierre y la decisión de documentar.",
                "Hoy la gestión observa satisfacción, defectos y tiempos de resolución. Esos datos ajustan la entrega y no dicen si las lecciones circularon hacia el proyecto siguiente.",
            ],
        ],
        [2.6, 6.7, 6.7],
    )
    note(document, "Elaboración propia con base en la operación de Nelumbo Consultores y en Cabrera-Moya y Prieto-Rodríguez (2022).")
    body(
        document,
        "Las tres entidades se regulan entre sí. El entorno pide adaptación y, a la vez, mueve el talento. La operación genera el saber en el desarrollo, el QA y el soporte, y lo necesita otra vez al iniciar requerimientos y diseño. La gestión puede amplificar ese saber con un criterio de cierre y una base compartida, o atenuarlo si el informe solo mira la entrega. Cuando la gestión se queda en la satisfacción, los defectos y los tiempos, el entorno devuelve el costo en forma de dependencia de personas. Mirar las tres piezas juntas ubica la problemática en el acople, que es el punto de partida para leer los cinco sistemas.",
    )

    heading(document, "Representación gráfica del Modelo de Sistemas Viables")
    body(
        document,
        "La Figura 1 conserva la estructura de la plantilla de la guía: entorno, organización, procesos del sistema 1 y gestión con los sistemas 2, 3, 3*, 4 y 5. Los textos corresponden a Nelumbo y a la gestión del conocimiento. La página está en horizontal para que los recuadros de la plantilla se puedan leer.",
        space_after=2,
    )

    landscape = document.add_section(WD_ORIENT.LANDSCAPE)
    configure_section(landscape, landscape=True)
    caption(document, "Figura 1", "Modelo de Sistemas Viables aplicado a Nelumbo Consultores")
    picture_paragraph = document.add_paragraph()
    picture_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    picture_paragraph.paragraph_format.space_after = Pt(2)
    run = picture_paragraph.add_run()
    picture = run.add_picture(str(PNG), width=Inches(9.6))
    set_alt(
        picture,
        "Diagrama del Modelo de Sistemas Viables de Nelumbo Consultores: entorno con clientes, talento, proveedores y reguladores; procesos de desarrollo, QA, soporte, requerimientos, cierre y lecciones; y gestión con director general, mercado, informes, líderes de proyecto y verificación del registro.",
    )
    note(
        document,
        "La figura mantiene la estructura de la plantilla de la actividad. Elaboración propia a partir de Cabrera-Moya y Prieto-Rodríguez (2022) y del análisis de la Tabla 1.",
    )

    portrait = document.add_section(WD_ORIENT.PORTRAIT)
    configure_section(portrait, landscape=False)

    heading(document, "Los cinco sistemas del Modelo de Sistemas Viables")
    body(
        document,
        "El MSV separa la organización en cinco funciones que tienen que conversar. El sistema 1 es la operación que produce aquello que la empresa es. En una empresa de software son los equipos que diseñan, construyen y prueban el producto del cliente. Cada una tiene gestión propia y, cuando está bien armada, decide lo cotidiano sin pedir permiso para cada caso. Cabrera-Moya y Prieto-Rodríguez (2022) las describen como nodos con autonomía responsable: el metasistema no las sustituye; les presta recursos, normas y rendición de cuentas. Cada sistema 1 está en contacto directo con su nicho, y por eso es el lugar donde la variedad del entorno se siente primero.",
    )
    body(
        document,
        "El sistema 2 evita que esas operaciones se estorben. En la lectura de Cabrera-Moya y Prieto-Rodríguez (2022), amortigua oscilaciones mediante lenguajes compartidos, estándares, programas de trabajo y sistemas de información. Sin ese acuerdo, un equipo cierra un incremento mientras otro todavía no tiene criterio de aceptación. El conjunto se descoordina aunque cada equipo esté ocupado. El sistema 3 mira el adentro y el ahora. Reparte recursos, pide cuentas y busca que las operaciones, juntas, rindan más que la suma de lo que harían aisladas. Junto a él trabaja el sistema 3*, que no se conforma con el informe del responsable de la operación: va a la fuente, de manera esporádica, y recoge la información que el canal formal filtra. Si ese canal no existe, la dirección conoce el problema cuando el problema ya salió al entorno.",
    )
    body(
        document,
        "El sistema 4 mira el afuera y el mañana. Vigila cambios que pueden favorecer o golpear la viabilidad, mantiene un modelo del entorno y propone adaptación. Cabrera-Moya y Prieto-Rodríguez (2022) lo tratan como un motor de aprendizaje. Si corre más que el sistema 3, la empresa promete capacidades que la operación todavía no sostiene. Si el sistema 3 lo tapa, la empresa cumple lo de hoy y pierde el mercado. El sistema 5 cierra la identidad. Define las políticas y el modo de actuar, y equilibra el presente del sistema 3 con el futuro del sistema 4. Ramírez Sánchez et al. (2009) recuerdan que esa identidad se administra, y que la estructura real son los mecanismos de comunicación.",
    )
    body(
        document,
        "Los cinco sistemas se regulan por bucles, no por una fila del 1 al 5. El entorno informa al sistema 1 y al sistema 4. El sistema 2 sincroniza al 1. El sistema 3 negocia recursos con el 1. El sistema 3* contrasta el informe. El sistema 5 mantiene el balance entre cohesión y adaptación. Una organización es viable cuando esos bucles alcanzan para la variedad del entorno y puede cambiar la forma de operar sin dejar de ser ella misma (Sánchez Rueda, 1995). En la Universidad Libre, el mismo modelo sirvió para revisar autonomía, canales de información y mecanismos de adaptación con quienes hacían el trabajo (Ramírez Sánchez et al., 2009). Esa lógica se traslada a Nelumbo en la Tabla 2: la función se asigna por lo que cada instancia hace.",
    )

    heading(document, "Identificación y justificación de los cinco sistemas")
    caption(document, "Tabla 2", "Identificación y justificación de los cinco sistemas del Modelo de Sistemas Viables en Nelumbo Consultores")
    add_table(
        document,
        ["Sistema", "Elemento identificado en la organización", "Justificación"],
        [
            [
                "Sistema 1 – Procesos",
                "Desarrollo de software, QA y soporte al cliente, junto con el levantamiento de requerimientos, el diseño, las pruebas, las incidencias y la entrega.",
                "Producen el servicio de la consultora y, en ese mismo trabajo, el conocimiento técnico. Sin el registro de lo aprendido, el sistema 1 entrega el proyecto y deja el saber en las personas.",
            ],
            [
                "Sistema 2 – Coordinación",
                "Líderes de proyecto, revisiones de sprint y plataformas de gestión que los equipos ya utilizan.",
                "Sincronizan desarrollo, QA y soporte. En el cierre pueden acordar qué lecciones se conservan y, al iniciar un proyecto, incluir la consulta de la base. Ese lenguaje común amortigua que cada equipo cierre a su manera.",
            ],
            [
                "Sistema 3 – Cohesión",
                "Director general, mediante los informes de desempeño por proyecto.",
                "Habilita personas y condiciones, y pide cuentas del conjunto. Hoy esas cuentas cubren satisfacción, tasa de defectos y tiempo de resolución. Miran el adentro y el ahora de la entrega, no la circulación del conocimiento.",
            ],
            [
                "Sistema 3* – Auditoría",
                "Verificación del registro en la base, hecha por alguien distinto de quien declara el cierre. Hoy esa verificación no está separada de la revisión de sprint.",
                "El sistema 3* contrasta en la fuente si la lección que el informe da por registrada existe y puede consultarse. La revisión de sprint, hecha por el mismo equipo, pertenece al sistema 2.",
            ],
            [
                "Sistema 4 – Inteligencia",
                "Lectura del mercado de talento digital, de los proveedores de tecnología y de las demandas de transformación digital de los clientes. La ejercen el director general y los líderes cuando deciden herramientas y contratación.",
                "Traduce el entorno en opciones de adaptación. Esa lectura depende de que el saber de los proyectos esté en la organización. Si permanece en las personas, la rotación debilita la inteligencia.",
            ],
            [
                "Sistema 5 – Política",
                "Director general, con la autoridad para autorizar o detener la base de conocimiento y con la visión de que el saber generado en los proyectos es un recurso de la organización.",
                "Cierra la identidad: la firma se sostiene si puede entregar y adaptarse. Esa política equilibra la entrega de hoy con la disponibilidad del saber para los proyectos futuros.",
            ],
        ],
        [3.2, 6.4, 6.4],
    )
    note(document, "Elaboración propia. La asignación sigue la función de cada sistema descrita por Cabrera-Moya y Prieto-Rodríguez (2022), aplicada a los actores descritos en la Fase 2.")

    heading(document, "Red de dependencias entre las actividades del conocimiento")
    body(
        document,
        "En la Fase 2 el modelo conceptual ordenó las actividades en una secuencia: identificar las lecciones al cierre, documentarlas, organizarlas en la base, consultarlas al iniciar requerimientos y diseño, y evaluar si se registran y se consultan, con una flecha de retroalimentación al final. La observación del tutor pide interconectar esos nodos en una red dinámica, con varias dependencias. El MSV sirve para ese paso porque sus sistemas no se recorren en fila: cada uno depende de los demás y del entorno (Cabrera-Moya y Prieto-Rodríguez, 2022). Osorio Gómez (2007) recuerda que los elementos se relacionan para un propósito común. En Nelumbo, el propósito es que el conocimiento del proyecto quede disponible para el siguiente.",
    )
    body(
        document,
        "La Figura 2 dibuja esas dependencias. Identificar lecciones no depende solo del cierre. También entra lo que el QA ve en los defectos y lo que el soporte atiende en las incidencias. Documentar depende de esa identificación, del formato que acuerdan los líderes en la revisión de sprint y del tiempo que habilita el director general. La base depende de lo documentado y de las plataformas que los equipos ya usan. Consultar depende de que la base exista y de que los líderes la incluyan al iniciar requerimientos y diseño. Evaluar depende de los informes de desempeño y de la evidencia que haya en la base. Su resultado vuelve a la identificación, a los líderes y a la decisión del director de sostener o detener la iniciativa.",
    )
    caption(document, "Figura 2", "Red de dependencias de la gestión del conocimiento en Nelumbo Consultores")
    red = document.add_paragraph()
    red.alignment = WD_ALIGN_PARAGRAPH.CENTER
    red.paragraph_format.space_after = Pt(2)
    red_run = red.add_run()
    red_picture = red_run.add_picture(str(PNG_RED), width=Cm(15.4))
    set_alt(
        red_picture,
        "Red de dependencias: cierre, QA y soporte alimentan la identificación de lecciones; los líderes aportan criterio y formato; el director autoriza; la base se consulta al diseñar; los informes y la base alimentan la evaluación, que ajusta la identificación y la decisión de continuar.",
    )
    note(
        document,
        "Las flechas continuas unen actividades de la operación. Las punteadas cierran la autorización del director, la retroalimentación de la evaluación y el efecto del mercado de talento. Elaboración propia a partir de la Fase 2 y de la observación del tutor sobre el modelo conceptual.",
    )
    body(
        document,
        "Esa red cambia la lectura de la viabilidad. Un formato de cierre, por sí solo, no conserva el conocimiento. Hace falta que QA, soporte, líderes, informes y dirección queden en el mismo circuito. El sistema 3* entra en ese cruce: alguien distinto de quien declara el cierre contrasta si el registro existe en la base y puede consultarse. Sin ese contraste, los indicadores actuales siguen mirando la entrega. El mercado de talento cierra el circuito por fuera: si la persona rota, el saber que no quedó escrito deja de estar disponible para adaptarse.",
    )

    heading(document, "Evaluación de la viabilidad organizacional")
    sub = document.add_paragraph()
    sub.paragraph_format.space_before = Pt(6)
    sub.paragraph_format.space_after = Pt(4)
    sub.paragraph_format.line_spacing = 1.15
    add_text(sub, "Fortalezas y oportunidades de mejora en la interacción de los cinco sistemas", size=12, bold=True, color=NAVY)
    body(
        document,
        "Nelumbo ya distingue las funciones del modelo, con los nombres de su operación. El sistema 1 está en desarrollo, QA y soporte. El sistema 2 está en los líderes de proyecto, las revisiones de sprint y las plataformas de gestión. El sistema 3 está en el director general y en los informes de satisfacción, defectos y tiempos. El sistema 4 aparece cuando la dirección y los líderes leen el mercado de talento, los proveedores de tecnología y las demandas de los clientes. El sistema 5 es la autoridad del director para sostener la identidad de una firma que entrega y se adapta. La fortaleza es que los roles y los procesos ya existen: cierre, sprint, requerimientos e informes. La oportunidad está en las dependencias que hoy no se cruzan. El sistema 2 coordina la entrega y no obliga a que el cierre, el QA y el soporte alimenten una misma base. El sistema 3 mide la entrega y no la consulta de lo aprendido. El sistema 3* no está separado de la revisión que hace el mismo equipo. El sistema 4 queda expuesto a la rotación, porque la inteligencia práctica vive en las personas. El bucle se corta al final del proyecto.",
    )
    sub = document.add_paragraph()
    sub.paragraph_format.space_before = Pt(4)
    sub.paragraph_format.space_after = Pt(4)
    sub.paragraph_format.line_spacing = 1.15
    add_text(sub, "Fortalecimiento de los sistemas, la problemática y el ODS 9", size=12, bold=True, color=NAVY)
    body(
        document,
        "Fortalecer la red mejora la respuesta al problema y el aporte al ODS 9. El criterio mínimo de cierre, acordado por los líderes, sube la variedad del sistema 2: QA, soporte y desarrollo dejan lección en el mismo formato. Incluir la consulta al iniciar requerimientos y diseño devuelve ese saber al sistema 1 antes de repetir el trabajo. Sumar a los informes el dato de si la lección se registró y se consultó le da al sistema 3 una cuenta distinta de la tasa de defectos. Una verificación breve, hecha por alguien que no declaró el cierre, abre el canal del sistema 3*. La decisión del director de sostener la base equilibra el sistema 5: la entrega de hoy y la capacidad de los proyectos futuros. Cabrera-Moya y Prieto-Rodríguez (2022) recuerdan que el regulador necesita tanta variedad como aquello que regula. El ODS 9 pide capacidad tecnológica que quede instalada (Naciones Unidas, s. f.). En Nelumbo esa capacidad es el conocimiento con el que diseña soluciones. Si las lecciones circulan entre desarrollo, QA y soporte, la innovación de la firma no depende de que una persona siga en el equipo. Desde Ingeniería de Sistemas, el fortalecimiento es el diseño de ese canal: qué se registra al cierre, qué se consulta al empezar y qué informe devuelve la señal para corregir.",
    )

    heading(document, "Conclusiones")
    body(
        document,
        "El Modelo de Sistemas Viables permite leer la situación de Nelumbo como un corte en los canales de regulación. La firma ya entrega, mide defectos y revisa el sprint. El conocimiento del proyecto no entra en ese circuito, y por eso la operación sigue dependiendo de personas específicas.",
    )
    body(
        document,
        "La observación sobre el modelo conceptual de la Fase 2 queda recogida en la red de la Figura 2. Identificar, documentar, consultar y evaluar no avanzan en una sola fila. Cada actividad depende del cierre, del QA, del soporte, de los líderes, de los informes y de la decisión del director. Esa red es la condición de viabilidad: la organización puede adaptarse si el saber permanece cuando las personas cambian.",
    )
    body(
        document,
        "Los cambios ya planteados en la Fase 2 —formato de lecciones, base interna, consulta al diseñar e indicador en los informes— se sostienen si el sistema 5 los autoriza, el sistema 2 los sincroniza y el sistema 3* verifica el registro. Desde la Ingeniería de Sistemas, eso diseña el canal de información. Desde el ODS 9, conserva la capacidad tecnológica con la que Nelumbo responde a sus clientes.",
    )

    heading(document, "Referencias")
    reference(
        document,
        [
            ("Cabrera-Moya, D. R. R. y Prieto-Rodríguez, G. A. (2022). On the need for structuring of the Integrated Public Transport System-IPTS of Bogotá, Colombia as a viable system. ", False),
            ("Revista de Investigaciones Universidad del Quindío, 34", True),
            ("(2), 440-461. https://doi.org/10.33975/riuq.vol34n2.1070", False),
        ],
    )
    reference(
        document,
        [
            ("Naciones Unidas. (s. f.). ", False),
            ("Objetivo 9: Construir infraestructuras resilientes, promover la industrialización sostenible y fomentar la innovación", True),
            (". https://www.un.org/sustainabledevelopment/es/infrastructure/", False),
        ],
    )
    reference(
        document,
        [
            ("Osorio Gómez, J. C. (2007). ", False),
            ("Introducción al pensamiento sistémico", True),
            (". Programa Editorial Universidad del Valle. https://elibro-net.bibliotecavirtual.unad.edu.co/es/ereader/unad/129056?page=10", False),
        ],
    )
    reference(
        document,
        [
            ("Ramírez Sánchez, M., Medina García, V. H. y de la Fuente García, D. (2009). Mejoramiento de gestión universitaria basado en el Modelo de Sistema Viable. Caso de estudio: Universidad Libre. ", False),
            ("Ingeniería, 14", True),
            ("(2), 59-66. https://revistas.udistrital.edu.co/index.php/reving/article/view/2380", False),
        ],
    )
    reference(
        document,
        [
            ("Sánchez Rueda, N. (1995). El modelo de sistema viable: un instrumento para la organización efectiva. ", False),
            ("Revista Escuela de Administración de Negocios", True),
            (", (25-26), 5-14. https://journal.universidadean.edu.co/index.php/Revista/article/view/1155", False),
        ],
    )
    document.save(DOCX)


FORO_TEXT = """FORO 1. Viabilidad en Debate
Publicar este texto como avance. El foro cierra el domingo 22 de noviembre de 2026.

Cordial saludo, tutor y compañeros.

Retomo a Nelumbo Consultores, consultora tecnológica de operación remota, y la problemática de la Fase 2: al cerrar un proyecto, el conocimiento técnico no siempre queda documentado y la operación depende de personas específicas. El Modelo de Sistemas Viables permite ver si el entorno, la operación y la gestión tienen canales para que ese saber circule (Cabrera-Moya y Prieto-Rodríguez, 2022).

En el entorno están los clientes empresariales, los proveedores de tecnología, los entes reguladores y el mercado de talento. Si una persona rota, el saber no escrito se va con ella. La operación la hacen desarrollo, QA y soporte: ahí se produce el conocimiento, en requerimientos, pruebas, incidencias y entrega. La gestión la hacen el director general y los líderes de proyecto. Hoy los informes miran satisfacción, defectos y tiempos de resolución, y no dicen si las lecciones quedaron disponibles para el proyecto siguiente.

También recojo la observación sobre el modelo conceptual. Las actividades de identificar, documentar, consultar y evaluar no pueden quedar en una sola fila: el cierre, el QA y el soporte alimentan la identificación; los líderes aportan el formato; y la evaluación tiene que volver al inicio y a la decisión del director.

Quedo atento a la retroalimentación.

---

FORO 2. Arquitectura Viable

Cordial saludo.

El Modelo de Sistemas Viables separa cinco funciones que dependen unas de otras. El sistema 1 produce lo que la organización es y toca su entorno; el metasistema no lo reemplaza, le presta recursos, normas y cuentas (Cabrera-Moya y Prieto-Rodríguez, 2022). El sistema 2 amortigua los choques entre operaciones con un lenguaje común y un sistema de información. El sistema 3 mira el adentro y el ahora. El sistema 3* no se queda con el informe: contrasta en la fuente. El sistema 4 mira el afuera y el mañana. El sistema 5 cierra la identidad y equilibra el presente con el futuro (Sánchez Rueda, 1995).

En Nelumbo el sistema 1 es desarrollo, QA y soporte. El 2 son los líderes de proyecto y la revisión de sprint. El 3 es el director con los informes de satisfacción, defectos y tiempos. El 3*, que hoy no está separado, sería verificar si la lección quedó registrada. El 4 es la lectura del mercado de talento y de la tecnología. El 5 es la autoridad del director para sostener la base de conocimiento. El punto frágil es que el saber se corta al cierre del proyecto y no vuelve, por varias vías, al proyecto siguiente.

---

CÓMO COMENTAR A DOS COMPAÑEROS

1. “En tu entorno listas varios actores. Conviene decir cuál de ellos le mete más variedad a la operación y si la gestión tiene un canal para enterarse a tiempo. Si el canal es solo el informe final, el sistema 3* queda corto.”

2. “Vi una secuencia de actividades. El MSV pide también las dependencias cruzadas: qué otra área alimenta esa actividad y a quién vuelve el resultado. Una sola flecha de retroalimentación al final deja el modelo en fila.”
"""


def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    if not TEMPLATE.exists():
        raise SystemExit("No está la plantilla en /tmp/plantilla.pptx")
    render_figure()
    render_network()
    build_document()
    FORO.write_text(FORO_TEXT, encoding="utf-8")
    subprocess.run(
        [
            "soffice",
            "--headless",
            "--norestore",
            "-env:UserInstallation=file:///tmp/lo-profile-fase3-doc",
            "--convert-to",
            "pdf",
            "--outdir",
            str(ROOT),
            str(DOCX),
        ],
        check=True,
        capture_output=True,
    )
    print("OK", DOCX, PDF, PPTX, PNG, FORO)


if __name__ == "__main__":
    main()
