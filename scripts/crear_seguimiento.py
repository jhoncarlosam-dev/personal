#!/usr/bin/env python3
"""Genera el Excel de seguimiento de postulaciones QA / desarrollo.

El libro está pensado para usarse a diario y para entregarse cuando la
búsqueda termina. Las fórmulas van en inglés, que es como Excel las guarda;
un Excel en español las muestra traducidas.
"""

from __future__ import annotations

from pathlib import Path

from openpyxl import Workbook
from openpyxl.chart import BarChart, Reference
from openpyxl.comments import Comment
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import column_index_from_string, get_column_letter
from openpyxl.workbook.properties import CalcProperties
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.worksheet.page import PageMargins

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "Seguimiento de postulaciones.xlsx"

POST_FIRST, POST_LAST = 5, 104
ENT_FIRST, ENT_LAST = 5, 64
OFER_FIRST, OFER_LAST = 5, 16
CONT_FIRST, CONT_LAST = 5, 64

S_POST = "Postulaciones"
S_TAB = "Tablero"
S_ENT = "Entrevistas"
S_OFE = "Ofertas"
S_CON = "Contactos"
S_CIE = "Cierre"
S_LEE = "Léeme"
S_LIS = "Listas"

# Cierre: celdas fijas. El mensaje y las pruebas dependen de estas coordenadas.
C_EMPRESA, C_CARGO = "C5", "E5"
C_AREA, C_MODALIDAD = "C6", "E6"
C_SALARIO, C_MONEDA = "C7", "E7"
C_PERIODO, C_INICIO_LAB = "C8", "E8"
C_CIUDAD, C_CONTACTO_EMP = "C9", "E9"
C_INICIO_BUSQ, C_ACEPTO = "C10", "E10"
C_DIAS_BUSQ, C_MARCADAS = "C11", "E11"
C_ENVIADAS, C_RESP, C_TASA, C_ENTREVISTAS = "B15", "C15", "D15", "E15"
C_OFERTAS, C_TOP, C_TOPN = "B17", "C17", "D17"
C_NOTAS = ("B21", "B23", "B25", "B27", "B29")
C_MENSAJE = "B33"
C_CHECK_FIRST, C_CHECK_LAST = 39, 43
C_STATUS = "B45"

FUNNEL_FIRST = 10
FUENTE_FIRST = 10
AREA_FIRST = 28
CHART_ANCHOR = "B36"
KPI_ROW = 5
SENTENCE_CELL = "B6"

INK = "1C1917"
MUTED = "57534E"
TEAL = "134E4A"
TEAL_SOFT = "E7F0EE"
YELLOW = "FFF4CC"
LINE = "E7E5E4"
LINE_STRONG = "D6D3D1"
WHITE = "FFFFFF"
RED = "9F1239"
RED_BG = "FEE2E2"
AMBER = "92400E"
AMBER_BG = "FEF3C7"
BLUE = "1E3A8A"
BLUE_BG = "E0E7FF"
GREEN = "166534"
GREEN_BG = "DCFCE7"
ORANGE = "9A3412"
ORANGE_BG = "FFEDD5"
GRAY = "A8A29E"
PAPER = "F8FAFC"

THIN = Border(
    left=Side(style="thin", color=LINE),
    right=Side(style="thin", color=LINE),
    top=Side(style="thin", color=LINE),
    bottom=Side(style="thin", color=LINE),
)
HAIR_BOTTOM = Border(bottom=Side(style="thin", color=LINE))
INPUT_BORDER = Border(
    left=Side(style="thin", color="E4D48A"),
    right=Side(style="thin", color="E4D48A"),
    top=Side(style="thin", color="E4D48A"),
    bottom=Side(style="thin", color="E4D48A"),
)

FILL_TEAL = PatternFill("solid", fgColor=TEAL)
FILL_SOFT = PatternFill("solid", fgColor=TEAL_SOFT)
FILL_YELLOW = PatternFill("solid", fgColor=YELLOW)
FILL_WHITE = PatternFill("solid", fgColor=WHITE)
FILL_PAPER = PatternFill("solid", fgColor=PAPER)
FILL_AMBER = PatternFill("solid", fgColor="FFFBEB")
FILL_RED = PatternFill("solid", fgColor="FFF5F5")
FILL_SECTION = PatternFill("solid", fgColor=TEAL)

FONT_TITLE = Font(name="Calibri", size=22, bold=True, color=TEAL)
FONT_HEADER = Font(name="Calibri", size=10, bold=True, color=WHITE)
FONT_BODY = Font(name="Calibri", size=11, color=INK)
FONT_SMALL = Font(name="Calibri", size=10, color=MUTED)
FONT_HINT = Font(name="Calibri", size=9, italic=True, color=MUTED)
FONT_KPI = Font(name="Calibri", size=26, bold=True, color=TEAL)
FONT_SECTION = Font(name="Calibri", size=12, bold=True, color=WHITE)
FONT_LABEL = Font(name="Calibri", size=11, color=MUTED)
FONT_FORMULA = Font(name="Calibri", size=11, color=TEAL)

CENTER = Alignment(horizontal="center", vertical="center", wrap_text=True)
LEFT = Alignment(horizontal="left", vertical="center", wrap_text=False)
LEFT_WRAP = Alignment(horizontal="left", vertical="center", wrap_text=True)
TOP_WRAP = Alignment(horizontal="left", vertical="top", wrap_text=True)

ALERTA_VENCIDA = "Acción vencida"
ALERTA_HOY = "Hoy"
ALERTA_PRONTO = "Pronto"
ALERTA_SEGUIMIENTO = "Hacer seguimiento"
ALERTA_FECHA = "Falta la fecha"
ALERTA_CURSO = "En curso"
ALERTA_CERRADA = "Cerrada"

ENT_HOY = "Hoy"
ENT_MANANA = "Mañana"
ENT_PENDIENTE = "Pasó y sigue pendiente"
ENT_FECHA = "Falta la fecha"
ENT_LISTA = "Lista"
ENT_PROGRAMADA = "Programada"

CERRADOS = (
    "Oferta aceptada",
    "Oferta rechazada",
    "Rechazada",
    "Retirada",
    "Sin respuesta",
)
EN_PROCESO = (
    "Postulada",
    "En revisión",
    "Screening",
    "Prueba técnica",
    "Entrevista técnica",
    "Entrevista final",
    "Oferta recibida",
)
RESPONDIERON = (
    "En revisión",
    "Screening",
    "Prueba técnica",
    "Entrevista técnica",
    "Entrevista final",
    "Oferta recibida",
    "Oferta aceptada",
    "Oferta rechazada",
    "Rechazada",
)
SEGUIMIENTO_ESTADOS = ("Postulada", "En revisión", "Por postular")

ESTADOS = (
    "Por postular",
    "Postulada",
    "En revisión",
    "Screening",
    "Prueba técnica",
    "Entrevista técnica",
    "Entrevista final",
    "Oferta recibida",
    "Oferta aceptada",
    "Oferta rechazada",
    "Rechazada",
    "Retirada",
    "Sin respuesta",
)
FUENTES = (
    "LinkedIn",
    "Get on Board",
    "Referido",
    "Web de la empresa",
    "Me escribió un recruiter",
    "Computrabajo",
    "elempleo",
    "Magneto",
    "Torre",
    "Indeed",
    "Glassdoor",
    "Wellfound",
    "Grupo o comunidad",
    "Feria o evento",
    "Otra",
)
AREAS = ("QA", "Desarrollo", "QA y desarrollo", "Otro")
MODALIDADES = ("Remoto", "Híbrido", "Presencial", "No especifica")

LISTAS = (
    ("ListaArea", "Área", AREAS),
    ("ListaSeniority", "Seniority", ("Trainee", "Junior", "Semi-senior", "Senior", "Lead", "No especifica")),
    ("ListaModalidad", "Modalidad", MODALIDADES),
    ("ListaFuente", "Fuente", FUENTES),
    (
        "ListaCV",
        "CV usado",
        ("CV QA", "CV automatización", "CV desarrollo", "CV fullstack", "CV general", "Sin CV"),
    ),
    ("ListaEstado", "Estado", ESTADOS),
    ("ListaPrioridad", "Prioridad", ("Alta", "Media", "Baja")),
    (
        "ListaPrueba",
        "Prueba",
        (
            "Aún no sé",
            "Ninguna",
            "Preguntas de QA",
            "Caso de prueba",
            "Ejercicio de QA para la casa",
            "Automatización para la casa",
            "Live coding",
            "Ejercicio de código para la casa",
            "System design",
            "Revisión de portafolio",
            "Otra",
        ),
    ),
    (
        "ListaAccion",
        "Próxima acción",
        (
            "Postular",
            "Hacer seguimiento",
            "Responder",
            "Preparar entrevista",
            "Hacer la prueba",
            "Agradecer",
            "Negociar",
            "Decidir la oferta",
            "Archivar",
        ),
    ),
    (
        "ListaRonda",
        "Ronda",
        (
            "Screening con RH",
            "Llamada con reclutador",
            "Entrevista técnica",
            "Prueba en vivo",
            "Entrevista con el jefe",
            "Entrevista final",
            "Conversación de oferta",
        ),
    ),
    (
        "ListaMedio",
        "Medio",
        ("Google Meet", "Zoom", "Microsoft Teams", "Teléfono o WhatsApp", "Presencial", "Otro"),
    ),
    (
        "ListaResultado",
        "Resultado de la entrevista",
        ("Pendiente", "Pasé", "No pasé", "En espera de feedback"),
    ),
    (
        "ListaTipoContacto",
        "Tipo de contacto",
        ("Reclutador", "Jefe del equipo", "Referido", "Mentor", "Otra persona del proceso"),
    ),
    (
        "ListaCompartir",
        "Compartir",
        ("Sí, se puede pasar", "Preguntar antes", "No compartir"),
    ),
    ("ListaDecision", "Decisión", ("Pendiente", "Negociando", "Aceptada", "Rechazada")),
    ("ListaMoneda", "Moneda", ("COP", "USD", "EUR")),
    ("ListaPeriodo", "Periodo", ("Mensual", "Anual")),
    (
        "ListaContrato",
        "Contrato",
        (
            "Indefinido",
            "Término fijo",
            "Obra o labor",
            "Prestación de servicios",
            "Práctica o aprendizaje",
            "No dijeron",
        ),
    ),
    ("ListaSiNo", "Sí o no", ("Sí", "No")),
)


