#!/usr/bin/env python3
"""Arma el Anexo de la Fase 4 a partir de la plantilla del curso."""

import shutil
import subprocess
from copy import deepcopy
from pathlib import Path

from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor
from docx.text.paragraph import Paragraph

ROOT = Path(__file__).resolve().parent
TEMPLATE = Path(
    "/home/ubuntu/.cursor/projects/agent-repos-personal/uploads/Anexo_Fase_4_0f18.docx"
)
DOCX = ROOT / "Anexo_Fase_4.docx"
PDF = ROOT / "Anexo_Fase_4.pdf"
FORO = ROOT / "textos-para-el-foro.txt"
NAVY = RGBColor(0x1F, 0x4E, 0x79)

INTRO = (
    "Nelumbo Consultores es una empresa colombiana de consultoría tecnológica que opera "
    "de manera remota. Desarrolla software, asegura la calidad de las soluciones y acompaña "
    "la transformación digital de clientes empresariales. La problemática, definida desde la "
    "Fase 1 y mantenida en las fases siguientes, es la ausencia de un sistema formal de gestión "
    "del conocimiento: al cerrar un proyecto, el saber técnico no siempre queda documentado y "
    "la operación depende de personas específicas. El Objetivo de Desarrollo Sostenible "
    "relacionado es el 9, porque conservar esas lecciones sostiene la capacidad de la firma "
    "para entregar soluciones y adaptarse."
    "\n\n"
    "Esta fase integra las herramientas del curso para formular una propuesta de "
    "fortalecimiento. El pensamiento sistémico situó el corte en la relación entre el cierre, "
    "la persona y el proyecto siguiente. La metodología de sistemas blandos definió la "
    "transformación y los actores que pueden hacerla. El modelo de sistemas viables mostró "
    "qué canales regulan la entrega y cuáles no regulan la circulación del saber. Los niveles "
    "jerárquicos de Boulding evitan leer la firma solo como un mecanismo de control y la "
    "sitúan como sistema sociocultural. A partir de esos hallazgos, y de una lectura crítica "
    "de recomendaciones producidas con una herramienta de inteligencia artificial generativa, "
    "la propuesta queda en tres prácticas: registrar la lección en el cierre, dejarla en una "
    "base que los equipos ya usan y consultarla al iniciar requerimientos y diseño, con una "
    "señal en los informes."
)

LEAD_INTEGRACION = (
    "La tabla recoge el hallazgo que cada herramienta dejó para la misma problemática. "
    "No transcribe las fases anteriores."
)

LEAD_BOULDING = (
    "La jerarquía de Boulding (1956) ordena los sistemas por complejidad creciente. "
    "Nelumbo pertenece al nivel sociocultural. Los niveles inferiores sirven para ver qué "
    "parte del problema quedaría mal explicada si se usara solo ese grado. Donde el nivel "
    "no corresponde a la firma, se dice y se justifica."
)

LEAD_IA = (
    "Se pidieron recomendaciones con los datos de la firma, la problemática y el ODS 9, "
    "sin adelantar la propuesta en el prompt. La tabla resume la respuesta y la contrasta "
    "con los actores y los canales ya identificados."
)

LEAD_PROPUESTA = (
    "Las tres estrategias retoman los cambios definidos en la Fase 2. Cada una indica qué "
    "herramienta la sostiene, qué cambia en la operación y de qué modo aporta al ODS 9."
)

Q1 = (
    "La integración evitó explicar el problema con una sola herramienta. El pensamiento "
    "sistémico lo situó en la relación entre el cierre, la persona y el proyecto siguiente: "
    "los informes corrigen la entrega y no guardan la lección, y el entorno se lleva el saber "
    "cuando alguien rota (Osorio Gómez, 2007). La metodología de sistemas blandos puso nombre "
    "a la transformación y a los actores que pueden hacerla, y la observación recibida en la "
    "Fase 2 impidió dejar esas actividades en una fila. El modelo de sistemas viables mostró "
    "el corte en los canales: el sistema 1 produce el saber, el 2 no lo sincroniza, el 3 mide "
    "otra cosa, el 3* no contrasta el registro y el 4 queda expuesto a la rotación "
    "(Cabrera-Moya y Prieto-Rodríguez, 2022). Boulding (1956) completa esa lectura al ordenar "
    "los grados de complejidad. Nelumbo es un sistema sociocultural. Tratarla solo como "
    "termostato, que es el nivel de los informes, reduce el problema a un indicador de "
    "defectos. El nivel humano explica por qué el saber está en quien vivió el proyecto; el "
    "nivel social explica por qué hace falta una norma compartida para que ese saber circule. "
    "Juntas, las herramientas muestran que la solución no es un archivo suelto, sino un "
    "circuito entre personas, roles y control."
)

