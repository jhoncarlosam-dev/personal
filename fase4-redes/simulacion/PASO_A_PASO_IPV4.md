# Ejercicio 1 en Packet Tracer, en el orden de las capturas

Abre Packet Tracer en tu computador. Guarda el archivo, desde el primer minuto, como `Simulacion_IPv4.pkt`.

La clave del Wi-Fi, del correo y de los objetos IoT es `Unad2026`. La de `enable` que ya traen los archivos de router es `unad2026`, en minúsculas. La máscara de las cuatro subredes es `255.255.255.192`. Si dejas `255.255.255.0`, el ping entre subredes falla.

Cada vez que aparezca **CAPTURA**, toma la pantalla, recórtala a la ventana de Packet Tracer y guárdala con ese nombre dentro de `fase4-redes/capturas/`.

## 1. Colocar los equipos

En la esquina inferior izquierda elige la categoría, el tipo y arrastra el modelo.

| Nombre que le pones | Dónde está en la paleta | Modelo |
| --- | --- | --- |
| R1-Nucleo | Network Devices, Routers | 2911 |
| R2-Borde | Network Devices, Routers | 2911 |
| SW-Acceso | Network Devices, Switches | 2960-24TT |
| SW-Usuarios | Network Devices, Switches | 2960-24TT |
| FW-UNAD | Network Devices, Security | ASA 5505. Si no está, ASA 5506-X |
| SRV-WEB | End Devices, End Devices | Server-PT |
| SRV-CORREO | End Devices, End Devices | Server-PT |
| SRV-DHCP | End Devices, End Devices | Server-PT |
| PC-Admin | End Devices, End Devices | PC-PT |
| PC-User1 | End Devices, End Devices | PC-PT |
| PC-User2 | End Devices, End Devices | PC-PT |
| PC-DHCP | End Devices, End Devices | PC-PT |
| Laptop-WiFi | End Devices, End Devices | Laptop-PT |
| AP-UNAD | Network Devices, Wireless Devices | AccessPoint-PT |
| HG-IoT | End Devices, Home | Home Gateway |
| TV1, TV2, TV3 | End Devices, Home | TV |
| Lampara, Camara, Sensor | End Devices, Home | Light, Webcam, Motion Detector |

Para renombrar: clic en el equipo, pestaña Config, Display Name.

**CAPTURA 01-topologia-vacia.png.** Se ven los nombres. Todavía no importa que no haya cables.

## 2. Cablear

Usa el rayo, Automatically Choose Connection Type. El orden del clic es origen y luego destino.

| Desde | Hacia |
| --- | --- |
| SW-Acceso FastEthernet0/1 | R1-Nucleo GigabitEthernet0/0 |
| R1-Nucleo GigabitEthernet0/1 | FW-UNAD Ethernet0/0. En el 5506-X es GigabitEthernet1/1 |
| FW-UNAD Ethernet0/1. En el 5506-X es GigabitEthernet1/2 | SW-Usuarios FastEthernet0/1 |
| R1-Nucleo GigabitEthernet0/2 | R2-Borde GigabitEthernet0/0 |
| SW-Acceso Fa0/2 | SRV-WEB |
| SW-Acceso Fa0/3 | SRV-CORREO |
| SW-Acceso Fa0/4 | PC-Admin |
| SW-Acceso Fa0/10 | AP-UNAD |
| SW-Acceso Fa0/18 | HG-IoT, puerto Internet |
| SW-Acceso Fa0/20 | SRV-DHCP |
| SW-Acceso Fa0/21 | PC-DHCP |
| SW-Acceso Fa0/22 | TV1 |
| SW-Acceso Fa0/23 | TV2 |
| SW-Acceso Fa0/24 | TV3 |
| SW-Usuarios Fa0/2 | PC-User1 |
| SW-Usuarios Fa0/3 | PC-User2 |

Los enlaces deben ponerse verdes. Un triángulo rojo es puerto apagado o cable en el puerto equivocado.

## 3. Pegar la configuración del switch y de los routers

Clic en el equipo, pestaña CLI. Si pregunta por las iniciales, escribe `no` y Enter. Borra lo que haya y pega el archivo completo. Espera a que el equipo diga que ya puede comprimir o simplemente pulsa Enter.

| Equipo | Archivo |
| --- | --- |
| SW-Acceso | `simulacion/SW-acceso.txt` |
| R1-Nucleo | `simulacion/R1-ipv4.txt` |
| R2-Borde | `simulacion/R2-ipv4.txt` |

En R1, al final:

```
show ip interface brief
```

Tienen que salir up/up GigabitEthernet0/0.10, 0/0.30, 0/0.40, 0/1 y 0/2.

**CAPTURA 02-interfaces-r1.png.** Esa salida completa.

```
show ip route
```