POST_COLS = (
    ("fecha", "Fecha", 15, "date"),
    ("empresa", "Empresa", 26, "text"),
    ("cargo", "Cargo", 32, "text"),
    ("area", "Área", 18, "list:ListaArea"),
    ("seniority", "Seniority", 15, "list:ListaSeniority"),
    ("modalidad", "Modalidad", 16, "list:ListaModalidad"),
    ("ubicacion", "Ubicación", 20, "text"),
    ("fuente", "Fuente", 26, "list:ListaFuente"),
    ("enlace", "Enlace", 28, "text"),
    ("contacto", "Contacto", 20, "text"),
    ("cv", "CV usado", 20, "list:ListaCV"),
    ("estado", "Estado", 20, "list:ListaEstado"),
    ("prioridad", "Prioridad", 12, "list:ListaPrioridad"),
    ("prueba", "Prueba", 34, "list:ListaPrueba"),
    ("salario", "Salario publicado", 22, "text"),
    ("expectativa", "Expectativa", 16, "text"),
    ("ultimo", "Último contacto", 16, "date"),
    ("accion", "Próxima acción", 22, "listwarn:ListaAccion"),
    ("fecha_accion", "Fecha de la acción", 16, "date"),
    ("dias", "Días", 10, "formula"),
    ("alerta", "Alerta", 22, "formula"),
    ("notas", "Notas", 42, "text"),
)
ENT_COLS = (
    ("fecha", "Fecha", 14, "date"),
    ("hora", "Hora", 10, "time"),
    ("empresa", "Empresa", 24, "text"),
    ("cargo", "Cargo", 28, "text"),
    ("ronda", "Ronda", 26, "list:ListaRonda"),
    ("quien", "Con quién", 20, "text"),
    ("medio", "Medio", 22, "list:ListaMedio"),
    ("enlace", "Enlace", 26, "text"),
    ("preparacion", "Preparación", 32, "text"),
    ("resultado", "Resultado", 24, "list:ListaResultado"),
    ("aprendizaje", "Aprendizaje", 42, "text"),
    ("alerta", "Alerta", 26, "formula"),
)
OFER_COLS = (
    ("empresa", "Empresa", 24, "text"),
    ("cargo", "Cargo", 28, "text"),
    ("fecha", "Fecha de la oferta", 16, "date"),
    ("limite", "Responder antes de", 18, "date"),
    ("salario", "Salario base", 16, "money"),
    ("moneda", "Moneda", 12, "list:ListaMoneda"),
    ("periodo", "Periodo", 12, "list:ListaPeriodo"),
    ("contrato", "Contrato", 26, "list:ListaContrato"),
    ("bono", "Bono o variable", 20, "text"),
    ("prestaciones", "Prestaciones", 28, "text"),
    ("modalidad", "Modalidad", 16, "list:ListaModalidad"),
    ("a_favor", "A favor", 28, "text"),
    ("en_contra", "En contra", 28, "text"),
    ("puntaje", "Puntaje", 12, "score"),
    ("decision", "Decisión", 16, "list:ListaDecision"),
    ("notas", "Notas", 28, "text"),
    ("dias", "Días para decidir", 16, "formula"),
)
CONT_COLS = (
    ("nombre", "Nombre", 24, "text"),
    ("empresa", "Empresa", 22, "text"),
    ("tipo", "Tipo", 26, "list:ListaTipoContacto"),
    ("como", "Cómo nos conocimos", 28, "text"),
    ("email", "Email", 28, "text"),
    ("whatsapp", "WhatsApp", 18, "text"),
    ("linkedin", "LinkedIn", 28, "text"),
    ("ultimo", "Último contacto", 16, "date"),
    ("notas", "Notas", 36, "text"),
    ("compartir", "Compartir", 24, "list:ListaCompartir"),
)


def col_index(cols: tuple, key: str) -> int:
    for i, spec in enumerate(cols, start=1):
        if spec[0] == key:
            return i
    raise KeyError(key)


def col_letter(cols: tuple, key: str) -> str:
    return get_column_letter(col_index(cols, key))


def col_range(sheet: str, cols: tuple, key: str, first: int, last: int) -> str:
    letter = col_letter(cols, key)
    return f"{sheet}!${letter}${first}:${letter}${last}"


POST_EMPRESA = col_range(S_POST, POST_COLS, "empresa", POST_FIRST, POST_LAST)
POST_FECHA = col_range(S_POST, POST_COLS, "fecha", POST_FIRST, POST_LAST)
POST_ESTADO = col_range(S_POST, POST_COLS, "estado", POST_FIRST, POST_LAST)
POST_FUENTE = col_range(S_POST, POST_COLS, "fuente", POST_FIRST, POST_LAST)
POST_AREA = col_range(S_POST, POST_COLS, "area", POST_FIRST, POST_LAST)
POST_MODALIDAD = col_range(S_POST, POST_COLS, "modalidad", POST_FIRST, POST_LAST)
POST_DIAS = col_range(S_POST, POST_COLS, "dias", POST_FIRST, POST_LAST)
POST_ALERTA = col_range(S_POST, POST_COLS, "alerta", POST_FIRST, POST_LAST)
ENT_EMPRESA = col_range(S_ENT, ENT_COLS, "empresa", ENT_FIRST, ENT_LAST)
ENT_ALERTA = col_range(S_ENT, ENT_COLS, "alerta", ENT_FIRST, ENT_LAST)
OFER_EMPRESA = col_range(S_OFE, OFER_COLS, "empresa", OFER_FIRST, OFER_LAST)
OFER_DIAS = col_range(S_OFE, OFER_COLS, "dias", OFER_FIRST, OFER_LAST)

SEMANA = f"{S_LIS}!$T$2"
MES = f"{S_LIS}!$T$4"
FUENTE_LAST = FUENTE_FIRST + len(FUENTES) - 1
FUNNEL_LAST = FUNNEL_FIRST + len(ESTADOS)  # incluye la fila Sin estado
FUENTE_ENVIADAS = f"{S_TAB}!$H${FUENTE_FIRST}:$H${FUENTE_LAST}"
FUENTE_NOMBRES = f"{S_TAB}!$G${FUENTE_FIRST}:$G${FUENTE_LAST}"


def check_invariants() -> None:
    keys = [spec[0] for spec in POST_COLS]
    if len(keys) != len(set(keys)):
        raise RuntimeError("Hay columnas repetidas en Postulaciones")
    if set(CERRADOS) - set(ESTADOS):
        raise RuntimeError("Un estado cerrado no está en la lista")
    if set(EN_PROCESO) & set(CERRADOS):
        raise RuntimeError("Un estado no puede estar en proceso y cerrado")
    if set(RESPONDIERON) - set(ESTADOS):
        raise RuntimeError("Una respuesta usa un estado desconocido")
    if set(RESPONDIERON) & {"Postulada", "Por postular", "Sin respuesta", "Retirada"}:
        raise RuntimeError("La tasa de respuesta está mezclando estados")
    if len(ESTADOS) != 13 or len(FUENTES) != 15:
        raise RuntimeError("El tablero espera 13 estados y 15 fuentes")


def apply_page(ws, orientation: str = "landscape", fit_height: int = 0, repeat_rows: str | None = "1:4") -> None:
    ws.page_setup.orientation = orientation
    ws.page_setup.paperSize = ws.PAPERSIZE_A4
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = fit_height
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.page_margins = PageMargins(left=0.45, right=0.45, top=0.6, bottom=0.55, header=0.2, footer=0.28)
    ws.print_options.horizontalCentered = True
    ws.page_setup.horizontalCentered = True
    ws.sheet_view.showGridLines = False
    ws.sheet_view.zoomScale = 110
    ws.sheet_view.view = "normal"
    ws.oddFooter.left.text = "Seguimiento de postulaciones · QA o desarrollo"
    ws.oddFooter.right.text = "Página &P de &N"
    ws.sheet_properties.tabColor = TEAL
    if repeat_rows:
        ws.print_title_rows = repeat_rows
    ws.sheet_format.defaultRowHeight = 20
    ws.sheet_view.showZeros = True


def write_title_block(
    ws,
    title: str,
    instruction: str,
    last_col: int,
    frozen_until: str,
    legend: str | None,
) -> None:
    """La instrucción queda dentro de las columnas congeladas para que no se parta."""
    ws.freeze_panes = frozen_until
    freeze_letter = "".join(ch for ch in frozen_until if ch.isalpha())
    frozen_cols = max(column_index_from_string(freeze_letter) - 1, 1)
    instruction_cols = last_col if frozen_cols == 0 else frozen_cols
    if frozen_until.startswith("A"):
        instruction_cols = last_col
    ws.row_dimensions[1].height = 30
    ws.row_dimensions[2].height = 48
    cell = ws.cell(1, 1, title)
    cell.font = FONT_TITLE
    cell.alignment = Alignment(horizontal="left", vertical="center")
    for col in range(1, last_col + 1):
        ws.cell(1, col).border = Border(bottom=Side(style="medium", color=TEAL))
    target = ws.cell(2, 1, instruction)
    target.font = FONT_SMALL
    target.alignment = LEFT_WRAP
    if instruction_cols > 1:
        ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=instruction_cols)
    if legend and instruction_cols > 1:
        ws.row_dimensions[3].height = 18
        note = ws.cell(3, 1, legend)
        note.font = FONT_HINT
        note.alignment = LEFT
        ws.merge_cells(start_row=3, start_column=1, end_row=3, end_column=instruction_cols)
    else:
        ws.row_dimensions[3].height = 8