Q2 = (
    "La inteligencia artificial aportó velocidad y un contraste. Ante el mismo caso devolvió "
    "el circuito que las fases anteriores ya sostenían —formato al cierre, base en las "
    "herramientas existentes, consulta al diseñar e indicador— y añadió un área nueva, una "
    "plataforma distinta, un incentivo individual y la publicación de lecciones. Ese exceso "
    "sirvió: obligó a decidir con los conceptos del curso y no con la lista completa. La "
    "limitación principal es que la herramienta no distingue el nivel de complejidad. Propone "
    "por igual un cambio de norma social y una compra de software, sin registrar que la Fase 2 "
    "ya había fijado las plataformas y los actores. Tampoco verifica los datos de la firma: "
    "completa con prácticas genéricas de gestión del conocimiento. Otra limitación es de "
    "autoría. Si el análisis se queda en la respuesta, el criterio deja de ser propio y el "
    "texto no se puede defender ante el tutor. Por eso el uso se restringió a generar opciones, "
    "y la decisión quedó en lo que el modelo de sistemas viables puede regular y en lo que "
    "Boulding (1956) impide reducir a un nivel inferior. La inteligencia artificial complementa "
    "la búsqueda de alternativas. No reemplaza la lectura de la organización ni la "
    "responsabilidad de la cita."
)

CONCLUSIONES = [
    (
        "El problema de Nelumbo no es la falta de informes. Es la ausencia de un circuito para "
        "que el saber del proyecto pase de la persona que lo vivió al sistema de roles y vuelva "
        "al encargo siguiente. Las herramientas del curso coinciden en ese corte y lo nombran "
        "desde lugares distintos."
    ),
    (
        "Boulding (1956) impide resolver el corte con el modelo de un nivel inferior. Un "
        "indicador nuevo, por sí solo, sigue siendo un mecanismo cibernético. La práctica tiene "
        "que quedar en los roles del cierre y de la consulta, que es donde la organización, como "
        "sistema sociocultural, conserva o pierde lo aprendido."
    ),
    (
        "La propuesta se sostiene porque cada estrategia usa una herramienta para una decisión "
        "que los actores reales pueden llevar: líderes, equipos y director, sobre las "
        "plataformas ya existentes. El aporte al ODS 9 es conservar, dentro de la firma, la "
        "capacidad con la que diseña soluciones para sus clientes (Naciones Unidas, s. f.)."
    ),
]

HALLAZGOS = [
    (
        "Pensamiento sistémico",
        "El saber no se pierde en un punto aislado. Se corta en la relación entre el cierre, "
        "la persona que ejecutó el proyecto y el encargo siguiente. Los informes de "
        "satisfacción, defectos y tiempos ajustan la entrega y no conservan la lección. "
        "Como sistema abierto, la firma intercambia requerimientos, talento, herramientas "
        "e información con clientes, proveedores tecnológicos, entes reguladores y el "
        "mercado de talento. Si la persona rota, sale con ella una variedad que el canal "
        "interno no guardó. Osorio Gómez (2007) recuerda que los elementos se relacionan "
        "para un propósito común: aquí, que la lección quede disponible para el proyecto siguiente.",
    ),
    (
        "Metodología de sistemas blandos",
        "La definición raíz ubicó la transformación: el saber disperso del cierre pasa a "
        "lecciones y mejores prácticas en una base interna, a cargo de desarrollo, QA y "
        "líderes de proyecto, bajo la autoridad del director general. El modelo conceptual "
        "de la Fase 2 ordenaba identificar, documentar, organizar, consultar y evaluar en "
        "una fila. La retroalimentación pidió una red. Identificar depende del cierre, del "
        "QA y del soporte. Documentar depende del formato que acuerdan los líderes. "
        "Consultar depende de que la base exista al iniciar requerimientos y diseño. "
        "Evaluar vuelve al inicio y a la decisión de sostener o detener la práctica.",
    ),
    (
        "Modelo de sistemas viables",
        "Los cinco sistemas ya tienen nombre en la operación y no cierran el circuito del "
        "saber. El sistema 1 produce el servicio y el conocimiento. El sistema 2 coordina "
        "la entrega y todavía no obliga a un mismo formato de lección. El sistema 3 mide "
        "satisfacción, defectos y tiempos. El sistema 3* no verifica el registro con alguien "
        "distinto de quien declara el cierre. El sistema 4 lee el mercado de talento y la "
        "tecnología, y queda expuesto si el saber vive en las personas. El sistema 5 puede "
        "autorizar la base. Cabrera-Moya y Prieto-Rodríguez (2022) recuerdan que la viabilidad "
        "depende de esos canales, no de una fila del 1 al 5.",
    ),
]

