#!/usr/bin/env python3
"""Genera las imágenes originales de la práctica y las páginas del servidor web."""

import base64
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
IMG = ROOT / "imagenes"
IMG.mkdir(exist_ok=True)

SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANSB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

NAVY = (27, 58, 75)
TEAL = (31, 111, 106)
GOLD = (184, 148, 74)
CREAM = (246, 244, 239)
INK = (33, 37, 41)
WHITE = (255, 255, 255)
RED = (140, 42, 48)
GREEN = (36, 112, 78)
BLUE = (36, 78, 120)


def font(size, bold=False):
    return ImageFont.truetype(SANSB if bold else SANS, size)


def wrap(draw, text, fnt, width):
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def card(w, h, title, lines, footer):
    im = Image.new("RGB", (w, h), CREAM)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, w, 58), fill=NAVY)
    d.rectangle((0, 58, w, 64), fill=GOLD)
    d.text((18, 16), title, font=font(20, True), fill=WHITE)
    y = 86
    body = font(16)
    for line in lines:
        for part in wrap(d, line, body, w - 40):
            d.text((20, y), part, font=body, fill=INK)
            y += 24
        y += 8
    d.rectangle((0, h - 36, w, h), fill=TEAL)
    d.text((16, h - 28), footer, font=font(12), fill=WHITE)
    return im


def foto():
    w, h = 360, 460
    im = Image.new("RGB", (w, h), CREAM)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, w, h), outline=NAVY, width=4)
    d.rectangle((18, 18, w - 18, 250), fill=(214, 224, 228))
    d.ellipse((130, 48, 230, 148), fill=NAVY)
    d.pieslice((100, 150, 260, 280), 200, 340, fill=TEAL)
    d.text((28, 270), "FOTOGRAFÍA", font=font(18, True), fill=NAVY)
    for i, line in enumerate(
        ["Jhon Carlos", "Acevedo Mendoza", "", "Reemplace este recuadro", "con su foto real"]
    ):
        d.text((28, 300 + i * 24), line, font=font(15, i < 2), fill=INK if i < 2 else RED)
    im.save(IMG / "foto_estudiante.png", optimize=True)


def convergencia():
    im = card(
        560,
        320,
        "Red convergente",
        [
            "Voz, datos y video comparten la misma infraestructura IP.",
            "En la práctica: correo, portal web, televisión e IoT",
            "viajan sobre el mismo plan de direccionamiento,",
            "separados por subred para que un servicio no",
            "comparta dominio de difusión con los servidores.",
        ],
        "Telemática  ·  servicios unificados",
    )
    im.save(IMG / "telematica_convergencia.png", optimize=True)


def iot():
    im = card(
        560,
        320,
        "Espacio inteligente",
        [
            "Sensores, cámara y luminaria se registran en una",
            "plataforma y dejan de ser objetos aislados.",
            "El mismo esquema, a escala de ciudad, alimenta",
            "la gestión urbana: estado del entorno, aviso a",
            "las personas y decisión sobre el servicio.",
        ],
        "Telemática  ·  Internet de las cosas",
    )
    im.save(IMG / "telematica_iot.png", optimize=True)


def seguridad():
    im = card(
        560,
        320,
        "Visibilidad de la red",
        [
            "Un cortafuegos aplica una política: deja pasar el",
            "tráfico del servicio y niega el que no hace falta.",
            "El escaneo autorizado completa esa política:",
            "inventario de equipos, puertos, versiones y filtros",
            "antes de que otro los encuentre.",
        ],
        "Telemática  ·  seguridad preventiva",
    )
    im.save(IMG / "telematica_seguridad.png", optimize=True)


def box(d, xy, text, fill, lines=None):
    x1, y1, x2, y2 = xy
    d.rounded_rectangle(xy, radius=8, fill=fill, outline=NAVY, width=2)
    f = font(13, True)
    tw = d.textlength(text, font=f)
    d.text(((x1 + x2 - tw) / 2, y1 + 8), text, font=f, fill=WHITE)
    if lines:
        g = font(11)
        y = y1 + 30
        for line in lines:
            tw = d.textlength(line, font=g)
            d.text(((x1 + x2 - tw) / 2, y), line, font=g, fill=WHITE)
            y += 15


def line(d, a, b):
    d.line((a, b), fill=NAVY, width=2)