def write_headers(ws, cols: tuple, row: int = 4) -> None:
    ws.row_dimensions[row].height = 36
    for i, (_, header, width, kind) in enumerate(cols, start=1):
        cell = ws.cell(row, i, header)
        cell.font = FONT_HEADER
        cell.fill = FILL_TEAL
        cell.alignment = CENTER
        ws.column_dimensions[get_column_letter(i)].width = width
        if kind == "formula":
            cell.fill = PatternFill("solid", fgColor="0F3D38")


def style_data_rows(ws, cols: tuple, first: int, last: int) -> None:
    for row in range(first, last + 1):
        ws.row_dimensions[row].height = 20
        for i, (_, _, _, kind) in enumerate(cols, start=1):
            cell = ws.cell(row, i)
            cell.font = FONT_FORMULA if kind == "formula" else FONT_BODY
            cell.alignment = CENTER if kind in {"date", "time", "formula", "score", "money"} else LEFT
            cell.border = HAIR_BOTTOM
            if kind == "formula":
                cell.fill = FILL_SOFT
            if kind == "date":
                cell.number_format = "DD/MM/YYYY"
            elif kind == "time":
                cell.number_format = "HH:MM"
            elif kind == "money":
                cell.number_format = '#,##0'
            elif kind == "score":
                cell.number_format = "0"


def add_list_validation(ws, formula: str, sqref: str, warning: bool = False) -> None:
    if formula.startswith("="):
        formula = formula[1:]
    dv = DataValidation(type="list", formula1=formula, allow_blank=True)
    dv.showInputMessage = False
    dv.showErrorMessage = True
    if warning:
        dv.errorStyle = "warning"
        dv.errorTitle = "Puedes escribir otra"
        dv.error = "La lista es una ayuda. Si la acción es distinta, puedes dejar tu propio texto."
    else:
        dv.errorStyle = "stop"
        dv.errorTitle = "Elige una opción"
        dv.error = "Usa la lista. Si falta una opción, agrégala en la hoja Listas insertando una celda dentro de la columna, no debajo de la última."
    dv.add(sqref)
    ws.add_data_validation(dv)


def add_date_validation(ws, sqref: str) -> None:
    dv = DataValidation(
        type="date",
        operator="between",
        formula1="DATE(2024,1,1)",
        formula2="DATE(2036,12,31)",
        allow_blank=True,
    )
    dv.showInputMessage = False
    dv.showErrorMessage = True
    dv.errorStyle = "stop"
    dv.errorTitle = "Fecha"
    dv.error = "Escribe una fecha real. En este archivo el formato es día/mes/año."
    for ref in sqref.split():
        dv.add(ref)
    ws.add_data_validation(dv)


def add_validations(ws, cols: tuple, first: int, last: int, listas: dict[str, str]) -> None:
    for i, (_, _, _, kind) in enumerate(cols, start=1):
        letter = get_column_letter(i)
        sqref = f"{letter}{first}:{letter}{last}"
        if kind == "date":
            add_date_validation(ws, sqref)
        elif kind.startswith("list"):
            name = kind.split(":", 1)[1]
            add_list_validation(ws, f"={listas[name]}", sqref, warning=kind.startswith("listwarn"))
        elif kind == "score":
            dv = DataValidation(type="whole", operator="between", formula1="1", formula2="10", allow_blank=True)
            dv.showInputMessage = False
            dv.showErrorMessage = True
            dv.errorStyle = "stop"
            dv.errorTitle = "Puntaje"
            dv.error = "Pon un número del 1 al 10."
            dv.add(sqref)
            ws.add_data_validation(dv)
        elif kind == "money":
            dv = DataValidation(type="decimal", operator="greaterThanOrEqual", formula1="0", allow_blank=True)
            dv.showInputMessage = False
            dv.showErrorMessage = True
            dv.errorStyle = "warning"
            dv.errorTitle = "Salario"
            dv.error = "Escríbelo en número, sin puntos ni texto. Ejemplo: 5000000. Si aún no lo sabes, déjalo vacío."
            dv.add(sqref)
            ws.add_data_validation(dv)


def formula_rule(
    formula: str,
    fill: str | None = None,
    color: str | None = None,
    bold: bool = False,
    size: int = 11,
) -> FormulaRule:
    font = Font(name="Calibri", size=size, color=color or INK, bold=bold) if color or bold else None
    pattern = PatternFill("solid", fgColor=fill) if fill else None
    return FormulaRule(formula=[formula], fill=pattern, font=font)


def end_hint(ws, row: int, last_col: int, text: str) -> None:
    cell = ws.cell(row, 1, text)
    cell.font = FONT_HINT
    cell.alignment = LEFT_WRAP
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=min(last_col, 8))
    ws.row_dimensions[row].height = 32


def dias_formula(row: int) -> str:
    fecha = f"{col_letter(POST_COLS, 'fecha')}{row}"
    empresa = f"{col_letter(POST_COLS, 'empresa')}{row}"
    ultimo = f"{col_letter(POST_COLS, 'ultimo')}{row}"
    return f'=IF(OR({empresa}="",{fecha}=""),"",MAX(0,TODAY()-IF({ultimo}="",{fecha},MAX({fecha},{ultimo}))))'


def alerta_formula(row: int) -> str:
    fecha = f"{col_letter(POST_COLS, 'fecha')}{row}"
    empresa = f"{col_letter(POST_COLS, 'empresa')}{row}"
    estado = f"{col_letter(POST_COLS, 'estado')}{row}"
    accion = f"{col_letter(POST_COLS, 'fecha_accion')}{row}"
    dias = f"{col_letter(POST_COLS, 'dias')}{row}"
    closed = ",".join(f'{estado}="{item}"' for item in CERRADOS)
    follow = ",".join(f'{estado}="{item}"' for item in SEGUIMIENTO_ESTADOS)
    return (
        f'=IF({empresa}="","",'
        f'IF(OR({closed}),"{ALERTA_CERRADA}",'
        f'IF(AND({accion}<>"",{accion}<TODAY()),"{ALERTA_VENCIDA}",'
        f'IF(AND({accion}<>"",{accion}=TODAY()),"{ALERTA_HOY}",'
        f'IF(AND({accion}<>"",{accion}<=TODAY()+2),"{ALERTA_PRONTO}",'
        f'IF({fecha}="","{ALERTA_FECHA}",'
        f'IF(AND(OR({follow},{estado}=""),{dias}>=10),"{ALERTA_SEGUIMIENTO}",'
        f'"{ALERTA_CURSO}")))))))'
    )


def entrevista_alerta_formula(row: int) -> str:
    fecha = f"A{row}"
    empresa = f"C{row}"
    resultado = f"J{row}"
    return (
        f'=IF({empresa}="","",'
        f'IF(OR({resultado}="Pasé",{resultado}="No pasé"),"{ENT_LISTA}",'
        f'IF({fecha}="","{ENT_FECHA}",'
        f'IF({fecha}<TODAY(),"{ENT_PENDIENTE}",'
        f'IF({fecha}=TODAY(),"{ENT_HOY}",'
        f'IF({fecha}=TODAY()+1,"{ENT_MANANA}","{ENT_PROGRAMADA}"))))))'
    )


def oferta_dias_formula(row: int) -> str:
    limite = f"D{row}"
    decision = f"O{row}"
    return f'=IF(OR({limite}="",{decision}="Aceptada",{decision}="Rechazada"),"",{limite}-TODAY())'


def count_states(range_ref: str, states: tuple[str, ...], extra_criteria: str = "") -> str:
    parts = []
    for state in states:
        criteria = f'{range_ref},"{state}"'
        if extra_criteria:
            criteria = f"{extra_criteria},{criteria}"
        parts.append(f"COUNTIFS({criteria})" if extra_criteria else f'COUNTIF({range_ref},"{state}")')
    return "+".join(parts)


def respuesta_por_fuente(cell: str) -> str:
    return "=" + count_states(POST_ESTADO, RESPONDIERON, extra_criteria=f"{POST_FUENTE},{cell}")


def enviadas_formula(extra: str = "") -> str:
    base = f'COUNTIFS({POST_EMPRESA},"<>",{POST_ESTADO},"<>Por postular",{POST_ESTADO},"<>"'
    if extra:
        return f"={base},{extra})"
    return f"={base})"


def build_listas(wb: Workbook) -> dict[str, str]:
    ws = wb.create_sheet(S_LIS)
    apply_page(ws, orientation="landscape", fit_height=1, repeat_rows=None)
    ws.sheet_properties.tabColor = "78716C"
    ranges: dict[str, str] = {}
    ws.row_dimensions[1].height = 24
    for col, (name, header, values) in enumerate(LISTAS, start=1):
        header_cell = ws.cell(1, col, header)
        header_cell.font = FONT_HEADER
        header_cell.fill = FILL_TEAL
        header_cell.alignment = CENTER
        ws.column_dimensions[get_column_letter(col)].width = 28
        for offset, value in enumerate(values):
            cell = ws.cell(2 + offset, col, value)
            cell.font = FONT_BODY
            cell.alignment = LEFT
            cell.border = HAIR_BOTTOM
        last = 1 + len(values)
        ranges[name] = f"{S_LIS}!${get_column_letter(col)}$2:${get_column_letter(col)}${last}"
    ws["T1"] = "Inicio de esta semana"
    ws["T2"] = "=TODAY()-WEEKDAY(TODAY(),2)+1"
    ws["T3"] = "Inicio de este mes"
    ws["T4"] = "=DATE(YEAR(TODAY()),MONTH(TODAY()),1)"
    for coord in ("T1", "T3"):
        ws[coord].font = FONT_HINT
    for coord in ("T2", "T4"):
        ws[coord].font = FONT_FORMULA
        ws[coord].fill = FILL_SOFT
        ws[coord].number_format = "DD/MM/YYYY"
    ws.column_dimensions["T"].width = 28
    ws.merge_cells("A18:G21")
    note = ws["A18"]
    note.value = (
        "Estas columnas alimentan los desplegables. Hay más listas a la derecha. Para agregar una opción: clic derecho en una celda de esa columna, "
        "Insertar, Desplazar celdas hacia abajo, y escribe. Tiene que quedar entre la primera y la última opción. "
        "Si la escribes debajo, el menú no la muestra. No dejes huecos y no le cambies el nombre a una opción que ya usaste: "
        "el Tablero dejaría de contarla. Las fechas de la columna T las usa el Tablero: no las borres."
    )
    note.font = FONT_BODY
    note.alignment = TOP_WRAP
    ws.row_dimensions[18].height = 24
    ws.row_dimensions[19].height = 24
    ws.row_dimensions[20].height = 24
    ws.row_dimensions[21].height = 24
    ws.auto_filter.ref = None
    ws.freeze_panes = "A2"
    return ranges


