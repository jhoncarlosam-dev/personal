# Ejercicio 3. Escaneo y análisis del segmento propio

## Qué se va a demostrar

La guía pide una máquina virtual con un sistema operativo distinto al del anfitrión, el adaptador de red en modo puente, conectividad entre los dos sistemas, Nmap para identificar hosts, servicios y versiones, sistemas operativos y filtros, y PRTG Network Monitor en su edición gratuita para ver los dispositivos del segmento y los puertos abiertos. El sentido, leído con Abu Bakar y Kijsirikul (2023), es de inventario preventivo: saber qué está encendido antes de que eso quede como superficie de ataque.

La ejecución de este ejercicio se hizo el 21 de noviembre de 2026, a las 14:39 hora de Bogotá, sobre un anfitrión Ubuntu 24.04.5 LTS y un invitado Alpine Linux 3.24.1. Alpine no es el mismo sistema del anfitrión: usa otra distribución, otro gestor de paquetes y otro init. Los dos quedaron en el segmento 192.168.100.0/24, unidos por un puente de capa 2. El barrido de Nmap se limitó a ese prefijo. La red 172.30.0.0/24, por donde el anfitrión sale hacia su proveedor, no se sondeó.

La guía nombra VirtualBox y PRTG porque el camino más común es un computador Windows. En este equipo el hipervisor disponible es QEMU con KVM, y el modo puente es un bridge de Linux. Cumple la misma condición que el adaptador en modo puente de VirtualBox: el invitado y el anfitrión comparten dominio de difusión, Nmap midió un salto y la respuesta llegó por ARP. No se usó la NAT propia de QEMU. PRTG Network Monitor no se instaló. El instalador oficial de Paessler corre en Windows y este anfitrión es Ubuntu. Esa parte queda descrita para completarla en un equipo Windows, si el grupo lo tiene, contrastando los puertos con la tabla de Nmap de esta sección.

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

## Resultados de la ejecución

### Los dos sistemas en el mismo segmento

| Equipo | Sistema | Dirección | Interfaz | Puerta de enlace |
| --- | --- | --- | --- | --- |
| Anfitrión | Ubuntu 24.04.5 LTS, kernel 6.12.113 | 192.168.100.10/24 | br-lab | sale por otra interfaz, hacia su proveedor |
| Invitado | Alpine Linux 3.24.1, kernel 6.18.35, hostname vm-alpine | 192.168.100.20/24 | eth0 | 192.168.100.10 |

El puente `br-lab` tiene como único puerto el adaptador `tap-lab` de la máquina virtual. La tabla ARP del anfitrión registra al invitado así:

```
192.168.100.20 lladdr 52:54:00:12:34:56 REACHABLE
```

Nmap lee esa MAC como NIC virtual de QEMU. Vecinos de capa 2, no clientes escondidos detrás de una traducción.

El ping del anfitrión hacia 192.168.100.20 envió 4 paquetes y recibió 4, con 0 % de pérdida y un tiempo medio de 0,567 ms. El ping del invitado hacia 192.168.100.10 también recibió los 4, con 0 % de pérdida y un tiempo medio de 0,327 ms.

### Descubrimiento de hosts

Nmap del anfitrión: 7.94SVN. El comando fue `nmap -sn 192.168.100.0/24`.

```
Nmap scan report for 192.168.100.20
Host is up (0.00043s latency).
MAC Address: 52:54:00:12:34:56 (QEMU virtual NIC)
Nmap scan report for 192.168.100.10
Host is up.
Nmap done: 256 IP addresses (2 hosts up) scanned in 2.04 seconds
```

Hay dos equipos vivos en el segmento de la práctica. Ningún otro respondió.

### Servicios, versiones, sistema y filtro

Contra el invitado se usó `nmap -sS -sV -O --osscan-guess -p 22,81,8000,8080 --reason 192.168.100.20`.