BOULDING = [
    (
        "1. Estructuras estáticas",
        "Áreas funcionales y plataformas de gestión ya usadas. No hay una base de lecciones como estructura fija.",
        "Boulding (1956) llama así a los marcos que describen una organización, como un organigrama, sin la complejidad de los niveles superiores. En Nelumbo ese marco son la gestión de proyectos, el desarrollo, el QA y el soporte, más las plataformas con las que ya coordinan. El saber del proyecto no tiene un lugar fijo. Por eso, al cerrar, no queda asentado en la estructura.",
    ),
    (
        "2. Sistemas dinámicos simples",
        "Ciclo del proyecto y revisión de sprint.",
        "Este nivel añade el movimiento previsto, como el de un mecanismo que recorre fases. El proyecto avanza de requerimientos a diseño, pruebas, entrega y cierre, y el sprint repite ese ritmo. El movimiento ocurre aunque la lección no se registre. Explica la continuidad del trabajo. No explica la conservación del saber.",
    ),
    (
        "3. Sistemas cibernéticos",
        "Informes de satisfacción, tasa de defectos y tiempo de resolución.",
        "El nivel cibernético se autorregula por retroalimentación, a la manera de un termostato. Esos informes corrigen la entrega. No comparan lo aprendido con lo que el proyecto siguiente consulta. El control existe y está calibrado para otro objetivo. La firma puede cumplir el plazo y repetir el mismo corte de conocimiento.",
    ),
    (
        "4. Sistemas abiertos",
        "Intercambio con clientes, proveedores tecnológicos, entes reguladores y el mercado de talento.",
        "El sistema abierto se mantiene por lo que entra y sale, y diferencia su interior para relacionarse con un entorno que también cambia. Nelumbo recibe requerimientos, herramientas y personas, y entrega soluciones. El talento es una de esas entradas. Si la lección no quedó escrita, la salida de una persona exporta variedad que el interior no repone.",
    ),
    (
        "5. Genético-social",
        "No hay un organismo vegetal. La analogía útil es la diferencia entre repetir el método de proyecto y heredar lo que una persona aprendió.",
        "Este nivel, propio de las plantas, distingue la reproducción del sistema y el individuo funcional, con división del trabajo entre las partes (Boulding, 1956). Nelumbo no es una planta. Sí se distingue el método que cada proyecto repite y la persona que ejecutó el anterior. El método se reproduce. La lección, no. La analogía se detiene ahí: no hay un código que transmita el saber de un proyecto al siguiente.",
    ),
    (
        "6. Animal",
        "No aplica.",
        "El nivel animal supone receptores especializados, una imagen del entorno y aprendizaje, sin el procesamiento simbólico del nivel humano. Nelumbo no es un organismo animal. La lectura del mercado la hacen personas, con lenguaje, dentro de una organización. Ubicar esa lectura aquí reduciría un sistema sociocultural al modelo de un nivel inferior, que es el salto que Boulding (1956) pide no dar.",
    ),
    (
        "7. Humano",
        "El saber técnico que queda en quien diseñó, probó o atendió la incidencia.",
        "El nivel humano añade el lenguaje simbólico: la persona sabe qué conoce y puede decirlo. En Nelumbo el conocimiento del proyecto tiene esa forma. Vive en desarrolladores, analistas QA y soporte, y solo pasa a otro si se enuncia. La dependencia de personas específicas es este nivel cuando el nivel social no recibe el símbolo.",
    ),
    (
        "8. Socioculturales",
        "Roles de director general, líderes de proyecto, desarrollo, QA y soporte, en una operación remota.",
        "Boulding (1956) sitúa las organizaciones en este nivel: roles, comunicación y valores compartidos. Nelumbo es este sistema, no solo la suma de las personas. La norma vigente es que el cierre entrega el producto. La norma que falta es que el cierre también deje la lección en un lugar común y que el proyecto siguiente la consulte. El problema está en esa pauta, no en la falta de competencia individual.",
    ),
    (
        "9. Trascendentes",
        "No se identifica un sistema trascendente en la operación.",
        "Este nivel señala lo que queda más allá de los sistemas que el modelo puede estudiar. El propósito de conservar capacidad tecnológica, vinculado al ODS 9, sigue siendo una decisión de la organización: pertenece al nivel sociocultural y a la autoridad del director. Tratar el ODS como sistema trascendente le atribuiría a Boulding una categoría que su jerarquía deja fuera del análisis empírico.",
    ),
]