def build_postulaciones(wb: Workbook, listas: dict[str, str]) -> None:
    ws = wb.active
    ws.title = S_POST
    apply_page(ws, orientation="landscape", fit_height=0, repeat_rows="1:4")
    ws.sheet_properties.tabColor = TEAL
    last_col = len(POST_COLS)
    write_title_block(
        ws,
        "Postulaciones",
        "Una fila por vacante. En Alerta, abre la flecha y atiende Acción vencida y Hoy. Al filtrar, las filas vacías se ocultan.",
        last_col,
        "D5",
        "El verde se calcula solo. La guía está en la hoja Léeme.",
    )
    write_headers(ws, POST_COLS)
    style_data_rows(ws, POST_COLS, POST_FIRST, POST_LAST)
    dias_col = col_index(POST_COLS, "dias")
    alerta_col = col_index(POST_COLS, "alerta")
    for row in range(POST_FIRST, POST_LAST + 1):
        ws.cell(row, dias_col, dias_formula(row))
        ws.cell(row, alerta_col, alerta_formula(row))
    add_validations(ws, POST_COLS, POST_FIRST, POST_LAST, listas)
    ws.auto_filter.ref = f"A4:{get_column_letter(last_col)}{POST_LAST}"
    expect = ws.cell(4, col_index(POST_COLS, "expectativa"))
    expect.comment = Comment(
        "Opcional. Antes de pasar el archivo, borra lo que no quieras que otra persona lea.",
        "Guía",
        width=240,
        height=55,
    )
    alerta_header = col_letter(POST_COLS, "alerta")
    rules = (
        (f'${alerta_header}{POST_FIRST}="{ALERTA_VENCIDA}"', RED_BG, RED, True),
        (f'${alerta_header}{POST_FIRST}="{ALERTA_HOY}"', AMBER_BG, AMBER, True),
        (f'${alerta_header}{POST_FIRST}="{ALERTA_PRONTO}"', BLUE_BG, BLUE, False),
        (f'${alerta_header}{POST_FIRST}="{ALERTA_SEGUIMIENTO}"', ORANGE_BG, ORANGE, True),
        (f'${alerta_header}{POST_FIRST}="{ALERTA_FECHA}"', AMBER_BG, AMBER, False),
        (f'${alerta_header}{POST_FIRST}="{ALERTA_CERRADA}"', None, GRAY, False),
        (f'${alerta_header}{POST_FIRST}="{ALERTA_CURSO}"', None, TEAL, False),
    )
    alerta_range = f"{alerta_header}{POST_FIRST}:{alerta_header}{POST_LAST}"
    for formula, fill, color, bold in rules:
        ws.conditional_formatting.add(alerta_range, formula_rule(formula, fill, color, bold))
    estado = col_letter(POST_COLS, "estado")
    estado_range = f"{estado}{POST_FIRST}:{estado}{POST_LAST}"
    ws.conditional_formatting.add(estado_range, formula_rule(f'${estado}{POST_FIRST}="Oferta aceptada"', GREEN_BG, GREEN, True))
    ws.conditional_formatting.add(estado_range, formula_rule(f'${estado}{POST_FIRST}="Oferta recibida"', AMBER_BG, AMBER, True))
    for state in ("Oferta rechazada", "Rechazada", "Retirada", "Sin respuesta"):
        ws.conditional_formatting.add(estado_range, formula_rule(f'${estado}{POST_FIRST}="{state}"', None, GRAY, False))
    for state in ("Entrevista técnica", "Entrevista final"):
        ws.conditional_formatting.add(estado_range, formula_rule(f'${estado}{POST_FIRST}="{state}"', None, BLUE, True))
    ws.conditional_formatting.add(estado_range, formula_rule(f'${estado}{POST_FIRST}="Prueba técnica"', None, ORANGE, True))
    prioridad = col_letter(POST_COLS, "prioridad")
    prioridad_range = f"{prioridad}{POST_FIRST}:{prioridad}{POST_LAST}"
    ws.conditional_formatting.add(prioridad_range, formula_rule(f'${prioridad}{POST_FIRST}="Alta"', None, RED, True))
    ws.conditional_formatting.add(prioridad_range, formula_rule(f'${prioridad}{POST_FIRST}="Baja"', None, GRAY, False))
    end_hint(
        ws,
        POST_LAST + 2,
        last_col,
        "Hay 100 filas listas. Si necesitas otra, clic derecho en la fila 104, Insertar. Así la fila nueva sigue contando en el Tablero.",
    )
    ws.page_setup.fitToHeight = 0
    ws.sheet_view.zoomScale = 110


def build_entrevistas(wb: Workbook, listas: dict[str, str]) -> None:
    ws = wb.create_sheet(S_ENT)
    apply_page(ws, orientation="landscape", fit_height=0)
    ws.sheet_properties.tabColor = "1D4ED8"
    last_col = len(ENT_COLS)
    write_title_block(
        ws,
        "Entrevistas",
        "Una fila por entrevista, no por empresa. Al salir, escribe qué aprendiste: eso es lo que más le sirve a quien reciba el archivo.",
        last_col,
        "E5",
        "El verde se calcula solo. La guía está en la hoja Léeme.",
    )
    write_headers(ws, ENT_COLS)
    style_data_rows(ws, ENT_COLS, ENT_FIRST, ENT_LAST)
    alerta_col = col_index(ENT_COLS, "alerta")
    for row in range(ENT_FIRST, ENT_LAST + 1):
        ws.cell(row, alerta_col, entrevista_alerta_formula(row))
    add_validations(ws, ENT_COLS, ENT_FIRST, ENT_LAST, listas)
    ws.auto_filter.ref = f"A4:{get_column_letter(last_col)}{ENT_LAST}"
    alerta = col_letter(ENT_COLS, "alerta")
    alerta_range = f"{alerta}{ENT_FIRST}:{alerta}{ENT_LAST}"
    for formula, fill, color, bold in (
        (f'${alerta}{ENT_FIRST}="{ENT_HOY}"', AMBER_BG, AMBER, True),
        (f'${alerta}{ENT_FIRST}="{ENT_MANANA}"', BLUE_BG, BLUE, False),
        (f'${alerta}{ENT_FIRST}="{ENT_PENDIENTE}"', RED_BG, RED, True),
        (f'${alerta}{ENT_FIRST}="{ENT_FECHA}"', AMBER_BG, AMBER, False),
        (f'${alerta}{ENT_FIRST}="{ENT_LISTA}"', None, GRAY, False),
        (f'${alerta}{ENT_FIRST}="{ENT_PROGRAMADA}"', None, TEAL, False),
    ):
        ws.conditional_formatting.add(alerta_range, formula_rule(formula, fill, color, bold))
    end_hint(
        ws,
        ENT_LAST + 2,
        last_col,
        "Hay 60 filas. Para otra, clic derecho en la fila 64, Insertar. No escribas debajo de esa fila: el Tablero no la vería.",
    )


def build_ofertas(wb: Workbook, listas: dict[str, str]) -> None:
    ws = wb.create_sheet(S_OFE)
    apply_page(ws, orientation="landscape", fit_height=1)
    ws.sheet_properties.tabColor = GREEN
    last_col = len(OFER_COLS)
    write_title_block(
        ws,
        "Ofertas",
        "Una fila por oferta, antes de responder. Si una es prestación de servicios y otra es nómina, el salario no se compara directo: en prestación, seguridad social y prestaciones salen de tu bolsillo. El salario va en número, sin puntos.",
        last_col,
        "A5",
        "La columna verde se calcula sola.",
    )
    write_headers(ws, OFER_COLS)
    style_data_rows(ws, OFER_COLS, OFER_FIRST, OFER_LAST)
    dias_col = col_index(OFER_COLS, "dias")
    for row in range(OFER_FIRST, OFER_LAST + 1):
        ws.cell(row, dias_col, oferta_dias_formula(row))
        ws.cell(row, dias_col).number_format = "0"
        ws.cell(row, dias_col).alignment = CENTER
    add_validations(ws, OFER_COLS, OFER_FIRST, OFER_LAST, listas)
    ws.auto_filter.ref = f"A4:{get_column_letter(last_col)}{OFER_LAST}"
    dias = col_letter(OFER_COLS, "dias")
    dias_range = f"{dias}{OFER_FIRST}:{dias}{OFER_LAST}"
    ws.conditional_formatting.add(dias_range, formula_rule(f"AND({dias}{OFER_FIRST}<>\"\",{dias}{OFER_FIRST}<0)", RED_BG, RED, True))
    ws.conditional_formatting.add(dias_range, formula_rule(f"AND({dias}{OFER_FIRST}<>\"\",{dias}{OFER_FIRST}=0)", AMBER_BG, AMBER, True))
    ws.conditional_formatting.add(
        dias_range,
        formula_rule(f"AND({dias}{OFER_FIRST}>0,{dias}{OFER_FIRST}<=3)", BLUE_BG, BLUE, False),
    )
    decision = col_letter(OFER_COLS, "decision")
    decision_range = f"{decision}{OFER_FIRST}:{decision}{OFER_LAST}"
    ws.conditional_formatting.add(decision_range, formula_rule(f'{decision}{OFER_FIRST}="Aceptada"', GREEN_BG, GREEN, True))
    ws.conditional_formatting.add(decision_range, formula_rule(f'{decision}{OFER_FIRST}="Rechazada"', None, GRAY, False))
    end_hint(ws, OFER_LAST + 2, last_col, "Hay 12 filas. Para comparar otra oferta, clic derecho en la fila 16, Insertar.")