def topologia_ipv4():
    w, h = 1400, 900
    im = Image.new("RGB", (w, h), CREAM)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, w, 70), fill=NAVY)
    d.text((24, 18), "Topología IPv4  ·  192.168.134.0/24 dividida en cuatro subredes /26", font=font(22, True), fill=WHITE)
    d.text((24, 78), "Clase C privada. Los enlaces /30 del firewall y del borde no consumen las cuatro subredes del ejercicio.", font=font(14), fill=INK)

    box(d, (560, 130, 760, 210), "R1-Nucleo", TEAL, ["OSPF área 0", "router-on-a-stick"])
    box(d, (980, 130, 1180, 210), "R2-Borde", BLUE, ["10.255.255.2/32", "vecino OSPF"])
    box(d, (180, 130, 400, 220), "FW-UNAD", RED, ["ASA 5505", "inside .65", "outside 172.16.1.2"])
    line(d, (760, 170), (980, 170))
    d.text((800, 146), "172.16.1.4/30", font=font(12), fill=INK)
    line(d, (400, 175), (560, 175))
    d.text((410, 150), "172.16.1.0/30", font=font(12), fill=INK)

    box(d, (40, 300, 250, 390), "SW-Usuarios", NAVY, ["subred usuarios", "192.168.134.64/26"])
    line(d, (250, 160), (145, 300))
    box(d, (40, 430, 230, 510), "PC-User1", GREEN, ["192.168.134.70"])
    box(d, (250, 430, 440, 510), "PC-User2", GREEN, ["192.168.134.80"])
    line(d, (145, 390), (135, 430))
    line(d, (145, 390), (345, 430))

    box(d, (520, 300, 800, 390), "SW-Acceso", NAVY, ["troncal VLAN 10, 30, 40"])
    line(d, (660, 210), (660, 300))

    box(d, (470, 460, 650, 555), "SRV-WEB", TEAL, ["192.168.134.10", "HTTP y DNS"])
    box(d, (670, 460, 860, 555), "SRV-CORREO", TEAL, ["192.168.134.20", "unad.edu.co"])
    box(d, (880, 460, 1060, 540), "PC-Admin", GREEN, ["192.168.134.30"])
    d.text((500, 420), "VLAN 10  ·  servidores  ·  192.168.134.0/26  ·  gateway .1", font=font(13, True), fill=NAVY)
    line(d, (600, 390), (560, 460))
    line(d, (660, 390), (760, 460))
    line(d, (720, 390), (970, 460))

    box(d, (470, 640, 680, 730), "AP-UNAD", BLUE, ["SSID UNAD-TELEMATICA", "WPA2-PSK"])
    box(d, (710, 640, 930, 730), "Laptop-WiFi", GREEN, ["192.168.134.150"])
    d.text((470, 600), "VLAN 30  ·  inalámbrica  ·  192.168.134.128/26  ·  gateway .129", font=font(13, True), fill=NAVY)
    line(d, (600, 390), (575, 640))
    line(d, (680, 685), (710, 685))

    box(d, (980, 620, 1180, 720), "SRV-DHCP", GOLD, ["192.168.134.194", "pool .210-.229"])
    box(d, (1200, 560, 1370, 650), "3 televisores", RED, [".200  .201  .202"])
    box(d, (1200, 680, 1370, 790), "IoT", TEAL, ["HG .195", "lámpara, cámara,", "sensor"])
    d.text((980, 500), "VLAN 40 · 192.168.134.192/26 · gateway .193", font=font(13, True), fill=NAVY)
    line(d, (760, 360), (1080, 620))
    line(d, (1180, 670), (1200, 605))
    line(d, (1180, 690), (1200, 730))

    d.rectangle((0, 850, w, 900), fill=NAVY)
    d.text((24, 864), "Ping de evidencia entre servidores, inalámbrica y DHCP. El firewall se demuestra con tráfico permitido y con la regla que niega un eco ICMP.", font=font(13), fill=WHITE)
    im.save(IMG / "topologia_ipv4.png", optimize=True)


def topologia_ipv6():
    w, h = 1200, 720
    im = Image.new("RGB", (w, h), CREAM)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, w, 70), fill=NAVY)
    d.text((24, 18), "Topología IPv6  ·  2001:DB8:134::/48  ·  tres subredes /64", font=font(22, True), fill=WHITE)
    box(d, (470, 110, 730, 200), "R1-IPv6", TEAL, ["ipv6 unicast-routing", "DHCPv6 en VLAN 30"])
    box(d, (80, 280, 360, 400), "Servidores /64", NAVY, ["2001:DB8:134:1::/64", "web ::10   correo ::20", "PC-Admin ::30"])
    box(d, (420, 280, 760, 400), "Inalámbrica /64", BLUE, ["2001:DB8:134:2::/64", "AP + Laptop ::100", "gateway ::1"])
    box(d, (820, 280, 1140, 420), "DHCP del router", GOLD, ["2001:DB8:134:3::/64", "pool POOL-V6", "IoT en esta subred"])
    line(d, (560, 200), (220, 280))
    line(d, (600, 200), (590, 280))
    line(d, (660, 200), (980, 280))
    d.text((40, 460), "Doble pila solo donde el simulador lo exige", font=font(16, True), fill=NAVY)
    body = font(15)
    y = 500
    for line_text in [
        "IPv6 lleva el direccionamiento pedido, el ping entre subredes y el portal web.",
        "El cliente de correo de Packet Tracer y varios objetos IoT abren la sesión en IPv4.",
        "Por eso los servidores también tienen 10.20.10.0/24, 10.20.20.0/24 y 10.20.30.0/24.",
        "Esa segunda pila no reemplaza a IPv6: documenta el límite real del simulador.",
    ]:
        d.text((40, y), line_text, font=body, fill=INK)
        y += 28
    d.rectangle((0, 670, w, 720), fill=TEAL)
    d.text((24, 688), "Prefijo 2001:DB8::/32 reservado para documentación (RFC 3849). No se anuncia en Internet.", font=font(14), fill=WHITE)
    im.save(IMG / "topologia_ipv6.png", optimize=True)


