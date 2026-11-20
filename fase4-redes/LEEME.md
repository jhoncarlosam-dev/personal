# Fase 4. Prácticas simuladas

Informe, página del portal y comandos para la red IPv4, la red IPv6 y el escaneo. La fecha de cierre de la fase es el domingo 22 de noviembre de 2026.

## Qué ya está hecho

- Cálculo de 192.168.134.0/24 en cuatro subredes /26 y de 2001:DB8:134::/48 en tres subredes /64.
- Comandos para pegar en Packet Tracer, en `simulacion/`.
- Portal `web/index.html`, con el nombre de Jhon Carlos Acevedo Mendoza, un recuadro de foto y tres imágenes de telemática.
- Informe en `informe/Informe_Fase4_Redes_y_Comunicaciones.docx`, con marco de las lecturas, procedimientos, matrices de prueba y guiones de video de cinco minutos.

## Qué tiene que hacer el grupo

Packet Tracer, VirtualBox, Nmap y PRTG corren en los computadores del grupo. Este material no incluye archivos `.pkt`, capturas ni videos. Esos son la evidencia de funcionamiento. Los recuadros amarillos del informe se llenan con lo que salga de esa ejecución.

1. Escribir el código del estudiante, el CEAD o la UDR, y los nombres de quienes sí participaron. Borrar las filas de integrantes que no correspondan.
2. Poner la foto real en el portal: `python3 insertar_foto.py foto.jpg "CEAD o UDR"` dentro de `web/`. Si no hay Python, editar el centro en `index.html` y seguir la nota del informe para la foto.
3. Armar `Simulacion_IPv4.pkt` siguiendo el ejercicio 1. Pegar los archivos `.txt` en la CLI de cada equipo. La clave Wi-Fi, la del router y la del correo es `Unad2026`.
4. Armar `Simulacion_IPv6.pkt` en un archivo nuevo, con el ejercicio 2.
5. En el computador propio: VirtualBox en modo puente, un sistema distinto al anfitrión, Nmap y PRTG. Barrer solo el prefijo de la red propia.
6. Pegar las capturas en los recuadros amarillos y borrar la frase roja de cada recuadro.
7. Grabar los tres videos con el guion del informe, subirlos y anotar las URL en `Enlaces_videos.txt`.
8. Publicar en el foro aportes propios. El apéndice B deja borradores para reescribir, no mensajes listos para copiar.
9. Comprimir el informe, los dos `.pkt`, el txt de los enlaces y, si el docente lo pide, las capturas sueltas. Entrega un solo integrante.

## Orden que evita rehacer trabajo

Primero los ping entre servidores, red inalámbrica y subred DHCP. Esos no pasan por el firewall. Después el ASA, el portal, el correo, los televisores y el IoT. La red IPv6 va en otro archivo. El escaneo se hace de último porque no depende de Packet Tracer.

## Si algo no responde

- Ping entre VLAN falla: máscara `255.255.255.192`, puerta de enlace la del router de esa subred, y `no shutdown` en la interfaz física y en la subinterfaz.
- IPv6 no cruza subredes: falta `ipv6 unicast-routing`.
- El PC de la tercera subred IPv6 no muestra arriendo: IP Configuration en DHCP, no en Auto-Config, y `show ipv6 dhcp binding` en el router.
- El ASA no deja salir: revisar `ASA-5505.txt` o `ASA-5506.txt`, según el equipo que tenga la versión de Packet Tracer. Los ping obligatorios entre subredes se capturan por el núcleo aunque el firewall todavía se esté ajustando.
- El correo no llega: pulsar Receive. Packet Tracer no empuja la bandeja.