def build_contactos(wb: Workbook, listas: dict[str, str]) -> None:
    ws = wb.create_sheet(S_CON)
    apply_page(ws, orientation="landscape", fit_height=0)
    ws.sheet_properties.tabColor = "7C3AED"
    last_col = len(CONT_COLS)
    write_title_block(
        ws,
        "Contactos",
        "En Compartir, «Sí, se puede pasar» solo si esa persona está de acuerdo. Si dudas, elige Preguntar antes y no dejes el teléfono.",
        last_col,
        "C5",
        "La guía está en la hoja Léeme.",
    )
    write_headers(ws, CONT_COLS)
    style_data_rows(ws, CONT_COLS, CONT_FIRST, CONT_LAST)
    add_validations(ws, CONT_COLS, CONT_FIRST, CONT_LAST, listas)
    ws.auto_filter.ref = f"A4:{get_column_letter(last_col)}{CONT_LAST}"
    compartir = col_letter(CONT_COLS, "compartir")
    compartir_range = f"{compartir}{CONT_FIRST}:{compartir}{CONT_LAST}"
    ws.conditional_formatting.add(
        compartir_range,
        formula_rule(f'{compartir}{CONT_FIRST}="Sí, se puede pasar"', GREEN_BG, GREEN, True),
    )
    ws.conditional_formatting.add(
        compartir_range,
        formula_rule(f'{compartir}{CONT_FIRST}="Preguntar antes"', AMBER_BG, AMBER, False),
    )
    ws.conditional_formatting.add(
        compartir_range,
        formula_rule(f'{compartir}{CONT_FIRST}="No compartir"', None, GRAY, False),
    )
    header = ws.cell(4, col_index(CONT_COLS, "compartir"))
    header.comment = Comment(
        "Sí, se puede pasar: esa persona sabe que puedes compartir su contacto. Si no estás seguro, Preguntar antes.",
        "Guía",
        width=260,
        height=60,
    )
    end_hint(ws, CONT_LAST + 2, last_col, "Hay 60 filas. Para otra, clic derecho en la fila 64, Insertar.")


def section_title(ws, cell: str, text: str) -> None:
    ws[cell] = text
    ws[cell].font = Font(name="Calibri", size=14, bold=True, color=TEAL)
    ws[cell].alignment = LEFT