PROMPT = (
    "Soy estudiante de Ingeniería de Sistemas y analizo una organización real. "
    "Nelumbo Consultores es una consultora tecnológica colombiana de operación remota. "
    "Desarrolla software, hace aseguramiento de calidad y acompaña la transformación digital "
    "de clientes empresariales. El equipo lo coordinan líderes de proyecto y un director general. "
    "Problema: al cerrar un proyecto, el conocimiento técnico no queda documentado de manera "
    "estructurada y la operación depende de personas específicas. Los informes actuales miran "
    "satisfacción, defectos y tiempos de resolución. El ODS relacionado es el 9, por la capacidad "
    "tecnológica que la firma necesita conservar. Desde un enfoque sistémico, recomienda acciones "
    "concretas para que ese conocimiento deje de depender de personas. Incluye responsables y "
    "riesgos, y señala qué alternativas conviene descartar en una firma de este tamaño."
)

RESPUESTA_IA = (
    "La respuesta propuso cuatro acciones y tres descarte. Acciones: un formato breve de "
    "lecciones al cierre, con lo visto por desarrollo, QA y soporte, a cargo de los líderes de "
    "proyecto; guardar ese registro en la plataforma de gestión que los equipos ya usan; "
    "consultar la base al iniciar requerimientos y diseño, como parte del arranque; y sumar al "
    "informe si la lección se registró y si el proyecto siguiente la consultó, con una "
    "verificación hecha por alguien que no declaró el cierre. Descarte explícito: abrir un área "
    "nueva de gestión del conocimiento y comprar una plataforma aparte; premiar a quien más "
    "registros suba; y publicar lecciones de clientes para mostrar el aporte al ODS 9. Añadió, "
    "como paso posterior, un asistente de inteligencia artificial para consultar la base cuando "
    "el registro ya exista."
)

CRITICA = (
    "Se acogen las cuatro acciones. Coinciden con los actores de la Fase 2 y con el corte que "
    "el modelo de sistemas viables ya mostró: el sistema 1 produce la lección, el 2 pone el "
    "formato, el 3 necesita una cuenta distinta de la entrega y el 3* contrasta el registro. "
    "Se confirman los tres descartes, ahora con la jerarquía de Boulding. Un área nueva y una "
    "plataforma nueva aumentan la variedad que el director tendría que regular, y bajan el "
    "problema a una compra, que es un marco estático. El incentivo individual se queda en el "
    "nivel humano y no crea la norma del nivel sociocultural. La publicación abierta trata como "
    "vitrina un saber de clientes que la firma no puede difundir; el ODS 9 pide capacidad "
    "instalada, no un canal público (Naciones Unidas, s. f.). Se ajusta el asistente: no entra "
    "en esta propuesta. Sin una base verificada, completa huecos y devuelve la dependencia a "
    "un sistema que nadie auditó."
)

CONCLUSION_IA = (
    "La herramienta ordenó el circuito que las fases 2 y 3 ya sostenían y sirvió para poner "
    "junto a ese circuito las opciones que sobran. El criterio se queda con el formato, la base "
    "existente, la consulta al diseñar y el indicador verificado. La inteligencia artificial no "
    "definió la propuesta. Obligó a justificar por qué unas recomendaciones caben en Nelumbo y "
    "otras no."
)

ESTRATEGIAS = [
    (
        "Formato de lecciones en cada cierre, con entradas de desarrollo, QA y soporte, acordado por los líderes de proyecto.",
        "Metodología de sistemas blandos y modelo de sistemas viables (sistemas 1 y 2), leídos en el nivel humano de Boulding: quien vivió el proyecto tiene que dejar el saber en un símbolo común.",
        "El cierre produce el servicio y una lección en el mismo formato. El saber deja de quedar solo en quien ejecutó el proyecto.",
        "La capacidad técnica queda registrada y puede usarse en encargos posteriores, en lugar de reiniciar el aprendizaje con cada contrato (ODS 9).",
    ),
    (
        "Base interna en las plataformas que los equipos ya usan, consultada al iniciar requerimientos y diseño.",
        "Pensamiento sistémico, metodología de sistemas blandos y sistemas 1 y 4 del modelo de sistemas viables. En Boulding, da un marco estático al saber y lo mantiene dentro del sistema abierto.",
        "El proyecto siguiente arranca con las lecciones del anterior. La salida de una persona no se lleva el único ejemplar.",
        "La innovación no depende de repetir desde cero. La infraestructura de conocimiento queda en la operación y sostiene la respuesta al cliente (ODS 9).",
    ),
    (
        "Incluir en el informe si la lección se registró y se consultó, y verificar el registro con alguien que no declaró el cierre.",
        "Modelo de sistemas viables (sistemas 3, 3* y 5) y nivel cibernético de Boulding, puesto al servicio del nivel sociocultural y no en su reemplazo.",
        "La gestión ve la circulación del saber y no solo la entrega. El director tiene una señal para sostener o detener la práctica.",
        "La capacidad tecnológica se puede seguir. Lo que no entra al canal de la organización no se conserva, y el ODS 9 pide que esa capacidad quede instalada.",
    ),
]

