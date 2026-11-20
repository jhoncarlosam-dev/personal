#!/usr/bin/env python3
"""Reemplaza el recuadro de la foto y el centro en el portal del servidor.

Uso, desde la carpeta web:

    python3 insertar_foto.py foto.jpg "CEAD Pasto"

La foto no sale del computador. El script solo reescribe index.html.
"""

import base64
import re
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent
INDEX = ROOT / "index.html"
MARKER_CENTRO = "[ESCRIBA SU CEAD O UDR]"


def foto_a_png(origen, destino):
    imagen = Image.open(origen).convert("RGB")
    imagen.thumbnail((360, 460))
    lienzo = Image.new("RGB", (360, 460), (246, 244, 239))
    x = (360 - imagen.width) // 2
    y = (460 - imagen.height) // 2
    lienzo.paste(imagen, (x, y))
    lienzo.save(destino, optimize=True)


def main():
    if len(sys.argv) < 3:
        print('Uso: python3 insertar_foto.py foto.jpg "CEAD o UDR"')
        sys.exit(1)
    origen = Path(sys.argv[1])
    centro = sys.argv[2].strip()
    if not origen.is_file():
        print("No encuentro la foto:", origen)
        sys.exit(1)
    if not centro or centro.startswith("["):
        print("Escriba el centro real, por ejemplo: CEAD Bogotá")
        sys.exit(1)
    destino = ROOT / "imagenes" / "foto_estudiante.png"
    foto_a_png(origen, destino)
    html = INDEX.read_text(encoding="utf-8")
    if MARKER_CENTRO not in html and "Centro de matrícula" not in html:
        print("index.html no tiene el texto del centro. Regenere la página primero.")
        sys.exit(1)
    nuevo = base64.b64encode(destino.read_bytes()).decode("ascii")
    inicio = html.find("data:image/png;base64,")
    if inicio < 0:
        print("No hay imagen embebida en index.html.")
        sys.exit(1)
    fin = html.find('"', inicio)
    html = html[:inicio] + "data:image/png;base64," + nuevo + html[fin:]
    html = html.replace(MARKER_CENTRO, centro)
    html = re.sub(
        r"(<b>Centro de matrícula:</b>\s*)([^<]*)",
        lambda match: match.group(1) + centro,
        html,
        count=1,
    )
    INDEX.write_text(html, encoding="utf-8")
    print("Listo. Abra index.html en el navegador y pegue todo el archivo en el servidor HTTP de Packet Tracer.")
    print("Centro escrito:", centro)


if __name__ == "__main__":
    main()