def build_tablero(wb: Workbook) -> None:
    ws = wb.create_sheet(S_TAB, 1)
    apply_page(ws, orientation="landscape", fit_height=1, repeat_rows=None)
    ws.sheet_properties.tabColor = "0F766E"
    widths = {
        "A": 3,
        "B": 26,
        "C": 18,
        "D": 16,
        "E": 18,
        "F": 3,
        "G": 32,
        "H": 14,
        "I": 16,
        "J": 14,
    }
    for letter, width in widths.items():
        ws.column_dimensions[letter].width = width
    ws.row_dimensions[1].height = 30
    ws["A1"] = "Tablero"
    ws["A1"].font = FONT_TITLE
    ws.merge_cells("A1:C1")
    ws["D1"] = "Se actualiza solo. Por la mañana mira Para hoy y Vencidas."
    ws["D1"].font = FONT_SMALL
    ws["D1"].alignment = LEFT
    ws.merge_cells("D1:J1")
    for col in range(1, 11):
        ws.cell(1, col).border = Border(bottom=Side(style="medium", color=TEAL))

    ws.merge_cells("B3:J3")
    ws["B3"] = '=IF(COUNTIF(' + POST_EMPRESA + ',"<>")+COUNTIF(' + ENT_EMPRESA + ',"<>")+COUNTIF(' + OFER_EMPRESA + ',"<>")=0,"Todavía no hay nada anotado. Empieza por una fila en Postulaciones.","")'
    ws["B3"].font = FONT_HINT
    ws["B3"].alignment = LEFT
    ws.row_dimensions[3].height = 18

    labels = (
        (2, "Para hoy", FILL_AMBER),
        (3, "Vencidas", FILL_RED),
        (4, "Por postular", None),
        (5, "Seguimiento", None),
        (7, "En proceso", None),
        (8, "Enviadas", None),
        (9, "Respondieron", None),
        (10, "Ofertas", None),
    )
    ws.row_dimensions[4].height = 30
    ws.row_dimensions[KPI_ROW].height = 38
    for col, label, fill in labels:
        label_cell = ws.cell(4, col, label)
        label_cell.font = Font(name="Calibri", size=9, bold=True, color=MUTED)
        label_cell.alignment = CENTER
        number = ws.cell(KPI_ROW, col, None)
        number.font = FONT_KPI
        number.alignment = CENTER
        if fill is not None:
            label_cell.fill = fill
            number.fill = fill

    ws["B5"] = (
        f'=COUNTIF({POST_ALERTA},"{ALERTA_HOY}")'
        f'+COUNTIF({ENT_ALERTA},"{ENT_HOY}")'
        f'+COUNTIFS({OFER_DIAS},0,{OFER_EMPRESA},"<>")'
    )
    ws["C5"] = (
        f'=COUNTIF({POST_ALERTA},"{ALERTA_VENCIDA}")'
        f'+COUNTIF({ENT_ALERTA},"{ENT_PENDIENTE}")'
        f'+COUNTIFS({OFER_DIAS},"<0",{OFER_EMPRESA},"<>")'
    )
    ws["D5"] = f'=COUNTIF({POST_ESTADO},"Por postular")'
    ws["E5"] = f'=COUNTIF({POST_ALERTA},"{ALERTA_SEGUIMIENTO}")'
    ws["G5"] = "=" + count_states(POST_ESTADO, EN_PROCESO)
    ws["H5"] = enviadas_formula()
    ws["I5"] = "=" + count_states(POST_ESTADO, RESPONDIERON)
    ws["J5"] = (
        f'=COUNTIF({POST_ESTADO},"Oferta recibida")'
        f'+COUNTIF({POST_ESTADO},"Oferta aceptada")'
        f'+COUNTIF({POST_ESTADO},"Oferta rechazada")'
    )
    for coord in ("B5", "C5", "D5", "E5", "G5", "H5", "I5", "J5"):
        ws[coord].number_format = "0"
    ws.conditional_formatting.add("B5", formula_rule("B5>0", None, AMBER, True, size=26))
    ws.conditional_formatting.add("C5", formula_rule("C5>0", None, RED, True, size=26))

    ws.merge_cells("B6:J6")
    ws["B6"] = (
        f'=IF(COUNTIF({POST_EMPRESA},"<>")+COUNTIF({ENT_EMPRESA},"<>")+COUNTIF({OFER_EMPRESA},"<>")=0,"",'
        f'"Postulaciones que tocan hoy: "&COUNTIF({POST_ALERTA},"{ALERTA_HOY}")'
        f'&". Entrevistas hoy: "&COUNTIF({ENT_ALERTA},"{ENT_HOY}")'
        f'&". Ofertas que vencen hoy: "&COUNTIFS({OFER_DIAS},0,{OFER_EMPRESA},"<>")'
        f'&". Acciones en 48 h: "&COUNTIF({POST_ALERTA},"{ALERTA_PRONTO}")'
        f'&". Entrevistas mañana: "&COUNTIF({ENT_ALERTA},"{ENT_MANANA}")'
        f'&". Enviadas esta semana: "&COUNTIFS({POST_FECHA},">="&{SEMANA},{POST_EMPRESA},"<>",{POST_ESTADO},"<>Por postular",{POST_ESTADO},"<>")'
        f'&". Este mes: "&COUNTIFS({POST_FECHA},">="&{MES},{POST_EMPRESA},"<>",{POST_ESTADO},"<>Por postular",{POST_ESTADO},"<>")'
        f'&". Promedio en curso: "&IFERROR(ROUND(AVERAGEIFS({POST_DIAS},{POST_ALERTA},"<>{ALERTA_CERRADA}",{POST_ALERTA},"<>"),0)&" días.","sin datos."))'
    )
    ws["B6"].font = FONT_SMALL
    ws["B6"].alignment = LEFT_WRAP
    ws.row_dimensions[6].height = 48

    ws.row_dimensions[8].height = 22
    section_title(ws, "B8", "Embudo")
    section_title(ws, "G8", "Por fuente")
    headers = ((2, "Estado"), (3, "Cantidad"), (4, "%"), (5, ""), (7, "Fuente"), (8, "Enviadas"), (9, "Con respuesta"), (10, "Tasa"))
    for col, text in headers:
        cell = ws.cell(9, col, text)
        cell.font = FONT_HEADER
        cell.fill = FILL_TEAL
        cell.alignment = CENTER
    ws.row_dimensions[9].height = 22

    for offset, estado in enumerate(ESTADOS):
        row = FUNNEL_FIRST + offset
        ws.row_dimensions[row].height = 18
        ws.cell(row, 2, estado).font = FONT_BODY
        ws.cell(row, 2).alignment = LEFT
        count = ws.cell(row, 3, f'=COUNTIF({POST_ESTADO},B{row})')
        count.font = FONT_BODY
        count.alignment = CENTER
        count.number_format = "0"
        part = ws.cell(row, 4, f'=IF($C$24=0,"",C{row}/$C$24)')
        part.font = FONT_SMALL
        part.alignment = CENTER
        part.number_format = "0%"
        bar = ws.cell(
            row,
            5,
            f'=IF(OR(C{row}=0,MAX($C${FUNNEL_FIRST}:$C${FUNNEL_LAST})=0),"",REPT("█",MAX(1,ROUND(C{row}/MAX($C${FUNNEL_FIRST}:$C${FUNNEL_LAST})*12,0))))',
        )
        bar.font = Font(name="Calibri", size=10, color=TEAL)
        bar.alignment = LEFT
        if estado == "Oferta aceptada":
            bar.font = Font(name="Calibri", size=10, color=GREEN)
        elif estado in {"Oferta rechazada", "Rechazada", "Retirada", "Sin respuesta"}:
            bar.font = Font(name="Calibri", size=10, color=GRAY)
            ws.cell(row, 2).font = Font(name="Calibri", size=11, color=GRAY)

    sin_row = FUNNEL_FIRST + len(ESTADOS)
    ws.row_dimensions[sin_row].height = 18
    ws.cell(sin_row, 2, "Sin estado").font = Font(name="Calibri", size=11, italic=True, color=MUTED)
    ws.cell(sin_row, 3, f'=COUNTIFS({POST_EMPRESA},"<>",{POST_ESTADO},"")')
    ws.cell(sin_row, 3).font = FONT_BODY
    ws.cell(sin_row, 3).alignment = CENTER
    ws.cell(sin_row, 3).number_format = "0"
    ws.cell(sin_row, 4, f'=IF($C$24=0,"",C{sin_row}/$C$24)')
    ws.cell(sin_row, 4).number_format = "0%"
    ws.cell(sin_row, 4).font = FONT_SMALL
    ws.cell(sin_row, 4).alignment = CENTER
    ws.cell(
        sin_row,
        5,
        f'=IF(OR(C{sin_row}=0,MAX($C${FUNNEL_FIRST}:$C${FUNNEL_LAST})=0),"",REPT("█",MAX(1,ROUND(C{sin_row}/MAX($C${FUNNEL_FIRST}:$C${FUNNEL_LAST})*12,0))))',
    )
    ws.cell(sin_row, 5).font = Font(name="Calibri", size=10, color=GRAY)

    total_row = sin_row + 1
    ws.cell(total_row, 2, "Total").font = Font(name="Calibri", size=11, bold=True, color=INK)
    ws.cell(total_row, 3, f"=SUM(C{FUNNEL_FIRST}:C{sin_row})")
    ws.cell(total_row, 3).font = Font(name="Calibri", size=12, bold=True, color=TEAL)
    ws.cell(total_row, 3).alignment = CENTER
    ws.cell(total_row, 3).number_format = "0"
    ws.merge_cells(start_row=total_row + 1, start_column=2, end_row=total_row + 1, end_column=5)
    ws.cell(
        total_row + 1,
        2,
        f'=IF(C{total_row}=COUNTIF({POST_EMPRESA},"<>"),"","Hay un estado escrito a mano y esa fila no entra en el embudo.")',
    )
    ws.cell(total_row + 1, 2).font = Font(name="Calibri", size=9, color=RED)

    for offset, fuente in enumerate(FUENTES):
        row = FUENTE_FIRST + offset
        ws.row_dimensions[row].height = 18
        ws.cell(row, 7, fuente).font = FONT_BODY
        ws.cell(row, 7).alignment = LEFT
        enviadas = ws.cell(
            row,
            8,
            f'=COUNTIFS({POST_FUENTE},G{row},{POST_ESTADO},"<>Por postular",{POST_ESTADO},"<>")',
        )
        enviadas.font = FONT_BODY
        enviadas.alignment = CENTER
        enviadas.number_format = "0"
        respuesta = ws.cell(row, 9, respuesta_por_fuente(f"G{row}"))
        respuesta.font = FONT_BODY
        respuesta.alignment = CENTER
        respuesta.number_format = "0"
        tasa = ws.cell(row, 10, f'=IF(H{row}=0,"",I{row}/H{row})')
        tasa.font = FONT_SMALL
        tasa.alignment = CENTER
        tasa.number_format = "0%"
    ws.merge_cells("G26:J26")
    ws["G26"] = (
        f'=IF(SUM(H{FUENTE_FIRST}:H{FUENTE_LAST})=H5,"","Hay enviadas sin una fuente de la lista, vacía o escrita a mano.")'
    )
    ws["G26"].font = Font(name="Calibri", size=9, color=RED)

    section_title(ws, "B27", "Por área")
    section_title(ws, "D27", "Por modalidad")
    ws["G27"] = "Fuente más usada"
    ws["G27"].font = FONT_LABEL
    ws["H27"] = f'=IF(COUNTIF({POST_EMPRESA},"<>")=0,"",IF(MAX({FUENTE_ENVIADAS})=0,"",INDEX({FUENTE_NOMBRES},MATCH(MAX({FUENTE_ENVIADAS}),{FUENTE_ENVIADAS},0))))'
    ws["H27"].font = Font(name="Calibri", size=12, bold=True, color=TEAL)
    ws["I27"] = f'=IF(H27="","",MAX({FUENTE_ENVIADAS}))'
    ws["I27"].font = Font(name="Calibri", size=12, bold=True, color=TEAL)
    ws["I27"].number_format = "0"
    ws["I27"].alignment = CENTER

    for offset, area in enumerate(AREAS):
        row = AREA_FIRST + offset
        ws.cell(row, 2, area).font = FONT_BODY
        ws.cell(row, 3, f'=COUNTIFS({POST_AREA},B{row},{POST_EMPRESA},"<>")')
        ws.cell(row, 3).font = FONT_BODY
        ws.cell(row, 3).alignment = CENTER
        ws.cell(row, 3).number_format = "0"
        ws.row_dimensions[row].height = 18
    sin_area = AREA_FIRST + len(AREAS)
    ws.cell(sin_area, 2, "Sin área").font = Font(name="Calibri", size=11, italic=True, color=MUTED)
    ws.cell(sin_area, 3, f'=COUNTIFS({POST_EMPRESA},"<>",{POST_AREA},"")')
    ws.cell(sin_area, 3).font = FONT_BODY
    ws.cell(sin_area, 3).alignment = CENTER
    ws.cell(sin_area, 3).number_format = "0"

    for offset, modalidad in enumerate(MODALIDADES):
        row = AREA_FIRST + offset
        ws.cell(row, 4, modalidad).font = FONT_BODY
        ws.cell(row, 5, f'=COUNTIFS({POST_MODALIDAD},D{row},{POST_EMPRESA},"<>")')
        ws.cell(row, 5).font = FONT_BODY
        ws.cell(row, 5).alignment = CENTER
        ws.cell(row, 5).number_format = "0"
    sin_mod = AREA_FIRST + len(MODALIDADES)
    ws.cell(sin_mod, 4, "Sin modalidad").font = Font(name="Calibri", size=11, italic=True, color=MUTED)
    ws.cell(sin_mod, 5, f'=COUNTIFS({POST_EMPRESA},"<>",{POST_MODALIDAD},"")')
    ws.cell(sin_mod, 5).font = FONT_BODY
    ws.cell(sin_mod, 5).alignment = CENTER
    ws.cell(sin_mod, 5).number_format = "0"

    chart = BarChart()
    chart.type = "bar"
    chart.grouping = "standard"
    chart.title = "Embudo"
    chart.style = 10
    data = Reference(ws, min_col=3, min_row=9, max_row=sin_row)
    cats = Reference(ws, min_col=2, min_row=FUNNEL_FIRST, max_row=sin_row)
    chart.add_data(data, titles_from_data=True)
    chart.set_categories(cats)
    chart.shape = 4
    chart.legend = None
    chart.series[0].graphicalProperties.solidFill = TEAL
    chart.width = 18
    chart.height = 8
    ws.add_chart(chart, CHART_ANCHOR)
    ws.freeze_panes = None
    ws.print_area = "A1:J52"
    ws.page_setup.fitToHeight = 1
    ws.sheet_view.zoomScale = 110


def label_input(ws, row: int, label_col: int, label: str, value_col: int, kind: str) -> None:
    lab = ws.cell(row, label_col, label)
    lab.font = FONT_LABEL
    lab.alignment = Alignment(horizontal="left", vertical="center")
    value = ws.cell(row, value_col, None)
    value.fill = FILL_YELLOW
    value.border = INPUT_BORDER
    value.font = Font(name="Calibri", size=12, color=INK)
    value.alignment = LEFT
    if kind == "date":
        value.number_format = "DD/MM/YYYY"
        value.alignment = CENTER
    elif kind == "money":
        value.number_format = '#,##0'
        value.alignment = CENTER


def section_bar(ws, row: int, text: str) -> None:
    ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=5)
    cell = ws.cell(row, 2, text)
    cell.font = FONT_SECTION
    cell.fill = FILL_SECTION
    cell.alignment = Alignment(horizontal="left", vertical="center", indent=1)
    for col in range(2, 6):
        ws.cell(row, col).fill = FILL_SECTION
        ws.cell(row, col).font = FONT_SECTION
    ws.row_dimensions[row].height = 24


