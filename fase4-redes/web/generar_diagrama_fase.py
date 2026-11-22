#!/usr/bin/env python3
"""Diagrama de la Fase 4: los tres ejercicios y el orden del escaneo."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent / "imagenes" / "diagrama_fase4.png"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANSB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

NAVY = (27, 58, 75)
TEAL = (31, 111, 106)
GOLD = (140, 108, 42)
CREAM = (246, 244, 239)
INK = (33, 37, 41)
WHITE = (255, 255, 255)
RED = (140, 42, 48)
GREEN = (36, 112, 78)
BLUE = (36, 78, 120)
LINE = (190, 186, 176)


def font(size, bold=False):
    return ImageFont.truetype(SANSB if bold else SANS, size)


def center(draw, text, box, fnt, fill):
    x1, y1, x2, y2 = box
    tw = draw.textlength(text, font=fnt)
    draw.text(((x1 + x2 - tw) / 2, y1), text, font=fnt, fill=fill)


def wrap(draw, text, fnt, width):
    lines, cur = [], ""
    for word in text.split():
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


def card(draw, box, head, head_fill, lines):
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=12, fill=WHITE, outline=NAVY, width=2)
    draw.rounded_rectangle((x1, y1, x2, y1 + 46), radius=12, fill=head_fill)
    draw.rectangle((x1, y1 + 28, x2, y1 + 46), fill=head_fill)
    center(draw, head, (x1, y1 + 12, x2, y1 + 40), font(16, True), WHITE)
    y = y1 + 62
    body = font(15)
    for line in lines:
        for part in wrap(draw, line, body, x2 - x1 - 36):
            draw.text((x1 + 18, y), part, font=body, fill=INK)
            y += 22


def main():
    w, h = 1500, 900
    im = Image.new("RGB", (w, h), CREAM)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, w, 78), fill=NAVY)
    d.text((36, 16), "Fase 4. Los tres ejercicios se entregan juntos", font=font(26, True), fill=WHITE)
    d.text((36, 48), "y se construyen por separado, en cualquier orden.", font=font(18), fill=(214, 232, 226))

    card(
        d,
        (36, 110, 490, 390),
        "Ejercicio 1",
        TEAL,
        [
            "Dónde: Packet Tracer",
            "Red IPv4  192.168.134.0/24",
            "Cuatro subredes /26",
            "Web, correo, DHCP, firewall,",
            "inalámbrica, IoT y 3 televisores",
            "Archivo: Simulacion_IPv4.pkt",
        ],
    )
    card(
        d,
        (522, 110, 976, 390),
        "Ejercicio 2",
        BLUE,
        [
            "Dónde: Packet Tracer",
            "Red IPv6  2001:DB8:134::/48",
            "Tres subredes /64",
            "Web, correo, DHCPv6 del router,",
            "inalámbrica e IoT",
            "Archivo: Simulacion_IPv6.pkt",
        ],
    )
    card(
        d,
        (1008, 110, 1464, 390),
        "Ejercicio 3",
        RED,
        [
            "Dónde: el computador real",
            "Otro sistema en una máquina virtual",
            "Adaptador en puente, mismo segmento",
            "Nmap: hosts, versiones, sistema y filtro",
            "PRTG solo si el anfitrión es Windows",
            "No abre los archivos .pkt",
        ],
    )

    d.line((250, 408, 750, 408), fill=TEAL, width=3)
    d.line((750, 408, 1250, 408), fill=TEAL, width=3)
    center(d, "Sin orden obligatorio. El 3 no espera a que el 1 o el 2 ya enciendan.", (200, 418, 1300, 448), font(16, True), TEAL)

    d.rounded_rectangle((36, 460, 1464, 548), radius=10, fill=(255, 248, 230), outline=GOLD, width=2)
    d.text((56, 476), "Se relacionan solo en el informe.", font=font(16, True), fill=GOLD)
    d.text(
        (56, 504),
        "El firewall de la red IPv4 y el puerto filtered de Nmap enseñan la misma idea: una regla deja pasar un servicio y calla el resto.",
        font=font(15),
        fill=INK,
    )

    d.text((36, 572), "Qué vamos a hacer en el ejercicio 3", font=font(22, True), fill=NAVY)

    steps = [
        ("1", "Anfitrión", "El sistema que ya usa el computador. Aquí: Ubuntu 24.04."),
        ("2", "Otro sistema", "La virtual lleva un sistema distinto. Aquí: Alpine Linux 3.24."),
        ("3", "Puente", "La virtual y el anfitrión quedan en el mismo segmento. Aquí: 192.168.100.0/24."),
        ("4", "Ping", "Cada uno responde al otro. Si solo uno contesta, todavía no comparten segmento."),
        ("5", "Nmap", "Hosts vivos, versión del servicio, familia del sistema y si un filtro descarta paquetes."),
        ("6", "PRTG", "Solo en Windows. En este Ubuntu no se instaló. No reemplaza a Nmap."),
    ]
    bw, gap = 226, 16
    x = 36
    for number, title, text in steps:
        box = (x, 620, x + bw, 820)
        d.rounded_rectangle(box, radius=10, fill=WHITE, outline=NAVY, width=2)
        d.ellipse((x + 16, 636, x + 52, 672), fill=NAVY)
        center(d, number, (x + 16, 642, x + 52, 668), font(16, True), WHITE)
        d.text((x + 60, 642), title, font=font(16, True), fill=NAVY)
        y = 690
        for part in wrap(d, text, font(13), bw - 28):
            d.text((x + 14, y), part, font=font(13), fill=INK)
            y += 20
        x += bw + gap

    d.rectangle((0, 840, w, h), fill=NAVY)
    d.text(
        (36, 860),
        "Hecho el 21 de noviembre de 2026: pasos 1 a 5.   Pendiente de esta parte: PRTG, si hay un Windows en el grupo.   Pendiente de la fase: los dos .pkt y los videos.",
        font=font(14),
        fill=WHITE,
    )
    OUT.parent.mkdir(exist_ok=True)
    im.save(OUT, optimize=True)
    print(OUT)


if __name__ == "__main__":
    main()