| Puerto | Estado | Razón que dio Nmap | Servicio y versión | Qué lo explica |
| --- | --- | --- | --- | --- |
| 22/tcp | open | syn-ack ttl 64 | OpenSSH 10.3 (protocol 2.0) | sshd del invitado, versión confirmada en el equipo: OpenSSH_10.3p1 |
| 81/tcp | closed | reset ttl 64 | sin aplicación | la regla del invitado rechaza ese puerto con TCP reset |
| 8000/tcp | closed | reset ttl 64 | sin aplicación | nadie escucha y el equipo responde con reset |
| 8080/tcp | filtered | no-response | no se pudo identificar | la regla del invitado descarta el paquete con DROP |

El escaneo ACK (`nmap -sA -p 22,81,8000,8080 --reason`) separa el filtro del simple puerto cerrado. Los puertos 22, 81 y 8000 salieron **unfiltered**: la sonda llegó al invitado. El 8080 salió **filtered**, con razón no-response. Esa es la evidencia del cortafuegos. El estado filtered no es un fallo de Nmap. Es la regla que descarta el paquete, que es el mecanismo que la guía pide identificar.

La detección de sistema operativo no encontró una coincidencia exacta en la base de Nmap 7.94SVN. La mejor estimación fue Linux 4.15 a 5.8, con 97 % de confianza. Otras estimaciones bajaron hasta Linux 3.x y Android, con menos porcentaje. El sistema real, leído en `/etc/os-release` del invitado, es Alpine Linux 3.24.1 con kernel 6.18.35. La huella acierta la familia y no el nombre ni la versión de la distribución. Abu Bakar y Kijsirikul (2023) miden exactamente esa distancia: su escáner llegó al 99,5 % de exactitud al identificar puertos abiertos en un banco de alta velocidad, y aun así la versión y el sistema siguen siendo la parte frágil del inventario. Aquí el puerto abierto se identificó bien. El sistema hubo que confirmarlo dentro del equipo.

Desde el invitado, Nmap 7.99 miró al anfitrión en la dirección del puente:

| Puerto | Estado | Razón | Servicio y versión |
| --- | --- | --- | --- |
| 22/tcp | closed | conn-refused | el SSH del anfitrión no está publicado en 192.168.100.10 |
| 8000/tcp | open | syn-ack | SimpleHTTPServer 0.6 (Python 3.12.3) |
| 8080/tcp | filtered | no-response | una regla del anfitrión, aplicada solo al puente, descarta ese puerto |

El puerto 8000 se abrió a propósito para tener un servicio con versión visible, y se apaga al cerrar la práctica. No hace falta dejarlo encendido.

La medida que sigue de este inventario, en la lógica del centro del ejercicio 1, es concreta. El servicio de prueba del puerto 8000 se retira. El DROP del 8080 muestra el comportamiento que se quiere para un puerto que no debe atender a nadie: silencio, no un rechazo que confirme que el equipo existe. El SSH del invitado sí se usa para administrar la práctica; en una sede se dejaría limitado al segmento de gestión, no publicado hacia usuarios.

### PRTG en este equipo

PRTG Network Monitor no forma parte de estos resultados. Se intentó respetar el alcance de la guía: la edición gratuita se instala en el equipo base, y el instalador publicado por Paessler es para Windows. El anfitrión de esta ejecución es Ubuntu 24.04.5. Instalarlo aquí no es posible con el paquete oficial, y no se sustituye por otra consola para hacerlo pasar por PRTG.

Si un integrante tiene computador Windows, completa solo esta parte: instala la edición gratuita, descubre el prefijo de su propia red y anota cuántos dispositivos vio y qué puertos marcó en la máquina virtual. Esa tabla se contrasta con Nmap. Si el Windows no está disponible antes del cierre, el informe entrega el inventario de Nmap y deja constancia de por qué PRTG no corrió en este anfitrión.