def build_cierre(wb: Workbook, listas: dict[str, str]) -> None:
    ws = wb.create_sheet(S_CIE)
    apply_page(ws, orientation="portrait", fit_height=1, repeat_rows=None)
    ws.sheet_properties.tabColor = "B45309"
    widths = {"A": 3, "B": 38, "C": 32, "D": 32, "E": 32}
    for letter, width in widths.items():
        ws.column_dimensions[letter].width = width
    ws.row_dimensions[1].height = 32
    ws.merge_cells("B1:E1")
    ws["B1"] = "Cierre de la búsqueda"
    ws["B1"].font = FONT_TITLE
    ws.merge_cells("B2:E2")
    ws["B2"] = (
        "Los números funcionan desde el primer día. Las celdas amarillas se llenan cuando aceptes. "
        "Con eso el archivo queda listo para pasárselo a otra persona. El detalle sigue en las demás hojas."
    )
    ws["B2"].font = FONT_SMALL
    ws["B2"].alignment = LEFT_WRAP
    ws.row_dimensions[2].height = 36

    section_bar(ws, 4, "EL EMPLEO QUE ACEPTÉ")
    pairs = (
        (5, "Empresa", 2, 3, "text", "Cargo", 4, 5, "text"),
        (6, "Área", 2, 3, "area", "Modalidad", 4, 5, "modalidad"),
        (7, "Salario acordado", 2, 3, "money", "Moneda", 4, 5, "moneda"),
        (8, "Periodo del salario", 2, 3, "periodo", "Fecha de inicio", 4, 5, "date"),
        (9, "Ciudad o país", 2, 3, "text", "Contacto", 4, 5, "text"),
        (10, "Empezaste a buscar", 2, 3, "date", "Aceptaste el", 4, 5, "date"),
    )
    for row, left_label, left_col, left_val, left_kind, right_label, right_col, right_val, right_kind in pairs:
        ws.row_dimensions[row].height = 24
        label_input(ws, row, left_col, left_label, left_val, left_kind)
        label_input(ws, row, right_col, right_label, right_val, right_kind)
    add_list_validation(ws, f"={listas['ListaArea']}", C_AREA)
    add_list_validation(ws, f"={listas['ListaModalidad']}", C_MODALIDAD)
    add_list_validation(ws, f"={listas['ListaMoneda']}", C_MONEDA)
    add_list_validation(ws, f"={listas['ListaPeriodo']}", C_PERIODO)
    add_date_validation(ws, f"{C_INICIO_LAB} {C_INICIO_BUSQ} {C_ACEPTO}")

    ws.row_dimensions[11].height = 24
    ws["B11"] = "Días de búsqueda"
    ws["B11"].font = FONT_LABEL
    ws["C11"] = f'=IF(OR({C_INICIO_BUSQ}="",{C_ACEPTO}=""),"",{C_ACEPTO}-{C_INICIO_BUSQ})'
    ws["C11"].font = Font(name="Calibri", size=14, bold=True, color=TEAL)
    ws["C11"].fill = FILL_SOFT
    ws["C11"].border = THIN
    ws["C11"].alignment = CENTER
    ws["C11"].number_format = "0"
    ws["D11"] = "Filas en Oferta aceptada"
    ws["D11"].font = FONT_LABEL
    ws["E11"] = f'=COUNTIF({POST_ESTADO},"Oferta aceptada")'
    ws["E11"].font = Font(name="Calibri", size=14, bold=True, color=TEAL)
    ws["E11"].fill = FILL_SOFT
    ws["E11"].border = THIN
    ws["E11"].alignment = CENTER
    ws["E11"].number_format = "0"

    section_bar(ws, 13, "LOS NÚMEROS")
    number_labels = (
        (14, 2, "Enviadas"),
        (14, 3, "Te respondieron"),
        (14, 4, "Tasa de respuesta"),
        (14, 5, "Entrevistas"),
        (16, 2, "Ofertas"),
        (16, 3, "Fuente más usada"),
        (16, 4, "Enviadas por esa fuente"),
    )
    for row, col, text in number_labels:
        cell = ws.cell(row, col, text)
        cell.font = Font(name="Calibri", size=9, bold=True, color=MUTED)
        cell.alignment = CENTER
    for row in (15, 17):
        ws.row_dimensions[row].height = 28
    ws["B15"] = f"={S_TAB}!H5"
    ws["C15"] = f"={S_TAB}!I5"
    ws["D15"] = f'=IF(B15=0,"",C15/B15)'
    ws["E15"] = f'=COUNTIF({ENT_EMPRESA},"<>")'
    ws["B17"] = f"={S_TAB}!J5"
    ws["C17"] = f'=IF({S_TAB}!H27="","",{S_TAB}!H27)'
    ws["D17"] = f'=IF(C17="","",{S_TAB}!I27)'
    for coord in ("B15", "C15", "E15", "B17", "D17"):
        ws[coord].font = Font(name="Calibri", size=18, bold=True, color=TEAL)
        ws[coord].alignment = CENTER
        ws[coord].number_format = "0"
        ws[coord].fill = FILL_SOFT
        ws[coord].border = THIN
    ws["D15"].font = Font(name="Calibri", size=18, bold=True, color=TEAL)
    ws["D15"].alignment = CENTER
    ws["D15"].number_format = "0%"
    ws["D15"].fill = FILL_SOFT
    ws["D15"].border = THIN
    ws["C17"].font = Font(name="Calibri", size=14, bold=True, color=TEAL)
    ws["C17"].alignment = CENTER
    ws["C17"].fill = FILL_SOFT
    ws["C17"].border = THIN

    section_bar(ws, 19, "QUÉ LE SIRVE A QUIEN SIGA")
    notes = (
        (20, "Fuentes que sí valieron la pena"),
        (22, "Qué no repetiría"),
        (24, "Cómo preparé las pruebas y las entrevistas"),
        (26, "Qué CV funcionó mejor"),
        (28, "Algo que quieras decirle"),
    )
    for row, text in notes:
        ws.cell(row, 2, text).font = FONT_LABEL
        ws.merge_cells(start_row=row + 1, start_column=2, end_row=row + 1, end_column=5)
        box = ws.cell(row + 1, 2, None)
        box.fill = FILL_YELLOW
        box.border = INPUT_BORDER
        box.alignment = TOP_WRAP
        box.font = FONT_BODY
        for col in range(2, 6):
            ws.cell(row + 1, col).fill = FILL_YELLOW
            ws.cell(row + 1, col).border = INPUT_BORDER
        ws.row_dimensions[row + 1].height = 36 if row != 26 else 28

    section_bar(ws, 31, "MENSAJE LISTO PARA COPIAR")
    ws.merge_cells("B32:E32")
    ws["B32"] = "Selecciónalo y mándalo con el archivo. Cámbialo si no suena a ti."
    ws["B32"].font = FONT_HINT
    ws.merge_cells("B33:E37")
    ws["B33"] = (
        f'=IF(OR({C_EMPRESA}="",{C_CARGO}="",{C_INICIO_BUSQ}="",{C_ACEPTO}=""),'
        '"Cuando completes empresa, cargo y las dos fechas, aquí aparece un texto listo para copiar y enviar con el archivo.",'
        '"Hola. Te comparto el seguimiento de mi búsqueda de empleo en QA y desarrollo, por si te sirve para la tuya. Busqué del "'
        f'&TEXT({C_INICIO_BUSQ},"DD/MM/YYYY")&" al "&TEXT({C_ACEPTO},"DD/MM/YYYY")&" ("&{C_DIAS_BUSQ}&" días). Envié "&{C_ENVIADAS}&" postulaciones y me respondieron "&{C_RESP}&" ("&IF({C_ENVIADAS}=0,"sin tasa",TEXT({C_TASA},"0%"))&"). Registré "&{C_ENTREVISTAS}&" entrevistas y "&{C_OFERTAS}&" ofertas. Acepté el cargo de "&{C_CARGO}&" en "&{C_EMPRESA}&". La fuente que más usé fue "&IF({C_TOP}="","ninguna",{C_TOP}&" ("&{C_TOPN}&" enviadas)")&". En esta hoja dejé qué fuentes sirvieron y cómo preparé las pruebas. En Entrevistas está lo que aprendí de cada proceso. En Contactos, escribe solo a quienes están marcados como Sí, se puede pasar.")'
    )
    ws["B33"].font = Font(name="Calibri", size=12, color=INK)
    ws["B33"].alignment = TOP_WRAP
    ws["B33"].fill = FILL_PAPER
    for row in range(33, 38):
        for col in range(2, 6):
            ws.cell(row, col).fill = FILL_PAPER
            ws.cell(row, col).border = Border(
                left=Side(style="medium", color=TEAL) if col == 2 else Side(style=None),
                right=Side(style="medium", color=TEAL) if col == 5 else Side(style=None),
                top=Side(style="medium", color=TEAL) if row == 33 else Side(style=None),
                bottom=Side(style="medium", color=TEAL) if row == 37 else Side(style=None),
            )
        ws.row_dimensions[row].height = 26

    section_bar(ws, 38, "ANTES DE PASAR EL ARCHIVO")
    checks = (
        "Marqué como Oferta aceptada la postulación que acepté",
        "Completé Aprendizaje en las entrevistas que ya pasaron",
        "En Contactos marqué quién se puede pasar y quité teléfonos que no debo compartir",
        "Borré expectativas, notas y cualquier dato que no quiero que vea otra persona",
        "Guardé una copia para mí y esta copia es la que voy a pasar",
    )
    for offset, text in enumerate(checks):
        row = C_CHECK_FIRST + offset
        ws.row_dimensions[row].height = 32
        ws.cell(row, 2, text).font = FONT_BODY
        ws.cell(row, 2).alignment = LEFT_WRAP
        box = ws.cell(row, 3, None)
        box.fill = FILL_YELLOW
        box.border = INPUT_BORDER
        box.alignment = CENTER
        box.font = Font(name="Calibri", size=12, bold=True, color=INK)
    add_list_validation(ws, f"={listas['ListaSiNo']}", f"C{C_CHECK_FIRST}:C{C_CHECK_LAST}")
    ws.merge_cells("B45:E45")
    ws["B45"] = (
        f'=COUNTIF(C{C_CHECK_FIRST}:C{C_CHECK_LAST},"Sí")&" de 5 marcados con Sí. "&'
        f'IF(COUNTIF({POST_ESTADO},"Oferta aceptada")=0,'
        '"En Postulaciones todavía ninguna fila dice Oferta aceptada.",'
        '"En Postulaciones ya hay una fila en Oferta aceptada.")'
    )
    ws["B45"].font = Font(name="Calibri", size=11, bold=True, color=TEAL)
    ws["B45"].alignment = LEFT_WRAP
    ws.row_dimensions[45].height = 28
    ws.row_dimensions[46].height = 32
    ws.merge_cells("B46:E46")
    ws["B46"] = "No escribas en este archivo cédula, dirección, contraseñas ni números de cuenta."
    ws["B46"].font = Font(name="Calibri", size=10, italic=True, color=RED)
    ws["B46"].alignment = LEFT_WRAP
    ws.freeze_panes = "A4"
    ws.print_area = "A1:E46"
    ws.page_setup.fitToHeight = 2
    ws.sheet_view.zoomScale = 110


