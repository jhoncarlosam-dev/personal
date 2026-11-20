# Ejercicio 3. Escaneo y análisis del segmento propio

## Qué se va a demostrar

La guía pide una máquina virtual con un sistema operativo distinto al del anfitrión, el adaptador de red en modo puente, conectividad entre los dos sistemas, Nmap para identificar hosts, servicios y versiones, sistemas operativos y filtros, y PRTG Network Monitor en su edición gratuita para ver los dispositivos del segmento y los puertos abiertos. El sentido, leído con Abu Bakar y Kijsirikul (2023), es de inventario preventivo: saber qué está encendido antes de que eso quede como superficie de ataque.

Este informe no trae resultados de ese escaneo. Un resultado de Nmap solo es evidencia si salió del segmento del grupo, con la fecha y las direcciones que muestren `ipconfig` y `ip a`. Pegar una salida de otra red, o una salida de ejemplo, no responde la guía. Al final de la sección está la forma de redactar lo que aparezca, y las tablas están vacías a propósito.

Hay un límite de alcance. El barrido se hace sobre el prefijo del enrutador propio, el de la casa o el del laboratorio que el grupo controla. Si el adaptador en puente cae en una red grande que no es del grupo, por ejemplo una red administrativa del campus, no se barre ese prefijo. Se limita el sondeo a la dirección del anfitrión y a la de la máquina virtual. El artículo citado evalúa escáneres en un banco de pruebas de los autores. Ese mismo cuidado aplica aquí.

La guía enlaza el instalador de Nmap 6.01, publicado en 2012. Se instala la versión estable vigente desde el sitio oficial del proyecto, https://nmap.org/download.html. La detección de versiones y de sistema operativo es justamente el punto que Abu Bakar y Kijsirikul (2023) tratan como exactitud del inventario. Un binario de 2012 reconoce mal sistemas actuales y debilita la evidencia. En el informe se anota el número de versión que quede instalado, con `nmap --version`.

## La máquina virtual en el mismo segmento

La ruta que mejor cumple la guía es un anfitrión Windows, donde corre PRTG, y un invitado Ubuntu, que es un sistema distinto. Si el anfitrión ya es Linux, el invitado puede ser otra familia, por ejemplo una imagen de Windows que el estudiante tenga licenciada. Lo que no cumple es clonar el mismo sistema y llamarlo "distinto".

El hipervisor es VirtualBox, descargado desde https://www.virtualbox.org/wiki/Downloads. La imagen de Ubuntu Desktop vigente se descarga desde https://ubuntu.com/download/desktop. Se crea una máquina tipo Linux, Ubuntu, de 64 bits, con al menos 2 GB de memoria y un disco dinámico de 25 GB. Se arranca con la ISO y se completa el instalador.

El punto que la guía vigila es el adaptador. En VirtualBox, Configuración, Red, Adaptador 1, se elige **Conectado a: Adaptador puente** y se selecciona la tarjeta física por la que el anfitrión sale a la red, la Ethernet o la Wi-Fi real. No se elige NAT, ni red interna, ni el adaptador solo-anfitrión. NAT metería al invitado en una red 10.0.2.0/24 inventada por VirtualBox: habría ping hacia el anfitrión por una dirección especial y los dos equipos no compartirían segmento. El puente hace que el invitado pida dirección al mismo enrutador que el anfitrión y aparezca como un vecino más.

En algunos adaptadores Wi-Fi el puente no entrega DHCP. Se prueba, en la misma ventana, el modo promiscuo en "Permitir todo". Si aun así no hay dirección, se conecta el anfitrión por cable. Es una limitación del controlador inalámbrico, no de la configuración lógica.

Con los dos sistemas encendidos se comparan las direcciones.

En Windows:

```
ipconfig /all
```

En Ubuntu:

```
ip -4 addr show
ip route
```