**CAPTURA 03-rutas-r1.png.** Se ven las redes conectadas 192.168.134.0, .128 y .192.

## 4. Direcciones fijas

En cada equipo: Desktop, IP Configuration. Máscara siempre `255.255.255.192`.

| Equipo | IP | Puerta de enlace | DNS |
| --- | --- | --- | --- |
| SRV-WEB | 192.168.134.10 | 192.168.134.1 | 192.168.134.10 |
| SRV-CORREO | 192.168.134.20 | 192.168.134.1 | 192.168.134.10 |
| PC-Admin | 192.168.134.30 | 192.168.134.1 | 192.168.134.10 |
| SRV-DHCP | 192.168.134.194 | 192.168.134.193 | 192.168.134.10 |
| HG-IoT, interfaz Internet | 192.168.134.195 | 192.168.134.193 | 192.168.134.10 |
| TV1 | 192.168.134.200 | 192.168.134.193 | 192.168.134.10 |
| TV2 | 192.168.134.201 | 192.168.134.193 | 192.168.134.10 |
| TV3 | 192.168.134.202 | 192.168.134.193 | 192.168.134.10 |

Desde PC-Admin, Command Prompt:

```
ping 192.168.134.1
ping 192.168.134.10
ping 192.168.134.20
```

Los tres tienen que responder. Si el primero falla, la máscara o el cable de la VLAN 10 están mal.

## 5. Red inalámbrica

1. Clic en AP-UNAD, Config, Port 1.
2. SSID: `UNAD-TELEMATICA`. Authentication: WPA2-PSK. PSK Pass Phrase: `Unad2026`.
3. Clic en Laptop-WiFi, pestaña Physical. Apaga el equipo con el botón de encendido.
4. Confirma que el módulo de la izquierda es WPC300N. Si es un cable de cobre, arrástralo abajo y sube el WPC300N desde el módulo de la izquierda.
5. Enciende la laptop.
6. Desktop, PC Wireless. Connect en `UNAD-TELEMATICA` y escribe `Unad2026`.
7. Config, interfaz Wireless0. IP `192.168.134.150`, máscara `255.255.255.192`, gateway `192.168.134.129`, DNS `192.168.134.10`.

**CAPTURA 04-laptop-wifi.png.** Se ve el SSID conectado y la IP .150.

Desde la laptop:

```
ping 192.168.134.10
```

**CAPTURA 05-ping-wifi-a-web.png.** Respuestas de eco. Esta captura cumple el ping entre subredes.

## 6. DHCP de la cuarta subred

En SRV-DHCP, Services, DHCP, ON. Add con estos datos:

| Campo | Valor |
| --- | --- |
| Pool Name | POOL-CONVERGENTE |
| Default Gateway | 192.168.134.193 |
| DNS Server | 192.168.134.10 |
| Start IP Address | 192.168.134.210 |
| Subnet Mask | 255.255.255.192 |
| Maximum number of Users | 20 |

Save. En PC-DHCP, Desktop, IP Configuration, elige DHCP. En Command Prompt:

```
ipconfig /all
```

Tiene que salir una IP entre .210 y .229, máscara 255.255.255.192, gateway .193 y DHCP server .194.

**CAPTURA 06-dhcp.png.** El pool encendido y el `ipconfig /all` juntos, o en dos tomas si no caben.

Desde PC-DHCP:

```
ping 192.168.134.10
ping 192.168.134.150
```

**CAPTURA 07-ping-entre-subredes.png.** Uno de esos ping, con respuesta.

## 7. Portal y DNS

En SRV-WEB, Services, DNS, ON. Agrega:

| Name | Type | Address |
| --- | --- | --- |
| www.unad.edu.co | A Record | 192.168.134.10 |
| mail.unad.edu.co | A Record | 192.168.134.20 |

En Services, HTTP, ON. Abre `index.html`, borra todo y pega el contenido de `web/index.html`. Antes de pegarlo, cambia en ese archivo el texto `[ESCRIBA SU CEAD O UDR]` por tu centro, y cambia la foto con `python3 insertar_foto.py tu_foto.jpg "Tu centro"` si puedes. Si el pegado se traba por el tamaño, usa `web/index-simple.html` e importa las imágenes de `web/imagenes/`.

Desde la laptop, Desktop, Web Browser:

```
http://192.168.134.10
http://www.unad.edu.co
```

**CAPTURA 08-portal.png.** Se leen tu nombre, el centro, la foto y las tres imágenes de telemática.

## 8. Correo unad.edu.co

En SRV-CORREO, Services, EMAIL. ON en SMTP y POP3. Domain Name: `unad.edu.co`. Set. User y Password, luego el signo +:

| Usuario | Clave | Correo |
| --- | --- | --- |
| jhon.acevedo | Unad2026 | jhon.acevedo@unad.edu.co |
| integrante.dos | Unad2026 | integrante.dos@unad.edu.co |
| integrante.tres | Unad2026 | integrante.tres@unad.edu.co |