def b64(name):
    return base64.b64encode((IMG / name).read_bytes()).decode("ascii")


def html():
    foto_b = b64("foto_estudiante.png")
    c1 = b64("telematica_convergencia.png")
    c2 = b64("telematica_iot.png")
    c3 = b64("telematica_seguridad.png")
    page = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>UNAD - Portal del centro</title>
</head>
<body style="margin:0; font-family:Arial, Helvetica, sans-serif; background:#f6f4ef; color:#212529;">
<table width="100%" cellpadding="16" cellspacing="0" bgcolor="#1b3a4b">
<tr><td>
<font color="#ffffff" size="5"><b>Universidad Nacional Abierta y a Distancia</b></font><br>
<font color="#d6efe4" size="3">Redes y comunicaciones &middot; código 202016898</font><br>
<font color="#e6d3a3" size="3">Portal de servicios del centro</font>
</td></tr>
</table>
<table width="100%" cellpadding="18" cellspacing="0">
<tr>
<td width="220" valign="top" bgcolor="#ffffff">
<img src="data:image/png;base64,{foto_b}" width="200" alt="Fotografia del estudiante"><br>
<font size="2" color="#8c2a30"><b>Reemplace esta imagen con su fotografía.</b></font>
</td>
<td valign="top">
<font size="5" color="#1b3a4b"><b>Jhon Carlos Acevedo Mendoza</b></font>
<p><b>Centro de matrícula:</b> [ESCRIBA SU CEAD O UDR]</p>
<p><b>Programa:</b> Ingeniería de Sistemas</p>
<p><b>Curso:</b> Redes y comunicaciones</p>
<p><b>Dominio de correo:</b> unad.edu.co</p>
<p>Este portal simula el punto de información del centro. Correo, televisión e Internet de las cosas usan la misma red y se separan por subred.</p>
<p><b>Integrantes del grupo:</b><br>
1. Jhon Carlos Acevedo Mendoza<br>
2. [Nombre del integrante]<br>
3. [Nombre del integrante]</p>
</td>
</tr>
</table>
<table width="100%" cellpadding="12" cellspacing="8">
<tr>
<td bgcolor="#ffffff" valign="top" width="33%">
<img src="data:image/png;base64,{c1}" width="100%" alt="Red convergente">
<p><b>1. Red convergente.</b> Datos, correo y video en una sola infraestructura IP.</p>
</td>
<td bgcolor="#ffffff" valign="top" width="33%">
<img src="data:image/png;base64,{c2}" width="100%" alt="Internet de las cosas">
<p><b>2. Espacio inteligente.</b> Sensores registrados y visibles para la gestión del servicio.</p>
</td>
<td bgcolor="#ffffff" valign="top" width="33%">
<img src="data:image/png;base64,{c3}" width="100%" alt="Seguridad de la red">
<p><b>3. Visibilidad.</b> El cortafuegos y el inventario de puertos protegen los servicios publicados.</p>
</td>
</tr>
</table>
<table width="100%" cellpadding="10" cellspacing="0" bgcolor="#1f6f6a">
<tr><td><font color="#ffffff" size="2">Práctica simulada &middot; Fase 4 &middot; uso académico del grupo</font></td></tr>
</table>
</body>
</html>
"""
    (ROOT / "index.html").write_text(page, encoding="utf-8")
    simple = """<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>UNAD - Portal del centro</title></head>
<body style="font-family:Arial, Helvetica, sans-serif; background:#f6f4ef; color:#212529;">
<table width="100%" cellpadding="16" cellspacing="0" bgcolor="#1b3a4b">
<tr><td>
<font color="#ffffff" size="5"><b>Universidad Nacional Abierta y a Distancia</b></font><br>
<font color="#d6efe4">Redes y comunicaciones · Portal de servicios del centro</font>
</td></tr>
</table>
<div style="padding:16px;">
<img src="foto_estudiante.png" width="180" alt="Fotografia del estudiante">
<h1>Jhon Carlos Acevedo Mendoza</h1>
<p><b>Centro de matrícula:</b> [ESCRIBA SU CEAD O UDR]</p>
<p><b>Programa:</b> Ingeniería de Sistemas</p>
<p><b>Curso:</b> Redes y comunicaciones · 202016898</p>
<p><b>Dominio de correo:</b> unad.edu.co</p>
<h2>Imágenes de telemática</h2>
<img src="telematica_convergencia.png" width="280" alt="Red convergente">
<img src="telematica_iot.png" width="280" alt="Internet de las cosas">
<img src="telematica_seguridad.png" width="280" alt="Seguridad de la red">
</div>
</body>
</html>
"""
    (ROOT / "index-simple.html").write_text(simple, encoding="utf-8")


def main():
    foto()
    convergencia()
    iot()
    seguridad()
    topologia_ipv4()
    topologia_ipv6()
    html()
    print("Recursos listos en", ROOT)


if __name__ == "__main__":
    main()
