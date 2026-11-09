#!/usr/bin/env python3
"""Recalcula el libro con LibreOffice y comprueba alertas, embudo y cierre."""

from __future__ import annotations

import os
import shutil
import socket
import subprocess
import sys
import time
import unittest
from datetime import date, timedelta
from pathlib import Path

import uno
from com.sun.star.beans import PropertyValue
from openpyxl.utils.datetime import from_excel

sys.path.insert(0, str(Path(__file__).resolve().parent))
import crear_seguimiento as gen  # noqa: E402

PORT = 2002
PROFILE = Path("/tmp/lo-profile-postulaciones")


def port_open(port: int) -> bool:
    with socket.socket() as sock:
        sock.settimeout(0.2)
        return sock.connect_ex(("127.0.0.1", port)) == 0


def start_soffice() -> subprocess.Popen:
    if PROFILE.exists():
        shutil.rmtree(PROFILE, ignore_errors=True)
    PROFILE.mkdir(parents=True)
    proc = subprocess.Popen(
        [
            "soffice",
            "--headless",
            "--nologo",
            "--nofirststartwizard",
            "--norestore",
            f"-env:UserInstallation=file://{PROFILE}",
            f"--accept=socket,host=127.0.0.1,port={PORT};urp;StarOffice.ComponentContext",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    for _ in range(80):
        if port_open(PORT):
            return proc
        if proc.poll() is not None:
            raise RuntimeError("LibreOffice terminó antes de abrir el puerto")
        time.sleep(0.25)
    raise RuntimeError("LibreOffice no abrió el puerto")


def connect():
    local = uno.getComponentContext()
    resolver = local.ServiceManager.createInstanceWithContext(
        "com.sun.star.bridge.UnoUrlResolver", local
    )
    ctx = resolver.resolve(
        f"uno:socket,host=127.0.0.1,port={PORT};urp;StarOffice.ComponentContext"
    )
    smgr = ctx.ServiceManager
    desktop = smgr.createInstanceWithContext("com.sun.star.frame.Desktop", ctx)
    return desktop


def load(desktop, path: Path):
    hidden = PropertyValue()
    hidden.Name = "Hidden"
    hidden.Value = True
    url = uno.systemPathToFileUrl(str(path.resolve()))
    doc = desktop.loadComponentFromURL(url, "_blank", 0, (hidden,))
    doc.calculateAll()
    return doc


def text(sheet, coord: str) -> str:
    return sheet.getCellRangeByName(coord).getString()


def number(sheet, coord: str) -> float:
    cell = sheet.getCellRangeByName(coord)
    error = cell.getError()
    if error:
        raise AssertionError(f"{coord} tiene error {error}: {cell.getFormula()}")
    return cell.getValue()


class Recalculo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ["TZ"] = "UTC"
        time.tzset()
        cls.today = date.today()
        cls.monday = cls.today - timedelta(days=cls.today.weekday())
        cls.month = cls.today.replace(day=1)
        cls.path = Path("/tmp/seguimiento-prueba.xlsx")
        wb = gen.build_workbook()
        cls._fill(wb)
        wb.save(cls.path)
        cls.proc = start_soffice()
        cls.desktop = connect()
        cls.doc = load(cls.desktop, cls.path)
        cls.post = cls.doc.Sheets.getByName(gen.S_POST)
        cls.tab = cls.doc.Sheets.getByName(gen.S_TAB)
        cls.ent = cls.doc.Sheets.getByName(gen.S_ENT)
        cls.ofe = cls.doc.Sheets.getByName(gen.S_OFE)
        cls.cierre = cls.doc.Sheets.getByName(gen.S_CIE)
        cls.listas = cls.doc.Sheets.getByName(gen.S_LIS)

    @classmethod
    def tearDownClass(cls):
        try:
            cls.doc.close(True)
        finally:
            cls.proc.terminate()
            cls.proc.wait(timeout=15)

    @classmethod
    def _fill(cls, wb):
        post = wb[gen.S_POST]
        p = lambda key: gen.col_index(gen.POST_COLS, key)
        today = cls.today
        monday = cls.monday
        rows = {
            5: dict(fecha=today - timedelta(days=12), empresa="Andes", area="QA", modalidad="Remoto", fuente="LinkedIn", estado="Postulada"),
            6: dict(fecha=today - timedelta(days=1), empresa="Nube", area="Desarrollo", fuente="Get on Board", estado="Postulada", fecha_accion=today),
            7: dict(fecha=today - timedelta(days=20), empresa="Río", area="QA", fuente="Referido", estado="En revisión", ultimo=today - timedelta(days=3), fecha_accion=today - timedelta(days=1)),
            8: dict(fecha=today - timedelta(days=2), empresa="Loma", fuente="LinkedIn", estado="Por postular", fecha_accion=today + timedelta(days=1)),
            9: dict(empresa="SinFecha", fuente="Torre", estado="Postulada"),
            10: dict(fecha=today - timedelta(days=30), empresa="Cerrada", fuente="elempleo", estado="Rechazada"),
            11: dict(fecha=today - timedelta(days=4), empresa="Oferta", fuente="Referido", estado="Oferta recibida"),
            12: dict(fecha=today, empresa="Gané", fuente="Referido", estado="Oferta aceptada"),
            13: dict(fecha=monday, empresa="Semana", fuente="Computrabajo", estado="Screening"),
            14: dict(fecha=monday - timedelta(days=1), empresa="SemanaPasada", fuente="Indeed", estado="Postulada"),
            15: dict(fecha=today - timedelta(days=15), empresa="Silencio", fuente="LinkedIn", estado="Sin respuesta"),
            16: dict(fecha=today - timedelta(days=11), empresa="Revision", fuente="LinkedIn", estado="En revisión"),
            17: dict(fecha=today - timedelta(days=5), empresa="RechazoViejo", fuente="Otra", estado="Rechazada", fecha_accion=today - timedelta(days=1)),
        }
        for row, values in rows.items():
            for key, value in values.items():
                post.cell(row, p(key), value)
        ent = wb[gen.S_ENT]
        e = lambda key: gen.col_index(gen.ENT_COLS, key)
        interviews = {
            5: dict(fecha=today, empresa="Nube", resultado="Pendiente"),
            6: dict(fecha=today - timedelta(days=1), empresa="Andes"),
            7: dict(fecha=today + timedelta(days=1), empresa="Loma", resultado="Pendiente"),
            8: dict(fecha=today - timedelta(days=1), empresa="Oferta", resultado="Pasé"),
            9: dict(empresa="Río", resultado="Pendiente"),
        }
        for row, values in interviews.items():
            for key, value in values.items():
                ent.cell(row, e(key), value)
        ofe = wb[gen.S_OFE]
        o = lambda key: gen.col_index(gen.OFER_COLS, key)
        offers = {
            5: dict(empresa="Oferta", limite=today, decision="Pendiente"),
            6: dict(empresa="Otra", limite=today - timedelta(days=2), decision="Negociando"),
            7: dict(empresa="Gané", limite=today - timedelta(days=1), decision="Aceptada"),
        }
        for row, values in offers.items():
            for key, value in values.items():
                ofe.cell(row, o(key), value)
        cierre = wb[gen.S_CIE]
        cierre["C5"] = "Andes"
        cierre["E5"] = "QA Automation"
        cierre["C10"] = today - timedelta(days=40)
        cierre["E10"] = today
        for row in range(39, 42):
            cierre.cell(row, 3, "Sí")
        wb[gen.S_LIS]["T6"] = "=TODAY()"

    def test_hoy_de_libreoffice_coincide(self):
        serial = number(self.listas, "T6")
        lo_today = from_excel(serial).date()
        self.assertEqual(lo_today, self.today)

    def test_alertas_y_dias(self):
        monday = self.monday
        expected = {
            5: (12, gen.ALERTA_SEGUIMIENTO),
            6: (1, gen.ALERTA_HOY),
            7: (3, gen.ALERTA_VENCIDA),
            8: (2, gen.ALERTA_PRONTO),
            9: (None, gen.ALERTA_FECHA),
            10: (30, gen.ALERTA_CERRADA),
            11: (4, gen.ALERTA_CURSO),
            12: (0, gen.ALERTA_CERRADA),
            13: ((self.today - monday).days, gen.ALERTA_CURSO),
            14: ((self.today - (monday - timedelta(days=1))).days, gen.ALERTA_CURSO),
            15: (15, gen.ALERTA_CERRADA),
            16: (11, gen.ALERTA_SEGUIMIENTO),
            17: (5, gen.ALERTA_CERRADA),
            18: (None, ""),
        }
        for row, (dias, alerta) in expected.items():
            got_alerta = text(self.post, f"U{row}")
            got_dias = number(self.post, f"T{row}")
            self.assertEqual(got_alerta, alerta, f"alerta fila {row}")
            if dias is None:
                self.assertEqual(got_dias, 0, f"días fila {row} debería estar vacío y no contar como número")
                self.assertEqual(text(self.post, f"T{row}"), "", f"días fila {row}")
            else:
                self.assertEqual(got_dias, dias, f"días fila {row}")

    def test_entrevistas_y_ofertas(self):
        self.assertEqual(text(self.ent, "L5"), gen.ENT_HOY)
        self.assertEqual(text(self.ent, "L6"), gen.ENT_PENDIENTE)
        self.assertEqual(text(self.ent, "L7"), gen.ENT_MANANA)
        self.assertEqual(text(self.ent, "L8"), gen.ENT_LISTA)
        self.assertEqual(text(self.ent, "L9"), gen.ENT_FECHA)
        self.assertEqual(text(self.ent, "L10"), "")
        self.assertEqual(number(self.ofe, "Q5"), 0)
        self.assertEqual(number(self.ofe, "Q6"), -2)
        self.assertEqual(text(self.ofe, "Q7"), "")

    def test_tablero(self):
        self.assertEqual(number(self.tab, "B5"), 3)  # hoy
        self.assertEqual(number(self.tab, "C5"), 3)  # vencidas
        self.assertEqual(number(self.tab, "D5"), 1)  # guardadas
        self.assertEqual(number(self.tab, "E5"), 2)  # seguimiento
        self.assertEqual(number(self.tab, "G5"), 8)  # en proceso
        self.assertEqual(number(self.tab, "H5"), 12)  # enviadas
        self.assertEqual(number(self.tab, "I5"), 7)  # respuestas
        self.assertEqual(number(self.tab, "J5"), 2)  # ofertas
        self.assertEqual(number(self.tab, "C24"), 13)  # total embudo
        self.assertEqual(text(self.tab, "B25"), "")
        self.assertEqual(text(self.tab, "G26"), "")
        self.assertEqual(text(self.tab, "H27"), "LinkedIn")
        self.assertEqual(number(self.tab, "I27"), 3)
        self.assertEqual(number(self.tab, "C10"), 1)  # por postular
        self.assertEqual(number(self.tab, "C11"), 4)  # postulada
        self.assertEqual(number(self.tab, "C20"), 2)  # Rechazada
        self.assertEqual(number(self.tab, "C28"), 2)  # QA
        self.assertEqual(number(self.tab, "C29"), 1)  # Desarrollo
        self.assertEqual(number(self.tab, "C32"), 10)  # sin área
        self.assertEqual(number(self.tab, "E28"), 1)  # remoto
        self.assertEqual(number(self.tab, "E32"), 12)  # sin modalidad
        linkedin = number(self.tab, "H10")
        referido = number(self.tab, "H12")
        self.assertEqual(linkedin, 3)
        self.assertEqual(referido, 3)
        self.assertEqual(number(self.tab, "I10"), 1)  # respuesta LinkedIn
        self.assertEqual(number(self.tab, "I12"), 3)  # respuesta Referido
        self.assertEqual(number(self.tab, "H18"), 1)  # Torre, fila sin fecha pero con fuente
        enviadas_semana = 0
        enviadas_mes = 0
        fechas = {
            5: self.today - timedelta(days=12),
            6: self.today - timedelta(days=1),
            7: self.today - timedelta(days=20),
            10: self.today - timedelta(days=30),
            11: self.today - timedelta(days=4),
            12: self.today,
            13: self.monday,
            14: self.monday - timedelta(days=1),
            15: self.today - timedelta(days=15),
            16: self.today - timedelta(days=11),
            17: self.today - timedelta(days=5),
        }
        for fecha in fechas.values():
            if fecha >= self.monday:
                enviadas_semana += 1
            if fecha >= self.month:
                enviadas_mes += 1
        dias = [12, 1, 3, 2, 4, (self.today - self.monday).days, (self.today - (self.monday - timedelta(days=1))).days, 11]
        promedio = round(sum(dias) / len(dias))
        sentence = text(self.tab, "B6")
        self.assertIn(f"Postulaciones que tocan hoy: 1.", sentence)
        self.assertIn("Entrevistas hoy: 1.", sentence)
        self.assertIn("Ofertas que vencen hoy: 1.", sentence)
        self.assertIn("Acciones en 48 h: 1.", sentence)
        self.assertIn("Entrevistas mañana: 1.", sentence)
        self.assertIn(f"Enviadas esta semana: {enviadas_semana}.", sentence)
        self.assertIn(f"Este mes: {enviadas_mes}.", sentence)
        self.assertIn(f"Promedio en curso: {promedio} días.", sentence)

    def test_cierre(self):
        self.assertEqual(number(self.cierre, "C11"), 40)
        self.assertEqual(number(self.cierre, "E11"), 1)
        self.assertEqual(number(self.cierre, "B15"), 12)
        self.assertEqual(number(self.cierre, "C15"), 7)
        self.assertAlmostEqual(number(self.cierre, "D15"), 7 / 12)
        self.assertEqual(number(self.cierre, "E15"), 5)
        self.assertEqual(number(self.cierre, "B17"), 2)
        self.assertEqual(text(self.cierre, "C17"), "LinkedIn")
        self.assertEqual(number(self.cierre, "D17"), 3)
        message = text(self.cierre, "B33")
        self.assertIn("QA Automation", message)
        self.assertIn("Andes", message)
        self.assertIn("40 días", message)
        self.assertIn("LinkedIn (3 enviadas)", message)
        self.assertIn("Envié 12 postulaciones", message)
        self.assertIn("me respondieron 7", message)
        status = text(self.cierre, "B45")
        self.assertIn("3 de 5", status)
        self.assertIn("ya hay una fila en Oferta aceptada", status)

    def test_fila_vacia_no_cuenta(self):
        self.assertEqual(text(self.post, "U104"), "")
        self.assertEqual(text(self.tab, "B3"), "")


if __name__ == "__main__":
    unittest.main(verbosity=2)
