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
    set_para_text(env_ps[1], "Clientes de varios sectores", size=1100)
    cursor = env_ps[1]
    for line in (
        "Usuarios del software",
        "Contratos y datos",
        "Cambio tecnológico",
    ):
        cursor = insert_after(entorno, cursor, line, 1100)

    org = shape_by_name(tree, "Rectángulo 5")
    org_ps = paragraphs(org)
    set_para_text(
        org_ps[3],
        "Nelumbo Consultores S. A. S., Cúcuta. Software a la medida.",
        size=1100,
    )
    problem = insert_after(
        org,
        org_ps[-1],
        "La calidad se acuerda tarde entre células que entregan a la vez. El defecto lo detecta el cliente.",
        1100,
    )
    problem_pr = problem.find(A + "pPr")
    if problem_pr is None:
        problem_pr = ET.Element(A + "pPr")
        problem.insert(0, problem_pr)
    problem_pr.set("algn", "l")

    processes = {
        "Rectángulo 25": "Desarrollo web",
        "Rectángulo 39": "App móvil",
        "Rectángulo 43": "Datos",
        "Rectángulo 45": "Diseño UX",
        "Rectángulo 41": "Analítica",
        "Rectángulo 37": "Pruebas",
    }
    for name, label in processes.items():
        sp = shape_by_name(tree, name)
        set_para_text(paragraphs(sp)[0], label, size=900, bold=True)

    systems = {
        "Rectángulo 47": "Dirección general",
        "Rectángulo 57": "Mercado y tecnología",
        "Rectángulo 59": "Dirección de operaciones",
        "Rectángulo 63": "Proyectos y tablero",
        "Rectángulo 61": "Muestreo de evidencias",
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
        "El entorno trae clientes, normas y tecnologías distintas. El sistema 1 construye y prueba; "
        "el 2 fija un mismo criterio de terminado; el 3 reparte personas y plazos; el 3* mira si la prueba quedó hecha; "
        "el 4 lee el mercado y el 5 cuida la identidad. Si el 3* llega tarde, el defecto lo encuentra el cliente.",
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


def body(document, text, space_after=8, first_line=None):
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
    add_text(subtitle, "Aplicación del Modelo de Sistemas Viables a Nelumbo Consultores", size=12, italic=True, color=NAVY)

    for label, value in (
        ("Nombre del estudiante: ", "Jhon Carlos Acevedo Mendoza"),
        ("Tutor: ", "Víctor Hugo Mercado Ramos"),
        ("Universidad: ", "Universidad Nacional Abierta y a Distancia"),
        ("Unidad gestora: ", "Escuela de Ciencias Básicas, Tecnología e Ingeniería"),
        ("Programa: ", "Ingeniería de Sistemas"),
        ("Curso: ", "Teoría de Sistemas en las Organizaciones"),
        ("Código: ", "204016"),
        ("Lugar y fecha: ", "Cúcuta, 17 de noviembre de 2026"),
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
        "Este documento aplica el Modelo de Sistemas Viables (MSV) a Nelumbo Consultores, empresa de desarrollo de software con sede en Cúcuta, para examinar si puede sostener la calidad cuando varias células entregan producto al mismo tiempo. En este modelo, una organización es viable cuando conserva su identidad y sigue existiendo en un entorno que cambia (Sánchez Rueda, 1995). El escrito presenta la organización, la problemática y el Objetivo de Desarrollo Sostenible 9; describe el entorno, la operación y la gestión; explica los cinco sistemas; muestra la figura del modelo aplicado al caso y cierra con fortalezas y oportunidades de fortalecimiento.",
    )
    body(
        document,
        "El pensamiento sistémico permite leer el defecto de software como una señal de los canales con los que la empresa se regula. Ramírez Sánchez et al. (2009) presentan el MSV como un instrumento de la cibernética organizacional para estudiar, diagnosticar y proponer mecanismos de viabilidad. En esa lectura, la estructura que importa es el conjunto de comunicaciones que atenúan la variedad.",
    )

    heading(document, "Contextualización de la organización")
    body(
        document,
        "Nelumbo Consultores S. A. S. desarrolla software a la medida desde Cúcuta. En su presentación pública se define por alinear la tecnología con la visión de negocio del cliente. Ofrece diseño de experiencia, arquitectura, desarrollo web y móvil, aseguramiento de calidad, analítica, servicios en la nube y dirección de proyectos. Los sectores que enuncia son, entre otros, aseguradoras, constructoras, comercio, dispositivos médicos y gestión organizacional (Nelumbo Consultores, s. f.-a). La misión publicada es consolidar soluciones tecnológicas alineadas con los clientes actuales y potenciales. La visión es sostenerse como referente nacional e internacional, adaptándose a las condiciones del mercado (Nelumbo Consultores, s. f.-b).",
    )
    body(
        document,
        "La operación se organiza en células que combinan análisis de negocio, diseño, desarrollo, pruebas y despliegue. La dirección general fija la identidad. La dirección de operaciones reparte personas y plazos. La dirección de proyectos sincroniza el día a día. Este análisis se sitúa en el aseguramiento de calidad, porque allí se hace visible si una entrega está realmente lista. Conozco ese punto desde la práctica de pruebas: el defecto que no quedó escrito en el acuerdo de aceptación reaparece cuando el cliente revisa.",
    )
    body(
        document,
        "La problemática priorizada es la coordinación tardía de la calidad entre células que trabajan en paralelo. Cada cliente llega con su lenguaje, su plazo y su criterio de aceptación. Negocio, desarrollo y pruebas pueden cerrar significados distintos de la palabra terminado. El defecto no se ve primero en el tablero. Se ve en la revisión del cliente o cuando el producto ya está en uso. La causa está en el desajuste de variedad. El entorno —varios clientes, normas sobre datos personales, cambios de alcance y tecnologías nuevas— se mueve con más estados posibles que los canales con los que la empresa se regula. Cabrera-Moya y Prieto-Rodríguez (2022) recogen el criterio de Conant y Ashby: un regulador necesita al menos tanta variedad como el sistema que pretende regular.",
    )
    body(
        document,
        "En la operación se observan tres condiciones que alimentan ese desajuste. El criterio de aceptación queda repartido en comentarios y conversaciones, y no en un acuerdo visible para las tres disciplinas. La prueba entra cuando el desarrollo ya considera cerrado el incremento, de modo que corregir consume el plazo. Y falta una mirada distinta de quien ejecutó la prueba, que muestree evidencias antes del paso a producción. Los actores internos son las células de entrega, los analistas de negocio, los analistas de calidad, la dirección de proyectos y la dirección de operaciones. Afuera están el cliente que contrata y la persona que usa el software. La consecuencia interna es retrabajo y presión sobre la fecha. La consecuencia externa es el desgaste de la promesa pública de entregar un producto listo, con calidad comprobada, en el tiempo acordado.",
    )
    body(
        document,
        "El Objetivo de Desarrollo Sostenible con el que se relaciona el caso es el 9: construir infraestructuras resilientes, promover la industrialización sostenible y fomentar la innovación (Naciones Unidas, s. f.). La meta 9.5 pide mejorar la capacidad tecnológica de los sectores productivos, y la meta 9.b pide apoyar el desarrollo tecnológico en los países en desarrollo. Nelumbo construye, desde una ciudad fronteriza, piezas de esa infraestructura para salud, seguros, obra y comercio. Si el software sale inestable, el aporte al objetivo se queda en el anuncio de la innovación.",
    )
    body(
        document,
        "El MSV es pertinente porque muestra el acople entre entorno, operación y gestión. El procedimiento de pruebas queda dentro de ese acople (Cabrera-Moya y Prieto-Rodríguez, 2022). Sánchez Rueda (1995) lo propone como lectura de la estabilidad y de la adaptabilidad, que son las dos condiciones de una organización efectiva. Desde Ingeniería de Sistemas, la misma problemática se puede tratar como diseño de canales de información: qué se atenúa, qué se amplifica y en qué momento la retroalimentación alcanza para corregir. Ramírez Sánchez et al. (2009), en la Universidad Libre, muestran que ese diseño se hace con las personas que viven la operación.",
    )

    heading(document, "Análisis de las tres entidades básicas del Modelo de Sistemas Viables")
    body(
        document,
        "Cabrera-Moya y Prieto-Rodríguez (2022) resumen el sistema viable en tres elementos: la operación, que produce el servicio; el metasistema de gestión, que presta recursos, normas y control; y el entorno, del que la organización depende y sobre el que también actúa. La Tabla 1 ubica esas tres entidades en Nelumbo y las relaciona con la problemática de la calidad tardía.",
        space_after=4,
    )
    caption(document, "Tabla 1", "Análisis de las tres entidades básicas del Modelo de Sistemas Viables en Nelumbo Consultores")
    add_table(
        document,
        ["Entidad", "Caracterización en la organización", "Contribución frente a la problemática"],
        [
            [
                "Entorno",
                "Clientes de seguros, construcción, comercio, salud y gestión organizacional; usuarios finales del software; contratos y normas sobre datos personales; competidores y tecnologías emergentes, entre ellas la nube, la analítica y los agentes de inteligencia artificial (Nelumbo Consultores, s. f.-a).",
                "Esos actores cambian el alcance, el plazo y el criterio de aceptación. Si la empresa los lee tarde, la calidad se negocia cuando el producto ya está construido.",
            ],
            [
                "Operación",
                "Células que desarrollan software web, aplicaciones móviles, datos e integraciones, diseño de experiencia y analítica, junto con las pruebas del incremento. Cada célula tiene una gestión local de proyecto.",
                "Son quienes construyen el software y quienes pueden ver el defecto mientras corregirlo todavía cabe en el plazo. Si la prueba entra después del cierre, la operación entrega un terminado que el cliente no reconoce.",
            ],
            [
                "Gestión",
                "Dirección general, dirección de operaciones, dirección de proyectos y el tablero de seguimiento compartido por negocio, desarrollo y pruebas.",
                "Reparte personas y plazos, sincroniza células y sostiene la promesa de calidad. Cuando pesa más la fecha que la evidencia de prueba, la gestión conoce el problema por el reclamo del cliente.",
            ],
        ],
        [2.6, 6.7, 6.7],
    )
    note(document, "Elaboración propia con base en la operación de Nelumbo Consultores y en Cabrera-Moya y Prieto-Rodríguez (2022).")
    body(
        document,
        "Las tres entidades se regulan entre sí. El entorno le mete variedad a la operación: cada cliente trae reglas y urgencias propias. La operación absorbe esa variedad cuando negocio, desarrollo y pruebas comparten el criterio de aceptación antes de construir. La gestión amplifica ese acuerdo, lo hace visible en el tablero, y atenúa el ruido de plazos que compiten entre células. Si la gestión se queda en el reporte de la fecha, el entorno devuelve el defecto por la vía del cliente. Mirar las tres piezas juntas ubica la problemática en el acople, que es el punto de partida para leer después los cinco sistemas.",
    )

    heading(document, "Representación gráfica del Modelo de Sistemas Viables")
    body(
        document,
        "La Figura 1 conserva la estructura de la plantilla de la guía: entorno, organización, procesos del sistema 1 y gestión con los sistemas 2, 3, 3*, 4 y 5. Los textos corresponden al caso de Nelumbo y a la problemática de la calidad tardía. La página está en horizontal para que los recuadros de la plantilla se puedan leer.",
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
        "Diagrama del Modelo de Sistemas Viables de Nelumbo Consultores: entorno con clientes, contratos y tecnología; seis procesos del sistema 1; y gestión con política, inteligencia, cohesión, coordinación y auditoría.",
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
        "El MSV separa la organización en cinco funciones que tienen que conversar. El sistema 1 es la operación que produce aquello que la empresa es. En una empresa de software son las células que diseñan, construyen y prueban el producto del cliente. Cada una tiene gestión propia y, cuando está bien armada, decide lo cotidiano sin pedir permiso para cada caso. Cabrera-Moya y Prieto-Rodríguez (2022) las describen como nodos con autonomía responsable: el metasistema no las sustituye; les presta recursos, normas y rendición de cuentas. Cada sistema 1 está en contacto directo con su nicho, y por eso es el lugar donde la variedad del entorno se siente primero.",
    )
    body(
        document,
        "El sistema 2 evita que esas operaciones se estorben. En la lectura de Cabrera-Moya y Prieto-Rodríguez (2022), amortigua oscilaciones mediante lenguajes compartidos, estándares, programas de trabajo y sistemas de información. Sin ese acuerdo, una célula cierra un incremento mientras otra todavía no tiene criterio de aceptación. El conjunto se descoordina aunque cada equipo esté ocupado. El sistema 3 mira el adentro y el ahora. Reparte recursos, pide cuentas y busca que las operaciones, juntas, rindan más que la suma de lo que harían aisladas. Junto a él trabaja el sistema 3*, que no se conforma con el informe del responsable de la operación: va a la fuente, de manera esporádica, y recoge la información que el canal formal filtra. Si ese canal no existe, la dirección conoce el problema cuando el problema ya salió al entorno.",
    )
    body(
        document,
        "El sistema 4 mira el afuera y el mañana. Vigila cambios que pueden favorecer o golpear la viabilidad, mantiene un modelo del entorno y propone adaptación. Cabrera-Moya y Prieto-Rodríguez (2022) lo tratan como un motor de aprendizaje. Si corre más que el sistema 3, la empresa promete capacidades que la operación todavía no sostiene. Si el sistema 3 lo tapa, la empresa cumple lo de hoy y pierde el mercado. El sistema 5 cierra la identidad. Define las políticas y el modo de actuar, y equilibra el presente del sistema 3 con el futuro del sistema 4. Ramírez Sánchez et al. (2009) recuerdan que esa identidad se administra, y que la estructura real son los mecanismos de comunicación.",
    )
    body(
        document,
        "Los cinco sistemas se regulan por bucles. El entorno informa al sistema 1 y al sistema 4. El sistema 2 sincroniza al 1. El sistema 3 negocia recursos con el 1. El sistema 3* contrasta el informe. El sistema 5 mantiene el balance entre cohesión y adaptación. Una organización es viable cuando esos bucles alcanzan para la variedad que el entorno le presenta, y cuando puede cambiar la forma de operar sin dejar de ser ella misma (Sánchez Rueda, 1995). En la Universidad Libre, el mismo modelo sirvió para revisar autonomía, canales de información y mecanismos de adaptación, con la participación de quienes hacían el trabajo (Ramírez Sánchez et al., 2009). Esa lógica se traslada a Nelumbo en la Tabla 2: la función se asigna por lo que cada instancia hace, no por el nombre del cargo.",
    )

    heading(document, "Identificación y justificación de los cinco sistemas")
    caption(document, "Tabla 2", "Identificación y justificación de los cinco sistemas del Modelo de Sistemas Viables en Nelumbo Consultores")
    add_table(
        document,
        ["Sistema", "Elemento identificado en la organización", "Justificación"],
        [
            [
                "Sistema 1 – Procesos",
                "Células de desarrollo web, aplicaciones móviles, datos e integraciones, diseño de experiencia y analítica, con las pruebas del incremento dentro de la entrega.",
                "Producen el servicio que la misión enuncia: software alineado con el negocio del cliente. La prueba hace parte de esa producción. Sin ella, el sistema 1 entrega actividad y no el producto prometido.",
            ],
            [
                "Sistema 2 – Coordinación",
                "Dirección de proyectos, seguimiento del trabajo y tablero compartido, con una definición de terminado común a negocio, desarrollo y pruebas.",
                "Sincroniza células que avanzan en paralelo y reduce el choque por personas, ambientes y criterios distintos. Es el mecanismo que amortigua la oscilación entre equipos.",
            ],
            [
                "Sistema 3 – Cohesión",
                "Dirección de operaciones.",
                "Asigna personas, cuida la carga y pide cuentas del plazo y del alcance sobre el conjunto de células. Mira el adentro y el ahora, que es la función de cohesión.",
            ],
            [
                "Sistema 3* – Auditoría",
                "Muestreo de evidencias de prueba, hecho por alguien que no ejecutó el caso, antes del paso a producción. Hoy ese muestreo es irregular.",
                "No reemplaza la prueba del sistema 1. Contrasta en la fuente si lo que el informe llama terminado tiene evidencia. Cuando no ocurre, el cliente queda haciendo de auditor.",
            ],
            [
                "Sistema 4 – Inteligencia",
                "Lectura comercial y técnica del mercado: los sectores que la empresa ya atiende y las capacidades que ya ofrece, como nube, analítica y agentes de inteligencia artificial.",
                "Traduce cambios del entorno en opciones de adaptación. Si esa lectura no se contrasta con la capacidad del sistema 3, la oferta crece más rápido que la calidad.",
            ],
            [
                "Sistema 5 – Política",
                "Dirección general, a partir de la misión, la visión y la promesa pública de cumplir lo acordado con calidad comprobada (Nelumbo Consultores, s. f.-b).",
                "Fija qué se conserva cuando hay que elegir entre un plazo, una tecnología nueva y la calidad. Es el cierre de identidad del sistema.",
            ],
        ],
        [3.2, 6.4, 6.4],
    )
    note(document, "Elaboración propia. La asignación sigue la función de cada sistema descrita por Cabrera-Moya y Prieto-Rodríguez (2022), aplicada a la operación de Nelumbo Consultores.")

    heading(document, "Evaluación de la viabilidad organizacional")
    sub = document.add_paragraph()
    sub.paragraph_format.space_before = Pt(6)
    sub.paragraph_format.space_after = Pt(4)
    sub.paragraph_format.line_spacing = 1.15
    add_text(sub, "Fortalezas y oportunidades de mejora en la interacción de los cinco sistemas", size=12, bold=True, color=NAVY)
    body(
        document,
        "En Nelumbo las cinco funciones ya se distinguen, aunque nadie las llame así. Hay células que entregan, jefes de proyecto con un tablero común, una dirección de operaciones que reparte gente y plazos, una oferta que ya incluye nube, analítica y agentes de inteligencia artificial, y una dirección general que sostiene una misión pública: tecnología alineada con el negocio del cliente y entrega con calidad comprobada (Nelumbo Consultores, s. f.-b). La fortaleza está en que la identidad, la operación y la lectura del mercado existen. La oportunidad está en el cruce. El sistema 2 todavía permite que terminado signifique cosas distintas para negocio, desarrollo y pruebas. El sistema 3 controla sobre todo el plazo y conoce la calidad por el reporte de la misma célula. El sistema 3* queda corto, porque falta un muestreo de evidencias hecho por alguien que no ejecutó la prueba. El sistema 4 puede abrir una línea tecnológica más rápido de lo que el sistema 3 consigue personas y capacidad de prueba. El bucle de retroalimentación llega tarde, y el cliente ocupa el lugar del auditor.",
    )
    sub = document.add_paragraph()
    sub.paragraph_format.space_before = Pt(4)
    sub.paragraph_format.space_after = Pt(4)
    sub.paragraph_format.line_spacing = 1.15
    add_text(sub, "Fortalecimiento de los sistemas, la problemática y el ODS 9", size=12, bold=True, color=NAVY)
    body(
        document,
        "Fortalecer esos canales cambia la respuesta al problema y el aporte al ODS 9. Un criterio de terminado visible, acordado antes de construir, aumenta la variedad del sistema 2 y la acerca a la variedad del cliente, en la línea del principio de variedad que recogen Cabrera-Moya y Prieto-Rodríguez (2022). Incluir la prueba dentro del incremento devuelve la corrección al sistema 1, donde todavía cabe en el plazo. Un muestreo de evidencias sobre los flujos críticos le da al sistema 3* información de primera mano. Una regla del sistema 5 equilibra el presente y el mañana: la tecnología nueva se ofrece al cliente cuando el sistema 3 confirma personas y capacidad de prueba. El ODS 9 pide capacidad tecnológica que quede realmente instalada (Naciones Unidas, s. f.). Nelumbo construye software para salud, seguros, obra y comercio. Si ese software sale con la calidad que la misión promete, la innovación se vuelve infraestructura que otros sectores pueden usar. Desde Ingeniería de Sistemas, el fortalecimiento es un diseño de información: qué dato se atenúa, cuál se amplifica y en qué momento vuelve para corregir.",
    )

    heading(document, "Conclusiones")
    body(
        document,
        "El Modelo de Sistemas Viables permite leer Nelumbo como una organización que ya cuenta con operación, coordinación, cohesión, inteligencia y política. La falla de calidad aparece como un bucle de información tardío. El cliente detecta el defecto porque el sistema 3* y el acuerdo de terminado del sistema 2 no alcanzan la variedad del entorno.",
    )
    body(
        document,
        "La viabilidad de la empresa se juega en conservar la identidad mientras se adapta. La misión publicada pide tecnología alineada con el negocio y calidad comprobada. Esa identidad se sostiene si la dirección equilibra la oferta nueva del sistema 4 con la capacidad real de las células, y si la prueba hace parte de la entrega y no de la disculpa posterior.",
    )
    body(
        document,
        "Ajustar el criterio de terminado, muestrear evidencias antes de producción y atar cada tecnología nueva a la capacidad de prueba son oportunidades de fortalecimiento concretas. Desde la Ingeniería de Sistemas, esas decisiones diseñan los canales de regulación. Desde el ODS 9, convierten la innovación de una empresa de Cúcuta en infraestructura digital que otros sectores pueden usar con confianza.",
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
            ("Nelumbo Consultores. (s. f.-a). ", False),
            ("Nelumbo Consultores", True),
            (". https://www.nelumboconsultores.com/", False),
        ],
    )
    reference(
        document,
        [
            ("Nelumbo Consultores. (s. f.-b). ", False),
            ("Sobre nosotros", True),
            (". https://www.nelumboconsultores.com/index.php/sobre-nosotros/", False),
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
Publicar este texto como avance, antes de cerrar el foro (domingo 22 de noviembre de 2026).

Cordial saludo, tutor y compañeros.

Retomo a Nelumbo Consultores, empresa de software a la medida con sede en Cúcuta, y la problemática de la calidad que se coordina tarde entre células que entregan al mismo tiempo. Analizarla con el Modelo de Sistemas Viables permite ver si la organización tiene variedad suficiente para responder a clientes, normas y tecnologías distintas, sin perder la promesa de entregar un producto listo. El modelo no se queda en el área de pruebas: mira el acople entre el entorno, la operación y la gestión (Cabrera-Moya y Prieto-Rodríguez, 2022).

En el entorno están los clientes de seguros, construcción, comercio y salud, los usuarios finales, los contratos y la norma de datos, y el cambio tecnológico. Esa variedad cambia el plazo y el criterio de aceptación. La operación son las células de desarrollo web, móvil, integraciones, diseño, analítica y las pruebas del incremento: allí se puede corregir el defecto mientras todavía cabe en el plazo. La gestión —dirección general, dirección de operaciones, dirección de proyectos y el tablero compartido— reparte personas y sincroniza el trabajo. Cuando la gestión sigue sobre todo la fecha, el entorno devuelve el defecto por boca del cliente.

Quedo atento a la retroalimentación antes de cerrar los cinco sistemas.

---

FORO 2. Arquitectura Viable
Publicar este texto cuando el tutor haya comentado el avance anterior. Es la explicación de los cinco sistemas, en palabras propias.

Cordial saludo.

El Modelo de Sistemas Viables separa cinco funciones que tienen que conversar, no cinco cargos. El sistema 1 produce lo que la organización es. Cada operación tiene gestión propia y toca su pedazo de entorno; el metasistema no la reemplaza, le presta recursos, normas y cuentas (Cabrera-Moya y Prieto-Rodríguez, 2022). El sistema 2 amortigua los choques entre esas operaciones con un lenguaje común, un estándar y un sistema de información. Sin eso, cada equipo cierra el trabajo a su manera y el conjunto se descoordina.

El sistema 3 mira el adentro y el ahora: reparte recursos y busca que las operaciones rindan juntas. El sistema 3* no se fía solo del informe. Va a la fuente, de vez en cuando, y contrasta. Si ese canal falta, la dirección se entera cuando el problema ya salió. El sistema 4 mira el afuera y el mañana, y por eso Cabrera-Moya y Prieto-Rodríguez (2022) lo tratan como motor de aprendizaje. Si va más rápido que el sistema 3, la empresa promete lo que todavía no puede sostener. El sistema 5 cierra la identidad y equilibra el presente con el futuro (Sánchez Rueda, 1995).

En Nelumbo el sistema 1 son las células que construyen y prueban; el 2, la dirección de proyectos y el tablero; el 3, la dirección de operaciones; el 3*, un muestreo de evidencias que hoy es irregular; el 4, la lectura de mercado y de tecnología; y el 5, la dirección general con la misión de calidad comprobada. El punto frágil es que el cliente está haciendo la auditoría que debería hacer el sistema 3*.

---

CÓMO COMENTAR A DOS COMPAÑEROS
No dejes un “de acuerdo”. Usa algo de lo que ellos escribieron. Puedes adaptar estas dos ideas:

1. “En tu entorno listas varios actores. El MSV pide, además, decir cuál de ellos le mete más variedad a la operación y si la gestión tiene un canal para enterarse a tiempo. Si ese canal es solo el informe final, el sistema 3* está débil.”

2. “Vi que ubicaste el área de calidad en el sistema 1. Tiene sentido si la prueba hace parte de producir el servicio. Convendría separar eso de una revisión hecha por alguien que no ejecutó la prueba: esa segunda mirada es el sistema 3*, y no compite con la primera.”
"""


def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    if not TEMPLATE.exists():
        raise SystemExit("No está la plantilla en /tmp/plantilla.pptx")
    render_figure()
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