def write_leeme_line(ws, row: int, kind: str, text: str, extra: str = "") -> int:
    if kind == "h":
        ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=3)
        cell = ws.cell(row, 2, text)
        cell.font = FONT_SECTION
        cell.fill = FILL_SECTION
        cell.alignment = Alignment(horizontal="left", vertical="center", indent=1)
        ws.cell(row, 3).fill = FILL_SECTION
        ws.row_dimensions[row].height = 24
        return row + 1
    if kind == "p":
        ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=3)
        cell = ws.cell(row, 2, text)
        cell.font = FONT_BODY
        cell.alignment = TOP_WRAP
        ws.row_dimensions[row].height = 78
        return row + 1
    if kind == "step":
        num = ws.cell(row, 2, text)
        num.font = Font(name="Calibri", size=12, bold=True, color=TEAL)
        num.alignment = Alignment(horizontal="right", vertical="top")
        body = ws.cell(row, 3, extra)
        body.font = FONT_BODY
        body.alignment = TOP_WRAP
        ws.row_dimensions[row].height = 40
        return row + 1
    if kind == "kv":
        key = ws.cell(row, 2, text)
        key.font = Font(name="Calibri", size=11, bold=True, color=INK)
        key.alignment = Alignment(horizontal="left", vertical="center")
        val = ws.cell(row, 3, extra)
        val.font = FONT_BODY
        val.alignment = LEFT_WRAP
        ws.row_dimensions[row].height = 32
        key.border = HAIR_BOTTOM
        val.border = HAIR_BOTTOM
        return row + 1
    raise ValueError(kind)


def build_leeme(wb: Workbook) -> None:
    ws = wb.create_sheet(S_LEE)
    apply_page(ws, orientation="portrait", fit_height=0, repeat_rows=None)
    ws.sheet_properties.tabColor = "78716C"
    ws.column_dimensions["A"].width = 3
    ws.column_dimensions["B"].width = 32
    ws.column_dimensions["C"].width = 92
    ws.row_dimensions[1].height = 32
    ws["B1"] = "Cómo usar este archivo"
    ws["B1"].font = FONT_TITLE
    ws.merge_cells("B2:C2")
    ws["B2"] = (
        "Es el control de una búsqueda de empleo en QA o desarrollo. Sirve para el día a día y, cuando aceptes, "
        "para pasarle a otra persona lo que de verdad sirvió: fuentes, pruebas, contactos y cómo cerraste."
    )
    ws["B2"].font = FONT_SMALL
    ws["B2"].alignment = LEFT_WRAP
    ws.row_dimensions[2].height = 36

    blocks: list[tuple] = [
        ("h", "Cada día"),
        ("step", "1", "Anota la vacante en Postulaciones. Una fila, aunque todavía no postules: en ese caso el estado es Por postular."),
        ("step", "2", "La fecha es el día en que postulaste. Si sigue guardada, pon el día en que la viste."),
        ("step", "3", "Si hay un siguiente paso, escríbelo y ponle fecha. Cuando te escriban o escribas, actualiza Último contacto: los días se reinician."),
        ("step", "4", "Al abrir el archivo, ve a Alerta y abre la flecha del encabezado. Deja marcadas Acción vencida y Hoy. Las filas vacías se ocultan solas."),
        ("step", "5", "Cada entrevista va en Entrevistas, aunque sea una llamada corta. Al salir, llena Aprendizaje con algo que se entienda sin estar en tu cabeza."),
        ("step", "6", "Cada oferta va en Ofertas, con fecha límite y puntaje, antes de responder."),
        ("step", "7", "El Tablero solo se lee. No hace falta escribir ahí."),
        ("h", "Qué significa Alerta"),
        ("kv", ALERTA_VENCIDA, "La fecha de la acción ya pasó."),
        ("kv", ALERTA_HOY, "Toca hoy."),
        ("kv", ALERTA_PRONTO, "Toca en los próximos dos días."),
        ("kv", ALERTA_SEGUIMIENTO, "Lleva 10 días o más en Por postular, Postulada o En revisión, y no hay una acción con fecha."),
        ("kv", ALERTA_FECHA, "Hay empresa, pero falta la fecha."),
        ("kv", ALERTA_CURSO, "Sigue abierta y no urge."),
        ("kv", ALERTA_CERRADA, "Aceptada, rechazada, retirada, sin respuesta, o una oferta que ya cerraste."),
        ("h", "Los estados, en este orden"),
        (
            "p",
            "Por postular → Postulada → En revisión → Screening → Prueba técnica → Entrevista técnica → Entrevista final → Oferta recibida → Oferta aceptada. Si se cierra de otra forma: Oferta rechazada, Rechazada, Retirada o Sin respuesta. Úsalos tal cual. El Tablero cuenta esos textos.",
        ),
        ("h", "Las hojas"),
        ("kv", "Postulaciones", "El día a día. Una fila por vacante."),
        ("kv", "Tablero", "El resumen. Se calcula solo."),
        ("kv", "Entrevistas", "Cada ronda y lo que aprendiste."),
        ("kv", "Ofertas", "Comparar antes de decidir. El salario va en número, sin puntos."),
        ("kv", "Contactos", "Personas del proceso y quién se puede pasar."),
        ("kv", "Cierre", "Se llena al aceptar. Deja un mensaje listo para copiar."),
        ("kv", "Listas", "Las opciones de los desplegables."),
        ("kv", "Léeme", "Esta guía."),
        ("h", "Cuando aceptes y vayas a pasarlo"),
        ("step", "1", "En la fila del empleo que aceptaste, cambia el estado a Oferta aceptada."),
        ("step", "2", "Completa las celdas amarillas de Cierre. Revisa el mensaje, selecciónalo y cópialo."),
        ("step", "3", "Lee Aprendizaje como si no hubieras estado en la entrevista. Completa lo que no se entienda."),
        ("step", "4", "En Contactos, «Sí, se puede pasar» solo si esa persona está de acuerdo. Si dudas, Preguntar antes, y borra el teléfono."),
        ("step", "5", "Borra de Expectativa y de Notas lo que sea solo tuyo: lo que pedías, opiniones de personas, datos de documentos."),
        ("step", "6", "Marca el checklist. Guarda una copia con tu nombre para ti y pasa la otra."),
        (
            "p",
            "No escribas cédula, dirección, contraseñas ni números de cuenta. El archivo está hecho para Excel. Si alguien lo abre en Google Sheets, que revise que los desplegables y el Tablero hayan pasado bien.",
        ),
        ("h", "Si falta una opción o una fila"),
        (
            "p",
            "Para una fuente o un estado nuevo: hoja Listas, clic derecho en una celda de esa columna, Insertar, Desplazar celdas hacia abajo, y escribe. No la pongas debajo de la última y no le cambies el nombre a una opción que ya usaste. Hay 100 filas de postulaciones, 60 de entrevistas y 60 de contactos. Para otra: clic derecho en la última fila, Insertar. No escribas debajo del aviso final.",
        ),
        ("h", "Ejemplo de una fila"),
        (
            "p",
            "09/11/2026 · Empresa · QA Automation · QA · Semi-senior · Remoto · Colombia · LinkedIn · enlace · nombre de la persona · CV automatización · Postulada · Media · Aún no sé · el salario si lo publican · tu expectativa · fecha de hoy en Último contacto · Hacer seguimiento · dentro de 7 días. Días y Alerta se llenan solos.",
        ),
    ]
    row = 4
    for block in blocks:
        row = write_leeme_line(ws, row, block[0], block[1], block[2] if len(block) > 2 else "")
    ws.freeze_panes = "A4"
    ws.print_area = f"A1:C{row}"
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 2
    ws.sheet_view.zoomScale = 110


def build_workbook() -> Workbook:
    check_invariants()
    wb = Workbook()
    wb.calculation = CalcProperties(calcMode="auto", fullCalcOnLoad=True, forceFullCalc=True)
    wb.properties.title = "Seguimiento de postulaciones"
    wb.properties.subject = "Búsqueda de empleo en QA o desarrollo"
    wb.properties.creator = "Seguimiento de postulaciones"
    wb.properties.description = (
        "Control diario de postulaciones y cierre para entregar cuando la búsqueda termine."
    )
    listas = build_listas(wb)
    build_postulaciones(wb, listas)
    build_tablero(wb)
    build_entrevistas(wb, listas)
    build_ofertas(wb, listas)
    build_contactos(wb, listas)
    build_cierre(wb, listas)
    build_leeme(wb)
    # Orden de pestañas: el día a día primero, la guía y las listas al final.
    order = [S_POST, S_TAB, S_ENT, S_OFE, S_CON, S_CIE, S_LEE, S_LIS]
    for index, name in enumerate(order):
        wb.move_sheet(name, offset=index - wb.sheetnames.index(name))
    wb.active = wb[S_POST]
    wb.views[0].activeTab = 0
    return wb


def main() -> None:
    wb = build_workbook()
    wb.save(OUTPUT)
    print(OUTPUT)


if __name__ == "__main__":
    main()