Las dos direcciones IPv4 deben caer en el mismo prefijo. En una red casera /24, los tres primeros octetos coinciden y la máscara es 255.255.255.0. La puerta de enlace predeterminada es la misma. Esa comparación es la prueba de "mismo segmento" que pide la guía.

Luego el ping en los dos sentidos. Desde Windows, `ping` a la IPv4 de Ubuntu. Desde Ubuntu, `ping` a la IPv4 de Windows. Se anota también la tabla ARP, porque confirma que se vieron en capa 2 y no a través de un traductor: en Windows, `arp -a`, y debe aparecer la MAC de la máquina virtual junto a su IPv4.

:::evidencia
Figura 22. VirtualBox con el Adaptador 1 en modo puente y el nombre de la tarjeta física visible.
:::

:::evidencia
Figura 23. Instalación del sistema invitado, distinto del anfitrión, ya en el escritorio.
:::

:::evidencia
Figura 24. `ipconfig /all` del anfitrión e `ip -4 addr` del invitado, con las dos direcciones en el mismo prefijo y la misma puerta de enlace.
:::

:::evidencia
Figura 25. Ping del anfitrión hacia la máquina virtual y ping de la máquina virtual hacia el anfitrión, ambos con respuesta.
:::

## Nmap: hosts, servicios, sistemas y filtros

Se instala Nmap en el anfitrión con el instalador oficial. Conviene instalarlo también en Ubuntu (`sudo apt install nmap`) para mostrar el sondeo en los dos sentidos. La evidencia mínima es la del anfitrión. Durante la instalación de Windows se deja marcada la opción de Npcap. Sin esa captura de paquetes, el escaneo SYN y la detección de sistema operativo no tienen de dónde leer.

En todas las órdenes siguientes, `PREFIJO` es el que se vio en `ipconfig`, por ejemplo 192.168.1.0/24, y las direcciones son las reales del anfitrión y de la máquina virtual. No se usan las de este párrafo.

Hosts encendidos:

```
nmap -sn PREFIJO
```

`-sn` descubre hosts y no barre puertos. Sirve para contar equipos antes de mirar servicios. En la salida se identifican, como mínimo, el enrutador, el anfitrión y la máquina virtual.

Servicios y versiones, contra la máquina virtual y contra el anfitrión:

```
nmap -sS -sV -p 1-1024 --reason IP_DE_LA_MAQUINA_VIRTUAL
nmap -sT -sV -p 1-1024 --reason IP_DEL_ANFITRION
```

`-sS` es un escaneo SYN: envía el primer segmento del establecimiento TCP y, si vuelve un SYN-ACK, el puerto está abierto, sin completar la conexión. Pide privilegios de administrador. `-sT` completa la conexión y sirve de respaldo donde el SYN no esté disponible. `-sV` interroga el servicio para leer la aplicación y la versión, que es la huella pasiva de banner que describen Abu Bakar y Kijsirikul (2023) junto a las sondas activas. `--reason` obliga a Nmap a decir por qué clasificó el puerto. Esa razón es la que se cita en el informe.

Sistema operativo:

```
nmap -O --osscan-guess IP_DE_LA_MAQUINA_VIRTUAL
nmap -O --osscan-guess IP_DEL_ANFITRION
```

La detección compara respuestas TCP, ICMP y de secuencia contra una base de huellas. Se ejecuta como administrador. Puede equivocarse o dar un porcentaje bajo: eso también se escribe. Un resultado honesto del tipo "la huella apunta a Linux 4.x o 5.x, con confianza 90" vale más que forzar el nombre exacto de la distribución.

Filtros y cortafuegos. Nmap distingue tres estados que bastan para esta fase.

- **open**. El puerto acepta conexión. Hay una aplicación escuchando.
- **closed**. El equipo respondió que el puerto no tiene aplicación. El paquete llegó al sistema.
- **filtered**. No hubo respuesta útil, o llegó un ICMP de tipo prohibido por un administrador. Un filtro, casi siempre un cortafuegos, descartó la sonda.

