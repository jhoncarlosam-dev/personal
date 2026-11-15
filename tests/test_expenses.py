from decimal import Decimal

from bandeja.expenses import summarize_expenses


def test_csv_colombiano_con_punto_y_coma(tmp_path) -> None:
    path = tmp_path / "gastos.csv"
    path.write_text(
        "fecha;concepto;categoria;monto\n"
        "15/03/2026;Almuerzo;Alimentación;25.000\n"
        "16/03/2026;Bus;Transporte;3.500\n"
        "02/04/2026;Arriendo;Hogar;1.200.000,50\n"
        "sin-fecha;Taxi;Transporte;no-es-un-monto\n",
        encoding="utf-8",
    )
    summary = summarize_expenses(path)
    assert summary is not None
    assert summary.rows == 3
    assert summary.skipped == 1
    assert summary.total == Decimal("1228500.50")
    assert summary.by_category["Alimentación"] == Decimal("25000.00")
    assert summary.by_category["Transporte"] == Decimal("3500.00")
    assert summary.by_category["Hogar"] == Decimal("1200000.50")


def test_monto_entre_comillas_y_separador_coma(tmp_path) -> None:
    path = tmp_path / "gastos.csv"
    path.write_text(
        'fecha,categoria,monto\n2026-03-02,Hogar,"1.200.000,50"\n',
        encoding="utf-8",
    )
    summary = summarize_expenses(path)
    assert summary is not None
    assert summary.by_category["Hogar"] == Decimal("1200000.50")


def test_un_csv_de_contactos_no_es_un_gasto(tmp_path) -> None:
    path = tmp_path / "contactos.csv"
    path.write_text("nombre,edad\nAna,30\n", encoding="utf-8")
    assert summarize_expenses(path) is None


def test_fusiona_la_categoria_sin_importar_tildes_ni_mayusculas(tmp_path) -> None:
    path = tmp_path / "gastos.csv"
    path.write_text(
        "fecha,categoria,monto\n"
        "2026-03-01,Alimentación,10\n"
        "2026-03-02,alimentacion,5\n",
        encoding="utf-8",
    )
    summary = summarize_expenses(path)
    assert summary is not None
    assert summary.by_category == {"Alimentación": Decimal("15.00")}


def test_si_no_hay_categoria_usa_el_concepto(tmp_path) -> None:
    path = tmp_path / "gastos.csv"
    path.write_text(
        "fecha,concepto,monto\n2026-03-01,Café,4.500\n",
        encoding="utf-8",
    )
    summary = summarize_expenses(path)
    assert summary is not None
    assert summary.by_category == {"Café": Decimal("4500.00")}


def test_un_monto_negativo_resta(tmp_path) -> None:
    path = tmp_path / "gastos.csv"
    path.write_text(
        "fecha,categoria,monto\n"
        "2026-03-01,Transporte,10.000\n"
        "2026-03-02,Transporte,-2.500\n",
        encoding="utf-8",
    )
    summary = summarize_expenses(path)
    assert summary is not None
    assert summary.total == Decimal("7500.00")
    assert list(summary.by_category) == ["Transporte"]


def test_acepta_bom_utf8(tmp_path) -> None:
    path = tmp_path / "gastos.csv"
    path.write_bytes("fecha,monto\n2026-03-01,10\n".encode("utf-8-sig"))
    summary = summarize_expenses(path)
    assert summary is not None
    assert summary.rows == 1
    assert summary.total == Decimal("10.00")
    assert summary.by_category == {"sin categoría": Decimal("10.00")}


def test_acepta_latin1(tmp_path) -> None:
    path = tmp_path / "gastos.csv"
    path.write_bytes(
        "fecha;categoria;monto\n15/03/2026;Niños;1.000\n".encode("latin-1")
    )
    summary = summarize_expenses(path)
    assert summary is not None
    assert summary.by_category["Niños"] == Decimal("1000.00")


def test_csv_vacio_y_solo_encabezado(tmp_path) -> None:
    empty = tmp_path / "vacio.csv"
    empty.write_text("", encoding="utf-8")
    assert summarize_expenses(empty) is None
    header = tmp_path / "encabezado.csv"
    header.write_text("fecha,monto\n", encoding="utf-8")
    summary = summarize_expenses(header)
    assert summary is not None
    assert summary.rows == 0
    assert summary.skipped == 0