FORO_TEXT = """FORO. Integrando herramientas para transformar organizaciones
Publicar esta síntesis. Máximo dos párrafos. El foro corresponde al Paso 6.
La actividad cierra el domingo 6 de diciembre de 2026.

Cordial saludo, tutor y compañeros.

En Nelumbo Consultores el problema sigue siendo el de las fases anteriores: al cerrar un proyecto, el saber técnico no queda documentado y la operación depende de personas. Integrar las herramientas cambia la lectura. El pensamiento sistémico y la metodología de sistemas blandos muestran el corte entre el cierre, la persona y el proyecto siguiente, y piden una red de actividades, no una fila. El modelo de sistemas viables muestra que los informes regulan la entrega y no la circulación de la lección. Boulding sitúa a la firma en el nivel sociocultural: un indicador, por sí solo, es solo un termostato.

La inteligencia artificial devolvió ese mismo circuito y añadió un área nueva, una plataforma distinta, un incentivo individual y la publicación de lecciones. Esas opciones se descartan porque no caben en los actores ni en el ODS 9, que pide capacidad instalada en la firma y no una vitrina. La propuesta queda en tres prácticas: formato de lecciones en el cierre, base en las plataformas ya usadas y consulta al iniciar requerimientos y diseño, con el dato de registro y consulta en el informe.

---

COMENTARIO PARA UN COMPAÑERO
Leer su aporte y adaptar este comentario al caso que haya publicado.

Tu integración nombra las herramientas y conviene dar un paso más: decir cuál nivel de Boulding explica el problema y cuál quedaría corto si se usa solo. En una organización, el nivel sociocultural incluye a los anteriores; no los reemplaza. Si la propuesta se queda en un indicador o en una herramienta nueva, el análisis baja un sistema de roles a un mecanismo de control. Vale la pena indicar qué recomendación de la inteligencia artificial descartas y con qué concepto del curso la descartas.
"""


def words(text):
    return len(text.replace("\n", " ").split())


def set_run_font(run, *, size=12, bold=False, color=None, italic=False):
    run.bold = bold
    run.italic = italic
    run.font.name = "Verdana"
    run.font.size = Pt(size)
    if color is not None:
        run.font.color.rgb = color
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    for attr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rfonts.set(qn(attr), "Verdana")


def replace_text(paragraph, text, *, size=12, bold=False, color=None, align=None, center=False):
    element = paragraph._p
    for child in list(element):
        if child.tag == qn("w:r"):
            element.remove(child)
    if align is not None:
        paragraph.alignment = align
    elif center:
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.paragraph_format.space_after = Pt(8)
    paragraph.paragraph_format.space_before = Pt(0)
    paragraph.paragraph_format.line_spacing = 1.15
    blocks = text.split("\n\n")
    run = paragraph.add_run(blocks[0])
    set_run_font(run, size=size, bold=bold, color=color)
    return blocks[1:]


def find_one(document, start):
    hits = [p for p in document.paragraphs if p.text.strip().startswith(start)]
    if len(hits) != 1:
        raise SystemExit(f"{start!r}: {len(hits)} coincidencias")
    return hits[0]


def find_all(document, start):
    return [p for p in document.paragraphs if p.text.strip().startswith(start)]


def insert_after(paragraph, text, *, size=12, bold=False, italic=False, hanging=False):
    new_p = OxmlElement("w:p")
    paragraph._p.addnext(new_p)
    para = Paragraph(new_p, paragraph._parent)
    if hanging:
        para.paragraph_format.left_indent = Cm(1.25)
        para.paragraph_format.first_line_indent = Cm(-1.25)
    para.paragraph_format.space_after = Pt(8)
    para.paragraph_format.line_spacing = 1.15
    para.alignment = WD_ALIGN_PARAGRAPH.LEFT if hanging else WD_ALIGN_PARAGRAPH.JUSTIFY
    run = para.add_run(text)
    set_run_font(run, size=size, bold=bold, italic=italic)
    return para