Para separar "el puerto está cerrado" de "un filtro se interpuso" se usa un escaneo ACK acotado a los puertos ya vistos, otra vez solo contra el anfitrión y la máquina virtual:

```
nmap -sA -p 22,80,135,139,443,445,3389 --reason IP_DEL_OBJETIVO
```

En un ACK scan, **unfiltered** significa que la sonda llegó al host y Nmap no puede decir si el puerto está abierto. **filtered** significa que un dispositivo intermedio la descartó. El cortafuegos de Windows, encendido por defecto, suele producir ese estado en puertos que no tienen una regla de entrada. Ese hallazgo es el que la guía pide cuando habla de "mecanismos de filtrado de paquetes o cortafuegos". La respuesta operativa, del lado de quien administra, es cerrar lo que no se usa, dejar el perfil de cortafuegos activo y anotar la versión que `-sV` haya mostrado para actualizarla.

No hace falta, y no corresponde a esta práctica, recorrer técnicas cuyo fin es ocultar el sondeo. El artículo las menciona como antecedentes de investigación en redes de alta velocidad. El ejercicio del curso es el inventario visible del segmento propio.

:::evidencia
Figura 26. `nmap --version` y `nmap -sn` del prefijo propio, con el anfitrión, la máquina virtual y el enrutador identificados.
:::

:::evidencia
Figura 27. `nmap -sV` contra la máquina virtual y contra el anfitrión, donde se lean nombres de servicio y versiones.
:::

:::evidencia
Figura 28. `nmap -O` con la familia de sistema operativo estimada y el nivel de confianza.
:::

:::evidencia
Figura 29. Salida donde se distinga al menos un puerto open, uno closed o uno filtered, con la columna de `--reason`.
:::

Tabla para transcribir la salida, sin inventar filas. Se agregan las que de verdad aparezcan.

| Dirección | Equipo | Estado en el descubrimiento | Sistema estimado | Confianza |
| --- | --- | --- | --- | --- |
| | Anfitrión | | | |
| | Máquina virtual | | | |
| | Enrutador | | | |

| Dirección | Puerto | Estado | Razón que dio Nmap | Servicio y versión |
| --- | --- | --- | --- | --- |
| | | | | |
| | | | | |
| | | | | |

## PRTG Network Monitor

PRTG se instala en el equipo anfitrión, que es donde la guía lo pide, desde https://www.paessler.com/es/download/prtg-download. Se elige la edición gratuita. Esa edición alcanza para cien sensores, de sobra para un segmento casero. El instalador deja un servicio local y abre la consola web en el propio equipo, por lo general en `http://127.0.0.1` o en el acceso directo del escritorio. Se crea la cuenta local que pida el asistente y se lanza un descubrimiento de la red local.

En el descubrimiento se indica el prefijo que ya se confirmó con `ipconfig`, el mismo del puente. Al terminar, el mapa o la lista de dispositivos debe mostrar al menos el anfitrión, la máquina virtual y el enrutador. Se abre el dispositivo de la máquina virtual y se revisan los sensores de disponibilidad y de puertos. Un puerto abierto en PRTG se contrasta con la fila correspondiente de Nmap: las dos herramientas deberían coincidir en lo evidente, por ejemplo el puerto 22 si en Ubuntu quedó SSH. Si no coinciden, se anota cuál de las dos no vio el puerto y si el cortafuegos del invitado lo explica.

PRTG y Nmap no se repiten. Nmap es una fotografía tomada a propósito, con detalle de versión y de motivo del estado. PRTG se queda vigilando: avisa si un equipo que estaba arriba deja de responder o si un sensor de puerto cambia. Abu Bakar y Kijsirikul (2023) concentran su aporte en la velocidad y la exactitud del sondeo. La práctica completa ese sondeo con una vigilancia continua, que es lo que una sede necesitaría al día siguiente de haber cerrado los puertos de más.