| Herramienta | Qué mostró del invitado 192.168.100.20 | Coincidencia |
| --- | --- | --- |
| Nmap 7.94SVN, 21 de noviembre de 2026, 14:39 hora de Bogotá | 2 hosts en el segmento. Puerto 22 open, OpenSSH 10.3. Puerto 81 closed. Puerto 8080 filtered. Sistema estimado Linux, sin coincidencia exacta. Sistema real: Alpine 3.24.1 | Base del inventario |
| PRTG Network Monitor | No ejecutado. El anfitrión es Ubuntu y el instalador oficial es para Windows | Pendiente si hay un equipo Windows |

## Cómo se redacta el hallazgo

Cada captura se acompaña de tres frases, escritas con los datos reales.

1. Qué dirección se sondeó y desde qué equipo, con la hora de la prueba.
2. Qué salió: cuántos hosts, qué puertos abiertos, qué versión, qué sistema, qué estado filtered.
3. Qué se haría con eso en la sede del primer ejercicio. Por ejemplo: el puerto de administración que no se usa se cierra; el servicio cuya versión apareció vieja se actualiza; el cortafuegos que ya filtra se deja activo y se documenta la regla.

El hallazgo de esta ejecución, redactado con las salidas reales, queda así:

El 21 de noviembre de 2026, a las 14:39 hora de Bogotá, desde el anfitrión Ubuntu 24.04.5 se barrió solo el prefijo 192.168.100.0/24. Respondieron dos equipos: el anfitrión en 192.168.100.10 y la máquina virtual Alpine 3.24.1 en 192.168.100.20. En la virtual, el puerto 22 apareció open con OpenSSH 10.3, el puerto 81 apareció closed con reset, y el puerto 8080 apareció filtered porque una regla DROP no contestó. Nmap estimó Linux con 97 % de confianza y sin coincidencia exacta. El archivo del sistema dice Alpine Linux 3.24.1, kernel 6.18.35. La medida siguiente es apagar el servicio de prueba del puerto 8000 del anfitrión y conservar el filtro en los puertos que no prestan servicio.

## Qué demuestra este ejercicio

El invitado usa otro sistema operativo y, por el puente `br-lab`, comparte el prefijo 192.168.100.0/24 con el anfitrión. El ping en los dos sentidos, la tabla ARP y la distancia de un salto muestran que se ven como vecinos. Nmap responde las cuatro preguntas de la guía dentro de ese segmento: quién está, qué servicio y qué versión escucha, qué sistema parece y si un filtro descarta paquetes. La detección de sistema operativo quedó corta frente a `/etc/os-release`, y esa diferencia se reporta en lugar de corregirla a mano. PRTG no corrió en este anfitrión Ubuntu. El procedimiento se mantiene dentro del segmento de la práctica.

La relación con Le et al. (2018) queda en el propio montaje. La máquina virtual es la abstracción del hardware: otro sistema, otra pila de red, el mismo computador. El puente es la decisión que evita esconder esa máquina detrás de la NAT del hipervisor. Sin esa decisión, el ejercicio habría medido una red inventada por el hipervisor y no el segmento compartido.

## Guion del video, cinco minutos

- 0:00 a 0:40. Decir que el anfitrión es Ubuntu 24.04.5 y el invitado es Alpine Linux 3.24.1. Mostrar las dos salidas de `os-release`.
- 0:40 a 1:30. Mostrar el puente `br-lab`, la dirección 192.168.100.10 y la del invitado 192.168.100.20. Explicar que comparten segmento, que es lo que VirtualBox llama adaptador puente, y que no se usó NAT.
- 1:30 a 2:20. Hacer, o mostrar, el ping en los dos sentidos y la tabla ARP con la MAC de QEMU.
- 2:20 a 3:40. Abrir el descubrimiento de dos hosts y la tabla de puertos del invitado. Leer en voz alta: 22 open, OpenSSH 10.3; 81 closed; 8080 filtered.
- 3:40 a 4:30. Mostrar que Nmap estimó Linux al 97 % y que el sistema real es Alpine 3.24.1. Decir que PRTG no se instaló porque este anfitrión no es Windows.
- 4:30 a 5:00. Cerrar con la medida: se apaga el puerto 8000 de prueba, se conserva el filtro y el sondeo no salió de 192.168.100.0/24.

<!-- salto -->