def write_cell(cell, text, *, bold=False, size=10, center=False, allow_split=False):
    paragraphs = cell.paragraphs
    first = paragraphs[0]
    for extra in paragraphs[1:]:
        extra._element.getparent().remove(extra._element)
    for run in list(first.runs):
        run._element.getparent().remove(run._element)
    first.alignment = WD_ALIGN_PARAGRAPH.CENTER if center else WD_ALIGN_PARAGRAPH.LEFT
    first.paragraph_format.space_after = Pt(0 if size <= 9 else 2)
    first.paragraph_format.space_before = Pt(0 if size <= 9 else 2)
    first.paragraph_format.line_spacing = 1.0 if size <= 9 else 1.05
    run = first.add_run(text)
    set_run_font(run, size=size, bold=bold, color=RGBColor(0xFF, 0xFF, 0xFF) if bold and center else None)
    if bold and center:
        run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    tc = cell._tc
    tc_pr = tc.find(qn("w:tcPr"))
    if tc_pr is None:
        tc_pr = OxmlElement("w:tcPr")
        tc.insert(0, tc_pr)
    if tc_pr.find(qn("w:vAlign")) is None:
        align = OxmlElement("w:vAlign")
        align.set(qn("w:val"), "center" if center else "top")
        tc_pr.append(align)
    if not allow_split:
        row = tc.getparent()
        tr_pr = row.find(qn("w:trPr"))
        if tr_pr is None:
            tr_pr = OxmlElement("w:trPr")
            row.insert(0, tr_pr)
        if tr_pr.find(qn("w:cantSplit")) is None:
            tr_pr.append(OxmlElement("w:cantSplit"))


def shade_header(row):
    tr_pr = row._tr.find(qn("w:trPr"))
    if tr_pr is None:
        tr_pr = OxmlElement("w:trPr")
        row._tr.insert(0, tr_pr)
    if tr_pr.find(qn("w:tblHeader")) is None:
        tr_pr.append(OxmlElement("w:tblHeader"))
    for cell in row.cells:
        tc_pr = cell._tc.find(qn("w:tcPr"))
        if tc_pr is None:
            tc_pr = OxmlElement("w:tcPr")
            cell._tc.insert(0, tc_pr)
        shd = tc_pr.find(qn("w:shd"))
        if shd is None:
            shd = OxmlElement("w:shd")
            tc_pr.append(shd)
        shd.set(qn("w:val"), "clear")
        shd.set(qn("w:color"), "auto")
        shd.set(qn("w:fill"), "1F4E79")


def set_widths(table, widths_cm):
    tbl = table._tbl
    tbl_pr = tbl.find(qn("w:tblPr"))
    tbl_w = tbl_pr.find(qn("w:tblW"))
    if tbl_w is None:
        tbl_w = OxmlElement("w:tblW")
        tbl_pr.append(tbl_w)
    total = sum(int(w * 567) for w in widths_cm)
    tbl_w.set(qn("w:w"), str(total))
    tbl_w.set(qn("w:type"), "dxa")
    layout = tbl_pr.find(qn("w:tblLayout"))
    if layout is not None:
        tbl_pr.remove(layout)
    grid = tbl.find(qn("w:tblGrid"))
    if grid is not None:
        cols = list(grid)
        for index, width in enumerate(widths_cm):
            if index < len(cols):
                cols[index].set(qn("w:w"), str(int(width * 567)))
    for row in table.rows:
        for index, cell in enumerate(row.cells):
            tc_pr = cell._tc.find(qn("w:tcPr"))
            if tc_pr is None:
                tc_pr = OxmlElement("w:tcPr")
                cell._tc.insert(0, tc_pr)
            tc_w = tc_pr.find(qn("w:tcW"))
            if tc_w is None:
                tc_w = OxmlElement("w:tcW")
                tc_pr.append(tc_w)
            tc_w.set(qn("w:w"), str(int(widths_cm[index] * 567)))
            tc_w.set(qn("w:type"), "dxa")


def ensure_borders(table):
    tbl_pr = table._tbl.find(qn("w:tblPr"))
    borders = tbl_pr.find(qn("w:tblBorders"))
    if borders is None:
        borders = OxmlElement("w:tblBorders")
        tbl_pr.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        element = borders.find(qn(f"w:{edge}"))
        if element is None:
            element = OxmlElement(f"w:{edge}")
            borders.append(element)
        element.set(qn("w:val"), "single")
        element.set(qn("w:sz"), "4")
        element.set(qn("w:space"), "0")
        element.set(qn("w:color"), "8FA8C4")
    for row in table.rows:
        for cell in row.cells:
            tc_pr = cell._tc.find(qn("w:tcPr"))
            if tc_pr is None:
                continue
            hide = tc_pr.find(qn("w:hideMark"))
            if hide is not None:
                tc_pr.remove(hide)