:::evidencia
Figura 30. Consola de PRTG con el descubrimiento del segmento y el número de dispositivos encontrados.
:::

:::evidencia
Figura 31. Ficha de la máquina virtual, o del anfitrión, con los sensores de puerto y el estado de cada uno.
:::

| Herramienta | Qué mostró del mismo equipo | Coincidencia |
| --- | --- | --- |
| Nmap | | |
| PRTG | | |

## Cómo se redacta el hallazgo

Cada captura se acompaña de tres frases, escritas con los datos reales.

1. Qué dirección se sondeó y desde qué equipo, con la hora de la prueba.
2. Qué salió: cuántos hosts, qué puertos abiertos, qué versión, qué sistema, qué estado filtered.
3. Qué se haría con eso en la sede del primer ejercicio. Por ejemplo: el puerto de administración que no se usa se cierra; el servicio cuya versión apareció vieja se actualiza; el cortafuegos que ya filtra se deja activo y se documenta la regla.

Un párrafo modelo, con datos de relleno que no se deben copiar como si fueran el resultado, solo muestra el tono. El párrafo que se entregue reemplaza cada dato por el de la salida propia:

Desde el anfitrión se barrió el prefijo del enrutador propio. Respondieron el enrutador, el anfitrión y la máquina virtual. En la virtual, el puerto 22 apareció open con OpenSSH y la versión que mostró Nmap. En el anfitrión, varios puertos devolvieron filtered y la razón fue la ausencia de respuesta, coherente con el cortafuegos de Windows activo. La medida siguiente es confirmar que ese puerto abierto hace falta para la práctica y dejar filtrados los que no se usan.

Si un comando falla, se pega el mensaje de error y la corrección. Una sección en blanco se lee como ejercicio no presentado.

## Qué demuestra este ejercicio

El invitado usa otro sistema operativo y, por el puente, comparte prefijo y puerta de enlace con el anfitrión. El ping en los dos sentidos y la tabla ARP muestran que se ven como vecinos. Nmap responde las cuatro preguntas de la guía: quién está, qué servicio y qué versión escucha, qué sistema parece y si un filtro descarta paquetes. PRTG vuelve a contar esos dispositivos y deja sensores sobre los puertos. El procedimiento se mantiene dentro del segmento autorizado, que es la condición para que el escaneo sea una medida preventiva y no una sonda contra redes ajenas.

La relación con Le et al. (2018) queda en el propio montaje. La máquina virtual es la abstracción del hardware: otro sistema, otra pila de red, el mismo computador. El modo puente es la decisión que evita esconder esa máquina detrás del NAT del hipervisor. Sin esa decisión, el ejercicio mediría la red interna de VirtualBox y no el segmento pedido.

## Guion del video, cinco minutos

- 0:00 a 0:40. Decir qué sistema tiene el anfitrión y cuál se instaló en la virtual. Mostrar el escritorio de los dos.
- 0:40 a 1:20. Abrir la configuración de red de VirtualBox y señalar **Adaptador puente** y el nombre de la tarjeta. Explicar en una frase por qué NAT no serviría.
- 1:20 a 2:10. Poner juntas las dos direcciones IP y hacer el ping en los dos sentidos.
- 2:10 a 3:30. Correr, o mostrar ya corrido y volver a lanzar uno en vivo, el descubrimiento de hosts y el `-sV` contra la virtual. Leer un puerto open y su versión.
- 3:30 a 4:20. Mostrar una línea filtered o la salida del ACK scan, y la detección de sistema operativo con su confianza. Abrir PRTG en el mismo prefijo.
- 4:20 a 5:00. Cerrar con la medida preventiva: qué puerto sobra, qué cortafuegos se queda encendido y por qué el sondeo no salió del segmento propio.

<!-- salto -->