Cambia los dos últimos por los compañeros que sí estén en el grupo.

En cada PC, Desktop, E Mail:

| Equipo | Nombre | Correo | Servidor de entrada y de salida | Usuario |
| --- | --- | --- | --- | --- |
| PC-Admin | Jhon Carlos Acevedo | jhon.acevedo@unad.edu.co | 192.168.134.20 | jhon.acevedo |
| Laptop-WiFi | el del segundo buzón | integrante.dos@unad.edu.co | 192.168.134.20 | integrante.dos |
| PC-DHCP | el del tercer buzón | integrante.tres@unad.edu.co | 192.168.134.20 | integrante.tres |

Save. Receive. La primera vez dice que no hay correo: eso ya prueba que el servidor contestó.

1. En PC-Admin, Compose, para `integrante.dos@unad.edu.co`, asunto `Prueba desde servidores`. Send.
2. En la laptop, Receive. Abre el mensaje.
3. En PC-DHCP, Compose hacia `jhon.acevedo@unad.edu.co`. Send.
4. En PC-Admin, Receive.

**CAPTURA 09-correo-usuarios.png.** El dominio `unad.edu.co` y los tres usuarios en el servidor.

**CAPTURA 10-correo-recibido.png.** Un mensaje abierto en la bandeja de quien lo recibió. Packet Tracer no entrega solo: hay que pulsar Receive.

## 9. Firewall

Si el equipo es ASA 5505, pega `simulacion/ASA-5505.txt` en la CLI. Si es 5506-X, pega `simulacion/ASA-5506.txt`.

En PC-User1 y PC-User2 la puerta de enlace es `192.168.134.65`, no la de R1. Máscara `255.255.255.192`. DNS `192.168.134.10`.

| Equipo | IP |
| --- | --- |
| PC-User1 | 192.168.134.70 |
| PC-User2 | 192.168.134.80 |

Pruebas, en este orden, y las dos en la misma captura si puedes:

1. PC-User2: `ping 192.168.134.10`. Tiene que responder.
2. PC-User1: `ping 192.168.134.20`. Tiene que agotar el tiempo. Esa regla niega solo a .70 hacia el correo.
3. En FW-UNAD: `show access-list`. El contador del deny tiene que ser mayor que cero.
4. Desde la laptop: `ping 192.168.134.70`. Tiempo agotado. El paquete llega al firewall y el firewall lo bota.

**CAPTURA 11-firewall-permite-y-niega.png.** El ping que responde y el ping que se agota.

**CAPTURA 12-firewall-acl.png.** `show access-list` con el contador.

Si el ASA no deja salir ni el HTTP, revisa que las interfaces estén en no shutdown y que PC-User use gateway .65. Los ping de las capturas 05 y 07 no pasan por el firewall: con esas ya cumpliste la conectividad entre subredes.

Desde PC-User1 abre `http://192.168.134.10`. La página debe cargar. Si el ping al correo falla y la página abre, el firewall está filtrando, que es lo que se quiere mostrar.

## 10. OSPF

En R1:

```
show ip ospf neighbor
ping 10.255.255.2
```

El vecino es 2.2.2.2 en estado FULL. El ping al loopback de R2 responde.

**CAPTURA 13-ospf.png.** Las dos salidas.

## 11. IoT y televisores

En HG-IoT, Wireless: SSID `IoT-UNAD`, WPA2-PSK, clave `Unad2026`. En cada objeto, Config, conéctalo a `IoT-UNAD`. Abre la pestaña GUI del Home Gateway: tienen que aparecer la lámpara, la cámara y el sensor. Enciende la lámpara desde ahí.

**CAPTURA 14-iot.png.** Los tres objetos y la lámpara en otro estado.

En cada televisor, pantalla o navegador: `http://192.168.134.10`.

**CAPTURA 15-tv1.png**, **16-tv2.png**, **17-tv3.png.** En cada una se leen el nombre, el centro y las imágenes. No repitas la misma toma tres veces: tiene que verse que son tres equipos.

Guarda `Simulacion_IPv4.pkt`.

## Si un ping no responde

| Síntoma | Revisa |
| --- | --- |
| El enlace sigue naranja | El puerto no es el de la tabla, o falta `no shutdown` |
| Ping a .1 falla | Máscara distinta de 255.255.255.192, o el PC no está en la VLAN de su servidor |
| La laptop no ve el SSID | El equipo quedó apagado en Physical, o la clave no es `Unad2026` |
| DHCP entrega 0.0.0.0 | El servidor no está en .194, o el pool no tiene máscara /26, o el servicio está en OFF |
| El correo no aparece | Falta pulsar Receive, o el servidor de correo no es 192.168.134.20 |