def fill_table(table, rows, widths, header=True, size=10, allow_split=False):
    if header:
        shade_header(table.rows[0])
        for cell in table.rows[0].cells:
            write_cell(cell, cell.text, bold=True, size=size, center=True)
    while len(table.rows) < len(rows) + (1 if header else 0):
        table._tbl.append(deepcopy(table.rows[-1]._tr))
    offset = 1 if header else 0
    for index, values in enumerate(rows):
        for col, value in enumerate(values):
            write_cell(table.rows[index + offset].cells[col], value, size=size, allow_split=allow_split)
    set_widths(table, widths)
    ensure_borders(table)


def add_page_number(paragraph):
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
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


def clone_section(template, landscape_mode):
    section = deepcopy(template)
    kind = section.find(qn("w:type"))
    if kind is None:
        kind = OxmlElement("w:type")
        section.insert(0, kind)
    kind.set(qn("w:val"), "nextPage")
    page = section.find(qn("w:pgSz"))
    if page is None:
        page = OxmlElement("w:pgSz")
        section.append(page)
    if landscape_mode:
        page.set(qn("w:w"), "15840")
        page.set(qn("w:h"), "12240")
        page.set(qn("w:orient"), "landscape")
    else:
        page.set(qn("w:w"), "12240")
        page.set(qn("w:h"), "15840")
        page.set(qn("w:orient"), "portrait")
    return section


def tidy_sections(document):
    saved = None
    for section in document.element.iter(qn("w:sectPr")):
        if section.find(qn("w:headerReference")) is not None:
            saved = deepcopy(section)
            break
    if saved is None:
        raise SystemExit("La plantilla no conservó el encabezado institucional")
    for paragraph in list(document.paragraphs):
        if paragraph.text == "\t":
            paragraph._p.getparent().remove(paragraph._p)
            continue
        properties = paragraph._p.find(qn("w:pPr"))
        if properties is None:
            continue
        section = properties.find(qn("w:sectPr"))
        if section is not None:
            properties.remove(section)
    body_section = document.element.body.find(qn("w:sectPr"))
    if body_section.find(qn("w:headerReference")) is None:
        for ref in list(saved):
            if ref.tag in (qn("w:headerReference"), qn("w:footerReference")):
                body_section.insert(0, deepcopy(ref))
    paragraphs = list(document.paragraphs)
    caption = find_all(document, "Análisis crítico de recomendaciones")[1]
    caption_index = next(i for i, paragraph in enumerate(paragraphs) if paragraph._p is caption._p)
    properties = caption._p.find(qn("w:pPr"))
    if properties is None:
        properties = OxmlElement("w:pPr")
        caption._p.insert(0, properties)
    properties.append(clone_section(saved, False))
    proposal = find_all(document, "Propuesta de fortalecimiento organizacional")[0]
    proposal_index = next(i for i, paragraph in enumerate(paragraphs) if paragraph._p is proposal._p)
    before = paragraphs[proposal_index - 1]
    properties = before._p.find(qn("w:pPr"))
    if properties is None:
        properties = OxmlElement("w:pPr")
        before._p.insert(0, properties)
    properties.append(clone_section(saved, True))


def build():
    counts = {
        "intro": words(INTRO),
        "pregunta 1": words(Q1),
        "pregunta 2": words(Q2),
    }
    for name, count in counts.items():
        if not 150 <= count <= 250:
            raise SystemExit(f"{name}: {count} palabras, fuera de 150-250")
    shutil.copy(TEMPLATE, DOCX)
    document = Document(DOCX)
    replace_text(
        find_one(document, "Nombre del estudiante"),
        "Nombre del estudiante: Jhon Carlos Acevedo Mendoza",
        bold=True,
        center=True,
    )
    replace_text(
        find_one(document, "Tutor"),
        "Tutor: Ing. Víctor Hugo Mercado Ramos",
        bold=True,
        center=True,
    )
    intro = find_one(document, "Redacte una introducción")
    pending = replace_text(intro, INTRO, size=12)
    intro.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    cursor = intro
    for block in pending:
        cursor = insert_after(cursor, block)
    replace_text(find_one(document, "Retome los principales hallazgos"), LEAD_INTEGRACION)
    find_one(document, "La tabla recoge").alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    replace_text(find_one(document, "Identifique, para cada nivel"), LEAD_BOULDING)
    find_one(document, "La jerarquía de Boulding").alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    replace_text(find_one(document, "Utilice una herramienta"), LEAD_IA)
    find_one(document, "Se pidieron recomendaciones").alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    replace_text(find_one(document, "Formule estrategias"), LEAD_PROPUESTA)
    find_one(document, "Las tres estrategias").alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    replace_text(
        find_one(document, "Responda de manera argumentada"),
        "Cada respuesta se sostiene en el análisis de las fases anteriores y en los referentes citados.",
    )
    find_one(document, "Cada respuesta se sostiene").alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    answers = find_all(document, "Respuesta:")
    if len(answers) != 2:
        raise SystemExit(f"respuestas: {len(answers)}")
    replace_text(answers[0], Q1)
    answers[0].alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    replace_text(answers[1], Q2)
    answers[1].alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    conclusion = find_one(document, "Redacte tres conclusiones")
    replace_text(conclusion, CONCLUSIONES[0])
    conclusion.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    cursor = conclusion
    for text in CONCLUSIONES[1:]:
        cursor = insert_after(cursor, text)
    bibliography = find_one(document, "Registre las referencias")
    refs = [
        "Boulding, K. E. (1956). General systems theory: The skeleton of science. Management Science, 2(3), 197–208. https://doi.org/10.1287/mnsc.2.3.197",
        "Cabrera-Moya, D. R. R. y Prieto-Rodríguez, G. A. (2022). On the need for structuring of the Integrated Public Transport System-IPTS of Bogotá, Colombia as a viable system. Revista de Investigaciones Universidad del Quindío, 34(2), 440–461. https://doi.org/10.33975/riuq.vol34n2.1070",
        "Naciones Unidas. (s. f.). Objetivo 9: Construir infraestructuras resilientes, promover la industrialización inclusiva y sostenible y fomentar la innovación. https://www.un.org/sustainabledevelopment/es/infrastructure/",
        "Osorio Gómez, J. C. (2007). Introducción al pensamiento sistémico. Programa Editorial Universidad del Valle. https://elibro-net.bibliotecavirtual.unad.edu.co/es/ereader/unad/129056?page=10",
    ]
    replace_text(bibliography, refs[0], size=12)
    bibliography.paragraph_format.left_indent = Cm(1.25)
    bibliography.paragraph_format.first_line_indent = Cm(-1.25)
    bibliography.alignment = WD_ALIGN_PARAGRAPH.LEFT
    cursor = bibliography
    for ref in refs[1:]:
        cursor = insert_after(cursor, ref, hanging=True)

    clean = document.add_table(rows=1 + len(HALLAZGOS), cols=2)
    clean.style = "Table Grid"
    for index, text in enumerate(("Herramienta sistémica", "Principal hallazgo obtenido")):
        write_cell(clean.rows[0].cells[index], text, bold=True, size=10, center=True)
    shade_header(clean.rows[0])
    for row_index, values in enumerate(HALLAZGOS):
        for col_index, value in enumerate(values):
            write_cell(clean.rows[row_index + 1].cells[col_index], value, size=10)
    set_widths(clean, [4.2, 11.0])
    ensure_borders(clean)
    document.tables[0]._tbl.getparent().replace(document.tables[0]._tbl, clean._tbl)
    fill_table(document.tables[1], BOULDING, [3.5, 4.8, 7.3], size=9)
    fill_table(
        document.tables[2],
        [[
            "Grok (xAI), consultada el 27 de noviembre de 2026 para esta actividad.",
            PROMPT,
            RESPUESTA_IA,
            CRITICA,
            CONCLUSION_IA,
        ]],
        [3.4, 5.0, 4.6, 5.0, 4.4],
        size=8,
        allow_split=True,
    )
    fill_table(document.tables[3], ESTRATEGIAS, [4.0, 4.2, 3.7, 3.7], size=9)

    tidy_sections(document)
    document.save(DOCX)
    FORO.write_text(FORO_TEXT, encoding="utf-8")
    print("WORDS", counts)
    print("DOCX", DOCX)


def to_pdf():
    profile = Path("/tmp/lo-profile-fase4")
    if profile.exists():
        shutil.rmtree(profile, ignore_errors=True)
    subprocess.run(
        [
            "soffice",
            f"-env:UserInstallation=file://{profile}",
            "--headless",
            "--norestore",
            "--convert-to",
            "pdf",
            "--outdir",
            str(ROOT),
            str(DOCX),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    print("PDF", PDF, PDF.stat().st_size)


if __name__ == "__main__":
    build()
    to_pdf()
